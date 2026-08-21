"""API views for the students application."""
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from authentication.permissions import IsAdmin, IsStudent
from authentication.serializers import LoginSerializer, LogoutSerializer, RefreshSerializer
from students import services
from students.repositories import StudentRepository
from students.serializers import AdminStudentWriteSerializer, StudentRegistrationSerializer
from utils.logging import get_logger
from utils.throttles import LoginRateThrottle

logger = get_logger('students')


class StudentRegisterView(APIView):
    """POST /api/student/register/ — create a student account."""

    permission_classes = [AllowAny]
    throttle_classes = [LoginRateThrottle]

    def post(self, request):
        serializer = StudentRegistrationSerializer(
            data=request.data,
            context={'purpose': 'registration'},
        )
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        password = data.pop('password', None) or None
        data.pop('confirmPassword', None)
        result = services.register_student(data, password=password)
        return Response(result, status=status.HTTP_201_CREATED)


class StudentLoginView(APIView):
    """POST /api/student/login/ — authenticate a student."""

    permission_classes = [AllowAny]
    throttle_classes = [LoginRateThrottle]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = services.login_student(**serializer.validated_data)
        return Response(result, status=status.HTTP_200_OK)


class StudentRefreshView(APIView):
    """POST /api/student/refresh/ — renew a student access token."""

    permission_classes = [AllowAny]
    throttle_classes = [LoginRateThrottle]

    def post(self, request):
        serializer = RefreshSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(services.student_refresh(serializer.validated_data['refresh']))


class StudentLogoutView(APIView):
    """POST /api/student/logout/ — revoke the student refresh token."""

    permission_classes = [AllowAny]
    throttle_classes = [LoginRateThrottle]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        services.student_logout(serializer.validated_data['refresh'])
        return Response({'detail': 'Logged out successfully.'})


class StudentProfileView(APIView):
    """GET/PUT /api/student/profile/ — read and update the current profile."""

    permission_classes = [IsStudent]

    def get(self, request):
        return Response(services.get_profile(request.principal.student))

    def put(self, request):
        serializer = StudentRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        profile = services.update_profile(request.principal.student, serializer.validated_data)
        return Response(profile)


class StudentDashboardView(APIView):
    """GET /api/student/dashboard/ — aggregated dashboard payload."""

    permission_classes = [IsStudent]

    def get(self, request):
        return Response(services.build_dashboard(request.principal.student))


class AdminStudentListView(APIView):
    """GET /api/admin/students/ — list every student for the admin panel."""

    permission_classes = [IsAdmin]

    def get(self, request):
        return Response(services.list_students(request.query_params))


class AdminStudentDetailView(APIView):
    """PUT/DELETE /api/admin/student/<student_id>/ — update or remove a student."""

    permission_classes = [IsAdmin]

    def _resolve(self, student_id: str):
        student = StudentRepository.get_by_student_id(student_id)
        if student is None:
            return None
        return student

    def put(self, request, student_id):
        student = self._resolve(student_id)
        if student is None:
            return Response(
                {'error': 'not_found', 'message': 'Student not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = AdminStudentWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(services.update_student_admin(student, serializer.validated_data))

    def delete(self, request, student_id):
        student = self._resolve(student_id)
        if student is None:
            return Response(
                {'error': 'not_found', 'message': 'Student not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        services.delete_student(student)
        return Response(status=status.HTTP_204_NO_CONTENT)


class AdminImportCsvView(APIView):
    """POST /api/admin/import-csv/ — upload a CSV of students.

    The file is validated, stored, analysed and groups are generated.
    """

    permission_classes = [IsAdmin]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        uploaded = request.FILES.get('file')
        if uploaded is None:
            return Response(
                {'error': 'validation_error', 'message': 'A CSV file is required (field name: file).'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        result = services.import_students_csv(uploaded)
        return Response(result, status=status.HTTP_201_CREATED)
