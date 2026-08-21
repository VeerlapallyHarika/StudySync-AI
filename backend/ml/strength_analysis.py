"""Strength and weakness detection for academic profiles.

A student is considered an *expert* (strength) in a subject when their score is
at or above ``STRENGTH_THRESHOLD`` and a *support needed* (weakness) when it is
at or below ``WEAKNESS_THRESHOLD``. Thresholds are kept configurable so callers
can tune behaviour without touching the clustering code.
"""
from __future__ import annotations

from .utils import SUBJECTS

STRENGTH_THRESHOLD = 75.0
WEAKNESS_THRESHOLD = 50.0
STRENGTH_LIMIT = 3
WEAKNESS_LIMIT = 3


def detect_strengths(scores: dict[str, float]) -> list[str]:
    """Top subjects the student excels at (score >= threshold, best first)."""
    return [
        subject
        for subject, _ in sorted(
            ((subject, score) for subject, score in scores.items() if score >= STRENGTH_THRESHOLD),
            key=lambda item: item[1],
            reverse=True,
        )
    ][:STRENGTH_LIMIT]


def detect_weaknesses(scores: dict[str, float]) -> list[str]:
    """Subjects needing the most support (score <= threshold, weakest first)."""
    return [
        subject
        for subject, _ in sorted(
            ((subject, score) for subject, score in scores.items() if score <= WEAKNESS_THRESHOLD),
            key=lambda item: item[1],
        )
    ][:WEAKNESS_LIMIT]


def is_expert_in(student, subject: str) -> bool:
    """Whether a student is a strength/expert for a given subject."""
    return float(student.scores.get(subject, 0.0)) >= STRENGTH_THRESHOLD


def strong_subjects_of(student) -> list[str]:
    """Strengths stored on the student, or freshly detected when empty."""
    stored = getattr(student, 'strengths', None)
    if stored:
        return list(stored)
    return detect_strengths(student.scores)


def weak_subjects_of(student) -> list[str]:
    """Weaknesses stored on the student, or freshly detected when empty."""
    stored = getattr(student, 'weaknesses', None)
    if stored:
        return list(stored)
    return detect_weaknesses(student.scores)


def subject_coverage(members) -> dict[str, bool]:
    """Which of the core subjects are covered by at least one member."""
    coverage: dict[str, bool] = {}
    for subject in SUBJECTS:
        coverage[subject] = any(is_expert_in(member, subject) for member in members)
    return coverage
