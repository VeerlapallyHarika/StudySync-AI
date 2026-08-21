"""API views for the groups application and the admin dashboard."""
from rest_framework import exceptions, status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from authentication.permissions import HasPrincipal, IsAdmin, IsStudent
from groups import services
from groups.serializers import (
    ChatMessageSerializer,
    GroupGenerateSerializer,
    GroupUpdateSerializer,
    ResourceShareSerializer,
)
from insights.services import students_requiring_improvement
from notifications import services as notification_services
from students.repositories import StudentRepository
from utils.logging import get_logger

logger = get_logger('groups')


class AdminDashboardView(APIView):
    """GET /api/admin/dashboard/ — aggregate metrics for the admin landing page."""

    permission_classes = [IsAdmin]

    def get(self, request):
        students = StudentRepository.all()
        groups = services.list_groups()

        assigned_count = sum(1 for student in students if student.group_id is not None)

        department_distribution: dict[str, int] = {}
        strength_distribution: dict[str, int] = {}
        weakness_distribution: dict[str, int] = {}
        for student in students:
            department_distribution[student.department] = department_distribution.get(student.department, 0) + 1
            for subject in (student.strengths or []):
                strength_distribution[subject] = strength_distribution.get(subject, 0) + 1
            for subject in (student.weaknesses or []):
                weakness_distribution[subject] = weakness_distribution.get(subject, 0) + 1

        if groups:
            last_generation = max(group['createdAt'] for group in groups)
        else:
            last_generation = 'Never'

        total_members = sum(len(group['members']) for group in groups)
        average_group_size = round(total_members / len(groups), 1) if groups else 0

        most_active_department = max(department_distribution, key=department_distribution.get) if department_distribution else None
        largest_group = max(groups, key=lambda group: len(group['members'])) if groups else None
        smallest_group = min(groups, key=lambda group: len(group['members'])) if groups else None

        average_student_score = round(sum(student.average_score for student in students) / len(students)) if students else 0
        average_complementary = (
            round(sum(group['complementarySkillScore'] for group in groups) / len(groups)) if groups else 0
        )

        recent_activities = notification_services.recent_activities(limit=8)
        latest_registrations = [
            {
                'studentId': student.student_id,
                'name': student.full_name,
                'department': student.department,
                'registeredAt': student.created_at.isoformat() if student.created_at else None,
            }
            for student in sorted(students, key=lambda item: item.created_at, reverse=True)[:5]
        ]

        return Response({
            'totalStudents': len(students),
            'totalGroups': len(groups),
            'studentsAssigned': assigned_count,
            'studentsWaiting': len(students) - assigned_count,
            'averageGroupSize': average_group_size,
            'lastGroupGeneration': last_generation,
            'departmentDistribution': department_distribution,
            'strengthDistribution': strength_distribution,
            'weaknessDistribution': weakness_distribution,
            'averageStudentScore': average_student_score,
            'averageComplementaryScore': average_complementary,
            'mostActiveDepartment': most_active_department,
            'largestGroup': largest_group['name'] if largest_group else None,
            'smallestGroup': smallest_group['name'] if smallest_group else None,
            'recentActivities': recent_activities,
            'latestRegistrations': latest_registrations,
            'studentsRequiringImprovement': students_requiring_improvement(limit=5),
        })


class GenerateGroupsView(APIView):
    """POST /api/groups/generate/ — run the ML grouping pipeline.

    Open to any authenticated principal (admin or student); no admin login is
    required. It fetches every registered student, clusters them, persists the
    assignments and returns the generated groups.
    """

    permission_classes = [HasPrincipal]

    def post(self, request):
        serializer = GroupGenerateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        groups, summary = services.generate_groups(serializer.validated_data['group_size'])
        return Response({'groups': groups, 'summary': summary}, status=status.HTTP_201_CREATED)


class GroupListView(APIView):
    """GET /api/groups/ — list all study groups."""

    permission_classes = [IsAdmin]

    def get(self, request):
        return Response(services.list_groups(request.query_params))


class GroupDetailView(APIView):
    """GET/PUT/DELETE /api/groups/<id>/ — manage a single study group."""

    permission_classes = [IsAdmin]

    def get(self, request, group_id):
        group = services.get_group(group_id)
        if group is None:
            return Response(
                {'error': 'not_found', 'message': 'Group not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(group)

    def put(self, request, group_id):
        serializer = GroupUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        group = services.update_group(group_id, serializer.validated_data)
        if group is None:
            return Response(
                {'error': 'not_found', 'message': 'Group not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(group)

    def delete(self, request, group_id):
        if not services.delete_group(group_id):
            return Response(
                {'error': 'not_found', 'message': 'Group not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


class DeleteAllGroupsView(APIView):
    """DELETE /api/groups/delete-all/ — remove every group and release students."""

    permission_classes = [IsAdmin]

    def delete(self, request):
        count = services.delete_all_groups()
        return Response({'deleted': count}, status=status.HTTP_200_OK)


class StudentGroupView(APIView):
    """GET /api/student/groups/ — the current student's group with chat + resources.

    Fetches the persisted assignment — does NOT trigger the ML pipeline on read.
    Returns a meaningful status when the student is not yet assigned.
    """

    permission_classes = [IsStudent]

    def get(self, request):
        student = request.principal.student
        # Always read the latest DB state; never regenerate on a plain GET.
        student.refresh_from_db()
        group = services.student_group(student, request=request)
        if group is not None:
            return Response({'group': group, 'assigned': True})
        return Response({
            'group': None,
            'assigned': False,
            'message': services._waiting_message(student, 0),
        })


class StudentGroupStatusView(APIView):
    """GET /api/student/groups/status/ — readiness for the group-formation states.

    Conditionally runs the ML pipeline: only when there are ≥5 unassigned
    eligible students. Plain status reads (page loads, refreshes) do NOT
    trigger K-Means clustering.
    """

    permission_classes = [IsStudent]

    def get(self, request):
        student = request.principal.student
        student.refresh_from_db()
        return Response({'status': services.group_status(student)})


class StudentGenerateGroupsView(APIView):
    """POST /api/student/groups/generate/ — form groups for the whole cohort.

    Runs the ML pipeline when the requesting student is unassigned (and enough
    students exist), assigning every registered student. Otherwise returns the
    student's existing assignment.
    """

    permission_classes = [IsStudent]

    def post(self, request):
        try:
            result = services.generate_for_student(request.principal.student)
        except exceptions.ValidationError as exc:
            return Response(
                {'error': 'generation_blocked', 'message': str(exc.detail)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        payload = {
            'generated': result['generated'],
            'assigned': result['assigned'],
            'group': result['group'],
            'status': services.group_status(request.principal.student),
        }
        if result.get('message'):
            payload['message'] = result['message']
        return Response(
            payload,
            status=status.HTTP_201_CREATED if result['generated'] else status.HTTP_200_OK,
        )


class StudentGroupChatView(APIView):
    """GET/POST /api/student/groups/chat/ — read or post group chat messages."""

    permission_classes = [IsStudent]

    def get(self, request):
        group = services.student_group(request.principal.student, request=request)
        return Response({'chat': (group or {}).get('chat', [])})

    def post(self, request):
        serializer = ChatMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        message = services.send_chat_message(
            request.principal.student,
            serializer.validated_data['message'],
        )
        if message is None:
            return Response(
                {'error': 'no_group', 'message': 'You have not been assigned to a study group yet.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(message, status=status.HTTP_201_CREATED)


class StudentGroupResourcesView(APIView):
    """GET/POST /api/student/groups/resources/ — group-shared study resources."""

    permission_classes = [IsStudent]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get(self, request):
        return Response({'resources': services.list_group_resources(request.principal.student, request=request)})

    def post(self, request):
        serializer = ResourceShareSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        resource = services.share_group_resource(
            request.principal.student,
            serializer.validated_data,
            request=request,
        )
        if resource is None:
            return Response(
                {'error': 'no_group', 'message': 'You have not been assigned to a study group yet.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(resource, status=status.HTTP_201_CREATED)


class StudentResourcesView(APIView):
    """GET /api/student/resources/ — every resource shared with the student's group."""

    permission_classes = [IsStudent]

    def get(self, request):
        return Response({'resources': services.list_group_resources(request.principal.student, request=request)})


class MyGroupView(APIView):
    """GET /api/groups/my-group/ — spec-compliant Task 4 endpoint.

    Identifies the authenticated student from the JWT and returns their group.
    Never uses hardcoded IDs, URL parameters, or localStorage as identity.
    """

    permission_classes = [IsStudent]

    def get(self, request):
        student = request.principal.student
        student.refresh_from_db()
        return Response(services.my_group(student, request=request))
