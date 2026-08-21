import type { AdminSubject } from '../types/admin'

export const ADMIN_SUBJECTS: AdminSubject[] = [
  'Mathematics',
  'Physics',
  'Programming',
  'Database',
  'Operating Systems',
]

export const ADMIN_DEPARTMENTS = ['Computer Science', 'Information Technology', 'Electronics', 'AIML', 'Mechanical', 'Civil']

export const ADMIN_YEARS = ['1st Year', '2nd Year', '3rd Year', '4th Year']

export const ADMIN_SECTIONS = ['A', 'B', 'C']

export const ADMIN_EMAIL = 'admin@studysync.ai'
export const ADMIN_PASSWORD = 'admin123'

export const DEFAULT_GROUP_SIZE = 4

export const ADMIN_STORAGE_KEYS = {
  students: 'studysync.admin.students',
  groups: 'studysync.admin.groups',
  session: 'studysync.admin.session',
  reports: 'studysync.admin.reports',
  reportDownloads: 'studysync.admin.reportDownloads',
  tokens: 'studysync.admin.tokens',
}

export const STRENGTH_THRESHOLD = 75
export const WEAKNESS_THRESHOLD = 50
