"""Notification and activity persistence.

- :class:`Notification` is an inbox item shown to an admin or a student.
- :class:`ActivityLog` is an immutable audit trail powering the "Recent
  Activity" widget on the admin dashboard.
"""
from django.db import models


class Notification(models.Model):
    """A toast/inbox notification scoped to a role (and optionally a student)."""

    ROLE_CHOICES = (('admin', 'admin'), ('student', 'student'))

    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    student = models.ForeignKey(
        'students.Student',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='notifications',
    )
    category = models.CharField(max_length=50, default='system')
    title = models.CharField(max_length=200)
    message = models.TextField(blank=True)
    tone = models.CharField(
        max_length=10,
        choices=(('success', 'success'), ('warning', 'warning'), ('info', 'info')),
        default='info',
    )
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['role', 'read'], name='notif_role_read_idx'),
            models.Index(fields=['created_at'], name='notif_created_idx'),
        ]

    def __str__(self) -> str:
        return f'{self.role} notification: {self.title}'


class ActivityLog(models.Model):
    """Audit trail entry describing a meaningful system event."""

    ACTION_CHOICES = (
        ('group_generated', 'Group generated'),
        ('csv_imported', 'CSV imported'),
        ('report_exported', 'Report exported'),
        ('student_registered', 'Student registered'),
        ('student_updated', 'Student updated'),
        ('group_deleted', 'Group deleted'),
        ('duplicate_skipped', 'Duplicate skipped'),
        ('student_deleted', 'Student deleted'),
        ('profile_updated', 'Profile updated'),
        ('settings_updated', 'Settings updated'),
    )

    action = models.CharField(max_length=40, choices=ACTION_CHOICES)
    actor = models.CharField(max_length=40, default='admin')
    detail = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['action', 'created_at'], name='activity_action_idx'),
        ]

    def __str__(self) -> str:
        return f'{self.action} @ {self.created_at:%H:%M}'
