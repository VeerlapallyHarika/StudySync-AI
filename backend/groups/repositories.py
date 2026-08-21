"""Repository layer for study group persistence."""
from __future__ import annotations

from typing import Any, List, Optional

from django.db import transaction

from groups.models import StudyGroup
from students.models import Student


class GroupRepository:
    """Data access for :class:`groups.models.StudyGroup`."""

    @staticmethod
    def all() -> List[StudyGroup]:
        return list(StudyGroup.objects.all())

    @staticmethod
    def get(pk) -> Optional[StudyGroup]:
        try:
            return StudyGroup.objects.get(pk=pk)
        except (StudyGroup.DoesNotExist, TypeError, ValueError):
            return None

    @staticmethod
    def count() -> int:
        return StudyGroup.objects.count()

    @staticmethod
    def create(
        name: str,
        members: List[str],
        overall_strengths: List[str],
        overall_weaknesses: List[str],
        average_performance: float,
        complementary_skill_score: float,
        team_leader: str,
        learning_recommendation: str,
        recommendations: dict | None = None,
    ) -> StudyGroup:
        return StudyGroup.objects.create(
            name=name,
            members=members,
            overall_strengths=overall_strengths,
            overall_weaknesses=overall_weaknesses,
            average_performance=average_performance,
            complementary_skill_score=complementary_skill_score,
            team_leader=team_leader,
            learning_recommendation=learning_recommendation,
            recommendations=recommendations or {},
        )

    @staticmethod
    @transaction.atomic
    def update(group: StudyGroup, **fields: Any) -> StudyGroup:
        for key, value in fields.items():
            if hasattr(group, key):
                setattr(group, key, value)
        group.save()
        return group

    @staticmethod
    @transaction.atomic
    def delete(group: StudyGroup) -> None:
        Student.objects.filter(group=group).update(group=None)
        group.delete()

    @staticmethod
    @transaction.atomic
    def delete_all() -> int:
        """Delete every group and release all student assignments."""
        count = StudyGroup.objects.count()
        Student.objects.update(group=None)
        StudyGroup.objects.all().delete()
        return count
