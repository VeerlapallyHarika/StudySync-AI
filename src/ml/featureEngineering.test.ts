import { describe, expect, it } from 'vitest'
import { averageScore, averageScoreOf, buildFeatureVector, normalizeScores } from './featureEngineering'
import type { AdminScores, AdminStudent } from '../types/admin'

const SCORES: AdminScores = {
  Mathematics: 90,
  Physics: 70,
  Programming: 50,
  Database: 60,
  'Operating Systems': 80,
}

describe('normalizeScores', () => {
  it('maps the minimum score to 0 and the maximum to 100', () => {
    const normalized = normalizeScores(SCORES)
    expect(normalized.Mathematics).toBe(100)
    expect(normalized.Programming).toBe(0)
    expect(normalized.Physics).toBe(50)
  })

  it('does not divide by zero when all scores are equal', () => {
    const flat: AdminScores = {
      Mathematics: 60,
      Physics: 60,
      Programming: 60,
      Database: 60,
      'Operating Systems': 60,
    }
    expect(normalizeScores(flat).Mathematics).toBe(0)
  })
})

describe('buildFeatureVector', () => {
  it('produces one normalized value per subject', () => {
    const vector = buildFeatureVector(SCORES)
    expect(vector).toHaveLength(5)
    expect(vector[0]).toBe(100)
  })
})

describe('averageScore', () => {
  it('rounds the mean of all subjects', () => {
    expect(averageScore(SCORES)).toBe(70)
  })

  it('returns 0 for a fully empty scores object', () => {
    expect(averageScore({} as AdminScores)).toBe(0)
  })
})

describe('averageScoreOf', () => {
  it('returns 0 for no students', () => {
    expect(averageScoreOf([])).toBe(0)
  })

  it('averages across students', () => {
    const studentA = { scores: SCORES } as AdminStudent
    const studentB = { ...studentA, scores: { ...SCORES, Mathematics: 50 } } as AdminStudent
    expect(averageScoreOf([studentA, studentB])).toBe(66)
  })
})
