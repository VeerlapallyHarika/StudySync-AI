import type { AdminScores, AdminStudent, AdminSubject } from '../types/admin'
import { ADMIN_SUBJECTS } from '../utils/adminConstants'

export const SUBJECT_DIMENSION_ORDER: AdminSubject[] = ADMIN_SUBJECTS

export function normalizeScores(scores: AdminScores): AdminScores {
  const values = ADMIN_SUBJECTS.map((subject) => scores[subject] ?? 0)
  const minimum = Math.min(...values)
  const maximum = Math.max(...values)
  const spread = maximum - minimum || 1

  const normalized = {} as AdminScores
  ADMIN_SUBJECTS.forEach((subject, index) => {
    normalized[subject] = Math.round(((values[index] - minimum) / spread) * 10000) / 100
  })
  return normalized
}

export function buildFeatureVector(scores: AdminScores): number[] {
  const normalized = normalizeScores(scores)
  return ADMIN_SUBJECTS.map((subject) => normalized[subject])
}

export function buildFeatureVectors(students: AdminStudent[]): number[][] {
  return students.map((student) => buildFeatureVector(student.scores))
}

export function averageScore(scores: AdminScores): number {
  if (ADMIN_SUBJECTS.length === 0) return 0
  const total = ADMIN_SUBJECTS.reduce((sum, subject) => sum + (scores[subject] ?? 0), 0)
  return Math.round(total / ADMIN_SUBJECTS.length)
}

export function averageScoreOf(students: AdminStudent[]): number {
  if (students.length === 0) return 0
  return Math.round(students.reduce((sum, student) => sum + averageScore(student.scores), 0) / students.length)
}
