"""
Persona service for managing AI personalities and behavior customization.
"""

import logging
from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import and_, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.chat import (
    AIPersona,
    PersonaCreate,
    PersonaSessionRequest,
    PersonaType,
    PersonaUpdate,
    UserPersonaSession,
)

logger = logging.getLogger(__name__)


class PersonaService:
    """Service for managing AI personas and behavior customization."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_persona(
        self, user_id: UUID | None, tenant_id: UUID | None, persona_data: PersonaCreate
    ) -> AIPersona:
        """Create a new AI persona."""
        try:
            persona = AIPersona(
                tenant_id=tenant_id,
                user_id=user_id,
                name=persona_data.name,
                description=persona_data.description,
                persona_type=persona_data.persona_type,
                system_prompt=persona_data.system_prompt,
                personality_traits=persona_data.personality_traits,
                communication_style=persona_data.communication_style,
                expertise_areas=persona_data.expertise_areas,
                restrictions=persona_data.restrictions,
                temperature=persona_data.temperature,
                max_tokens=persona_data.max_tokens,
                is_public=persona_data.is_public,
                model_preferences=getattr(persona_data, "model_preferences", None),
            )

            self.db.add(persona)
            await self.db.commit()
            await self.db.refresh(persona)

            logger.info(f"Created persona {persona.id}: {persona.name}")
            return persona

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating persona: {e}")
            raise

    async def get_persona(
        self,
        persona_id: UUID,
        user_id: UUID | None = None,
        tenant_id: UUID | None = None,
    ) -> AIPersona | None:
        """Get a specific persona by ID."""
        try:
            conditions = [AIPersona.id == persona_id, AIPersona.is_active]

            # Add access control
            if user_id and tenant_id:
                conditions.append(
                    or_(
                        AIPersona.user_id == user_id,  # User's own persona
                        AIPersona.persona_type == PersonaType.SYSTEM,  # System persona
                        and_(
                            AIPersona.is_public,
                            AIPersona.tenant_id == tenant_id,
                        ),  # Public tenant persona
                    )
                )

            query = select(AIPersona).where(and_(*conditions))
            result = await self.db.execute(query)
            persona = result.scalar_one_or_none()

            if persona:
                # Update usage tracking
                persona.usage_count += 1
                await self.db.commit()

            return persona

        except Exception as e:
            logger.error(f"Error getting persona: {e}")
            return None

    async def get_user_personas(
        self,
        user_id: UUID,
        tenant_id: UUID,
        include_public: bool = True,
        include_system: bool = True,
        persona_type: PersonaType | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[AIPersona]:
        """Get personas available to a user."""
        try:
            conditions = [AIPersona.is_active]

            # Access control conditions
            access_conditions = [AIPersona.user_id == user_id]  # User's own personas

            if include_system:
                access_conditions.append(AIPersona.persona_type == PersonaType.SYSTEM)

            if include_public:
                access_conditions.append(
                    and_(AIPersona.is_public, AIPersona.tenant_id == tenant_id)
                )

            conditions.append(or_(*access_conditions))

            # Filter by persona type if specified
            if persona_type:
                conditions.append(AIPersona.persona_type == persona_type)

            query = (
                select(AIPersona)
                .where(and_(*conditions))
                .order_by(
                    AIPersona.persona_type,  # System first, then templates, then user
                    desc(AIPersona.usage_count),
                    AIPersona.name,
                )
                .limit(limit)
                .offset(offset)
            )

            result = await self.db.execute(query)
            return result.scalars().all()

        except Exception as e:
            logger.error(f"Error getting user personas: {e}")
            return []

    async def update_persona(
        self, persona_id: UUID, user_id: UUID, updates: PersonaUpdate
    ) -> AIPersona | None:
        """Update a persona (only if user owns it)."""
        try:
            persona = await self.get_persona(persona_id, user_id)
            if not persona or persona.user_id != user_id:
                return None

            # Update fields
            update_data = updates.dict(exclude_unset=True)
            for field, value in update_data.items():
                if hasattr(persona, field):
                    setattr(persona, field, value)

            persona.updated_at = datetime.now()
            await self.db.commit()
            await self.db.refresh(persona)

            logger.info(f"Updated persona {persona_id}")
            return persona

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating persona: {e}")
            return None

    async def delete_persona(self, persona_id: UUID, user_id: UUID) -> bool:
        """Delete a persona (soft delete)."""
        try:
            persona = await self.get_persona(persona_id, user_id)
            if not persona or persona.user_id != user_id:
                return False

            persona.is_active = False
            persona.updated_at = datetime.now()
            await self.db.commit()

            logger.info(f"Deleted persona {persona_id}")
            return True

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error deleting persona: {e}")
            return False

    async def set_session_persona(
        self, user_id: UUID, persona_request: PersonaSessionRequest
    ) -> UserPersonaSession | None:
        """Set persona for a specific session or as global preference."""
        try:
            # Verify persona access
            persona = await self.get_persona(persona_request.persona_id, user_id)
            if not persona:
                return None

            # Check if assignment already exists
            conditions = [
                UserPersonaSession.user_id == user_id,
                UserPersonaSession.persona_id == persona_request.persona_id,
            ]

            if persona_request.session_id:
                conditions.append(
                    UserPersonaSession.session_id == persona_request.session_id
                )
            else:
                conditions.append(UserPersonaSession.session_id.is_(None))

            existing_query = select(UserPersonaSession).where(and_(*conditions))
            existing_result = await self.db.execute(existing_query)
            existing_assignment = existing_result.scalar_one_or_none()

            if existing_assignment:
                # Update existing assignment
                existing_assignment.custom_prompt_additions = (
                    persona_request.custom_prompt_additions
                )
                existing_assignment.temperature_override = (
                    persona_request.temperature_override
                )
                existing_assignment.updated_at = datetime.now()
                assignment = existing_assignment
            else:
                # Create new assignment
                assignment = UserPersonaSession(
                    user_id=user_id,
                    session_id=persona_request.session_id,
                    persona_id=persona_request.persona_id,
                    custom_prompt_additions=persona_request.custom_prompt_additions,
                    temperature_override=persona_request.temperature_override,
                )
                self.db.add(assignment)

            await self.db.commit()
            await self.db.refresh(assignment)

            logger.info(f"Set persona {persona_request.persona_id} for user {user_id}")
            return assignment

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error setting session persona: {e}")
            return None

    async def get_session_persona(
        self, user_id: UUID, session_id: UUID | None = None
    ) -> AIPersona | None:
        """Get active persona for a session or user's global preference."""
        try:
            # First check for session-specific persona
            if session_id:
                session_query = (
                    select(UserPersonaSession)
                    .options(selectinload(UserPersonaSession.persona))
                    .where(
                        and_(
                            UserPersonaSession.user_id == user_id,
                            UserPersonaSession.session_id == session_id,
                        )
                    )
                )
                session_result = await self.db.execute(session_query)
                session_assignment = session_result.scalar_one_or_none()

                if session_assignment and session_assignment.persona.is_active:
                    return session_assignment.persona

            # Fall back to global persona preference
            global_query = (
                select(UserPersonaSession)
                .options(selectinload(UserPersonaSession.persona))
                .where(
                    and_(
                        UserPersonaSession.user_id == user_id,
                        UserPersonaSession.session_id.is_(None),
                    )
                )
                .order_by(desc(UserPersonaSession.updated_at))
                .limit(1)
            )
            global_result = await self.db.execute(global_query)
            global_assignment = global_result.scalar_one_or_none()

            if global_assignment and global_assignment.persona.is_active:
                return global_assignment.persona

            # No persona set, return default system persona
            return await self.get_default_persona()

        except Exception as e:
            logger.error(f"Error getting session persona: {e}")
            return await self.get_default_persona()

    async def get_default_persona(self) -> AIPersona | None:
        """Get default system persona."""
        try:
            query = (
                select(AIPersona)
                .where(
                    and_(
                        AIPersona.persona_type == PersonaType.SYSTEM,
                        AIPersona.is_active,
                        AIPersona.name == "Default Assistant",  # Default system persona
                    )
                )
                .limit(1)
            )

            result = await self.db.execute(query)
            return result.scalar_one_or_none()

        except Exception as e:
            logger.error(f"Error getting default persona: {e}")
            return None

    async def generate_persona_prompt(
        self,
        user_id: UUID,
        session_id: UUID | None = None,
        base_prompt: str | None = None,
        user_context: str | None = None,
    ) -> str:
        """Generate complete system prompt with persona and context."""
        try:
            persona = await self.get_session_persona(user_id, session_id)

            # Start with persona's system prompt or default
            if persona and persona.system_prompt:
                prompt_parts = [persona.system_prompt]
            else:
                prompt_parts = ["You are a helpful AI assistant."]

            # Add personality traits
            if persona and persona.personality_traits:
                traits_text = ", ".join(persona.personality_traits)
                prompt_parts.append(f"Your personality traits: {traits_text}")

            # Add communication style
            if persona and persona.communication_style:
                style_parts = []
                for key, value in persona.communication_style.items():
                    style_parts.append(f"{key}: {value}")
                if style_parts:
                    prompt_parts.append(
                        f"Communication style - {', '.join(style_parts)}"
                    )

            # Add expertise areas
            if persona and persona.expertise_areas:
                expertise_text = ", ".join(persona.expertise_areas)
                prompt_parts.append(f"Areas of expertise: {expertise_text}")

            # Add restrictions
            if persona and persona.restrictions:
                restrictions_text = ", ".join(persona.restrictions)
                prompt_parts.append(f"Important restrictions: {restrictions_text}")

            # Add user context if provided
            if user_context:
                prompt_parts.append(f"User context: {user_context}")

            # Add custom prompt additions from session assignment
            if session_id:
                session_assignment_query = select(UserPersonaSession).where(
                    and_(
                        UserPersonaSession.user_id == user_id,
                        UserPersonaSession.session_id == session_id,
                    )
                )
                result = await self.db.execute(session_assignment_query)
                assignment = result.scalar_one_or_none()

                if assignment and assignment.custom_prompt_additions:
                    prompt_parts.append(
                        f"Additional instructions: {assignment.custom_prompt_additions}"
                    )

            # Add base prompt if provided
            if base_prompt:
                prompt_parts.append(base_prompt)

            return "\n\n".join(prompt_parts)

        except Exception as e:
            logger.error(f"Error generating persona prompt: {e}")
            return base_prompt or "You are a helpful AI assistant."

    async def get_persona_stats(
        self, user_id: UUID | None = None, tenant_id: UUID | None = None
    ) -> dict[str, Any]:
        """Get persona usage statistics."""
        try:
            conditions = [AIPersona.is_active]

            if user_id:
                conditions.append(AIPersona.user_id == user_id)
            if tenant_id:
                conditions.append(AIPersona.tenant_id == tenant_id)

            # Total personas
            total_query = select(func.count(AIPersona.id)).where(and_(*conditions))
            total_result = await self.db.execute(total_query)
            total_personas = total_result.scalar() or 0

            # Personas by type
            type_query = (
                select(AIPersona.persona_type, func.count(AIPersona.id))
                .where(and_(*conditions))
                .group_by(AIPersona.persona_type)
            )
            type_result = await self.db.execute(type_query)
            personas_by_type = dict(type_result.fetchall())

            # Most used personas
            popular_query = (
                select(AIPersona.name, AIPersona.usage_count)
                .where(and_(*conditions))
                .order_by(desc(AIPersona.usage_count))
                .limit(5)
            )
            popular_result = await self.db.execute(popular_query)
            popular_personas = [
                {"name": row.name, "usage_count": row.usage_count}
                for row in popular_result.fetchall()
            ]

            return {
                "total_personas": total_personas,
                "personas_by_type": personas_by_type,
                "popular_personas": popular_personas,
                "public_personas": personas_by_type.get(
                    PersonaType.USER, 0
                ),  # Public user personas
            }

        except Exception as e:
            logger.error(f"Error getting persona stats: {e}")
            return {
                "total_personas": 0,
                "personas_by_type": {},
                "popular_personas": [],
                "public_personas": 0,
            }

    async def create_system_personas(self) -> list[AIPersona]:
        """Create default system personas if they don't exist."""
        try:
            system_personas = [
                {
                    "name": "Default Assistant",
                    "description": "A helpful, balanced AI assistant for general tasks",
                    "system_prompt": "You are a helpful AI assistant. Provide accurate, helpful, and friendly responses.",
                    "personality_traits": ["helpful", "friendly", "professional"],
                    "communication_style": {
                        "tone": "professional",
                        "formality": "balanced",
                    },
                    "temperature": 0.7,
                },
                {
                    "name": "Creative Writer",
                    "description": "A creative AI specialized in writing and storytelling",
                    "system_prompt": "You are a creative writing assistant. Help users with creative writing, storytelling, and literary tasks. Be imaginative and inspiring.",
                    "personality_traits": ["creative", "imaginative", "inspiring"],
                    "communication_style": {
                        "tone": "enthusiastic",
                        "formality": "casual",
                    },
                    "expertise_areas": [
                        "creative writing",
                        "storytelling",
                        "literature",
                    ],
                    "temperature": 0.9,
                },
                {
                    "name": "Technical Expert",
                    "description": "A technical AI assistant for programming and engineering tasks",
                    "system_prompt": "You are a technical expert assistant. Provide precise, accurate technical information and solutions. Be thorough and detail-oriented.",
                    "personality_traits": ["precise", "analytical", "thorough"],
                    "communication_style": {
                        "tone": "professional",
                        "formality": "formal",
                    },
                    "expertise_areas": [
                        "programming",
                        "engineering",
                        "technology",
                        "mathematics",
                    ],
                    "temperature": 0.3,
                },
                {
                    "name": "Casual Friend",
                    "description": "A casual, friendly AI companion for informal conversations",
                    "system_prompt": "You are a casual, friendly AI companion. Have natural, relaxed conversations like you would with a friend. Be warm and approachable.",
                    "personality_traits": [
                        "friendly",
                        "casual",
                        "warm",
                        "approachable",
                    ],
                    "communication_style": {"tone": "casual", "formality": "informal"},
                    "temperature": 0.8,
                },
            ]

            created_personas = []

            for persona_data in system_personas:
                # Check if persona already exists
                existing_query = select(AIPersona).where(
                    and_(
                        AIPersona.name == persona_data["name"],
                        AIPersona.persona_type == PersonaType.SYSTEM,
                    )
                )
                existing_result = await self.db.execute(existing_query)
                existing_persona = existing_result.scalar_one_or_none()

                if not existing_persona:
                    persona = AIPersona(
                        tenant_id=None,  # System personas have no tenant
                        user_id=None,  # System personas have no user
                        persona_type=PersonaType.SYSTEM,
                        is_active=True,
                        is_public=True,
                        **persona_data,
                    )

                    self.db.add(persona)
                    created_personas.append(persona)

            await self.db.commit()

            logger.info(f"Created {len(created_personas)} system personas")
            return created_personas

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating system personas: {e}")
            return []
