"""
Comprehensive unit tests for theme service functionality.
"""

import os

# Add src to path
import sys
from datetime import datetime
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from models.theme import (
    DisplayMode,
    FontFamily,
    FontSize,
    ThemeCategory,
    ThemeCreate,
    ThemeSearchRequest,
    ThemeUpdate,
    UserSettingsCreate,
)
from services.theme_service import ThemeService


class MockAsyncSession:
    """Mock async SQLAlchemy session."""

    def __init__(self):
        self.add = Mock()
        self.commit = AsyncMock()
        self.rollback = AsyncMock()
        self.refresh = AsyncMock()
        self.execute = AsyncMock()
        self.scalar_one_or_none = Mock()


@pytest.fixture
def mock_db_session():
    """Mock database session fixture."""
    session = MockAsyncSession()
    return session


@pytest.fixture
def theme_service(mock_db_session):
    """Theme service fixture."""
    return ThemeService(mock_db_session)


@pytest.fixture
def sample_theme_create():
    """Sample theme creation data."""
    return ThemeCreate(
        name="test_theme",
        display_name="Test Theme",
        description="A test theme",
        category=ThemeCategory.PROFESSIONAL,
        color_scheme={
            "light": {
                "primary": "#1e40af",
                "secondary": "#3b82f6",
                "accent": "#60a5fa",
                "background": "#ffffff",
                "surface": "#f8fafc",
                "text": "#0f172a",
            },
            "dark": {
                "primary": "#3b82f6",
                "secondary": "#60a5fa",
                "accent": "#93c5fd",
                "background": "#0f172a",
                "surface": "#1e293b",
                "text": "#f8fafc",
            },
        },
        supports_dark_mode=True,
        accessibility_features={"high_contrast": True},
    )


@pytest.fixture
def sample_theme():
    """Sample theme model (mock object)."""
    theme_id = uuid4()
    theme = Mock()
    theme.id = theme_id
    theme.name = "test_theme"
    theme.display_name = "Test Theme"
    theme.description = "A test theme"
    theme.category = ThemeCategory.PROFESSIONAL
    theme.color_scheme = {
        "light": {
            "primary": "#1e40af",
            "secondary": "#3b82f6",
            "accent": "#60a5fa",
            "background": "#ffffff",
            "surface": "#f8fafc",
            "text": "#0f172a",
        },
        "dark": {
            "primary": "#3b82f6",
            "secondary": "#60a5fa",
            "accent": "#93c5fd",
            "background": "#0f172a",
            "surface": "#1e293b",
            "text": "#f8fafc",
        },
    }
    theme.supports_dark_mode = True
    theme.accessibility_features = {"high_contrast": True}
    theme.is_system = False
    theme.is_active = True
    theme.version = "1.0"
    theme.usage_count = 0
    theme.created_at = datetime.now()
    theme.updated_at = datetime.now()
    theme.css_variables = None
    theme.component_styles = None
    return theme


class TestThemeService:
    """Test cases for theme service."""

    @pytest.mark.asyncio
    async def test_create_theme_success(
        self, theme_service, sample_theme_create, mock_db_session
    ):
        """Test successful theme creation."""
        # Arrange
        mock_db_session.commit = AsyncMock()
        mock_db_session.refresh = AsyncMock()

        # Act
        result = await theme_service.create_theme(sample_theme_create, is_system=False)

        # Assert
        assert result is not None
        assert result.name == sample_theme_create.name
        assert result.display_name == sample_theme_create.display_name
        assert result.category == sample_theme_create.category
        assert result.is_system is False
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_theme_with_commit_error(
        self, theme_service, sample_theme_create, mock_db_session
    ):
        """Test theme creation with database commit error."""
        # Arrange
        mock_db_session.commit.side_effect = Exception("Database error")
        mock_db_session.rollback = AsyncMock()

        # Act & Assert
        with pytest.raises(Exception):
            await theme_service.create_theme(sample_theme_create)

        mock_db_session.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_theme_found(self, theme_service, sample_theme, mock_db_session):
        """Test getting an existing theme."""
        # Arrange
        theme_id = sample_theme.id
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = sample_theme
        mock_db_session.execute.return_value = mock_result
        mock_db_session.commit = AsyncMock()

        # Act
        result = await theme_service.get_theme(theme_id)

        # Assert
        assert result is not None
        assert result.id == theme_id
        assert result.name == sample_theme.name
        mock_db_session.execute.assert_called_once()
        mock_db_session.commit.assert_called_once()  # Usage count update

    @pytest.mark.asyncio
    async def test_get_theme_not_found(self, theme_service, mock_db_session):
        """Test getting a non-existent theme."""
        # Arrange
        theme_id = uuid4()
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result

        # Act
        result = await theme_service.get_theme(theme_id)

        # Assert
        assert result is None
        mock_db_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_themes_no_filter(
        self, theme_service, sample_theme, mock_db_session
    ):
        """Test getting themes without filters."""
        # Arrange
        themes = [sample_theme]
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = themes
        mock_db_session.execute.return_value = mock_result

        # Act
        result = await theme_service.get_themes()

        # Assert
        assert result == themes
        mock_db_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_themes_with_search_filter(
        self, theme_service, sample_theme, mock_db_session
    ):
        """Test getting themes with search filters."""
        # Arrange
        search_request = ThemeSearchRequest(
            category=ThemeCategory.PROFESSIONAL,
            supports_dark_mode=True,
            search_term="test",
            limit=10,
        )
        themes = [sample_theme]
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = themes
        mock_db_session.execute.return_value = mock_result

        # Act
        result = await theme_service.get_themes(search_request)

        # Assert
        assert result == themes
        mock_db_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_themes_database_error(self, theme_service, mock_db_session):
        """Test getting themes with database error."""
        # Arrange
        mock_db_session.execute.side_effect = Exception("Database error")

        # Act
        result = await theme_service.get_themes()

        # Assert
        assert result == []

    @pytest.mark.asyncio
    async def test_update_theme_success(
        self, theme_service, sample_theme, mock_db_session
    ):
        """Test successful theme update."""
        # Arrange
        theme_id = sample_theme.id
        updates = ThemeUpdate(display_name="Updated Theme")

        # Mock get_theme to return our sample theme
        theme_service.get_theme = AsyncMock(return_value=sample_theme)
        mock_db_session.commit = AsyncMock()
        mock_db_session.refresh = AsyncMock()

        # Act
        result = await theme_service.update_theme(theme_id, updates)

        # Assert
        assert result is not None
        assert result.display_name == "Updated Theme"
        assert isinstance(result.updated_at, datetime)
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_theme_not_found(self, theme_service, mock_db_session):
        """Test updating a non-existent theme."""
        # Arrange
        theme_id = uuid4()
        updates = ThemeUpdate(display_name="Updated Theme")
        theme_service.get_theme = AsyncMock(return_value=None)

        # Act
        result = await theme_service.update_theme(theme_id, updates)

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_delete_theme_success(
        self, theme_service, sample_theme, mock_db_session
    ):
        """Test successful theme deletion (soft delete)."""
        # Arrange
        theme_id = sample_theme.id
        sample_theme.is_system = False  # Ensure it's not a system theme
        theme_service.get_theme = AsyncMock(return_value=sample_theme)
        mock_db_session.commit = AsyncMock()

        # Act
        result = await theme_service.delete_theme(theme_id)

        # Assert
        assert result is True
        assert sample_theme.is_active is False
        assert isinstance(sample_theme.updated_at, datetime)
        mock_db_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_system_theme_fails(
        self, theme_service, sample_theme, mock_db_session
    ):
        """Test that system themes cannot be deleted."""
        # Arrange
        theme_id = sample_theme.id
        sample_theme.is_system = True  # Make it a system theme
        theme_service.get_theme = AsyncMock(return_value=sample_theme)

        # Act
        result = await theme_service.delete_theme(theme_id)

        # Assert
        assert result is False

    @pytest.mark.asyncio
    async def test_delete_theme_not_found(self, theme_service, mock_db_session):
        """Test deleting a non-existent theme."""
        # Arrange
        theme_id = uuid4()
        theme_service.get_theme = AsyncMock(return_value=None)

        # Act
        result = await theme_service.delete_theme(theme_id)

        # Assert
        assert result is False

    @pytest.mark.asyncio
    async def test_generate_theme_css(self, theme_service, sample_theme):
        """Test CSS generation for themes."""
        # Act
        css = await theme_service.generate_theme_css(
            sample_theme,
            display_mode=DisplayMode.LIGHT,
            font_size=FontSize.MD,
            font_family=FontFamily.SYSTEM,
        )

        # Assert
        assert isinstance(css, str)
        assert ":root {" in css
        assert "--color-primary: #1e40af;" in css
        assert "--font-size-base: 16px;" in css
        assert "}" in css

    @pytest.mark.asyncio
    async def test_generate_theme_css_dark_mode(self, theme_service, sample_theme):
        """Test CSS generation for themes in dark mode."""
        # Act
        css = await theme_service.generate_theme_css(
            sample_theme,
            display_mode=DisplayMode.DARK,
            font_size=FontSize.LG,
            font_family=FontFamily.INTER,
        )

        # Assert
        assert isinstance(css, str)
        assert ":root {" in css
        assert "--color-primary: #3b82f6;" in css  # Dark mode primary
        assert "--font-size-base: 18px;" in css
        assert "'Inter'" in css

    @pytest.mark.asyncio
    async def test_check_theme_accessibility(
        self, theme_service, sample_theme, mock_db_session
    ):
        """Test theme accessibility checking."""
        # Arrange
        theme_id = sample_theme.id
        theme_service.get_theme = AsyncMock(return_value=sample_theme)

        # Act
        result = await theme_service.check_theme_accessibility(theme_id)

        # Assert
        assert result is not None
        assert result.theme_id == theme_id
        assert isinstance(result.wcag_aa_compliant, bool)
        assert isinstance(result.wcag_aaa_compliant, bool)
        assert isinstance(result.contrast_ratios, dict)
        assert isinstance(result.accessibility_issues, list)
        assert isinstance(result.recommendations, list)
        assert isinstance(result.overall_score, int)

    @pytest.mark.asyncio
    async def test_check_theme_accessibility_not_found(
        self, theme_service, mock_db_session
    ):
        """Test accessibility check for non-existent theme."""
        # Arrange
        theme_id = uuid4()
        theme_service.get_theme = AsyncMock(return_value=None)

        # Act
        result = await theme_service.check_theme_accessibility(theme_id)

        # Assert
        assert result is not None
        assert result.theme_id == theme_id
        assert result.wcag_aa_compliant is False
        assert result.wcag_aaa_compliant is False
        assert result.overall_score == 0

    def test_calculate_contrast_ratio(self, theme_service):
        """Test contrast ratio calculation."""
        # Test white on black (high contrast)
        ratio1 = theme_service._calculate_contrast_ratio("#ffffff", "#000000")
        assert ratio1 > 15  # Very high contrast

        # Test black on white (same high contrast)
        ratio2 = theme_service._calculate_contrast_ratio("#000000", "#ffffff")
        assert abs(ratio1 - ratio2) < 0.01  # Should be approximately equal

        # Test same color (no contrast)
        ratio3 = theme_service._calculate_contrast_ratio("#ffffff", "#ffffff")
        assert ratio3 == 1.0  # No contrast

        # Test moderate contrast
        ratio4 = theme_service._calculate_contrast_ratio("#1e40af", "#ffffff")
        assert 4 < ratio4 < 10  # Reasonable range for blue on white

    @pytest.mark.asyncio
    async def test_get_default_theme(
        self, theme_service, sample_theme, mock_db_session
    ):
        """Test getting the default system theme."""
        # Arrange
        sample_theme.name = "corporate_blue"
        sample_theme.is_system = True
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = sample_theme
        mock_db_session.execute.return_value = mock_result

        # Act
        result = await theme_service.get_default_theme()

        # Assert
        assert result is not None
        assert result.name == "corporate_blue"
        assert result.is_system is True

    @pytest.mark.asyncio
    async def test_get_default_theme_not_found(self, theme_service, mock_db_session):
        """Test getting default theme when none exists."""
        # Arrange
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result

        # Act
        result = await theme_service.get_default_theme()

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_get_theme_usage_stats(self, theme_service, mock_db_session):
        """Test getting theme usage statistics."""
        # Arrange
        mock_popular_result = Mock()
        mock_popular_result.fetchall.return_value = [
            ("Theme 1", 100, "professional"),
            ("Theme 2", 50, "creative"),
        ]

        mock_category_result = Mock()
        mock_category_result.fetchall.return_value = [
            ("professional", 5),
            ("creative", 3),
        ]

        mock_total_result = Mock()
        mock_total_result.scalar.return_value = 8

        mock_db_session.execute.side_effect = [
            mock_popular_result,
            mock_category_result,
            mock_total_result,
        ]

        # Act
        result = await theme_service.get_theme_usage_stats()

        # Assert
        assert isinstance(result, dict)
        assert "total_themes" in result
        assert "themes_by_category" in result
        assert "popular_themes" in result
        assert result["total_themes"] == 8
        assert len(result["popular_themes"]) == 2


class TestThemeServiceUserSettings:
    """Test cases for user settings functionality."""

    @pytest.fixture
    def sample_user_settings_create(self):
        """Sample user settings creation data."""
        return UserSettingsCreate(
            active_theme_id=uuid4(),
            display_mode=DisplayMode.LIGHT,
            font_size=FontSize.MD,
            font_family=FontFamily.SYSTEM,
        )

    @pytest.mark.asyncio
    async def test_create_user_settings_success(
        self, theme_service, sample_user_settings_create, mock_db_session
    ):
        """Test successful user settings creation."""
        # Arrange
        user_id = uuid4()
        tenant_id = uuid4()
        mock_db_session.commit = AsyncMock()
        mock_db_session.refresh = AsyncMock()

        # Act
        result = await theme_service.create_user_settings(
            user_id, tenant_id, sample_user_settings_create
        )

        # Assert
        assert result is not None
        assert result.user_id == user_id
        assert result.tenant_id == tenant_id
        assert result.active_theme_id == sample_user_settings_create.active_theme_id
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_user_settings_with_default_theme(
        self, theme_service, sample_theme, mock_db_session
    ):
        """Test user settings creation with default theme."""
        # Arrange
        user_id = uuid4()
        tenant_id = uuid4()
        settings_data = UserSettingsCreate()  # No theme specified
        theme_service.get_default_theme = AsyncMock(return_value=sample_theme)
        mock_db_session.commit = AsyncMock()
        mock_db_session.refresh = AsyncMock()

        # Act
        result = await theme_service.create_user_settings(
            user_id, tenant_id, settings_data
        )

        # Assert
        assert result is not None
        assert result.active_theme_id == sample_theme.id
        theme_service.get_default_theme.assert_called_once()

    @pytest.mark.asyncio
    async def test_apply_theme_to_user_success(
        self, theme_service, sample_theme, mock_db_session
    ):
        """Test successfully applying a theme to user."""
        # Arrange
        user_id = uuid4()
        tenant_id = uuid4()
        theme_id = sample_theme.id

        theme_service.get_theme = AsyncMock(return_value=sample_theme)
        theme_service.update_user_settings = AsyncMock(return_value=Mock())
        theme_service.record_theme_usage = AsyncMock()

        # Act
        result = await theme_service.apply_theme_to_user(user_id, tenant_id, theme_id)

        # Assert
        assert result is True
        theme_service.get_theme.assert_called_once_with(theme_id)
        theme_service.update_user_settings.assert_called_once()
        theme_service.record_theme_usage.assert_called_once()

    @pytest.mark.asyncio
    async def test_apply_theme_to_user_theme_not_found(
        self, theme_service, mock_db_session
    ):
        """Test applying non-existent theme to user."""
        # Arrange
        user_id = uuid4()
        tenant_id = uuid4()
        theme_id = uuid4()

        theme_service.get_theme = AsyncMock(return_value=None)

        # Act
        result = await theme_service.apply_theme_to_user(user_id, tenant_id, theme_id)

        # Assert
        assert result is False
        theme_service.get_theme.assert_called_once_with(theme_id)

    @pytest.mark.asyncio
    async def test_record_theme_usage(self, theme_service, mock_db_session):
        """Test recording theme usage."""
        # Arrange
        user_id = uuid4()
        theme_id = uuid4()
        mock_db_session.commit = AsyncMock()
        mock_db_session.refresh = AsyncMock()

        # Act
        result = await theme_service.record_theme_usage(user_id, theme_id, "manual")

        # Assert
        assert result is not None
        assert result.user_id == user_id
        assert result.theme_id == theme_id
        assert result.applied_via == "manual"
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once()


class TestThemeServiceErrorHandling:
    """Test error handling in theme service."""

    @pytest.mark.asyncio
    async def test_get_theme_database_error(self, theme_service, mock_db_session):
        """Test get_theme with database error."""
        # Arrange
        theme_id = uuid4()
        mock_db_session.execute.side_effect = Exception("Database error")

        # Act
        result = await theme_service.get_theme(theme_id)

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_update_theme_database_error(
        self, theme_service, sample_theme, mock_db_session
    ):
        """Test update_theme with database error."""
        # Arrange
        theme_id = sample_theme.id
        updates = ThemeUpdate(display_name="Updated")
        theme_service.get_theme = AsyncMock(return_value=sample_theme)
        mock_db_session.commit.side_effect = Exception("Database error")
        mock_db_session.rollback = AsyncMock()

        # Act
        result = await theme_service.update_theme(theme_id, updates)

        # Assert
        assert result is None
        mock_db_session.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_theme_database_error(
        self, theme_service, sample_theme, mock_db_session
    ):
        """Test delete_theme with database error."""
        # Arrange
        theme_id = sample_theme.id
        sample_theme.is_system = False
        theme_service.get_theme = AsyncMock(return_value=sample_theme)
        mock_db_session.commit.side_effect = Exception("Database error")
        mock_db_session.rollback = AsyncMock()

        # Act
        result = await theme_service.delete_theme(theme_id)

        # Assert
        assert result is False
        mock_db_session.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_theme_css_error(self, theme_service):
        """Test CSS generation with malformed theme."""
        # Arrange - theme with invalid color scheme
        invalid_theme = Mock()
        invalid_theme.color_scheme = "invalid"  # Should be dict
        invalid_theme.supports_dark_mode = True
        invalid_theme.css_variables = None
        invalid_theme.component_styles = None

        # Act
        css = await theme_service.generate_theme_css(invalid_theme)

        # Assert
        assert css == ""  # Should return empty string on error

    def test_calculate_contrast_ratio_invalid_colors(self, theme_service):
        """Test contrast ratio calculation with invalid colors."""
        # Test with invalid hex color
        ratio = theme_service._calculate_contrast_ratio("invalid", "#ffffff")
        assert ratio == 1.0  # Should return default on error

        # Test with malformed hex
        ratio2 = theme_service._calculate_contrast_ratio("#zzz", "#ffffff")
        assert ratio2 == 1.0  # Should return default on error
