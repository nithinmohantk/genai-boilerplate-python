"""
Database models for authentication, users, and multi-tenancy.
"""

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID as SQLAlchemyUUID
from sqlalchemy.orm import relationship

from core.database import Base


class UserRole(str, Enum):
    """User roles in the system."""

    SUPER_ADMIN = "super_admin"  # System-wide admin
    TENANT_ADMIN = "tenant_admin"  # Tenant administrator
    TENANT_USER = "tenant_user"  # Regular tenant user
    TENANT_VIEWER = "tenant_viewer"  # Read-only tenant user


class AuthProvider(str, Enum):
    """Authentication providers."""

    EMAIL = "email"
    GOOGLE = "google"
    MICROSOFT = "microsoft"
    APPLE = "apple"


class TenantStatus(str, Enum):
    """Tenant status."""

    ACTIVE = "active"
    SUSPENDED = "suspended"
    PENDING = "pending"
    CANCELLED = "cancelled"


# Database Models


class Tenant(Base):
    """Tenant model for multi-tenancy."""

    __tablename__ = "tenants"

    id = Column(SQLAlchemyUUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(100), nullable=False)
    domain = Column(String(100), unique=True, nullable=False)
    status = Column(String(20), nullable=False, default=TenantStatus.ACTIVE)

    # Configuration
    settings = Column(JSON, nullable=True)  # Tenant-specific settings
    branding = Column(JSON, nullable=True)  # Logo, colors, etc.
    limits = Column(JSON, nullable=True)  # Usage limits, quotas

    # Metadata
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    created_by = Column(SQLAlchemyUUID(as_uuid=True), nullable=True)

    # Relationships
    users = relationship("User", back_populates="tenant", cascade="all, delete-orphan")
    api_keys = relationship(
        "TenantApiKey", back_populates="tenant", cascade="all, delete-orphan"
    )
    chat_sessions = relationship("ChatSession", back_populates="tenant")

    __table_args__ = (
        Index("idx_tenant_domain", "domain"),
        Index("idx_tenant_status", "status"),
        {"extend_existing": True},
    )


class User(Base):
    """User model."""

    __tablename__ = "users"

    id = Column(SQLAlchemyUUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id = Column(
        SQLAlchemyUUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False
    )

    # Basic info
    email = Column(String(255), nullable=False)
    username = Column(String(100), nullable=True)
    full_name = Column(String(200), nullable=True)

    # Authentication
    hashed_password = Column(String(255), nullable=True)  # For email auth
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)

    # Role and permissions
    role = Column(String(20), nullable=False, default=UserRole.TENANT_USER)
    permissions = Column(JSON, nullable=True)  # Additional permissions

    # Profile
    avatar_url = Column(String(500), nullable=True)
    timezone = Column(String(50), nullable=True, default="UTC")
    language = Column(String(10), nullable=True, default="en")
    preferences = Column(JSON, nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    last_login_at = Column(DateTime, nullable=True)

    # Relationships
    tenant = relationship("Tenant", back_populates="users")
    auth_providers = relationship(
        "UserAuthProvider", back_populates="user", cascade="all, delete-orphan"
    )
    chat_sessions = relationship("ChatSession", back_populates="user")
    chat_messages = relationship("ChatMessage", back_populates="user")

    __table_args__ = (
        UniqueConstraint("tenant_id", "email", name="uq_tenant_user_email"),
        Index("idx_user_email", "email"),
        Index("idx_user_tenant_role", "tenant_id", "role"),
        Index("idx_user_active", "is_active"),
    )


class UserAuthProvider(Base):
    """OAuth provider connections for users."""

    __tablename__ = "user_auth_providers"

    id = Column(SQLAlchemyUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(
        SQLAlchemyUUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )

    provider = Column(String(20), nullable=False)  # google, microsoft, apple
    provider_user_id = Column(String(100), nullable=False)  # Provider's user ID
    provider_email = Column(String(255), nullable=True)
    provider_data = Column(JSON, nullable=True)  # Additional provider data

    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships
    user = relationship("User", back_populates="auth_providers")

    __table_args__ = (
        UniqueConstraint("provider", "provider_user_id", name="uq_provider_user"),
        Index("idx_auth_provider_user", "user_id"),
    )


class TenantApiKey(Base):
    """API keys for tenant integrations."""

    __tablename__ = "tenant_api_keys"

    id = Column(SQLAlchemyUUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id = Column(
        SQLAlchemyUUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False
    )

    name = Column(String(100), nullable=False)  # Human-readable name
    key_hash = Column(String(255), nullable=False, unique=True)  # Hashed API key
    key_prefix = Column(
        String(10), nullable=False
    )  # First few chars for identification

    # Configuration
    provider = Column(String(50), nullable=False)  # openai, anthropic, etc.
    is_active = Column(Boolean, default=True, nullable=False)
    usage_limits = Column(JSON, nullable=True)  # Rate limits, quotas

    # Metadata
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    created_by = Column(SQLAlchemyUUID(as_uuid=True), nullable=True)
    last_used_at = Column(DateTime, nullable=True)

    # Relationships
    tenant = relationship("Tenant", back_populates="api_keys")

    __table_args__ = (
        UniqueConstraint("tenant_id", "name", name="uq_tenant_api_key_name"),
        Index("idx_api_key_tenant", "tenant_id"),
        Index("idx_api_key_active", "is_active"),
    )


class RefreshToken(Base):
    """Refresh tokens for JWT authentication."""

    __tablename__ = "refresh_tokens"

    id = Column(SQLAlchemyUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(
        SQLAlchemyUUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )

    token_hash = Column(String(255), nullable=False, unique=True)
    is_revoked = Column(Boolean, default=False, nullable=False)
    expires_at = Column(DateTime, nullable=False)

    # Device/session info
    device_info = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)  # IPv6 compatible
    user_agent = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.now, nullable=False)

    __table_args__ = (
        Index("idx_refresh_token_user", "user_id"),
        Index("idx_refresh_token_expires", "expires_at"),
        Index("idx_refresh_token_revoked", "is_revoked"),
    )


# Pydantic Models for API


class TenantBase(BaseModel):
    """Base tenant model."""

    name: str = Field(..., min_length=1, max_length=100)
    domain: str = Field(..., min_length=3, max_length=100)
    status: TenantStatus = TenantStatus.ACTIVE
    settings: dict[str, Any] | None = None
    branding: dict[str, Any] | None = None
    limits: dict[str, Any] | None = None


class TenantCreate(TenantBase):
    """Tenant creation model."""

    pass


class TenantUpdate(BaseModel):
    """Tenant update model."""

    name: str | None = Field(None, min_length=1, max_length=100)
    status: TenantStatus | None = None
    settings: dict[str, Any] | None = None
    branding: dict[str, Any] | None = None
    limits: dict[str, Any] | None = None


class TenantResponse(TenantBase):
    """Tenant response model."""

    id: UUID
    created_at: datetime
    updated_at: datetime
    created_by: UUID | None = None

    class Config:
        from_attributes = True


class UserBase(BaseModel):
    """Base user model."""

    email: EmailStr
    username: str | None = Field(None, min_length=3, max_length=100)
    full_name: str | None = Field(None, max_length=200)
    role: UserRole = UserRole.TENANT_USER
    is_active: bool = True
    timezone: str = "UTC"
    language: str = "en"
    preferences: dict[str, Any] | None = None


class UserCreate(UserBase):
    """User creation model."""

    tenant_id: UUID
    password: str | None = Field(None, min_length=8, max_length=100)


class UserUpdate(BaseModel):
    """User update model."""

    username: str | None = Field(None, min_length=3, max_length=100)
    full_name: str | None = Field(None, max_length=200)
    role: UserRole | None = None
    is_active: bool | None = None
    timezone: str | None = None
    language: str | None = None
    preferences: dict[str, Any] | None = None
    avatar_url: str | None = None


class UserResponse(UserBase):
    """User response model."""

    id: UUID
    tenant_id: UUID
    is_verified: bool
    avatar_url: str | None = None
    created_at: datetime
    updated_at: datetime
    last_login_at: datetime | None = None

    class Config:
        from_attributes = True


class ApiKeyBase(BaseModel):
    """Base API key model."""

    name: str = Field(..., min_length=1, max_length=100)
    provider: str = Field(..., min_length=1, max_length=50)
    usage_limits: dict[str, Any] | None = None


class ApiKeyCreate(ApiKeyBase):
    """API key creation model."""

    api_key: str = Field(..., min_length=10)  # The actual key value


class ApiKeyResponse(BaseModel):
    """API key response model."""

    id: UUID
    name: str
    provider: str
    key_prefix: str
    is_active: bool
    usage_limits: dict[str, Any] | None = None
    created_at: datetime
    last_used_at: datetime | None = None

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Token response model."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class LoginRequest(BaseModel):
    """Login request model."""

    email: EmailStr
    password: str
    tenant_domain: str | None = None  # If not provided, use default


class AuthProviderCallback(BaseModel):
    """OAuth callback data."""

    provider: AuthProvider
    code: str
    state: str | None = None
    tenant_domain: str | None = None
