"""Clustering and complementary matching for StudySync AI.

Pipeline stage
--------------
1. ``k_means_cluster`` runs the actual clustering on preprocessed feature
   vectors using scikit-learn's ``KMeans`` (with deterministic initialisation
   for reproducible results).
2. ``complementary_match`` places students so that every group receives a
   distinct skill spread: subjects are handled one at a time and each group is
   seeded with an expert for that subject before generic students are added.

Design rules (Complementary Matching Rules)
-------------------------------------------
- Students with the same strength are never massed into one group.
- Every group tries to contain one expert per core subject when possible.
- Group sizes are kept as close to ``target_size`` as the population allows
  (final rebalancing happens in ``group_balancer.balance_groups``).
"""
from __future__ import annotations

from typing import Optional

import numpy as np
from sklearn.cluster import KMeans

from .quality import evaluate_clustering, standardize_matrix
from .strength_analysis import is_expert_in
from .utils import SUBJECTS


def recommended_group_count(student_count: int, target_size: int = 4, minimum_size: int = 3) -> int:
    """Number of groups so every group holds between 3 and 4 students.

    The number of groups ``k`` must satisfy ``ceil(n / target_size) <= k <=
    floor(n / minimum_size)``. The smallest valid ``k`` (largest groups) is
    preferred so the population is packed into as few groups as possible while
    keeping sizes inside the ``[3, 4]`` window. When the population cannot be
    split that way (e.g. fewer than 6 students) a single group is returned.
    """
    if student_count <= 0:
        return 0
    if student_count <= target_size:
        return 1

    min_groups = -(-student_count // target_size)
    max_groups = student_count // minimum_size

    return min(max_groups, min_groups)


class ClusterLabels(list):
    """A list of cluster labels that can carry a quality payload.

    Behaves exactly like a plain ``list`` (length, indexing, sorting) but also
    exposes an optional ``quality`` dict describing K, inertia, silhouette and
    group-size bounds for the run that produced it.
    """

    quality: Optional[dict] = None


def k_means_cluster(
    feature_rows: list[list[float]],
    cluster_count: Optional[int] = None,
    target_size: int = 4,
    random_state: int = 42,
    max_iterations: int = 300,
    use_scaler: bool = True,
    include_quality: bool = False,
) -> list[int]:
    """Cluster feature rows and return a label per row.

    Uses ``KMeans(n_init='auto', init='k-means++')`` from scikit-learn so the
    frontend's pure-TS fallback (``src/ml/kmeans.ts``) can be swapped in and
    produce the same architecture end to end.

    When ``cluster_count`` is omitted it is derived from ``target_size``.
    With ``use_scaler`` enabled the feature matrix is standardized via
    ``StandardScaler`` before fitting so every dimension contributes equally.
    With ``include_quality`` the returned labels carry a ``.quality`` attribute
    describing K, inertia, silhouette and group-size bounds.
    """
    points = np.asarray(feature_rows, dtype=np.float64)
    if points.size == 0 or len(points) == 0:
        return []

    if cluster_count is None:
        cluster_count = recommended_group_count(len(points), target_size)
    cluster_count = max(1, min(int(cluster_count), len(points)))

    if cluster_count == 1:
        labels = ClusterLabels([0] * len(points))
        labels.quality = evaluate_clustering(points.tolist(), list(labels))
        return labels

    model = KMeans(
        n_clusters=cluster_count,
        init='k-means++',
        n_init='auto',
        max_iter=max_iterations,
        random_state=random_state,
    )
    if use_scaler:
        model.fit(standardize_matrix(points))
    else:
        model.fit(points)
    labels = ClusterLabels([int(label) for label in model.labels_])
    if include_quality:
        labels.quality = evaluate_clustering(points.tolist(), list(labels))
    return labels


def _candidate_pool(students, assigned: set[int], subject: str):
    """Sorted, unassigned students who are experts in ``subject``."""
    return [
        (index, student)
        for index, student in enumerate(students)
        if index not in assigned and is_expert_in(student, subject)
    ]


def complementary_match(students, cluster_labels: list[int], target_size: int):
    """Assign students into balanced, skill-complementary groups.

    Returns a list of member lists (one per group). Groups with no members are
    dropped. The algorithm:

    1. Seed each group with one expert per subject, rotating across groups so a
       single subject's experts are spread out.
    2. Fill remaining capacity while preferring each student's own cluster to
       preserve academic similarity, then any group with free space.
    """
    group_count = max(1, min(recommended_group_count(len(students), target_size), len(students)))
    groups: list[list] = [[] for _ in range(group_count)]
    assigned: set[int] = set()

    if len(students) == 0:
        return [group for group in groups if group]

    for subject_offset, subject in enumerate(SUBJECTS):
        pool = _candidate_pool(students, assigned, subject)
        pool.sort(key=lambda item: (item[1].scores.get(subject, 0.0),), reverse=True)

        for step in range(group_count):
            if not pool:
                break
            group_index = (subject_offset + step) % group_count
            if len(groups[group_index]) >= target_size:
                continue
            candidate_index, candidate = pool.pop(0)
            groups[group_index].append(candidate)
            assigned.add(candidate_index)

    remaining = [
        (index, student)
        for index, student in enumerate(students)
        if index not in assigned
    ]
    remaining.sort(key=lambda item: cluster_labels[item[0]] if cluster_labels else 0)

    for index, student in remaining:
        best_group = _best_remaining_group(
            groups,
            target_size,
            cluster_labels[index] if cluster_labels else 0,
        )
        groups[best_group].append(student)

    return [group for group in groups if group]


def _best_remaining_group(groups: list[list], target_size: int, cluster_label: int) -> int:
    """Pick the group with the lowest cost (own cluster + capacity balance)."""
    best_index = -1
    best_cost = float('inf')

    for group_index, group in enumerate(groups):
        if len(group) >= target_size:
            continue
        cluster_penalty = 0 if group_index == cluster_label else 10
        cost = cluster_penalty + len(group)
        if cost < best_cost:
            best_cost = cost
            best_index = group_index

    if best_index == -1:
        return min(range(len(groups)), key=lambda index: len(groups[index]))
    return best_index
