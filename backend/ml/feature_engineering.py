"""Feature engineering for the StudySync AI clustering pipeline.

Responsibilities
----------------
- Normalize raw academic scores onto a comparable 0-100 scale.
- Build numeric feature vectors (one fixed-dimension vector per student).
- Compute aggregate score statistics used by the rest of the pipeline.

All score helpers accept plain ``dict`` values so they can be reused by the
frontend mirror module (``src/ml/featureEngineering.ts``) with identical
semantics.
"""
from __future__ import annotations

from .utils import SUBJECTS, normalize_scores


def build_feature_vector(scores: dict[str, float]) -> list[float]:
    """Return a normalized feature vector in fixed subject order.

    The subject order is defined by ``ml.utils.SUBJECTS`` so every student is
    mapped onto the same dimensions before clustering.
    """
    normalized = normalize_scores(scores)
    return [float(normalized.get(subject, 0.0)) for subject in SUBJECTS]


def build_feature_matrix(students) -> list[list[float]]:
    """Build a feature matrix (list of rows) for a collection of students."""
    return [build_feature_vector(student.scores) for student in students]


def build_student_features(student) -> list[float]:
    """Backward-compatible alias used by older pipeline code."""
    return build_feature_vector(student.scores)


def average_score(scores: dict[str, float]) -> int:
    """Mean of a student's raw scores (0-100), rounded."""
    if not scores:
        return 0
    return round(sum(float(value) for value in scores.values()) / len(scores))


def average_score_of(students) -> int:
    """Mean of per-student average scores across a collection."""
    if not students:
        return 0
    return round(sum(average_score(student.scores) for student in students) / len(students))
