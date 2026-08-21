"""Repository layer for notifications and activity log entries."""
from __future__ import annotations

from typing import List, Optional

from notifications.models import ActivityLog, Notification


class NotificationRepository:
    """Data access for :class:`notifications.models.Notification`."""

    @staticmethod
    def for_admin() -> List[Notification]:
        return list(Notification.objects.filter(role='admin'))

    @staticmethod
    def for_student(student) -> List[Notification]:
        return list(Notification.objects.filter(role='student', student=student))

    @staticmethod
    def get(pk, role: str) -> Optional[Notification]:
        try:
            return Notification.objects.get(pk=pk, role=role)
        except (Notification.DoesNotExist, TypeError, ValueError):
            return None

    @staticmethod
    def create(role: str, title: str, message: str, tone: str = 'info', category: str = 'system', student=None) -> Notification:
        return Notification.objects.create(
            role=role,
            title=title,
            message=message,
            tone=tone,
            category=category,
            student=student,
        )

    @staticmethod
    def mark_read(notification: Notification) -> None:
        if not notification.read:
            notification.read = True
            notification.save(update_fields=['read'])

    @staticmethod
    def mark_all_read(role: str, student=None) -> int:
        queryset = Notification.objects.filter(role=role, read=False)
        if student is not None:
            queryset = queryset.filter(student=student)
        return queryset.update(read=True)

    @staticmethod
    def delete(notification: Notification) -> None:
        notification.delete()

    @staticmethod
    def clear(role: str, student=None) -> int:
        queryset = Notification.objects.filter(role=role)
        if student is not None:
            queryset = queryset.filter(student=student)
        return queryset.delete()[0]


class ActivityLogRepository:
    """Data access for :class:`notifications.models.ActivityLog`."""

    @staticmethod
    def log(action: str, actor: str = 'admin', detail: str = '') -> ActivityLog:
        return ActivityLog.objects.create(action=action, actor=actor, detail=detail)

    @staticmethod
    def recent(limit: int = 12) -> List[ActivityLog]:
        return list(ActivityLog.objects.all()[:limit])
