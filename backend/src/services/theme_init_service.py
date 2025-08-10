"""
Theme initialization service for creating default professional themes.
"""

import logging
from typing import Any

from models.theme import Theme, ThemeCategory, ThemeCreate
from services.theme_service import ThemeService

logger = logging.getLogger(__name__)


class ThemeInitService:
    """Service for initializing default system themes."""

    def __init__(self, theme_service: ThemeService):
        self.theme_service = theme_service

    async def create_default_themes(self) -> list[Theme]:
        """Create all default system themes."""
        try:
            themes_data = self._get_theme_definitions()
            created_themes = []

            for theme_data in themes_data:
                # Check if theme already exists
                existing_themes = await self.theme_service.get_themes()
                theme_exists = any(
                    theme.name == theme_data["name"] for theme in existing_themes
                )

                if not theme_exists:
                    theme_create = ThemeCreate(**theme_data)
                    theme = await self.theme_service.create_theme(
                        theme_data=theme_create, is_system=True
                    )
                    created_themes.append(theme)
                    logger.info(f"Created system theme: {theme.name}")

            logger.info(f"Created {len(created_themes)} default themes")
            return created_themes

        except Exception as e:
            logger.error(f"Error creating default themes: {e}")
            return []

    def _get_theme_definitions(self) -> list[dict[str, Any]]:
        """Get definitions for all default themes."""
        return [
            # 1. Corporate Blue - Professional business environment
            {
                "name": "corporate_blue",
                "display_name": "Corporate Blue",
                "description": "Professional business environment with sophisticated blue tones",
                "category": ThemeCategory.PROFESSIONAL,
                "color_scheme": {
                    "light": {
                        "primary": "#1e40af",  # Blue-700
                        "secondary": "#3b82f6",  # Blue-500
                        "accent": "#60a5fa",  # Blue-400
                        "background": "#ffffff",  # White
                        "surface": "#f8fafc",  # Slate-50
                        "surface_variant": "#e2e8f0",  # Slate-200
                        "text": "#0f172a",  # Slate-900
                        "text_secondary": "#475569",  # Slate-600
                        "text_muted": "#94a3b8",  # Slate-400
                        "border": "#e2e8f0",  # Slate-200
                        "success": "#10b981",  # Emerald-500
                        "warning": "#f59e0b",  # Amber-500
                        "error": "#ef4444",  # Red-500
                        "info": "#3b82f6",  # Blue-500
                    },
                    "dark": {
                        "primary": "#3b82f6",  # Blue-500
                        "secondary": "#60a5fa",  # Blue-400
                        "accent": "#93c5fd",  # Blue-300
                        "background": "#0f172a",  # Slate-900
                        "surface": "#1e293b",  # Slate-800
                        "surface_variant": "#334155",  # Slate-700
                        "text": "#f8fafc",  # Slate-50
                        "text_secondary": "#cbd5e1",  # Slate-300
                        "text_muted": "#64748b",  # Slate-500
                        "border": "#334155",  # Slate-700
                        "success": "#10b981",  # Emerald-500
                        "warning": "#f59e0b",  # Amber-500
                        "error": "#ef4444",  # Red-500
                        "info": "#3b82f6",  # Blue-500
                    },
                },
                "supports_dark_mode": True,
                "accessibility_features": {
                    "high_contrast": True,
                    "focus_indicators": True,
                    "reduced_motion": True,
                },
                "css_variables": {
                    "border-radius": "6px",
                    "shadow": "0 1px 3px 0 rgb(0 0 0 / 0.1)",
                    "shadow-lg": "0 10px 15px -3px rgb(0 0 0 / 0.1)",
                },
            },
            # 2. Executive Dark - Sophisticated dark theme
            {
                "name": "executive_dark",
                "display_name": "Executive Dark",
                "description": "Sophisticated dark theme for executives and premium users",
                "category": ThemeCategory.PROFESSIONAL,
                "color_scheme": {
                    "light": {
                        "primary": "#111827",  # Gray-900
                        "secondary": "#374151",  # Gray-700
                        "accent": "#d97706",  # Amber-600
                        "background": "#f9fafb",  # Gray-50
                        "surface": "#ffffff",  # White
                        "surface_variant": "#f3f4f6",  # Gray-100
                        "text": "#111827",  # Gray-900
                        "text_secondary": "#4b5563",  # Gray-600
                        "text_muted": "#9ca3af",  # Gray-400
                        "border": "#e5e7eb",  # Gray-200
                        "success": "#059669",  # Emerald-600
                        "warning": "#d97706",  # Amber-600
                        "error": "#dc2626",  # Red-600
                        "info": "#2563eb",  # Blue-600
                    },
                    "dark": {
                        "primary": "#d97706",  # Amber-600
                        "secondary": "#f59e0b",  # Amber-500
                        "accent": "#fbbf24",  # Amber-400
                        "background": "#111827",  # Gray-900
                        "surface": "#1f2937",  # Gray-800
                        "surface_variant": "#374151",  # Gray-700
                        "text": "#f9fafb",  # Gray-50
                        "text_secondary": "#d1d5db",  # Gray-300
                        "text_muted": "#6b7280",  # Gray-500
                        "border": "#374151",  # Gray-700
                        "success": "#10b981",  # Emerald-500
                        "warning": "#f59e0b",  # Amber-500
                        "error": "#f87171",  # Red-400
                        "info": "#60a5fa",  # Blue-400
                    },
                },
                "supports_dark_mode": True,
                "accessibility_features": {
                    "high_contrast": True,
                    "focus_indicators": True,
                    "premium_features": True,
                },
            },
            # 3. Minimalist Light - Clean, distraction-free
            {
                "name": "minimalist_light",
                "display_name": "Minimalist Light",
                "description": "Clean, distraction-free interface for focused work",
                "category": ThemeCategory.PROFESSIONAL,
                "color_scheme": {
                    "light": {
                        "primary": "#000000",  # Black
                        "secondary": "#525252",  # Gray-500
                        "accent": "#737373",  # Gray-500
                        "background": "#ffffff",  # White
                        "surface": "#fafafa",  # Gray-50
                        "surface_variant": "#f5f5f5",  # Gray-100
                        "text": "#000000",  # Black
                        "text_secondary": "#525252",  # Gray-500
                        "text_muted": "#a3a3a3",  # Gray-400
                        "border": "#e5e5e5",  # Gray-200
                        "success": "#22c55e",  # Green-500
                        "warning": "#f97316",  # Orange-500
                        "error": "#ef4444",  # Red-500
                        "info": "#6366f1",  # Indigo-500
                    },
                    "dark": {
                        "primary": "#ffffff",  # White
                        "secondary": "#a3a3a3",  # Gray-400
                        "accent": "#737373",  # Gray-500
                        "background": "#0a0a0a",  # Near black
                        "surface": "#171717",  # Gray-900
                        "surface_variant": "#262626",  # Gray-800
                        "text": "#ffffff",  # White
                        "text_secondary": "#a3a3a3",  # Gray-400
                        "text_muted": "#525252",  # Gray-600
                        "border": "#262626",  # Gray-800
                        "success": "#22c55e",  # Green-500
                        "warning": "#f97316",  # Orange-500
                        "error": "#ef4444",  # Red-500
                        "info": "#6366f1",  # Indigo-500
                    },
                },
                "supports_dark_mode": True,
                "accessibility_features": {
                    "minimal_distractions": True,
                    "focus_mode": True,
                },
            },
            # 4. Focus Mode - High contrast, productivity-focused
            {
                "name": "focus_mode",
                "display_name": "Focus Mode",
                "description": "High contrast, productivity-focused theme for deep work",
                "category": ThemeCategory.PROFESSIONAL,
                "color_scheme": {
                    "light": {
                        "primary": "#7c2d12",  # Orange-800
                        "secondary": "#ea580c",  # Orange-600
                        "accent": "#fb923c",  # Orange-400
                        "background": "#fffbeb",  # Amber-50
                        "surface": "#ffffff",  # White
                        "surface_variant": "#fef3c7",  # Amber-100
                        "text": "#7c2d12",  # Orange-800
                        "text_secondary": "#92400e",  # Amber-700
                        "text_muted": "#d97706",  # Amber-600
                        "border": "#fbbf24",  # Amber-400
                        "success": "#166534",  # Green-800
                        "warning": "#92400e",  # Amber-700
                        "error": "#991b1b",  # Red-800
                        "info": "#1e40af",  # Blue-800
                    },
                    "dark": {
                        "primary": "#fb923c",  # Orange-400
                        "secondary": "#f97316",  # Orange-500
                        "accent": "#fdba74",  # Orange-300
                        "background": "#0c0a09",  # Stone-950
                        "surface": "#1c1917",  # Stone-900
                        "surface_variant": "#292524",  # Stone-800
                        "text": "#fbbf24",  # Amber-400
                        "text_secondary": "#fcd34d",  # Amber-300
                        "text_muted": "#a16207",  # Amber-700
                        "border": "#451a03",  # Amber-900
                        "success": "#22c55e",  # Green-500
                        "warning": "#f59e0b",  # Amber-500
                        "error": "#f87171",  # Red-400
                        "info": "#60a5fa",  # Blue-400
                    },
                },
                "supports_dark_mode": True,
                "accessibility_features": {
                    "ultra_high_contrast": True,
                    "focus_indicators": True,
                    "reduced_motion": True,
                },
            },
            # 5. Tech Console - Developer-friendly
            {
                "name": "tech_console",
                "display_name": "Tech Console",
                "description": "Developer-friendly theme with syntax highlighting optimization",
                "category": ThemeCategory.INDUSTRY,
                "color_scheme": {
                    "light": {
                        "primary": "#059669",  # Emerald-600
                        "secondary": "#10b981",  # Emerald-500
                        "accent": "#34d399",  # Emerald-400
                        "background": "#f0fdf4",  # Green-50
                        "surface": "#ffffff",  # White
                        "surface_variant": "#dcfce7",  # Green-100
                        "text": "#064e3b",  # Emerald-900
                        "text_secondary": "#047857",  # Emerald-700
                        "text_muted": "#059669",  # Emerald-600
                        "border": "#bbf7d0",  # Green-200
                        "success": "#059669",  # Emerald-600
                        "warning": "#d97706",  # Amber-600
                        "error": "#dc2626",  # Red-600
                        "info": "#2563eb",  # Blue-600
                        "code_bg": "#f8fafc",  # Slate-50
                        "code_border": "#e2e8f0",  # Slate-200
                    },
                    "dark": {
                        "primary": "#10b981",  # Emerald-500
                        "secondary": "#34d399",  # Emerald-400
                        "accent": "#6ee7b7",  # Emerald-300
                        "background": "#0f1419",  # Custom dark
                        "surface": "#1a1f2e",  # Custom surface
                        "surface_variant": "#2d3748",  # Custom variant
                        "text": "#a7f3d0",  # Emerald-200
                        "text_secondary": "#6ee7b7",  # Emerald-300
                        "text_muted": "#10b981",  # Emerald-500
                        "border": "#064e3b",  # Emerald-900
                        "success": "#10b981",  # Emerald-500
                        "warning": "#f59e0b",  # Amber-500
                        "error": "#f87171",  # Red-400
                        "info": "#60a5fa",  # Blue-400
                        "code_bg": "#1e293b",  # Slate-800
                        "code_border": "#334155",  # Slate-700
                    },
                },
                "supports_dark_mode": True,
                "accessibility_features": {
                    "syntax_highlighting": True,
                    "code_focused": True,
                    "monospace_optimization": True,
                },
            },
            # 6. Medical Professional - Healthcare optimized
            {
                "name": "medical_professional",
                "display_name": "Medical Professional",
                "description": "Healthcare industry optimized theme with calming colors",
                "category": ThemeCategory.INDUSTRY,
                "color_scheme": {
                    "light": {
                        "primary": "#0369a1",  # Sky-700
                        "secondary": "#0ea5e9",  # Sky-500
                        "accent": "#38bdf8",  # Sky-400
                        "background": "#f0f9ff",  # Sky-50
                        "surface": "#ffffff",  # White
                        "surface_variant": "#e0f2fe",  # Sky-100
                        "text": "#0c4a6e",  # Sky-900
                        "text_secondary": "#0369a1",  # Sky-700
                        "text_muted": "#0284c7",  # Sky-600
                        "border": "#bae6fd",  # Sky-200
                        "success": "#059669",  # Emerald-600
                        "warning": "#d97706",  # Amber-600
                        "error": "#dc2626",  # Red-600
                        "info": "#0369a1",  # Sky-700
                        "medical_urgent": "#dc2626",  # Red-600
                        "medical_normal": "#059669",  # Emerald-600
                    },
                    "dark": {
                        "primary": "#0ea5e9",  # Sky-500
                        "secondary": "#38bdf8",  # Sky-400
                        "accent": "#7dd3fc",  # Sky-300
                        "background": "#0c1821",  # Custom medical dark
                        "surface": "#1e3a5f",  # Custom surface
                        "surface_variant": "#2c5282",  # Custom variant
                        "text": "#e0f2fe",  # Sky-100
                        "text_secondary": "#bae6fd",  # Sky-200
                        "text_muted": "#0ea5e9",  # Sky-500
                        "border": "#0c4a6e",  # Sky-900
                        "success": "#10b981",  # Emerald-500
                        "warning": "#f59e0b",  # Amber-500
                        "error": "#f87171",  # Red-400
                        "info": "#38bdf8",  # Sky-400
                        "medical_urgent": "#f87171",  # Red-400
                        "medical_normal": "#10b981",  # Emerald-500
                    },
                },
                "supports_dark_mode": True,
                "accessibility_features": {
                    "medical_compliance": True,
                    "calming_colors": True,
                    "high_readability": True,
                },
            },
            # 7. Creative Studio - Design and creative work
            {
                "name": "creative_studio",
                "display_name": "Creative Studio",
                "description": "Design and creative work optimized with inspiring colors",
                "category": ThemeCategory.CREATIVE,
                "color_scheme": {
                    "light": {
                        "primary": "#7c3aed",  # Violet-600
                        "secondary": "#8b5cf6",  # Violet-500
                        "accent": "#a78bfa",  # Violet-400
                        "background": "#faf5ff",  # Violet-50
                        "surface": "#ffffff",  # White
                        "surface_variant": "#f3e8ff",  # Violet-100
                        "text": "#581c87",  # Violet-900
                        "text_secondary": "#7c3aed",  # Violet-600
                        "text_muted": "#8b5cf6",  # Violet-500
                        "border": "#c4b5fd",  # Violet-300
                        "success": "#059669",  # Emerald-600
                        "warning": "#d97706",  # Amber-600
                        "error": "#dc2626",  # Red-600
                        "info": "#7c3aed",  # Violet-600
                        "creative_accent_1": "#ec4899",  # Pink-500
                        "creative_accent_2": "#06b6d4",  # Cyan-500
                    },
                    "dark": {
                        "primary": "#8b5cf6",  # Violet-500
                        "secondary": "#a78bfa",  # Violet-400
                        "accent": "#c4b5fd",  # Violet-300
                        "background": "#1a0b2e",  # Custom creative dark
                        "surface": "#2d1b4e",  # Custom surface
                        "surface_variant": "#4c1d95",  # Violet-800
                        "text": "#f3e8ff",  # Violet-100
                        "text_secondary": "#c4b5fd",  # Violet-300
                        "text_muted": "#8b5cf6",  # Violet-500
                        "border": "#581c87",  # Violet-900
                        "success": "#10b981",  # Emerald-500
                        "warning": "#f59e0b",  # Amber-500
                        "error": "#f87171",  # Red-400
                        "info": "#a78bfa",  # Violet-400
                        "creative_accent_1": "#f472b6",  # Pink-400
                        "creative_accent_2": "#22d3ee",  # Cyan-400
                    },
                },
                "supports_dark_mode": True,
                "accessibility_features": {
                    "creative_inspiration": True,
                    "color_harmony": True,
                    "design_focused": True,
                },
            },
            # 8. Financial Dashboard - Finance industry
            {
                "name": "financial_dashboard",
                "display_name": "Financial Dashboard",
                "description": "Finance industry professional theme with data visualization focus",
                "category": ThemeCategory.INDUSTRY,
                "color_scheme": {
                    "light": {
                        "primary": "#065f46",  # Emerald-800
                        "secondary": "#059669",  # Emerald-600
                        "accent": "#10b981",  # Emerald-500
                        "background": "#f0fdf4",  # Green-50
                        "surface": "#ffffff",  # White
                        "surface_variant": "#dcfce7",  # Green-100
                        "text": "#064e3b",  # Emerald-900
                        "text_secondary": "#065f46",  # Emerald-800
                        "text_muted": "#047857",  # Emerald-700
                        "border": "#bbf7d0",  # Green-200
                        "success": "#059669",  # Emerald-600
                        "warning": "#d97706",  # Amber-600
                        "error": "#dc2626",  # Red-600
                        "info": "#0369a1",  # Sky-700
                        "profit": "#059669",  # Emerald-600
                        "loss": "#dc2626",  # Red-600
                        "neutral": "#6b7280",  # Gray-500
                    },
                    "dark": {
                        "primary": "#10b981",  # Emerald-500
                        "secondary": "#34d399",  # Emerald-400
                        "accent": "#6ee7b7",  # Emerald-300
                        "background": "#0f1b0f",  # Custom financial dark
                        "surface": "#1a2e1a",  # Custom surface
                        "surface_variant": "#065f46",  # Emerald-800
                        "text": "#dcfce7",  # Green-100
                        "text_secondary": "#bbf7d0",  # Green-200
                        "text_muted": "#34d399",  # Emerald-400
                        "border": "#064e3b",  # Emerald-900
                        "success": "#10b981",  # Emerald-500
                        "warning": "#f59e0b",  # Amber-500
                        "error": "#f87171",  # Red-400
                        "info": "#38bdf8",  # Sky-400
                        "profit": "#34d399",  # Emerald-400
                        "loss": "#f87171",  # Red-400
                        "neutral": "#9ca3af",  # Gray-400
                    },
                },
                "supports_dark_mode": True,
                "accessibility_features": {
                    "data_visualization": True,
                    "financial_indicators": True,
                    "professional_grade": True,
                },
            },
            # 9. High Contrast - WCAG AAA accessibility
            {
                "name": "high_contrast",
                "display_name": "High Contrast",
                "description": "WCAG AAA accessibility compliant high contrast theme",
                "category": ThemeCategory.ACCESSIBILITY,
                "color_scheme": {
                    "light": {
                        "primary": "#000000",  # Black
                        "secondary": "#000000",  # Black
                        "accent": "#0000ff",  # Blue
                        "background": "#ffffff",  # White
                        "surface": "#ffffff",  # White
                        "surface_variant": "#f0f0f0",  # Light gray
                        "text": "#000000",  # Black
                        "text_secondary": "#000000",  # Black
                        "text_muted": "#333333",  # Dark gray
                        "border": "#000000",  # Black
                        "success": "#008000",  # Green
                        "warning": "#ff8c00",  # Orange
                        "error": "#ff0000",  # Red
                        "info": "#0000ff",  # Blue
                    },
                    "dark": {
                        "primary": "#ffffff",  # White
                        "secondary": "#ffffff",  # White
                        "accent": "#00ffff",  # Cyan
                        "background": "#000000",  # Black
                        "surface": "#000000",  # Black
                        "surface_variant": "#333333",  # Dark gray
                        "text": "#ffffff",  # White
                        "text_secondary": "#ffffff",  # White
                        "text_muted": "#cccccc",  # Light gray
                        "border": "#ffffff",  # White
                        "success": "#00ff00",  # Lime
                        "warning": "#ffff00",  # Yellow
                        "error": "#ff0000",  # Red
                        "info": "#00ffff",  # Cyan
                    },
                },
                "supports_dark_mode": True,
                "accessibility_features": {
                    "wcag_aaa_compliant": True,
                    "screen_reader_optimized": True,
                    "keyboard_navigation": True,
                    "ultra_high_contrast": True,
                },
            },
            # 10. Night Shift - Blue light reduced
            {
                "name": "night_shift",
                "display_name": "Night Shift",
                "description": "Blue light reduced theme for comfortable evening use",
                "category": ThemeCategory.ACCESSIBILITY,
                "color_scheme": {
                    "light": {
                        "primary": "#a16207",  # Amber-700
                        "secondary": "#d97706",  # Amber-600
                        "accent": "#f59e0b",  # Amber-500
                        "background": "#fffbeb",  # Amber-50
                        "surface": "#fefce8",  # Yellow-50
                        "surface_variant": "#fef3c7",  # Amber-100
                        "text": "#78350f",  # Amber-900
                        "text_secondary": "#92400e",  # Amber-700
                        "text_muted": "#a16207",  # Amber-700
                        "border": "#fed7aa",  # Orange-200
                        "success": "#166534",  # Green-800
                        "warning": "#92400e",  # Amber-700
                        "error": "#991b1b",  # Red-800
                        "info": "#a16207",  # Amber-700
                    },
                    "dark": {
                        "primary": "#fbbf24",  # Amber-400
                        "secondary": "#f59e0b",  # Amber-500
                        "accent": "#fdba74",  # Orange-300
                        "background": "#1c1410",  # Custom warm dark
                        "surface": "#2c2112",  # Custom warm surface
                        "surface_variant": "#451a03",  # Amber-900
                        "text": "#fef3c7",  # Amber-100
                        "text_secondary": "#fed7aa",  # Orange-200
                        "text_muted": "#f59e0b",  # Amber-500
                        "border": "#78350f",  # Amber-900
                        "success": "#22c55e",  # Green-500
                        "warning": "#f59e0b",  # Amber-500
                        "error": "#f87171",  # Red-400
                        "info": "#fbbf24",  # Amber-400
                    },
                },
                "supports_dark_mode": True,
                "accessibility_features": {
                    "blue_light_filter": True,
                    "eye_strain_reduction": True,
                    "evening_optimized": True,
                },
            },
            # 11. Accessibility Plus - Enhanced readability
            {
                "name": "accessibility_plus",
                "display_name": "Accessibility Plus",
                "description": "Enhanced readability and navigation for all users",
                "category": ThemeCategory.ACCESSIBILITY,
                "color_scheme": {
                    "light": {
                        "primary": "#1f2937",  # Gray-800
                        "secondary": "#374151",  # Gray-700
                        "accent": "#4b5563",  # Gray-600
                        "background": "#ffffff",  # White
                        "surface": "#f9fafb",  # Gray-50
                        "surface_variant": "#f3f4f6",  # Gray-100
                        "text": "#111827",  # Gray-900
                        "text_secondary": "#374151",  # Gray-700
                        "text_muted": "#6b7280",  # Gray-500
                        "border": "#d1d5db",  # Gray-300
                        "success": "#047857",  # Emerald-700
                        "warning": "#b45309",  # Amber-700
                        "error": "#b91c1c",  # Red-700
                        "info": "#1d4ed8",  # Blue-700
                    },
                    "dark": {
                        "primary": "#e5e7eb",  # Gray-200
                        "secondary": "#d1d5db",  # Gray-300
                        "accent": "#9ca3af",  # Gray-400
                        "background": "#1f2937",  # Gray-800
                        "surface": "#374151",  # Gray-700
                        "surface_variant": "#4b5563",  # Gray-600
                        "text": "#f3f4f6",  # Gray-100
                        "text_secondary": "#e5e7eb",  # Gray-200
                        "text_muted": "#9ca3af",  # Gray-400
                        "border": "#6b7280",  # Gray-500
                        "success": "#10b981",  # Emerald-500
                        "warning": "#f59e0b",  # Amber-500
                        "error": "#ef4444",  # Red-500
                        "info": "#3b82f6",  # Blue-500
                    },
                },
                "supports_dark_mode": True,
                "accessibility_features": {
                    "enhanced_readability": True,
                    "focus_indicators": True,
                    "large_touch_targets": True,
                    "clear_navigation": True,
                    "wcag_aa_compliant": True,
                },
            },
            # 12. Warm Reading - Comfortable for long conversations
            {
                "name": "warm_reading",
                "display_name": "Warm Reading",
                "description": "Comfortable warm theme for long conversations and reading",
                "category": ThemeCategory.ACCESSIBILITY,
                "color_scheme": {
                    "light": {
                        "primary": "#9a3412",  # Orange-800
                        "secondary": "#c2410c",  # Orange-700
                        "accent": "#ea580c",  # Orange-600
                        "background": "#fefce8",  # Yellow-50
                        "surface": "#fffbeb",  # Amber-50
                        "surface_variant": "#fef3c7",  # Amber-100
                        "text": "#78350f",  # Amber-900
                        "text_secondary": "#92400e",  # Amber-700
                        "text_muted": "#a16207",  # Amber-700
                        "border": "#fed7aa",  # Orange-200
                        "success": "#15803d",  # Green-700
                        "warning": "#a16207",  # Amber-700
                        "error": "#c2410c",  # Orange-700
                        "info": "#1d4ed8",  # Blue-700
                    },
                    "dark": {
                        "primary": "#fb923c",  # Orange-400
                        "secondary": "#f97316",  # Orange-500
                        "accent": "#fdba74",  # Orange-300
                        "background": "#1c1814",  # Custom warm dark
                        "surface": "#2c2416",  # Custom warm surface
                        "surface_variant": "#451a03",  # Amber-900
                        "text": "#fef3c7",  # Amber-100
                        "text_secondary": "#fed7aa",  # Orange-200
                        "text_muted": "#f59e0b",  # Amber-500
                        "border": "#78350f",  # Amber-900
                        "success": "#22c55e",  # Green-500
                        "warning": "#f59e0b",  # Amber-500
                        "error": "#f97316",  # Orange-500
                        "info": "#60a5fa",  # Blue-400
                    },
                },
                "supports_dark_mode": True,
                "accessibility_features": {
                    "reading_optimized": True,
                    "warm_color_temperature": True,
                    "reduced_eye_strain": True,
                    "comfortable_contrast": True,
                },
            },
            # 13. Glossy White - Material Design with glossy white aesthetics
            {
                "name": "glossy_white",
                "display_name": "Glossy White",
                "description": "Material Design with pristine glossy white aesthetics and subtle shadows",
                "category": ThemeCategory.MODERN,
                "color_scheme": {
                    "light": {
                        "primary": "#1976d2",  # Material Blue 700
                        "secondary": "#2196f3",  # Material Blue 500
                        "accent": "#42a5f5",  # Material Blue 400
                        "background": "#fafafa",  # Material Grey 50
                        "surface": "#ffffff",  # Pure White
                        "surface_variant": "#f5f5f5",  # Material Grey 100
                        "text": "#212121",  # Material Grey 900
                        "text_secondary": "#757575",  # Material Grey 600
                        "text_muted": "#9e9e9e",  # Material Grey 500
                        "border": "#e0e0e0",  # Material Grey 300
                        "success": "#4caf50",  # Material Green 500
                        "warning": "#ff9800",  # Material Orange 500
                        "error": "#f44336",  # Material Red 500
                        "info": "#2196f3",  # Material Blue 500
                        "elevation_1": "rgba(0, 0, 0, 0.05)",
                        "elevation_2": "rgba(0, 0, 0, 0.1)",
                        "elevation_3": "rgba(0, 0, 0, 0.15)",
                    },
                    "dark": {
                        "primary": "#90caf9",  # Material Blue 200
                        "secondary": "#64b5f6",  # Material Blue 300
                        "accent": "#42a5f5",  # Material Blue 400
                        "background": "#121212",  # Material Dark Background
                        "surface": "#1e1e1e",  # Material Dark Surface
                        "surface_variant": "#2c2c2c",  # Material Dark Surface Variant
                        "text": "#ffffff",  # White
                        "text_secondary": "#b3b3b3",  # Light Grey
                        "text_muted": "#808080",  # Medium Grey
                        "border": "#404040",  # Dark Grey
                        "success": "#81c784",  # Material Green 300
                        "warning": "#ffb74d",  # Material Orange 300
                        "error": "#e57373",  # Material Red 300
                        "info": "#64b5f6",  # Material Blue 300
                        "elevation_1": "rgba(255, 255, 255, 0.05)",
                        "elevation_2": "rgba(255, 255, 255, 0.08)",
                        "elevation_3": "rgba(255, 255, 255, 0.12)",
                    },
                },
                "supports_dark_mode": True,
                "accessibility_features": {
                    "material_design": True,
                    "glossy_effects": True,
                    "clean_aesthetics": True,
                },
                "css_variables": {
                    "border-radius": "8px",
                    "shadow": "0 2px 8px rgba(0, 0, 0, 0.1)",
                    "shadow-lg": "0 8px 24px rgba(0, 0, 0, 0.15)",
                    "glossy-overlay": "linear-gradient(145deg, rgba(255,255,255,0.3) 0%, rgba(255,255,255,0.1) 100%)",
                },
            },
            # 14. Glossy Black - Material Design with sophisticated black glossy finish
            {
                "name": "glossy_black",
                "display_name": "Glossy Black",
                "description": "Material Design with sophisticated black glossy finish and chrome accents",
                "category": ThemeCategory.MODERN,
                "color_scheme": {
                    "light": {
                        "primary": "#424242",  # Material Grey 800
                        "secondary": "#616161",  # Material Grey 700
                        "accent": "#757575",  # Material Grey 600
                        "background": "#fafafa",  # Material Grey 50
                        "surface": "#ffffff",  # White
                        "surface_variant": "#f5f5f5",  # Material Grey 100
                        "text": "#212121",  # Material Grey 900
                        "text_secondary": "#424242",  # Material Grey 800
                        "text_muted": "#757575",  # Material Grey 600
                        "border": "#bdbdbd",  # Material Grey 400
                        "success": "#4caf50",  # Material Green 500
                        "warning": "#ff9800",  # Material Orange 500
                        "error": "#f44336",  # Material Red 500
                        "info": "#607d8b",  # Material Blue Grey 500
                        "chrome_accent": "#9e9e9e",  # Material Grey 500
                    },
                    "dark": {
                        "primary": "#ffffff",  # White
                        "secondary": "#e0e0e0",  # Material Grey 300
                        "accent": "#bdbdbd",  # Material Grey 400
                        "background": "#000000",  # Pure Black
                        "surface": "#121212",  # Material Dark Surface
                        "surface_variant": "#1e1e1e",  # Darker Surface
                        "text": "#ffffff",  # White
                        "text_secondary": "#e0e0e0",  # Material Grey 300
                        "text_muted": "#bdbdbd",  # Material Grey 400
                        "border": "#424242",  # Material Grey 800
                        "success": "#66bb6a",  # Material Green 400
                        "warning": "#ffa726",  # Material Orange 400
                        "error": "#ef5350",  # Material Red 400
                        "info": "#78909c",  # Material Blue Grey 400
                        "chrome_accent": "#757575",  # Material Grey 600
                    },
                },
                "supports_dark_mode": True,
                "accessibility_features": {
                    "material_design": True,
                    "glossy_effects": True,
                    "premium_finish": True,
                },
                "css_variables": {
                    "border-radius": "6px",
                    "shadow": "0 4px 12px rgba(0, 0, 0, 0.3)",
                    "shadow-lg": "0 12px 32px rgba(0, 0, 0, 0.4)",
                    "glossy-overlay": "linear-gradient(145deg, rgba(255,255,255,0.1) 0%, rgba(0,0,0,0.1) 100%)",
                },
            },
            # 15. Glossy Glass - Material Design with translucent glass morphism
            {
                "name": "glossy_glass",
                "display_name": "Glossy Glass",
                "description": "Material Design with translucent glass morphism and frosted effects",
                "category": ThemeCategory.MODERN,
                "color_scheme": {
                    "light": {
                        "primary": "#1976d2",  # Material Blue 700
                        "secondary": "#2196f3",  # Material Blue 500
                        "accent": "#03dac6",  # Material Teal A400
                        "background": "rgba(248, 250, 252, 0.8)",  # Semi-transparent light
                        "surface": "rgba(255, 255, 255, 0.7)",  # Glass white
                        "surface_variant": "rgba(245, 245, 245, 0.6)",  # Glass variant
                        "text": "#1a1a1a",  # Near black
                        "text_secondary": "#4a4a4a",  # Medium dark
                        "text_muted": "#757575",  # Material Grey 600
                        "border": "rgba(224, 224, 224, 0.5)",  # Semi-transparent border
                        "success": "#4caf50",  # Material Green 500
                        "warning": "#ff9800",  # Material Orange 500
                        "error": "#f44336",  # Material Red 500
                        "info": "#2196f3",  # Material Blue 500
                        "glass_overlay": "rgba(255, 255, 255, 0.25)",
                        "backdrop_filter": "blur(20px)",
                    },
                    "dark": {
                        "primary": "#bb86fc",  # Material Purple 200
                        "secondary": "#03dac6",  # Material Teal A400
                        "accent": "#cf6679",  # Material Pink A100
                        "background": "rgba(18, 18, 18, 0.8)",  # Semi-transparent dark
                        "surface": "rgba(30, 30, 30, 0.7)",  # Glass dark
                        "surface_variant": "rgba(44, 44, 44, 0.6)",  # Glass dark variant
                        "text": "#ffffff",  # White
                        "text_secondary": "#e0e0e0",  # Light grey
                        "text_muted": "#9e9e9e",  # Material Grey 500
                        "border": "rgba(66, 66, 66, 0.5)",  # Semi-transparent dark border
                        "success": "#81c784",  # Material Green 300
                        "warning": "#ffb74d",  # Material Orange 300
                        "error": "#e57373",  # Material Red 300
                        "info": "#64b5f6",  # Material Blue 300
                        "glass_overlay": "rgba(255, 255, 255, 0.1)",
                        "backdrop_filter": "blur(20px)",
                    },
                },
                "supports_dark_mode": True,
                "accessibility_features": {
                    "material_design": True,
                    "glass_morphism": True,
                    "backdrop_filter": True,
                    "translucent_effects": True,
                },
                "css_variables": {
                    "border-radius": "12px",
                    "shadow": "0 8px 32px rgba(0, 0, 0, 0.12)",
                    "shadow-lg": "0 16px 48px rgba(0, 0, 0, 0.18)",
                    "backdrop-filter": "blur(20px) saturate(180%)",
                    "glass-border": "1px solid rgba(255, 255, 255, 0.2)",
                },
            },
            # 16. Glossy Black White - High contrast Material Design with glossy accents
            {
                "name": "glossy_black_white",
                "display_name": "Glossy Black White",
                "description": "High contrast Material Design combining glossy black and white elements",
                "category": ThemeCategory.MODERN,
                "color_scheme": {
                    "light": {
                        "primary": "#000000",  # Pure Black
                        "secondary": "#212121",  # Material Grey 900
                        "accent": "#1976d2",  # Material Blue 700
                        "background": "#ffffff",  # Pure White
                        "surface": "#fafafa",  # Material Grey 50
                        "surface_variant": "#f5f5f5",  # Material Grey 100
                        "text": "#000000",  # Pure Black
                        "text_secondary": "#424242",  # Material Grey 800
                        "text_muted": "#757575",  # Material Grey 600
                        "border": "#000000",  # Pure Black
                        "success": "#388e3c",  # Material Green 700
                        "warning": "#f57c00",  # Material Orange 700
                        "error": "#d32f2f",  # Material Red 700
                        "info": "#1976d2",  # Material Blue 700
                        "contrast_surface": "#000000",  # Black accent surface
                        "contrast_text": "#ffffff",  # White text on black
                    },
                    "dark": {
                        "primary": "#ffffff",  # Pure White
                        "secondary": "#f5f5f5",  # Material Grey 100
                        "accent": "#64b5f6",  # Material Blue 300
                        "background": "#000000",  # Pure Black
                        "surface": "#121212",  # Material Dark Surface
                        "surface_variant": "#1e1e1e",  # Dark Surface Variant
                        "text": "#ffffff",  # Pure White
                        "text_secondary": "#e0e0e0",  # Material Grey 300
                        "text_muted": "#bdbdbd",  # Material Grey 400
                        "border": "#ffffff",  # Pure White
                        "success": "#66bb6a",  # Material Green 400
                        "warning": "#ffa726",  # Material Orange 400
                        "error": "#ef5350",  # Material Red 400
                        "info": "#64b5f6",  # Material Blue 300
                        "contrast_surface": "#ffffff",  # White accent surface
                        "contrast_text": "#000000",  # Black text on white
                    },
                },
                "supports_dark_mode": True,
                "accessibility_features": {
                    "material_design": True,
                    "ultra_high_contrast": True,
                    "glossy_effects": True,
                    "wcag_aaa_compliant": True,
                },
                "css_variables": {
                    "border-radius": "4px",
                    "shadow": "0 2px 8px rgba(0, 0, 0, 0.26)",
                    "shadow-lg": "0 8px 24px rgba(0, 0, 0, 0.38)",
                    "contrast-shadow": "0 4px 12px rgba(255, 255, 255, 0.3)",
                },
            },
            # 17. Glossy Green - Material Design with vibrant green glossy aesthetics
            {
                "name": "glossy_green",
                "display_name": "Glossy Green",
                "description": "Material Design with vibrant green glossy aesthetics and natural tones",
                "category": ThemeCategory.MODERN,
                "color_scheme": {
                    "light": {
                        "primary": "#2e7d32",  # Material Green 800
                        "secondary": "#388e3c",  # Material Green 700
                        "accent": "#4caf50",  # Material Green 500
                        "background": "#f1f8e9",  # Material Light Green 50
                        "surface": "#ffffff",  # White
                        "surface_variant": "#e8f5e8",  # Light Green 100
                        "text": "#1b5e20",  # Material Green 900
                        "text_secondary": "#2e7d32",  # Material Green 800
                        "text_muted": "#4caf50",  # Material Green 500
                        "border": "#a5d6a7",  # Material Green 200
                        "success": "#388e3c",  # Material Green 700
                        "warning": "#f57c00",  # Material Orange 700
                        "error": "#d32f2f",  # Material Red 700
                        "info": "#0277bd",  # Material Light Blue 800
                        "nature_accent_1": "#66bb6a",  # Material Green 400
                        "nature_accent_2": "#81c784",  # Material Green 300
                    },
                    "dark": {
                        "primary": "#66bb6a",  # Material Green 400
                        "secondary": "#4caf50",  # Material Green 500
                        "accent": "#81c784",  # Material Green 300
                        "background": "#0d1b0d",  # Dark Green Background
                        "surface": "#1a2c1a",  # Dark Green Surface
                        "surface_variant": "#2e4a2e",  # Dark Green Variant
                        "text": "#c8e6c9",  # Material Green 100
                        "text_secondary": "#a5d6a7",  # Material Green 200
                        "text_muted": "#66bb6a",  # Material Green 400
                        "border": "#2e7d32",  # Material Green 800
                        "success": "#4caf50",  # Material Green 500
                        "warning": "#ffa726",  # Material Orange 400
                        "error": "#ef5350",  # Material Red 400
                        "info": "#29b6f6",  # Material Light Blue 400
                        "nature_accent_1": "#4caf50",  # Material Green 500
                        "nature_accent_2": "#81c784",  # Material Green 300
                    },
                },
                "supports_dark_mode": True,
                "accessibility_features": {
                    "material_design": True,
                    "nature_inspired": True,
                    "glossy_effects": True,
                    "eco_friendly_theme": True,
                },
                "css_variables": {
                    "border-radius": "8px",
                    "shadow": "0 2px 12px rgba(76, 175, 80, 0.15)",
                    "shadow-lg": "0 8px 28px rgba(76, 175, 80, 0.25)",
                    "nature-gradient": "linear-gradient(135deg, #4caf50 0%, #81c784 100%)",
                },
            },
            # 18. Green Theme - Comprehensive green ecosystem theme
            {
                "name": "green_theme",
                "display_name": "Green Theme",
                "description": "Comprehensive green ecosystem theme with multiple green shades and natural harmony",
                "category": ThemeCategory.CREATIVE,
                "color_scheme": {
                    "light": {
                        "primary": "#1b5e20",  # Material Green 900
                        "secondary": "#2e7d32",  # Material Green 800
                        "accent": "#00c853",  # Material Green A400
                        "background": "#e8f5e8",  # Custom Light Green
                        "surface": "#f1f8e9",  # Material Light Green 50
                        "surface_variant": "#dcedc8",  # Material Light Green 100
                        "text": "#1b5e20",  # Material Green 900
                        "text_secondary": "#2e7d32",  # Material Green 800
                        "text_muted": "#558b2f",  # Material Light Green 800
                        "border": "#8bc34a",  # Material Light Green 500
                        "success": "#4caf50",  # Material Green 500
                        "warning": "#ff8f00",  # Material Amber 800
                        "error": "#c62828",  # Material Red 800
                        "info": "#00695c",  # Material Teal 800
                        "forest_green": "#2e7d32",  # Forest Green
                        "lime_green": "#689f38",  # Lime Green
                        "mint_green": "#00695c",  # Mint Green (Teal)
                        "sage_green": "#8bc34a",  # Sage Green (Light Green)
                        "emerald_green": "#00c853",  # Emerald Green
                    },
                    "dark": {
                        "primary": "#4caf50",  # Material Green 500
                        "secondary": "#66bb6a",  # Material Green 400
                        "accent": "#69f0ae",  # Material Green A200
                        "background": "#0a1a0a",  # Deep Dark Green
                        "surface": "#1a2c1a",  # Dark Green Surface
                        "surface_variant": "#2d4a2d",  # Darker Green Variant
                        "text": "#c8e6c9",  # Material Green 100
                        "text_secondary": "#a5d6a7",  # Material Green 200
                        "text_muted": "#81c784",  # Material Green 300
                        "border": "#388e3c",  # Material Green 700
                        "success": "#4caf50",  # Material Green 500
                        "warning": "#ffb300",  # Material Amber 600
                        "error": "#e53935",  # Material Red 600
                        "info": "#26a69a",  # Material Teal 400
                        "forest_green": "#388e3c",  # Forest Green (darker)
                        "lime_green": "#9ccc65",  # Lime Green (lighter)
                        "mint_green": "#4db6ac",  # Mint Green (Teal 300)
                        "sage_green": "#aed581",  # Sage Green (Light Green 300)
                        "emerald_green": "#00e676",  # Emerald Green (Green A400)
                    },
                },
                "supports_dark_mode": True,
                "accessibility_features": {
                    "nature_harmony": True,
                    "multiple_green_shades": True,
                    "eco_consciousness": True,
                    "calming_environment": True,
                },
                "css_variables": {
                    "border-radius": "10px",
                    "shadow": "0 2px 16px rgba(76, 175, 80, 0.2)",
                    "shadow-lg": "0 8px 32px rgba(76, 175, 80, 0.3)",
                    "nature-gradient-1": "linear-gradient(45deg, #4caf50 0%, #81c784 50%, #c8e6c9 100%)",
                    "nature-gradient-2": "linear-gradient(135deg, #2e7d32 0%, #4caf50 50%, #66bb6a 100%)",
                    "forest-overlay": "radial-gradient(circle, rgba(76,175,80,0.1) 0%, rgba(46,125,50,0.05) 100%)",
                },
            },
        ]
