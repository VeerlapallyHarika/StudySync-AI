import { describe, expect, it } from 'vitest'
import { detectStrengths, detectWeaknesses, isExpertIn, strongSubjectsOf, weakSubjectsOf } from './strengthAnalysis'
import type { AdminScores, AdminSubject } from '../types/admin'

const SCORES: AdminScores = {
  Mathematics: 90,
  Physics: 55,
  Programming: 78,
  Database: 40,
  'Operating Systems': 65,
}

describe('detectStrengths', () => {
  it('flags subjects at or above the strength threshold, sorted descending', () => {
    expect(detectStrengths(SCORES)).toEqual(['Mathematics', 'Programming'])
  })

  it('returns empty when nothing qualifies', () => {
    const low: AdminScores = { ...SCORES, Mathematics: 50, Programming: 50 }
    expect(detectStrengths(low)).toEqual([])
  })
})

describe('detectWeaknesses', () => {
  it('flags subjects at or below the weakness threshold, sorted ascending', () => {
    expect(detectWeaknesses(SCORES)).toEqual(['Database'])
  })

  it('returns empty when nothing qualifies', () => {
    const high: AdminScores = { ...SCORES, Database: 70 }
    expect(detectWeaknesses(high)).toEqual([])
  })
})

describe('strongSubjectsOf / weakSubjectsOf', () => {
  it('prefers pre-computed lists over re-detection', () => {
    const student: { scores: AdminScores; strengths: AdminSubject[] } = { scores: SCORES, strengths: ['Physics'] }
    expect(strongSubjectsOf(student)).toEqual(['Physics'])
  })

  it('falls back to detection when no list is stored', () => {
    expect(weakSubjectsOf({ scores: SCORES })).toEqual(['Database'])
  })
})

describe('isExpertIn', () => {
  it('returns true for a subject at or above the threshold', () => {
    expect(isExpertIn({ scores: SCORES }, 'Mathematics')).toBe(true)
  })

  it('returns false below the threshold', () => {
    expect(isExpertIn({ scores: SCORES }, 'Database')).toBe(false)
  })
})
