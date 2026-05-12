"""
Bug Condition Exploration Test for Post Management API

**Validates: Requirements 1.1, 1.2, 1.3**

This test explores the bug condition where API endpoints for post management
do not exist, causing 404 errors. On unfixed code, this test will FAIL,
confirming the bug exists. After the fix is implemented, this test will PASS,
confirming the expected behavior is satisfied.

Property 1: Fault Condition - API Endpoints Return Valid JSON Responses
For any HTTP request where the path is /api/posts/get/, /api/posts/create/,
or /api/posts/delete/{id}/, the fixed system SHALL return valid JSON responses
with appropriate HTTP status codes (not 404 Not Found).
"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from dashboard.models import Post
import json


class PostAPIBugConditionTest(TestCase):
    """
    Test that verifies the bug condition and expected behavior for Post API endpoints.
    
    EXPECTED BEHAVIOR ON UNFIXED CODE: All tests FAIL with 404 errors
    EXPECTED BEHAVIOR ON FIXED CODE: All tests PASS with valid JSON responses
    """
    
    def setUp(self):
        """Set up test client and test data"""
        self.client = Client()
        
        # Create a test user for authentication if needed
        self.user = User.objects.create_user(
            username='testadmin',
            password='testpass123'
        )
        
        # Create a test post for delete operations
        self.test_post = Post.objects.create(
            title='Test Post',
            content='Test content',
            category='general',
            target_audience='all',
            status='published'
        )
    
    def test_get_posts_endpoint_exists_and_returns_json(self):
        """
        Test that GET /api/posts/get/ returns valid JSON response.
        
        Bug Condition: On unfixed code, returns 404 Not Found
        Expected Behavior: Returns 200 OK with JSON array of posts
        
        **Validates: Requirements 1.1, 2.1**
        """
        response = self.client.get('/api/posts/get/')
        
        # After fix: endpoint should exist and return 200
        self.assertNotEqual(response.status_code, 404, 
                           "GET /api/posts/get/ should not return 404 - endpoint should exist")
        
        # After fix: should return JSON content type
        self.assertEqual(response['Content-Type'], 'application/json',
                        "Response should be JSON")
        
        # After fix: should return valid JSON
        try:
            data = json.loads(response.content)
            self.assertIsInstance(data, list, "Response should be a JSON array")
        except json.JSONDecodeError:
            self.fail("Response should be valid JSON")
    
    def test_create_post_endpoint_exists_and_creates_post(self):
        """
        Test that POST /api/posts/create/ creates a post and returns valid JSON.
        
        Bug Condition: On unfixed code, returns 404 Not Found
        Expected Behavior: Creates post in database and returns success JSON
        
        **Validates: Requirements 1.2, 2.2**
        """
        post_data = {
            'title': 'New Test Post',
            'content': 'New test content',
            'category': 'event',
            'target_audience': 'cas',
            'status': 'published'
        }
        
        initial_count = Post.objects.count()
        response = self.client.post('/api/posts/create/', data=post_data)
        
        # After fix: endpoint should exist and not return 404
        self.assertNotEqual(response.status_code, 404,
                           "POST /api/posts/create/ should not return 404 - endpoint should exist")
        
        # After fix: should return JSON content type
        self.assertEqual(response['Content-Type'], 'application/json',
                        "Response should be JSON")
        
        # After fix: should create post in database
        self.assertEqual(Post.objects.count(), initial_count + 1,
                        "A new post should be created in the database")
        
        # After fix: verify the created post has correct data
        new_post = Post.objects.latest('created_at')
        self.assertEqual(new_post.title, 'New Test Post')
        self.assertEqual(new_post.content, 'New test content')
        self.assertEqual(new_post.category, 'event')
        self.assertEqual(new_post.target_audience, 'cas')
    
    def test_delete_post_endpoint_exists_and_deletes_post(self):
        """
        Test that POST /api/posts/delete/{id}/ deletes a post and returns valid JSON.
        
        Bug Condition: On unfixed code, returns 404 Not Found
        Expected Behavior: Deletes post from database and returns success JSON
        
        **Validates: Requirements 1.3, 2.3**
        """
        post_id = self.test_post.id
        initial_count = Post.objects.count()
        
        response = self.client.post(f'/api/posts/delete/{post_id}/')
        
        # After fix: endpoint should exist and not return 404
        self.assertNotEqual(response.status_code, 404,
                           "POST /api/posts/delete/{id}/ should not return 404 - endpoint should exist")
        
        # After fix: should return JSON content type
        self.assertEqual(response['Content-Type'], 'application/json',
                        "Response should be JSON")
        
        # After fix: should delete post from database
        self.assertEqual(Post.objects.count(), initial_count - 1,
                        "Post should be deleted from the database")
        
        # After fix: verify post no longer exists
        self.assertFalse(Post.objects.filter(id=post_id).exists(),
                        "Deleted post should not exist in database")
    
    def test_delete_nonexistent_post_returns_error(self):
        """
        Test that POST /api/posts/delete/999/ returns appropriate error for non-existent post.
        
        Bug Condition: On unfixed code, returns 404 Not Found (endpoint doesn't exist)
        Expected Behavior: Returns error JSON with 404 status for non-existent post
        
        **Validates: Requirements 2.3**
        """
        response = self.client.post('/api/posts/delete/999/')
        
        # After fix: should return JSON content type (proves endpoint exists)
        self.assertEqual(response['Content-Type'], 'application/json',
                        "Response should be JSON - this proves endpoint exists")
        
        # After fix: should return 404 for non-existent post (this is correct REST behavior)
        self.assertEqual(response.status_code, 404,
                        "Should return 404 for non-existent post")
        
        # After fix: should return error in JSON
        try:
            data = json.loads(response.content)
            self.assertIn('error', data, "Response should contain error message")
            self.assertFalse(data.get('success', True), "Success should be False")
        except json.JSONDecodeError:
            self.fail("Response should be valid JSON")
