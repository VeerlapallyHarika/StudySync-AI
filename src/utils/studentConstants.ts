import type {
  LearningPreference,
  StudentAvailability,
  StudentSubject,
} from '../types/student'

export const STUDENT_SUBJECTS: StudentSubject[] = [
  'Mathematics',
  'Physics',
  'Programming',
  'Database Management',
  'Operating Systems',
]

export const STUDENT_AVAILABILITY_OPTIONS: StudentAvailability[] = [
  'Morning',
  'Afternoon',
  'Evening',
]

export const STUDENT_PREFERENCE_OPTIONS: LearningPreference[] = [
  'Practical',
  'Theory',
  'Mixed',
]

export const STUDENT_STORAGE_KEYS = {
  profile: 'studysync.student.profile',
  session: 'studysync.student.session',
  tokens: 'studysync.student.tokens',
  preferences: 'studysync.student.preferences',
}
