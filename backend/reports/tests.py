"""Tests for report generation and CSV/Excel/PDF exports."""
from django.conf import settings
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

FAST_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']


def register(client, student_id: str, name: str, department='Computer Science'):
    return client.post(
        '/api/student/register/',
        {
            'fullName': name,
            'studentId': student_id,
            'email': f'{student_id.lower()}@studysync.ai',
            'department': department,
            'year': '2nd Year',
            'section': 'A',
            'availability': 'Morning',
            'learningPreference': 'Mixed',
            'password': 'password123',
            'confirmPassword': 'password123',
            'scores': {
                'Mathematics': 80,
                'Physics': 60,
                'Programming': 90,
                'Database Management': 70,
                'Operating Systems': 65,
            },
        },
        format='json',
    )


def admin_headers(client):
    response = client.post(
        '/api/admin/login/',
        {'email': settings.ADMIN_EMAIL, 'password': settings.ADMIN_PASSWORD},
        format='json',
    )
    return {'HTTP_AUTHORIZATION': f"Bearer {response.data['access']}"}


@override_settings(PASSWORD_HASHERS=FAST_HASHERS)
class ReportTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.headers = admin_headers(self.client)
        register(self.client, 'RP-001', 'Ravi Kumar', 'Computer Science')
        register(self.client, 'RP-002', 'Ananya Iyer', 'Information Technology')
        register(self.client, 'RP-003', 'Tom Berry', 'AIML')
        register(self.client, 'RP-004', 'Dina Park', 'Computer Science')
        register(self.client, 'RP-005', 'Omar Sheikh', 'Electronics')
        self.client.post('/api/groups/generate/', {}, format='json', **self.headers)

    def test_generate_report_returns_report_data(self):
        response = self.client.post('/api/reports/', {}, format='json', **self.headers)
        self.assertEqual(response.status_code, 201)
        data = response.data
        self.assertEqual(data['title'], 'StudySync AI Institutional Report')
        self.assertEqual(data['totalStudents'], 5)
        self.assertGreater(data['totalGroups'], 0)
        self.assertEqual(len(data['sections']), 7)
        keys = [section['key'] for section in data['sections']]
        self.assertEqual(
            keys,
            [
                'group_composition',
                'student_analysis',
                'department_analysis',
                'strength_analysis',
                'weakness_analysis',
                'group_performance',
                'analytics_summary',
            ],
        )

    def test_list_reports(self):
        self.client.post('/api/reports/', {}, format='json', **self.headers)
        response = self.client.get('/api/reports/', **self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_list_reports_filters_by_department(self):
        self.client.post('/api/reports/', {}, format='json', **self.headers)
        response = self.client.get('/api/reports/?department=Computer%20Science', **self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

        response = self.client.get('/api/reports/?department=History', **self.headers)
        self.assertEqual(len(response.data), 0)

    def test_list_reports_filters_by_group(self):
        groups = self.client.get('/api/groups/', **self.headers).data
        self.client.post('/api/reports/', {}, format='json', **self.headers)
        response = self.client.get(f"/api/reports/?group={groups[0]['name']}", **self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_export_csv_logs_activity(self):
        self.client.post('/api/reports/csv/', {}, format='json', **self.headers)
        activities = self.client.get('/api/admin/activities/', **self.headers).data['activities']
        self.assertIn('report_exported', [item['action'] for item in activities])

    def test_export_csv(self):
        response = self.client.post('/api/reports/csv/', {}, format='json', **self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        body = response.content.decode('utf-8-sig')
        self.assertIn('Student ID', body)
        self.assertIn('RP-001', body)
        self.assertIn('Mathematics', body)

    def test_export_excel(self):
        response = self.client.post('/api/reports/excel/', {}, format='json', **self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn('spreadsheetml', response['Content-Type'])
        self.assertGreater(len(response.content), 1000)

    def test_export_pdf(self):
        response = self.client.post('/api/reports/pdf/', {}, format='json', **self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertTrue(response.content.startswith(b'%PDF'))

    def test_export_unsupported_format(self):
        response = self.client.post('/api/reports/unknown/', {}, format='json', **self.headers)
        self.assertEqual(response.status_code, 400)
