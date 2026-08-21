export type StudentAvailability = 'Morning' | 'Afternoon' | 'Evening'
export type LearningPreference = 'Practical' | 'Theory' | 'Mixed'

export type StudentSubject =
  | 'Mathematics'
  | 'Physics'
  | 'Programming'
  | 'Database Management'
  | 'Operating Systems'

export type StudentScores = Record<StudentSubject, number>

export interface StudentRegistrationFormValues {
  fullName: string
  studentId: string
  email: string
  department: string
  year: string
  section: string
  scores: StudentScores
  availability: StudentAvailability
  learningPreference: LearningPreference
  password: string
  confirmPassword: string
}

export interface StudentLoginFormValues {
  email: string
  password: string
  rememberMe: boolean
}

export interface StudentProfileData extends StudentRegistrationFormValues {
  assignedGroup?: string
  overallGroupStrength?: string
  groupMembers?: StudentGroupMember[]
  notifications?: StudentNotification[]
  averageScore?: number
  strengths?: StudentSubject[]
  insights?: StudentInsights
}

export interface StudentProfileUpdateValues extends StudentRegistrationFormValues {}

export interface StudentInsights {
  academicSummary: string
  learningTrend: string
  strengthScore: number
  weaknessScore: number
  improvementSuggestions: string[]
  learningResources: Array<{ subject: string; resource: string }>
  peerMentor: { name: string | null; subject: string | null; reason: string | null }
  studySessions: Array<{ day: string; slot: string; focus: string }>
}

export interface StudentStatsCardData {
  label: string
  value: string
  note?: string
}

export interface StudentSubjectSummary {
  subject: StudentSubject
  score: number
  status: string
  description: string
  progress: number
}

export interface StudentStrengthAnalysis {
  strengths: StudentSubject[]
  weaknesses: StudentSubject[]
}

export interface StudentGroupData {
  name: string
  members: string[]
  overallStrength: string
}

export interface StudentGroupMember {
  avatar: string
  name: string
  department: string
  strongSubject: string
  weakSubject: string
  status: string
}

export interface StudentNotification {
  title: string
  description: string
  tone?: 'info' | 'success' | 'warning'
}

export interface StudentDashboardData {
  welcomeName: string
  stats: StudentStatsCardData[]
  academicSummary: StudentSubjectSummary[]
  strengthAnalysis: StudentStrengthAnalysis
  assignedGroup: StudentGroupData
  groupMembers: StudentGroupMember[]
  notifications: StudentNotification[]
  overallPerformance: number
  insights?: StudentInsights
}

export interface StudentNotificationPreferences {
  emailNotifications: boolean
  groupUpdates: boolean
  aiInsights: boolean
  weeklyDigest: boolean
}

export const DEFAULT_STUDENT_NOTIFICATION_PREFERENCES: StudentNotificationPreferences = {
  emailNotifications: true,
  groupUpdates: true,
  aiInsights: true,
  weeklyDigest: false,
}

export interface GroupMemberDetail {
  studentId: string
  name: string
  department: string
  avatar: string
  strongSubjects: string[]
  weakSubjects: string[]
  averageScore: number
  learningPreference?: string
  availability?: string
  isSelf: boolean
}

export interface ChatMessageItem {
  id: number
  sender: string
  senderId: string
  isSelf: boolean
  message: string
  createdAt: string
}

export type ResourceType =
  | 'Study Notes'
  | 'Documents'
  | 'Useful Links'
  | 'Videos'
  | 'Assignments'
  | 'Other'

export interface SharedResourceItem {
  id: number
  title: string
  resourceType: ResourceType
  url: string
  fileName: string | null
  fileUrl: string | null
  uploader: string
  createdAt: string
}

export interface GroupActivityItem {
  type: 'message' | 'resource'
  actor: string
  text: string
  detail: string
  createdAt: string
}

export interface GroupWeaknessCoverage {
  subject: string
  covered: boolean
  coveredBy: string[]
}

export interface StudentGroupStatus {
  profileComplete: boolean
  eligibleStudents: number
  minimumRequired: number
  groupsGenerated: boolean
  group: StudentGroupDetail | null
  message?: string | null
}

export interface StudentGroupDetail {
  id: string
  name: string
  members: GroupMemberDetail[]
  overallStrengths: string[]
  overallWeaknesses: string[]
  weaknessCoverage: GroupWeaknessCoverage[]
  averagePerformance: number
  complementarySkillScore: number
  teamLeader: string
  learningRecommendation: string
  chat: ChatMessageItem[]
  resources: SharedResourceItem[]
  activity: GroupActivityItem[]
  createdAt: string | null
}
