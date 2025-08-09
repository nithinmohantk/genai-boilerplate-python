"""
Database models for chat functionality with multi-tenancy support.
"""

from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, List
from uuid import UUID, uuid4

from pydantic import BaseModel, Field
from sqlalchemy import (
    Column, String, Text, DateTime, JSON, Boolean, Integer,
    ForeignKey, Index
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


# Database Models

class ChatSession(Base):
    """Chat session model."""
    __tablename__ = "chat_sessions"

    id = Column(SQLAlchemyUUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id = Column(SQLAlchemyUUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    user_id = Column(SQLAlchemyUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
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
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_session_tenant_user', 'tenant_id', 'user_id'),
        Index('idx_session_status', 'status'),
        Index('idx_session_created', 'created_at'),
    )


class ChatMessage(Base):
    """Chat message model."""
    __tablename__ = "chat_messages"

    id = Column(SQLAlchemyUUID(as_uuid=True), primary_key=True, default=uuid4)
    session_id = Column(SQLAlchemyUUID(as_uuid=True), ForeignKey("chat_sessions.id"), nullable=False)
    user_id = Column(SQLAlchemyUUID(as_uuid=True), ForeignKey("users.id"), nullable=True)  # Null for assistant
    
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
        Index('idx_message_session', 'session_id'),
        Index('idx_message_timestamp', 'timestamp'),
        Index('idx_message_type', 'message_type'),
    )


class ChatDocument(Base):
    """Documents uploaded to chat sessions for RAG."""
    __tablename__ = "chat_documents"

    id = Column(SQLAlchemyUUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id = Column(SQLAlchemyUUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    user_id = Column(SQLAlchemyUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    session_id = Column(SQLAlchemyUUID(as_uuid=True), ForeignKey("chat_sessions.id"), nullable=True)
    
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
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_document_tenant', 'tenant_id'),
        Index('idx_document_user', 'user_id'),
        Index('idx_document_session', 'session_id'),
        Index('idx_document_processed', 'processed'),
    )


class DocumentChunk(Base):
    """Text chunks from processed documents for vector search."""
    __tablename__ = "document_chunks"

    id = Column(SQLAlchemyUUID(as_uuid=True), primary_key=True, default=uuid4)
    document_id = Column(SQLAlchemyUUID(as_uuid=True), ForeignKey("chat_documents.id"), nullable=False)
    
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
        Index('idx_chunk_document', 'document_id'),
        Index('idx_chunk_index', 'chunk_index'),
    )


# Pydantic Models for API

class ChatSessionBase(BaseModel):
    """Base chat session model."""
    title: Optional[str] = Field(None, max_length=200)
    model_config: Optional[Dict[str, Any]] = None
    system_prompt: Optional[str] = None
    context_window: Optional[int] = Field(4000, ge=1000, le=32000)


class ChatSessionCreate(ChatSessionBase):
    """Chat session creation model."""
    pass


class ChatSessionUpdate(BaseModel):
    """Chat session update model."""
    title: Optional[str] = Field(None, max_length=200)
    status: Optional[SessionStatus] = None
    model_config: Optional[Dict[str, Any]] = None
    system_prompt: Optional[str] = None


class ChatSessionResponse(ChatSessionBase):
    """Chat session response model."""
    id: UUID
    tenant_id: UUID
    user_id: UUID
    status: SessionStatus
    created_at: datetime
    updated_at: datetime
    archived_at: Optional[datetime] = None
    
    # Message count (computed)
    message_count: Optional[int] = None

    class Config:
        from_attributes = True


class ChatMessageBase(BaseModel):
    """Base chat message model."""
    message: str = Field(..., min_length=1)
    message_type: MessageType = MessageType.USER
    metadata: Optional[Dict[str, Any]] = None


class ChatMessageCreate(ChatMessageBase):
    """Chat message creation model."""
    session_id: UUID


class ChatMessageResponse(ChatMessageBase):
    """Chat message response model."""
    id: UUID
    session_id: UUID
    user_id: Optional[UUID] = None
    timestamp: datetime
    tokens_used: Optional[int] = None
    processing_time_ms: Optional[int] = None

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
    chunks_count: Optional[int] = None
    uploaded_at: datetime
    processed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ChatSessionWithMessages(ChatSessionResponse):
    """Chat session with messages."""
    messages: List[ChatMessageResponse] = []


class ChatCompletionRequest(BaseModel):
    """Chat completion request."""
    message: str = Field(..., min_length=1, max_length=10000)
    session_id: Optional[UUID] = None  # If None, create new session
    stream: bool = False
    model_config: Optional[Dict[str, Any]] = None
    include_documents: bool = True  # Whether to include uploaded documents in context


class ChatCompletionResponse(BaseModel):
    """Chat completion response."""
    session_id: UUID
    user_message_id: UUID
    assistant_message_id: UUID
    response: str
    tokens_used: Optional[int] = None
    processing_time_ms: Optional[int] = None
    model_info: Optional[Dict[str, Any]] = None
