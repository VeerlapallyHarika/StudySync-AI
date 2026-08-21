import type { AdminStudent, AdminSubject } from '../types/admin'
import { ADMIN_SUBJECTS } from '../utils/adminConstants'
import { isExpertIn } from './strengthAnalysis'

export interface MatchingContext {
  students: AdminStudent[]
  clusterLabels: number[]
  targetSize: number
}

export function complementaryMatch(context: MatchingContext): AdminStudent[][] {
  const { students, clusterLabels, targetSize } = context
  const groupCount = Math.max(1, Math.min(Math.round(students.length / targetSize), students.length))
  const groups: AdminStudent[][] = Array.from({ length: groupCount }, () => [])
  const assigned = new Set<number>()

  if (students.length === 0) return groups

  for (let subjectIndex = 0; subjectIndex < ADMIN_SUBJECTS.length; subjectIndex += 1) {
    const subject = ADMIN_SUBJECTS[subjectIndex]
    const expertPool = students
      .map((student, index) => ({ student, index }))
      .filter(({ index, student }) => !assigned.has(index) && isExpertIn(student, subject))
      .sort((left, right) => right.student.scores[subject] - left.student.scores[subject])

    for (let groupOffset = 0; groupOffset < groupCount && expertPool.length > 0; groupOffset += 1) {
      const groupIndex = (subjectIndex + groupOffset) % groupCount
      if (groups[groupIndex].length >= targetSize) continue

      let bestCandidateIndex = 0
      let bestAffinity = -1
      expertPool.forEach(({ index }, poolPosition) => {
        const affinity = clusterLabels[index] === groupIndex ? 1 : 0
        const weight = affinity * 10 + (expertPool.length - poolPosition)
        if (weight > bestAffinity) {
          bestAffinity = weight
          bestCandidateIndex = poolPosition
        }
      })

      const candidate = expertPool[bestCandidateIndex]
      groups[groupIndex].push(candidate.student)
      assigned.add(candidate.index)
      expertPool.splice(bestCandidateIndex, 1)
    }
  }

  const remaining = students
    .map((student, index) => ({ student, index }))
    .filter(({ index }) => !assigned.has(index))
    .sort((left, right) => clusterLabels[left.index] - clusterLabels[right.index])

  for (const { student, index } of remaining) {
    let bestGroupIndex = -1
    let bestScore = Number.POSITIVE_INFINITY

    for (let groupIndex = 0; groupIndex < groupCount; groupIndex += 1) {
      if (groups[groupIndex].length >= targetSize) continue
      const clusterPenalty = clusterLabels[index] === groupIndex ? 0 : 1
      const capacityPenalty = groups[groupIndex].length
      const score = clusterPenalty * 10 + capacityPenalty
      if (score < bestScore) {
        bestScore = score
        bestGroupIndex = groupIndex
      }
    }

    if (bestGroupIndex === -1) {
      groups[groupCount - 1].push(student)
    } else {
      groups[bestGroupIndex].push(student)
    }
  }

  return groups.filter((group) => group.length > 0)
}

export function subjectCoverage(members: AdminStudent[]): Record<AdminSubject, boolean> {
  const coverage = {} as Record<AdminSubject, boolean>
  ADMIN_SUBJECTS.forEach((subject) => {
    coverage[subject] = members.some((member) => isExpertIn(member, subject))
  })
  return coverage
}

export function uniqueStrengths(members: AdminStudent[]): AdminSubject[] {
  const seen = new Set<AdminSubject>()
  members.forEach((member) => {
    member.strengths.forEach((subject) => seen.add(subject))
  })
  return [...seen]
}
