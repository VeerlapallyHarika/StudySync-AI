import type { AdminStudent, AdminSubject } from '../types/admin'
import { averageScore } from './featureEngineering'
import { overallWeaknessOf } from './groupBalancer'

export function suggestTeamLeader(members: AdminStudent[]): AdminStudent {
  return [...members].sort((left, right) => {
    const leftCoverage = left.strengths.length
    const rightCoverage = right.strengths.length
    if (rightCoverage !== leftCoverage) return rightCoverage - leftCoverage
    return averageScore(right.scores) - averageScore(left.scores)
  })[0]
}

export function buildLearningRecommendation(members: AdminStudent[]): string {
  const weaknesses = overallWeaknessOf(members)
  if (weaknesses.length === 0) {
    return 'Maintain momentum with advanced problem sets and cross-subject projects.'
  }

  const focusSubject = weaknesses[0]
  const experts = members
    .filter((member) => member.strengths.includes(focusSubject))
    .map((member) => member.name)

  const mentorSuggestion = experts.length > 0 ? ` ${experts.join(', ')} can lead peer tutoring sessions.` : ' Pair with an external tutor or focused workshops.'

  return `Prioritize ${focusSubject} support with weekly peer study blocks.${mentorSuggestion}`
}

export function leadershipQualities(members: AdminStudent[]): Record<string, string> {
  const leader = suggestTeamLeader(members)
  const nextLeaders = [...members]
    .filter((member) => member.id !== leader.id)
    .sort((left, right) => averageScore(right.scores) - averageScore(left.scores))
    .slice(0, 2)

  return {
    suggestedLeader: leader.name,
    coLeadCandidates: nextLeaders.map((member) => member.name).join(', ') || 'None',
  }
}

export function formatSubjects(subjects: AdminSubject[] | string[]): string {
  return subjects.length > 0 ? subjects.join(', ') : 'Balanced'
}
