import type { AdminStudent, AdminSubject } from '../types/admin'
import { subjectCoverage } from './complementaryMatching'
import { averageScore } from './featureEngineering'

function balancePenalty(members: AdminStudent[], candidate: AdminStudent): number {
  return -Math.abs(members.length - candidate.strengths.length)
}

export function balanceGroups(groups: AdminStudent[][], _targetSize: number): AdminStudent[][] {
  const nonEmpty = groups.filter((group) => group.length > 0)
  if (nonEmpty.length === 0) return nonEmpty

  const totalMembers = nonEmpty.reduce((sum, group) => sum + group.length, 0)
  const groupCount = nonEmpty.length
  const minimumSize = Math.floor(totalMembers / groupCount)
  const maximumSize = Math.ceil(totalMembers / groupCount)

  const moveToSmallest = (groupIndex: number, member: AdminStudent) => {
    let smallestIndex = -1
    let smallestSize = Number.POSITIVE_INFINITY

    nonEmpty.forEach((group, index) => {
      if (index === groupIndex) return
      if (group.length < smallestSize) {
        smallestSize = group.length
        smallestIndex = index
      }
    })

    if (smallestIndex !== -1 && smallestSize < minimumSize) {
      nonEmpty[groupIndex] = nonEmpty[groupIndex].filter((current) => current.id !== member.id)
      nonEmpty[smallestIndex].push(member)
      return true
    }
    return false
  }

  let rebalanced = true
  let guard = 0
  while (rebalanced && guard < 100) {
    rebalanced = false
    guard += 1

    for (let groupIndex = 0; groupIndex < nonEmpty.length; groupIndex += 1) {
      const group = nonEmpty[groupIndex]
      if (group.length <= maximumSize) continue

      const sorted = [...group].sort(
        (left, right) => balancePenalty(group, left) - balancePenalty(group, right),
      )

      for (const candidate of sorted) {
        if (group.length <= maximumSize) break
        if (moveToSmallest(groupIndex, candidate)) {
          rebalanced = true
        }
      }
    }
  }

  return nonEmpty.filter((group) => group.length > 0)
}

export function computeComplementarySkillScore(members: AdminStudent[]): number {
  if (members.length === 0) return 0

  const coverage = subjectCoverage(members)
  const coveredSubjects = Object.values(coverage).filter(Boolean).length
  const totalSubjects = Object.keys(coverage).length

  const coverageScore = (coveredSubjects / totalSubjects) * 60

  const distinctStrengths = new Set(members.flatMap((member) => member.strengths)).size
  const diversityScore = Math.min(distinctStrengths / (members.length * 3), 1) * 25

  const balancedSizes = members.length >= 3 && members.length <= 5 ? 1 : 0.5
  const sizeScore = balancedSizes * 15

  return Math.round(coverageScore + diversityScore + sizeScore)
}

export function overallStrengthOf(members: AdminStudent[]): AdminSubject[] {
  const seen = new Set<AdminSubject>()
  members.forEach((member) => {
    member.strengths.forEach((subject) => seen.add(subject))
  })
  return [...seen].slice(0, 4)
}

export function overallWeaknessOf(members: AdminStudent[]): AdminSubject[] {
  const seen = new Set<AdminSubject>()
  members.forEach((member) => {
    member.weaknesses.forEach((subject) => seen.add(subject))
  })
  return [...seen].slice(0, 4)
}

export function averagePerformanceOf(members: AdminStudent[]): number {
  if (members.length === 0) return 0
  return Math.round(members.reduce((sum, member) => sum + averageScore(member.scores), 0) / members.length)
}
