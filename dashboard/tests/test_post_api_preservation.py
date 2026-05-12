"""
Preservation Property Tests for Post Management API Fix

**Validates: Requirements 3.1, 3.2, 3.3, 3.4**

These tests verify that the fix for missing Post API endpoints does NOT break
existing functionality. They test that non-API requests continue to work exactly
as before the fix.

Property 2: Preservation - Non-API Request Behavior
For any HTTP request where the path is NOT one of the three missing API endpoints,
the fixed system SHALL produce exactly the same routing, view handling, and response
behavior as the original system.

IMPORTANT: These tests should PASS on UNFIXED code to establish baseline behavior.
"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from dashboard.models import Post, Alumni, Announcement, News, Achievement, Program


class PostAPIPreservationTest(TestCase):
    """
    Test that verifies existing functionality is preserved after the API fix.
    
    EXPECTED BEHAVIOR: All tests PASS on both unfixed and fixed code
    """
    
    def setUp(self):
        """Set up test client and test data"""
        self.client = Client()
        
        # Create a test user for authentication
        self.user = User.objects.create_user(
            username='testadmin',
            password='testpass123',
            is_staff=True,
            is_superuser=True
        )
    
    def test_super_admin_dashboard_renders_correctly(self):
        """
        Test that /super-admin-dashboard/ continues to render correctly.
        
        **Validates: Requirement 3.1**
        """
        # Login first
        self.client.login(username='testadmin', password='testpass123')
        
        response = self.client.get('/super-admin-dashboard/')
        
        # Should return 200 OK
        self.assertEqual(response.status_code, 200,
                        "Super admin dashboard should be accessible")
        
        # Should render the correct template
        self.assertTemplateUsed(response, 'dashboard/super-admin-dashboard.html',
                               "Should use super-admin-dashboard.html template")
    
    def test_authentication_flow_works(self):
        """
        Test that login/logout flow continues to work.
        
        **Validates: Requirement 3.4**
        """
        # Test login page renders
        response = self.client.get('/super-admin-login/')
        self.assertEqual(response.status_code, 200,
                        "Login page should be accessible")
        self.assertTemplateUsed(response, 'dashboard/super-admin-login.html')
        
        # Test login functionality
        response = self.client.post('/super-admin-login/', {
            'username': 'testadmin',
            'password': 'testpass123'
        })
        # Should redirect after successful login
        self.assertEqual(response.status_code, 302,
                        "Should redirect after successful login")
    
    def test_cas_dashboard_continues_to_work(self):
        """
        Test that /cas/ dashboard continues to function.
        
        **Validates: Requirement 3.3**
        """
        response = self.client.get('/cas/')
        self.assertEqual(response.status_code, 200,
                        "CAS dashboard should be accessible")
        self.assertTemplateUsed(response, 'dashboard/dashbordcas.html')
    
    def test_cit_dashboard_continues_to_work(self):
        """
        Test that /cit/ dashboard continues to function.
        
        **Validates: Requirement 3.3**
        """
        response = self.client.get('/cit/')
        self.assertEqual(response.status_code, 200,
                        "CIT dashboard should be accessible")
        self.assertTemplateUsed(response, 'dashboard/dashbordcit.html')
    
    def test_cted_dashboard_continues_to_work(self):
        """
        Test that /cted/ dashboard continues to function.
        
        **Validates: Requirement 3.3**
        """
        response = self.client.get('/cted/')
        self.assertEqual(response.status_code, 200,
                        "CTED dashboard should be accessible")
        self.assertTemplateUsed(response, 'dashboard/dashbordcted.html')
    
    def test_ccje_dashboard_continues_to_work(self):
        """
        Test that /ccje/ dashboard continues to function.
        
        **Validates: Requirement 3.3**
        """
        response = self.client.get('/ccje/')
        self.assertEqual(response.status_code, 200,
                        "CCJE dashboard should be accessible")
        self.assertTemplateUsed(response, 'dashboard/dashbordccje.html')
    
    def test_cba_dashboard_continues_to_work(self):
        """
        Test that /cba/ dashboard continues to function.
        
        **Validates: Requirement 3.3**
        """
        response = self.client.get('/cba/')
        self.assertEqual(response.status_code, 200,
                        "CBA dashboard should be accessible")
        self.assertTemplateUsed(response, 'dashboard/dashbordcba.html')
    
    def test_caf_dashboard_continues_to_work(self):
        """
        Test that /caf/ dashboard continues to function.
        
        **Validates: Requirement 3.3**
        """
        response = self.client.get('/caf/')
        self.assertEqual(response.status_code, 200,
                        "CAF dashboard should be accessible")
        self.assertTemplateUsed(response, 'dashboard/dashbordcaf.html')
    
    def test_news_dashboard_continues_to_work(self):
        """
        Test that /news/ dashboard continues to function.
        
        **Validates: Requirement 3.3**
        """
        response = self.client.get('/news/')
        self.assertEqual(response.status_code, 200,
                        "News dashboard should be accessible")
        self.assertTemplateUsed(response, 'dashboard/newsdashbord.html')
    
    def test_alumni_dashboard_continues_to_work(self):
        """
        Test that /alumnidasbord/ dashboard continues to function.
        
        **Validates: Requirement 3.3**
        """
        response = self.client.get('/alumnidasbord/')
        self.assertEqual(response.status_code, 200,
                        "Alumni dashboard should be accessible")
        self.assertTemplateUsed(response, 'dashboard/alumnidasbord.html')
    
    def test_index_page_continues_to_work(self):
        """
        Test that index page continues to function.
        
        **Validates: Requirement 3.3**
        """
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200,
                        "Index page should be accessible")
        self.assertTemplateUsed(response, 'dashboard/index.html')
    
    def test_post_model_crud_operations_work(self):
        """
        Test that Post model CRUD operations continue to work.
        
        **Validates: Requirement 3.2**
        """
        # Create
        post = Post.objects.create(
            title='Test Post',
            content='Test content',
            category='general',
            target_audience='all',
            status='published'
        )
        self.assertIsNotNone(post.id, "Post should be created with an ID")
        
        # Read
        retrieved_post = Post.objects.get(id=post.id)
        self.assertEqual(retrieved_post.title, 'Test Post')
        
        # Update
        retrieved_post.title = 'Updated Post'
        retrieved_post.save()
        updated_post = Post.objects.get(id=post.id)
        self.assertEqual(updated_post.title, 'Updated Post')
        
        # Delete
        post_id = post.id
        post.delete()
        self.assertFalse(Post.objects.filter(id=post_id).exists())
    
    def test_other_models_unaffected(self):
        """
        Test that other models (Alumni, Announcement, News, Achievement, Program)
        continue to work correctly.
        
        **Validates: Requirement 3.2**
        """
        # Test Alumni model
        alumni = Alumni.objects.create(
            name='Test Alumni',
            email='test@example.com',
            batch='2020',
            course='Computer Science'
        )
        self.assertIsNotNone(alumni.id)
        
        # Test Announcement model
        announcement = Announcement.objects.create(
            title='Test Announcement',
            content='Test content',
            priority='medium'
        )
        self.assertIsNotNone(announcement.id)
        
        # Test News model
        news = News.objects.create(
            title='Test News',
            content='Test content',
            category='general'
        )
        self.assertIsNotNone(news.id)
        
        # Test Achievement model
        achievement = Achievement.objects.create(
            title='Test Achievement',
            description='Test description',
            category='academic'
        )
        self.assertIsNotNone(achievement.id)
        
        # Test Program model
        program = Program.objects.create(
            title='Test Program',
            description='Test description',
            level='undergraduate',
            college='cas'
        )
        self.assertIsNotNone(program.id)
