import re

from dashboard.models import College, Program, SiteContactInfo
from dashboard.program_ordering import get_program_sort_key


def _normalize_college_key(value):
    return (value or '').strip().lower()


def _summarize_college_description(college):
    raw = (college.about or college.hero_description or '').strip()
    if not raw:
        return f'Explore alumni, stories, and academic programs from {college.name}.'

    clean = re.sub(r'\s+', ' ', raw)
    return clean[:177] + '...' if len(clean) > 180 else clean


def _build_program_code(title):
    value = (title or '').strip()
    if not value:
        return ''

    lowered = value.lower()
    prefix = ''
    remainder = value

    known_prefixes = [
        ('bachelor of science in ', 'BS'),
        ('bachelor of science ', 'BS'),
        ('bachelor of arts in ', 'BA'),
        ('bachelor of arts ', 'BA'),
        ('bachelor of ', 'B'),
        ('master of science in ', 'MS'),
        ('master of science ', 'MS'),
        ('master of ', 'M'),
    ]

    for start, code in known_prefixes:
        if lowered.startswith(start):
            prefix = code
            remainder = value[len(start):]
            break

    tokens = []
    for part in re.split(r'[\s/&-]+', remainder):
        cleaned = re.sub(r'[^A-Za-z0-9]', '', part)
        if not cleaned:
            continue
        if cleaned.lower() in {'of', 'in', 'the', 'and', 'for'}:
            continue
        tokens.append(cleaned[0].upper())

    if prefix and tokens:
        return prefix + ''.join(tokens)
    if prefix:
        return prefix
    return ''.join(tokens[:6]) or value[:8].upper()


def global_colleges(request):
    colleges = list(College.objects.all().order_by('name'))
    visible_programs = Program.objects.exclude(status__in=['draft', 'archived']).order_by('title')

    programs_by_key = {}
    for program in visible_programs:
        college_key = _normalize_college_key(program.college)
        programs_by_key.setdefault(college_key, []).append({
            'title': program.title,
            'code': _build_program_code(program.title),
        })
    for college_key, programs in programs_by_key.items():
        programs.sort(key=lambda program: get_program_sort_key(college_key, program['title']))

    alumni_college_navigation = []
    for college in colleges:
        college_key = _normalize_college_key(college.abbreviation)
        alumni_college_navigation.append({
            'id': college.id,
            'name': college.name,
            'abbreviation': college.abbreviation,
            'key': college_key,
            'theme_color': college.theme_color or '#A51C30',
            'image_url': college.image.url if college.image else '',
            'description': _summarize_college_description(college),
            'programs': programs_by_key.get(college_key, []),
        })

    return {
        'global_colleges': colleges,
        'alumni_college_navigation': alumni_college_navigation,
    }


def site_contact_info(request):
    contact_info = SiteContactInfo.objects.order_by('-updated_at', '-created_at').first()
    if contact_info is None:
        contact_info = SiteContactInfo()

    return {
        'site_contact_info': contact_info,
    }
