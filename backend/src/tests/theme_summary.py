"""
Simple theme summary script to show basic information about our theme definitions.
"""

import os
import re


def analyze_theme_file():
    """Analyze the theme initialization service file."""

    theme_file = os.path.join(
        os.path.dirname(__file__), "..", "services", "theme_init_service.py"
    )

    if not os.path.exists(theme_file):
        print(f"❌ Theme file not found: {theme_file}")
        return False

    with open(theme_file) as f:
        content = f.read()

    # Count themes by looking for theme definitions
    theme_patterns = [
        r'"name":\s*"([^"]+)"',  # Theme names
        r'"display_name":\s*"([^"]+)"',  # Display names
        r'"description":\s*"([^"]+)"',  # Descriptions
        r"ThemeCategory\.([A-Z_]+)",  # Categories
    ]

    theme_names = re.findall(theme_patterns[0], content)
    display_names = re.findall(theme_patterns[1], content)
    descriptions = re.findall(theme_patterns[2], content)
    categories = re.findall(theme_patterns[3], content)

    print("🎨 Theme System Summary")
    print("=" * 50)

    print(f"📊 Total themes defined: {len(theme_names)}")
    print(f"📊 Display names found: {len(display_names)}")
    print(f"📊 Descriptions found: {len(descriptions)}")
    print(f"📊 Categories used: {len(set(categories))}")

    print("\n🏷️ Theme Names:")
    for i, name in enumerate(theme_names, 1):
        print(f"  {i:2d}. {name}")

    print("\n📋 Display Names:")
    for i, display in enumerate(display_names, 1):
        print(f"  {i:2d}. {display}")

    print("\n📁 Categories Used:")
    category_counts = {}
    for cat in categories:
        category_counts[cat] = category_counts.get(cat, 0) + 1

    for cat, count in sorted(category_counts.items()):
        print(f"  - {cat}: {count} themes")

    # Check for color definitions
    color_patterns = [
        r'"primary":\s*"(#[0-9a-fA-F]{6})"',
        r'"background":\s*"(#[0-9a-fA-F]{6})"',
        r'"text":\s*"(#[0-9a-fA-F]{6})"',
    ]

    primary_colors = re.findall(color_patterns[0], content)
    bg_colors = re.findall(color_patterns[1], content)
    text_colors = re.findall(color_patterns[2], content)

    print("\n🎨 Color Definitions Found:")
    print(f"  - Primary colors: {len(primary_colors)}")
    print(f"  - Background colors: {len(bg_colors)}")
    print(f"  - Text colors: {len(text_colors)}")

    # Check for light/dark mode support
    light_count = content.count('"light":')
    dark_count = content.count('"dark":')

    print("\n🌓 Mode Support:")
    print(f"  - Light mode definitions: {light_count}")
    print(f"  - Dark mode definitions: {dark_count}")

    # Check accessibility features
    accessibility_features = [
        "high_contrast",
        "focus_indicators",
        "reduced_motion",
        "wcag_aaa_compliant",
        "wcag_aa_compliant",
        "screen_reader_optimized",
        "blue_light_filter",
        "eye_strain_reduction",
    ]

    found_features = []
    for feature in accessibility_features:
        if feature in content:
            count = content.count(feature)
            found_features.append(f"{feature}: {count}")

    print("\n♿ Accessibility Features:")
    for feature in found_features:
        print(f"  - {feature}")

    # Basic validation
    print("\n✅ Basic Validation:")

    issues = []

    if len(theme_names) != len(display_names):
        issues.append(
            f"Mismatch between theme names ({len(theme_names)}) and display names ({len(display_names)})"
        )

    if len(theme_names) != len(descriptions):
        issues.append(
            f"Mismatch between theme names ({len(theme_names)}) and descriptions ({len(descriptions)})"
        )

    if light_count != dark_count:
        issues.append(
            f"Mismatch between light mode ({light_count}) and dark mode ({dark_count}) definitions"
        )

    expected_themes = 12  # Based on our design
    if len(theme_names) < expected_themes:
        issues.append(
            f"Expected at least {expected_themes} themes, found {len(theme_names)}"
        )

    if not issues:
        print("  ✅ All basic validations passed!")
        print("\n🎉 Theme system appears to be properly defined!")
        return True
    else:
        print("  ❌ Issues found:")
        for issue in issues:
            print(f"     - {issue}")
        return False


if __name__ == "__main__":
    success = analyze_theme_file()
    exit(0 if success else 1)
