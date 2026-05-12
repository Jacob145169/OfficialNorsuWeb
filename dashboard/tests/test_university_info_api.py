import json

from django.contrib.auth.models import User
from django.test import Client, TestCase

from dashboard.models import UniversityInfo


class UniversityInfoAPITest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='superadmin_test',
            password='testpass123'
        )
        self.info = UniversityInfo.objects.create(
            general_mandate='General mandate text',
            vision='Vision text',
            mission='Mission text',
            strategic_goals='Strategic goals text',
            core_values='Core values text',
            quality_policy='Quality policy text',
        )

    def test_public_list_returns_university_information(self):
        response = self.client.get('/api/university-info/')

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(len(data['info']), 1)
        self.assertEqual(data['info'][0]['id'], self.info.id)
        self.assertEqual(data['info'][0]['generalMandate'], 'General mandate text')
        self.assertEqual(data['info'][0]['qualityPolicy'], 'Quality policy text')

    def test_authenticated_create_saves_university_information(self):
        self.client.force_login(self.user)

        response = self.client.post('/api/university-info/', data={
            'generalMandate': 'Updated mandate',
            'vision': 'Updated vision',
            'mission': 'Updated mission',
            'strategicGoals': 'Updated goals',
            'coreValues': 'Updated values',
            'qualityPolicy': 'Updated quality policy',
        })

        self.assertEqual(response.status_code, 201)
        self.assertEqual(UniversityInfo.objects.count(), 2)

        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(data['info']['generalMandate'], 'Updated mandate')

    def test_authenticated_update_modifies_existing_record(self):
        self.client.force_login(self.user)

        response = self.client.post(f'/api/university-info/{self.info.id}/', data={
            'generalMandate': 'Revised mandate',
            'vision': 'Revised vision',
            'mission': 'Revised mission',
            'strategicGoals': 'Revised goals',
            'coreValues': 'Revised values',
            'qualityPolicy': 'Revised policy',
        })

        self.assertEqual(response.status_code, 200)
        self.info.refresh_from_db()
        self.assertEqual(self.info.general_mandate, 'Revised mandate')
        self.assertEqual(self.info.quality_policy, 'Revised policy')
