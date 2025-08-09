"""
Theme management API routes.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from models.theme import (
    Theme, ThemeCreate, ThemeUpdate, ThemeCategory,
    UserThemeSettings, UserThemeSettingsCreate, UserThemeSettingsUpdate
)
from services.theme_service import ThemeService
from api.auth import get_current_user  # Assuming auth middleware exists
from models.user import User  # Assuming user model exists

router = APIRouter(prefix="/themes", tags=["themes"])


@router.get("/", response_model=List[Theme])
async def get_themes(
    category: Optional[ThemeCategory] = None,
    include_system: bool = True,
    session: AsyncSession = Depends(get_db_session)
):
    """Get all available themes, optionally filtered by category."""
    theme_service = ThemeService(session)
    themes = await theme_service.get_themes(
        category=category,
        include_system=include_system
    )
    return themes


@router.get("/{theme_id}", response_model=Theme)
async def get_theme(
    theme_id: str,
    session: AsyncSession = Depends(get_db_session)
):
    """Get a specific theme by ID."""
    theme_service = ThemeService(session)
    theme = await theme_service.get_theme(theme_id)
    if not theme:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Theme not found"
        )
    return theme


@router.post("/", response_model=Theme, status_code=status.HTTP_201_CREATED)
async def create_theme(
    theme_data: ThemeCreate,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """Create a new custom theme."""
    theme_service = ThemeService(session)
    theme = await theme_service.create_theme(
        theme_data=theme_data,
        created_by=current_user.id
    )
    return theme


@router.put("/{theme_id}", response_model=Theme)
async def update_theme(
    theme_id: str,
    theme_data: ThemeUpdate,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """Update an existing theme (only custom themes can be updated)."""
    theme_service = ThemeService(session)
    theme = await theme_service.update_theme(
        theme_id=theme_id,
        theme_data=theme_data,
        updated_by=current_user.id
    )
    if not theme:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Theme not found or cannot be updated"
        )
    return theme


@router.delete("/{theme_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_theme(
    theme_id: str,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """Delete a custom theme (system themes cannot be deleted)."""
    theme_service = ThemeService(session)
    success = await theme_service.delete_theme(theme_id, deleted_by=current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Theme not found or cannot be deleted"
        )


@router.get("/{theme_id}/css")
async def get_theme_css(
    theme_id: str,
    display_mode: str = "light",
    session: AsyncSession = Depends(get_db_session)
):
    """Get generated CSS for a theme."""
    theme_service = ThemeService(session)
    css = await theme_service.generate_theme_css(theme_id, display_mode)
    if css is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Theme not found"
        )
    
    return {
        "theme_id": theme_id,
        "display_mode": display_mode,
        "css": css
    }


@router.get("/categories/", response_model=List[str])
async def get_theme_categories():
    """Get all available theme categories."""
    return [category.value for category in ThemeCategory]


# User Theme Settings Endpoints

@router.get("/user/settings", response_model=UserThemeSettings)
async def get_user_theme_settings(
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """Get current user's theme settings."""
    theme_service = ThemeService(session)
    settings = await theme_service.get_user_theme_settings(current_user.id)
    if not settings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User theme settings not found"
        )
    return settings


@router.post("/user/settings", response_model=UserThemeSettings, status_code=status.HTTP_201_CREATED)
async def create_user_theme_settings(
    settings_data: UserThemeSettingsCreate,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """Create or update user theme settings."""
    theme_service = ThemeService(session)
    settings = await theme_service.create_user_theme_settings(
        user_id=current_user.id,
        settings_data=settings_data
    )
    return settings


@router.put("/user/settings", response_model=UserThemeSettings)
async def update_user_theme_settings(
    settings_data: UserThemeSettingsUpdate,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """Update user theme settings."""
    theme_service = ThemeService(session)
    settings = await theme_service.update_user_theme_settings(
        user_id=current_user.id,
        settings_data=settings_data
    )
    if not settings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User theme settings not found"
        )
    return settings


@router.post("/user/apply/{theme_id}", response_model=UserThemeSettings)
async def apply_theme_to_user(
    theme_id: str,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """Apply a theme to the current user."""
    theme_service = ThemeService(session)
    settings = await theme_service.apply_theme_to_user(
        user_id=current_user.id,
        theme_id=theme_id
    )
    if not settings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Theme not found or could not be applied"
        )
    return settings


@router.get("/user/current-css")
async def get_current_user_theme_css(
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """Get CSS for current user's applied theme."""
    theme_service = ThemeService(session)
    css = await theme_service.get_user_theme_css(current_user.id)
    if css is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User theme not found"
        )
    
    return {
        "user_id": current_user.id,
        "css": css
    }


@router.get("/analytics/{theme_id}")
async def get_theme_analytics(
    theme_id: str,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)  # Admin check could be added here
):
    """Get analytics for a theme (usage statistics)."""
    theme_service = ThemeService(session)
    analytics = await theme_service.get_theme_usage_analytics(theme_id)
    if analytics is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Theme not found"
        )
    
    return analytics


@router.post("/{theme_id}/record-usage")
async def record_theme_usage(
    theme_id: str,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """Record theme usage for analytics."""
    theme_service = ThemeService(session)
    await theme_service.record_theme_usage(theme_id, current_user.id)
    
    return {"message": "Theme usage recorded"}


@router.get("/{theme_id}/accessibility-check")
async def check_theme_accessibility(
    theme_id: str,
    session: AsyncSession = Depends(get_db_session)
):
    """Check accessibility compliance for a theme."""
    theme_service = ThemeService(session)
    compliance = await theme_service.check_accessibility_compliance(theme_id)
    if compliance is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Theme not found"
        )
    
    return compliance
