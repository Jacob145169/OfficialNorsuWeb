"""
Unit Tests for Program Management API Endpoints

This test verifies that the Program API endpoints work correctly:
- GET /api/programs/ - List all programs
- POST /api/programs/ - Create a new program
- GET /api/programs/<id>/ - Retrieve a specific program
- PUT /api/programs/<id>/ - Update a program
- DELETE /api/programs/<id>/ - Delete a program

**Validates: Requirements 2.1, 2.2, 2.3, 2.5**
"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from dashboard.models import Program
import json


class ProgramAPITest(TestCase):
    """
    Test suite for Program API endpoints.
    Verifies CRUD operations work correctly.
    """
    
    def setUp(self):
        """Set up test client and test data"""
        self.client = Client()
        
        # Create a test user for authentication if needed
        self.user = User.objects.create_user(
            username='testadmin',
            password='testpass123'
        )
        
        # Create a test program for update/delete operations
        self.test_program = Program.objects.create(
            title='Bachelor of Science in Criminology',
            description='A comprehensive program in criminal justice',
            level='undergraduate',
            college='ccje',
            duration='4 years',
            status='published'
        )
    
    def test_list_programs_endpoint(self):
        """
        Test that GET /api/programs/ returns list of programs.
        
        **Validates: Requirements 2.4**
        """
        response = self.client.get('/api/programs/')
        
        # Should return 200 OK
        self.assertEqual(response.status_code, 200,
                        "GET /api/programs/ should return 200 OK")
        
        # Should return JSON content type
        self.assertEqual(response['Content-Type'], 'application/json',
                        "Response should be JSON")
        
        # Should return valid JSON with programs array
        data = json.loads(response.content)
        self.assertTrue(data.get('success'), "Response should have success=True")
        self.assertIn('programs', data, "Response should contain programs array")
        self.assertIsInstance(data['programs'], list, "Programs should be an array")
        self.assertGreater(len(data['programs']), 0, "Should return at least one program")
    
    def test_create_program_endpoint(self):
        """
        Test that POST /api/programs/ creates a program and returns 201 Created.
        
        **Validates: Requirements 2.1, 2.2, 2.3**
        """
        program_data = {
            'title': 'Bachelor of Science in Forensic Science',
            'description': 'Advanced forensic science program',
            'level': 'undergraduate',
            'college': 'ccje',
            'duration': '4 years',
            'status': 'published'
        }
        
        initial_count = Program.objects.count()
        response = self.client.post('/api/programs/', data=program_data)
        
        # Should return 201 Created
        self.assertEqual(response.status_code, 201,
                        "POST /api/programs/ should return 201 Created")
        
        # Should return JSON content type
        self.assertEqual(response['Content-Type'], 'application/json',
                        "Response should be JSON")
        
        # Should create program in database
        self.assertEqual(Program.objects.count(), initial_count + 1,
                        "A new program should be created in the database")
        
        # Should return created program data with ID
        data = json.loads(response.content)
        self.assertTrue(data.get('success'), "Response should have success=True")
        self.assertIn('program', data, "Response should contain program object")
        self.assertIn('id', data['program'], "Program should have database-generated ID")
        
        # Verify the created program has correct data
        new_program = Program.objects.latest('created_at')
        self.assertEqual(new_program.title, 'Bachelor of Science in Forensic Science')
        self.assertEqual(new_program.college, 'ccje')
        self.assertEqual(new_program.duration, '4 years')
    
    def test_create_program_missing_required_fields(self):
        """
        Test that POST /api/programs/ returns 400 Bad Request when required fields are missing.
        
        **Validates: Requirements 2.1**
        """
        # Missing title
        program_data = {
            'college': 'ccje',
            'duration': '4 years'
        }
        
        response = self.client.post('/api/programs/', data=program_data)
        
        # Should return 400 Bad Request
        self.assertEqual(response.status_code, 400,
                        "Should return 400 when title is missing")
        
        data = json.loads(response.content)
        self.assertFalse(data.get('success'), "Success should be False")
        self.assertIn('error', data, "Response should contain error message")
    
    def test_retrieve_program_endpoint(self):
        """
        Test that GET /api/programs/<id>/ returns a specific program.
        
        **Validates: Requirements 2.4**
        """
        program_id = self.test_program.id
        response = self.client.get(f'/api/programs/{program_id}/')
        
        # Should return 200 OK
        self.assertEqual(response.status_code, 200,
                        "GET /api/programs/<id>/ should return 200 OK")
        
        # Should return JSON with program data
        data = json.loads(response.content)
        self.assertTrue(data.get('success'), "Response should have success=True")
        self.assertIn('program', data, "Response should contain program object")
        self.assertEqual(data['program']['id'], program_id)
        self.assertEqual(data['program']['title'], 'Bachelor of Science in Criminology')
    
    def test_update_program_endpoint(self):
        """
        Test that PUT /api/programs/<id>/ updates a program.
        
        **Validates: Requirements 2.2**
        """
        program_id = self.test_program.id
        update_data = {
            'title': 'Updated Criminology Program',
            'duration': '5 years'
        }
        
        response = self.client.post(f'/api/programs/{program_id}/', data=update_data)
        
        # Should return 200 OK
        self.assertEqual(response.status_code, 200,
                        "PUT /api/programs/<id>/ should return 200 OK")
        
        # Should return JSON with updated program data
        data = json.loads(response.content)
        self.assertTrue(data.get('success'), "Response should have success=True")
        self.assertEqual(data['program']['title'], 'Updated Criminology Program')
        self.assertEqual(data['program']['duration'], '5 years')
        
        # Verify database was updated
        updated_program = Program.objects.get(pk=program_id)
        self.assertEqual(updated_program.title, 'Updated Criminology Program')
        self.assertEqual(updated_program.duration, '5 years')
    
    def test_delete_program_endpoint(self):
        """
        Test that DELETE /api/programs/<id>/ deletes a program.
        
        **Validates: Requirements 2.3**
        """
        program_id = self.test_program.id
        initial_count = Program.objects.count()
        
        # Use DELETE method via generic() since client.delete() doesn't support it directly
        response = self.client.generic('DELETE', f'/api/programs/{program_id}/')
        
        # Should return 200 OK
        self.assertEqual(response.status_code, 200,
                        "DELETE /api/programs/<id>/ should return 200 OK")
        
        # Should return JSON with success message
        data = json.loads(response.content)
        self.assertTrue(data.get('success'), "Response should have success=True")
        
        # Should delete program from database
        self.assertEqual(Program.objects.count(), initial_count - 1,
                        "Program should be deleted from the database")
        
        # Verify program no longer exists
        self.assertFalse(Program.objects.filter(id=program_id).exists(),
                        "Deleted program should not exist in database")
    
    def test_retrieve_nonexistent_program(self):
        """
        Test that GET /api/programs/999/ returns 404 for non-existent program.
        
        **Validates: Requirements 2.4**
        """
        response = self.client.get('/api/programs/999/')
        
        # Should return 404 Not Found
        self.assertEqual(response.status_code, 404,
                        "Should return 404 for non-existent program")
        
        # Should return error in JSON
        data = json.loads(response.content)
        self.assertFalse(data.get('success'), "Success should be False")
        self.assertIn('error', data, "Response should contain error message")
