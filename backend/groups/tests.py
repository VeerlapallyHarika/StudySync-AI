"""Tests for group generation, management and the admin dashboard."""
from django.conf import settings
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from groups.models import StudyGroup
from students.models import Student

FAST_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']

GROUP_SIZE = 5


def register(client, student_id: str, name: str, scores: dict, department='Computer Science'):
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
            'scores': scores,
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


def balanced_scores():
    return {'Mathematics': 70, 'Physics': 70, 'Programming': 70, 'Database': 70, 'Operating Systems': 70}


def varied_scores(index):
    """One standout subject and one weak subject per student so groups get
    non-empty strength/weakness summaries."""
    base = balanced_scores()
    subjects = ['Mathematics', 'Physics', 'Programming', 'Database', 'Operating Systems']
    strong = subjects[index % len(subjects)]
    weak = subjects[(index + 2) % len(subjects)]
    base[strong] = 92
    base[weak] = 45
    return base


@override_settings(PASSWORD_HASHERS=FAST_HASHERS)
class GroupGenerationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.headers = admin_headers(self.client)
        for index in range(10):
            register(
                self.client,
                f'GRP-{index + 1:03d}',
                f'Student {index + 1}',
                varied_scores(index),
            )

    def test_generate_forms_exactly_five_member_groups(self):
        response = self.client.post('/api/groups/generate/', {'group_size': 5}, format='json', **self.headers)
        self.assertEqual(response.status_code, 201)
        groups = response.data['groups']
        self.assertEqual(len(groups), 2)
        for group in groups:
            self.assertEqual(len(group['members']), GROUP_SIZE)
            self.assertIn('overallStrengths', group)
            self.assertIn('overallWeaknesses', group)
            self.assertIn('teamLeader', group)
            self.assertIn('learningRecommendation', group)
            self.assertIn('complementarySkillScore', group)
        self.assertEqual(Student.objects.filter(group__isnull=False).count(), 10)

    def test_generate_is_idempotent_and_never_reshuffles(self):
        first = self.client.post('/api/groups/generate/', {}, format='json', **self.headers)
        second = self.client.post('/api/groups/generate/', {}, format='json', **self.headers)
        self.assertEqual(len(first.data['groups']), 2)
        self.assertEqual(len(second.data['groups']), 2)
        self.assertEqual(
            {group['id'] for group in first.data['groups']},
            {group['id'] for group in second.data['groups']},
        )
        self.assertEqual(Student.objects.filter(group__isnull=False).count(), 10)

    def test_eleventh_student_starts_new_group(self):
        register(self.client, 'GRP-011', 'Student 11', varied_scores(1))
        response = self.client.post('/api/groups/generate/', {}, format='json', **self.headers)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(response.data['groups']), 3)
        self.assertEqual(Student.objects.filter(group__isnull=False).count(), 11)

    def test_generated_groups_include_recommendations(self):
        response = self.client.post('/api/groups/generate/', {'group_size': 5}, format='json', **self.headers)
        self.assertEqual(response.status_code, 201)
        for group in response.data['groups']:
            self.assertIn('recommendations', group)
            recommendations = group['recommendations']
            self.assertIn('overallSkillLevel', recommendations)
            self.assertIn('leaderReason', recommendations)
            self.assertIn('meetingRecommendation', recommendations)
        for member in response.data['groups'][0]['members']:
            self.assertIn('learningPreference', member)
            self.assertIn('availability', member)


@override_settings(PASSWORD_HASHERS=FAST_HASHERS)
class GroupManagementTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.headers = admin_headers(self.client)
        for index in range(10):
            register(self.client, f'MG-{index + 1:03d}', f'Member {index + 1}', balanced_scores())
        self.client.post('/api/groups/generate/', {}, format='json', **self.headers)

    def test_list_groups(self):
        response = self.client.get('/api/groups/', **self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

    def test_get_group(self):
        groups = self.client.get('/api/groups/', **self.headers).data
        response = self.client.get(f"/api/groups/{groups[0]['id']}/", **self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['id'], groups[0]['id'])

    def test_get_missing_group_is_404(self):
        response = self.client.get('/api/groups/99999/', **self.headers)
        self.assertEqual(response.status_code, 404)

    def test_update_group_renames(self):
        groups = self.client.get('/api/groups/', **self.headers).data
        response = self.client.put(
            f"/api/groups/{groups[0]['id']}/",
            {'name': 'Alpha Squad'},
            format='json',
            **self.headers,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], 'Alpha Squad')

    def test_delete_group_releases_students(self):
        groups = self.client.get('/api/groups/', **self.headers).data
        response = self.client.delete(f"/api/groups/{groups[0]['id']}/", **self.headers)
        self.assertEqual(response.status_code, 204)
        remaining = self.client.get('/api/groups/', **self.headers).data
        self.assertEqual(len(remaining), 1)
        self.assertEqual(Student.objects.filter(group__isnull=False).count(), GROUP_SIZE)

    def test_delete_all_groups(self):
        response = self.client.delete('/api/groups/delete-all/', **self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['deleted'], 2)
        self.assertEqual(self.client.get('/api/groups/', **self.headers).data, [])
        self.assertEqual(Student.objects.filter(group__isnull=False).count(), 0)


@override_settings(PASSWORD_HASHERS=FAST_HASHERS)
class GroupFilterTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.headers = admin_headers(self.client)
        for index in range(8):
            register(self.client, f'FLT-{index + 1:03d}', f'Filter {index + 1}', balanced_scores())
        self.client.post('/api/groups/generate/', {}, format='json', **self.headers)

    def test_search_groups_by_name(self):
        groups = self.client.get('/api/groups/', **self.headers).data
        name = groups[0]['name']
        response = self.client.get(f'/api/groups/?search={name}', **self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual([item['name'] for item in response.data], [name])

    def test_filter_groups_by_department(self):
        response = self.client.get('/api/groups/?department=Computer%20Science', **self.headers)
        self.assertEqual(response.status_code, 200)
        for group in response.data:
            departments = {member['department'] for member in group['members']}
            self.assertIn('Computer Science', departments)

    def test_filter_groups_by_min_performance(self):
        response = self.client.get('/api/groups/?minPerformance=60', **self.headers)
        self.assertEqual(response.status_code, 200)
        for group in response.data:
            self.assertGreaterEqual(group['averagePerformance'], 60)


@override_settings(PASSWORD_HASHERS=FAST_HASHERS)
class AdminDashboardTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.headers = admin_headers(self.client)

    def test_dashboard_shape(self):
        for index in range(6):
            register(self.client, f'DB-{index + 1:03d}', f'User {index + 1}', balanced_scores())
        self.client.post('/api/groups/generate/', {}, format='json', **self.headers)

        response = self.client.get('/api/admin/dashboard/', **self.headers)
        self.assertEqual(response.status_code, 200)
        data = response.data
        self.assertEqual(data['totalStudents'], 6)
        self.assertEqual(data['totalGroups'], 2)
        self.assertEqual(data['studentsAssigned'], 6)
        self.assertEqual(data['studentsWaiting'], 0)
        self.assertIn('departmentDistribution', data)
        self.assertIn('strengthDistribution', data)
        self.assertIn('weaknessDistribution', data)
        self.assertNotEqual(data['lastGroupGeneration'], 'Never')

    def test_dashboard_extra_metrics(self):
        for index in range(6):
            register(self.client, f'DB-{index + 1:03d}', f'User {index + 1}', balanced_scores())
        self.client.post('/api/groups/generate/', {}, format='json', **self.headers)

        response = self.client.get('/api/admin/dashboard/', **self.headers)
        data = response.data
        self.assertGreaterEqual(data['averageStudentScore'], 0)
        self.assertGreaterEqual(data['averageComplementaryScore'], 0)
        self.assertIn('mostActiveDepartment', data)
        self.assertIn('largestGroup', data)
        self.assertIn('smallestGroup', data)
        self.assertIn('recentActivities', data)
        self.assertIn('latestRegistrations', data)
        self.assertIn('studentsRequiringImprovement', data)
        self.assertTrue(any(item['action'] == 'group_generated' for item in data['recentActivities']))


@override_settings(PASSWORD_HASHERS=FAST_HASHERS)
class StudentGroupCollaborationTests(TestCase):
    """Tests for the student-facing group, chat and resource endpoints."""

    def setUp(self):
        self.client = APIClient()
        self.headers = admin_headers(self.client)
        for index in range(5):
            register(self.client, f'CLB-{index + 1:03d}', f'Collab {index + 1}', balanced_scores())

        login = self.client.post(
            '/api/student/login/',
            {'email': 'clb-001@studysync.ai', 'password': 'password123'},
            format='json',
        )
        self.student_headers = {'HTTP_AUTHORIZATION': f"Bearer {login.data['access']}"}

    def login_student(self, student_id):
        login = self.client.post(
            '/api/student/login/',
            {'email': f'{student_id.lower()}@studysync.ai', 'password': 'password123'},
            format='json',
        )
        return {'HTTP_AUTHORIZATION': f"Bearer {login.data['access']}"}

    def test_student_group_payload(self):
        response = self.client.get('/api/student/groups/', **self.student_headers)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['assigned'])
        group = response.data['group']
        self.assertIsNotNone(group)
        self.assertEqual(len(group['members']), GROUP_SIZE)
        self.assertIn('chat', group)
        self.assertIn('resources', group)
        self.assertIn('activity', group)
        self.assertTrue(any(member['isSelf'] for member in group['members']))

    def test_student_without_group_returns_waiting_status(self):
        # Student created directly with missing scores / unassigned
        loner = Student.objects.create(
            student_id='CLB-900',
            full_name='Loner',
            email='clb-900@studysync.ai',
            password='password123',
        )
        loner.set_password('password123')
        loner.save()
        headers = self.login_student('CLB-900')
        response = self.client.get('/api/student/groups/', **headers)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.data['assigned'])
        self.assertIsNone(response.data['group'])

    def test_send_and_list_chat_messages(self):
        response = self.client.post(
            '/api/student/groups/chat/',
            {'message': 'Check this Python tutorial'},
            format='json',
            **self.student_headers,
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.data['isSelf'])
        self.assertEqual(response.data['sender'], 'Collab 1')

        listed = self.client.get('/api/student/groups/chat/', **self.student_headers)
        self.assertEqual(listed.status_code, 200)
        self.assertEqual(len(listed.data['chat']), 1)

    def test_chat_rejects_empty_message(self):
        response = self.client.post(
            '/api/student/groups/chat/',
            {'message': '   '},
            format='json',
            **self.student_headers,
        )
        self.assertEqual(response.status_code, 400)

    def test_share_and_list_resources(self):
        response = self.client.post(
            '/api/student/groups/resources/',
            {'title': 'Python Notes', 'resourceType': 'Study Notes', 'url': 'https://example.com/notes'},
            format='json',
            **self.student_headers,
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['title'], 'Python Notes')

        listed = self.client.get('/api/student/resources/', **self.student_headers)
        self.assertEqual(listed.status_code, 200)
        self.assertEqual(len(listed.data['resources']), 1)

    def test_resource_requires_url_or_file(self):
        response = self.client.post(
            '/api/student/groups/resources/',
            {'title': 'Broken', 'resourceType': 'Other'},
            format='json',
            **self.student_headers,
        )
        self.assertEqual(response.status_code, 400)

    def test_chat_creates_notification_for_other_members(self):
        self.client.post(
            '/api/student/groups/chat/',
            {'message': 'Anyone free to study?'},
            format='json',
            **self.student_headers,
        )
        headers = self.login_student('CLB-002')
        response = self.client.get('/api/notifications/', **headers)
        self.assertEqual(response.status_code, 200)
        titles = [item['title'] for item in response.data['notifications']]
        self.assertIn('New Message in Your Study Group', titles)


@override_settings(PASSWORD_HASHERS=FAST_HASHERS)
class StudentGroupAutoFormationTests(TestCase):
    """The user-facing acceptance flow for automatic 5-member groups."""

    def setUp(self):
        self.client = APIClient()
        self.headers = admin_headers(self.client)

    def register_n(self, prefix: str, count: int, index_offset: int = 0):
        for index in range(index_offset, index_offset + count):
            register(self.client, f'{prefix}-{index + 1:03d}', f'{prefix} {index + 1}', varied_scores(index))

    def login_student(self, student_id):
        login = self.client.post(
            '/api/student/login/',
            {'email': f'{student_id.lower()}@studysync.ai', 'password': 'password123'},
            format='json',
        )
        return {'HTTP_AUTHORIZATION': f"Bearer {login.data['access']}"}

    def test_three_students_form_group_of_three(self):
        self.register_n('GATE', 3)
        headers = self.login_student('GATE-001')

        status = self.client.get('/api/student/groups/status/', **headers).data['status']
        self.assertTrue(status['profileComplete'])
        self.assertEqual(status['eligibleStudents'], 3)
        self.assertEqual(status['minimumRequired'], 1)
        self.assertTrue(status['groupsGenerated'])
        self.assertIsNotNone(status['group'])
        self.assertEqual(len(status['group']['members']), 3)

        group_response = self.client.get('/api/student/groups/', **headers)
        self.assertTrue(group_response.data['assigned'])
        self.assertIsNotNone(group_response.data['group'])
        self.assertEqual(len(group_response.data['group']['members']), 3)

    def test_fifth_registration_completes_group(self):
        self.register_n('FRM', 4)
        headers = self.login_student('FRM-001')
        before = self.client.get('/api/student/groups/status/', **headers).data['status']
        self.assertTrue(before['groupsGenerated'])
        self.assertEqual(len(before['group']['members']), 4)

        self.register_n('FRM', 1, index_offset=4)
        after = self.client.get('/api/student/groups/status/', **headers).data['status']
        self.assertTrue(after['groupsGenerated'])
        self.assertIsNotNone(after['group'])
        self.assertEqual(len(after['group']['members']), GROUP_SIZE)

    def test_all_five_members_share_the_same_group(self):
        self.register_n('SHARE', 5)
        group_ids = set()
        for index in range(1, 6):
            headers = self.login_student(f'SHARE-{index:03d}')
            group = self.client.get('/api/student/groups/', **headers).data['group']
            self.assertIsNotNone(group)
            self.assertEqual(len(group['members']), GROUP_SIZE)
            group_ids.add(group['id'])
        self.assertEqual(len(group_ids), 1)

    def test_sixth_student_starts_new_group(self):
        self.register_n('SIX', 6)
        self.assertEqual(Student.objects.filter(group__isnull=False).count(), 6)
        self.assertEqual(StudyGroup.objects.count(), 2)

        sixth = Student.objects.get(student_id='SIX-006')
        self.assertIsNotNone(sixth.group)
        self.assertEqual(len(sixth.group.members), 1)

        headers = self.login_student('SIX-006')
        response = self.client.get('/api/student/groups/', **headers)
        self.assertTrue(response.data['assigned'])
        self.assertEqual(response.data['group']['name'], sixth.group.name)

    def test_ten_students_form_two_groups(self):
        self.register_n('TEN', 10)
        groups = self.client.get('/api/groups/', **self.headers).data
        self.assertEqual(len(groups), 2)
        for group in groups:
            self.assertEqual(len(group['members']), GROUP_SIZE)
        self.assertEqual(Student.objects.filter(group__isnull=False).count(), 10)

    def test_group_two_grows_to_five(self):
        self.register_n('NEXT', 6)
        sixth = Student.objects.get(student_id='NEXT-006')
        self.assertEqual(len(sixth.group.members), 1)

        self.register_n('NEXT', 4, index_offset=6)
        sixth.refresh_from_db()
        self.assertEqual(len(sixth.group.members), 5)
        self.assertEqual(Student.objects.filter(group__isnull=False).count(), 10)
        self.assertEqual(StudyGroup.objects.count(), 2)

    def test_generate_is_idempotent_for_assigned_students(self):
        self.register_n('IDEM', 5)
        headers = self.login_student('IDEM-001')
        response = self.client.post('/api/student/groups/generate/', {}, format='json', **headers)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.data['generated'])
        self.assertTrue(response.data['assigned'])
        self.assertIsNotNone(response.data['group'])

    def test_weakness_coverage_matches_group_weaknesses(self):
        self.register_n('COV', 5)
        headers = self.login_student('COV-001')
        group = self.client.get('/api/student/groups/', **headers).data['group']
        coverage = group['weaknessCoverage']
        self.assertGreaterEqual(len(coverage), 1)
        self.assertEqual([item['subject'] for item in coverage], group['overallWeaknesses'])
        member_names = {member['name'] for member in group['members']}
        for item in coverage:
            self.assertIn('covered', item)
            self.assertEqual(bool(item['coveredBy']), item['covered'])
            self.assertTrue(set(item['coveredBy']) <= member_names)

    def test_chat_is_isolated_between_groups(self):
        self.register_n('ISO', 10)
        groups = self.client.get('/api/groups/', **self.headers).data
        self.assertEqual(len(groups), 2)
        group_a_id = groups[0]['id']
        group_b_id = groups[1]['id']
        a_headers = self.login_student(groups[0]['members'][0]['studentId'])
        b_headers = self.login_student(groups[1]['members'][0]['studentId'])

        self.assertNotEqual(self.client.get('/api/student/groups/', **a_headers).data['group']['id'], group_b_id)
        self.assertNotEqual(self.client.get('/api/student/groups/', **b_headers).data['group']['id'], group_a_id)

        self.client.post(
            '/api/student/groups/chat/',
            {'message': 'Hello Group A'},
            format='json',
            **a_headers,
        )
        self.assertEqual(self.client.get('/api/student/groups/chat/', **b_headers).data['chat'], [])

        self.client.post(
            '/api/student/groups/chat/',
            {'message': 'Hello Group B'},
            format='json',
            **b_headers,
        )
        a_chat = self.client.get('/api/student/groups/chat/', **a_headers).data['chat']
        b_chat = self.client.get('/api/student/groups/chat/', **b_headers).data['chat']
        self.assertEqual([message['message'] for message in a_chat], ['Hello Group A'])
        self.assertEqual([message['message'] for message in b_chat], ['Hello Group B'])

    def test_unassigned_student_cannot_chat(self):
        loner = Student.objects.create(
            student_id='WT-001',
            full_name='Loner',
            email='wt-001@studysync.ai',
        )
        loner.set_password('password123')
        loner.save()
        headers = self.login_student('WT-001')

        response = self.client.post(
            '/api/student/groups/chat/',
            {'message': 'hello'},
            format='json',
            **headers,
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('no_group', response.data['error'])

        listed = self.client.get('/api/student/groups/chat/', **headers)
        self.assertEqual(listed.data['chat'], [])

    def test_status_requires_student_auth(self):
        response = self.client.get('/api/student/groups/status/')
        self.assertEqual(response.status_code, 401)

    def test_generate_requires_student_auth(self):
        response = self.client.post('/api/student/groups/generate/', {}, format='json')
        self.assertEqual(response.status_code, 401)
