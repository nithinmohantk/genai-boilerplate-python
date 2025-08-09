"""
Database models for chat functionality with multi-tenancy support.
"""

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field
from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID as SQLAlchemyUUID
from sqlalchemy.orm import relationship

from core.database import Base


class MessageType(str, Enum):
    """Chat message types."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    ERROR = "error"


class SessionStatus(str, Enum):
    """Chat session status."""

    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"


class MemoryType(str, Enum):
    """Types of memories that can be stored."""

    FACT = "fact"  # Factual information about user
    PREFERENCE = "preference"  # User preferences and style
    CONTEXT = "context"  # Contextual information
    SKILL = "skill"  # User skills and expertise
    GOAL = "goal"  # User goals and objectives
    RELATIONSHIP = "relationship"  # Relationship context
    EXPERIENCE = "experience"  # Past experiences or events


class MemoryImportance(str, Enum):
    """Memory importance levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class PersonaType(str, Enum):
    """Types of personas available."""

    SYSTEM = "system"  # Built-in system personas
    USER = "user"  # User-created personas
    TEMPLATE = "template"  # Template personas


class FeatureStatus(str, Enum):
    """Feature toggle status."""

    DISABLED = "disabled"
    ENABLED = "enabled"
    PREVIEW = "preview"  # Preview/beta features
    DEPRECATED = "deprecated"


# Database Models


class ChatSession(Base):
    """Chat session model."""

    __tablename__ = "chat_sessions"

    id = Column(SQLAlchemyUUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id = Column(
        SQLAlchemyUUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False
    )
    user_id = Column(
        SQLAlchemyUUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )

    # Session info
    title = Column(String(200), nullable=True)
    status = Column(String(20), nullable=False, default=SessionStatus.ACTIVE)

    # Configuration
    model_config = Column(JSON, nullable=True)  # Model settings, parameters
    system_prompt = Column(Text, nullable=True)
    context_window = Column(Integer, nullable=True, default=4000)

    # Metadata
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    archived_at = Column(DateTime, nullable=True)

    # Relationships
    tenant = relationship("Tenant", back_populates="chat_sessions")
    user = relationship("User", back_populates="chat_sessions")
    messages = relationship(
        "ChatMessage", back_populates="session", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_session_tenant_user", "tenant_id", "user_id"),
        Index("idx_session_status", "status"),
        Index("idx_session_created", "created_at"),
        Index(
            "idx_session_user_updated_at",
            "user_id",
            "updated_at",
            postgresql_using="btree",
        ),
        Index(
            "idx_session_tenant_updated_at",
            "tenant_id",
            "updated_at",
            postgresql_using="btree",
        ),
        Index("idx_session_user_status_updated", "user_id", "status", "updated_at"),
    )


class ChatMessage(Base):
    """Chat message model."""

    __tablename__ = "chat_messages"

    id = Column(SQLAlchemyUUID(as_uuid=True), primary_key=True, default=uuid4)
    session_id = Column(
        SQLAlchemyUUID(as_uuid=True), ForeignKey("chat_sessions.id"), nullable=False
    )
    user_id = Column(
        SQLAlchemyUUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )  # Null for assistant

    # Message content
    message = Column(Text, nullable=False)
    message_type = Column(String(20), nullable=False, default=MessageType.USER)

    # Message metadata
    metadata = Column(JSON, nullable=True)  # Model info, tokens, etc.
    tokens_used = Column(Integer, nullable=True)
    processing_time_ms = Column(Integer, nullable=True)

    # Timestamps
    timestamp = Column(DateTime, default=datetime.now, nullable=False)

    # Relationships
    session = relationship("ChatSession", back_populates="messages")
    user = relationship("User", back_populates="chat_messages")

    __table_args__ = (
        Index("idx_message_session", "session_id"),
        Index("idx_message_timestamp", "timestamp"),
        Index("idx_message_type", "message_type"),
    )


class ChatDocument(Base):
    """Documents uploaded to chat sessions for RAG."""

    __tablename__ = "chat_documents"

    id = Column(SQLAlchemyUUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id = Column(
        SQLAlchemyUUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False
    )
    user_id = Column(
        SQLAlchemyUUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    session_id = Column(
        SQLAlchemyUUID(as_uuid=True), ForeignKey("chat_sessions.id"), nullable=True
    )

    # Document info
    filename = Column(String(255), nullable=False)
    content_type = Column(String(100), nullable=False)
    file_size = Column(Integer, nullable=False)

    # Storage
    file_path = Column(String(500), nullable=False)  # Path to stored file
    processed = Column(Boolean, default=False, nullable=False)

    # Processing metadata
    chunks_count = Column(Integer, nullable=True)
    processing_metadata = Column(JSON, nullable=True)

    # Timestamps
    uploaded_at = Column(DateTime, default=datetime.now, nullable=False)
    processed_at = Column(DateTime, nullable=True)

    # Relationships
    tenant = relationship("Tenant")
    user = relationship("User")
    session = relationship("ChatSession")
    chunks = relationship(
        "DocumentChunk", back_populates="document", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_document_tenant", "tenant_id"),
        Index("idx_document_user", "user_id"),
        Index("idx_document_session", "session_id"),
        Index("idx_document_processed", "processed"),
    )


class DocumentChunk(Base):
    """Text chunks from processed documents for vector search."""

    __tablename__ = "document_chunks"

    id = Column(SQLAlchemyUUID(as_uuid=True), primary_key=True, default=uuid4)
    document_id = Column(
        SQLAlchemyUUID(as_uuid=True), ForeignKey("chat_documents.id"), nullable=False
    )

    # Chunk content
    content = Column(Text, nullable=False)
    chunk_index = Column(Integer, nullable=False)  # Order within document

    # Vector embedding (if using vector DB)
    embedding = Column(JSON, nullable=True)  # Store as JSON array

    # Metadata
    metadata = Column(JSON, nullable=True)  # Page number, section, etc.
    token_count = Column(Integer, nullable=True)

    created_at = Column(DateTime, default=datetime.now, nullable=False)

    # Relationships
    document = relationship("ChatDocument", back_populates="chunks")

    __table_args__ = (
        Index("idx_chunk_document", "document_id"),
        Index("idx_chunk_index", "chunk_index"),
    )


class UserMemory(Base):
    """User memory storage for personalized AI interactions."""

    __tablename__ = "user_memories"

    id = Column(SQLAlchemyUUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id = Column(
        SQLAlchemyUUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False
    )
    user_id = Column(
        SQLAlchemyUUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    session_id = Column(
        SQLAlchemyUUID(as_uuid=True), ForeignKey("chat_sessions.id"), nullable=True
    )

    # Memory content
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    memory_type = Column(String(20), nullable=False, default=MemoryType.FACT)
    importance = Column(String(20), nullable=False, default=MemoryImportance.MEDIUM)

    # Memory metadata
    tags = Column(JSON, nullable=True)  # List of tags for categorization
    context = Column(JSON, nullable=True)  # Additional context data
    embedding = Column(JSON, nullable=True)  # Vector embedding for semantic search

    # Lifecycle management
    access_count = Column(Integer, default=0, nullable=False)
    last_accessed = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)  # Optional expiration

    # Timestamps
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships
    tenant = relationship("Tenant")
    user = relationship("User")
    session = relationship("ChatSession")

    __table_args__ = (
        Index("idx_memory_user", "user_id"),
        Index("idx_memory_tenant", "tenant_id"),
        Index("idx_memory_type", "memory_type"),
        Index("idx_memory_importance", "importance"),
        Index("idx_memory_created", "created_at"),
        Index("idx_memory_accessed", "last_accessed"),
    )


class AIPersona(Base):
    """AI Persona definitions for customized behavior."""

    __tablename__ = "ai_personas"

    id = Column(SQLAlchemyUUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id = Column(
        SQLAlchemyUUID(as_uuid=True), ForeignKey("tenants.id"), nullable=True
    )  # Null for system personas
    user_id = Column(
        SQLAlchemyUUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )  # Null for system/template personas

    # Persona definition
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    persona_type = Column(String(20), nullable=False, default=PersonaType.USER)

    # Behavior configuration
    system_prompt = Column(Text, nullable=False)  # Core persona prompt
    personality_traits = Column(JSON, nullable=True)  # Personality characteristics
    communication_style = Column(JSON, nullable=True)  # Tone, formality, etc.
    expertise_areas = Column(JSON, nullable=True)  # Areas of expertise
    restrictions = Column(JSON, nullable=True)  # Behavioral restrictions

    # Configuration
    temperature = Column(Float, nullable=True, default=0.7)  # Response creativity
    max_tokens = Column(Integer, nullable=True)
    model_preferences = Column(JSON, nullable=True)  # Preferred models

    # Usage tracking
    usage_count = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_public = Column(
        Boolean, default=False, nullable=False
    )  # Available to other users

    # Timestamps
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships
    tenant = relationship("Tenant")
    user = relationship("User")

    __table_args__ = (
        Index("idx_persona_user", "user_id"),
        Index("idx_persona_tenant", "tenant_id"),
        Index("idx_persona_type", "persona_type"),
        Index("idx_persona_active", "is_active"),
        Index("idx_persona_public", "is_public"),
    )


class UserPersonaSession(Base):
    """User's active persona for chat sessions."""

    __tablename__ = "user_persona_sessions"

    id = Column(SQLAlchemyUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(
        SQLAlchemyUUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    session_id = Column(
        SQLAlchemyUUID(as_uuid=True), ForeignKey("chat_sessions.id"), nullable=True
    )  # Null for global preference
    persona_id = Column(
        SQLAlchemyUUID(as_uuid=True), ForeignKey("ai_personas.id"), nullable=False
    )

    # Session-specific overrides
    custom_prompt_additions = Column(Text, nullable=True)
    temperature_override = Column(Float, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships
    user = relationship("User")
    session = relationship("ChatSession")
    persona = relationship("AIPersona")

    __table_args__ = (
        Index("idx_user_persona_session", "user_id", "session_id"),
        Index("idx_user_persona", "user_id", "persona_id"),
    )


class FeatureToggle(Base):
    """Feature toggle definitions and configurations."""

    __tablename__ = "feature_toggles"

    id = Column(SQLAlchemyUUID(as_uuid=True), primary_key=True, default=uuid4)

    # Feature definition
    feature_key = Column(String(100), nullable=False, unique=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=True)  # UI, AI, Integration, etc.

    # Feature status
    default_status = Column(String(20), nullable=False, default=FeatureStatus.DISABLED)
    is_preview = Column(Boolean, default=False, nullable=False)
    requires_opt_in = Column(Boolean, default=False, nullable=False)

    # Configuration
    config_schema = Column(JSON, nullable=True)  # JSON schema for feature config
    default_config = Column(JSON, nullable=True)  # Default configuration

    # Rollout control
    rollout_percentage = Column(Integer, default=0, nullable=False)  # 0-100
    target_audience = Column(JSON, nullable=True)  # User segments, roles, etc.

    # Metadata
    version = Column(String(20), nullable=True)
    documentation_url = Column(String(500), nullable=True)

    # Lifecycle
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    deprecated_at = Column(DateTime, nullable=True)

    __table_args__ = (
        Index("idx_feature_key", "feature_key"),
        Index("idx_feature_status", "default_status"),
        Index("idx_feature_preview", "is_preview"),
        Index("idx_feature_category", "category"),
    )


class UserFeatureToggle(Base):
    """User-specific feature toggle preferences."""

    __tablename__ = "user_feature_toggles"

    id = Column(SQLAlchemyUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(
        SQLAlchemyUUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    feature_id = Column(
        SQLAlchemyUUID(as_uuid=True), ForeignKey("feature_toggles.id"), nullable=False
    )

    # User preference
    status = Column(String(20), nullable=False)
    custom_config = Column(JSON, nullable=True)  # User-specific configuration

    # Opt-in tracking
    opted_in_at = Column(DateTime, nullable=True)
    feedback_provided = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships
    user = relationship("User")
    feature = relationship("FeatureToggle")

    __table_args__ = (
        Index("idx_user_feature", "user_id", "feature_id"),
        Index("idx_user_feature_status", "user_id", "status"),
    )


# Pydantic Models for API


class ChatSessionBase(BaseModel):
    """Base chat session model."""

    title: str | None = Field(None, max_length=200)
    model_config: dict[str, Any] | None = None
    system_prompt: str | None = None
    context_window: int | None = Field(4000, ge=1000, le=32000)


class ChatSessionCreate(ChatSessionBase):
    """Chat session creation model."""

    pass


class ChatSessionUpdate(BaseModel):
    """Chat session update model."""

    title: str | None = Field(None, max_length=200)
    status: SessionStatus | None = None
    model_config: dict[str, Any] | None = None
    system_prompt: str | None = None


class ChatSessionResponse(ChatSessionBase):
    """Chat session response model."""

    id: UUID
    tenant_id: UUID
    user_id: UUID
    status: SessionStatus
    created_at: datetime
    updated_at: datetime
    archived_at: datetime | None = None

    # Message count (computed)
    message_count: int | None = None

    class Config:
        from_attributes = True


class ChatMessageBase(BaseModel):
    """Base chat message model."""

    message: str = Field(..., min_length=1)
    message_type: MessageType = MessageType.USER
    metadata: dict[str, Any] | None = None


class ChatMessageCreate(ChatMessageBase):
    """Chat message creation model."""

    session_id: UUID


class ChatMessageResponse(ChatMessageBase):
    """Chat message response model."""

    id: UUID
    session_id: UUID
    user_id: UUID | None = None
    timestamp: datetime
    tokens_used: int | None = None
    processing_time_ms: int | None = None

    class Config:
        from_attributes = True


class ChatResponse(BaseModel):
    """Complete chat response with user and assistant messages."""

    user_message: ChatMessageResponse
    assistant_message: ChatMessageResponse


class DocumentUploadResponse(BaseModel):
    """Document upload response."""

    id: UUID
    filename: str
    content_type: str
    file_size: int
    uploaded_at: datetime
    processed: bool

    class Config:
        from_attributes = True


class DocumentResponse(BaseModel):
    """Document response model."""

    id: UUID
    filename: str
    content_type: str
    file_size: int
    processed: bool
    chunks_count: int | None = None
    uploaded_at: datetime
    processed_at: datetime | None = None

    class Config:
        from_attributes = True


class ChatSessionWithMessages(ChatSessionResponse):
    """Chat session with messages."""

    messages: list[ChatMessageResponse] = []


class ChatCompletionRequest(BaseModel):
    """Chat completion request."""

    message: str = Field(..., min_length=1, max_length=10000)
    session_id: UUID | None = None  # If None, create new session
    stream: bool = False
    model_config: dict[str, Any] | None = None
    include_documents: bool = True  # Whether to include uploaded documents in context


class ChatCompletionWithFilesRequest(BaseModel):
    """Chat completion request with file upload support."""

    message: str = Field(..., min_length=1, max_length=10000)
    session_id: UUID | None = None  # If None, create new session
    stream: bool = False
    model_config: dict[str, Any] | None = None
    include_documents: bool = True
    process_uploaded_files: bool = True  # Auto-process uploaded files for RAG


class ChatCompletionResponse(BaseModel):
    """Chat completion response."""

    session_id: UUID
    user_message_id: UUID
    assistant_message_id: UUID
    response: str
    tokens_used: int | None = None
    processing_time_ms: int | None = None
    model_info: dict[str, Any] | None = None


# Memory API Models


class MemoryBase(BaseModel):
    """Base memory model."""

    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1, max_length=5000)
    memory_type: MemoryType = MemoryType.FACT
    importance: MemoryImportance = MemoryImportance.MEDIUM
    tags: list[str] | None = None
    context: dict[str, Any] | None = None
    expires_at: datetime | None = None


class MemoryCreate(MemoryBase):
    """Memory creation model."""

    session_id: UUID | None = None  # Associate with specific session


class MemoryUpdate(BaseModel):
    """Memory update model."""

    title: str | None = Field(None, min_length=1, max_length=200)
    content: str | None = Field(None, min_length=1, max_length=5000)
    memory_type: MemoryType | None = None
    importance: MemoryImportance | None = None
    tags: list[str] | None = None
    context: dict[str, Any] | None = None
    expires_at: datetime | None = None


class MemoryResponse(MemoryBase):
    """Memory response model."""

    id: UUID
    tenant_id: UUID
    user_id: UUID
    session_id: UUID | None = None
    access_count: int
    last_accessed: datetime | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MemorySearchRequest(BaseModel):
    """Memory search request."""

    query: str = Field(..., min_length=1, max_length=500)
    memory_types: list[MemoryType] | None = None
    importance_levels: list[MemoryImportance] | None = None
    tags: list[str] | None = None
    limit: int = Field(10, ge=1, le=50)


# Persona API Models


class PersonaBase(BaseModel):
    """Base persona model."""

    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(None, max_length=1000)
    system_prompt: str = Field(..., min_length=10, max_length=5000)
    personality_traits: list[str] | None = None
    communication_style: dict[str, Any] | None = None
    expertise_areas: list[str] | None = None
    restrictions: list[str] | None = None
    temperature: float | None = Field(0.7, ge=0.0, le=2.0)
    max_tokens: int | None = Field(None, ge=1, le=4000)
    is_public: bool = False


class PersonaCreate(PersonaBase):
    """Persona creation model."""

    persona_type: PersonaType = PersonaType.USER


class PersonaUpdate(BaseModel):
    """Persona update model."""

    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, max_length=1000)
    system_prompt: str | None = Field(None, min_length=10, max_length=5000)
    personality_traits: list[str] | None = None
    communication_style: dict[str, Any] | None = None
    expertise_areas: list[str] | None = None
    restrictions: list[str] | None = None
    temperature: float | None = Field(None, ge=0.0, le=2.0)
    max_tokens: int | None = Field(None, ge=1, le=4000)
    is_public: bool | None = None
    is_active: bool | None = None


class PersonaResponse(PersonaBase):
    """Persona response model."""

    id: UUID
    tenant_id: UUID | None = None
    user_id: UUID | None = None
    persona_type: PersonaType
    usage_count: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PersonaSessionRequest(BaseModel):
    """Request to set persona for session."""

    persona_id: UUID
    session_id: UUID | None = None  # If None, set as global preference
    custom_prompt_additions: str | None = Field(None, max_length=1000)
    temperature_override: float | None = Field(None, ge=0.0, le=2.0)


class PersonaSessionResponse(BaseModel):
    """Persona session assignment response."""

    id: UUID
    user_id: UUID
    session_id: UUID | None = None
    persona: PersonaResponse
    custom_prompt_additions: str | None = None
    temperature_override: float | None = None
    created_at: datetime

    class Config:
        from_attributes = True


# Feature Toggle API Models


class FeatureToggleBase(BaseModel):
    """Base feature toggle model."""

    name: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(None, max_length=1000)
    category: str | None = Field(None, max_length=50)
    is_preview: bool = False
    requires_opt_in: bool = False
    default_config: dict[str, Any] | None = None
    rollout_percentage: int = Field(0, ge=0, le=100)
    documentation_url: str | None = Field(None, max_length=500)


class FeatureToggleCreate(FeatureToggleBase):
    """Feature toggle creation model."""

    feature_key: str = Field(..., min_length=1, max_length=100, regex="^[a-z0-9_]+$")
    default_status: FeatureStatus = FeatureStatus.DISABLED
    config_schema: dict[str, Any] | None = None
    target_audience: dict[str, Any] | None = None
    version: str | None = Field(None, max_length=20)


class FeatureToggleUpdate(BaseModel):
    """Feature toggle update model."""

    name: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = Field(None, max_length=1000)
    default_status: FeatureStatus | None = None
    is_preview: bool | None = None
    requires_opt_in: bool | None = None
    rollout_percentage: int | None = Field(None, ge=0, le=100)
    default_config: dict[str, Any] | None = None
    documentation_url: str | None = Field(None, max_length=500)


class FeatureToggleResponse(FeatureToggleBase):
    """Feature toggle response model."""

    id: UUID
    feature_key: str
    default_status: FeatureStatus
    config_schema: dict[str, Any] | None = None
    target_audience: dict[str, Any] | None = None
    version: str | None = None
    created_at: datetime
    updated_at: datetime
    deprecated_at: datetime | None = None

    class Config:
        from_attributes = True


class UserFeaturePreferenceRequest(BaseModel):
    """User feature preference request."""

    feature_key: str = Field(..., min_length=1, max_length=100)
    status: FeatureStatus
    custom_config: dict[str, Any] | None = None
    feedback: str | None = Field(None, max_length=1000)


class UserFeaturePreferenceResponse(BaseModel):
    """User feature preference response."""

    feature: FeatureToggleResponse
    user_status: FeatureStatus
    custom_config: dict[str, Any] | None = None
    opted_in_at: datetime | None = None
    feedback_provided: str | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FeatureDiscoveryResponse(BaseModel):
    """Feature discovery response for new features."""

    feature_key: str
    name: str
    description: str | None = None
    category: str | None = None
    is_preview: bool
    requires_opt_in: bool
    is_new: bool  # New since last check
    documentation_url: str | None = None
    user_status: FeatureStatus | None = None  # Current user's status


# Enhanced Chat Completion with Memory & Persona


class ChatCompletionWithPersonaRequest(BaseModel):
    """Chat completion request with persona and memory integration."""

    message: str = Field(..., min_length=1, max_length=10000)
    session_id: UUID | None = None
    persona_id: UUID | None = None  # Override session persona
    include_memory: bool = True  # Include relevant memories
    include_documents: bool = True
    memory_search_limit: int = Field(5, ge=0, le=20)
    stream: bool = False
    model_config: dict[str, Any] | None = None


class EnhancedChatCompletionResponse(ChatCompletionResponse):
    """Enhanced chat completion response with memory and persona info."""

    persona_used: PersonaResponse | None = None
    memories_accessed: list[MemoryResponse] = []
    new_memories_created: list[MemoryResponse] = []
    features_used: list[str] = []  # Feature keys that were active
