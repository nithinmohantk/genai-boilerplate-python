"""
Database models for theming and user settings functionality.
"""

from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, List
from uuid import UUID, uuid4

from pydantic import BaseModel, Field
from sqlalchemy import (
    Column, String, Text, DateTime, JSON, Boolean, Integer, Float,
    ForeignKey, Index, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID as SQLAlchemyUUID
from sqlalchemy.orm import relationship

from core.database import Base


class ThemeCategory(str, Enum):
    """Theme categories for organization."""
    PROFESSIONAL = "professional"
    CREATIVE = "creative" 
    INDUSTRY = "industry"
    ACCESSIBILITY = "accessibility"
    SYSTEM = "system"


class DisplayMode(str, Enum):
    """Display mode preferences."""
    LIGHT = "light"
    DARK = "dark"
    AUTO = "auto"  # System preference


class FontSize(str, Enum):
    """Font size options."""
    XS = "xs"  # 12px
    SM = "sm"  # 14px
    MD = "md"  # 16px (default)
    LG = "lg"  # 18px
    XL = "xl"  # 20px
    XXL = "xxl" # 24px


class FontFamily(str, Enum):
    """Font family options."""
    SYSTEM = "system"  # System default
    INTER = "inter"    # Modern, clean
    ROBOTO = "roboto"  # Google's readable font
    OPEN_SANS = "open_sans"  # Highly legible
    ACCESSIBILITY = "accessibility"  # High readability font


class ChatLayout(str, Enum):
    """Chat layout density options."""
    COMPACT = "compact"
    COMFORTABLE = "comfortable"
    SPACIOUS = "spacious"


class MessageStyle(str, Enum):
    """Message bubble styles."""
    BUBBLES = "bubbles"
    CARDS = "cards"
    MINIMAL = "minimal"
    PROFESSIONAL = "professional"


# Database Models

class Theme(Base):
    """Theme definitions with color schemes and styling."""
    __tablename__ = "themes"

    id = Column(SQLAlchemyUUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # Theme identity
    name = Column(String(100), nullable=False)
    display_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(20), nullable=False, default=ThemeCategory.PROFESSIONAL)
    
    # Theme configuration
    color_scheme = Column(JSON, nullable=False)  # Complete color palette
    typography = Column(JSON, nullable=True)     # Font settings
    layout_config = Column(JSON, nullable=True)  # Layout specifications
    component_styles = Column(JSON, nullable=True)  # Component-specific styles
    
    # Theme metadata
    is_system = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    supports_dark_mode = Column(Boolean, default=True, nullable=False)
    accessibility_features = Column(JSON, nullable=True)
    
    # Usage and versioning
    version = Column(String(10), nullable=False, default="1.0")
    usage_count = Column(Integer, default=0, nullable=False)
    
    # Preview and assets
    preview_image_url = Column(String(500), nullable=True)
    css_variables = Column(JSON, nullable=True)  # CSS custom properties
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    __table_args__ = (
        Index('idx_theme_category', 'category'),
        Index('idx_theme_system', 'is_system'),
        Index('idx_theme_active', 'is_active'),
        UniqueConstraint('name', name='uq_theme_name'),
    )


class UserSettings(Base):
    """User preferences and settings storage."""
    __tablename__ = "user_settings"

    id = Column(SQLAlchemyUUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id = Column(SQLAlchemyUUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    user_id = Column(SQLAlchemyUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Theme preferences
    active_theme_id = Column(SQLAlchemyUUID(as_uuid=True), ForeignKey("themes.id"), nullable=True)
    display_mode = Column(String(10), nullable=False, default=DisplayMode.AUTO)
    
    # Typography preferences
    font_size = Column(String(5), nullable=False, default=FontSize.MD)
    font_family = Column(String(20), nullable=False, default=FontFamily.SYSTEM)
    line_height = Column(Float, nullable=False, default=1.5)
    
    # Chat interface preferences
    chat_layout = Column(String(15), nullable=False, default=ChatLayout.COMFORTABLE)
    message_style = Column(String(20), nullable=False, default=MessageStyle.BUBBLES)
    show_timestamps = Column(Boolean, default=True, nullable=False)
    show_avatars = Column(Boolean, default=True, nullable=False)
    compact_mode = Column(Boolean, default=False, nullable=False)
    
    # Accessibility preferences
    high_contrast = Column(Boolean, default=False, nullable=False)
    reduce_motion = Column(Boolean, default=False, nullable=False)
    screen_reader_optimized = Column(Boolean, default=False, nullable=False)
    
    # Notification preferences
    sound_enabled = Column(Boolean, default=True, nullable=False)
    desktop_notifications = Column(Boolean, default=True, nullable=False)
    email_notifications = Column(Boolean, default=False, nullable=False)
    
    # Chat behavior preferences
    auto_scroll = Column(Boolean, default=True, nullable=False)
    typing_indicators = Column(Boolean, default=True, nullable=False)
    message_reactions = Column(Boolean, default=True, nullable=False)
    quick_replies = Column(Boolean, default=True, nullable=False)
    
    # Privacy preferences
    save_chat_history = Column(Boolean, default=True, nullable=False)
    analytics_consent = Column(Boolean, default=False, nullable=False)
    
    # Custom settings (JSON for extensibility)
    custom_preferences = Column(JSON, nullable=True)
    
    # Backup and sync
    settings_backup = Column(JSON, nullable=True)  # Last known good config
    last_sync = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    tenant = relationship("Tenant")
    user = relationship("User")
    theme = relationship("Theme")

    __table_args__ = (
        Index('idx_user_settings_user', 'user_id'),
        Index('idx_user_settings_tenant', 'tenant_id'),
        UniqueConstraint('user_id', name='uq_user_settings_user'),
    )


class UserThemeHistory(Base):
    """Track user theme usage and preferences over time."""
    __tablename__ = "user_theme_history"

    id = Column(SQLAlchemyUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(SQLAlchemyUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    theme_id = Column(SQLAlchemyUUID(as_uuid=True), ForeignKey("themes.id"), nullable=False)
    
    # Usage tracking
    applied_at = Column(DateTime, default=datetime.now, nullable=False)
    duration_minutes = Column(Integer, nullable=True)  # How long theme was active
    
    # Context
    applied_via = Column(String(50), nullable=True)  # 'manual', 'auto', 'preview'
    device_info = Column(JSON, nullable=True)  # Device/browser context
    
    # Relationships
    user = relationship("User")
    theme = relationship("Theme")

    __table_args__ = (
        Index('idx_theme_history_user', 'user_id'),
        Index('idx_theme_history_theme', 'theme_id'),
        Index('idx_theme_history_applied', 'applied_at'),
    )


# Pydantic Models for API

class ThemeBase(BaseModel):
    """Base theme model."""
    name: str = Field(..., min_length=1, max_length=100)
    display_name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    category: ThemeCategory = ThemeCategory.PROFESSIONAL
    color_scheme: Dict[str, Any]
    supports_dark_mode: bool = True
    accessibility_features: Optional[Dict[str, Any]] = None


class ThemeCreate(ThemeBase):
    """Theme creation model."""
    typography: Optional[Dict[str, Any]] = None
    layout_config: Optional[Dict[str, Any]] = None
    component_styles: Optional[Dict[str, Any]] = None
    css_variables: Optional[Dict[str, Any]] = None
    version: str = "1.0"


class ThemeUpdate(BaseModel):
    """Theme update model."""
    display_name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    color_scheme: Optional[Dict[str, Any]] = None
    typography: Optional[Dict[str, Any]] = None
    layout_config: Optional[Dict[str, Any]] = None
    component_styles: Optional[Dict[str, Any]] = None
    accessibility_features: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class ThemeResponse(ThemeBase):
    """Theme response model."""
    id: UUID
    is_system: bool
    is_active: bool
    version: str
    usage_count: int
    preview_image_url: Optional[str] = None
    css_variables: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserSettingsBase(BaseModel):
    """Base user settings model."""
    display_mode: DisplayMode = DisplayMode.AUTO
    font_size: FontSize = FontSize.MD
    font_family: FontFamily = FontFamily.SYSTEM
    line_height: float = Field(1.5, ge=1.0, le=3.0)
    chat_layout: ChatLayout = ChatLayout.COMFORTABLE
    message_style: MessageStyle = MessageStyle.BUBBLES
    show_timestamps: bool = True
    show_avatars: bool = True
    compact_mode: bool = False
    high_contrast: bool = False
    reduce_motion: bool = False
    screen_reader_optimized: bool = False


class UserSettingsCreate(UserSettingsBase):
    """User settings creation model."""
    active_theme_id: Optional[UUID] = None


class UserSettingsUpdate(BaseModel):
    """User settings update model."""
    active_theme_id: Optional[UUID] = None
    display_mode: Optional[DisplayMode] = None
    font_size: Optional[FontSize] = None
    font_family: Optional[FontFamily] = None
    line_height: Optional[float] = Field(None, ge=1.0, le=3.0)
    chat_layout: Optional[ChatLayout] = None
    message_style: Optional[MessageStyle] = None
    show_timestamps: Optional[bool] = None
    show_avatars: Optional[bool] = None
    compact_mode: Optional[bool] = None
    high_contrast: Optional[bool] = None
    reduce_motion: Optional[bool] = None
    screen_reader_optimized: Optional[bool] = None
    sound_enabled: Optional[bool] = None
    desktop_notifications: Optional[bool] = None
    email_notifications: Optional[bool] = None
    auto_scroll: Optional[bool] = None
    typing_indicators: Optional[bool] = None
    message_reactions: Optional[bool] = None
    quick_replies: Optional[bool] = None
    save_chat_history: Optional[bool] = None
    analytics_consent: Optional[bool] = None
    custom_preferences: Optional[Dict[str, Any]] = None


class UserSettingsResponse(UserSettingsBase):
    """User settings response model."""
    id: UUID
    tenant_id: UUID
    user_id: UUID
    active_theme_id: Optional[UUID] = None
    theme: Optional[ThemeResponse] = None
    sound_enabled: bool
    desktop_notifications: bool
    email_notifications: bool
    auto_scroll: bool
    typing_indicators: bool
    message_reactions: bool
    quick_replies: bool
    save_chat_history: bool
    analytics_consent: bool
    custom_preferences: Optional[Dict[str, Any]] = None
    last_sync: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ThemePreviewRequest(BaseModel):
    """Theme preview request."""
    theme_id: UUID
    display_mode: Optional[DisplayMode] = None
    font_size: Optional[FontSize] = None


class ThemePreviewResponse(BaseModel):
    """Theme preview response with generated CSS."""
    theme: ThemeResponse
    generated_css: str
    preview_html: str
    accessibility_score: Optional[int] = None  # 0-100 accessibility rating


class SettingsExportResponse(BaseModel):
    """Settings export response."""
    user_settings: UserSettingsResponse
    theme_preferences: List[str]  # Theme names used by user
    export_timestamp: datetime
    version: str = "1.0"


class SettingsImportRequest(BaseModel):
    """Settings import request."""
    settings_data: Dict[str, Any]
    overwrite_existing: bool = False
    import_themes: bool = True


class ThemeSearchRequest(BaseModel):
    """Theme search and filtering request."""
    category: Optional[ThemeCategory] = None
    supports_dark_mode: Optional[bool] = None
    accessibility_required: Optional[bool] = None
    search_term: Optional[str] = Field(None, max_length=100)
    limit: int = Field(20, ge=1, le=100)


class AccessibilityCheckResponse(BaseModel):
    """Accessibility compliance check response."""
    theme_id: UUID
    wcag_aa_compliant: bool
    wcag_aaa_compliant: bool
    contrast_ratios: Dict[str, float]
    accessibility_issues: List[str]
    recommendations: List[str]
    overall_score: int  # 0-100
