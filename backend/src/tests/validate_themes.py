"""
Standalone validation script for theme definitions.
This does not require any imports from the main codebase.
"""

import asyncio
import logging
import os
import sys
from enum import Enum
from typing import Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Define theme categories for validation
class ThemeCategory(str, Enum):
    PROFESSIONAL = "professional"
    CREATIVE = "creative"
    INDUSTRY = "industry"
    ACCESSIBILITY = "accessibility"


# Path to the theme definition file
THEME_SERVICE_PATH = os.path.join(
    os.path.dirname(__file__), "..", "services", "theme_init_service.py"
)


def extract_theme_definitions(filepath: str) -> list[dict[str, Any]]:
    """Extract theme definitions from the theme service file."""
    try:
        with open(filepath) as f:
            content = f.read()

        # Find the start of the theme definitions array
        start_marker = "def _get_theme_definitions(self) -> List[Dict[str, Any]]:"
        end_marker = "        ]"  # End of the array

        if start_marker not in content:
            logger.error(f"Could not find theme definitions in {filepath}")
            return []

        # Extract the content between markers
        start_idx = content.find(start_marker)
        start_idx = content.find("return [", start_idx)
        start_idx = content.find("[", start_idx) + 1

        end_idx = content.find(end_marker, start_idx)

        # Get the theme array content
        themes_content = content[start_idx:end_idx].strip()

        # Parse theme definitions
        themes = []
        current_theme = {}
        theme_lines = []
        in_theme = False

        for line in themes_content.split("\n"):
            line = line.strip()

            # Start of a new theme
            if line.startswith("{"):
                in_theme = True
                theme_lines = [line]

            # Inside a theme definition
            elif in_theme:
                theme_lines.append(line)

                # End of the theme
                if line.startswith("},"):
                    # Join lines and parse
                    theme_str = "\n".join(theme_lines)
                    # Clean up the theme string to make it valid JSON
                    theme_str = theme_str.rstrip(",")  # Remove trailing comma

                    # Replace enum values with strings
                    for category in ThemeCategory:
                        theme_str = theme_str.replace(
                            f"ThemeCategory.{category.name}", f'"{category.value}"'
                        )

                    # Remove Python comments
                    lines = theme_str.split("\n")
                    cleaned_lines = []
                    for line in lines:
                        comment_idx = line.find("#")
                        if comment_idx >= 0:
                            line = line[:comment_idx].rstrip()
                        cleaned_lines.append(line)
                    theme_str = "\n".join(cleaned_lines)

                    try:
                        # Parse as dictionary with eval (since it's not valid JSON with Python syntax)
                        theme_dict = eval(theme_str, {"__builtins__": {}})
                        themes.append(theme_dict)
                    except Exception as e:
                        logger.error(f"Error parsing theme: {e}")

                    in_theme = False

        logger.info(f"Successfully extracted {len(themes)} theme definitions")
        return themes

    except Exception as e:
        logger.error(f"Error extracting theme definitions: {e}")
        return []


async def validate_theme_definitions(themes: list[dict[str, Any]]) -> bool:
    """Validate that all theme definitions are correct."""
    logger.info("Validating theme definitions...")

    if not themes:
        logger.error("No themes found to validate")
        return False

    logger.info(f"Found {len(themes)} theme definitions")

    is_valid = True

    # Validate each theme
    for theme in themes:
        theme_name = theme.get("name", "Unknown")

        # Check required fields
        required_fields = [
            "name",
            "display_name",
            "description",
            "category",
            "color_scheme",
        ]
        for field in required_fields:
            if field not in theme:
                logger.error(f"Theme {theme_name} is missing required field: {field}")
                is_valid = False

        # Skip further validation if required fields are missing
        if not all(field in theme for field in required_fields):
            continue

        # Check category is valid
        try:
            category = theme["category"]
            if not any(category == cat.value for cat in ThemeCategory):
                logger.error(f"Theme {theme_name} has invalid category: {category}")
                is_valid = False
        except Exception:
            logger.error(f"Theme {theme_name} has invalid category format")
            is_valid = False

        # Check color scheme structure
        color_scheme = theme.get("color_scheme", {})
        if not isinstance(color_scheme, dict):
            logger.error(f"Theme {theme_name} has invalid color_scheme format")
            is_valid = False
            continue

        # Check light and dark modes exist
        for mode in ["light", "dark"]:
            if mode not in color_scheme:
                logger.error(f"Theme {theme_name} is missing {mode} color scheme")
                is_valid = False
                continue

            colors = color_scheme[mode]
            if not isinstance(colors, dict):
                logger.error(
                    f"Theme {theme_name} has invalid {mode} color scheme format"
                )
                is_valid = False
                continue

            # Check basic colors exist
            basic_colors = [
                "primary",
                "secondary",
                "accent",
                "background",
                "surface",
                "text",
            ]
            for color in basic_colors:
                if color not in colors:
                    logger.error(
                        f"Theme {theme_name} is missing {color} in {mode} mode"
                    )
                    is_valid = False

            # Validate color values are hex format
            for color_name, color_value in colors.items():
                if not isinstance(color_value, str) or not color_value.startswith("#"):
                    logger.error(
                        f"Theme {theme_name} has invalid color value for {color_name} in {mode} mode: {color_value}"
                    )
                    is_valid = False

        # Check dark mode is supported
        if "supports_dark_mode" not in theme:
            logger.warning(f"Theme {theme_name} does not specify supports_dark_mode")

        if is_valid:
            logger.info(f"✓ Theme {theme_name} is valid")
        else:
            logger.error(f"✗ Theme {theme_name} has validation errors")

    return is_valid


async def check_color_accessibility(themes: list[dict[str, Any]]) -> bool:
    """Check basic color accessibility for the themes."""
    logger.info("Checking color accessibility...")

    def hex_to_rgb(hex_color: str) -> tuple:
        """Convert hex color to RGB tuple."""
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))

    def calculate_luminance(rgb: tuple) -> float:
        """Calculate relative luminance of a color."""

        def normalize(c):
            c = c / 255.0
            return c / 12.92 if c <= 0.03928 else pow((c + 0.055) / 1.055, 2.4)

        r, g, b = [normalize(c) for c in rgb]
        return 0.2126 * r + 0.7152 * g + 0.0722 * b

    def contrast_ratio(color1: str, color2: str) -> float:
        """Calculate contrast ratio between two colors."""
        lum1 = calculate_luminance(hex_to_rgb(color1))
        lum2 = calculate_luminance(hex_to_rgb(color2))
        bright = max(lum1, lum2)
        dark = min(lum1, lum2)
        return (bright + 0.05) / (dark + 0.05)

    accessibility_issues = []

    for theme in themes:
        theme_name = theme.get("name", "Unknown")
        color_scheme = theme.get("color_scheme", {})

        for mode in ["light", "dark"]:
            if mode not in color_scheme:
                continue

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
        return False
    else:
        logger.info("✓ No basic accessibility issues found!")
        return True


async def check_theme_categories(themes: list[dict[str, Any]]) -> bool:
    """Check theme category distribution."""
    logger.info("Checking theme categories...")

    category_counts = {}

    for theme in themes:
        category = theme.get("category")
        if not category:
            continue

        if category not in category_counts:
            category_counts[category] = 0
        category_counts[category] += 1

    logger.info("Category distribution:")
    for category, count in category_counts.items():
        logger.info(f"  {category}: {count} themes")

    # Check we have at least one theme in each category
    missing_categories = set(cat.value for cat in ThemeCategory) - set(
        category_counts.keys()
    )
    if missing_categories:
        logger.warning(f"Missing themes in categories: {', '.join(missing_categories)}")
        return False

    return True


async def run_validations() -> bool:
    """Run all theme validations."""
    logger.info("Starting theme validation...")

    # Extract theme definitions
    themes = extract_theme_definitions(THEME_SERVICE_PATH)
    if not themes:
        logger.error("Failed to extract theme definitions")
        return False

    # Run validation checks
    validation_results = await asyncio.gather(
        validate_theme_definitions(themes),
        check_color_accessibility(themes),
        check_theme_categories(themes),
    )

    # Check if all validations passed
    if all(validation_results):
        logger.info("🎉 All theme validations passed!")
        return True
    else:
        logger.error("❌ Some theme validations failed")
        return False


if __name__ == "__main__":
    # Ensure the theme service file exists
    if not os.path.exists(THEME_SERVICE_PATH):
        logger.error(f"Theme service file not found: {THEME_SERVICE_PATH}")
        sys.exit(1)

    success = asyncio.run(run_validations())
    sys.exit(0 if success else 1)
