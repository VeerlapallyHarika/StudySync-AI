"""Student persistence model.

Scores are stored in explicit per-subject columns (not a JSON blob) so they can
be queried, validated and reported on directly. The :attr:`Student.scores`
property exposes the same ``{subject: score}`` mapping the ML pipeline expects.
"""
from __future__ import annotations

from typing import Any, Dict, List

from django.contrib.auth.hashers import check_password, make_password
from django.db import models

from ml.utils import SUBJECTS

LEARNING_PREFERENCES = (
    ('Practical', 'Practical'),
    ('Theory', 'Theory'),
    ('Mixed', 'Mixed'),
)

AVAILABILITY_CHOICES = (
    ('Morning', 'Morning'),
    ('Afternoon', 'Afternoon'),
    ('Evening', 'Evening'),
)

SUBJECT_FIELDS = {
    'Mathematics': 'mathematics',
    'Physics': 'physics',
    'Programming': 'programming',
    'Database': 'database_management',
    'Operating Systems': 'operating_systems',
}


class Student(models.Model):
    """A registered student with an academic profile and optional group."""

    student_id = models.CharField(max_length=50, unique=True)
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    department = models.CharField(max_length=100, default='Computer Science')
    year = models.CharField(max_length=20, default='1st Year')
    section = models.CharField(max_length=10, default='A')

    mathematics = models.FloatField(default=0.0)
    physics = models.FloatField(default=0.0)
    programming = models.FloatField(default=0.0)
    database_management = models.FloatField(default=0.0)
    operating_systems = models.FloatField(default=0.0)

    learning_preference = models.CharField(max_length=20, choices=LEARNING_PREFERENCES, default='Mixed')
    availability = models.CharField(max_length=20, choices=AVAILABILITY_CHOICES, default='Morning')

    average_score = models.FloatField(default=0.0)
    strengths = models.JSONField(default=list)
    weaknesses = models.JSONField(default=list)

    group = models.ForeignKey(
        'groups.StudyGroup',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='student_assignments',
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['full_name']
        indexes = [
            models.Index(fields=['email'], name='student_email_idx'),
            models.Index(fields=['department'], name='student_dept_idx'),
            models.Index(fields=['average_score'], name='student_avg_idx'),
            models.Index(fields=['created_at'], name='student_created_idx'),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(
                    mathematics__gte=0.0,
                    mathematics__lte=100.0,
                    physics__gte=0.0,
                    physics__lte=100.0,
                    programming__gte=0.0,
                    programming__lte=100.0,
                    database_management__gte=0.0,
                    database_management__lte=100.0,
                    operating_systems__gte=0.0,
                    operating_systems__lte=100.0,
                ),
                name='student_scores_range_0_100',
            ),
        ]

    def __str__(self) -> str:
        return f'{self.full_name} ({self.student_id})'

    # ------------------------------------------------------------------
    # Academic helpers shared with the ML pipeline
    # ------------------------------------------------------------------
    @property
    def scores(self) -> Dict[str, float]:
        """Subject-keyed scores using the ML pipeline's subject names."""
        return {
            'Mathematics': self.mathematics,
            'Physics': self.physics,
            'Programming': self.programming,
            'Database': self.database_management,
            'Operating Systems': self.operating_systems,
        }

    def set_score(self, subject: str, value: float) -> None:
        """Persist a single subject score onto the matching column."""
        field = SUBJECT_FIELDS.get(subject)
        if field is None:
            return
        setattr(self, field, float(value))

    @property
    def subject_list(self) -> List[str]:
        return list(SUBJECTS)

    def set_password(self, raw_password: str) -> None:
        self.password = make_password(raw_password)

    def check_password(self, raw_password: str) -> bool:
        return check_password(raw_password, self.password)

    def recompute_profile(self, save: bool = True) -> None:
        """Recompute strengths, weaknesses and the overall average score.

        When ``save=False`` the caller is responsible for persisting the
        derived fields (used by bulk operations).
        """
        from ml.strength_analysis import detect_strengths, detect_weaknesses
        from ml.utils import average_score

        scores = self.scores
        self.strengths = detect_strengths(scores)
        self.weaknesses = detect_weaknesses(scores)
        self.average_score = float(average_score(scores))
        if save:
            self.save(update_fields=['strengths', 'weaknesses', 'average_score', 'updated_at'])
