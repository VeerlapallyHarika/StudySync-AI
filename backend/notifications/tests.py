"""Tests for notifications and activity logging."""
from django.conf import settings
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

FAST_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']

STUDENT_PAYLOAD = {
    'fullName': 'Notify User',
    'studentId': 'NOT-001',
    'email': 'notify@studysync.ai',
    'department': 'Computer Science',
    'year': '2nd Year',
    'section': 'A',
    'availability': 'Morning',
    'learningPreference': 'Mixed',
    'password': 'password123',
    'confirmPassword': 'password123',
    'scores': {
        'Mathematics': 70,
        'Physics': 70,
        'Programming': 70,
        'Database Management': 70,
        'Operating Systems': 70,
    },
}


def register(client, payload=None):
    return client.post('/api/student/register/', payload or STUDENT_PAYLOAD, format='json')


def admin_headers(client):
    response = client.post(
        '/api/admin/login/',
        {'email': settings.ADMIN_EMAIL, 'password': settings.ADMIN_PASSWORD},
        format='json',
    )
    return {'HTTP_AUTHORIZATION': f"Bearer {response.data['access']}"}


def register_student_and_headers(client, payload=None):
    payload = payload or STUDENT_PAYLOAD
    client.post('/api/student/register/', payload, format='json')
    login = client.post(
        '/api/student/login/',
        {'email': payload['email'], 'password': payload['password']},
        format='json',
    )
    return {'HTTP_AUTHORIZATION': f"Bearer {login.data['access']}"}


def student_payload(student_id: str, email: str) -> dict:
    return {**STUDENT_PAYLOAD, 'studentId': student_id, 'email': email}


def register_cohort(client, prefix: str, count: int = 6):
    for index in range(count):
        payload = {**STUDENT_PAYLOAD, 'studentId': f'{prefix}-{index + 1:03d}', 'email': f'{prefix.lower()}{index}@studysync.ai'}
        client.post('/api/student/register/', payload, format='json')


@override_settings(PASSWORD_HASHERS=FAST_HASHERS)
class NotificationTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_group_generation_creates_admin_and_student_notifications(self):
        register_cohort(self.client, 'NOT')
        headers = admin_headers(self.client)
        self.client.post('/api/groups/generate/', {}, format='json', **headers)

        admin_list = self.client.get('/api/notifications/', **headers)
        self.assertEqual(admin_list.status_code, 200)
        self.assertGreaterEqual(len(admin_list.data['notifications']), 1)
        self.assertIn('groups', [item['category'] for item in admin_list.data['notifications']])

    def test_student_can_mark_and_read_notifications(self):
        register_cohort(self.client, 'NOT', count=4)
        s_headers = register_student_and_headers(self.client, student_payload('MYSELF-001', 'myself@studysync.ai'))
        headers = admin_headers(self.client)
        self.client.post('/api/groups/generate/', {}, format='json', **headers)

        response = self.client.get('/api/notifications/', **s_headers)
        self.assertEqual(response.status_code, 200)
        notifications = response.data['notifications']
        self.assertGreaterEqual(len(notifications), 1)
        unread = [item for item in notifications if not item['read']]
        self.assertTrue(unread)

        notification_id = notifications[0]['id']
        read = self.client.post(f'/api/notifications/{notification_id}/read/', **s_headers)
        self.assertEqual(read.status_code, 200)

        refreshed = self.client.get('/api/notifications/', **s_headers).data['notifications']
        target = next(item for item in refreshed if item['id'] == notification_id)
        self.assertTrue(target['read'])

    def test_mark_all_read(self):
        register_cohort(self.client, 'NOT', count=4)
        s_headers = register_student_and_headers(self.client, student_payload('MYSELF-001', 'myself@studysync.ai'))
        headers = admin_headers(self.client)
        self.client.post('/api/groups/generate/', {}, format='json', **headers)

        response = self.client.post('/api/notifications/read-all/', **s_headers)
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(response.data['marked'], 1)
        refreshed = self.client.get('/api/notifications/', **s_headers).data['notifications']
        self.assertTrue(all(item['read'] for item in refreshed))

    def test_clear_notifications(self):
        register_cohort(self.client, 'NOT', count=4)
        s_headers = register_student_and_headers(self.client, student_payload('MYSELF-001', 'myself@studysync.ai'))
        headers = admin_headers(self.client)
        self.client.post('/api/groups/generate/', {}, format='json', **headers)

        response = self.client.delete('/api/notifications/', **s_headers)
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(response.data['deleted'], 1)
        refreshed = self.client.get('/api/notifications/', **s_headers).data['notifications']
        self.assertEqual(refreshed, [])


@override_settings(PASSWORD_HASHERS=FAST_HASHERS)
class ActivityTests(TestCase):
    def test_recent_activities_after_generation_and_export(self):
        self.client = APIClient()
        for index in range(6):
            payload = {**STUDENT_PAYLOAD, 'studentId': f'ACT-{index + 1:03d}', 'email': f'act{index}@studysync.ai'}
            self.client.post('/api/student/register/', payload, format='json')
        headers = admin_headers(self.client)
        self.client.post('/api/groups/generate/', {}, format='json', **headers)
        self.client.post('/api/reports/csv/', {}, format='json', **headers)

        response = self.client.get('/api/admin/activities/', **headers)
        self.assertEqual(response.status_code, 200)
        actions = [item['action'] for item in response.data['activities']]
        self.assertIn('group_generated', actions)
        self.assertIn('report_exported', actions)
