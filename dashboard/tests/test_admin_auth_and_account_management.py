from django.contrib.auth import get_user_model
from django.test import TestCase

from dashboard.models import AdminProfile, College


User = get_user_model()


class AdminAuthAndAccountManagementTests(TestCase):
    def setUp(self):
        for name, abbreviation in [
            ('College of Arts and Sciences', 'CAS'),
            ('College of Industrial Technology', 'CIT'),
            ('College of Teacher Education', 'CTED'),
            ('College of Criminal Justice Education', 'CCJE'),
            ('College of Business Administration', 'CBA'),
            ('College of Agriculture and Forestry', 'CAF'),
        ]:
            College.objects.create(
                name=name,
                abbreviation=abbreviation,
                dean=f'{abbreviation} Dean',
            )

        self.superadmin = User.objects.create_superuser(
            username='superadmin',
            email='superadmin@example.com',
            password='SuperAdmin123!',
        )
        self.college_admin = User.objects.create_user(
            username='casadmin',
            password='CollegeAdmin123!',
            is_staff=True,
        )
        self.college_profile = AdminProfile.objects.create(
            user=self.college_admin,
            college='cas',
        )

    def test_login_redirects_college_admin_to_shared_admin_dashboard(self):
        response = self.client.post('/admin-login/', {
            'username': 'casadmin',
            'password': 'CollegeAdmin123!',
        })

        self.assertRedirects(response, '/admin-dashboard/')

    def test_college_admin_cannot_access_super_admin_dashboard(self):
        self.client.login(username='casadmin', password='CollegeAdmin123!')

        response = self.client.get('/super-admin-dashboard/')

        self.assertRedirects(response, '/admin-dashboard/')

    def test_admin_accounts_endpoint_auto_provisions_all_college_accounts(self):
        self.client.force_login(self.superadmin)

        response = self.client.get('/api/admin-accounts/')

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload['success'])
        self.assertEqual(len(payload['accounts']), 7)
        self.assertEqual(AdminProfile.objects.count(), 6)

        college_accounts = [account for account in payload['accounts'] if account['role'] == 'college_admin']
        self.assertTrue(all(account['exists'] for account in college_accounts))
        self.assertTrue(all(account['username'] for account in college_accounts))

    def test_superadmin_can_create_or_update_college_admin_credentials(self):
        self.client.force_login(self.superadmin)

        response = self.client.post(
            '/api/admin-accounts/cit/',
            {
                'username': 'citadmin',
                'password': 'CollegeAdmin456!',
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload['success'])

        created_user = User.objects.get(username='citadmin')
        created_profile = AdminProfile.objects.get(college='cit')
        self.assertEqual(created_profile.user, created_user)
        self.assertTrue(created_user.check_password('CollegeAdmin456!'))
        self.assertTrue(created_user.is_staff)
        self.assertFalse(created_user.is_superuser)

    def test_superadmin_can_change_own_username_and_password(self):
        self.client.force_login(self.superadmin)

        response = self.client.post(
            '/api/admin-accounts/superadmin/',
            {
                'username': 'real_superadmin',
                'password': 'RiverCloud928!',
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload['success'])

        self.superadmin.refresh_from_db()
        self.assertEqual(self.superadmin.username, 'real_superadmin')
        self.assertTrue(self.superadmin.check_password('RiverCloud928!'))

        self.client.logout()
        self.assertTrue(self.client.login(username='real_superadmin', password='RiverCloud928!'))

    def test_superadmin_dashboard_shows_superadmin_account_card(self):
        self.client.force_login(self.superadmin)

        response = self.client.get('/super-admin-dashboard/?tab=admin-accounts')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Super Admin')
        self.assertContains(response, 'University-wide access')
        self.assertContains(response, '/api/admin-accounts/superadmin/')
        self.assertContains(response, 'value="superadmin"', html=False)

    def test_superadmin_cannot_use_short_username_for_admin_account(self):
        self.client.force_login(self.superadmin)

        response = self.client.post(
            '/api/admin-accounts/caf/',
            {
                'username': 'short7',
                'password': 'ForestRiver482!',
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )

        self.assertEqual(response.status_code, 400)
        payload = response.json()
        self.assertFalse(payload['success'])
        self.assertIn('Username must be at least 8 characters long.', payload['error'])

    def test_superadmin_cannot_use_short_password_for_admin_account(self):
        self.client.force_login(self.superadmin)

        response = self.client.post(
            '/api/admin-accounts/caf/',
            {
                'username': 'cafadmin8',
                'password': 'short7',
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )

        self.assertEqual(response.status_code, 400)
        payload = response.json()
        self.assertFalse(payload['success'])
        self.assertIn('at least 8 characters', payload['error'])

    def test_standard_form_post_redirects_back_to_admin_accounts_tab(self):
        self.client.force_login(self.superadmin)

        response = self.client.post('/api/admin-accounts/caf/', {
            'username': 'caf_updated',
            'password': 'ForestRiver482!',
        })

        self.assertRedirects(response, '/super-admin-dashboard/?tab=admin-accounts')
