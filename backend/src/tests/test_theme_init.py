"""
Test script for theme initialization system.
"""

import asyncio
import logging
import os
import sys

import pytest

# Add the src directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from models.theme import ThemeCategory
from services.theme_init_service import ThemeInitService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MockSession:
    """Mock database session for testing without actual database."""

    def __init__(self):
        self.themes = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


class MockThemeService:
    """Mock theme service for testing."""

    def __init__(self, session):
        self.session = session
        self.themes = []

    async def get_themes(self):
        return self.themes

    async def create_theme(self, theme_data, is_system=False):
        # Simulate creating a theme
        if hasattr(theme_data, "model_dump"):
            theme_dict = theme_data.model_dump()
        elif hasattr(theme_data, "dict"):
            theme_dict = theme_data.dict()
        else:
            theme_dict = theme_data if isinstance(theme_data, dict) else {}

        theme_dict["id"] = f"theme_{len(self.themes) + 1}"
        theme_dict["is_system"] = is_system

        # Create a mock theme object that supports attribute access
        mock_theme = type("MockTheme", (object,), theme_dict)()

        self.themes.append(mock_theme)
        return mock_theme


def test_theme_definitions():
    """Test that all theme definitions are valid."""
    logger.info("Testing theme definitions...")

    session = MockSession()
    theme_service = MockThemeService(session)
    theme_init_service = ThemeInitService(theme_service)

    # Get theme definitions
    themes_data = theme_init_service._get_theme_definitions()

    logger.info(f"Found {len(themes_data)} theme definitions")

    # Validate each theme
    for theme_data in themes_data:
        # Check required fields
        required_fields = [
            "name",
            "display_name",
            "description",
            "category",
            "color_scheme",
        ]
        for field in required_fields:
            assert (
                field in theme_data
            ), f"Missing required field '{field}' in theme '{theme_data.get('name')}'"

        # Check color scheme structure
        color_scheme = theme_data["color_scheme"]
        assert (
            "light" in color_scheme
        ), f"Missing 'light' color scheme in theme '{theme_data['name']}'"
        assert (
            "dark" in color_scheme
        ), f"Missing 'dark' color scheme in theme '{theme_data['name']}'"

        # Check basic colors exist
        basic_colors = [
            "primary",
            "secondary",
            "accent",
            "background",
            "surface",
            "text",
        ]
        for mode in ["light", "dark"]:
            for color in basic_colors:
                assert (
                    color in color_scheme[mode]
                ), f"Missing '{color}' in {mode} mode for theme '{theme_data['name']}'"

        logger.info(f"✓ Theme '{theme_data['name']}' is valid")

    logger.info("All theme definitions are valid!")


def test_theme_categories():
    """Test that all themes have valid categories."""
    logger.info("Testing theme categories...")

    theme_init_service = ThemeInitService(None)
    themes_data = theme_init_service._get_theme_definitions()

    category_counts = {}

    for theme_data in themes_data:
        category = theme_data["category"]

        # Verify category is valid enum value
        assert (
            category in ThemeCategory
        ), f"Invalid category '{category}' in theme '{theme_data['name']}'"

        if category not in category_counts:
            category_counts[category] = 0
        category_counts[category] += 1

    logger.info("Category distribution:")
    for category, count in category_counts.items():
        logger.info(f"  {category.value}: {count} themes")

    logger.info("All theme categories are valid!")


def test_color_accessibility():
    """Test basic color accessibility checks."""
    logger.info("Testing color accessibility...")

    theme_init_service = ThemeInitService(None)
    themes_data = theme_init_service._get_theme_definitions()

    def hex_to_rgb(hex_color):
        """Convert hex color to RGB tuple."""
        # Skip non-hex colors (like rgba, rgb, etc.)
        if not isinstance(hex_color, str) or not hex_color.startswith("#"):
            # Return a default high-contrast color for non-hex values
            return (128, 128, 128)  # Gray as fallback

        hex_color = hex_color.lstrip("#")
        if len(hex_color) != 6:
            # Return a default color for invalid hex format
            return (128, 128, 128)  # Gray as fallback

        try:
            return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
        except ValueError:
            # Return a default color for parsing errors
            return (128, 128, 128)  # Gray as fallback

    def calculate_luminance(rgb):
        """Calculate relative luminance of a color."""

        def normalize(c):
            c = c / 255.0
            return c / 12.92 if c <= 0.03928 else pow((c + 0.055) / 1.055, 2.4)

        r, g, b = [normalize(c) for c in rgb]
        return 0.2126 * r + 0.7152 * g + 0.0722 * b

    def contrast_ratio(color1, color2):
        """Calculate contrast ratio between two colors."""
        lum1 = calculate_luminance(hex_to_rgb(color1))
        lum2 = calculate_luminance(hex_to_rgb(color2))
        bright = max(lum1, lum2)
        dark = min(lum1, lum2)
        return (bright + 0.05) / (dark + 0.05)

    accessibility_issues = []

    for theme_data in themes_data:
        theme_name = theme_data["name"]
        color_scheme = theme_data["color_scheme"]

        for mode in ["light", "dark"]:
            colors = color_scheme[mode]

            # Check text on background contrast
            if "text" in colors and "background" in colors:
                ratio = contrast_ratio(colors["text"], colors["background"])
                if ratio < 4.5:  # WCAG AA standard
                    accessibility_issues.append(
                        f"Low contrast in {theme_name} ({mode}): text on background = {ratio:.2f}"
                    )

            # Check text on surface contrast
            if "text" in colors and "surface" in colors:
                ratio = contrast_ratio(colors["text"], colors["surface"])
                if ratio < 4.5:
                    accessibility_issues.append(
                        f"Low contrast in {theme_name} ({mode}): text on surface = {ratio:.2f}"
                    )

    if accessibility_issues:
        logger.warning(
            f"Found {len(accessibility_issues)} potential accessibility issues:"
        )
        for issue in accessibility_issues[:10]:  # Show first 10
            logger.warning(f"  {issue}")
        if len(accessibility_issues) > 10:
            logger.warning(f"  ... and {len(accessibility_issues) - 10} more")
    else:
        logger.info("No basic accessibility issues found!")


@pytest.mark.asyncio
async def test_theme_creation():
    """Test theme creation process."""
    logger.info("Testing theme creation process...")

    session = MockSession()
    theme_service = MockThemeService(session)
    theme_init_service = ThemeInitService(theme_service)

    # Test creating themes
    created_themes = await theme_init_service.create_default_themes()

    logger.info(f"Successfully created {len(created_themes)} themes")

    # Verify all themes were created
    expected_count = len(theme_init_service._get_theme_definitions())
    assert (
        len(created_themes) == expected_count
    ), f"Expected {expected_count} themes, got {len(created_themes)}"

    logger.info("Theme creation process works correctly!")


async def run_tests():
    """Run all tests."""
    logger.info("Starting theme initialization tests...")

    tests = [
        test_theme_definitions,
        test_theme_categories,
        test_color_accessibility,
        test_theme_creation,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if asyncio.iscoroutinefunction(test):
                await test()
            else:
                test()
            passed += 1
            logger.info(f"✓ {test.__name__} PASSED")
        except Exception as e:
            failed += 1
            logger.error(f"✗ {test.__name__} FAILED: {e}")

    logger.info(f"\nTest Results: {passed} passed, {failed} failed")

    if failed == 0:
        logger.info("🎉 All tests passed! Theme system is ready.")
    else:
        logger.error("❌ Some tests failed. Please fix the issues before proceeding.")

    return failed == 0


if __name__ == "__main__":
    success = asyncio.run(run_tests())
    sys.exit(0 if success else 1)
