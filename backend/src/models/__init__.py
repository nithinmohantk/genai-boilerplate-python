"""
Models package initialization.
Imports all database models to ensure SQLAlchemy can set up relationships correctly.
"""

# Import all models to ensure they are registered with SQLAlchemy
from .auth import Tenant, TenantApiKey, User, UserAuthProvider
from .chat import ChatMessage, ChatSession
from .theme import Theme, UserSettings, UserThemeHistory

# Make models available at package level
__all__ = [
    # Auth models
    "Tenant",
    "User",
    "UserAuthProvider",
    "TenantApiKey",
    # Theme models
    "Theme",
    "UserSettings",
    "UserThemeHistory",
    # Chat models
    "ChatSession",
    "ChatMessage",
]
