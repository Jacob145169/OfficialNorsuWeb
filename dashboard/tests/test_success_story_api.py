from django.contrib.auth import get_user_model
from django.test import TestCase

from dashboard.models import AlumniSuccessStory


class SuccessStoryAPITests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_superuser(
            username='superadmin',
            email='superadmin@example.com',
            password='testpass123',
        )
        self.client.force_login(self.user)

    def test_create_success_story_accepts_latin_honor_choices(self):
        response = self.client.post('/api/success-stories/', data={
            'alumni_name': 'Jane Doe',
            'achievement': 'Magna Cum Laude',
            'description': 'Sample success story',
            'status': 'published',
        })

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])

        story = AlumniSuccessStory.objects.get()
        self.assertEqual(story.alumni_name, 'Jane Doe')
        self.assertEqual(story.achievement, 'Magna Cum Laude')

    def test_create_success_story_rejects_invalid_achievement_choice(self):
        response = self.client.post('/api/success-stories/', data={
            'alumni_name': 'John Doe',
            'achievement': 'CEO of Tech Corp',
            'description': 'Sample success story',
            'status': 'published',
        })

        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()['success'])
        self.assertEqual(AlumniSuccessStory.objects.count(), 0)
