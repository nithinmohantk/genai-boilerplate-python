"""
Memory service for managing user memories and contextual AI information.
"""

import logging
from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import and_, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.chat import (
    MemoryCreate,
    MemoryImportance,
    MemorySearchRequest,
    MemoryType,
    MemoryUpdate,
    UserMemory,
)

logger = logging.getLogger(__name__)


class MemoryService:
    """Service for managing user memories and contextual information."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_memory(
        self, user_id: UUID, tenant_id: UUID, memory_data: MemoryCreate
    ) -> UserMemory:
        """Create a new user memory."""
        try:
            # Generate embedding for semantic search (placeholder for actual embedding)
            embedding = await self._generate_embedding(memory_data.content)

            memory = UserMemory(
                tenant_id=tenant_id,
                user_id=user_id,
                session_id=memory_data.session_id,
                title=memory_data.title,
                content=memory_data.content,
                memory_type=memory_data.memory_type,
                importance=memory_data.importance,
                tags=memory_data.tags,
                context=memory_data.context,
                embedding=embedding,
                expires_at=memory_data.expires_at,
            )

            self.db.add(memory)
            await self.db.commit()
            await self.db.refresh(memory)

            logger.info(f"Created memory {memory.id} for user {user_id}")
            return memory

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating memory: {e}")
            raise

    async def get_memory(self, memory_id: UUID, user_id: UUID) -> UserMemory | None:
        """Get a specific memory by ID."""
        try:
            query = select(UserMemory).where(
                and_(UserMemory.id == memory_id, UserMemory.user_id == user_id)
            )

            result = await self.db.execute(query)
            memory = result.scalar_one_or_none()

            if memory:
                # Update access tracking
                memory.access_count += 1
                memory.last_accessed = datetime.now()
                await self.db.commit()

            return memory

        except Exception as e:
            logger.error(f"Error getting memory: {e}")
            return None

    async def get_user_memories(
        self,
        user_id: UUID,
        tenant_id: UUID,
        memory_types: list[MemoryType] | None = None,
        importance_levels: list[MemoryImportance] | None = None,
        tags: list[str] | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[UserMemory]:
        """Get user's memories with filtering."""
        try:
            conditions = [
                UserMemory.user_id == user_id,
                UserMemory.tenant_id == tenant_id,
                or_(
                    UserMemory.expires_at.is_(None),
                    UserMemory.expires_at > datetime.now(),
                ),
            ]

            if memory_types:
                conditions.append(UserMemory.memory_type.in_(memory_types))

            if importance_levels:
                conditions.append(UserMemory.importance.in_(importance_levels))

            if tags:
                # JSON array contains any of the specified tags
                conditions.append(
                    UserMemory.tags.op("@>")(
                        [tags]
                    )  # PostgreSQL JSON contains operator
                )

            query = (
                select(UserMemory)
                .where(and_(*conditions))
                .order_by(desc(UserMemory.importance), desc(UserMemory.created_at))
                .limit(limit)
                .offset(offset)
            )

            result = await self.db.execute(query)
            return result.scalars().all()

        except Exception as e:
            logger.error(f"Error getting user memories: {e}")
            return []

    async def search_memories(
        self, user_id: UUID, tenant_id: UUID, search_request: MemorySearchRequest
    ) -> list[UserMemory]:
        """Search memories using semantic similarity and filters."""
        try:
            # Generate embedding for search query (placeholder)
            query_embedding = await self._generate_embedding(search_request.query)

            conditions = [
                UserMemory.user_id == user_id,
                UserMemory.tenant_id == tenant_id,
                or_(
                    UserMemory.expires_at.is_(None),
                    UserMemory.expires_at > datetime.now(),
                ),
            ]

            # Apply filters
            if search_request.memory_types:
                conditions.append(
                    UserMemory.memory_type.in_(search_request.memory_types)
                )

            if search_request.importance_levels:
                conditions.append(
                    UserMemory.importance.in_(search_request.importance_levels)
                )

            if search_request.tags:
                conditions.append(UserMemory.tags.op("@>")(search_request.tags))

            # Text search in title and content
            text_search = f"%{search_request.query.lower()}%"
            conditions.append(
                or_(
                    func.lower(UserMemory.title).like(text_search),
                    func.lower(UserMemory.content).like(text_search),
                )
            )

            query = (
                select(UserMemory)
                .where(and_(*conditions))
                .order_by(
                    desc(UserMemory.importance),
                    desc(UserMemory.access_count),
                    desc(UserMemory.last_accessed),
                )
                .limit(search_request.limit)
            )

            result = await self.db.execute(query)
            return result.scalars().all()

        except Exception as e:
            logger.error(f"Error searching memories: {e}")
            return []

    async def update_memory(
        self, memory_id: UUID, user_id: UUID, updates: MemoryUpdate
    ) -> UserMemory | None:
        """Update a user memory."""
        try:
            memory = await self.get_memory(memory_id, user_id)
            if not memory:
                return None

            # Update fields
            update_data = updates.dict(exclude_unset=True)
            for field, value in update_data.items():
                if hasattr(memory, field):
                    setattr(memory, field, value)

            # Regenerate embedding if content changed
            if "content" in update_data:
                memory.embedding = await self._generate_embedding(memory.content)

            memory.updated_at = datetime.now()
            await self.db.commit()
            await self.db.refresh(memory)

            logger.info(f"Updated memory {memory_id}")
            return memory

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating memory: {e}")
            return None

    async def delete_memory(self, memory_id: UUID, user_id: UUID) -> bool:
        """Delete a user memory."""
        try:
            memory = await self.get_memory(memory_id, user_id)
            if not memory:
                return False

            await self.db.delete(memory)
            await self.db.commit()

            logger.info(f"Deleted memory {memory_id}")
            return True

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error deleting memory: {e}")
            return False

    async def get_relevant_memories(
        self,
        user_id: UUID,
        tenant_id: UUID,
        query: str,
        limit: int = 5,
        importance_threshold: MemoryImportance = MemoryImportance.LOW,
    ) -> list[UserMemory]:
        """Get memories relevant to a specific query/context."""
        try:
            # Priority order: CRITICAL > HIGH > MEDIUM > LOW
            importance_order = {
                MemoryImportance.CRITICAL: 4,
                MemoryImportance.HIGH: 3,
                MemoryImportance.MEDIUM: 2,
                MemoryImportance.LOW: 1,
            }

            min_importance = importance_order.get(importance_threshold, 1)

            # Text search for relevant memories
            text_search = f"%{query.lower()}%"

            conditions = [
                UserMemory.user_id == user_id,
                UserMemory.tenant_id == tenant_id,
                or_(
                    UserMemory.expires_at.is_(None),
                    UserMemory.expires_at > datetime.now(),
                ),
                or_(
                    func.lower(UserMemory.title).like(text_search),
                    func.lower(UserMemory.content).like(text_search),
                    func.lower(UserMemory.tags.astext).like(text_search),
                ),
            ]

            # Add importance filter
            if importance_threshold != MemoryImportance.LOW:
                important_types = [
                    k for k, v in importance_order.items() if v >= min_importance
                ]
                conditions.append(UserMemory.importance.in_(important_types))

            query = (
                select(UserMemory)
                .where(and_(*conditions))
                .order_by(
                    desc(UserMemory.importance),
                    desc(UserMemory.access_count),
                    desc(UserMemory.created_at),
                )
                .limit(limit)
            )

            result = await self.db.execute(query)
            memories = result.scalars().all()

            # Update access tracking for retrieved memories
            for memory in memories:
                memory.access_count += 1
                memory.last_accessed = datetime.now()

            await self.db.commit()

            return memories

        except Exception as e:
            logger.error(f"Error getting relevant memories: {e}")
            return []

    async def cleanup_expired_memories(
        self, user_id: UUID | None = None, tenant_id: UUID | None = None
    ) -> int:
        """Clean up expired memories."""
        try:
            conditions = [UserMemory.expires_at < datetime.now()]

            if user_id:
                conditions.append(UserMemory.user_id == user_id)
            if tenant_id:
                conditions.append(UserMemory.tenant_id == tenant_id)

            # Get expired memories
            query = select(UserMemory).where(and_(*conditions))
            result = await self.db.execute(query)
            expired_memories = result.scalars().all()

            # Delete expired memories
            for memory in expired_memories:
                await self.db.delete(memory)

            await self.db.commit()

            count = len(expired_memories)
            logger.info(f"Cleaned up {count} expired memories")
            return count

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error cleaning up expired memories: {e}")
            return 0

    async def get_memory_stats(self, user_id: UUID, tenant_id: UUID) -> dict[str, Any]:
        """Get user's memory statistics."""
        try:
            # Total memories
            total_query = select(func.count(UserMemory.id)).where(
                UserMemory.user_id == user_id,
                UserMemory.tenant_id == tenant_id,
                or_(
                    UserMemory.expires_at.is_(None),
                    UserMemory.expires_at > datetime.now(),
                ),
            )
            total_result = await self.db.execute(total_query)
            total_memories = total_result.scalar() or 0

            # Memories by type
            type_query = (
                select(UserMemory.memory_type, func.count(UserMemory.id))
                .where(
                    UserMemory.user_id == user_id,
                    UserMemory.tenant_id == tenant_id,
                    or_(
                        UserMemory.expires_at.is_(None),
                        UserMemory.expires_at > datetime.now(),
                    ),
                )
                .group_by(UserMemory.memory_type)
            )
            type_result = await self.db.execute(type_query)
            memories_by_type = dict(type_result.fetchall())

            # Memories by importance
            importance_query = (
                select(UserMemory.importance, func.count(UserMemory.id))
                .where(
                    UserMemory.user_id == user_id,
                    UserMemory.tenant_id == tenant_id,
                    or_(
                        UserMemory.expires_at.is_(None),
                        UserMemory.expires_at > datetime.now(),
                    ),
                )
                .group_by(UserMemory.importance)
            )
            importance_result = await self.db.execute(importance_query)
            memories_by_importance = dict(importance_result.fetchall())

            return {
                "total_memories": total_memories,
                "memories_by_type": memories_by_type,
                "memories_by_importance": memories_by_importance,
                "most_accessed_count": 0,  # Placeholder
                "recent_memories_count": 0,  # Placeholder
            }

        except Exception as e:
            logger.error(f"Error getting memory stats: {e}")
            return {
                "total_memories": 0,
                "memories_by_type": {},
                "memories_by_importance": {},
                "most_accessed_count": 0,
                "recent_memories_count": 0,
            }

    async def _generate_embedding(self, text: str) -> list[float] | None:
        """Generate embedding for text (placeholder for actual embedding service)."""
        # TODO: Implement actual embedding generation using OpenAI, SentenceTransformers, etc.
        # For now, return None - semantic search will fall back to text search
        try:
            # Placeholder implementation
            # In production, this would call an embedding service like:
            # - OpenAI embeddings API
            # - SentenceTransformers
            # - Hugging Face models
            # - Azure Cognitive Services
            return None
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return None

    async def extract_memories_from_conversation(
        self,
        user_id: UUID,
        tenant_id: UUID,
        session_id: UUID,
        conversation_text: str,
        user_message: str,
        ai_response: str,
    ) -> list[UserMemory]:
        """Extract and store memories from conversation (AI-powered extraction)."""
        try:
            # TODO: Implement AI-powered memory extraction
            # This would analyze the conversation and automatically extract:
            # - User preferences mentioned
            # - Facts about the user
            # - Goals and objectives
            # - Skills and expertise areas
            # - Important context

            memories_created = []

            # Placeholder: Simple keyword-based extraction
            # In production, this would use LLM-based extraction

            # Example patterns to detect
            preference_patterns = ["i prefer", "i like", "i don't like", "i hate"]
            fact_patterns = ["i am", "i work", "my name is", "i live"]
            goal_patterns = ["i want to", "i need to", "my goal", "i'm trying to"]

            # Simple extraction logic (placeholder)
            memories_to_create = []

            text_to_analyze = f"{user_message} {ai_response}".lower()

            # Extract preferences
            for pattern in preference_patterns:
                if pattern in text_to_analyze:
                    # Extract surrounding context
                    memories_to_create.append(
                        {
                            "title": "User Preference",
                            "content": user_message,
                            "memory_type": MemoryType.PREFERENCE,
                            "importance": MemoryImportance.MEDIUM,
                        }
                    )
                    break

            # Extract facts
            for pattern in fact_patterns:
                if pattern in text_to_analyze:
                    memories_to_create.append(
                        {
                            "title": "User Information",
                            "content": user_message,
                            "memory_type": MemoryType.FACT,
                            "importance": MemoryImportance.MEDIUM,
                        }
                    )
                    break

            # Extract goals
            for pattern in goal_patterns:
                if pattern in text_to_analyze:
                    memories_to_create.append(
                        {
                            "title": "User Goal",
                            "content": user_message,
                            "memory_type": MemoryType.GOAL,
                            "importance": MemoryImportance.HIGH,
                        }
                    )
                    break

            # Create memories
            for memory_data in memories_to_create:
                memory = UserMemory(
                    tenant_id=tenant_id,
                    user_id=user_id,
                    session_id=session_id,
                    title=memory_data["title"],
                    content=memory_data["content"],
                    memory_type=memory_data["memory_type"],
                    importance=memory_data["importance"],
                    context={
                        "extracted_from": "conversation",
                        "session_id": str(session_id),
                    },
                    embedding=await self._generate_embedding(memory_data["content"]),
                )

                self.db.add(memory)
                memories_created.append(memory)

            await self.db.commit()

            logger.info(f"Extracted {len(memories_created)} memories from conversation")
            return memories_created

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error extracting memories from conversation: {e}")
            return []
