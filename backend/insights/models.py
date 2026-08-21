"""System configuration persisted per-deployment.

The whole application reads tuneable knobs (group size, K-Means parameters,
departments, export preferences) from this single row so admins can change
behaviour without touching code.
"""
from django.db import models

DEFAULT_DEPARTMENTS = [
    'Computer Science',
    'Information Technology',
    'Electronics',
    'AIML',
    'Mechanical',
    'Civil',
]


class SystemSettings(models.Model):
    """Single-row configuration store (row 1 is the canonical instance)."""

    departments = models.JSONField(default=list)
    default_group_size = models.IntegerField(default=4)
    kmeans_random_state = models.IntegerField(default=42)
    kmeans_max_iterations = models.IntegerField(default=300)
    export_default_format = models.CharField(max_length=10, default='csv')
    notify_groups_generated = models.BooleanField(default=True)
    notify_csv_imported = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'System settings'

    def __str__(self) -> str:
        return f'System settings (group size {self.default_group_size})'

    @classmethod
    def current(cls) -> 'SystemSettings':
        """Return the singleton settings row, creating defaults if needed."""
        instance, _created = cls.objects.get_or_create(pk=1)
        if _created:
            instance.departments = list(DEFAULT_DEPARTMENTS)
            instance.save(update_fields=['departments'])
        return instance
