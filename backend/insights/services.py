"""Analytics, recommendations and settings services for the insights app."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List

from django.conf import settings as django_settings

from insights.models import SystemSettings
from ml.recommendation import build_student_insights
from ml.utils import SUBJECTS, average_score
from students.repositories import StudentRepository
from utils.logging import get_logger

logger = get_logger('insights')


# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------

def get_settings_payload() -> Dict[str, Any]:
    settings_row = SystemSettings.current()
    return {
        'departments': list(settings_row.departments or []),
        'defaultGroupSize': settings_row.default_group_size,
        'kmeansRandomState': settings_row.kmeans_random_state,
        'kmeansMaxIterations': settings_row.kmeans_max_iterations,
        'exportDefaultFormat': settings_row.export_default_format,
        'notifyGroupsGenerated': settings_row.notify_groups_generated,
        'notifyCsvImported': settings_row.notify_csv_imported,
    }


def update_settings(data: Dict[str, Any]) -> Dict[str, Any]:
    settings_row = SystemSettings.current()
    departments = data.get('departments')
    if isinstance(departments, list):
        settings_row.departments = [str(item).strip() for item in departments if str(item).strip()]

    for field, key, cast in (
        ('default_group_size', 'defaultGroupSize', int),
        ('kmeans_random_state', 'kmeansRandomState', int),
        ('kmeans_max_iterations', 'kmeansMaxIterations', int),
    ):
        if key in data:
            try:
                setattr(settings_row, field, max(cast(data[key]), 1))
            except (TypeError, ValueError):
                pass

    if data.get('exportDefaultFormat') in ('csv', 'excel', 'pdf'):
        settings_row.export_default_format = data['exportDefaultFormat']
    if isinstance(data.get('notifyGroupsGenerated'), bool):
        settings_row.notify_groups_generated = data['notifyGroupsGenerated']
    if isinstance(data.get('notifyCsvImported'), bool):
        settings_row.notify_csv_imported = data['notifyCsvImported']

    settings_row.save()
    logger.info('System settings updated')
    return get_settings_payload()


def system_info() -> Dict[str, Any]:
    students = StudentRepository.all()
    return {
        'name': 'StudySync AI',
        'version': '2.0.0',
        'djangoVersion': django_settings.VERSION if hasattr(django_settings, 'VERSION') else '',
        'backend': 'Django REST Framework',
        'frontend': 'React + TypeScript + Vite',
        'ml': 'scikit-learn KMeans with complementary matching',
        'database': 'SQLite',
        'totalStudents': len(students),
        'assignedStudents': sum(1 for student in students if student.group_id is not None),
    }


# ---------------------------------------------------------------------------
# Analytics
# ---------------------------------------------------------------------------

def _distribution(items: List[str]) -> Dict[str, int]:
    distribution: Dict[str, int] = {}
    for item in items:
        distribution[item] = distribution.get(item, 0) + 1
    return distribution


def subject_averages() -> List[Dict[str, Any]]:
    students = StudentRepository.all()
    if not students:
        return [{'subject': subject, 'average': 0, 'students': 0} for subject in SUBJECTS]
    totals = {subject: 0.0 for subject in SUBJECTS}
    for student in students:
        scores = student.scores
        for subject in SUBJECTS:
            totals[subject] += scores.get(subject, 0)
    return [
        {'subject': subject, 'average': round(totals[subject] / len(students)), 'students': len(students)}
        for subject in SUBJECTS
    ]


def department_performance() -> List[Dict[str, Any]]:
    students = StudentRepository.all()
    grouped: Dict[str, List[float]] = {}
    for student in students:
        grouped.setdefault(student.department, []).append(student.average_score)
    return [
        {
            'department': department,
            'average': round(sum(scores) / len(scores)) if scores else 0,
            'students': len(scores),
        }
        for department, scores in sorted(grouped.items(), key=lambda item: item[0])
    ]


def students_requiring_improvement(limit: int = 8) -> List[Dict[str, Any]]:
    threshold = 60
    candidates = [
        student
        for student in StudentRepository.all()
        if student.average_score < threshold
    ]
    candidates.sort(key=lambda student: student.average_score)
    return [
        {
            'studentId': student.student_id,
            'name': student.full_name,
            'department': student.department,
            'averageScore': round(student.average_score),
            'weaknesses': list(student.weaknesses or []),
            'group': student.group.name if student.group is not None else None,
        }
        for student in candidates[:limit]
    ]


def group_comparison() -> List[Dict[str, Any]]:
    from groups.services import list_groups

    groups = list_groups()
    return [
        {
            'id': group['id'],
            'name': group['name'],
            'members': len(group['members']),
            'averagePerformance': group['averagePerformance'],
            'complementarySkillScore': group['complementarySkillScore'],
        }
        for group in groups
    ]


def build_analytics() -> Dict[str, Any]:
    students = StudentRepository.all()
    strength_distribution = _distribution([subject for student in students for subject in (student.strengths or [])])
    weakness_distribution = _distribution([subject for student in students for subject in (student.weaknesses or [])])
    overall_average = round(sum(student.average_score for student in students) / len(students)) if students else 0

    return {
        'generatedAt': datetime.now(timezone.utc).isoformat(),
        'totalStudents': len(students),
        'totalGroups': len(group_comparison()),
        'overallAverageScore': overall_average,
        'subjectAverages': subject_averages(),
        'departmentPerformance': department_performance(),
        'strengthDistribution': strength_distribution,
        'weaknessDistribution': weakness_distribution,
        'groupComparison': group_comparison(),
        'studentsRequiringImprovement': students_requiring_improvement(),
    }


# ---------------------------------------------------------------------------
# Student insights
# ---------------------------------------------------------------------------

def student_insights(student) -> Dict[str, Any]:
    return build_student_insights(student)


def change_password(student, current_password: str, new_password: str) -> None:
    from rest_framework import exceptions

    if not student.check_password(current_password):
        raise exceptions.AuthenticationFailed('Current password is incorrect.')
    if len(new_password) < 6:
        raise exceptions.ValidationError('New password must be at least 6 characters.')
    student.set_password(new_password)
    student.save(update_fields=['password'])
    logger.info('Student password changed :: student_id=%s', student.student_id)


__all__ = ['SUBJECTS']
