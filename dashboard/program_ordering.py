import re


_CUSTOM_PROGRAM_ORDER = {
    'cba': (
        'hospitality management',
        'business administration',
        'office administration',
    ),
}


def _normalize_program_title(title):
    return re.sub(r'\s+', ' ', re.sub(r'[^a-z0-9&\s-]+', ' ', (title or '').lower())).strip()


def get_program_sort_key(college_key, title):
    normalized_college = (college_key or '').strip().lower()
    normalized_title = _normalize_program_title(title)

    for index, keyword in enumerate(_CUSTOM_PROGRAM_ORDER.get(normalized_college, ())):
        if keyword in normalized_title:
            return (0, index, normalized_title)

    return (1, normalized_title)
