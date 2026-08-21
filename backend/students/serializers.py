"""Serializers for the students application.

Input validation mirrors the exact camelCase payloads sent by the React
frontend (``src/services/studentService.ts`` and ``src/services/adminService.ts``).
"""
from __future__ import annotations

from rest_framework import serializers

# Maps frontend subject keys (student-facing) onto the ML pipeline keys.
STUDENT_TO_ML_SUBJECTS = {
    'Mathematics': 'Mathematics',
    'Physics': 'Physics',
    'Programming': 'Programming',
    'Database Management': 'Database',
    'Operating Systems': 'Operating Systems',
}


def _scores_to_ml(value):
    return {
        STUDENT_TO_ML_SUBJECTS.get(subject, subject): score
        for subject, score in value.items()
    }


class StudentRegistrationSerializer(serializers.Serializer):
    """Payload used for student registration and profile updates."""

    fullName = serializers.CharField(max_length=255)
    studentId = serializers.CharField(max_length=50)
    email = serializers.EmailField()
    department = serializers.CharField(max_length=100, required=False, default='Computer Science')
    year = serializers.CharField(max_length=20, required=False, default='1st Year')
    section = serializers.CharField(max_length=10, required=False, default='A')
    scores = serializers.DictField()
    availability = serializers.ChoiceField(
        choices=['Morning', 'Afternoon', 'Evening'],
        required=False,
        default='Morning',
    )
    learningPreference = serializers.ChoiceField(
        choices=['Practical', 'Theory', 'Mixed'],
        required=False,
        default='Mixed',
    )
    password = serializers.CharField(max_length=128, required=False, allow_blank=True)
    confirmPassword = serializers.CharField(max_length=128, required=False, allow_blank=True)

    def validate(self, attrs):
        password = attrs.get('password', '')
        confirm_password = attrs.get('confirmPassword', '')

        if password:
            if len(password) < 8:
                raise serializers.ValidationError({'password': 'Password must be at least 8 characters.'})
            if confirm_password and password != confirm_password:
                raise serializers.ValidationError({'confirmPassword': 'Passwords do not match.'})

        if self.context.get('purpose') == 'registration':
            if not password:
                raise serializers.ValidationError({'password': 'Password is required.'})
            if not confirm_password:
                raise serializers.ValidationError({'confirmPassword': 'Please confirm your password.'})
            if password != confirm_password:
                raise serializers.ValidationError({'confirmPassword': 'Passwords do not match.'})

        return attrs

    def validate_scores(self, value):
        from ml.preprocessing import clean_scores

        if not isinstance(value, dict) or not value:
            raise serializers.ValidationError('Scores must be a non-empty object.')
        cleaned = clean_scores(_scores_to_ml(value))
        if all(score == 0 for score in cleaned.values()):
            raise serializers.ValidationError('Provide at least one score above zero.')
        return cleaned


class AdminStudentWriteSerializer(serializers.Serializer):
    """Payload used by the admin student create/update endpoints."""

    id = serializers.CharField(max_length=50)
    name = serializers.CharField(max_length=255)
    department = serializers.CharField(max_length=100, required=False, default='Computer Science')
    year = serializers.CharField(max_length=20, required=False, default='1st Year')
    section = serializers.CharField(max_length=10, required=False, default='A')
    scores = serializers.DictField()

    def validate_scores(self, value):
        from ml.preprocessing import clean_scores

        cleaned = clean_scores(value)
        if not cleaned:
            raise serializers.ValidationError('Scores must be a non-empty object.')
        return cleaned
