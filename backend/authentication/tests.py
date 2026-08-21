"""Tests for JWT authentication, admin login, refresh and logout."""
from django.conf import settings
from django.test import TestCase, override_settings
from rest_framework.test import APIClient


@override_settings(PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher'])
class AuthenticationTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def login_admin(self):
        return self.client.post(
            '/api/admin/login/',
            {'email': settings.ADMIN_EMAIL, 'password': settings.ADMIN_PASSWORD},
            format='json',
        )

    def test_admin_login_returns_token_pair(self):
        response = self.login_admin()
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.data['email'], settings.ADMIN_EMAIL)

    def test_admin_login_rejects_bad_credentials(self):
        response = self.client.post(
            '/api/admin/login/',
            {'email': 'admin@studysync.ai', 'password': 'wrong'},
            format='json',
        )
        self.assertEqual(response.status_code, 401)

    def test_protected_endpoint_rejects_missing_token(self):
        response = self.client.get('/api/admin/students/')
        self.assertEqual(response.status_code, 401)

    def test_admin_refresh_issues_new_access_token(self):
        login = self.login_admin()
        refresh = login.data['refresh']
        response = self.client.post('/api/admin/refresh/', {'refresh': refresh}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)

    def test_admin_logout_revokes_refresh_token(self):
        login = self.login_admin()
        refresh = login.data['refresh']
        logout = self.client.post('/api/admin/logout/', {'refresh': refresh}, format='json')
        self.assertEqual(logout.status_code, 200)

        second_refresh = self.client.post('/api/admin/refresh/', {'refresh': refresh}, format='json')
        self.assertEqual(second_refresh.status_code, 401)

    def test_student_token_denied_on_admin_endpoint(self):
        self.client.post(
            '/api/student/register/',
            {
                'fullName': 'Test Student',
                'studentId': 'STU-100',
                'email': 'test@studysync.ai',
                'department': 'Computer Science',
                'year': '1st Year',
                'section': 'A',
                'availability': 'Morning',
                'learningPreference': 'Mixed',
                'password': 'password123',
                'confirmPassword': 'password123',
                'scores': {
                    'Mathematics': 85,
                    'Physics': 70,
                    'Programming': 90,
                    'Database Management': 80,
                    'Operating Systems': 75,
                },
            },
            format='json',
        )
        student_login = self.client.post(
            '/api/student/login/',
            {'email': 'test@studysync.ai', 'password': 'password123'},
            format='json',
        )
        access = student_login.data['access']
        response = self.client.get('/api/admin/students/', HTTP_AUTHORIZATION=f'Bearer {access}')
        self.assertEqual(response.status_code, 403)
