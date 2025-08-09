"""
Chat service for managing chat sessions, messages, and AI interactions.
"""

import logging
import time
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID

from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.chat import (
    ChatSession, ChatMessage, ChatDocument, DocumentChunk,
    MessageType, SessionStatus
)
from models.auth import User, Tenant
from core.genai_client import GenAIClient  # To be implemented
from config.settings import settings

logger = logging.getLogger(__name__)


class ChatService:
    """Service for managing chat functionality."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_session(
        self,
        user_id: UUID,
        tenant_id: UUID,
        title: Optional[str] = None,
        model_config: Optional[Dict[str, Any]] = None,
        system_prompt: Optional[str] = None,
        context_window: Optional[int] = None
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
                status=SessionStatus.ACTIVE
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
        self,
        session_id: UUID,
        user_id: UUID,
        include_messages: bool = False
    ) -> Optional[ChatSession]:
        """Get a chat session by ID."""
        try:
            query = (
                select(ChatSession)
                .where(
                    ChatSession.id == session_id,
                    ChatSession.user_id == user_id,
                    ChatSession.status != SessionStatus.DELETED
                )
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
        status: Optional[SessionStatus] = None
    ) -> List[ChatSession]:
        """Get user's chat sessions."""
        try:
            query = (
                select(ChatSession)
                .where(
                    ChatSession.user_id == user_id,
                    ChatSession.tenant_id == tenant_id
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
        self,
        session_id: UUID,
        user_id: UUID,
        updates: Dict[str, Any]
    ) -> Optional[ChatSession]:
        """Update a chat session."""
        try:
            session = await self.get_session(session_id, user_id)
            if not session:
                return None

            # Update allowed fields
            allowed_fields = {'title', 'model_config', 'system_prompt', 'status'}
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
                session_query = (
                    select(ChatSession)
                    .where(ChatSession.id == message.session_id)
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
        before_message_id: Optional[UUID] = None
    ) -> List[ChatMessage]:
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
                before_message_query = (
                    select(ChatMessage.timestamp)
                    .where(ChatMessage.id == before_message_id)
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
        self,
        session_id: UUID,
        context_window: int = 4000,
        max_messages: int = 20
    ) -> List[ChatMessage]:
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
        model_config: Optional[Dict[str, Any]] = None,
        include_documents: bool = True
    ) -> Optional[str]:
        """Generate AI response to user message."""
        try:
            # Get session
            session = await self.get_session(session_id, user_id)
            if not session:
                logger.error(f"Session {session_id} not found")
                return None

            # Get context messages
            context_messages = await self.get_context_messages(
                session_id,
                session.context_window or 4000
            )

            # Get relevant documents if enabled
            document_context = ""
            if include_documents:
                document_context = await self.get_document_context(
                    session_id, message, tenant_id
                )

            # TODO: Implement actual AI client integration
            # For now, return a mock response
            response = f"This is a mock response to: {message}"

            logger.info(f"Generated response for session {session_id}")
            return response

        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return None

    async def get_document_context(
        self,
        session_id: UUID,
        query: str,
        tenant_id: UUID,
        max_chunks: int = 5
    ) -> str:
        """Get relevant document context for the query."""
        try:
            # TODO: Implement vector search for document chunks
            # For now, return empty context
            return ""

        except Exception as e:
            logger.error(f"Error getting document context: {e}")
            return ""

    async def get_session_stats(
        self,
        user_id: UUID,
        tenant_id: UUID
    ) -> Dict[str, Any]:
        """Get user's chat session statistics."""
        try:
            # Total sessions
            total_query = (
                select(func.count(ChatSession.id))
                .where(
                    ChatSession.user_id == user_id,
                    ChatSession.tenant_id == tenant_id,
                    ChatSession.status != SessionStatus.DELETED
                )
            )
            total_result = await self.db.execute(total_query)
            total_sessions = total_result.scalar() or 0

            # Active sessions
            active_query = (
                select(func.count(ChatSession.id))
                .where(
                    ChatSession.user_id == user_id,
                    ChatSession.tenant_id == tenant_id,
                    ChatSession.status == SessionStatus.ACTIVE
                )
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
                    ChatSession.status != SessionStatus.DELETED
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
                )
            }

        except Exception as e:
            logger.error(f"Error getting session stats: {e}")
            return {
                "total_sessions": 0,
                "active_sessions": 0,
                "archived_sessions": 0,
                "total_messages": 0,
                "average_messages_per_session": 0
            }

    async def search_sessions(
        self,
        user_id: UUID,
        tenant_id: UUID,
        query: str,
        limit: int = 20
    ) -> List[ChatSession]:
        """Search user's chat sessions."""
        try:
            # Simple title search for now
            search_query = (
                select(ChatSession)
                .where(
                    ChatSession.user_id == user_id,
                    ChatSession.tenant_id == tenant_id,
                    ChatSession.status != SessionStatus.DELETED,
                    ChatSession.title.ilike(f"%{query}%")
                )
                .order_by(desc(ChatSession.updated_at))
                .limit(limit)
            )

            result = await self.db.execute(search_query)
            return result.scalars().all()

        except Exception as e:
            logger.error(f"Error searching sessions: {e}")
            return []
