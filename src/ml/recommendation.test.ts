import { describe, expect, it } from 'vitest'
import { buildLearningRecommendation, formatSubjects, leadershipQualities, suggestTeamLeader } from './recommendation'
import type { AdminStudent } from '../types/admin'

function student(id: string, name: string, scores: [number, number, number, number, number], strengths: string[], weaknesses: string[]): AdminStudent {
  return {
    id,
    name,
    department: 'Computer Science',
    year: '2nd Year',
    section: 'A',
    scores: {
      Mathematics: scores[0],
      Physics: scores[1],
      Programming: scores[2],
      Database: scores[3],
      'Operating Systems': scores[4],
    },
    strengths: strengths as AdminStudent['strengths'],
    weaknesses: weaknesses as AdminStudent['weaknesses'],
    status: 'Waiting',
    averageScore: 0,
  }
}

const MEMBERS = [
  student('S1', 'Alice', [95, 90, 85, 80, 75], ['Mathematics', 'Physics'], ['Database']),
  student('S2', 'Bob', [60, 55, 95, 90, 85], ['Programming', 'Database'], ['Mathematics']),
  student('S3', 'Carol', [70, 75, 70, 45, 55], ['Physics'], ['Database']),
]

describe('suggestTeamLeader', () => {
  it('prefers the member with the broadest strength coverage', () => {
    expect(suggestTeamLeader(MEMBERS).name).toBe('Alice')
  })
})

describe('leadershipQualities', () => {
  it('names a suggested leader and co-lead candidates', () => {
    const result = leadershipQualities(MEMBERS)
    expect(result.suggestedLeader).toBe('Alice')
    expect(result.coLeadCandidates).toContain('Bob')
  })
})

describe('buildLearningRecommendation', () => {
  it('mentions the weakest subject and available peer experts', () => {
    const recommendation = buildLearningRecommendation(MEMBERS)
    expect(recommendation).toContain('Database')
    expect(recommendation).toContain('Bob')
  })

  it('returns a positive message when there are no weaknesses', () => {
    const strong = MEMBERS.map((member) => ({ ...member, weaknesses: [] }))
    const recommendation = buildLearningRecommendation(strong)
    expect(recommendation).toContain('Maintain momentum')
  })
})

describe('formatSubjects', () => {
  it('joins subjects with commas', () => {
    expect(formatSubjects(['Mathematics', 'Physics'])).toBe('Mathematics, Physics')
  })

  it('returns "Balanced" for an empty list', () => {
    expect(formatSubjects([])).toBe('Balanced')
  })
})
