"""Service layer for notifications and activity logging."""
from __future__ import annotations

from typing import Any, Dict, List

from notifications.repositories import ActivityLogRepository, NotificationRepository
from students.repositories import StudentRepository
from utils.logging import get_logger

logger = get_logger('notifications')


def notify_admin(title: str, message: str, tone: str = 'info', category: str = 'system') -> None:
    NotificationRepository.create(role='admin', title=title, message=message, tone=tone, category=category)


def notify_students(student_ids, title: str, message: str, tone: str = 'info', category: str = 'system') -> int:
    """Create a notification for every listed student id; returns the count."""
    created = 0
    for student_id in student_ids:
        student = StudentRepository.get_by_student_id(student_id)
        if student is None:
            continue
        NotificationRepository.create(
            role='student',
            student=student,
            title=title,
            message=message,
            tone=tone,
            category=category,
        )
        created += 1
    return created


def log_activity(action: str, actor: str = 'admin', detail: str = '') -> None:
    ActivityLogRepository.log(action, actor=actor, detail=detail)


def list_for(principal) -> List[Dict[str, Any]]:
    """Serialize notifications visible to the given principal."""
    if principal is not None and principal.is_student:
        records = NotificationRepository.for_student(principal.student)
    else:
        records = NotificationRepository.for_admin()
    return [
        {
            'id': record.pk,
            'category': record.category,
            'title': record.title,
            'message': record.message,
            'tone': record.tone,
            'read': record.read,
            'createdAt': record.created_at.isoformat(),
        }
        for record in records
    ]


def unread_count(principal) -> int:
    records = list_for(principal)
    return sum(1 for record in records if not record['read'])


def mark_read(principal, notification_id: int) -> bool:
    role = 'student' if (principal is not None and principal.is_student) else 'admin'
    notification = NotificationRepository.get(notification_id, role)
    if notification is None:
        return False
    NotificationRepository.mark_read(notification)
    return True


def mark_all_read(principal) -> int:
    role = 'student' if (principal is not None and principal.is_student) else 'admin'
    student = principal.student if (principal is not None and principal.is_student) else None
    return NotificationRepository.mark_all_read(role, student=student)


def clear_all(principal) -> int:
    role = 'student' if (principal is not None and principal.is_student) else 'admin'
    student = principal.student if (principal is not None and principal.is_student) else None
    return NotificationRepository.clear(role, student=student)


def recent_activities(limit: int = 12) -> List[Dict[str, Any]]:
    return [
        {
            'action': record.action,
            'actor': record.actor,
            'detail': record.detail,
            'createdAt': record.created_at.isoformat(),
        }
        for record in ActivityLogRepository.recent(limit)
    ]
