"""Team leader suggestion, learning recommendations and AI insights.

This module turns raw academic data into human-readable, decision-ready
recommendations for both generated groups and individual students:

- :func:`suggest_team_leader` and :func:`leadership_qualities` pick a leader.
- :func:`build_learning_recommendation` produces the group study plan.
- :func:`build_group_recommendations` returns the full structured insight
  payload (skill level, leader + reason, weak/strong areas, meetings).
- :func:`build_student_insights` produces per-student intelligence: learning
  trend, strength/weakness scores, improvement suggestions, resources, a
  suggested peer mentor and study sessions.
"""
from __future__ import annotations

from .group_balancer import overall_strength_of, overall_weakness_of
from .utils import SUBJECTS, average_score

SKILL_LEVELS = ('Excellent', 'Good', 'Fair', 'Needs Support')

RESOURCE_MAP = {
    'Mathematics': 'Interactive problem sets, Khan Academy Calculus & Algebra playlists',
    'Physics': 'Conceptual simulations, Feynman lectures and daily derivation practice',
    'Programming': 'LeetCode/HackerRank daily drills and pair-programming sprints',
    'Database': 'SQL Zoo, schema-design case studies and normalized practice labs',
    'Operating Systems': 'Process/thread visualizers, OSDev tutorials and command-line labs',
}


def suggest_team_leader(members) -> object:
    """Pick the member with the widest strength coverage, then highest average.

    Returns the chosen student object (the caller decides how to serialise the
    name). Falls back to the highest-scoring member when strengths are empty.
    """
    if not members:
        return None

    def key(member):
        strengths = getattr(member, 'strengths', None) or []
        return (len(strengths), average_score(member.scores))

    return sorted(members, key=key, reverse=True)[0]


def suggest_team_leader_name(members) -> str:
    leader = suggest_team_leader(members)
    if leader is None:
        return ''
    return getattr(leader, 'full_name', None) or getattr(leader, 'name', '') or ''


def leader_reason(members) -> str:
    """Explain why the chosen leader stands out."""
    leader = suggest_team_leader(members)
    if leader is None:
        return 'No members in this group yet.'
    strengths = getattr(leader, 'strengths', None) or []
    leader_avg = average_score(leader.scores)
    if leader_avg >= 85 and len(strengths) >= 2:
        return 'Highest average score with balanced, multi-subject strengths.'
    if len(strengths) >= 3:
        return 'Broad subject expertise covering most of the group\u2019s strengths.'
    if leader_avg >= 80:
        return 'Top academic performer with a steady all-round profile.'
    if len(strengths) >= 1:
        return 'Widest subject coverage combined with a strong overall average.'
    return 'Highest overall average score in the group.'


def overall_skill_level(members) -> str:
    """Categorise the group's academic standing into a skill level."""
    if not members:
        return 'Needs Support'
    avg = round(sum(average_score(member.scores) for member in members) / len(members))
    if avg >= 80:
        return 'Excellent'
    if avg >= 70:
        return 'Good'
    if avg >= 50:
        return 'Fair'
    return 'Needs Support'


def strong_area_recommendation(members) -> dict:
    """Suggest how to channel the group's strongest subject."""
    strengths = overall_strength_of(members)
    if not strengths:
        return {'subject': None, 'recommendation': None}
    subject = strengths[0]
    return {
        'subject': subject,
        'recommendation': (
            f'Assign {subject} practice tasks and let strong members mentor '
            f'the rest of the group.'
        ),
    }


def weak_area_recommendation(members) -> dict:
    """Suggest a remediation plan for the group's weakest subject."""
    weaknesses = overall_weakness_of(members)
    if not weaknesses:
        return {'subject': None, 'recommendation': None}
    subject = weaknesses[0]
    experts = [
        getattr(member, 'full_name', None) or getattr(member, 'name', '')
        for member in members
        if subject in (getattr(member, 'strengths', None) or [])
    ]
    mentor = f', led by {", ".join(experts)}' if experts else ''
    return {
        'subject': subject,
        'recommendation': (
            f'Schedule weekly {subject} revision sessions{mentor} until the '
            f'average group score clears 70.'
        ),
    }


def meeting_recommendation(members) -> str:
    """Derive a practical meeting cadence from member availability."""
    if not members:
        return 'No members to schedule yet.'
    availability = [
        getattr(member, 'availability', None)
        for member in members
        if getattr(member, 'availability', None)
    ]
    if not availability:
        return 'Meet twice a week for focused 60-minute study blocks.'
    most_common = max(set(availability), key=availability.count)
    return (
        f'Meet twice a week during {most_common} slots; reserve one session '
        f'for the group\u2019s weakest subject and one for peer review.'
    )


def suggested_improvements(members) -> list[str]:
    """Actionable improvement items for the whole group."""
    items: list[str] = []
    strengths = overall_strength_of(members)
    weaknesses = overall_weakness_of(members)
    if strengths:
        items.append(f'Keep strengthening {", ".join(strengths[:2])} through applied projects.')
    for subject in weaknesses[:2]:
        items.append(f'Dedicate weekly focused practice to {subject}.')
    if len(members) >= 3:
        items.append('Rotate a \u201ctopic lead\u201d each week so every member presents.')
    if not items:
        items.append('Maintain momentum with advanced problem sets and cross-subject projects.')
    return items


def build_group_recommendations(members) -> dict:
    """Full structured recommendation payload for a generated group."""
    return {
        'overallSkillLevel': overall_skill_level(members),
        'recommendedLeader': suggest_team_leader_name(members),
        'leaderReason': leader_reason(members),
        'weakArea': weak_area_recommendation(members),
        'strongArea': strong_area_recommendation(members),
        'meetingRecommendation': meeting_recommendation(members),
        'suggestedImprovements': suggested_improvements(members),
    }


def build_learning_recommendation(members) -> str:
    """Human-readable study recommendation driven by the group's weakest area."""
    if not members:
        return 'No members in this group yet.'

    weaknesses = overall_weakness_of(members)
    if not weaknesses:
        return 'Maintain momentum with advanced problem sets and cross-subject projects.'

    focus_subject = weaknesses[0]
    experts = [
        getattr(member, 'full_name', None) or getattr(member, 'name', '')
        for member in members
        if focus_subject in (getattr(member, 'strengths', None) or [])
    ]

    if experts:
        mentor = f' {", ".join(experts)} can lead peer tutoring sessions.'
    else:
        mentor = ' Pair with an external tutor or focused workshops.'

    return f'Prioritize {focus_subject} support with weekly peer study blocks.{mentor}'


def leadership_qualities(members) -> dict[str, str]:
    """Suggested leader plus the top co-lead candidates."""
    leader = suggest_team_leader(members)
    if leader is None:
        return {'suggestedLeader': '', 'coLeadCandidates': 'None'}

    leader_id = getattr(leader, 'id', None)
    co_leads = sorted(
        (member for member in members if getattr(member, 'id', None) != leader_id),
        key=lambda member: average_score(member.scores),
        reverse=True,
    )[:2]

    names = [
        getattr(member, 'full_name', None) or getattr(member, 'name', '')
        for member in co_leads
    ]
    return {
        'suggestedLeader': getattr(leader, 'full_name', None) or getattr(leader, 'name', ''),
        'coLeadCandidates': ', '.join(names) or 'None',
    }


def format_subjects(subjects) -> str:
    if not subjects:
        return 'Balanced'
    return ', '.join(subjects)


# ---------------------------------------------------------------------------
# Individual student insights
# ---------------------------------------------------------------------------

def strength_score(scores: dict) -> int:
    """Average of a student's above-threshold subject scores."""
    from .strength_analysis import STRENGTH_THRESHOLD

    strong = [value for value in (scores or {}).values() if value >= STRENGTH_THRESHOLD]
    if not strong:
        return 0
    return round(sum(strong) / len(strong))


def weakness_score(scores: dict) -> int:
    """Average of a student's at-or-below-threshold subject scores."""
    from .strength_analysis import WEAKNESS_THRESHOLD

    weak = [value for value in (scores or {}).values() if value <= WEAKNESS_THRESHOLD]
    if not weak:
        return 0
    return round(sum(weak) / len(weak))


def learning_trend(scores: dict) -> str:
    """Label the student's overall trajectory from raw scores."""
    if not scores:
        return 'Stable'
    values = list(scores.values())
    avg = sum(values) / len(values)
    above = sum(1 for value in values if value >= 75)
    below = sum(1 for value in values if value < 50)
    if avg >= 80 and above >= len(values) - 1:
        return 'Excelling'
    if below == 0 and avg >= 65:
        return 'Improving'
    if below >= 2:
        return 'Needs Attention'
    return 'Stable'


def improvement_suggestions(student) -> list[str]:
    """Concrete per-subject suggestions for a student."""
    suggestions: list[str] = []
    weaknesses = getattr(student, 'weaknesses', None) or []
    scores = student.scores or {}
    for subject in weaknesses[:3]:
        score = scores.get(subject, 0)
        if score < 40:
            suggestions.append(f'{subject}: start with fundamentals before attempting advanced problems.')
        else:
            suggestions.append(f'{subject}: raise your score past 70 with weekly guided practice.')
    if not weaknesses:
        suggestions.append('Stay challenged: attempt cross-subject capstone projects.')
    if suggestions:
        suggestions.append(f'Average {average_score(scores)}% \u2014 aim for 80%+ next term.')
    return suggestions[:4]


def learning_resources(student) -> list[dict]:
    """Recommended resources targeting the student's weakest subjects."""
    weaknesses = getattr(student, 'weaknesses', None) or []
    subjects = weaknesses[:2] if weaknesses else SUBJECTS[:1]
    return [
        {
            'subject': subject,
            'resource': RESOURCE_MAP.get(subject, 'Curated practice sets and study notes'),
        }
        for subject in subjects
    ]


def suggested_peer_mentor(student) -> dict:
    """A group mate strong in the student's weakest subject (if any)."""
    weaknesses = getattr(student, 'weaknesses', None) or []
    group = getattr(student, 'group', None)
    if not weaknesses or group is None:
        return {'name': None, 'subject': None, 'reason': None}

    focus = weaknesses[0]
    for member_id in group.members:
        from students.models import Student

        try:
            member = Student.objects.get(student_id=member_id)
        except Student.DoesNotExist:
            continue
        if member.pk == student.pk:
            continue
        if focus in (member.strengths or []):
            return {
                'name': member.full_name,
                'subject': focus,
                'reason': f'{member.full_name} is strong in {focus} and can guide you.',
            }
    return {
        'name': None,
        'subject': focus,
        'reason': f'No group mate specialises in {focus} \u2014 ask the leader for a workshop.',
    }


def study_sessions(student) -> list[dict]:
    """A weekly study-session plan adapted to the student's availability."""
    availability = getattr(student, 'availability', None) or 'Morning'
    slot_map = {
        'Morning': '8:00 AM \u2013 9:00 AM',
        'Afternoon': '2:00 PM \u2013 3:00 PM',
        'Evening': '7:00 PM \u2013 8:00 PM',
    }
    slot = slot_map.get(availability, 'Flexible slot')
    return [
        {'day': 'Monday', 'slot': slot, 'focus': 'Weakest subject deep-dive'},
        {'day': 'Wednesday', 'slot': slot, 'focus': 'Peer review with group mates'},
        {'day': 'Friday', 'slot': slot, 'focus': 'Practice problems and revision'},
    ]


def build_student_insights(student) -> dict:
    """Complete intelligence payload for a student."""
    scores = student.scores or {}
    weaknesses = getattr(student, 'weaknesses', None) or []
    strengths = getattr(student, 'strengths', None) or []
    return {
        'academicSummary': (
            f'Average {average_score(scores)}% across {len(SUBJECTS)} subjects with '
            f'{len(strengths)} strength{"s" if len(strengths) != 1 else ""} and '
            f'{len(weaknesses)} area{"s" if len(weaknesses) != 1 else ""} to improve.'
        ),
        'learningTrend': learning_trend(scores),
        'strengthScore': strength_score(scores),
        'weaknessScore': weakness_score(scores),
        'improvementSuggestions': improvement_suggestions(student),
        'learningResources': learning_resources(student),
        'peerMentor': suggested_peer_mentor(student),
        'studySessions': study_sessions(student),
    }
