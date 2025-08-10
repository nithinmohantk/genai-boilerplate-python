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
        # For now, return mock themes since we need to resolve model dependencies
        mock_themes = [
            {
                "id": "corporate_blue",
                "name": "corporate_blue", 
                "display_name": "Corporate Blue",
                "description": "Professional business environment with sophisticated blue tones",
                "category": "professional"
            },
            {
                "id": "executive_dark",
                "name": "executive_dark",
                "display_name": "Executive Dark", 
                "description": "Sophisticated dark theme for executives and premium users",
                "category": "professional"
            },
            {
                "id": "minimalist_light",
                "name": "minimalist_light",
                "display_name": "Minimalist Light",
                "description": "Clean, distraction-free interface for focused work", 
                "category": "professional"
            },
            {
                "id": "focus_mode",
                "name": "focus_mode",
                "display_name": "Focus Mode",
                "description": "High contrast, productivity-focused theme for deep work",
                "category": "professional"
            },
            {
                "id": "creative_studio",
                "name": "creative_studio", 
                "display_name": "Creative Studio",
                "description": "Design and creative work optimized with inspiring colors",
                "category": "creative"
            },
            {
                "id": "tech_console",
                "name": "tech_console",
                "display_name": "Tech Console", 
                "description": "Developer-friendly theme with syntax highlighting optimization",
                "category": "industry"
            },
            {
                "id": "medical_professional", 
                "name": "medical_professional",
                "display_name": "Medical Professional",
                "description": "Healthcare industry optimized theme with calming colors",
                "category": "industry"
            },
            {
                "id": "financial_dashboard",
                "name": "financial_dashboard",
                "display_name": "Financial Dashboard",
                "description": "Finance industry professional theme with data visualization focus", 
                "category": "industry"
            },
            {
                "id": "high_contrast",
                "name": "high_contrast",
                "display_name": "High Contrast",
                "description": "WCAG AAA accessibility compliant high contrast theme",
                "category": "accessibility"
            },
            {
                "id": "night_shift",
                "name": "night_shift", 
                "display_name": "Night Shift",
                "description": "Blue light reduced theme for comfortable evening use",
                "category": "accessibility"
            },
            {
                "id": "accessibility_plus",
                "name": "accessibility_plus",
                "display_name": "Accessibility Plus", 
                "description": "Enhanced readability and navigation for all users",
                "category": "accessibility"
            },
            {
                "id": "warm_reading",
                "name": "warm_reading",
                "display_name": "Warm Reading",
                "description": "Comfortable warm theme for long conversations and reading",
                "category": "accessibility"
            }
        ]
        return mock_themes
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching themes: {str(e)}"
        )


@router.get("/categories/")
async def get_theme_categories():
    """Get all available theme categories."""
    return ["professional", "creative", "industry", "accessibility"]


@router.get("/{theme_id}")
async def get_theme(theme_id: str, session: AsyncSession = Depends(get_db_session)):
    """Get a specific theme by ID.""" 
    mock_themes = {
        "corporate_blue": {
            "id": "corporate_blue",
            "name": "corporate_blue",
            "display_name": "Corporate Blue", 
            "description": "Professional business environment with sophisticated blue tones",
            "category": "professional",
            "color_scheme": {
                "light": {
                    "primary": "#1e40af",
                    "secondary": "#3b82f6",
                    "background": "#ffffff", 
                    "text": "#0f172a"
                },
                "dark": {
                    "primary": "#6366f1",
                    "secondary": "#8b5cf6",
                    "background": "#0f172a",
                    "text": "#f1f5f9"
                }
            }
        }
    }
    
    theme = mock_themes.get(theme_id)
    if not theme:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Theme not found"
        )
    return theme
