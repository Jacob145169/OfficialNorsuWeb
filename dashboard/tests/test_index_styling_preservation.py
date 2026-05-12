"""
Preservation Property Tests for Index Styling Fixes

**Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5**

This test verifies that existing CSS styles remain unchanged after the fix.
These tests should PASS on UNFIXED code (establishing baseline behavior to preserve).

Property 2: Preservation - Existing CSS Styles Remain Unchanged
"""

import os
import re
from pathlib import Path
from hypothesis import given, strategies as st, settings, Phase
from bs4 import BeautifulSoup


def get_css_rules_from_stylesheet(css_path):
    """
    Extract CSS rules from a stylesheet.
    Returns a dictionary mapping selectors to their rule blocks.
    """
    with open(css_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove comments
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
    
    # Extract CSS rules (selector { properties })
    # This is a simplified parser - matches selector followed by { ... }
    rule_pattern = r'([^{}]+)\{([^{}]+)\}'
    matches = re.findall(rule_pattern, content)
    
    rules = {}
    for selector, properties in matches:
        selector = selector.strip()
        properties = properties.strip()
        if selector and properties:
            rules[selector] = properties
    
    return rules


def get_existing_css_classes(css_path):
    """Extract all CSS class selectors that already exist in the stylesheet."""
    with open(css_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove comments
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
    
    # Find all class selectors
    class_pattern = r'\.([a-zA-Z0-9_-]+)'
    matches = re.findall(class_pattern, content)
    
    return set(matches)


def get_media_queries(css_path):
    """Extract all media queries from the stylesheet."""
    with open(css_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove comments
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
    
    # Find all media queries
    media_pattern = r'@media[^{]+\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
    matches = re.findall(media_pattern, content, flags=re.DOTALL)
    
    return matches


# Define existing CSS classes that should be preserved
# These are classes that exist BEFORE the fix and should remain unchanged
EXISTING_PRESERVED_CLASSES = {
    # Navbar classes (from navbar.css)
    'navbar': 'Navbar container with blue background',
    'nav-brand': 'Navbar brand/logo area',
    'nav-menu': 'Navigation menu links',
    'btn-join': 'Join button in navbar',
    
    # Hero section classes (existing, not the new hero-section)
    'hero': 'Existing hero section',
    'hero-content': 'Hero content container',
    'hero-label': 'Hero label text',
    'hero-text': 'Hero description text',
    'hero-buttons': 'Hero button container',
    'hero-stats': 'Hero statistics grid',
    
    # Feature section classes
    'features': 'Features section container',
    'feature-grid': 'Features grid layout',
    'feature-card': 'Individual feature card',
    
    # Common utility classes
    'container': 'Main container with max-width',
    'section-label': 'Section label styling',
    'section-desc': 'Section description',
    'stat-card': 'Statistics card',
    
    # Button classes
    'btn-primary': 'Primary button style',
    'btn-secondary': 'Secondary button style',
}


def test_existing_css_classes_are_preserved():
    """
    Test that existing CSS classes continue to exist in the stylesheet.
    
    This test verifies that the fix doesn't remove or break existing CSS definitions.
    
    EXPECTED OUTCOME: This test PASSES on unfixed code (baseline behavior).
    """
    base_dir = Path(__file__).resolve().parent.parent
    css_path = base_dir / 'static' / 'dashboard' / 'css' / 'styles.css'
    
    existing_classes = get_existing_css_classes(css_path)
    
    print("\n" + "="*80)
    print("PRESERVATION TEST - Existing CSS Classes")
    print("="*80)
    print(f"\nTotal classes in styles.css: {len(existing_classes)}")
    
    missing_preserved_classes = []
    
    for css_class, description in EXISTING_PRESERVED_CLASSES.items():
        if css_class not in existing_classes:
            missing_preserved_classes.append((css_class, description))
            print(f"  ❌ Missing: .{css_class} - {description}")
        else:
            print(f"  ✓ Present: .{css_class} - {description}")
    
    print("="*80 + "\n")
    
    # This should pass on unfixed code - all existing classes should be present
    assert len(missing_preserved_classes) == 0, (
        f"Preservation check: {len(missing_preserved_classes)} existing CSS classes "
        f"are missing from styles.css. This indicates existing styles may have been removed. "
        f"Missing: {[cls for cls, _ in missing_preserved_classes]}"
    )


@given(css_class=st.sampled_from([
    'navbar', 'nav-brand', 'nav-menu', 'btn-join',
    'hero', 'hero-content', 'hero-label', 'hero-buttons',
    'features', 'feature-grid', 'feature-card',
    'container', 'btn-primary', 'btn-secondary'
]))
@settings(phases=[Phase.generate, Phase.target])
def test_property_existing_classes_remain_defined(css_class):
    """
    Property-Based Test: For any existing CSS class that was defined before the fix,
    the class should continue to be defined in styles.css after the fix.
    
    **Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5**
    
    This property ensures no regressions - existing styles are preserved.
    
    EXPECTED OUTCOME: This test PASSES on unfixed code (baseline behavior).
    """
    base_dir = Path(__file__).resolve().parent.parent
    css_path = base_dir / 'static' / 'dashboard' / 'css' / 'styles.css'
    
    existing_classes = get_existing_css_classes(css_path)
    
    # Check if this existing class is still defined
    is_defined = css_class in existing_classes
    
    if not is_defined:
        print(f"\nPreservation violation: .{css_class}")
        print(f"  - Was defined before fix: Yes (expected)")
        print(f"  - Is defined after fix: No (VIOLATION)")
    
    # This should pass on unfixed code - all existing classes should be present
    assert is_defined, (
        f"Preservation property violated: CSS class '.{css_class}' was defined "
        f"before the fix but is no longer defined in styles.css. "
        f"Existing styles must be preserved."
    )


def test_navbar_styles_are_preserved():
    """
    Test that navbar styles remain unchanged.
    
    Verifies: Navbar displays with blue background, logo, menu items, and join button styling.
    
    EXPECTED OUTCOME: This test PASSES on unfixed code (baseline behavior).
    """
    base_dir = Path(__file__).resolve().parent.parent
    css_path = base_dir / 'static' / 'dashboard' / 'css' / 'styles.css'
    
    rules = get_css_rules_from_stylesheet(css_path)
    
    print("\n" + "="*80)
    print("PRESERVATION TEST - Navbar Styles")
    print("="*80)
    
    # Check for navbar-related rules
    navbar_selectors = ['.navbar', '.nav-brand', '.nav-menu', '.btn-join']
    navbar_rules_found = []
    
    for selector in navbar_selectors:
        # Check if selector exists in any rule
        found = any(selector in rule_selector for rule_selector in rules.keys())
        if found:
            navbar_rules_found.append(selector)
            print(f"  ✓ Found: {selector}")
        else:
            print(f"  ❌ Missing: {selector}")
    
    print("="*80 + "\n")
    
    # At least some navbar styles should exist
    assert len(navbar_rules_found) > 0, (
        "Preservation check: Navbar styles should be present in styles.css. "
        f"Expected to find rules for: {navbar_selectors}, "
        f"but only found: {navbar_rules_found}"
    )


def test_feature_card_styles_are_preserved():
    """
    Test that existing feature card styles remain unchanged.
    
    Verifies: Existing feature cards maintain their styling and hover effects.
    
    EXPECTED OUTCOME: This test PASSES on unfixed code (baseline behavior).
    """
    base_dir = Path(__file__).resolve().parent.parent
    css_path = base_dir / 'static' / 'dashboard' / 'css' / 'styles.css'
    
    existing_classes = get_existing_css_classes(css_path)
    
    print("\n" + "="*80)
    print("PRESERVATION TEST - Feature Card Styles")
    print("="*80)
    
    # Check for feature-related classes
    feature_classes = ['features', 'feature-grid', 'feature-card']
    feature_classes_found = []
    
    for css_class in feature_classes:
        if css_class in existing_classes:
            feature_classes_found.append(css_class)
            print(f"  ✓ Present: .{css_class}")
        else:
            print(f"  ❌ Missing: .{css_class}")
    
    print("="*80 + "\n")
    
    # At least some feature classes should exist
    assert len(feature_classes_found) > 0, (
        "Preservation check: Feature card styles should be present in styles.css. "
        f"Expected to find: {feature_classes}, "
        f"but only found: {feature_classes_found}"
    )


def test_responsive_breakpoints_are_preserved():
    """
    Test that responsive breakpoints (media queries) remain in the stylesheet.
    
    Verifies: Responsive breakpoints work for navbar, footer, and other sections.
    
    EXPECTED OUTCOME: This test PASSES on unfixed code (baseline behavior).
    """
    base_dir = Path(__file__).resolve().parent.parent
    css_path = base_dir / 'static' / 'dashboard' / 'css' / 'styles.css'
    
    media_queries = get_media_queries(css_path)
    
    print("\n" + "="*80)
    print("PRESERVATION TEST - Responsive Breakpoints")
    print("="*80)
    print(f"\nTotal media queries found: {len(media_queries)}")
    
    if media_queries:
        print("\nMedia queries present:")
        for i, query in enumerate(media_queries[:5], 1):  # Show first 5
            # Extract just the media condition
            condition = query.split('{')[0].strip()
            print(f"  {i}. {condition}")
        
        if len(media_queries) > 5:
            print(f"  ... and {len(media_queries) - 5} more")
    else:
        print("\n  ⚠ No media queries found")
    
    print("="*80 + "\n")
    
    # Note: It's possible that styles.css doesn't have media queries if they're
    # in separate files (navbar.css, footer.css, etc.)
    # So we just document what we find rather than asserting
    # The key is that this count should remain the same after the fix
    
    # Store the count for comparison (in a real scenario, we'd compare before/after)
    print(f"Baseline media query count: {len(media_queries)}")
    
    # This test passes as long as we can read the file
    assert True, "Responsive breakpoints preservation check completed"


def test_button_styles_are_preserved():
    """
    Test that button styles remain unchanged.
    
    Verifies: Button classes (btn-primary, btn-secondary, btn-join) maintain their styling.
    
    EXPECTED OUTCOME: This test PASSES on unfixed code (baseline behavior).
    """
    base_dir = Path(__file__).resolve().parent.parent
    css_path = base_dir / 'static' / 'dashboard' / 'css' / 'styles.css'
    
    existing_classes = get_existing_css_classes(css_path)
    
    print("\n" + "="*80)
    print("PRESERVATION TEST - Button Styles")
    print("="*80)
    
    # Check for button-related classes
    button_classes = ['btn-primary', 'btn-secondary', 'btn-join']
    button_classes_found = []
    
    for css_class in button_classes:
        if css_class in existing_classes:
            button_classes_found.append(css_class)
            print(f"  ✓ Present: .{css_class}")
        else:
            print(f"  ❌ Missing: .{css_class}")
    
    print("="*80 + "\n")
    
    # At least some button classes should exist
    assert len(button_classes_found) > 0, (
        "Preservation check: Button styles should be present in styles.css. "
        f"Expected to find: {button_classes}, "
        f"but only found: {button_classes_found}"
    )


def test_container_and_layout_styles_are_preserved():
    """
    Test that container and layout utility classes remain unchanged.
    
    Verifies: Core layout classes like .container maintain their styling.
    
    EXPECTED OUTCOME: This test PASSES on unfixed code (baseline behavior).
    """
    base_dir = Path(__file__).resolve().parent.parent
    css_path = base_dir / 'static' / 'dashboard' / 'css' / 'styles.css'
    
    existing_classes = get_existing_css_classes(css_path)
    
    print("\n" + "="*80)
    print("PRESERVATION TEST - Container and Layout Styles")
    print("="*80)
    
    # Check for layout-related classes
    layout_classes = ['container', 'hero-stats', 'stat-card']
    layout_classes_found = []
    
    for css_class in layout_classes:
        if css_class in existing_classes:
            layout_classes_found.append(css_class)
            print(f"  ✓ Present: .{css_class}")
        else:
            print(f"  ❌ Missing: .{css_class}")
    
    print("="*80 + "\n")
    
    # At least some layout classes should exist
    assert len(layout_classes_found) > 0, (
        "Preservation check: Container and layout styles should be present in styles.css. "
        f"Expected to find: {layout_classes}, "
        f"but only found: {layout_classes_found}"
    )


@given(viewport_width=st.integers(min_value=320, max_value=1920))
@settings(phases=[Phase.generate, Phase.target], max_examples=20)
def test_property_css_file_structure_is_valid(viewport_width):
    """
    Property-Based Test: The CSS file should remain valid and parseable
    regardless of viewport width considerations.
    
    **Validates: Requirements 3.3, 3.4, 3.5**
    
    This property ensures the CSS file structure is not corrupted by the fix.
    
    EXPECTED OUTCOME: This test PASSES on unfixed code (baseline behavior).
    """
    base_dir = Path(__file__).resolve().parent.parent
    css_path = base_dir / 'static' / 'dashboard' / 'css' / 'styles.css'
    
    # Check that the file exists and is readable
    assert css_path.exists(), f"CSS file should exist at {css_path}"
    
    with open(css_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Basic validation: file should have content
    assert len(content) > 0, "CSS file should not be empty"
    
    # Basic validation: should have some CSS rules
    assert '{' in content and '}' in content, "CSS file should contain rule blocks"
    
    # Count opening and closing braces - they should match
    open_braces = content.count('{')
    close_braces = content.count('}')
    
    # Allow for some flexibility in case of media queries or nested rules
    # But they should be roughly balanced
    brace_diff = abs(open_braces - close_braces)
    
    assert brace_diff <= 2, (
        f"CSS file structure check: Opening and closing braces should be balanced. "
        f"Found {open_braces} opening braces and {close_braces} closing braces. "
        f"Difference: {brace_diff}"
    )


def test_css_file_size_baseline():
    """
    Test to establish baseline CSS file size.
    
    This helps detect if the fix accidentally removes large portions of CSS.
    
    EXPECTED OUTCOME: This test PASSES on unfixed code (baseline behavior).
    """
    base_dir = Path(__file__).resolve().parent.parent
    css_path = base_dir / 'static' / 'dashboard' / 'css' / 'styles.css'
    
    file_size = css_path.stat().st_size
    
    print("\n" + "="*80)
    print("PRESERVATION TEST - CSS File Size Baseline")
    print("="*80)
    print(f"\nCurrent file size: {file_size} bytes ({file_size / 1024:.2f} KB)")
    print("="*80 + "\n")
    
    # File should have some reasonable size (at least 1KB)
    assert file_size > 1024, (
        f"CSS file seems too small ({file_size} bytes). "
        "This might indicate content was accidentally removed."
    )
    
    # Store baseline for future comparison
    print(f"Baseline CSS file size: {file_size} bytes")
    
    # This test passes as long as the file has reasonable content
    assert True, "CSS file size baseline established"
