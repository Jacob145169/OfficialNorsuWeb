from django.test import TestCase
from django.urls import reverse

from dashboard.models import AlumniSuccessStory


class SuccessStoryDetailPageTests(TestCase):
    def test_homepage_read_more_links_to_success_story_detail_page(self):
        story = AlumniSuccessStory.objects.create(
            alumni_name='Jane Doe',
            achievement='Summa Cum Laude',
            description='Jane story body',
            status='published',
        )

        response = self.client.get(reverse('index'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse('alumni_success_story_detail', args=[story.id]))

    def test_success_story_detail_page_renders_red_banner_layout(self):
        story = AlumniSuccessStory.objects.create(
            alumni_name='John Doe',
            achievement='Magna Cum Laude',
            description='<p>Story content for John Doe.</p>',
            status='published',
        )

        response = self.client.get(reverse('alumni_success_story_detail', args=[story.id]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Alumni Success Stories')
        self.assertContains(response, 'John Doe')
        self.assertContains(response, 'Magna Cum Laude')
