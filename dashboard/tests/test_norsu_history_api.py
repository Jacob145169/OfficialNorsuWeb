from django.contrib.auth import get_user_model
from django.test import TestCase

from dashboard.models import NorsuHistory


User = get_user_model()


class NorsuHistoryAPITests(TestCase):
    def setUp(self):
        self.superadmin = User.objects.create_superuser(
            username='historyadmin',
            email='historyadmin@example.com',
            password='SuperAdmin123!',
        )

    def test_superadmin_saved_history_persists_in_database(self):
        self.client.force_login(self.superadmin)

        response = self.client.post('/api/norsu-history/', {
            'title': 'NORSU HISTORY',
            'body': 'Persistent institutional history text.',
        })

        self.assertEqual(response.status_code, 200)
        post_payload = response.json()
        self.assertTrue(post_payload['success'])
        self.assertEqual(post_payload['message'], 'NORSU history saved successfully')
        self.assertEqual(post_payload['history']['body'], 'Persistent institutional history text.')
        self.assertEqual(post_payload['data']['content'], 'Persistent institutional history text.')
        self.assertIn('updatedAt', post_payload['history'])
        self.assertEqual(NorsuHistory.objects.count(), 1)
        history = NorsuHistory.objects.get()
        self.assertEqual(history.title, 'NORSU HISTORY')
        self.assertEqual(history.body, 'Persistent institutional history text.')

        self.client.logout()
        public_response = self.client.get('/api/norsu-history/')
        payload = public_response.json()

        self.assertEqual(public_response.status_code, 200)
        self.assertTrue(payload['success'])
        self.assertEqual(payload['history']['title'], 'NORSU HISTORY')
        self.assertEqual(payload['history']['body'], 'Persistent institutional history text.')
        self.assertEqual(payload['data']['content'], 'Persistent institutional history text.')

    def test_non_superadmin_cannot_modify_history(self):
        response = self.client.post('/api/norsu-history/', {
            'title': 'Blocked',
            'body': 'Should not save.',
        })

        self.assertEqual(response.status_code, 401)
        self.assertFalse(NorsuHistory.objects.exists())

    def test_superadmin_can_delete_history(self):
        NorsuHistory.objects.create(title='NORSU HISTORY', body='Delete me.')
        self.client.force_login(self.superadmin)

        response = self.client.delete('/api/norsu-history/')

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        self.assertFalse(NorsuHistory.objects.exists())
