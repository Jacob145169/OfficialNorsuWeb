from django.test import SimpleTestCase
from django.urls import resolve

from dashboard import views


class PublicUrlResolutionTests(SimpleTestCase):
    def test_public_single_segment_routes_resolve_before_college_router(self):
        route_to_view = {
            '/alumni/': views.alumni,
            '/news/': views.news,
            '/programs/': views.programs,
            '/contacts/': views.contacts,
            '/about/': views.aboutnorsu,
            '/academic-calendar/': views.academic_calendar,
            '/directory/': views.alumni_directory,
        }

        for route, expected_view in route_to_view.items():
            with self.subTest(route=route):
                match = resolve(route)
                self.assertIs(match.func, expected_view)

    def test_unknown_college_abbreviation_still_uses_generic_router(self):
        match = resolve('/coe/')

        self.assertIs(match.func, views.college_dashboard_router)
        self.assertEqual(match.kwargs['abbr'], 'coe')
