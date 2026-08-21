"""Tests for analytics, settings, system info, student insights and password change."""
from django.conf import settings
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

FAST_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']

STUDENT_PAYLOAD = {
    'fullName': 'Insight User',
    'studentId': 'INS-001',
    'email': 'insight@studysync.ai',
    'department': 'Computer Science',
    'year': '2nd Year',
    'section': 'A',
    'availability': 'Morning',
    'learningPreference': 'Mixed',
    'password': 'password123',
    'confirmPassword': 'password123',
    'scores': {
        'Mathematics': 88,
        'Physics': 55,
        'Programming': 92,
        'Database Management': 78,
        'Operating Systems': 72,
    },
}


def register(client, payload=None):
    return client.post('/api/student/register/', payload or STUDENT_PAYLOAD, format='json')


def register_and_login(client, payload=None):
    """Register a student and sign in, returning the token-pair response."""
    payload = payload or STUDENT_PAYLOAD
    register(client, payload)
    return client.post(
        '/api/student/login/',
        {'email': payload['email'], 'password': payload['password']},
        format='json',
    ).data


def admin_headers(client):
    response = client.post(
        '/api/admin/login/',
        {'email': settings.ADMIN_EMAIL, 'password': settings.ADMIN_PASSWORD},
        format='json',
    )
    return {'HTTP_AUTHORIZATION': f"Bearer {response.data['access']}"}


@override_settings(PASSWORD_HASHERS=FAST_HASHERS)
class AdminAnalyticsTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.headers = admin_headers(self.client)

    def test_analytics_shape(self):
        for index in range(6):
            payload = {**STUDENT_PAYLOAD, 'studentId': f'ANA-{index + 1:03d}', 'email': f'ana{index}@studysync.ai'}
            register(self.client, payload)
        self.client.post('/api/groups/generate/', {}, format='json', **self.headers)

        response = self.client.get('/api/admin/analytics/', **self.headers)
        self.assertEqual(response.status_code, 200)
        data = response.data
        self.assertEqual(data['totalStudents'], 6)
        self.assertGreater(data['totalGroups'], 0)
        self.assertGreater(data['overallAverageScore'], 0)
        self.assertEqual(len(data['subjectAverages']), 5)
        self.assertIn('departmentPerformance', data)
        self.assertIn('strengthDistribution', data)
        self.assertIn('weaknessDistribution', data)
        self.assertIn('groupComparison', data)
        self.assertIn('studentsRequiringImprovement', data)

    def test_analytics_requires_admin(self):
        response = self.client.get('/api/admin/analytics/')
        self.assertEqual(response.status_code, 401)


@override_settings(PASSWORD_HASHERS=FAST_HASHERS)
class SettingsTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.headers = admin_headers(self.client)

    def test_settings_defaults(self):
        response = self.client.get('/api/admin/settings/', **self.headers)
        self.assertEqual(response.status_code, 200)
        data = response.data
        self.assertEqual(data['defaultGroupSize'], 4)
        self.assertIn('departments', data)
        self.assertEqual(data['notifyGroupsGenerated'], True)

    def test_update_settings(self):
        response = self.client.put(
            '/api/admin/settings/',
            {
                'defaultGroupSize': 5,
                'kmeansRandomState': 7,
                'notifyGroupsGenerated': False,
                'exportDefaultFormat': 'pdf',
            },
            format='json',
            **self.headers,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['defaultGroupSize'], 5)
        self.assertEqual(response.data['kmeansRandomState'], 7)
        self.assertEqual(response.data['notifyGroupsGenerated'], False)
        self.assertEqual(response.data['exportDefaultFormat'], 'pdf')

    def test_settings_used_for_group_generation(self):
        self.client.put('/api/admin/settings/', {'defaultGroupSize': 6}, format='json', **self.headers)
        for index in range(12):
            payload = {**STUDENT_PAYLOAD, 'studentId': f'SET-{index + 1:03d}', 'email': f'set{index}@studysync.ai'}
            register(self.client, payload)
        response = self.client.post('/api/groups/generate/', {}, format='json', **self.headers)
        self.assertEqual(response.status_code, 201)
        for group in response.data['groups']:
            self.assertLessEqual(len(group['members']), 6)


@override_settings(PASSWORD_HASHERS=FAST_HASHERS)
class SystemInfoTests(TestCase):
    def test_system_info(self):
        self.client = APIClient()
        headers = admin_headers(self.client)
        response = self.client.get('/api/admin/system-info/', **headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], 'StudySync AI')
        self.assertIn('version', response.data)
        self.assertIn('totalStudents', response.data)


@override_settings(PASSWORD_HASHERS=FAST_HASHERS)
class StudentInsightsTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_student_insights(self):
        tokens = register_and_login(self.client)
        headers = {'HTTP_AUTHORIZATION': f"Bearer {tokens['access']}"}
        response = self.client.get('/api/student/insights/', **headers)
        self.assertEqual(response.status_code, 200)
        data = response.data
        self.assertIn('academicSummary', data)
        self.assertIn('learningTrend', data)
        self.assertIn('strengthScore', data)
        self.assertIn('weaknessScore', data)
        self.assertIn('improvementSuggestions', data)
        self.assertIn('learningResources', data)
        self.assertIn('peerMentor', data)
        self.assertIn('studySessions', data)

    def test_change_password(self):
        tokens = register_and_login(self.client)
        headers = {'HTTP_AUTHORIZATION': f"Bearer {tokens['access']}"}
        response = self.client.post(
            '/api/student/change-password/',
            {'currentPassword': 'password123', 'newPassword': 'newpassword9'},
            format='json',
            **headers,
        )
        self.assertEqual(response.status_code, 200)

        self.client.post('/api/student/logout/', {'refresh': tokens['refresh']}, format='json', **headers)
        failed = self.client.post(
            '/api/student/login/',
            {'email': 'insight@studysync.ai', 'password': 'password123'},
            format='json',
        )
        self.assertEqual(failed.status_code, 401)
        success = self.client.post(
            '/api/student/login/',
            {'email': 'insight@studysync.ai', 'password': 'newpassword9'},
            format='json',
        )
        self.assertEqual(success.status_code, 200)

    def test_change_password_rejects_wrong_current(self):
        tokens = register_and_login(self.client)
        headers = {'HTTP_AUTHORIZATION': f"Bearer {tokens['access']}"}
        response = self.client.post(
            '/api/student/change-password/',
            {'currentPassword': 'wrongpass', 'newPassword': 'newpassword9'},
            format='json',
            **headers,
        )
        self.assertEqual(response.status_code, 401)
