"""
Bug Condition Exploration Test for Index Styling Fixes

**Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 2.10, 2.11, 2.12, 2.13**

This test verifies the bug condition: HTML elements with CSS classes that don't exist in styles.css
will appear unstyled. This test is EXPECTED TO FAIL on unfixed code - failure confirms the bug exists.

Property 1: Fault Condition - Missing CSS Classes Cause Unstyled Elements
"""

import os
import re
from pathlib import Path
from hypothesis import given, strategies as st, settings, Phase
from bs4 import BeautifulSoup


def get_css_classes_from_html(html_path):
    """Extract all CSS classes used in the HTML file."""
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    soup = BeautifulSoup(content, 'html.parser')
    classes = set()
    
    for element in soup.find_all(class_=True):
        for cls in element.get('class', []):
            classes.add(cls)
    
    return classes


def get_css_selectors_from_stylesheet(css_path):
    """Extract all CSS class selectors defined in the stylesheet."""
    with open(css_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove comments
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
    
    # Find all class selectors (including those with pseudo-classes and combinators)
    # Match patterns like .classname, .classname:hover, .parent .classname, etc.
    class_pattern = r'\.([a-zA-Z0-9_-]+)'
    matches = re.findall(class_pattern, content)
    
    return set(matches)


def get_missing_css_classes():
    """
    Identify CSS classes used in index.html that are not defined in styles.css.
    This is the bug condition.
    """
    # Get paths
    base_dir = Path(__file__).resolve().parent.parent
    html_path = base_dir / 'templates' / 'dashboard' / 'index.html'
    css_path = base_dir / 'static' / 'dashboard' / 'css' / 'styles.css'
    
    # Get classes from HTML and CSS
    html_classes = get_css_classes_from_html(html_path)
    css_classes = get_css_selectors_from_stylesheet(css_path)
    
    # Find missing classes
    missing_classes = html_classes - css_classes
    
    return missing_classes, html_classes, css_classes


# Define the specific sections we expect to be affected by missing CSS
EXPECTED_MISSING_CLASS_GROUPS = {
    'hero-section': ['hero-section', 'hero-slideshow', 'hero-slide', 'hero-overlay', 
                     'hero-content', 'hero-text-line', 'hero-title', 'hero-subtitle', 
                     'hero-tagline', 'university-name'],
    'top-cards': ['top-cards', 'label', 'highlight', 'info-btn'],
    'main-section': ['main-section', 'left-content', 'right-image', 'main-btn'],
    'uv-news': ['uv-news-section', 'uv-news-header', 'uv-title-group', 'uv-title', 
                'uv-subtitle', 'uv-nav-buttons', 'uv-nav-btn', 'uv-news-grid', 
                'uv-news-card', 'uv-card-content', 'uv-date', 'uv-card-title', 'uv-read-more'],
    'colleges': ['colleges-section', 'header', 'header-title-row', 'colleges-grid-wrapper', 
                 'colleges-nav-arrow', 'colleges-scroll', 'college-card-link', 
                 'college-card', 'college-title'],
    'alumni': ['alumni', 'top-header', 'title-row', 'subtitle', 'cards', 'avatar', 
               'quote', 'card-link', 'bottom', 'big-btn'],
    'achievements': ['achievements-section', 'section-header', 'title-content', 
                     'cards-container', 'achievement-card', 'highlighted', 'card-text', 
                     'card-title', 'achievement-dots'],
    'programs-offered': ['programs-offered-section', 'programs-offered-header', 
                         'programs-offered-title-group', 'programs-offered-title', 
                         'programs-offered-subtitle', 'programs-offered-grid', 
                         'program-offered-card', 'program-card-content', 'program-date', 
                         'program-card-title', 'program-college', 'program-learn-more', 
                         'programs-dots', 'programs-dot', 'programs-see-more-wrapper'],
    'location': ['location-section', 'location-header', 'map-frame', 'location-info', 
                 'info-item', 'btn-direction'],
    'admin-updates': ['admin-updates-section', 'admin-updates-container', 
                      'admin-updates-title', 'admin-updates-grid', 'admin-updates-loading', 
                      'admin-update-card', 'admin-update-image', 'admin-update-no-image', 
                      'admin-update-content', 'admin-update-title', 'admin-update-text', 
                      'admin-update-date', 'admin-updates-empty'],
    'upcoming-events': ['upcoming-events-section', 'events-container', 'events-title', 
                        'events-grid', 'events-loading', 'event-card', 'event-date-badge', 
                        'event-title', 'event-description', 'event-location'],
    'quick-links': ['quick-links-section', 'quick-links-container', 'quick-links-title', 
                    'quick-links-grid', 'quick-link-card']
}


def test_bug_condition_missing_css_classes_exist():
    """
    Test that verifies the bug condition exists: CSS classes are used in HTML
    but not defined in styles.css.
    
    EXPECTED OUTCOME: This test FAILS on unfixed code (proving the bug exists).
    When the fix is implemented, this test will PASS.
    """
    missing_classes, html_classes, css_classes = get_missing_css_classes()
    
    # Document the findings
    print("\n" + "="*80)
    print("BUG CONDITION EXPLORATION - Missing CSS Classes")
    print("="*80)
    print(f"\nTotal classes in HTML: {len(html_classes)}")
    print(f"Total classes in CSS: {len(css_classes)}")
    print(f"Missing classes: {len(missing_classes)}")
    
    if missing_classes:
        print("\n" + "-"*80)
        print("COUNTEREXAMPLES FOUND - Classes used in HTML but not defined in CSS:")
        print("-"*80)
        
        # Group missing classes by section
        for section_name, expected_classes in EXPECTED_MISSING_CLASS_GROUPS.items():
            section_missing = [cls for cls in expected_classes if cls in missing_classes]
            if section_missing:
                print(f"\n{section_name.upper()} Section:")
                for cls in section_missing:
                    print(f"  - .{cls}")
        
        # Show any other missing classes not in our expected groups
        all_expected = set()
        for classes in EXPECTED_MISSING_CLASS_GROUPS.values():
            all_expected.update(classes)
        
        other_missing = missing_classes - all_expected
        if other_missing:
            print("\nOTHER Missing Classes:")
            for cls in sorted(other_missing):
                print(f"  - .{cls}")
    
    print("\n" + "="*80)
    print("VISUAL IMPACT:")
    print("="*80)
    print("Elements with these missing classes will appear:")
    print("  - With browser default styling (Times New Roman font, no spacing)")
    print("  - Without intended backgrounds, colors, or layouts")
    print("  - Without proper grid/flexbox positioning")
    print("  - Without hover effects and transitions")
    print("  - As unstyled blocks of text instead of styled cards/sections")
    print("="*80 + "\n")
    
    # This assertion will FAIL on unfixed code (which is correct - it proves the bug exists)
    # When the fix is implemented, this assertion will PASS
    assert len(missing_classes) == 0, (
        f"Bug condition confirmed: {len(missing_classes)} CSS classes are used in HTML "
        f"but not defined in styles.css. These elements will appear unstyled. "
        f"Missing classes: {sorted(missing_classes)}"
    )


@given(css_class=st.sampled_from([
    'hero-section', 'uv-news-card', 'college-card', 'alumni', 
    'achievement-card', 'program-offered-card', 'location-section',
    'admin-update-card', 'event-card', 'quick-link-card'
]))
@settings(phases=[Phase.generate, Phase.target])
def test_property_missing_css_classes_cause_unstyled_elements(css_class):
    """
    Property-Based Test: For any CSS class used in index.html that is not defined
    in styles.css, the element will appear unstyled.
    
    **Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 2.10, 2.11, 2.12, 2.13**
    
    This test checks specific key classes from each section that should have styling.
    
    EXPECTED OUTCOME: This test FAILS on unfixed code (proving the bug exists).
    """
    missing_classes, html_classes, css_classes = get_missing_css_classes()
    
    # Check if this class is used in HTML
    if css_class in html_classes:
        # The bug condition: class is used in HTML but not defined in CSS
        is_bug_condition = css_class not in css_classes
        
        if is_bug_condition:
            print(f"\nCounterexample found: .{css_class}")
            print(f"  - Used in HTML: Yes")
            print(f"  - Defined in CSS: No")
            print(f"  - Result: Elements will appear UNSTYLED")
        
        # This assertion will FAIL on unfixed code for missing classes
        # When the fix is implemented, all classes will be defined in CSS
        assert css_class in css_classes, (
            f"Bug condition: CSS class '.{css_class}' is used in index.html "
            f"but not defined in styles.css. Elements with this class will appear unstyled."
        )


def test_specific_sections_have_css_definitions():
    """
    Test that specific sections mentioned in the bug report have their CSS classes defined.
    
    This test explicitly checks the 13 section groups identified in the bug report.
    
    EXPECTED OUTCOME: This test FAILS on unfixed code (proving the bug exists).
    """
    missing_classes, html_classes, css_classes = get_missing_css_classes()
    
    sections_with_missing_css = {}
    
    for section_name, expected_classes in EXPECTED_MISSING_CLASS_GROUPS.items():
        section_missing = [cls for cls in expected_classes if cls in html_classes and cls not in css_classes]
        if section_missing:
            sections_with_missing_css[section_name] = section_missing
    
    if sections_with_missing_css:
        print("\n" + "="*80)
        print("SECTIONS WITH MISSING CSS DEFINITIONS:")
        print("="*80)
        for section, missing in sections_with_missing_css.items():
            print(f"\n{section}:")
            print(f"  Missing {len(missing)} CSS classes: {', '.join(missing)}")
        print("="*80 + "\n")
    
    # This assertion will FAIL on unfixed code
    assert len(sections_with_missing_css) == 0, (
        f"Bug confirmed: {len(sections_with_missing_css)} sections have missing CSS definitions. "
        f"Affected sections: {', '.join(sections_with_missing_css.keys())}"
    )
