"""Repository layer for student persistence and queries.

Keeps all ``Student`` ORM access behind one interface so services and views
never touch the query set directly.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from django.db import transaction

from students.models import Student


class StudentRepository:
    """Data access for :class:`students.models.Student`."""

    @staticmethod
    def all() -> list:
        return list(Student.objects.all())

    @staticmethod
    def count() -> int:
        return Student.objects.count()

    @staticmethod
    def get(pk: int) -> Optional[Student]:
        try:
            return Student.objects.get(pk=pk)
        except Student.DoesNotExist:
            return None

    @staticmethod
    def get_by_student_id(student_id: str) -> Optional[Student]:
        try:
            return Student.objects.get(student_id=student_id)
        except Student.DoesNotExist:
            return None

    @staticmethod
    def get_by_email(email: str) -> Optional[Student]:
        try:
            return Student.objects.get(email__iexact=email.strip())
        except Student.DoesNotExist:
            return None

    @staticmethod
    def exists_by_student_id(student_id: str) -> bool:
        return Student.objects.filter(student_id__iexact=student_id).exists()

    @staticmethod
    def exists_by_email(email: str) -> bool:
        return Student.objects.filter(email__iexact=email).exists()

    @staticmethod
    @transaction.atomic
    def create(
        student_id: str,
        full_name: str,
        email: str,
        password: str,
        department: str,
        year: str,
        section: str,
        scores: Dict[str, float],
        learning_preference: str,
        availability: str,
    ) -> Student:
        student = Student(
            student_id=student_id,
            full_name=full_name,
            email=email,
            department=department,
            year=year,
            section=section,
            learning_preference=learning_preference,
            availability=availability,
        )
        student.set_password(password)
        for subject, value in scores.items():
            student.set_score(subject, value)
        student.save()
        student.recompute_profile()
        return student

    @staticmethod
    @transaction.atomic
    def update(student: Student, **fields: Any) -> Student:
        """Apply provided fields and recompute derived academic data."""
        scores = fields.pop('scores', None)
        password = fields.pop('password', None)

        for key, value in fields.items():
            if hasattr(student, key):
                setattr(student, key, value)

        if scores:
            for subject, value in scores.items():
                student.set_score(subject, value)

        if password:
            student.set_password(password)

        student.save()
        student.recompute_profile()
        return student

    @staticmethod
    @transaction.atomic
    def delete(student: Student) -> None:
        student.delete()

    @staticmethod
    @transaction.atomic
    def create_many(rows: List[Dict[str, Any]]) -> List[Student]:
        """Bulk-create students from cleaned CSV rows.

        Each row is ``{student_id, name, email, department, year, section,
        scores, password}``. Existing IDs/emails are skipped. Uses a single
        ``bulk_create`` followed by one ``bulk_update`` so a large upload is
        committed in O(1) round trips instead of one save per student.
        """
        existing_ids = set(
            Student.objects.filter(student_id__in=[row['student_id'] for row in rows]).values_list('student_id', flat=True)
        )
        existing_emails = set(
            Student.objects.filter(email__in=[row['email'] for row in rows]).values_list('email', flat=True)
        )

        instances: List[Student] = []
        for row in rows:
            student_id = row['student_id']
            email = row['email']
            if student_id in existing_ids or email.lower() in {item.lower() for item in existing_emails}:
                continue
            student = Student(
                student_id=student_id,
                full_name=row['name'],
                email=email,
                department=row.get('department', 'Computer Science'),
                year=row.get('year', '1st Year'),
                section=row.get('section', 'A'),
                learning_preference=row.get('learning_preference', 'Mixed'),
                availability=row.get('availability', 'Morning'),
            )
            student.set_password(row.get('password', '') or '')
            for subject, value in (row.get('scores', {}) or {}).items():
                student.set_score(subject, value)
            instances.append(student)

        if not instances:
            return []

        Student.objects.bulk_create(instances, ignore_conflicts=True)

        created = list(Student.objects.filter(student_id__in=[instance.student_id for instance in instances]))
        for student in created:
            student.recompute_profile(save=False)
        Student.objects.bulk_update(
            created,
            ['strengths', 'weaknesses', 'average_score', 'updated_at'],
        )
        return created

    @staticmethod
    def unassigned() -> list:
        return list(Student.objects.filter(group__isnull=True))
