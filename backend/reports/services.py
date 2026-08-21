"""Report generation and export services (CSV, Excel, PDF).

Reports are built from live database state using pandas and reportlab, then
stored as JSON payloads in :class:`reports.models.Report`.
"""
from __future__ import annotations

import io
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

from groups.models import StudyGroup
from ml.utils import SUBJECTS
from notifications import services as notification_services
from reports.repositories import ReportRepository
from students.models import Student
from students.repositories import StudentRepository
from utils.logging import get_logger

logger = get_logger('reports')

DEFAULT_TITLE = 'StudySync AI Institutional Report'
EXPORT_COLUMNS = ['Student ID', 'Name', 'Department', 'Year', 'Section', 'Group', 'Average Score', *SUBJECTS]


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _distribution(items: List[str]) -> Dict[str, int]:
    distribution: Dict[str, int] = {}
    for item in items:
        distribution[item] = distribution.get(item, 0) + 1
    return distribution


def _most_common(distribution: Dict[str, int]):
    if not distribution:
        return None
    return max(distribution.items(), key=lambda item: item[1])


def _students_frame(students: List[Student]) -> pd.DataFrame:
    rows = []
    for student in students:
        rows.append({
            'Student ID': student.student_id,
            'Name': student.full_name,
            'Department': student.department,
            'Year': student.year,
            'Section': student.section,
            'Group': student.group.name if student.group is not None else 'Unassigned',
            'Average Score': round(student.average_score),
            **student.scores,
        })
    return pd.DataFrame(rows, columns=EXPORT_COLUMNS)


def _groups_frame(groups: List[StudyGroup]) -> pd.DataFrame:
    rows = []
    for group in groups:
        rows.append({
            'Group': group.name,
            'Member Count': len(group.members),
            'Average Performance': round(group.average_performance),
            'Complementary Skill Score': round(group.complementary_skill_score),
            'Team Leader': group.team_leader,
            'Overall Strengths': ', '.join(group.overall_strengths or []),
            'Overall Weaknesses': ', '.join(group.overall_weaknesses or []),
            'Learning Recommendation': group.learning_recommendation,
        })
    return pd.DataFrame(rows)


def build_report_data(title: str = DEFAULT_TITLE, generated_by: str = '') -> Dict[str, Any]:
    """Compute the full ``ReportData`` payload from current database state."""
    students = StudentRepository.all()
    groups = list(StudyGroup.objects.all())

    total_members = sum(len(group.members) for group in groups)
    average_group_size = round(total_members / len(groups), 1) if groups else 0
    assigned = sum(1 for student in students if student.group_id is not None)
    waiting = len(students) - assigned

    department_distribution = _distribution([student.department for student in students])
    strength_distribution = _distribution([subject for student in students for subject in (student.strengths or [])])
    weakness_distribution = _distribution([subject for student in students for subject in (student.weaknesses or [])])

    top_strength = _most_common(strength_distribution)
    top_weakness = _most_common(weakness_distribution)
    if top_strength:
        strength_summary = f'{top_strength[0]} is the most common strength, present in {top_strength[1]} students.'
    else:
        strength_summary = 'No strengths detected yet — generate groups or import students first.'
    if top_weakness:
        weakness_summary = f'{top_weakness[0]} requires the most support, flagged in {top_weakness[1]} students.'
    else:
        weakness_summary = 'No weaknesses detected yet — import students to begin analysis.'

    average_performance = round(sum(student.average_score for student in students) / len(students)) if students else 0

    group_performance_items = []
    for group in groups:
        group_performance_items.append(
            f'{group.name}: {len(group.members)} members, '
            f'{round(group.average_performance)}% avg, '
            f'{round(group.complementary_skill_score)}/100 complementary'
        )
    group_performance_summary = (
        '; '.join(group_performance_items) if group_performance_items else 'No groups generated yet.'
    )

    overall_weakest = _most_common(weakness_distribution)
    analytics_summary = (
        f'Overall cohort average is {average_performance}%. '
        f'Strongest subject: {top_strength[0] if top_strength else "n/a"}. '
        f'Most-needed support: {overall_weakest[0] if overall_weakest else "n/a"}. '
        f'{assigned} of {len(students)} students are placed in a group.'
    )

    sections = [
        {
            'key': 'group_composition',
            'title': 'Group Composition',
            'summary': f'{len(groups)} study groups formed with an average size of {average_group_size} members.',
        },
        {
            'key': 'student_analysis',
            'title': 'Student Analysis',
            'summary': f'{len(students)} students enrolled, {assigned} assigned and {waiting} waiting for placement.',
        },
        {
            'key': 'department_analysis',
            'title': 'Department Analysis',
            'summary': ', '.join(f'{department}: {count}' for department, count in sorted(department_distribution.items(), key=lambda item: item[1], reverse=True)) or 'No students yet.',
        },
        {'key': 'strength_analysis', 'title': 'Strength Analysis', 'summary': strength_summary},
        {'key': 'weakness_analysis', 'title': 'Weakness Analysis', 'summary': weakness_summary},
        {
            'key': 'group_performance',
            'title': 'Group Performance',
            'summary': group_performance_summary,
        },
        {
            'key': 'analytics_summary',
            'title': 'Analytics Summary',
            'summary': analytics_summary,
        },
    ]

    return {
        'generatedAt': _now_iso(),
        'generatedBy': generated_by or 'System Administrator',
        'title': title,
        'totalStudents': len(students),
        'totalGroups': len(groups),
        'averageGroupSize': average_group_size,
        'averagePerformance': average_performance,
        'sections': sections,
    }


def generate_report(generated_by: str = '') -> Dict[str, Any]:
    """Persist a fresh report and return its payload."""
    payload = build_report_data(generated_by=generated_by)
    ReportRepository.create(
        title=payload['title'],
        payload=payload,
        departments=[student.department for student in StudentRepository.all()],
        group_names=[group.name for group in StudyGroup.objects.all()],
    )
    logger.info(
        'Report generated :: total_students=%s total_groups=%s generated_by=%s',
        payload['totalStudents'],
        payload['totalGroups'],
        payload['generatedBy'],
    )
    return payload


def list_reports(filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """List stored reports, optionally filtered by date, department or group."""
    filters = filters or {}
    reports = ReportRepository.all()

    date_from = filters.get('from')
    date_to = filters.get('to')
    department = (filters.get('department') or '').strip().lower()
    group_name = (filters.get('group') or '').strip().lower()

    matched: List[Dict[str, Any]] = []
    for report in reports:
        created_at = report.created_at
        if date_from and created_at.replace(tzinfo=None) < _parse_date(date_from):
            continue
        if date_to and created_at.replace(tzinfo=None) > _parse_date(date_to, end=True):
            continue
        if department and department not in [item.lower() for item in (report.departments or [])]:
            continue
        if group_name and group_name not in [item.lower() for item in (report.group_names or [])]:
            continue
        matched.append(report)

    return [report.payload for report in matched]


def _parse_date(value: str, end: bool = False) -> datetime:
    try:
        return datetime.strptime(value, '%Y-%m-%d')
    except ValueError:
        pass
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        parsed = datetime(1970, 1, 1)
    if end:
        return parsed.replace(hour=23, minute=59, second=59)
    return parsed


def export_csv() -> Tuple[bytes, str, str]:
    """CSV export: student list with scores and group assignment."""
    frame = _students_frame(StudentRepository.all())
    content = '\ufeff' + frame.to_csv(index=False)
    logger.info('Report exported as CSV')
    notification_services.log_activity('report_exported', detail='CSV export downloaded')
    return content.encode('utf-8'), 'studysync-report.csv', 'text/csv'


def export_excel() -> Tuple[bytes, str, str]:
    """Excel export: students, groups and the four analysis distributions."""
    students = StudentRepository.all()
    groups = list(StudyGroup.objects.all())

    strength_distribution = _distribution([subject for student in students for subject in (student.strengths or [])])
    weakness_distribution = _distribution([subject for student in students for subject in (student.weaknesses or [])])
    department_distribution = _distribution([student.department for student in students])

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        _students_frame(students).to_excel(writer, sheet_name='Students', index=False)
        _groups_frame(groups).to_excel(writer, sheet_name='Groups', index=False)
        _distribution_frame('Subject', 'Students', strength_distribution).to_excel(writer, sheet_name='Strength Distribution', index=False)
        _distribution_frame('Subject', 'Students', weakness_distribution).to_excel(writer, sheet_name='Weakness Distribution', index=False)
        _distribution_frame('Department', 'Students', department_distribution).to_excel(writer, sheet_name='Department Analysis', index=False)

    logger.info('Report exported as Excel')
    notification_services.log_activity('report_exported', detail='Excel export downloaded')
    return buffer.getvalue(), 'studysync-report.xlsx', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'


def export_pdf() -> Tuple[bytes, str, str]:
    """PDF export: report header, section summaries and a student table."""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    payload = build_report_data()
    students = StudentRepository.all()

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=inch * 0.8,
        leftMargin=inch * 0.8,
        topMargin=inch * 0.8,
        bottomMargin=inch * 0.8,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('StudyTitle', parent=styles['Title'], fontSize=20, spaceAfter=4)
    subtitle_style = ParagraphStyle('StudySubtitle', parent=styles['Normal'], fontSize=10, textColor=colors.grey)
    heading_style = ParagraphStyle('StudyHeading', parent=styles['Heading2'], fontSize=13, spaceBefore=14, spaceAfter=4)

    story = [
        Paragraph(_escape(payload['title']), title_style),
        Paragraph(
            _escape(f'Generated {datetime.now().strftime("%d %b %Y, %H:%M")} by {payload["generatedBy"]} · {payload["totalStudents"]} students · {payload["totalGroups"]} groups'),
            subtitle_style,
        ),
        Spacer(1, 10),
    ]

    for section in payload['sections']:
        story.append(Paragraph(_escape(section['title']), heading_style))
        story.append(Paragraph(_escape(section['summary']), styles['Normal']))

    story.append(Spacer(1, 14))
    story.append(Paragraph('Student List', heading_style))

    table_data = [EXPORT_COLUMNS]
    for student in students:
        table_data.append([
            student.student_id,
            student.full_name,
            student.department,
            student.year,
            student.section,
            student.group.name if student.group is not None else 'Unassigned',
            round(student.average_score),
            *[round(student.scores[subject]) for subject in SUBJECTS],
        ])

    table = Table(table_data, repeatRows=1)
    table.setStyle(
        TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 7.5),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1d4ed8')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#cbd5e1')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ])
    )
    story.append(table)

    doc.build(story)
    logger.info('Report exported as PDF')
    notification_services.log_activity('report_exported', detail='PDF export downloaded')
    return buffer.getvalue(), 'studysync-report.pdf', 'application/pdf'


def _distribution_frame(label: str, count_label: str, distribution: Dict[str, int]) -> pd.DataFrame:
    rows = [{'label': key, count_label: value} for key, value in sorted(distribution.items(), key=lambda item: item[1], reverse=True)]
    return pd.DataFrame(rows)


def _escape(text: str) -> str:
    return str(text).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
