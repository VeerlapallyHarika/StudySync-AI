"""Clustering quality metrics, automatic K selection and data hygiene.

Production ML additions for the StudySync AI pipeline:

- :func:`standardize_matrix` applies scikit-learn's ``StandardScaler`` so every
  feature dimension contributes equally before K-Means.
- :func:`elbow_inertias` / :func:`optimal_k_by_elbow` implement the elbow
  method for automatic K selection.
- :func:`silhouette_value` reports the silhouette score for a fitted labelling.
- :func:`evaluate_clustering` bundles K, inertia, silhouette and group-size
  bounds into one quality payload.
- :func:`detect_duplicates` and :func:`missing_scores` surface data hygiene
  problems before clustering.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

from .utils import SUBJECTS


def standardize_matrix(feature_rows: List[List[float]]) -> np.ndarray:
    """Center and scale feature rows to unit variance.

    ``StandardScaler`` produces a degenerate (all-zero) matrix when every
    feature has zero variance (e.g. a cohort of identical score vectors); we
    fall back to the raw matrix in that case so downstream code never divides
    by zero.
    """
    matrix = np.asarray(feature_rows, dtype=np.float64)
    if matrix.size == 0:
        return matrix

    scaler = StandardScaler()
    scaled = scaler.fit_transform(matrix)
    if not np.isfinite(scaled).all() or np.allclose(scaled, 0.0):
        return matrix
    return scaled


def elbow_inertias(
    feature_rows: List[List[float]],
    max_k: int = 10,
    random_state: int = 42,
    max_iterations: int = 300,
) -> List[Dict[str, Any]]:
    """Run K-Means for ``k`` in ``1..max_k`` and return the inertia curve.

    Each entry is ``{'k': k, 'inertia': inertia}`` ordered by ``k``. Inertia is
    the within-cluster sum of squares used by the elbow method.
    """
    matrix = np.asarray(feature_rows, dtype=np.float64)
    sample_count = len(matrix)
    if sample_count == 0:
        return []

    results: List[Dict[str, Any]] = []
    for k in range(1, max(1, min(int(max_k), sample_count)) + 1):
        if k == 1:
            results.append({'k': 1, 'inertia': _single_cluster_inertia(matrix)})
            continue
        model = KMeans(
            n_clusters=k,
            init='k-means++',
            n_init='auto',
            max_iter=max_iterations,
            random_state=random_state,
        )
        model.fit(matrix)
        results.append({'k': k, 'inertia': float(model.inertia_)})
    return results


def _single_cluster_inertia(matrix: np.ndarray) -> float:
    centroid = matrix.mean(axis=0)
    return float(np.sum((matrix - centroid) ** 2))


def optimal_k_by_elbow(
    feature_rows: List[List[float]],
    max_k: int = 10,
    random_state: int = 42,
    max_iterations: int = 300,
) -> int:
    """Pick ``k`` at the steepest bend of the inertia curve.

    Uses the maximum perpendicular-distance heuristic: the elbow is the point
    on the curve farthest from the straight line joining the first and last
    curve points. Falls back to 1 when there is nothing to evaluate.
    """
    curve = elbow_inertias(feature_rows, max_k, random_state, max_iterations)
    if len(curve) <= 2:
        return 1

    ks = np.array([item['k'] for item in curve], dtype=np.float64)
    inertias = np.array([item['inertia'] for item in curve], dtype=np.float64)

    first = np.array([ks[0], inertias[0]])
    last = np.array([ks[-1], inertias[-1]])
    line = last - first
    line_norm = float(np.linalg.norm(line))
    if line_norm == 0:
        return 1

    # Perpendicular distance from each curve point to the end-to-end line,
    # computed directly (avoids np.cross vector-dimension pitfalls).
    line_x, line_y = float(line[0]), float(line[1])
    distances: List[float] = []
    for k, inertia in zip(ks, inertias):
        offset_x = float(k) - first[0]
        offset_y = float(inertia) - first[1]
        distances.append(abs(line_x * offset_y - line_y * offset_x) / line_norm)

    best_index = int(np.argmax(distances))
    return int(ks[best_index])


def silhouette_value(feature_rows: List[List[float]], labels: List[int]) -> Optional[float]:
    """Silhouette score for a labelling, or ``None`` when not computable.

    The score is undefined for a single cluster or when every cluster holds one
    sample; those cases return ``None`` instead of raising.
    """
    matrix = np.asarray(feature_rows, dtype=np.float64)
    label_array = np.asarray(labels, dtype=int)
    cluster_count = len(set(label_array.tolist())) if label_array.size else 0
    if matrix.shape[0] < 2 or cluster_count < 2:
        return None
    if any(np.sum(label_array == value) < 2 for value in set(label_array.tolist())):
        return None
    try:
        return float(silhouette_score(matrix, label_array))
    except ValueError:
        return None


def evaluate_clustering(
    feature_rows: List[List[float]],
    labels: List[int],
) -> Dict[str, Any]:
    """Quality payload for a completed clustering run."""
    matrix = np.asarray(feature_rows, dtype=np.float64)
    sample_count = len(matrix)
    unique_labels = sorted(set(labels)) if labels else []
    sizes = [sum(1 for label in labels if label == value) for value in unique_labels]

    inertia = None
    if sample_count:
        inertia = _single_cluster_inertia(matrix)
        if len(unique_labels) > 1:
            inertia = float(
                sum(
                    float(np.sum((matrix[np.asarray(labels) == label] - matrix[np.asarray(labels) == label].mean(axis=0)) ** 2))
                    for label in unique_labels
                )
            )

    return {
        'k': len(unique_labels),
        'sampleCount': sample_count,
        'inertia': inertia,
        'silhouette': silhouette_value(feature_rows, labels),
        'minGroupSize': min(sizes) if sizes else 0,
        'maxGroupSize': max(sizes) if sizes else 0,
    }


def detect_duplicates(students) -> List[Dict[str, Any]]:
    """Flag exact and near-duplicate student profiles.

    A duplicate is reported when two students share the same student ID or
    email (already enforced at the database level, reported for visibility) or
    when two different accounts carry a near-identical score vector plus the
    same name — a strong signal of a double import.
    """
    from .utils import SUBJECTS

    seen_ids: Dict[str, str] = {}
    seen_emails: Dict[str, str] = {}
    seen_profiles: Dict[tuple, str] = {}
    duplicates: List[Dict[str, Any]] = []

    for student in students:
        student_id = getattr(student, 'student_id', None) or ''
        email = (getattr(student, 'email', None) or '').strip().lower()
        name = (getattr(student, 'full_name', None) or '').strip().lower()
        scores = getattr(student, 'scores', None) or {}

        if student_id:
            owner = seen_ids.get(student_id)
            if owner is not None:
                duplicates.append({'kind': 'duplicate_id', 'studentId': student_id, 'owner': owner})
            else:
                seen_ids[student_id] = name or email

        if email:
            owner = seen_emails.get(email)
            if owner is not None:
                duplicates.append({'kind': 'duplicate_email', 'email': email, 'owner': owner})
            else:
                seen_emails[email] = name

        vector = tuple(round(float(scores.get(subject, 0.0)), 1) for subject in SUBJECTS)
        key = (name, vector)
        if name:
            owner = seen_profiles.get(key)
            if owner is not None:
                duplicates.append({'kind': 'duplicate_profile', 'studentId': student_id, 'owner': owner})
            else:
                seen_profiles[key] = student_id

    return duplicates


def missing_scores(student) -> List[str]:
    """Core subjects without a usable score for the given student."""
    scores = getattr(student, 'scores', None) or {}
    missing: List[str] = []
    for subject in SUBJECTS:
        raw = scores.get(subject)
        try:
            value = float(raw)
        except (TypeError, ValueError):
            value = float('nan')
        if not np.isfinite(value):
            missing.append(subject)
    return missing


__all__ = [
    'standardize_matrix',
    'elbow_inertias',
    'optimal_k_by_elbow',
    'silhouette_value',
    'evaluate_clustering',
    'detect_duplicates',
    'missing_scores',
]
