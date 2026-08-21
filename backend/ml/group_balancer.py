"""Group size balancing and complementary-skill scoring.

After clustering + complementary matching the groups may still have uneven
sizes (some oversized, some undersized). This module rebalances so every group
is as close to ``target_size`` as the population allows, then computes the
complementary skill score and aggregate strength/weakness summaries that are
stored on each generated group.
"""
from __future__ import annotations

from .strength_analysis import subject_coverage
from .utils import SUBJECTS, average_score


def _move_to_smallest(groups: list[list], source_index: int, member, minimum_size: int) -> bool:
    """Move ``member`` from ``source_index`` into the smallest smaller group."""
    smallest_index = -1
    smallest_size = float('inf')

    for index, group in enumerate(groups):
        if index == source_index:
            continue
        if len(group) < smallest_size:
            smallest_size = len(group)
            smallest_index = index

    if smallest_index != -1 and smallest_size < minimum_size:
        groups[source_index] = [candidate for candidate in groups[source_index] if candidate.id != member.id]
        groups[smallest_index].append(member)
        return True
    return False


def balance_groups(groups: list[list], _target_size: int) -> list[list]:
    """Even out group sizes around the mean, preserving skill composition.

    Only the outermost students (weakest contribution to the source group) are
    moved, and only when the destination is strictly smaller than the average,
    so complementary spread is disturbed as little as possible.
    """
    non_empty = [group for group in groups if group]
    if not non_empty:
        return non_empty

    total = sum(len(group) for group in non_empty)
    group_count = len(non_empty)
    minimum_size = total // group_count
    maximum_size = -(-total // group_count)

    rebalanced = True
    guard = 0
    while rebalanced and guard < 100:
        rebalanced = False
        guard += 1

        for index, group in enumerate(non_empty):
            if len(group) <= maximum_size:
                continue

            candidates = sorted(
                group,
                key=lambda member: (len(group) - len(_strengths_of(member))),
                reverse=True,
            )

            for candidate in candidates:
                if len(non_empty[index]) <= maximum_size:
                    break
                if _move_to_smallest(non_empty, index, candidate, minimum_size):
                    rebalanced = True

    return [group for group in non_empty if group]


def _strengths_of(member):
    stored = getattr(member, 'strengths', None)
    if stored:
        return list(stored)
    from .strength_analysis import detect_strengths  # local import to avoid a cycle

    return detect_strengths(member.scores)


def compute_complementary_skill_score(members) -> int:
    """0-100 score rewarding skill coverage, diversity and balanced sizing."""
    if not members:
        return 0

    coverage = subject_coverage(members)
    covered = sum(1 for value in coverage.values() if value)
    coverage_score = (covered / max(len(SUBJECTS), 1)) * 60

    distinct_strengths = len({subject for member in members for subject in _strengths_of(member)})
    diversity_score = min(distinct_strengths / max(len(members) * 3, 1), 1) * 25

    size_score = 15.0 if len(members) == 5 else (len(members) / 5.0) * 15.0

    return min(100, round(coverage_score + diversity_score + size_score))


def overall_strength_of(members) -> list[str]:
    """Unique subjects covered as strengths across the group (max 4)."""
    seen: list[str] = []
    for member in members:
        for subject in _strengths_of(member):
            if subject not in seen:
                seen.append(subject)
    return seen[:4]


def overall_weakness_of(members) -> list[str]:
    """Unique subjects flagged as weaknesses across the group (max 4)."""
    seen: list[str] = []
    for member in members:
        weaknesses = getattr(member, 'weaknesses', None) or []
        for subject in weaknesses:
            if subject not in seen:
                seen.append(subject)
    return seen[:4]


def average_performance_of(members) -> int:
    """Mean of per-member average scores."""
    if not members:
        return 0
    return round(sum(average_score(member.scores) for member in members) / len(members))
