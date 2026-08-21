import type { AdminScores, AdminSubject } from '../types/admin'
import { ADMIN_SUBJECTS, STRENGTH_THRESHOLD, WEAKNESS_THRESHOLD } from '../utils/adminConstants'

export function detectStrengths(scores: AdminScores): AdminSubject[] {
  return ADMIN_SUBJECTS.filter((subject) => scores[subject] >= STRENGTH_THRESHOLD)
    .sort((left, right) => scores[right] - scores[left])
    .slice(0, 3)
}

export function detectWeaknesses(scores: AdminScores): AdminSubject[] {
  return ADMIN_SUBJECTS.filter((subject) => scores[subject] <= WEAKNESS_THRESHOLD)
    .sort((left, right) => scores[left] - scores[right])
    .slice(0, 3)
}

export function strongSubjectsOf(student: { scores: AdminScores; strengths?: AdminSubject[] }): AdminSubject[] {
  if (student.strengths && student.strengths.length > 0) return student.strengths
  return detectStrengths(student.scores)
}

export function weakSubjectsOf(student: { scores: AdminScores; weaknesses?: AdminSubject[] }): AdminSubject[] {
  if (student.weaknesses && student.weaknesses.length > 0) return student.weaknesses
  return detectWeaknesses(student.scores)
}

export function isExpertIn(student: { scores: AdminScores }, subject: AdminSubject): boolean {
  return student.scores[subject] >= STRENGTH_THRESHOLD
}
