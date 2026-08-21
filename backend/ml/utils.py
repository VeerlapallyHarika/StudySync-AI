"""Shared helpers for the StudySync AI ML pipeline."""
from __future__ import annotations

SUBJECTS: list[str] = [
    'Mathematics',
    'Physics',
    'Programming',
    'Database',
    'Operating Systems',
]


def normalize_scores(scores: dict[str, float]) -> dict[str, float]:
    """Min-max normalize a score dictionary to a 0-100 scale."""
    if not scores:
        return {}

    values = [float(value) for value in scores.values()]
    minimum = min(values)
    maximum = max(values)
    spread = maximum - minimum or 1

    return {
        subject: round(((float(value) - minimum) / spread) * 100, 2)
        for subject, value in scores.items()
    }


def top_subjects(scores: dict[str, float], limit: int = 3) -> list[str]:
    return [subject for subject, _ in sorted(scores.items(), key=lambda item: item[1], reverse=True)[:limit]]


def bottom_subjects(scores: dict[str, float], limit: int = 3) -> list[str]:
    return [subject for subject, _ in sorted(scores.items(), key=lambda item: item[1])[:limit]]


def average_score(scores: dict[str, float]) -> int:
    if not scores:
        return 0
    return round(sum(float(value) for value in scores.values()) / len(scores))


def average_score_of(students) -> int:
    if not students:
        return 0
    return round(sum(average_score(student.scores) for student in students) / len(students))
