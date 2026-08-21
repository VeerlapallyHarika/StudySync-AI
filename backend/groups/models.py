"""Study group model.

A :class:`StudyGroup` has a one-to-many relationship with students: each
:class:`students.models.Student` holds a nullable ``group`` foreign key. The
ordered member ids are mirrored in ``members`` so aggregates can be computed
without loading the full student table.
"""
from django.db import models


class StudyGroup(models.Model):
    """A balanced, skill-complementary study group."""

    name = models.CharField(max_length=100)
    members = models.JSONField(default=list)  # ordered student_id strings
    overall_strengths = models.JSONField(default=list)
    overall_weaknesses = models.JSONField(default=list)
    average_performance = models.FloatField(default=0.0)
    complementary_skill_score = models.FloatField(default=0.0)
    team_leader = models.CharField(max_length=255, blank=True)
    learning_recommendation = models.TextField(blank=True)
    recommendations = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['created_at'], name='group_created_idx'),
            models.Index(fields=['average_performance'], name='group_perf_idx'),
        ]

    def __str__(self) -> str:
        return f'{self.name} ({len(self.members)} members)'


class ChatMessage(models.Model):
    """A message posted by a student inside a study group chat."""

    group = models.ForeignKey(
        StudyGroup,
        on_delete=models.CASCADE,
        related_name='chat_messages',
    )
    sender = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='chat_messages',
    )
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['group', 'created_at'], name='chat_group_created_idx'),
        ]

    def __str__(self) -> str:
        return f'{self.sender.full_name}: {self.message[:50]}'


class SharedResource(models.Model):
    """A study resource shared by a group member with their study group."""

    RESOURCE_TYPE_CHOICES = (
        ('Study Notes', 'Study Notes'),
        ('Documents', 'Documents'),
        ('Useful Links', 'Useful Links'),
        ('Videos', 'Videos'),
        ('Assignments', 'Assignments'),
        ('Other', 'Other'),
    )

    group = models.ForeignKey(
        StudyGroup,
        on_delete=models.CASCADE,
        related_name='resources',
    )
    uploader = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='shared_resources',
    )
    title = models.CharField(max_length=255)
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPE_CHOICES, default='Other')
    url = models.URLField(blank=True)
    file = models.FileField(upload_to='resources/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['group', 'created_at'], name='resource_group_created_idx'),
        ]

    def __str__(self) -> str:
        return f'{self.title} ({self.get_resource_type_display()})'
