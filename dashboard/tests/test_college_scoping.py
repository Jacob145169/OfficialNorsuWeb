from django.contrib.auth import get_user_model
from django.test import TestCase

from dashboard.models import AdminProfile, Alumni, College, Faculty, Post, Program


User = get_user_model()


class CollegeScopingTests(TestCase):
    def setUp(self):
        self.superadmin = User.objects.create_superuser(
            username='superadmin',
            email='superadmin@example.com',
            password='SuperAdmin123!',
        )
        self.cas = College.objects.create(
            name='College of Arts and Sciences',
            abbreviation='CAS',
            dean='CAS Dean',
        )
        self.cit = College.objects.create(
            name='College of Industrial Technology',
            abbreviation='CIT',
            dean='CIT Dean',
        )
        self.cas_admin = User.objects.create_user(
            username='casadmin',
            password='CollegeAdmin123!',
            is_staff=True,
        )
        AdminProfile.objects.create(user=self.cas_admin, college='cas')

    def test_superadmin_creating_college_provisions_scoped_admin_profile(self):
        self.client.force_login(self.superadmin)

        response = self.client.post('/api/colleges/', {
            'name': 'College of Engineering',
            'abbreviation': 'COE',
            'dean': 'COE Dean',
            'students': '0',
            'programs': '0',
            'instructors': '0',
            'status': 'active',
        })

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        self.assertTrue(College.objects.filter(abbreviation__iexact='coe').exists())

        profile = AdminProfile.objects.select_related('user').get(college='coe')
        self.assertTrue(profile.user.is_staff)
        self.assertFalse(profile.user.is_superuser)
        self.assertFalse(profile.user.has_usable_password())

    def test_college_admin_post_list_is_forced_to_own_college(self):
        Post.objects.create(title='CAS Post', content='Own', college='cas', status='published')
        Post.objects.create(title='CIT Post', content='Other', college='cit', status='published')
        self.client.force_login(self.cas_admin)

        response = self.client.get('/api/posts/get/?college=cit')

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload['success'])
        self.assertEqual([post['title'] for post in payload['posts']], ['CAS Post'])

    def test_college_admin_cannot_get_or_delete_other_college_post(self):
        other_post = Post.objects.create(title='CIT Post', content='Other', college='cit', status='published')
        self.client.force_login(self.cas_admin)

        detail_response = self.client.get(f'/api/posts/get/{other_post.id}/')
        delete_response = self.client.post(f'/api/posts/delete/{other_post.id}/')

        self.assertEqual(detail_response.status_code, 404)
        self.assertEqual(delete_response.status_code, 404)
        self.assertTrue(Post.objects.filter(pk=other_post.pk).exists())

    def test_college_admin_create_post_ignores_spoofed_college(self):
        self.client.force_login(self.cas_admin)

        response = self.client.post('/api/posts/create/', {
            'title': 'Spoofed',
            'content': 'Should stay CAS',
            'type': 'announcement',
            'college': 'cit',
        })

        self.assertEqual(response.status_code, 200)
        post = Post.objects.get(title='Spoofed')
        self.assertEqual(post.college, 'cas')

    def test_college_admin_program_and_faculty_lists_are_scoped(self):
        Program.objects.create(title='CAS Program', description='Own', college='cas')
        Program.objects.create(title='CIT Program', description='Other', college='cit')
        Faculty.objects.create(name='CAS Faculty', position='Dean', college='cas')
        Faculty.objects.create(name='CIT Faculty', position='Dean', college='cit')
        self.client.force_login(self.cas_admin)

        programs_response = self.client.get('/api/programs/')
        faculty_response = self.client.get('/api/faculty/?college=cit')

        self.assertEqual(programs_response.status_code, 200)
        self.assertEqual([p['title'] for p in programs_response.json()['programs']], ['CAS Program'])
        self.assertEqual(faculty_response.status_code, 200)
        self.assertEqual([f['name'] for f in faculty_response.json()['faculty']], ['CAS Faculty'])

    def test_college_admin_program_create_is_forced_to_assigned_college(self):
        self.client.force_login(self.cas_admin)

        response = self.client.post('/api/programs/', {
            'title': 'Spoofed Program',
            'description': 'Should stay under CAS',
            'college': 'cit',
            'duration': '4 years',
            'status': 'published',
        })

        self.assertEqual(response.status_code, 201)
        created_program = Program.objects.get(title='Spoofed Program')
        self.assertEqual(created_program.college, 'cas')
        self.assertEqual(created_program.college_ref, self.cas)

    def test_college_admin_program_list_is_scoped_to_assigned_college(self):
        Program.objects.create(title='CAS Program', description='Own', college='cas', college_ref=self.cas)
        Program.objects.create(title='CIT Program', description='Other', college='cit', college_ref=self.cit)
        self.client.force_login(self.cas_admin)

        response = self.client.get('/api/programs/?college=cit')

        self.assertEqual(response.status_code, 200)
        self.assertEqual([program['title'] for program in response.json()['programs']], ['CAS Program'])

    def test_college_admin_cannot_update_or_delete_other_college_program(self):
        other_program = Program.objects.create(
            title='CIT Program',
            description='Other',
            college='cit',
            college_ref=self.cit,
            duration='4 years',
        )
        self.client.force_login(self.cas_admin)

        update_response = self.client.post(f'/api/programs/{other_program.id}/', {
            'title': 'Hijacked Program',
        })
        delete_response = self.client.generic('DELETE', f'/api/programs/{other_program.id}/')

        self.assertEqual(update_response.status_code, 404)
        self.assertEqual(delete_response.status_code, 404)
        other_program.refresh_from_db()
        self.assertEqual(other_program.title, 'CIT Program')

    def test_college_admin_alumni_list_is_scoped_by_college_field(self):
        Alumni.objects.create(name='CAS Alum', batch='2025', course='CAS Course', college='cas')
        Alumni.objects.create(name='CIT Alum', batch='2025', course='CIT Course', college='cit')
        self.client.force_login(self.cas_admin)

        response = self.client.get('/api/alumni/?college=cit')

        self.assertEqual(response.status_code, 200)
        self.assertEqual([a['name'] for a in response.json()['alumni']], ['CAS Alum'])
