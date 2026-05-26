import json

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase

from dashboard.models import UniversityInfo


class UniversityInfoAPITest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_superuser(
            username='superadmin_test',
            email='superadmin@example.com',
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
        self.assertEqual(data['info'][0]['visionImage'], '')
        self.assertEqual(data['info'][0]['missionImage'], '')

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

    def test_authenticated_update_can_attach_editorial_images(self):
        self.client.force_login(self.user)

        vision_image = SimpleUploadedFile(
            'vision.gif',
            b'GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!'
            b'\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00'
            b'\x00\x02\x02D\x01\x00;',
            content_type='image/gif',
        )
        mission_image = SimpleUploadedFile(
            'mission.gif',
            b'GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!'
            b'\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00'
            b'\x00\x02\x02D\x01\x00;',
            content_type='image/gif',
        )

        response = self.client.post(
            f'/api/university-info/{self.info.id}/',
            data={
                'vision': 'Vision with image',
                'mission': 'Mission with image',
                'visionImage': vision_image,
                'missionImage': mission_image,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.info.refresh_from_db()
        self.assertTrue(bool(self.info.vision_image))
        self.assertTrue(bool(self.info.mission_image))

        data = json.loads(response.content)
        self.assertTrue(data['info']['visionImage'])
        self.assertTrue(data['info']['missionImage'])
