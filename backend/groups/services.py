"""Service layer for study group generation and management."""
from __future__ import annotations

import string
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from django.db import transaction
from rest_framework import exceptions

from groups.models import ChatMessage, SharedResource, StudyGroup
from groups.repositories import GroupRepository
from ml.clustering import k_means_cluster
from ml.feature_engineering import build_feature_matrix
from ml.group_balancer import (
    average_performance_of,
    compute_complementary_skill_score,
    overall_strength_of,
    overall_weakness_of,
)
from ml.quality import detect_duplicates, evaluate_clustering, missing_scores
from ml.recommendation import (
    build_group_recommendations,
    build_learning_recommendation,
    suggest_team_leader_name,
)
from notifications import services as notification_services
from students.models import Student
from students.repositories import StudentRepository
from utils.logging import get_logger

logger = get_logger('groups')

TARGET_GROUP_SIZE = 5
DEFAULT_GROUP_SIZE = 5
MINIMUM_GROUP_SIZE = 1

WAITING_MESSAGE = 'Waiting for profile completion to join a study group.'


def build_group_payload(group: StudyGroup) -> Dict[str, Any]:
    """Serialize a group into the payload the frontend consumes."""
    members = []
    for student_id in group.members:
        member = StudentRepository.get_by_student_id(student_id)
        if member is None:
            continue
        members.append({
            'studentId': member.student_id,
            'name': member.full_name,
            'department': member.department,
            'strongSubjects': member.strengths or [],
            'weakSubjects': member.weaknesses or [],
            'averageScore': round(member.average_score),
            'scores': member.scores,
            'learningPreference': member.learning_preference,
            'availability': member.availability,
        })

    created_at = group.created_at
    if created_at is not None and created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)

    recommendations = getattr(group, 'recommendations', None) or {}

    return {
        'id': str(group.pk),
        'name': group.name,
        'members': members,
        'overallStrengths': group.overall_strengths or [],
        'overallWeaknesses': group.overall_weaknesses or [],
        'averagePerformance': round(group.average_performance),
        'complementarySkillScore': round(group.complementary_skill_score),
        'teamLeader': group.team_leader,
        'learningRecommendation': group.learning_recommendation,
        'recommendations': recommendations,
        'createdAt': created_at.astimezone(timezone.utc).isoformat() if created_at else None,
    }


def _group_name(index: int) -> str:
    """Human-friendly group name (Group A, Group B, ... Group Z, then numeric)."""
    letters = string.ascii_uppercase
    if index <= len(letters):
        return f'Group {letters[index - 1]}'
    return f'Group {index}'


def _build_summary(
    groups: List[Dict[str, Any]],
    students: List[Student],
    quality: Optional[Dict[str, Any]] = None,
    duplicates: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    total_members = sum(len(group['members']) for group in groups)
    return {
        'groupsCreated': len(groups),
        'studentsNotAssigned': max(0, len(students) - total_members),
        'averageGroupSize': round((total_members / len(groups)), 1) if groups else 0,
        'quality': quality or {},
        'duplicatesDetected': duplicates or [],
    }


def eligible_students() -> List[Student]:
    """Students whose profiles are complete enough for group matching."""
    return [student for student in StudentRepository.all() if profile_complete(student)]


def _recompute_group_metrics(group: StudyGroup) -> None:
    """Recompute all aggregate fields on a StudyGroup from its current members."""
    member_objs: List[Student] = []
    valid_ids: List[str] = []
    for sid in group.members:
        m = StudentRepository.get_by_student_id(sid)
        if m is not None:
            member_objs.append(m)
            valid_ids.append(m.student_id)

    group.members = valid_ids
    group.overall_strengths = overall_strength_of(member_objs)
    group.overall_weaknesses = overall_weakness_of(member_objs)
    group.average_performance = average_performance_of(member_objs)
    group.complementary_skill_score = compute_complementary_skill_score(member_objs)
    group.team_leader = suggest_team_leader_name(member_objs)
    group.learning_recommendation = build_learning_recommendation(member_objs)
    group.recommendations = build_group_recommendations(member_objs)
    group.save()
    for m in member_objs:
        if m.group_id != group.pk:
            m.group = group
            m.save(update_fields=['group'])


@transaction.atomic
def assign_student_to_group(student: Student) -> StudyGroup:
    """Assign an unassigned student to an existing incomplete group or create a new group.

    - Evaluates complementary compatibility across incomplete groups (<5 members).
    - Caps groups strictly at 5 members.
    - Creates a new group only when all existing groups are full (5 members) or none exist.
    - Preserves existing group assignments without reshuffling.
    """
    if student.group is not None:
        return student.group

    existing_groups = list(StudyGroup.objects.all().order_by('created_at', 'id'))
    incomplete_groups = [g for g in existing_groups if len(g.members) < TARGET_GROUP_SIZE]

    if incomplete_groups:
        best_group = None
        best_score = -1.0

        for candidate_group in incomplete_groups:
            current_members = [
                StudentRepository.get_by_student_id(sid)
                for sid in candidate_group.members
                if StudentRepository.get_by_student_id(sid) is not None
            ]
            candidate_members = current_members + [student]
            score = compute_complementary_skill_score(candidate_members)
            if score > best_score:
                best_score = score
                best_group = candidate_group

        if best_group is None:
            best_group = incomplete_groups[0]

        if student.student_id not in best_group.members:
            best_group.members.append(student.student_id)
        _recompute_group_metrics(best_group)
        student.group = best_group
        student.save(update_fields=['group'])

        other_ids = [mid for mid in best_group.members if mid != student.student_id]
        if other_ids:
            notification_services.notify_students(
                other_ids,
                'New Member Joined Your Group',
                f'{student.full_name} has joined {best_group.name}.',
                tone='info',
                category='groups',
            )
        notification_services.notify_admin(
            'Study Group Updated',
            f'{student.full_name} joined {best_group.name}.',
            tone='info',
            category='groups',
        )
        notification_services.notify_students(
            [student.student_id],
            'You Have a Study Group',
            f'You have joined {best_group.name}. Check your dashboard for members and recommendations.',
            tone='success',
            category='groups',
        )
        notification_services.log_activity('group_generated', detail=f'{student.full_name} joined {best_group.name}')
        return best_group
    else:
        next_index = len(existing_groups) + 1
        group_name = _group_name(next_index)
        new_group = GroupRepository.create(
            name=group_name,
            members=[student.student_id],
            overall_strengths=overall_strength_of([student]),
            overall_weaknesses=overall_weakness_of([student]),
            average_performance=average_performance_of([student]),
            complementary_skill_score=compute_complementary_skill_score([student]),
            team_leader=suggest_team_leader_name([student]),
            learning_recommendation=build_learning_recommendation([student]),
            recommendations=build_group_recommendations([student]),
        )
        student.group = new_group
        student.save(update_fields=['group'])

        notification_services.notify_students(
            [student.student_id],
            'You Have a New Study Group',
            f'Your study group {new_group.name} has been formed.',
            tone='success',
            category='groups',
        )
        notification_services.notify_admin(
            'New Study Group Formed',
            f'{new_group.name} formed.',
            tone='success',
            category='groups',
        )
        notification_services.log_activity('group_generated', detail=f'{new_group.name} formed')
        return new_group


@transaction.atomic
def ensure_groups() -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Incrementally assign every unassigned eligible student into study groups.

    - Preserves all existing group assignments.
    - Fills incomplete existing groups first.
    - Uses K-Means clustering and complementary matching when a cohort of unassigned students exists.
    - Groups start as soon as 1 real student is eligible.
    - Groups never exceed 5 members.
    """
    from insights.models import SystemSettings

    students = eligible_students()
    existing_groups = list(list(GroupRepository.all()))

    unassigned = [s for s in students if s.group_id is None]
    if not unassigned:
        existing_payloads = [build_group_payload(g) for g in existing_groups]
        return existing_payloads, _build_summary(existing_payloads, students)

    # First, fill existing incomplete groups (< 5 members)
    for g in existing_groups:
        while len(g.members) < TARGET_GROUP_SIZE and unassigned:
            current_members = [
                StudentRepository.get_by_student_id(sid)
                for sid in g.members
                if StudentRepository.get_by_student_id(sid) is not None
            ]
            best_stu = None
            best_score = -1.0
            for cand in unassigned:
                score = compute_complementary_skill_score(current_members + [cand])
                if score > best_score:
                    best_score = score
                    best_stu = cand
            if best_stu is None:
                best_stu = unassigned[0]

            unassigned.remove(best_stu)
            if best_stu.student_id not in g.members:
                g.members.append(best_stu.student_id)
            best_stu.group = g
            best_stu.save(update_fields=['group'])
            _recompute_group_metrics(g)

    # Now for remaining unassigned students (if any)
    if unassigned:
        if len(unassigned) >= TARGET_GROUP_SIZE:
            settings_row = SystemSettings.current()
            feature_matrix = build_feature_matrix(unassigned)
            cluster_labels = k_means_cluster(
                feature_matrix,
                target_size=TARGET_GROUP_SIZE,
                random_state=settings_row.kmeans_random_state,
                max_iterations=settings_row.kmeans_max_iterations,
                use_scaler=True,
                include_quality=True,
            )
            ordered = sorted(
                zip(unassigned, cluster_labels),
                key=lambda item: (item[1], -item[0].average_score),
            )
            unassigned_ordered = [s for s, _ in ordered]
        else:
            unassigned_ordered = list(unassigned)

        while unassigned_ordered:
            cohort = unassigned_ordered[:TARGET_GROUP_SIZE]
            unassigned_ordered = unassigned_ordered[TARGET_GROUP_SIZE:]

            next_idx = GroupRepository.count() + 1
            new_group = GroupRepository.create(
                name=_group_name(next_idx),
                members=[s.student_id for s in cohort],
                overall_strengths=overall_strength_of(cohort),
                overall_weaknesses=overall_weakness_of(cohort),
                average_performance=average_performance_of(cohort),
                complementary_skill_score=compute_complementary_skill_score(cohort),
                team_leader=suggest_team_leader_name(cohort),
                learning_recommendation=build_learning_recommendation(cohort),
                recommendations=build_group_recommendations(cohort),
            )
            for s in cohort:
                s.group = new_group
            Student.objects.bulk_update(cohort, ['group'])
            for s in cohort:
                notification_services.notify_students(
                    [s.student_id],
                    'You Have a New Study Group',
                    f'Your AI-matched study group {new_group.name} has been formed.',
                    tone='success',
                    category='groups',
                )
            notification_services.notify_admin(
                'New Study Groups Formed',
                f'{new_group.name} formed.',
                tone='success',
                category='groups',
            )
            notification_services.log_activity('group_generated', detail=f'{new_group.name} formed')

    all_groups = list(GroupRepository.all())
    all_payloads = [build_group_payload(g) for g in all_groups]
    summary = _build_summary(all_payloads, students)
    return all_payloads, summary


@transaction.atomic
def generate_groups(target_size: int = 0) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Idempotent group generation (never wipes existing assignments)."""
    return ensure_groups()


def list_groups(filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """List groups, optionally filtered by name, member department or min performance."""
    filters = filters or {}
    search = (filters.get('search') or '').strip().lower()
    department = (filters.get('department') or '').strip()
    min_performance = filters.get('minPerformance')
    try:
        min_performance = float(min_performance) if min_performance else None
    except (TypeError, ValueError):
        min_performance = None

    matched = []
    for group in list(GroupRepository.all()):
        payload = build_group_payload(group)
        if search and search not in payload['name'].lower():
            continue
        if department and department not in [member['department'] for member in payload['members']]:
            continue
        if min_performance is not None and payload['averagePerformance'] < min_performance:
            continue
        matched.append(payload)
    return matched


def get_group(pk) -> Optional[Dict[str, Any]]:
    group = GroupRepository.get(pk)
    if group is None:
        return None
    return build_group_payload(group)


def update_group(pk, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Rename a group and/or rebuild it around the provided member list."""
    group = GroupRepository.get(pk)
    if group is None:
        return None

    fields: Dict[str, Any] = {}
    if 'name' in data:
        fields['name'] = data['name'].strip()

    if 'members' in data:
        member_ids = [str(member_id) for member_id in data['members']]
        members: List[Student] = []
        for member_id in member_ids:
            member = StudentRepository.get_by_student_id(member_id)
            if member is not None:
                members.append(member)

        if members:
            fields.update({
                'members': [member.student_id for member in members],
                'overall_strengths': overall_strength_of(members),
                'overall_weaknesses': overall_weakness_of(members),
                'average_performance': average_performance_of(members),
                'complementary_skill_score': compute_complementary_skill_score(members),
                'team_leader': suggest_team_leader_name(members),
                'learning_recommendation': build_learning_recommendation(members),
                'recommendations': build_group_recommendations(members),
            })
            Student.objects.filter(group=group).update(group=None)
            for member in members:
                member.group = group
            Student.objects.bulk_update(members, ['group'])

    GroupRepository.update(group, **fields)
    logger.info('Group updated :: group=%s', group.pk)
    return build_group_payload(group)


def delete_group(pk) -> bool:
    group = GroupRepository.get(pk)
    if group is None:
        return False
    GroupRepository.delete(group)
    logger.info('Group deleted :: group=%s', pk)
    notification_services.log_activity('group_deleted', detail=f'{group.name} removed')
    return True


def delete_all_groups() -> int:
    count = GroupRepository.delete_all()
    logger.info('All groups deleted :: count=%s', count)
    notification_services.log_activity('group_deleted', detail=f'All {count} groups removed')
    return count


# ---------------------------------------------------------------------------
# Student-facing group collaboration (chat + shared resources)
# ---------------------------------------------------------------------------

_STUDENT_DISPLAY_NAMES = {'Database': 'Database Management'}


def _student_subject(subject: str) -> str:
    return _STUDENT_DISPLAY_NAMES.get(subject, subject)


def _chat_payload(message: ChatMessage, current_student: Student) -> Dict[str, Any]:
    return {
        'id': message.pk,
        'sender': message.sender.full_name,
        'senderId': message.sender.student_id,
        'isSelf': message.sender.pk == current_student.pk,
        'message': message.message,
        'createdAt': message.created_at.isoformat(),
    }


def _resource_payload(resource: SharedResource, request=None) -> Dict[str, Any]:
    file_url = None
    if resource.file:
        url = resource.file.url
        file_url = request.build_absolute_uri(url) if request is not None else url
    return {
        'id': resource.pk,
        'title': resource.title,
        'resourceType': resource.resource_type,
        'url': resource.url,
        'fileName': resource.file.name.rsplit('/', 1)[-1] if resource.file else None,
        'fileUrl': file_url,
        'uploader': resource.uploader.full_name,
        'createdAt': resource.created_at.isoformat(),
    }


def _group_member_payload(member: Student, current_student: Student) -> Dict[str, Any]:
    strengths = member.strengths or []
    weaknesses = member.weaknesses or []
    return {
        'studentId': member.student_id,
        'name': member.full_name,
        'department': member.department,
        'avatar': member.full_name[:1].upper() if member.full_name else '?',
        'strongSubjects': [_student_subject(subject) for subject in strengths],
        'weakSubjects': [_student_subject(subject) for subject in weaknesses],
        'averageScore': round(member.average_score),
        'learningPreference': member.learning_preference,
        'availability': member.availability,
        'isSelf': member.pk == current_student.pk,
    }


def _group_activity(group: StudyGroup) -> List[Dict[str, Any]]:
    activity: List[Dict[str, Any]] = []
    for message in group.chat_messages.all()[:6]:
        activity.append({
            'type': 'message',
            'actor': message.sender.full_name,
            'text': 'posted a message',
            'detail': message.message,
            'createdAt': message.created_at.isoformat(),
        })
    for resource in group.resources.all()[:6]:
        activity.append({
            'type': 'resource',
            'actor': resource.uploader.full_name,
            'text': 'shared a resource',
            'detail': resource.title,
            'createdAt': resource.created_at.isoformat(),
        })
    activity.sort(key=lambda item: item['createdAt'], reverse=True)
    return activity[:12]


def _weakness_coverage(group: StudyGroup, members: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Map each group weakness to whether a member is strong in that subject."""
    coverage: List[Dict[str, Any]] = []
    for subject in (group.overall_weaknesses or []):
        display_subject = _student_subject(subject)
        covered_by = [
            member['name']
            for member in members
            if display_subject in (member.get('strongSubjects') or [])
        ]
        coverage.append({
            'subject': display_subject,
            'covered': bool(covered_by),
            'coveredBy': covered_by,
        })
    return coverage


def profile_complete(student: Student) -> bool:
    """A student profile is group-ready when every core subject has a score and at least one score is non-zero."""
    if missing_scores(student):
        return False
    return any(score > 0 for score in student.scores.values())


def _waiting_message(student: Student, eligible_count: int) -> str:
    """Return status message for unassigned state."""
    if not profile_complete(student):
        return 'Complete your academic profile to join a study group.'
    return 'Waiting for group placement.'


def ensure_groups_if_needed() -> bool:
    """Run the group placement pipeline if unassigned eligible students exist."""
    unassigned = [s for s in eligible_students() if s.group_id is None]
    if not unassigned:
        return False
    ensure_groups()
    return True


def group_status(student: Student) -> Dict[str, Any]:
    """Readiness payload that drives the group-formation states on the frontend."""
    if student.group is None and profile_complete(student):
        assign_student_to_group(student)
        student.refresh_from_db()

    eligible = len(eligible_students())
    group_payload = student_group(student)
    return {
        'profileComplete': profile_complete(student),
        'eligibleStudents': eligible,
        'minimumRequired': 1,
        'groupsGenerated': GroupRepository.count() > 0,
        'group': group_payload,
        'message': None if group_payload is not None else _waiting_message(student, eligible),
    }


def my_group(student: Student, request=None) -> Dict[str, Any]:
    """Return the spec-compliant /api/groups/my-group/ payload."""
    if student.group is None and profile_complete(student):
        assign_student_to_group(student)
        student.refresh_from_db()

    if student.group is None:
        return {
            'assigned': False,
            'message': _waiting_message(student, 0),
        }

    group = student.group
    members_payload = []
    for student_id in group.members:
        member = StudentRepository.get_by_student_id(student_id)
        if member is None:
            continue
        members_payload.append({
            'id': member.pk,
            'studentId': member.student_id,
            'name': member.full_name,
            'department': member.department,
            'strengths': [_student_subject(s) for s in (member.strengths or [])],
            'weaknesses': [_student_subject(s) for s in (member.weaknesses or [])],
            'averageScore': round(member.average_score),
            'isSelf': member.pk == student.pk,
        })

    return {
        'assigned': True,
        'group': {
            'id': group.pk,
            'name': group.name,
            'compatibilityScore': round(group.complementary_skill_score),
            'memberCount': len(members_payload),
            'members': members_payload,
            'overallStrengths': [_student_subject(s) for s in (group.overall_strengths or [])],
            'overallWeaknesses': [_student_subject(s) for s in (group.overall_weaknesses or [])],
            'averagePerformance': round(group.average_performance),
            'teamLeader': group.team_leader,
            'learningRecommendation': group.learning_recommendation,
        },
    }


@transaction.atomic
def generate_for_student(student: Student) -> Dict[str, Any]:
    """Form study groups from the student's side and return a result payload."""
    if not profile_complete(student):
        raise exceptions.ValidationError('Complete your academic profile to join a study group.')

    if student.group is not None:
        return {'generated': False, 'assigned': True, 'group': student_group(student)}

    assign_student_to_group(student)
    student.refresh_from_db()
    return {'generated': True, 'assigned': True, 'group': student_group(student)}


def student_group(student: Student, request=None) -> Optional[Dict[str, Any]]:
    """Build the collaboration payload for the student's assigned group."""
    group = student.group
    if group is None:
        return None

    members = []
    for student_id in group.members:
        member = StudentRepository.get_by_student_id(student_id)
        if member is None:
            continue
        members.append(_group_member_payload(member, student))

    created_at = group.created_at
    if created_at is not None and created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)

    return {
        'id': str(group.pk),
        'name': group.name,
        'members': members,
        'overallStrengths': [_student_subject(subject) for subject in (group.overall_strengths or [])],
        'overallWeaknesses': [_student_subject(subject) for subject in (group.overall_weaknesses or [])],
        'weaknessCoverage': _weakness_coverage(group, members),
        'averagePerformance': round(group.average_performance),
        'complementarySkillScore': round(group.complementary_skill_score),
        'teamLeader': group.team_leader,
        'learningRecommendation': group.learning_recommendation,
        'chat': [_chat_payload(message, student) for message in group.chat_messages.all()],
        'resources': [_resource_payload(resource, request) for resource in group.resources.all()],
        'activity': _group_activity(group),
        'createdAt': created_at.astimezone(timezone.utc).isoformat() if created_at else None,
    }


def send_chat_message(student: Student, message: str) -> Optional[Dict[str, Any]]:
    """Persist a group chat message and notify the other members."""
    group = student.group
    if group is None:
        return None

    record = ChatMessage.objects.create(group=group, sender=student, message=message)
    member_ids = [member_id for member_id in group.members if member_id != student.student_id]
    notification_services.notify_students(
        member_ids,
        'New Message in Your Study Group',
        f'{student.full_name} posted a message in {group.name}.',
        tone='info',
        category='groups',
    )
    logger.info('Group chat message sent :: group=%s sender=%s', group.pk, student.student_id)
    return _chat_payload(record, student)


def list_group_resources(student: Student, request=None) -> List[Dict[str, Any]]:
    """Resources shared with the student's study group."""
    group = student.group
    if group is None:
        return []
    return [_resource_payload(resource, request) for resource in group.resources.all()]


def share_group_resource(student: Student, data: Dict[str, Any], request=None) -> Optional[Dict[str, Any]]:
    """Persist a resource shared with the group and notify the other members."""
    group = student.group
    if group is None:
        return None

    record = SharedResource.objects.create(
        group=group,
        uploader=student,
        title=data['title'],
        resource_type=data.get('resourceType') or 'Other',
        url=(data.get('url') or '').strip(),
        file=data.get('file') or None,
    )
    member_ids = [member_id for member_id in group.members if member_id != student.student_id]
    notification_services.notify_students(
        member_ids,
        'New Resource Shared',
        f'{student.full_name} shared "{record.title}" in {group.name}.',
        tone='info',
        category='groups',
    )
    logger.info('Group resource shared :: group=%s uploader=%s title=%s', group.pk, student.student_id, record.title)
    return _resource_payload(record, request)
