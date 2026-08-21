import { API_ENDPOINTS } from '../api/endpoints'
import {
  STUDENT_STORAGE_KEYS,
} from '../utils/studentConstants'
import {
  clearStudentTokens,
  getStudentRefreshToken,
  getStudentToken,
  saveStudentTokens,
} from '../utils/authStorage'
import type {
  ChatMessageItem,
  ResourceType,
  SharedResourceItem,
  StudentDashboardData,
  StudentGroupDetail,
  StudentGroupStatus,
  StudentInsights,
  StudentLoginFormValues,
  StudentProfileData,
  StudentProfileUpdateValues,
  StudentRegistrationFormValues,
} from '../types/student'
import type { NotificationItem } from '../types/admin'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

const STORAGE_KEYS = STUDENT_STORAGE_KEYS

class StudentServiceError extends Error {
  status?: number

  constructor(message: string, status?: number) {
    super(message)
    this.name = 'StudentServiceError'
    this.status = status
  }
}

function authHeaders(extra?: Record<string, string>): Record<string, string> {
  const token = getStudentToken()
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...(extra ?? {}),
  }
}

async function requestJson<T>(path: string, init?: RequestInit, _retry = false): Promise<T> {
  const isAuthEndpoint = [
    API_ENDPOINTS.studentLogin,
    API_ENDPOINTS.studentRegister,
    '/api/student/refresh/',
  ].includes(path)

  let headers = authHeaders(init?.headers as Record<string, string>)
  if (isAuthEndpoint) {
    headers = { 'Content-Type': 'application/json', ...(init?.headers as Record<string, string> ?? {}) }
  }

  let response: Response
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...init,
      headers,
    })
  } catch {
    // Network-level failure: backend not running, wrong port, DNS failure, etc.
    throw new StudentServiceError(
      'Unable to connect to the server. Please make sure the backend is running.',
      0,
    )
  }

  if (response.status === 401 && !_retry && !isAuthEndpoint) {
    const refresh = getStudentRefreshToken()
    if (refresh) {
      try {
        const refreshResponse = await fetch(`${API_BASE_URL}/api/student/refresh/`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ refresh })
        })
        
        if (refreshResponse.ok) {
          const newTokens = await refreshResponse.json()
          saveStudentTokens({ access: newTokens.access, refresh: newTokens.refresh })
          return requestJson<T>(path, init, true)
        }
      } catch {
        // Fall through to clearing tokens
      }
    }
    
    clearStudentTokens()
    if (typeof window !== 'undefined') {
      window.sessionStorage.removeItem(STORAGE_KEYS.session)
      window.localStorage.removeItem(STORAGE_KEYS.session)
    }
  }

  if (!response.ok) {
    let message = ''
    try {
      const body = await response.json()
      // Django REST Framework can return errors as { message }, { detail },
      // { non_field_errors: [...] }, or { field: [...] } shapes.
      if (body.message) {
        message = body.message
      } else if (body.detail) {
        message = body.detail
      } else if (body.non_field_errors) {
        message = Array.isArray(body.non_field_errors)
          ? body.non_field_errors.join(' ')
          : String(body.non_field_errors)
      } else {
        // Flatten any field-level validation errors into one readable string.
        const fieldErrors = Object.entries(body)
          .map(([field, errs]) => {
            const text = Array.isArray(errs) ? errs.join(', ') : String(errs)
            return `${field}: ${text}`
          })
          .join(' | ')
        message = fieldErrors
      }
    } catch {
      // fall through to the status-based generic message
    }

    // Override with cleaner messages for well-known status codes.
    if (!message) {
      if (response.status === 400) {
        message = 'Invalid input. Please check the form and try again.'
      } else if (response.status === 409) {
        message = 'An account with this email or student ID already exists.'
      } else if (response.status === 429) {
        message = 'Too many attempts. Please wait a moment and try again.'
      } else if (response.status >= 500) {
        message = 'Server error. Please try again later.'
      } else {
        message = `Request failed with status ${response.status}`
      }
    } else if (response.status === 409) {
      message = 'An account with this email or student ID already exists.'
    }

    throw new StudentServiceError(message, response.status)
  }

  if (response.status === 204) {
    return undefined as T
  }

  return response.json() as Promise<T>
}

function readStorage<T>(key: string): T | null {
  if (typeof window === 'undefined') return null

  const raw = window.localStorage.getItem(key)
  if (!raw) return null

  try {
    return JSON.parse(raw) as T
  } catch {
    return null
  }
}

function writeStorage<T>(key: string, value: T) {
  if (typeof window === 'undefined') return
  window.localStorage.setItem(key, JSON.stringify(value))
}

function writeSession<T>(key: string, value: T) {
  if (typeof window === 'undefined') return
  window.sessionStorage.setItem(key, JSON.stringify(value))
}

function writePersistent<T>(key: string, value: T) {
  if (typeof window === 'undefined') return
  window.localStorage.setItem(key, JSON.stringify(value))
}

function readSession<T>(key: string): T | null {
  if (typeof window === 'undefined') return null

  const raw = window.sessionStorage.getItem(key)
  if (!raw) return null

  try {
    return JSON.parse(raw) as T
  } catch {
    return null
  }
}

interface AuthResponse {
  access: string
  refresh: string
}

function storeSession(profile: StudentProfileData, tokens: AuthResponse, rememberMe = false) {
  const sessionPayload = { email: profile.email, studentId: profile.studentId }
  if (rememberMe) {
    writePersistent(STORAGE_KEYS.session, sessionPayload)
  } else {
    writeSession(STORAGE_KEYS.session, sessionPayload)
  }
  saveStudentTokens({ access: tokens.access, refresh: tokens.refresh })
}

function persistAuthenticated(profile: StudentProfileData, tokens: AuthResponse, rememberMe = false) {
  writeStorage(STORAGE_KEYS.profile, profile)
  storeSession(profile, tokens, rememberMe)
  return profile
}

export async function registerStudent(values: StudentRegistrationFormValues): Promise<StudentProfileData> {
  return requestJson<StudentProfileData>(API_ENDPOINTS.studentRegister, {
    method: 'POST',
    body: JSON.stringify(values),
  })
}

export async function loginStudent(values: StudentLoginFormValues): Promise<StudentProfileData> {
  const response = await requestJson<StudentProfileData & AuthResponse>(API_ENDPOINTS.studentLogin, {
    method: 'POST',
    body: JSON.stringify({ email: values.email, password: values.password }),
  })
  return persistAuthenticated(response, { access: response.access, refresh: response.refresh }, values.rememberMe)
}

export async function getStudentProfile(): Promise<StudentProfileData> {
  if (!getStudentToken()) {
    const cached = readStorage<StudentProfileData>(STORAGE_KEYS.profile)
    if (cached) return cached
    throw new StudentServiceError('Please log in to view your profile.', 401)
  }

  try {
    const profile = await requestJson<StudentProfileData>(API_ENDPOINTS.studentProfile)
    writeStorage(STORAGE_KEYS.profile, profile)
    return profile
  } catch (error) {
    if (error instanceof StudentServiceError && error.status === 401) {
      clearStudentTokens()
      throw error
    }
    const cached = readStorage<StudentProfileData>(STORAGE_KEYS.profile)
    if (cached) return cached
    throw error
  }
}

export async function updateStudentProfile(values: StudentProfileUpdateValues): Promise<StudentProfileData> {
  const { password: _password, confirmPassword: _confirmPassword, ...payload } = values
  const response = await requestJson<StudentProfileData>(API_ENDPOINTS.studentProfile, {
    method: 'PUT',
    body: JSON.stringify(payload),
  })
  writeStorage(STORAGE_KEYS.profile, response)
  return response
}

export async function getStudentDashboard(): Promise<StudentDashboardData> {
  return requestJson<StudentDashboardData>(API_ENDPOINTS.studentDashboard)
}

export async function getStudentInsights(): Promise<StudentInsights> {
  return requestJson<StudentInsights>(API_ENDPOINTS.studentInsights)
}

export async function getStudentGroup(): Promise<StudentGroupDetail | null> {
  const payload = await requestJson<{ group: StudentGroupDetail | null }>(API_ENDPOINTS.studentGroup)
  return payload.group
}

export async function getStudentGroupStatus(): Promise<StudentGroupStatus> {
  const payload = await requestJson<{ status: StudentGroupStatus }>(API_ENDPOINTS.studentGroupStatus)
  return payload.status
}

export interface GenerateStudentGroupResult {
  generated: boolean
  assigned: boolean
  group: StudentGroupDetail | null
  status: StudentGroupStatus
  message?: string
}

export async function generateStudentGroup(): Promise<GenerateStudentGroupResult> {
  return requestJson<GenerateStudentGroupResult>(API_ENDPOINTS.studentGroupGenerate, {
    method: 'POST',
    body: JSON.stringify({}),
  })
}

export async function sendGroupChatMessage(message: string): Promise<ChatMessageItem> {
  return requestJson<ChatMessageItem>(API_ENDPOINTS.studentGroupChat, {
    method: 'POST',
    body: JSON.stringify({ message }),
  })
}

export interface ShareResourceValues {
  title: string
  resourceType: ResourceType
  url?: string
  file?: File | null
}

export async function shareGroupResource(values: ShareResourceValues): Promise<SharedResourceItem> {
  const token = getStudentToken()
  const form = new FormData()
  form.append('title', values.title)
  form.append('resourceType', values.resourceType)
  if (values.url) form.append('url', values.url)
  if (values.file) form.append('file', values.file)

  const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.studentGroupResources}`, {
    method: 'POST',
    headers: token ? { Authorization: `Bearer ${token}` } : {},
    body: form,
  })

  if (!response.ok) {
    let message = ''
    try {
      const body = await response.json()
      message = body.message ?? body.detail ?? ''
    } catch {
      // fall through to the generic message
    }
    throw new StudentServiceError(message || `Request failed with status ${response.status}`, response.status)
  }

  return response.json() as Promise<SharedResourceItem>
}

export async function getStudentResources(): Promise<SharedResourceItem[]> {
  const payload = await requestJson<{ resources: SharedResourceItem[] }>(API_ENDPOINTS.studentResources)
  return payload.resources
}

export async function changeStudentPassword(currentPassword: string, newPassword: string): Promise<void> {
  await requestJson<{ detail: string }>(API_ENDPOINTS.studentChangePassword, {
    method: 'POST',
    body: JSON.stringify({ currentPassword, newPassword }),
  })
}

export async function getStudentNotifications(): Promise<NotificationItem[]> {
  const payload = await requestJson<{ notifications: NotificationItem[] }>(API_ENDPOINTS.notifications)
  return payload.notifications
}

export async function markStudentNotificationRead(id: number): Promise<void> {
  await requestJson<void>(API_ENDPOINTS.notificationRead(id), { method: 'POST' })
}

export async function markAllStudentNotificationsRead(): Promise<number> {
  const payload = await requestJson<{ marked: number }>(API_ENDPOINTS.notificationReadAll, { method: 'POST' })
  return payload.marked
}

export async function clearStudentNotifications(): Promise<number> {
  const payload = await requestJson<{ deleted: number }>(API_ENDPOINTS.notifications, { method: 'DELETE' })
  return payload.deleted
}

export function getCachedStudentSession() {
  return (
    readStorage<{ email: string; studentId: string }>(STORAGE_KEYS.session) ??
    readSession<{ email: string; studentId: string }>(STORAGE_KEYS.session)
  )
}

export function getCachedStudentProfile() {
  return readStorage<StudentProfileData>(STORAGE_KEYS.profile)
}

export function clearStudentSession() {
  if (typeof window === 'undefined') return
  const refresh = getStudentRefreshToken()
  if (refresh) {
    fetch(`${API_BASE_URL}${API_ENDPOINTS.studentLogout}`, {
      method: 'POST',
      headers: authHeaders(),
      body: JSON.stringify({ refresh }),
    }).catch(() => undefined)
  }
  window.sessionStorage.removeItem(STORAGE_KEYS.session)
  window.localStorage.removeItem(STORAGE_KEYS.session)
  clearStudentTokens()
}
