"""
Simplified theme management API routes without authentication.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db_session

router = APIRouter(tags=["themes"])


@router.get("/")
async def get_themes(session: AsyncSession = Depends(get_db_session)):
    """Get all available themes (simplified version)."""
    try:
        from services.theme_service import ThemeService

        theme_service = ThemeService(session)
        themes = await theme_service.get_themes()

        # Convert theme objects to dictionary format
        theme_list = []
        for theme in themes:
            theme_dict = {
                "id": str(theme.id),
                "name": theme.name,
                "display_name": theme.display_name,
                "description": theme.description,
                "category": theme.category,
                "supports_dark_mode": theme.supports_dark_mode,
                "color_scheme": theme.color_scheme,
                "accessibility_features": theme.accessibility_features,
                "css_variables": theme.css_variables,
                "is_system": theme.is_system,
                "is_active": theme.is_active,
                "usage_count": theme.usage_count,
            }
            theme_list.append(theme_dict)

        return theme_list

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching themes: {str(e)}",
        ) from e


@router.get("/categories/")
async def get_theme_categories():
    """Get all available theme categories."""
    return ["professional", "creative", "industry", "accessibility", "modern"]


@router.get("/{theme_id}")
async def get_theme(theme_id: str, session: AsyncSession = Depends(get_db_session)):
    """Get a specific theme by ID or name."""
    try:
        from services.theme_service import ThemeService

        theme_service = ThemeService(session)

        # Try to get theme by ID first (UUID format)
        try:
            from uuid import UUID

            # If it's a valid UUID, search by ID
            uuid_obj = UUID(theme_id)
            theme = await theme_service.get_theme(uuid_obj)
        except ValueError:
            # If not a UUID, try to find by name
            all_themes = await theme_service.get_themes()
            theme = next((t for t in all_themes if t.name == theme_id), None)

        if not theme:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Theme not found"
            )

        # Convert theme object to dictionary format
        theme_dict = {
            "id": str(theme.id),
            "name": theme.name,
            "display_name": theme.display_name,
            "description": theme.description,
            "category": theme.category,
            "supports_dark_mode": theme.supports_dark_mode,
            "color_scheme": theme.color_scheme,
            "accessibility_features": theme.accessibility_features,
            "css_variables": theme.css_variables,
            "is_system": theme.is_system,
            "is_active": theme.is_active,
            "usage_count": theme.usage_count,
        }

        return theme_dict

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching theme: {str(e)}",
        ) from e
