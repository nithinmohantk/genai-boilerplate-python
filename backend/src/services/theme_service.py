"""
Theme service for managing themes, user settings, and UI customization.
"""

import logging
from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import and_, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.theme import (
    AccessibilityCheckResponse,
    DisplayMode,
    FontFamily,
    FontSize,
    Theme,
    ThemeCreate,
    ThemeSearchRequest,
    ThemeUpdate,
    UserSettings,
    UserSettingsCreate,
    UserSettingsUpdate,
    UserThemeHistory,
)

logger = logging.getLogger(__name__)


class ThemeService:
    """Service for managing themes and user interface customization."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_theme(
        self, theme_data: ThemeCreate, is_system: bool = False
    ) -> Theme:
        """Create a new theme."""
        try:
            theme = Theme(
                name=theme_data.name,
                display_name=theme_data.display_name,
                description=theme_data.description,
                category=theme_data.category,
                color_scheme=theme_data.color_scheme,
                typography=theme_data.typography,
                layout_config=theme_data.layout_config,
                component_styles=theme_data.component_styles,
                supports_dark_mode=theme_data.supports_dark_mode,
                accessibility_features=theme_data.accessibility_features,
                css_variables=theme_data.css_variables,
                version=theme_data.version,
                is_system=is_system,
            )

            self.db.add(theme)
            await self.db.commit()
            await self.db.refresh(theme)

            logger.info(f"Created theme {theme.id}: {theme.name}")
            return theme

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating theme: {e}")
            raise

    async def get_theme(self, theme_id: UUID) -> Theme | None:
        """Get a theme by ID."""
        try:
            query = select(Theme).where(
                and_(Theme.id == theme_id, Theme.is_active)
            )

            result = await self.db.execute(query)
            theme = result.scalar_one_or_none()

            if theme:
                # Update usage tracking
                theme.usage_count += 1
                await self.db.commit()

            return theme

        except Exception as e:
            logger.error(f"Error getting theme: {e}")
            return None

    async def get_themes(
        self,
        search_request: ThemeSearchRequest | None = None,
        include_inactive: bool = False,
    ) -> list[Theme]:
        """Get themes with filtering and search."""
        try:
            conditions = []

            if not include_inactive:
                conditions.append(Theme.is_active)

            if search_request:
                if search_request.category:
                    conditions.append(Theme.category == search_request.category)

                if search_request.supports_dark_mode is not None:
                    conditions.append(
                        Theme.supports_dark_mode == search_request.supports_dark_mode
                    )

                if search_request.accessibility_required:
                    conditions.append(Theme.accessibility_features.isnot(None))

                if search_request.search_term:
                    search_term = f"%{search_request.search_term.lower()}%"
                    conditions.append(
                        or_(
                            func.lower(Theme.display_name).like(search_term),
                            func.lower(Theme.description).like(search_term),
                            func.lower(Theme.name).like(search_term),
                        )
                    )

                limit = search_request.limit
            else:
                limit = 50

            query = (
                select(Theme).where(and_(*conditions)) if conditions else select(Theme)
            )
            query = query.order_by(
                Theme.is_system.desc(),  # System themes first
                Theme.category,
                desc(Theme.usage_count),
                Theme.display_name,
            ).limit(limit)

            result = await self.db.execute(query)
            return result.scalars().all()

        except Exception as e:
            logger.error(f"Error getting themes: {e}")
            return []

    async def update_theme(self, theme_id: UUID, updates: ThemeUpdate) -> Theme | None:
        """Update a theme."""
        try:
            theme = await self.get_theme(theme_id)
            if not theme:
                return None

            # Update fields
            update_data = updates.dict(exclude_unset=True)
            for field, value in update_data.items():
                if hasattr(theme, field):
                    setattr(theme, field, value)

            theme.updated_at = datetime.now()
            await self.db.commit()
            await self.db.refresh(theme)

            logger.info(f"Updated theme {theme_id}")
            return theme

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating theme: {e}")
            return None

    async def delete_theme(self, theme_id: UUID) -> bool:
        """Delete a theme (soft delete)."""
        try:
            theme = await self.get_theme(theme_id)
            if not theme or theme.is_system:
                return False

            theme.is_active = False
            theme.updated_at = datetime.now()
            await self.db.commit()

            logger.info(f"Deleted theme {theme_id}")
            return True

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error deleting theme: {e}")
            return False

    async def get_user_settings(
        self, user_id: UUID, tenant_id: UUID
    ) -> UserSettings | None:
        """Get user's settings, create defaults if not exist."""
        try:
            query = (
                select(UserSettings)
                .options(selectinload(UserSettings.theme))
                .where(UserSettings.user_id == user_id)
            )

            result = await self.db.execute(query)
            settings = result.scalar_one_or_none()

            if not settings:
                # Create default settings
                settings = await self.create_user_settings(
                    user_id=user_id,
                    tenant_id=tenant_id,
                    settings_data=UserSettingsCreate(),
                )

            return settings

        except Exception as e:
            logger.error(f"Error getting user settings: {e}")
            return None

    async def create_user_settings(
        self, user_id: UUID, tenant_id: UUID, settings_data: UserSettingsCreate
    ) -> UserSettings:
        """Create user settings with defaults."""
        try:
            # Get default theme if not specified
            theme_id = settings_data.active_theme_id
            if not theme_id:
                default_theme = await self.get_default_theme()
                theme_id = default_theme.id if default_theme else None

            settings = UserSettings(
                tenant_id=tenant_id,
                user_id=user_id,
                active_theme_id=theme_id,
                display_mode=settings_data.display_mode,
                font_size=settings_data.font_size,
                font_family=settings_data.font_family,
                line_height=settings_data.line_height,
                chat_layout=settings_data.chat_layout,
                message_style=settings_data.message_style,
                show_timestamps=settings_data.show_timestamps,
                show_avatars=settings_data.show_avatars,
                compact_mode=settings_data.compact_mode,
                high_contrast=settings_data.high_contrast,
                reduce_motion=settings_data.reduce_motion,
                screen_reader_optimized=settings_data.screen_reader_optimized,
            )

            self.db.add(settings)
            await self.db.commit()
            await self.db.refresh(settings)

            logger.info(f"Created user settings for user {user_id}")
            return settings

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating user settings: {e}")
            raise

    async def update_user_settings(
        self, user_id: UUID, tenant_id: UUID, updates: UserSettingsUpdate
    ) -> UserSettings | None:
        """Update user settings."""
        try:
            settings = await self.get_user_settings(user_id, tenant_id)
            if not settings:
                # Create settings if they don't exist
                settings = await self.create_user_settings(
                    user_id=user_id,
                    tenant_id=tenant_id,
                    settings_data=UserSettingsCreate(),
                )

            # Create backup of current settings
            settings.settings_backup = {
                "active_theme_id": str(settings.active_theme_id)
                if settings.active_theme_id
                else None,
                "display_mode": settings.display_mode,
                "font_size": settings.font_size,
                "font_family": settings.font_family,
                "line_height": settings.line_height,
                "chat_layout": settings.chat_layout,
                "message_style": settings.message_style,
                "backup_timestamp": datetime.now().isoformat(),
            }

            # Update fields
            update_data = updates.dict(exclude_unset=True)
            for field, value in update_data.items():
                if hasattr(settings, field):
                    setattr(settings, field, value)

            settings.updated_at = datetime.now()
            settings.last_sync = datetime.now()
            await self.db.commit()
            await self.db.refresh(settings)

            logger.info(f"Updated user settings for user {user_id}")
            return settings

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating user settings: {e}")
            return None

    async def apply_theme_to_user(
        self,
        user_id: UUID,
        tenant_id: UUID,
        theme_id: UUID,
        display_mode: DisplayMode | None = None,
    ) -> bool:
        """Apply a theme to user's settings."""
        try:
            # Verify theme exists and is active
            theme = await self.get_theme(theme_id)
            if not theme:
                return False

            # Update user settings
            settings_update = UserSettingsUpdate(
                active_theme_id=theme_id, display_mode=display_mode or DisplayMode.AUTO
            )

            updated_settings = await self.update_user_settings(
                user_id=user_id, tenant_id=tenant_id, updates=settings_update
            )

            if updated_settings:
                # Record theme usage history
                await self.record_theme_usage(
                    user_id=user_id, theme_id=theme_id, applied_via="manual"
                )

                logger.info(f"Applied theme {theme_id} to user {user_id}")
                return True

            return False

        except Exception as e:
            logger.error(f"Error applying theme to user: {e}")
            return False

    async def record_theme_usage(
        self,
        user_id: UUID,
        theme_id: UUID,
        applied_via: str = "manual",
        device_info: dict[str, Any] | None = None,
    ) -> UserThemeHistory:
        """Record theme usage for analytics."""
        try:
            history = UserThemeHistory(
                user_id=user_id,
                theme_id=theme_id,
                applied_via=applied_via,
                device_info=device_info,
            )

            self.db.add(history)
            await self.db.commit()
            await self.db.refresh(history)

            return history

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error recording theme usage: {e}")
            raise

    async def generate_theme_css(
        self,
        theme: Theme,
        display_mode: DisplayMode = DisplayMode.AUTO,
        font_size: FontSize = FontSize.MD,
        font_family: FontFamily = FontFamily.SYSTEM,
    ) -> str:
        """Generate CSS variables and styles for a theme."""
        try:
            css_parts = []

            # Root CSS variables
            css_parts.append(":root {")

            # Color scheme variables
            color_scheme = theme.color_scheme
            if display_mode == DisplayMode.DARK and theme.supports_dark_mode:
                # Use dark mode colors if available
                color_scheme = color_scheme.get("dark", color_scheme)
            elif display_mode == DisplayMode.LIGHT:
                # Use light mode colors
                color_scheme = color_scheme.get("light", color_scheme)

            # Generate CSS color variables
            for key, value in color_scheme.items():
                if isinstance(value, str) and value.startswith("#"):
                    css_parts.append(f"  --color-{key.replace('_', '-')}: {value};")

            # Font size variables
            font_sizes = {
                FontSize.XS: "12px",
                FontSize.SM: "14px",
                FontSize.MD: "16px",
                FontSize.LG: "18px",
                FontSize.XL: "20px",
                FontSize.XXL: "24px",
            }
            css_parts.append(f"  --font-size-base: {font_sizes[font_size]};")

            # Font family variables
            font_families = {
                FontFamily.SYSTEM: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
                FontFamily.INTER: "'Inter', -apple-system, BlinkMacSystemFont, sans-serif",
                FontFamily.ROBOTO: "'Roboto', -apple-system, BlinkMacSystemFont, sans-serif",
                FontFamily.OPEN_SANS: "'Open Sans', -apple-system, BlinkMacSystemFont, sans-serif",
                FontFamily.ACCESSIBILITY: "'Arial', 'Helvetica Neue', Arial, sans-serif",
            }
            css_parts.append(f"  --font-family-base: {font_families[font_family]};")

            # Add theme-specific CSS variables
            if theme.css_variables:
                for key, value in theme.css_variables.items():
                    css_parts.append(f"  --{key}: {value};")

            css_parts.append("}")

            # Add component styles
            if theme.component_styles:
                css_parts.append("")
                for selector, styles in theme.component_styles.items():
                    css_parts.append(f"{selector} {{")
                    for prop, value in styles.items():
                        css_parts.append(f"  {prop.replace('_', '-')}: {value};")
                    css_parts.append("}")

            return "\n".join(css_parts)

        except Exception as e:
            logger.error(f"Error generating theme CSS: {e}")
            return ""

    async def check_theme_accessibility(
        self, theme_id: UUID
    ) -> AccessibilityCheckResponse:
        """Check theme accessibility compliance."""
        try:
            theme = await self.get_theme(theme_id)
            if not theme:
                raise ValueError("Theme not found")

            color_scheme = theme.color_scheme
            contrast_ratios = {}
            accessibility_issues = []
            recommendations = []

            # Check contrast ratios for common color combinations
            bg_color = color_scheme.get("background", "#ffffff")
            text_color = color_scheme.get("text", "#000000")

            # Calculate contrast ratio (simplified)
            contrast_ratio = self._calculate_contrast_ratio(bg_color, text_color)
            contrast_ratios["background_text"] = contrast_ratio

            # WCAG compliance checks
            wcag_aa_compliant = contrast_ratio >= 4.5
            wcag_aaa_compliant = contrast_ratio >= 7.0

            if not wcag_aa_compliant:
                accessibility_issues.append(
                    "Background-text contrast ratio below WCAG AA standards"
                )
                recommendations.append(
                    "Increase contrast between background and text colors"
                )

            if not wcag_aaa_compliant:
                accessibility_issues.append(
                    "Background-text contrast ratio below WCAG AAA standards"
                )

            # Check for accessibility features
            if not theme.accessibility_features:
                accessibility_issues.append("No accessibility features defined")
                recommendations.append(
                    "Add accessibility features like focus indicators and high contrast support"
                )

            # Calculate overall score
            score = 100
            if not wcag_aa_compliant:
                score -= 40
            if not wcag_aaa_compliant:
                score -= 20
            if not theme.accessibility_features:
                score -= 20

            return AccessibilityCheckResponse(
                theme_id=theme_id,
                wcag_aa_compliant=wcag_aa_compliant,
                wcag_aaa_compliant=wcag_aaa_compliant,
                contrast_ratios=contrast_ratios,
                accessibility_issues=accessibility_issues,
                recommendations=recommendations,
                overall_score=max(0, score),
            )

        except Exception as e:
            logger.error(f"Error checking theme accessibility: {e}")
            return AccessibilityCheckResponse(
                theme_id=theme_id,
                wcag_aa_compliant=False,
                wcag_aaa_compliant=False,
                contrast_ratios={},
                accessibility_issues=["Error during accessibility check"],
                recommendations=["Please check theme configuration"],
                overall_score=0,
            )

    def _calculate_contrast_ratio(self, color1: str, color2: str) -> float:
        """Calculate contrast ratio between two colors (simplified implementation)."""
        try:
            # Convert hex to RGB
            def hex_to_rgb(hex_color):
                hex_color = hex_color.lstrip("#")
                return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))

            # Calculate relative luminance
            def relative_luminance(rgb):
                rgb_norm = [c / 255.0 for c in rgb]
                rgb_linear = []
                for c in rgb_norm:
                    if c <= 0.03928:
                        rgb_linear.append(c / 12.92)
                    else:
                        rgb_linear.append(((c + 0.055) / 1.055) ** 2.4)
                return (
                    0.2126 * rgb_linear[0]
                    + 0.7152 * rgb_linear[1]
                    + 0.0722 * rgb_linear[2]
                )

            rgb1 = hex_to_rgb(color1)
            rgb2 = hex_to_rgb(color2)

            lum1 = relative_luminance(rgb1)
            lum2 = relative_luminance(rgb2)

            # Ensure lum1 is the lighter color
            if lum1 < lum2:
                lum1, lum2 = lum2, lum1

            return (lum1 + 0.05) / (lum2 + 0.05)

        except Exception as e:
            logger.error(f"Error calculating contrast ratio: {e}")
            return 1.0  # Default to poor contrast

    async def get_default_theme(self) -> Theme | None:
        """Get the default system theme."""
        try:
            query = (
                select(Theme)
                .where(
                    and_(
                        Theme.is_system,
                        Theme.is_active,
                        Theme.name == "corporate_blue",  # Default theme
                    )
                )
                .limit(1)
            )

            result = await self.db.execute(query)
            return result.scalar_one_or_none()

        except Exception as e:
            logger.error(f"Error getting default theme: {e}")
            return None

    async def get_theme_usage_stats(self) -> dict[str, Any]:
        """Get theme usage statistics."""
        try:
            # Most popular themes
            popular_query = (
                select(Theme.display_name, Theme.usage_count, Theme.category)
                .where(Theme.is_active)
                .order_by(desc(Theme.usage_count))
                .limit(10)
            )
            popular_result = await self.db.execute(popular_query)
            popular_themes = [
                {
                    "name": row.display_name,
                    "usage_count": row.usage_count,
                    "category": row.category,
                }
                for row in popular_result.fetchall()
            ]

            # Themes by category
            category_query = (
                select(Theme.category, func.count(Theme.id))
                .where(Theme.is_active)
                .group_by(Theme.category)
            )
            category_result = await self.db.execute(category_query)
            themes_by_category = dict(category_result.fetchall())

            # Total themes
            total_query = select(func.count(Theme.id)).where(Theme.is_active)
            total_result = await self.db.execute(total_query)
            total_themes = total_result.scalar() or 0

            return {
                "total_themes": total_themes,
                "themes_by_category": themes_by_category,
                "popular_themes": popular_themes,
                "system_themes": themes_by_category.get("system", 0),
            }

        except Exception as e:
            logger.error(f"Error getting theme usage stats: {e}")
            return {
                "total_themes": 0,
                "themes_by_category": {},
                "popular_themes": [],
                "system_themes": 0,
            }
