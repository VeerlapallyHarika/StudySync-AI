"""Authentication API views."""
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from authentication.serializers import LoginSerializer, LogoutSerializer, RefreshSerializer
from authentication.services import admin_login, admin_logout, admin_refresh
from utils.logging import get_logger
from utils.throttles import LoginRateThrottle

logger = get_logger('authentication')


class AdminLoginView(APIView):
    """POST /api/admin/login/ — authenticate an administrator."""

    permission_classes = [AllowAny]
    throttle_classes = [LoginRateThrottle]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tokens = admin_login(**serializer.validated_data)
        return Response(tokens, status=status.HTTP_200_OK)


class AdminRefreshView(APIView):
    """POST /api/admin/refresh/ — renew an admin access token."""

    permission_classes = [AllowAny]
    throttle_classes = [LoginRateThrottle]

    def post(self, request):
        serializer = RefreshSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payload = admin_refresh(serializer.validated_data['refresh'])
        return Response(payload, status=status.HTTP_200_OK)


class AdminLogoutView(APIView):
    """POST /api/admin/logout/ — revoke the admin refresh token."""

    permission_classes = [AllowAny]
    throttle_classes = [LoginRateThrottle]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        admin_logout(serializer.validated_data['refresh'])
        return Response({'detail': 'Logged out successfully.'}, status=status.HTTP_200_OK)
