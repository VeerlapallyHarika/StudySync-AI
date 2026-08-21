"""Repository layer for report persistence."""
from __future__ import annotations

from typing import List, Optional

from reports.models import Report


class ReportRepository:
    """Data access for :class:`reports.models.Report`."""

    @staticmethod
    def all() -> List[Report]:
        return list(Report.objects.all())

    @staticmethod
    def get(pk) -> Optional[Report]:
        try:
            return Report.objects.get(pk=pk)
        except (Report.DoesNotExist, TypeError, ValueError):
            return None

    @staticmethod
    def latest() -> Optional[Report]:
        return Report.objects.first()

    @staticmethod
    def count() -> int:
        return Report.objects.count()

    @staticmethod
    def create(title: str, payload: dict, departments=None, group_names=None) -> Report:
        return Report.objects.create(
            title=title,
            payload=payload,
            departments=departments or [],
            group_names=group_names or [],
        )

    @staticmethod
    def delete(report: Report) -> None:
        report.delete()
