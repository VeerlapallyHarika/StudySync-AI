"""API views for analytics, settings, system info and student insights."""
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from authentication.permissions import IsAdmin, IsStudent
from insights import services
from insights.serializers import ChangePasswordSerializer, SettingsSerializer
from utils.logging import get_logger

logger = get_logger('insights')


class AdminAnalyticsView(APIView):
    """GET /api/admin/analytics/ — comprehensive performance analytics."""

    permission_classes = [IsAdmin]

    def get(self, request):
        return Response(services.build_analytics())


class AdminSettingsView(APIView):
    """GET/PUT /api/admin/settings/ — read and update system settings."""

    permission_classes = [IsAdmin]

    def get(self, request):
        return Response(services.get_settings_payload())

    def put(self, request):
        serializer = SettingsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(services.update_settings(serializer.validated_data))


class AdminSystemInfoView(APIView):
    """GET /api/admin/system-info/ — deployment and version details."""

    permission_classes = [IsAdmin]

    def get(self, request):
        return Response(services.system_info())


class StudentInsightsView(APIView):
    """GET /api/student/insights/ — AI insights for the current student."""

    permission_classes = [IsStudent]

    def get(self, request):
        return Response(services.student_insights(request.principal.student))


class StudentChangePasswordView(APIView):
    """POST /api/student/change-password/ — update the student's password."""

    permission_classes = [IsStudent]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        services.change_password(
            request.principal.student,
            serializer.validated_data['currentPassword'],
            serializer.validated_data['newPassword'],
        )
        return Response({'detail': 'Password updated successfully.'}, status=status.HTTP_200_OK)
