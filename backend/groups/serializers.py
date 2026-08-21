"""Serializers for the groups application."""
from rest_framework import serializers


class GroupUpdateSerializer(serializers.Serializer):
    """Payload for updating a group name and/or member composition."""

    name = serializers.CharField(max_length=100, required=False)
    members = serializers.ListField(
        child=serializers.CharField(max_length=50),
        required=False,
    )


class GroupGenerateSerializer(serializers.Serializer):
    """Payload for group generation (size is fixed at 5)."""

    group_size = serializers.IntegerField(min_value=5, max_value=5, required=False, default=5)


class ChatMessageSerializer(serializers.Serializer):
    """Payload for posting a message to the group chat."""

    message = serializers.CharField(max_length=2000, trim_whitespace=True)

    def validate_message(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError('Message cannot be empty.')
        return value


class ResourceShareSerializer(serializers.Serializer):
    """Payload for sharing a resource with a study group.

    Supports either a ``url`` (links/videos) or an uploaded ``file``. At least
    one of the two must be provided.
    """

    title = serializers.CharField(max_length=255, trim_whitespace=True)
    resourceType = serializers.ChoiceField(
        choices=['Study Notes', 'Documents', 'Useful Links', 'Videos', 'Assignments', 'Other'],
        required=False,
        default='Other',
    )
    url = serializers.URLField(required=False, allow_blank=True)
    file = serializers.FileField(required=False, allow_empty_file=False)

    def validate_title(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError('Title cannot be empty.')
        return value

    def validate(self, attrs):
        url = (attrs.get('url') or '').strip()
        if not url and not attrs.get('file'):
            raise serializers.ValidationError('Provide either a URL or a file to share.')
        return attrs
