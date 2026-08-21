"""Service layer for students: registration, login, profiles and dashboards."""
from __future__ import annotations

import io
from typing import Any, Dict, List, Optional

import pandas as pd
from django.conf import settings
from rest_framework import exceptions

from authentication.jwt import Principal, issue_access_token, issue_refresh_token
from ml.strength_analysis import detect_strengths, detect_weaknesses
from ml.utils import SUBJECTS
from notifications import services as notification_services
from students.models import Student
from students.repositories import StudentRepository
from utils.logging import get_logger

logger = get_logger('students')

DISPLAY_SUBJECTS = [
    'Mathematics',
    'Physics',
    'Programming',
    'Database Management',
    'Operating Systems',
]
DISPLAY_NAME_MAP = {'Database': 'Database Management'}
SUBJECT_COLUMN_ALIASES = {
    'mathematics': 'Mathematics',
    'math': 'Mathematics',
    'physics': 'Physics',
    'programming': 'Programming',
    'database': 'Database',
    'database management': 'Database',
    'database_management': 'Database',
    'operating systems': 'Operating Systems',
    'operating_system': 'Operating Systems',
    'os': 'Operating Systems',
}


def _display_subject(subject: str) -> str:
    return DISPLAY_NAME_MAP.get(subject, subject)


def _student_scores(student: Student) -> Dict[str, float]:
    """Display scores keyed by the frontend subject names."""
    return {
        'Mathematics': student.mathematics,
        'Physics': student.physics,
        'Programming': student.programming,
        'Database Management': student.database_management,
        'Operating Systems': student.operating_systems,
    }


def _subject_status(score: float) -> str:
    if score >= 85:
        return 'Excellent'
    if score >= 70:
        return 'Strong'
    if score >= 50:
        return 'Average'
    return 'Needs Improvement'


def _subject_description(score: float) -> str:
    if score >= 85:
        return 'Excellent'
    if score >= 70:
        return 'Strong'
    if score >= 50:
        return 'Improving'
    return 'Needs Improvement'


def _student_insights(student: Student) -> Dict[str, Any]:
    """AI insights for the student dashboard/profile (frontend subject names)."""
    from ml.recommendation import build_student_insights

    insights = build_student_insights(student)

    def _display_list(values):
        return [_display_subject(value) for value in values]

    def _display_resources(resources):
        return [
            {
                'subject': _display_subject(resource['subject']),
                'resource': resource['resource'],
            }
            for resource in resources
        ]

    peer = insights['peerMentor']
    return {
        'academicSummary': insights['academicSummary'],
        'learningTrend': insights['learningTrend'],
        'strengthScore': insights['strengthScore'],
        'weaknessScore': insights['weaknessScore'],
        'improvementSuggestions': insights['improvementSuggestions'],
        'learningResources': _display_resources(insights['learningResources']),
        'peerMentor': {
            'name': peer['name'],
            'subject': _display_subject(peer['subject']) if peer['subject'] else None,
            'reason': peer['reason'],
        },
        'studySessions': insights['studySessions'],
    }


def _group_members(student: Student) -> List[Dict[str, Any]]:
    group = student.group
    if group is None:
        return []
    members: List[Dict[str, Any]] = []
    for member_id in group.members:
        member = StudentRepository.get_by_student_id(member_id)
        if member is None:
            continue
        strengths = member.strengths or detect_strengths(member.scores)
        weaknesses = member.weaknesses or detect_weaknesses(member.scores)
        members.append({
            'avatar': member.full_name[:1].upper() if member.full_name else '?',
            'name': member.full_name,
            'department': member.department,
            'strongSubject': _display_subject(strengths[0]) if strengths else 'Balanced',
            'weakSubject': _display_subject(weaknesses[0]) if weaknesses else 'None',
            'status': 'You' if member.pk == student.pk else 'Active',
        })
    return members


def _notifications(student: Student) -> List[Dict[str, str]]:
    weaknesses = student.weaknesses or detect_weaknesses(student.scores)
    notifications: List[Dict[str, str]] = [
        {
            'title': 'Profile Ready',
            'description': 'Your academic profile is ready for smart group matching.',
            'tone': 'success',
        }
    ]
    if student.group is not None:
        notifications.append({
            'title': f'Group {student.group.name}',
            'description': 'Your study group has been formed. Review the members below.',
            'tone': 'info',
        })
    if weaknesses:
        notifications.append({
            'title': 'Focus Area',
            'description': f'Prioritize {_display_subject(weaknesses[0])} with your study plan.',
            'tone': 'warning',
        })
    return notifications


def build_profile(student: Student) -> Dict[str, Any]:
    """Build the exact ``StudentProfileData`` payload the frontend expects."""
    group = student.group
    strengths = student.strengths or detect_strengths(student.scores)
    overall_strength = (
        ', '.join(_display_subject(subject) for subject in (group.overall_strengths or []))
        if group is not None and group.overall_strengths
        else 'Balanced cohort'
    )
    return {
        'fullName': student.full_name,
        'studentId': student.student_id,
        'email': student.email,
        'department': student.department,
        'year': student.year,
        'section': student.section,
        'availability': student.availability,
        'learningPreference': student.learning_preference,
        'scores': _student_scores(student),
        'assignedGroup': group.name if group is not None else None,
        'overallGroupStrength': overall_strength,
        'groupMembers': _group_members(student),
        'notifications': _notifications(student),
        'averageScore': round(student.average_score),
        'strengths': [_display_subject(subject) for subject in strengths],
        'insights': _student_insights(student),
    }


def build_dashboard(student: Student) -> Dict[str, Any]:
    """Build the ``StudentDashboardData`` payload."""
    scores = _student_scores(student)
    strengths = student.strengths or detect_strengths(student.scores)
    weaknesses = student.weaknesses or detect_weaknesses(student.scores)
    display_strengths = [_display_subject(subject) for subject in strengths][:2]
    display_weaknesses = [_display_subject(subject) for subject in weaknesses][:2]

    group = student.group
    group_name = group.name if group is not None else 'Not assigned'
    group_overall = (
        ', '.join(_display_subject(subject) for subject in (group.overall_strengths or []))
        if group is not None and group.overall_strengths
        else ('Balanced cohort' if group is not None else 'Waiting for placement')
    )

    stats = [
        {'label': 'Academic Strengths', 'value': str(len(display_strengths)), 'note': ', '.join(display_strengths) or 'None yet'},
        {'label': 'Weak Subjects', 'value': str(len(display_weaknesses)), 'note': ', '.join(display_weaknesses) or 'None yet'},
        {'label': 'Assigned Group', 'value': group_name, 'note': group_overall},
        {'label': 'Overall Performance', 'value': f'{round(student.average_score)}%', 'note': 'Excellent' if student.average_score >= 80 else 'Growing strong'},
    ]

    return {
        'welcomeName': student.full_name or 'Student',
        'stats': stats,
        'academicSummary': [
            {
                'subject': subject,
                'score': int(scores[subject]),
                'status': _subject_status(scores[subject]),
                'description': _subject_description(scores[subject]),
                'progress': max(0, min(100, scores[subject])),
            }
            for subject in DISPLAY_SUBJECTS
        ],
        'strengthAnalysis': {'strengths': display_strengths, 'weaknesses': display_weaknesses},
        'assignedGroup': {
            'name': group_name,
            'members': [_member['name'] for _member in _group_members(student)],
            'overallStrength': group_overall,
        },
        'groupMembers': _group_members(student),
        'notifications': _notifications(student),
        'overallPerformance': round(student.average_score),
        'insights': _student_insights(student),
    }


def build_admin_student(student: Student) -> Dict[str, Any]:
    """Build the ``AdminStudent`` payload."""
    group = student.group
    return {
        'id': student.student_id,
        'name': student.full_name,
        'department': student.department,
        'year': student.year,
        'section': student.section,
        'scores': student.scores,
        'strengths': student.strengths or [],
        'weaknesses': student.weaknesses or [],
        'status': 'Assigned' if group is not None else 'Waiting',
        'groupName': group.name if group is not None else None,
        'averageScore': round(student.average_score),
    }


def _token_pair(student: Student) -> Dict[str, str]:
    principal = Principal(role='student', student=student)
    return {
        'access': issue_access_token(principal),
        'refresh': issue_refresh_token(principal),
    }


def student_refresh(refresh_token: str) -> Dict[str, str]:
    """Issue a fresh access token from a valid student refresh token."""
    from datetime import datetime, timezone

    from authentication.models import RefreshToken

    digest = RefreshToken.hash_token(refresh_token)
    record = (
        RefreshToken.objects.filter(token_hash=digest, role='student', revoked=False)
        .filter(expires_at__gt=datetime.now(timezone.utc))
        .select_related('student')
        .first()
    )
    if record is None or record.student is None:
        raise exceptions.AuthenticationFailed('Invalid or expired refresh token.')
    return {'access': issue_access_token(Principal(role='student', student=record.student))}


def student_logout(refresh_token: str) -> None:
    """Revoke a student refresh token."""
    from authentication.jwt import revoke_refresh_token

    if revoke_refresh_token(refresh_token):
        logger.info('Student refresh token revoked')


def register_student(data: Dict[str, Any], password: Optional[str] = None) -> Dict[str, Any]:
    """Register a new student and return their profile without signing them in."""
    student_id = data['studentId'].strip()
    email = data['email'].strip().lower()
    password = password or settings.DEFAULT_STUDENT_PASSWORD

    if StudentRepository.exists_by_student_id(student_id):
        raise exceptions.ValidationError('A student with this ID is already registered.')
    if StudentRepository.exists_by_email(email):
        raise exceptions.ValidationError('A student with this email is already registered.')

    student = StudentRepository.create(
        student_id=student_id,
        full_name=data['fullName'].strip(),
        email=email,
        password=password,
        department=data['department'],
        year=data['year'],
        section=data['section'],
        scores=data['scores'],
        learning_preference=data['learningPreference'],
        availability=data['availability'],
    )
    logger.info('Student registered :: student_id=%s email=%s', student.student_id, student.email)
    notification_services.log_activity('student_registered', detail=f'{student.full_name} registered')
    notification_services.notify_admin(
        'New Student Registered',
        f'{student.full_name} ({student.student_id}) registered and is waiting for group placement.',
        tone='info',
        category='students',
    )

    from groups.services import assign_student_to_group  # local import to avoid a cycle

    assign_student_to_group(student)
    student.refresh_from_db()
    return build_profile(student)


def login_student(email: str, password: str) -> Dict[str, Any]:
    """Authenticate a student and return their profile plus a token pair."""
    student = StudentRepository.get_by_email(email)
    if student is None or not student.check_password(password):
        logger.warning('Student authentication failed :: email=%s', (email or '').strip().lower())
        raise exceptions.AuthenticationFailed('Invalid student credentials.')
    logger.info('Student logged in :: student_id=%s', student.student_id)
    if student.group is None:
        from groups.services import assign_student_to_group, profile_complete
        if profile_complete(student):
            assign_student_to_group(student)
            student.refresh_from_db()
    return {**build_profile(student), **_token_pair(student)}


def get_profile(student: Student) -> Dict[str, Any]:
    return build_profile(student)


def update_profile(student: Student, data: Dict[str, Any]) -> Dict[str, Any]:
    """Apply profile updates, guarding uniqueness of the ID and email."""
    new_id = data.get('studentId', student.student_id).strip()
    new_email = data.get('email', student.email).strip().lower()

    duplicate_id = StudentRepository.get_by_student_id(new_id)
    if duplicate_id is not None and duplicate_id.pk != student.pk:
        raise exceptions.ValidationError('A student with this ID already exists.')
    duplicate_email = StudentRepository.get_by_email(new_email)
    if duplicate_email is not None and duplicate_email.pk != student.pk:
        raise exceptions.ValidationError('A student with this email already exists.')

    updated = StudentRepository.update(
        student,
        student_id=new_id,
        full_name=data['fullName'].strip(),
        email=new_email,
        department=data['department'],
        year=data['year'],
        section=data['section'],
        scores=data['scores'],
        learning_preference=data['learningPreference'],
        availability=data['availability'],
    )
    logger.info('Student profile updated :: student_id=%s', updated.student_id)
    notification_services.log_activity('student_updated', detail=f'{updated.full_name} updated their profile')

    if updated.group is not None:
        from groups.services import _recompute_group_metrics
        _recompute_group_metrics(updated.group)
    else:
        from groups.services import assign_student_to_group, profile_complete
        if profile_complete(updated):
            assign_student_to_group(updated)

    updated.refresh_from_db()
    return build_profile(updated)


def list_students(filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """List students, optionally filtered by search term, department, year or status."""
    filters = filters or {}
    search = (filters.get('search') or '').strip().lower()
    department = (filters.get('department') or '').strip()
    year = (filters.get('year') or '').strip()
    status_filter = (filters.get('status') or '').strip().lower()

    students = StudentRepository.all()
    matched: List[Dict[str, Any]] = []
    for student in students:
        group = student.group
        status = 'Assigned' if group is not None else 'Waiting'
        if search and search not in f'{student.student_id} {student.full_name} {student.email}'.lower():
            continue
        if department and department != student.department:
            continue
        if year and year != student.year:
            continue
        if status_filter and status.lower() != status_filter:
            continue
        matched.append(build_admin_student(student))
    return matched


def get_student_admin(student: Student) -> Dict[str, Any]:
    return build_admin_student(student)


def update_student_admin(student: Student, data: Dict[str, Any]) -> Dict[str, Any]:
    new_id = data.get('id', student.student_id).strip()
    duplicate_id = StudentRepository.get_by_student_id(new_id)
    if duplicate_id is not None and duplicate_id.pk != student.pk:
        raise exceptions.ValidationError('A student with this ID already exists.')

    updated = StudentRepository.update(
        student,
        student_id=new_id,
        full_name=data['name'].strip(),
        department=data['department'],
        year=data['year'],
        section=data['section'],
        scores=data['scores'],
    )
    logger.info('Admin updated student :: student_id=%s', updated.student_id)
    return build_admin_student(updated)


def delete_student(student: Student) -> None:
    logger.info('Admin deleted student :: student_id=%s', student.student_id)
    notification_services.log_activity('student_deleted', detail=f'{student.full_name} was removed')
    StudentRepository.delete(student)


def import_students_csv(uploaded_file) -> Dict[str, Any]:
    """Validate, store and analyze a CSV upload, then auto-generate groups.

    Returns counts plus the freshly generated groups so the admin dashboard can
    refresh immediately.
    """
    raw = uploaded_file.read()
    try:
        text = raw.decode('utf-8-sig')
    except UnicodeDecodeError:
        text = raw.decode('latin-1')

    try:
        frame = pd.read_csv(io.StringIO(text))
    except Exception as exc:
        raise exceptions.ValidationError(f'Unable to parse CSV: {exc}') from exc

    if frame.empty:
        raise exceptions.ValidationError('The uploaded CSV contains no data rows.')

    columns = {str(column).strip().lower().replace('_', ' '): column for column in frame.columns}
    score_map = {alias: column for alias, column in columns.items() if alias in SUBJECT_COLUMN_ALIASES}

    id_column = _first_present(columns, ['student id', 'studentid', 'id', 'student'])
    name_column = _first_present(columns, ['name', 'full name', 'student name'])
    email_column = _first_present(columns, ['email', 'e mail'])
    department_column = _first_present(columns, ['department'])
    year_column = _first_present(columns, ['year'])
    section_column = _first_present(columns, ['section'])

    if id_column is None or name_column is None or not score_map:
        raise exceptions.ValidationError(
            'CSV must include student ID, name and subject score columns '
            '(Mathematics, Physics, Programming, Database, Operating Systems).'
        )

    rows: List[Dict[str, Any]] = []
    skipped = 0
    for _, record in frame.iterrows():
        student_id = _cell(record[id_column])
        name = _cell(record[name_column])
        if not student_id or not name:
            skipped += 1
            continue
        if StudentRepository.exists_by_student_id(student_id):
            skipped += 1
            continue

        scores = {}
        for alias, column in score_map.items():
            scores[SUBJECT_COLUMN_ALIASES[alias]] = _cell(record[column], fallback=0)
        if all(float(value or 0) == 0 for value in scores.values()):
            skipped += 1
            continue

        email = (_cell(record[email_column]) or f'{student_id.lower()}@studysync.ai') if email_column else f'{student_id.lower()}@studysync.ai'
        if StudentRepository.exists_by_email(email):
            skipped += 1
            continue

        rows.append({
            'student_id': student_id,
            'name': name,
            'email': email,
            'department': _cell(record[department_column], fallback='Computer Science') if department_column else 'Computer Science',
            'year': _cell(record[year_column], fallback='1st Year') if year_column else '1st Year',
            'section': _cell(record[section_column], fallback='A') if section_column else 'A',
            'scores': scores,
            'password': settings.DEFAULT_STUDENT_PASSWORD,
        })

    created = StudentRepository.create_many(rows)
    added = len(created)
    logger.info('CSV import finished :: added=%s skipped=%s', added, skipped)
    notification_services.log_activity('csv_imported', detail=f'{added} students added, {skipped} skipped')
    if added:
        notification_services.notify_admin(
            'Students Imported from CSV',
            f'{added} students added; {skipped} rows skipped.',
            tone='info',
            category='students',
        )

    if added == 0:
        return {'added': 0, 'skipped': skipped, 'groups': [], 'summary': None}

    from groups.services import ensure_groups  # local import to avoid a cycle

    groups, summary = ensure_groups()
    return {
        'added': added,
        'skipped': skipped,
        'groups': groups,
        'summary': summary,
    }


def _first_present(columns: Dict[str, str], candidates: List[str]) -> Optional[str]:
    for candidate in candidates:
        if candidate in columns:
            return columns[candidate]
    return None


def _cell(value: Any, fallback: Any = '') -> Any:
    if value is None:
        return fallback
    try:
        if pd.isna(value):
            return fallback
    except (TypeError, ValueError):
        pass
    return str(value).strip()


__all__ = ['SUBJECTS']
