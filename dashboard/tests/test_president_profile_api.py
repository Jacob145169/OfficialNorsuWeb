import json
import shutil
import tempfile

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings

from dashboard.models import PresidentProfile


class PresidentProfileAPITest(TestCase):
    @classmethod
    def setUpClass(cls):
        cls._media_root = tempfile.mkdtemp()
        cls._settings = override_settings(MEDIA_ROOT=cls._media_root)
        cls._settings.enable()
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls._settings.disable()
        shutil.rmtree(cls._media_root, ignore_errors=True)

    def setUp(self):
        self.client = Client()
        self.superadmin = User.objects.create_superuser(
            username='superadmin_test',
            email='superadmin@example.com',
            password='testpass123',
        )

    def test_public_get_returns_database_president_profile(self):
        profile = PresidentProfile.objects.create(
            name='DR. TEST PRESIDENT',
            role='Campus President',
            caption='A database-backed message.',
        )

        response = self.client.get('/api/president-profile/')

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(data['profile']['id'], profile.id)
        self.assertEqual(data['profile']['name'], 'DR. TEST PRESIDENT')
        self.assertEqual(data['profile']['role'], 'Campus President')
        self.assertEqual(data['profile']['caption'], 'A database-backed message.')

    def test_superadmin_can_save_role_caption_and_photo(self):
        self.client.force_login(self.superadmin)
        image = SimpleUploadedFile(
            'president.gif',
            b'GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!'
            b'\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00'
            b'\x00\x02\x02D\x01\x00;',
            content_type='image/gif',
        )

        response = self.client.post('/api/president-profile/', data={
            'name': 'DR. UPDATED PRESIDENT',
            'role': 'University President',
            'caption': 'Updated from superadmin.',
            'image': image,
        })

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(data['profile']['name'], 'DR. UPDATED PRESIDENT')
        self.assertEqual(data['profile']['caption'], 'Updated from superadmin.')
        self.assertTrue(data['profile']['photo'])

        profile = PresidentProfile.objects.get()
        self.assertEqual(profile.role, 'University President')
        self.assertEqual(profile.caption, 'Updated from superadmin.')
        self.assertTrue(bool(profile.image))

    def test_non_superadmin_cannot_save_president_profile(self):
        user = User.objects.create_user(username='staff_test', password='testpass123')
        self.client.force_login(user)

        response = self.client.post('/api/president-profile/', data={
            'name': 'Unauthorized',
            'role': 'Unauthorized',
            'caption': 'Unauthorized',
        })

        self.assertEqual(response.status_code, 403)
        self.assertFalse(PresidentProfile.objects.exists())
