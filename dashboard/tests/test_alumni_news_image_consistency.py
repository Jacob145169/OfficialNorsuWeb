from django.test import Client, TestCase

from dashboard.models import AlumniNews


class AlumniNewsImageConsistencyTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.news_item = AlumniNews.objects.create(
            title='Celebration',
            content=(
                '<figure class="image"><img src="data:image/jpeg;base64,AAA"></figure>'
                '<p>Join us as we celebrate a meaningful milestone.</p>'
            ),
            image='alumni/news/cover.jpg',
            status='published',
        )

    def test_home_card_prefers_cover_image(self):
        response = self.client.get('/alumni/')

        self.assertEqual(response.status_code, 200)
        html = response.content.decode('utf-8')
        self.assertIn('/media/alumni/news/cover.jpg', html)

    def test_detail_page_uses_same_cover_image_and_strips_conflicting_lead_image(self):
        response = self.client.get(f'/alumni/news/?id={self.news_item.id}')

        self.assertEqual(response.status_code, 200)
        html = response.content.decode('utf-8')

        self.assertIn('/media/alumni/news/cover.jpg', html)
        self.assertNotIn('data:image/jpeg;base64,AAA', html)
        self.assertIn('Join us as we celebrate a meaningful milestone.', html)
