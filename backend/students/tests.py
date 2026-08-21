"""Tests for student registration, login, profiles, dashboards and admin CRUD."""
import io

from django.conf import settings
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

FAST_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']

STUDENT_PAYLOAD = {
    'fullName': 'Aarav Sharma',
    'studentId': 'STU-001',
    'email': 'aarav@studysync.ai',
    'department': 'Computer Science',
    'year': '2nd Year',
    'section': 'A',
    'availability': 'Morning',
    'learningPreference': 'Practical',
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


def admin_headers(client):
    response = client.post(
        '/api/admin/login/',
        {'email': settings.ADMIN_EMAIL, 'password': settings.ADMIN_PASSWORD},
        format='json',
    )
    return {'HTTP_AUTHORIZATION': f"Bearer {response.data['access']}"}


@override_settings(PASSWORD_HASHERS=FAST_HASHERS)
class StudentRegistrationTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def register(self, payload=None):
        return self.client.post('/api/student/register/', payload or STUDENT_PAYLOAD, format='json')

    def test_register_returns_profile_without_tokens(self):
        response = self.register()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['fullName'], 'Aarav Sharma')
        self.assertEqual(response.data['studentId'], 'STU-001')
        self.assertEqual(response.data['scores']['Database Management'], 78)
        self.assertNotIn('access', response.data)
        self.assertNotIn('refresh', response.data)

    def test_register_saved_password_can_log_in(self):
        self.register()
        login = self.client.post(
            '/api/student/login/',
            {'email': 'aarav@studysync.ai', 'password': 'password123'},
            format='json',
        )
        self.assertEqual(login.status_code, 200)

    def test_register_requires_password(self):
        payload = {**STUDENT_PAYLOAD, 'password': '', 'confirmPassword': ''}
        response = self.register(payload)
        self.assertEqual(response.status_code, 400)

    def test_register_rejects_confirm_password_mismatch(self):
        payload = {**STUDENT_PAYLOAD, 'confirmPassword': 'different99'}
        response = self.register(payload)
        self.assertEqual(response.status_code, 400)

    def test_register_rejects_short_password(self):
        payload = {**STUDENT_PAYLOAD, 'password': 'short', 'confirmPassword': 'short'}
        response = self.register(payload)
        self.assertEqual(response.status_code, 400)

    def test_register_rejects_duplicate_student_id(self):
        self.register()
        response = self.register()
        self.assertEqual(response.status_code, 400)

    def test_register_rejects_duplicate_email(self):
        self.register()
        duplicate = {**STUDENT_PAYLOAD, 'studentId': 'STU-002'}
        response = self.register(duplicate)
        self.assertEqual(response.status_code, 400)


@override_settings(PASSWORD_HASHERS=FAST_HASHERS)
class StudentAuthTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.client.post('/api/student/register/', STUDENT_PAYLOAD, format='json')

    def test_login_returns_profile_and_tokens(self):
        response = self.client.post(
            '/api/student/login/',
            {'email': 'aarav@studysync.ai', 'password': 'password123'},
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['fullName'], 'Aarav Sharma')
        self.assertIn('access', response.data)

    def test_login_rejects_wrong_password(self):
        response = self.client.post(
            '/api/student/login/',
            {'email': 'aarav@studysync.ai', 'password': 'nope'},
            format='json',
        )
        self.assertEqual(response.status_code, 401)

    def test_login_rejects_unknown_email(self):
        response = self.client.post(
            '/api/student/login/',
            {'email': 'missing@studysync.ai', 'password': 'password123'},
            format='json',
        )
        self.assertEqual(response.status_code, 401)


@override_settings(PASSWORD_HASHERS=FAST_HASHERS)
class StudentProfileTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.client.post('/api/student/register/', STUDENT_PAYLOAD, format='json')
        login = self.client.post(
            '/api/student/login/',
            {'email': 'aarav@studysync.ai', 'password': 'password123'},
            format='json',
        )
        self.headers = {'HTTP_AUTHORIZATION': f"Bearer {login.data['access']}"}

    def test_profile_get_requires_auth(self):
        response = self.client.get('/api/student/profile/')
        self.assertEqual(response.status_code, 401)

    def test_profile_get_returns_expected_shape(self):
        response = self.client.get('/api/student/profile/', **self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['email'], 'aarav@studysync.ai')
        self.assertIn('assignedGroup', response.data)
        self.assertIn('overallGroupStrength', response.data)

    def test_profile_put_updates_scores(self):
        payload = {**STUDENT_PAYLOAD, 'scores': {**STUDENT_PAYLOAD['scores'], 'Physics': 90}}
        response = self.client.put('/api/student/profile/', payload, format='json', **self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['scores']['Physics'], 90)
        self.assertIn('Physics', response.data['strengths'])

    def test_profile_and_dashboard_include_insights(self):
        profile = self.client.get('/api/student/profile/', **self.headers).data
        self.assertIn('insights', profile)
        self.assertIn('learningTrend', profile['insights'])
        self.assertIn('improvementSuggestions', profile['insights'])
        self.assertIn('learningResources', profile['insights'])
        self.assertIn('studySessions', profile['insights'])

        dashboard = self.client.get('/api/student/dashboard/', **self.headers).data
        self.assertIn('insights', dashboard)
        self.assertEqual(len(dashboard['insights']['studySessions']), 3)

    def test_dashboard_returns_expected_shape(self):
        response = self.client.get('/api/student/dashboard/', **self.headers)
        self.assertEqual(response.status_code, 200)
        data = response.data
        self.assertEqual(data['welcomeName'], 'Aarav Sharma')
        self.assertEqual(len(data['stats']), 4)
        self.assertEqual(len(data['academicSummary']), 5)
        self.assertIn('strengthAnalysis', data)
        self.assertIn('assignedGroup', data)
        self.assertIn('groupMembers', data)
        self.assertIn('notifications', data)
        self.assertEqual(data['overallPerformance'], round((88 + 55 + 92 + 78 + 72) / 5))


@override_settings(PASSWORD_HASHERS=FAST_HASHERS)
class AdminStudentManagementTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.headers = admin_headers(self.client)

    def test_admin_lists_students(self):
        self.client.post('/api/student/register/', STUDENT_PAYLOAD, format='json')
        response = self.client.get('/api/admin/students/', **self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        student = response.data[0]
        self.assertEqual(student['id'], 'STU-001')
        self.assertEqual(student['name'], 'Aarav Sharma')
        self.assertIn('Database', student['scores'])
        self.assertIn('strengths', student)
        self.assertIn('weaknesses', student)
        self.assertEqual(student['status'], 'Assigned')

    def test_admin_updates_student(self):
        self.client.post('/api/student/register/', STUDENT_PAYLOAD, format='json')
        response = self.client.put(
            '/api/admin/student/STU-001/',
            {
                'id': 'STU-001',
                'name': 'Aarav S',
                'department': 'Information Technology',
                'year': '3rd Year',
                'section': 'B',
                'scores': {'Mathematics': 95, 'Physics': 60, 'Programming': 80, 'Database': 85, 'Operating Systems': 70},
            },
            format='json',
            **self.headers,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], 'Aarav S')
        self.assertEqual(response.data['averageScore'], 78)

    def test_admin_delete_student(self):
        self.client.post('/api/student/register/', STUDENT_PAYLOAD, format='json')
        response = self.client.delete('/api/admin/student/STU-001/', **self.headers)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(self.client.get('/api/admin/students/', **self.headers).data, [])

    def test_admin_update_missing_student_is_404(self):
        response = self.client.put(
            '/api/admin/student/STU-999/',
            {'id': 'STU-999', 'name': 'X', 'scores': {'Mathematics': 50, 'Physics': 50, 'Programming': 50, 'Database': 50, 'Operating Systems': 50}},
            format='json',
            **self.headers,
        )
        self.assertEqual(response.status_code, 404)


@override_settings(PASSWORD_HASHERS=FAST_HASHERS)
class AdminStudentFilterTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.headers = admin_headers(self.client)
        self.client.post('/api/student/register/', STUDENT_PAYLOAD, format='json')
        self.client.post(
            '/api/student/register/',
            {
                **STUDENT_PAYLOAD,
                'studentId': 'STU-002',
                'email': 'meera@studysync.ai',
                'fullName': 'Meera Nair',
                'department': 'Information Technology',
            },
            format='json',
        )

    def test_search_by_name_and_id(self):
        response = self.client.get('/api/admin/students/?search=Meera', **self.headers)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], 'STU-002')

        response = self.client.get('/api/admin/students/?search=STU-001', **self.headers)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], 'STU-001')

    def test_filter_by_department(self):
        response = self.client.get('/api/admin/students/?department=Information%20Technology', **self.headers)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], 'STU-002')

    def test_filter_by_status(self):
        response = self.client.get('/api/admin/students/?status=assigned', **self.headers)
        self.assertEqual(len(response.data), 2)


@override_settings(PASSWORD_HASHERS=FAST_HASHERS)
class CsvImportTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.headers = admin_headers(self.client)

    def test_csv_import_stores_students_and_generates_groups(self):
        csv_text = (
            'Student ID,Name,Department,Year,Section,Mathematics,Physics,Programming,Database,Operating Systems\n'
            'CSV-001,Ali Khan,Computer Science,1st Year,A,85,60,90,70,65\n'
            'CSV-002,Sara Ali,Computer Science,1st Year,A,60,88,70,80,55\n'
            'CSV-003,John Doe,Information Technology,2nd Year,B,90,55,75,85,70\n'
            'CSV-004,Mia Chen,Information Technology,2nd Year,B,55,90,60,70,88\n'
            'CSV-005,Leo Park,AIML,3rd Year,C,70,70,95,60,60\n'
            'CSV-006,Nina Rao,AIML,3rd Year,C,60,60,70,95,70\n'
        )
        response = self.client.post(
            '/api/admin/import-csv/',
            {'file': io.BytesIO(csv_text.encode('utf-8'))},
            format='multipart',
            **self.headers,
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['added'], 6)
        self.assertEqual(response.data['skipped'], 0)
        self.assertGreater(response.data['summary']['groupsCreated'], 0)
        self.assertEqual(self.client.get('/api/admin/students/', **self.headers).status_code, 200)

    def test_csv_import_requires_file(self):
        response = self.client.post('/api/admin/import-csv/', {}, format='multipart', **self.headers)
        self.assertEqual(response.status_code, 400)

    def test_csv_import_rejects_invalid_headers(self):
        csv_text = 'Foo,Bar\n1,2\n'
        response = self.client.post(
            '/api/admin/import-csv/',
            {'file': io.BytesIO(csv_text.encode('utf-8'))},
            format='multipart',
            **self.headers,
        )
        self.assertEqual(response.status_code, 400)
