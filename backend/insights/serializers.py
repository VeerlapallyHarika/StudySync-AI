"""Serializers for the insights application."""
from rest_framework import serializers


class SettingsSerializer(serializers.Serializer):
    """Payload used to read/update system settings."""

    departments = serializers.ListField(child=serializers.CharField(), required=False)
    defaultGroupSize = serializers.IntegerField(min_value=2, max_value=8, required=False)
    kmeansRandomState = serializers.IntegerField(required=False)
    kmeansMaxIterations = serializers.IntegerField(min_value=50, max_value=5000, required=False)
    exportDefaultFormat = serializers.ChoiceField(choices=['csv', 'excel', 'pdf'], required=False)
    notifyGroupsGenerated = serializers.BooleanField(required=False)
    notifyCsvImported = serializers.BooleanField(required=False)


class ChangePasswordSerializer(serializers.Serializer):
    """Payload for a student's password change."""

    currentPassword = serializers.CharField()
    newPassword = serializers.CharField(min_length=6, max_length=128)
