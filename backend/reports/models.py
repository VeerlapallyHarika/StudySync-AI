"""Persisted institutional reports."""
from django.db import models


class Report(models.Model):
    """A generated report snapshot stored as a JSON payload."""

    title = models.CharField(max_length=200)
    payload = models.JSONField()
    departments = models.JSONField(default=list, blank=True)
    group_names = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f'{self.title} ({self.created_at:%Y-%m-%d %H:%M})'
