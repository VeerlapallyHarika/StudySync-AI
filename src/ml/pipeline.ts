import type { AdminGroup, AdminGroupMember, AdminStudent, GenerationSummary } from '../types/admin'
import { DEFAULT_GROUP_SIZE } from '../utils/adminConstants'
import { complementaryMatch } from './complementaryMatching'
import { averageScore, buildFeatureVectors } from './featureEngineering'
import {
  averagePerformanceOf,
  balanceGroups,
  computeComplementarySkillScore,
  overallStrengthOf,
  overallWeaknessOf,
} from './groupBalancer'
import { kMeansCluster } from './kmeans'
import { buildLearningRecommendation, suggestTeamLeader } from './recommendation'
import { detectStrengths, detectWeaknesses, weakSubjectsOf } from './strengthAnalysis'

export interface GenerationOptions {
  targetGroupSize?: number
}

export function preprocessStudents(students: AdminStudent[]): AdminStudent[] {
  return students.map((student) => ({
    ...student,
    strengths: student.strengths.length > 0 ? student.strengths : detectStrengths(student.scores),
    weaknesses: student.weaknesses.length > 0 ? student.weaknesses : detectWeaknesses(student.scores),
  }))
}

export function toGroupMember(student: AdminStudent): AdminGroupMember {
  return {
    studentId: student.id,
    name: student.name,
    department: student.department,
    strongSubjects: student.strengths,
    weakSubjects: weakSubjectsOf(student),
    averageScore: averageScore(student.scores),
  }
}

export function generateStudyGroups(students: AdminStudent[], options: GenerationOptions = {}): {
  groups: AdminGroup[]
  summary: GenerationSummary
} {
  const targetGroupSize = options.targetGroupSize ?? DEFAULT_GROUP_SIZE
  const prepared = preprocessStudents(students)

  if (prepared.length === 0) {
    return {
      groups: [],
      summary: { groupsCreated: 0, studentsNotAssigned: 0, averageGroupSize: 0 },
    }
  }

  const featureVectors = buildFeatureVectors(prepared)
  const groupCount = Math.max(1, Math.min(Math.round(prepared.length / targetGroupSize), prepared.length))
  const clusterLabels = kMeansCluster(featureVectors, groupCount)

  const matched = complementaryMatch({ students: prepared, clusterLabels, targetSize: targetGroupSize })
  const balanced = balanceGroups(matched, targetGroupSize)

  const assignedCount = balanced.reduce((sum, group) => sum + group.length, 0)
  const groups: AdminGroup[] = balanced.map((members, index) => {
    const leader = suggestTeamLeader(members)
    return {
      id: `GRP-${String(index + 1).padStart(2, '0')}`,
      name: `Group ${String.fromCharCode(65 + index)}`,
      members: members.map(toGroupMember),
      overallStrengths: overallStrengthOf(members),
      overallWeaknesses: overallWeaknessOf(members),
      averagePerformance: averagePerformanceOf(members),
      complementarySkillScore: computeComplementarySkillScore(members),
      teamLeader: leader.name,
      learningRecommendation: buildLearningRecommendation(members),
      createdAt: new Date().toISOString(),
    }
  })

  return {
    groups,
    summary: {
      groupsCreated: groups.length,
      studentsNotAssigned: prepared.length - assignedCount,
      averageGroupSize: groups.length > 0 ? assignedCount / groups.length : 0,
    },
  }
}
