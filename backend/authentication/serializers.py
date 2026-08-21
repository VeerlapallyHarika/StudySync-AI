"""DRF serializers for the authentication endpoints."""
from rest_framework import serializers


class LoginSerializer(serializers.Serializer):
    """Shared email/password login payload."""

    email = serializers.EmailField()
    password = serializers.CharField(trim_whitespace=False)


class RefreshSerializer(serializers.Serializer):
    """Refresh-token payload for access-token renewal."""

    refresh = serializers.CharField()


class LogoutSerializer(serializers.Serializer):
    """Refresh-token payload for logout/revocation."""

    refresh = serializers.CharField()


class TokenPairSerializer(serializers.Serializer):
    """Serialized JWT token pair returned on successful authentication."""

    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)
    email = serializers.EmailField(read_only=True)
