"""Data preprocessing for the StudySync AI clustering pipeline.

Responsibilities
----------------
- Coerce and clamp raw scores to a valid ``0-100`` range.
- Guarantee every core subject is present before feature building.
- Infer a learning preference from academic strengths.
- Build clean, ready-to-consume dictionaries for downstream ML modules.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from .utils import SUBJECTS

STRENGTH_CUTOFF = 75.0


def clean_score(value: Any) -> float:
    """Coerce a raw value to a float and clamp it into ``[0, 100]``."""
    try:
        score = float(value)
    except (TypeError, ValueError):
        score = 0.0
    return min(100.0, max(0.0, score))


def clean_scores(scores: Optional[Dict[str, Any]]) -> Dict[str, float]:
    """Normalize a score mapping so every subject key is present and valid."""
    source = scores or {}
    return {subject: clean_score(source.get(subject)) for subject in SUBJECTS}


def clean_student_dict(row: Dict[str, Any]) -> Dict[str, Any]:
    """Return a cleaned student dict ready for clustering."""
    return {
        'id': row.get('id'),
        'name': row.get('name', ''),
        'department': row.get('department', ''),
        'year': row.get('year', ''),
        'section': row.get('section', ''),
        'scores': clean_scores(row.get('scores') or {}),
    }


def infer_learning_preference(scores: Dict[str, float]) -> str:
    """Infer one of ``Practical`` / ``Theory`` / ``Mixed`` from strengths."""
    strengths = [subject for subject, score in (scores or {}).items() if score >= STRENGTH_CUTOFF]
    if 'Programming' in strengths and 'Database' in strengths:
        return 'Practical'
    if 'Mathematics' in strengths and 'Physics' in strengths:
        return 'Theory'
    return 'Mixed'
