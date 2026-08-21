import type {
  StudentLoginFormValues,
  StudentProfileData,
  StudentRegistrationFormValues,
} from '../types/student'
import { STUDENT_SUBJECTS } from './studentConstants'

const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

export type StudentFormErrors = Partial<Record<string, string>>

export function isValidEmail(email: string) {
  return EMAIL_REGEX.test(email)
}

export function validateRegistrationForm(
  values: StudentRegistrationFormValues,
  existingStudent?: StudentProfileData | null,
  options: { requirePassword?: boolean } = {},
): StudentFormErrors {
  const errors: StudentFormErrors = {}

  if (!values.fullName.trim()) errors.fullName = 'Full name is required.'
  if (!values.studentId.trim()) errors.studentId = 'Student ID is required.'
  if (!values.email.trim()) errors.email = 'Email is required.'
  if (values.email.trim() && !isValidEmail(values.email)) {
    errors.email = 'Enter a valid email address.'
  }
  if (!values.department.trim()) errors.department = 'Department is required.'
  if (!values.year.trim()) errors.year = 'Year is required.'
  if (!values.section.trim()) errors.section = 'Section is required.'
  if (!values.availability) errors.availability = 'Select an availability slot.'
  if (!values.learningPreference)
    errors.learningPreference = 'Select a learning preference.'

  const password = values.password ?? ''
  const confirmPassword = values.confirmPassword ?? ''
  if (options.requirePassword && !password) {
    errors.password = 'Password is required.'
  }
  if (password) {
    if (password.length < 8) {
      errors.password = 'Password must be at least 8 characters.'
    }
    if (!confirmPassword) {
      errors.confirmPassword = 'Please confirm your password.'
    } else if (confirmPassword !== password) {
      errors.confirmPassword = 'Passwords do not match.'
    }
  }

  STUDENT_SUBJECTS.forEach((subject) => {
    const score = values.scores[subject]
    if (score === undefined || score === null || Number.isNaN(score)) {
      errors[`scores.${subject}`] = `${subject} is required.`
      return
    }
    if (score < 0 || score > 100) {
      errors[`scores.${subject}`] = `${subject} must be between 0 and 100.`
    }
  })

  if (existingStudent && existingStudent.studentId === values.studentId.trim()) {
    errors.studentId = 'Student ID already exists.'
  }

  return errors
}

export function validateLoginForm(values: StudentLoginFormValues): StudentFormErrors {
  const errors: StudentFormErrors = {}

  if (!values.email.trim()) errors.email = 'Email is required.'
  if (values.email.trim() && !isValidEmail(values.email)) {
    errors.email = 'Enter a valid email address.'
  }
  if (!values.password.trim()) errors.password = 'Password is required.'

  return errors
}

export function validateProfileForm(
  values: StudentRegistrationFormValues,
): StudentFormErrors {
  return validateRegistrationForm(values)
}
