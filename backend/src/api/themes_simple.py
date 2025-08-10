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
        },
        "executive_dark": {
            "id": "executive_dark",
            "name": "executive_dark",
            "display_name": "Executive Dark", 
            "description": "Sophisticated dark theme for executives and premium users",
            "category": "professional",
            "color_scheme": {
                "light": {
                    "primary": "#374151",
                    "secondary": "#6b7280",
                    "background": "#f9fafb", 
                    "text": "#111827"
                },
                "dark": {
                    "primary": "#d1d5db",
                    "secondary": "#9ca3af",
                    "background": "#111827",
                    "text": "#f9fafb"
                }
            }
        },
        "minimalist_light": {
            "id": "minimalist_light",
            "name": "minimalist_light",
            "display_name": "Minimalist Light",
            "description": "Clean, distraction-free interface for focused work", 
            "category": "professional",
            "color_scheme": {
                "light": {
                    "primary": "#6b7280",
                    "secondary": "#9ca3af",
                    "background": "#ffffff", 
                    "text": "#374151"
                },
                "dark": {
                    "primary": "#9ca3af",
                    "secondary": "#6b7280",
                    "background": "#1f2937",
                    "text": "#f3f4f6"
                }
            }
        },
        "focus_mode": {
            "id": "focus_mode",
            "name": "focus_mode",
            "display_name": "Focus Mode",
            "description": "High contrast, productivity-focused theme for deep work",
            "category": "professional",
            "color_scheme": {
                "light": {
                    "primary": "#000000",
                    "secondary": "#374151",
                    "background": "#ffffff", 
                    "text": "#000000"
                },
                "dark": {
                    "primary": "#ffffff",
                    "secondary": "#d1d5db",
                    "background": "#000000",
                    "text": "#ffffff"
                }
            }
        },
        "creative_studio": {
            "id": "creative_studio",
            "name": "creative_studio", 
            "display_name": "Creative Studio",
            "description": "Design and creative work optimized with inspiring colors",
            "category": "creative",
            "color_scheme": {
                "light": {
                    "primary": "#ec4899",
                    "secondary": "#f97316",
                    "background": "#fef7ff", 
                    "text": "#831843"
                },
                "dark": {
                    "primary": "#f472b6",
                    "secondary": "#fb923c",
                    "background": "#581c87",
                    "text": "#fdf4ff"
                }
            }
        },
        "tech_console": {
            "id": "tech_console",
            "name": "tech_console",
            "display_name": "Tech Console", 
            "description": "Developer-friendly theme with syntax highlighting optimization",
            "category": "industry",
            "color_scheme": {
                "light": {
                    "primary": "#059669",
                    "secondary": "#0d9488",
                    "background": "#f0fdf4", 
                    "text": "#064e3b"
                },
                "dark": {
                    "primary": "#10b981",
                    "secondary": "#14b8a6",
                    "background": "#064e3b",
                    "text": "#d1fae5"
                }
            }
        },
        "medical_professional": {
            "id": "medical_professional",
            "name": "medical_professional",
            "display_name": "Medical Professional",
            "description": "Healthcare industry optimized theme with calming colors",
            "category": "industry",
            "color_scheme": {
                "light": {
                    "primary": "#0ea5e9",
                    "secondary": "#06b6d4",
                    "background": "#f0f9ff", 
                    "text": "#0c4a6e"
                },
                "dark": {
                    "primary": "#38bdf8",
                    "secondary": "#22d3ee",
                    "background": "#0c4a6e",
                    "text": "#e0f2fe"
                }
            }
        },
        "financial_dashboard": {
            "id": "financial_dashboard",
            "name": "financial_dashboard",
            "display_name": "Financial Dashboard",
            "description": "Finance industry professional theme with data visualization focus", 
            "category": "industry",
            "color_scheme": {
                "light": {
                    "primary": "#7c3aed",
                    "secondary": "#a855f7",
                    "background": "#faf5ff", 
                    "text": "#581c87"
                },
                "dark": {
                    "primary": "#a78bfa",
                    "secondary": "#c084fc",
                    "background": "#581c87",
                    "text": "#f3e8ff"
                }
            }
        },
        "high_contrast": {
            "id": "high_contrast",
            "name": "high_contrast",
            "display_name": "High Contrast",
            "description": "WCAG AAA accessibility compliant high contrast theme",
            "category": "accessibility",
            "color_scheme": {
                "light": {
                    "primary": "#000000",
                    "secondary": "#1f2937",
                    "background": "#ffffff", 
                    "text": "#000000"
                },
                "dark": {
                    "primary": "#ffffff",
                    "secondary": "#f3f4f6",
                    "background": "#000000",
                    "text": "#ffffff"
                }
            }
        },
        "night_shift": {
            "id": "night_shift",
            "name": "night_shift", 
            "display_name": "Night Shift",
            "description": "Blue light reduced theme for comfortable evening use",
            "category": "accessibility",
            "color_scheme": {
                "light": {
                    "primary": "#dc2626",
                    "secondary": "#ea580c",
                    "background": "#fef2f2", 
                    "text": "#7f1d1d"
                },
                "dark": {
                    "primary": "#fca5a5",
                    "secondary": "#fdba74",
                    "background": "#7f1d1d",
                    "text": "#fef2f2"
                }
            }
        },
        "accessibility_plus": {
            "id": "accessibility_plus",
            "name": "accessibility_plus",
            "display_name": "Accessibility Plus", 
            "description": "Enhanced readability and navigation for all users",
            "category": "accessibility",
            "color_scheme": {
                "light": {
                    "primary": "#1d4ed8",
                    "secondary": "#1e40af",
                    "background": "#ffffff", 
                    "text": "#1e293b"
                },
                "dark": {
                    "primary": "#60a5fa",
                    "secondary": "#3b82f6",
                    "background": "#1e293b",
                    "text": "#f1f5f9"
                }
            }
        },
        "warm_reading": {
            "id": "warm_reading",
            "name": "warm_reading",
            "display_name": "Warm Reading",
            "description": "Comfortable warm theme for long conversations and reading",
            "category": "accessibility",
            "color_scheme": {
                "light": {
                    "primary": "#92400e",
                    "secondary": "#b45309",
                    "background": "#fffbeb", 
                    "text": "#78350f"
                },
                "dark": {
                    "primary": "#fbbf24",
                    "secondary": "#f59e0b",
                    "background": "#78350f",
                    "text": "#fffbeb"
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
