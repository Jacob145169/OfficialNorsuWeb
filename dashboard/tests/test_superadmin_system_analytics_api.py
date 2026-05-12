from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from dashboard.models import (
    AdminProfile,
    Alumni,
    Announcement,
    Achievement,
    College,
    ContactMessage,
    Facility,
    Faculty,
    MediaUpload,
    News,
    Post,
    Program,
    UniversityInfo,
)


User = get_user_model()


class SuperAdminSystemAnalyticsAPITest(TestCase):
    def setUp(self):
        self.cas = College.objects.create(
            name='College of Arts and Sciences',
            abbreviation='CAS',
            dean='CAS Dean',
            theme_color='#17cada',
            status='active',
        )
        self.cba = College.objects.create(
            name='College of Business Administration',
            abbreviation='CBA',
            dean='CBA Dean',
            theme_color='#f2994a',
            status='active',
        )

        self.superadmin = User.objects.create_superuser(
            username='superanalytics',
            email='superanalytics@example.com',
            password='SuperAdmin123!',
        )
        self.college_admin = User.objects.create_user(
            username='casadmin',
            password='CollegeAdmin123!',
            is_staff=True,
        )
        AdminProfile.objects.create(user=self.college_admin, college='cas')

        Post.objects.create(
            title='CAS Update',
            content='A system-wide update from CAS',
            post_type='news',
            category='academic',
            college='cas',
            status='published',
        )
        Announcement.objects.create(
            title='Enrollment Reminder',
            content='Enrollment closes this week.',
            priority='high',
        )
        News.objects.create(
            title='Research Milestone',
            content='Research center reached a new milestone.',
            category='academic',
        )
        Achievement.objects.create(
            title='National Competition Win',
            description='Students won first place.',
            category='academic',
            status='published',
        )
        Alumni.objects.create(
            name='Jane Doe',
            batch='2025',
            course='Bachelor of Science in Computer Science',
            college='cas',
            position='Engineer',
            company='Tech Co',
        )
        Program.objects.create(
            title='Bachelor of Science in Computer Science',
            description='Computer science program',
            level='undergraduate',
            college='cas',
            duration='4 years',
            status='published',
        )
        Faculty.objects.create(
            name='Prof. Smith',
            position='Professor',
            college='cas',
            status='active',
        )
        Facility.objects.create(
            name='Innovation Lab',
            type='Laboratory',
            capacity='40',
            college='cas',
            status='available',
        )
        MediaUpload.objects.create(
            title='Alumni Homecoming',
            description='Event gallery upload',
            media_type='photo',
            file=SimpleUploadedFile('homecoming.jpg', b'filecontent', content_type='image/jpeg'),
            year=2026,
            college='College of Arts and Sciences',
            approval_status='pending',
        )
        ContactMessage.objects.create(
            full_name='Concerned Parent',
            email='parent@example.com',
            subject='Need assistance',
            message='Please provide details on admissions.',
            is_read=False,
        )
        UniversityInfo.objects.create(
            general_mandate='Serve the public through education.',
            vision='A globally recognized state university.',
            mission='Provide transformative education.',
        )

    def test_superadmin_can_fetch_live_system_analytics(self):
        self.client.force_login(self.superadmin)

        response = self.client.get('/api/system-analytics/')

        self.assertEqual(response.status_code, 200)
        payload = response.json()

        self.assertTrue(payload['success'])
        self.assertEqual(payload['summary']['total_posts'], 1)
        self.assertEqual(payload['summary']['total_alumni'], 1)
        self.assertEqual(payload['summary']['total_colleges'], 2)
        self.assertEqual(payload['summary']['total_university_info'], 1)
        self.assertEqual(payload['summary']['total_inquiries'], 1)

        self.assertEqual(payload['content_distribution']['total'], 5)
        self.assertEqual(len(payload['content_distribution']['items']), 5)

        kpis = {item['key']: item['value'] for item in payload['kpis']}
        self.assertEqual(kpis['pending_media'], 1)
        self.assertEqual(kpis['unread_inquiries'], 1)
        self.assertEqual(kpis['managed_content'], 5)
        self.assertEqual(kpis['alumni_records'], 1)

        self.assertEqual(len(payload['monthly_activity']['labels']), 6)
        self.assertEqual(len(payload['monthly_activity']['values']), 6)
        self.assertEqual(payload['alumni_growth']['values'][-1], 1)

        top_engagement = payload['college_engagement']['items'][0]
        self.assertEqual(top_engagement['key'], 'cas')
        self.assertEqual(top_engagement['percentage'], 100)
        self.assertIn('1 posts', top_engagement['meta'])
        self.assertIn('1 alumni', top_engagement['meta'])

    def test_superadmin_dashboard_bootstraps_system_analytics(self):
        self.client.force_login(self.superadmin)

        response = self.client.get('/super-admin-dashboard/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['system_analytics']['summary']['total_posts'], 1)
        self.assertContains(response, 'Live database metrics updated')
        self.assertContains(response, 'Managed Content')
        self.assertContains(response, 'Monthly Activity')
        self.assertNotContains(response, 'systemAnalyticsBootstrap')
        self.assertNotContains(response, 'data-analytics-url=')

    def test_college_admin_cannot_fetch_system_analytics(self):
        self.client.force_login(self.college_admin)

        response = self.client.get('/api/system-analytics/')

        self.assertEqual(response.status_code, 403)
        payload = response.json()
        self.assertFalse(payload['success'])
        self.assertIn('Superadmin access required', payload['error'])
