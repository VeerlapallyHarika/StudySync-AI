export type AdminSubject =
  | 'Mathematics'
  | 'Physics'
  | 'Programming'
  | 'Database'
  | 'Operating Systems'

export type AdminScores = Record<AdminSubject, number>

export type StudentStatus = 'Assigned' | 'Waiting' | 'Registered'

export interface AdminStudent {
  id: string
  name: string
  department: string
  year: string
  section: string
  scores: AdminScores
  strengths: AdminSubject[]
  weaknesses: AdminSubject[]
  status: StudentStatus
  groupName?: string
  averageScore: number
}

export interface AdminGroupMember {
  studentId: string
  name: string
  department: string
  strongSubjects: AdminSubject[]
  weakSubjects: AdminSubject[]
  averageScore: number
  scores?: Record<string, number>
  learningPreference?: string
  availability?: string
}

export interface GroupRecommendations {
  overallSkillLevel: string
  leaderReason: string
  strongAreaRecommendation?: string
  weakAreaRecommendation?: string
  meetingRecommendation: string
  suggestedImprovements?: string[]
}

export interface AdminGroup {
  id: string
  name: string
  members: AdminGroupMember[]
  overallStrengths: AdminSubject[]
  overallWeaknesses: AdminSubject[]
  averagePerformance: number
  complementarySkillScore: number
  teamLeader: string
  learningRecommendation: string
  recommendations?: GroupRecommendations
  createdAt: string
}

export interface ActivityEntry {
  action: string
  actor: string
  detail: string
  createdAt: string
}

export interface StudentRegistrationEntry {
  studentId: string
  name: string
  department: string
  registeredAt?: string | null
}

export interface AtRiskStudent {
  studentId: string
  name: string
  department: string
  averageScore: number
  weaknesses: string[]
  group?: string | null
}

export interface AdminDashboardData {
  totalStudents: number
  totalGroups: number
  studentsAssigned: number
  studentsWaiting: number
  averageGroupSize: number
  lastGroupGeneration: string
  departmentDistribution: Record<string, number>
  strengthDistribution: Record<string, number>
  weaknessDistribution: Record<string, number>
  averageStudentScore: number
  averageComplementaryScore: number
  mostActiveDepartment?: string | null
  largestGroup?: string | null
  smallestGroup?: string | null
  recentActivities?: ActivityEntry[]
  latestRegistrations?: StudentRegistrationEntry[]
  studentsRequiringImprovement?: AtRiskStudent[]
}

export interface AdminNotification {
  id: string
  title: string
  description: string
  tone: 'success' | 'warning' | 'info'
}

export interface GroupAnalytics {
  studentsPerGroup: Array<{ label: string; value: number }>
  strengthDistribution: Record<string, number>
  weaknessDistribution: Record<string, number>
  departmentDistribution: Record<string, number>
  averageGroupScore: number
}

export type ReportSectionKey =
  | 'group_composition'
  | 'student_analysis'
  | 'department_analysis'
  | 'strength_analysis'
  | 'weakness_analysis'
  | 'group_performance'
  | 'analytics_summary'

export interface ReportSection {
  key: ReportSectionKey
  title: string
  summary: string
}

export interface ReportData {
  generatedAt: string
  generatedBy: string
  title: string
  totalStudents: number
  totalGroups: number
  averageGroupSize: number
  averagePerformance: number
  sections: ReportSection[]
}

export interface GenerationSummary {
  groupsCreated: number
  studentsNotAssigned: number
  averageGroupSize: number
}

export interface SubjectAverage {
  subject: AdminSubject
  average: number
  students: number
}

export interface DepartmentPerformance {
  department: string
  average: number
  students: number
}

export interface GroupComparisonEntry {
  id: string
  name: string
  members: number
  averagePerformance: number
  complementarySkillScore: number
}

export interface AdminAnalytics {
  generatedAt: string
  totalStudents: number
  totalGroups: number
  overallAverageScore: number
  subjectAverages: SubjectAverage[]
  departmentPerformance: DepartmentPerformance[]
  strengthDistribution: Record<string, number>
  weaknessDistribution: Record<string, number>
  groupComparison: GroupComparisonEntry[]
  studentsRequiringImprovement: AtRiskStudent[]
}

export interface AdminSettings {
  departments: string[]
  defaultGroupSize: number
  kmeansRandomState: number
  kmeansMaxIterations: number
  exportDefaultFormat: 'csv' | 'excel' | 'pdf'
  notifyGroupsGenerated: boolean
  notifyCsvImported: boolean
}

export interface SystemInfo {
  name: string
  version: string
  djangoVersion?: string
  backend: string
  frontend: string
  ml: string
  database: string
  totalStudents: number
  assignedStudents: number
}

export interface NotificationItem {
  id: number
  category: string
  title: string
  message: string
  tone: 'success' | 'warning' | 'info'
  read: boolean
  createdAt: string
}

export interface ReportDownload {
  format: 'csv' | 'excel' | 'pdf'
  filename: string
  at: string
}
