"""
Chat service for managing chat sessions, messages, and AI interactions.
"""

import logging
from datetime import datetime, timedelta
from typing import Any
from uuid import UUID

from sqlalchemy import and_, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.chat import (
    ChatMessage,
    ChatSession,
    SessionStatus,
)

logger = logging.getLogger(__name__)


class ChatService:
    """Service for managing chat functionality."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_session(
        self,
        user_id: UUID,
        tenant_id: UUID,
        title: str | None = None,
        model_config: dict[str, Any] | None = None,
        system_prompt: str | None = None,
        context_window: int | None = None,
    ) -> ChatSession:
        """Create a new chat session."""
        try:
            session = ChatSession(
                tenant_id=tenant_id,
                user_id=user_id,
                title=title or f"Chat {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                model_config=model_config,
                system_prompt=system_prompt,
                context_window=context_window or 4000,
                status=SessionStatus.ACTIVE,
            )

            self.db.add(session)
            await self.db.commit()
            await self.db.refresh(session)

            logger.info(f"Created chat session {session.id} for user {user_id}")
            return session

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating chat session: {e}")
            raise

    async def get_session(
        self, session_id: UUID, user_id: UUID, include_messages: bool = False
    ) -> ChatSession | None:
        """Get a chat session by ID."""
        try:
            query = select(ChatSession).where(
                ChatSession.id == session_id,
                ChatSession.user_id == user_id,
                ChatSession.status != SessionStatus.DELETED,
            )

            if include_messages:
                query = query.options(
                    selectinload(ChatSession.messages).selectinload(ChatMessage.user)
                )

            result = await self.db.execute(query)
            return result.scalar_one_or_none()

        except Exception as e:
            logger.error(f"Error getting chat session: {e}")
            return None

    async def get_user_sessions(
        self,
        user_id: UUID,
        tenant_id: UUID,
        limit: int = 50,
        offset: int = 0,
        status: SessionStatus | None = None,
    ) -> list[ChatSession]:
        """Get user's chat sessions."""
        try:
            query = (
                select(ChatSession)
                .where(
                    ChatSession.user_id == user_id, ChatSession.tenant_id == tenant_id
                )
                .order_by(desc(ChatSession.updated_at))
                .limit(limit)
                .offset(offset)
            )

            if status:
                query = query.where(ChatSession.status == status)
            else:
                query = query.where(ChatSession.status != SessionStatus.DELETED)

            result = await self.db.execute(query)
            return result.scalars().all()

        except Exception as e:
            logger.error(f"Error getting user sessions: {e}")
            return []

    async def update_session(
        self, session_id: UUID, user_id: UUID, updates: dict[str, Any]
    ) -> ChatSession | None:
        """Update a chat session."""
        try:
            session = await self.get_session(session_id, user_id)
            if not session:
                return None

            # Update allowed fields
            allowed_fields = {"title", "model_config", "system_prompt", "status"}
            for field, value in updates.items():
                if field in allowed_fields and hasattr(session, field):
                    setattr(session, field, value)

            session.updated_at = datetime.now()
            await self.db.commit()
            await self.db.refresh(session)

            logger.info(f"Updated chat session {session_id}")
            return session

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating chat session: {e}")
            return None

    async def archive_session(self, session_id: UUID, user_id: UUID) -> bool:
        """Archive a chat session."""
        try:
            session = await self.get_session(session_id, user_id)
            if not session:
                return False

            session.status = SessionStatus.ARCHIVED
            session.archived_at = datetime.now()
            session.updated_at = datetime.now()

            await self.db.commit()

            logger.info(f"Archived chat session {session_id}")
            return True

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error archiving chat session: {e}")
            return False

    async def delete_session(self, session_id: UUID, user_id: UUID) -> bool:
        """Delete a chat session (soft delete)."""
        try:
            session = await self.get_session(session_id, user_id)
            if not session:
                return False

            session.status = SessionStatus.DELETED
            session.updated_at = datetime.now()

            await self.db.commit()

            logger.info(f"Deleted chat session {session_id}")
            return True

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error deleting chat session: {e}")
            return False

    async def save_message(self, message: ChatMessage) -> ChatMessage:
        """Save a chat message to the database."""
        try:
            self.db.add(message)
            await self.db.commit()
            await self.db.refresh(message)

            # Update session's updated_at timestamp
            if message.session_id:
                session_query = select(ChatSession).where(
                    ChatSession.id == message.session_id
                )
                session_result = await self.db.execute(session_query)
                session = session_result.scalar_one_or_none()
                if session:
                    session.updated_at = datetime.now()
                    await self.db.commit()

            return message

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error saving message: {e}")
            raise

    async def get_session_messages(
        self,
        session_id: UUID,
        user_id: UUID,
        limit: int = 100,
        before_message_id: UUID | None = None,
    ) -> list[ChatMessage]:
        """Get messages for a chat session."""
        try:
            # Verify user has access to session
            session = await self.get_session(session_id, user_id)
            if not session:
                return []

            query = (
                select(ChatMessage)
                .options(selectinload(ChatMessage.user))
                .where(ChatMessage.session_id == session_id)
                .order_by(desc(ChatMessage.timestamp))
                .limit(limit)
            )

            if before_message_id:
                # Get messages before a specific message (for pagination)
                before_message_query = select(ChatMessage.timestamp).where(
                    ChatMessage.id == before_message_id
                )
                before_result = await self.db.execute(before_message_query)
                before_timestamp = before_result.scalar_one_or_none()

                if before_timestamp:
                    query = query.where(ChatMessage.timestamp < before_timestamp)

            result = await self.db.execute(query)
            messages = result.scalars().all()

            # Return in chronological order
            return list(reversed(messages))

        except Exception as e:
            logger.error(f"Error getting session messages: {e}")
            return []

    async def get_context_messages(
        self, session_id: UUID, context_window: int = 4000, max_messages: int = 20
    ) -> list[ChatMessage]:
        """Get recent messages for context, respecting token limits."""
        try:
            query = (
                select(ChatMessage)
                .where(ChatMessage.session_id == session_id)
                .order_by(desc(ChatMessage.timestamp))
                .limit(max_messages)
            )

            result = await self.db.execute(query)
            messages = list(reversed(result.scalars().all()))

            # TODO: Implement token counting and context window management
            # For now, just return the messages
            return messages

        except Exception as e:
            logger.error(f"Error getting context messages: {e}")
            return []

    async def generate_response(
        self,
        message: str,
        session_id: UUID,
        user_id: UUID,
        tenant_id: UUID,
        model_config: dict[str, Any] | None = None,
        include_documents: bool = True,
    ) -> str | None:
        """Generate AI response to user message."""
        try:
            # Get session
            session = await self.get_session(session_id, user_id)
            if not session:
                logger.error(f"Session {session_id} not found")
                return None

            # Get context messages
            context_messages = await self.get_context_messages(
                session_id, session.context_window or 4000
            )

            # Get relevant documents if enabled
            document_context = ""
            if include_documents:
                document_context = await self.get_document_context(
                    session_id, message, tenant_id
                )

            # Use GenAI client to generate response
            from core.genai_client import genai_client

            # Format messages for AI API
            formatted_messages = genai_client.format_messages(
                user_message=message,
                context_messages=context_messages,
                system_prompt=session.system_prompt,
                document_context=document_context,
            )

            # Generate AI response
            response = await genai_client.generate_response(
                messages=formatted_messages,
                model=model_config.get("model") if model_config else None,
                temperature=model_config.get("temperature") if model_config else None,
                max_tokens=model_config.get("max_tokens") if model_config else None,
                document_context=document_context,
            )

            logger.info(f"Generated response for session {session_id}")
            return response

        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return None

    async def get_document_context(
        self, session_id: UUID, query: str, tenant_id: UUID, max_chunks: int = 5
    ) -> str:
        """Get relevant document context for the query."""
        try:
            from services.document_service import DocumentService

            # Get session to find user_id
            session_query = select(ChatSession).where(ChatSession.id == session_id)
            session_result = await self.db.execute(session_query)
            session = session_result.scalar_one_or_none()

            if not session:
                return ""

            # Search for relevant document chunks
            doc_service = DocumentService(self.db)
            chunks = await doc_service.search_documents(
                query=query,
                user_id=session.user_id,
                tenant_id=tenant_id,
                limit=max_chunks,
            )

            if not chunks:
                return ""

            # Combine chunks into context
            context_parts = []
            for chunk in chunks:
                context_parts.append(
                    f"[Document: {chunk.document.filename if hasattr(chunk, 'document') else 'Unknown'}]"
                )
                context_parts.append(chunk.content)
                context_parts.append("")

            return "\n".join(context_parts)

        except Exception as e:
            logger.error(f"Error getting document context: {e}")
            return ""

    async def get_session_stats(self, user_id: UUID, tenant_id: UUID) -> dict[str, Any]:
        """Get user's chat session statistics."""
        try:
            # Total sessions
            total_query = select(func.count(ChatSession.id)).where(
                ChatSession.user_id == user_id,
                ChatSession.tenant_id == tenant_id,
                ChatSession.status != SessionStatus.DELETED,
            )
            total_result = await self.db.execute(total_query)
            total_sessions = total_result.scalar() or 0

            # Active sessions
            active_query = select(func.count(ChatSession.id)).where(
                ChatSession.user_id == user_id,
                ChatSession.tenant_id == tenant_id,
                ChatSession.status == SessionStatus.ACTIVE,
            )
            active_result = await self.db.execute(active_query)
            active_sessions = active_result.scalar() or 0

            # Total messages
            messages_query = (
                select(func.count(ChatMessage.id))
                .join(ChatSession, ChatMessage.session_id == ChatSession.id)
                .where(
                    ChatSession.user_id == user_id,
                    ChatSession.tenant_id == tenant_id,
                    ChatSession.status != SessionStatus.DELETED,
                )
            )
            messages_result = await self.db.execute(messages_query)
            total_messages = messages_result.scalar() or 0

            return {
                "total_sessions": total_sessions,
                "active_sessions": active_sessions,
                "archived_sessions": total_sessions - active_sessions,
                "total_messages": total_messages,
                "average_messages_per_session": (
                    total_messages / total_sessions if total_sessions > 0 else 0
                ),
            }

        except Exception as e:
            logger.error(f"Error getting session stats: {e}")
            return {
                "total_sessions": 0,
                "active_sessions": 0,
                "archived_sessions": 0,
                "total_messages": 0,
                "average_messages_per_session": 0,
            }

    async def search_sessions(
        self, user_id: UUID, tenant_id: UUID, query: str, limit: int = 20
    ) -> list[ChatSession]:
        """Search user's chat sessions."""
        try:
            # Simple title search for now
            search_query = (
                select(ChatSession)
                .where(
                    ChatSession.user_id == user_id,
                    ChatSession.tenant_id == tenant_id,
                    ChatSession.status != SessionStatus.DELETED,
                    ChatSession.title.ilike(f"%{query}%"),
                )
                .order_by(desc(ChatSession.updated_at))
                .limit(limit)
            )

            result = await self.db.execute(search_query)
            return result.scalars().all()

        except Exception as e:
            logger.error(f"Error searching sessions: {e}")
            return []

    async def get_user_sessions_paginated(
        self,
        user_id: UUID,
        tenant_id: UUID,
        page: int = 1,
        page_size: int = 20,
        status: SessionStatus | None = None,
        include_message_count: bool = True,
    ) -> tuple[list[dict[str, Any]], int]:
        """Get user's chat sessions with optimized pagination and metadata."""
        try:
            offset = (page - 1) * page_size

            # Build base query
            base_conditions = [
                ChatSession.user_id == user_id,
                ChatSession.tenant_id == tenant_id,
            ]

            if status:
                base_conditions.append(ChatSession.status == status)
            else:
                base_conditions.append(ChatSession.status != SessionStatus.DELETED)

            # Query for sessions with message counts
            if include_message_count:
                query = (
                    select(
                        ChatSession,
                        func.count(ChatMessage.id).label("message_count"),
                        func.max(ChatMessage.timestamp).label("last_message_at"),
                    )
                    .outerjoin(ChatMessage, ChatSession.id == ChatMessage.session_id)
                    .where(and_(*base_conditions))
                    .group_by(ChatSession.id)
                    .order_by(
                        desc(
                            func.coalesce(
                                func.max(ChatMessage.timestamp), ChatSession.updated_at
                            )
                        )
                    )
                    .limit(page_size)
                    .offset(offset)
                )
            else:
                query = (
                    select(ChatSession)
                    .where(and_(*base_conditions))
                    .order_by(desc(ChatSession.updated_at))
                    .limit(page_size)
                    .offset(offset)
                )

            # Execute query
            result = await self.db.execute(query)

            if include_message_count:
                rows = result.all()
                sessions = []
                for row in rows:
                    session_dict = {
                        "id": str(row.ChatSession.id),
                        "tenant_id": str(row.ChatSession.tenant_id),
                        "user_id": str(row.ChatSession.user_id),
                        "title": row.ChatSession.title,
                        "status": row.ChatSession.status,
                        "created_at": row.ChatSession.created_at.isoformat(),
                        "updated_at": row.ChatSession.updated_at.isoformat(),
                        "message_count": row.message_count,
                        "last_message_at": (
                            row.last_message_at.isoformat()
                            if row.last_message_at
                            else None
                        ),
                    }
                    sessions.append(session_dict)
            else:
                sessions = result.scalars().all()

            # Get total count for pagination
            count_query = select(func.count(ChatSession.id)).where(
                and_(*base_conditions)
            )
            count_result = await self.db.execute(count_query)
            total_count = count_result.scalar() or 0

            return sessions, total_count

        except Exception as e:
            logger.error(f"Error getting paginated sessions: {e}")
            return [], 0

    async def get_session_messages_optimized(
        self,
        session_id: UUID,
        user_id: UUID,
        page: int = 1,
        page_size: int = 50,
        cursor_timestamp: datetime | None = None,
    ) -> tuple[list[ChatMessage], bool]:
        """Get session messages with cursor-based pagination for better performance."""
        try:
            # Verify user has access to session
            session = await self.get_session(session_id, user_id)
            if not session:
                return [], False

            # Build query with cursor-based pagination
            query = (
                select(ChatMessage)
                .where(ChatMessage.session_id == session_id)
                .order_by(desc(ChatMessage.timestamp))
                .limit(page_size + 1)  # Get one extra to check if there are more
            )

            if cursor_timestamp:
                query = query.where(ChatMessage.timestamp < cursor_timestamp)

            result = await self.db.execute(query)
            messages = result.scalars().all()

            # Check if there are more messages
            has_more = len(messages) > page_size
            if has_more:
                messages = messages[:-1]  # Remove the extra message

            # Return in chronological order
            return list(reversed(messages)), has_more

        except Exception as e:
            logger.error(f"Error getting optimized session messages: {e}")
            return [], False

    async def bulk_archive_sessions(
        self, session_ids: list[UUID], user_id: UUID
    ) -> int:
        """Bulk archive multiple sessions for better performance."""
        try:
            if not session_ids:
                return 0

            # Update sessions in bulk
            update_query = (
                ChatSession.__table__.update()
                .where(
                    and_(
                        ChatSession.id.in_(session_ids),
                        ChatSession.user_id == user_id,
                        ChatSession.status != SessionStatus.DELETED,
                    )
                )
                .values(
                    status=SessionStatus.ARCHIVED,
                    archived_at=datetime.now(),
                    updated_at=datetime.now(),
                )
                .returning(ChatSession.id)
            )

            result = await self.db.execute(update_query)
            updated_count = len(result.fetchall())
            await self.db.commit()

            logger.info(f"Bulk archived {updated_count} sessions for user {user_id}")
            return updated_count

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error bulk archiving sessions: {e}")
            return 0

    async def cleanup_old_sessions(
        self,
        user_id: UUID,
        tenant_id: UUID,
        days_old: int = 90,
        max_sessions: int = 1000,
    ) -> int:
        """Clean up old sessions to maintain performance with large session counts."""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_old)

            # Find old sessions to archive/delete
            cleanup_query = (
                select(ChatSession.id)
                .where(
                    and_(
                        ChatSession.user_id == user_id,
                        ChatSession.tenant_id == tenant_id,
                        ChatSession.status == SessionStatus.ACTIVE,
                        ChatSession.updated_at < cutoff_date,
                    )
                )
                .order_by(ChatSession.updated_at)
                .limit(max_sessions)
            )

            result = await self.db.execute(cleanup_query)
            session_ids = [row.id for row in result.fetchall()]

            if not session_ids:
                return 0

            # Archive old sessions
            archived_count = await self.bulk_archive_sessions(session_ids, user_id)

            logger.info(f"Cleaned up {archived_count} old sessions for user {user_id}")
            return archived_count

        except Exception as e:
            logger.error(f"Error cleaning up old sessions: {e}")
            return 0

    async def get_session_preview(
        self, session_id: UUID, user_id: UUID
    ) -> dict[str, Any] | None:
        """Get a lightweight session preview with last message."""
        try:
            # Get session with last message in one query
            query = (
                select(
                    ChatSession,
                    ChatMessage.message.label("last_message"),
                    ChatMessage.timestamp.label("last_message_at"),
                    func.count(ChatMessage.id).label("message_count"),
                )
                .outerjoin(ChatMessage, ChatSession.id == ChatMessage.session_id)
                .where(
                    and_(
                        ChatSession.id == session_id,
                        ChatSession.user_id == user_id,
                        ChatSession.status != SessionStatus.DELETED,
                    )
                )
                .group_by(ChatSession.id, ChatMessage.message, ChatMessage.timestamp)
                .order_by(desc(ChatMessage.timestamp))
                .limit(1)
            )

            result = await self.db.execute(query)
            row = result.first()

            if not row:
                return None

            return {
                "id": str(row.ChatSession.id),
                "title": row.ChatSession.title,
                "status": row.ChatSession.status,
                "created_at": row.ChatSession.created_at.isoformat(),
                "updated_at": row.ChatSession.updated_at.isoformat(),
                "last_message": row.last_message,
                "last_message_at": (
                    row.last_message_at.isoformat() if row.last_message_at else None
                ),
                "message_count": row.message_count,
            }

        except Exception as e:
            logger.error(f"Error getting session preview: {e}")
            return None
