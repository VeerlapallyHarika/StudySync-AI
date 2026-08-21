import { STUDENT_STORAGE_KEYS } from './studentConstants'

export interface SessionTokens {
  access: string
  refresh: string
}

function readTokens(key: string): SessionTokens | null {
  if (typeof window === 'undefined') return null
  try {
    const raw = window.localStorage.getItem(key)
    return raw ? (JSON.parse(raw) as SessionTokens) : null
  } catch {
    return null
  }
}

function writeTokens(key: string, tokens: SessionTokens) {
  if (typeof window === 'undefined') return
  window.localStorage.setItem(key, JSON.stringify(tokens))
}

function clearTokens(key: string) {
  if (typeof window === 'undefined') return
  window.localStorage.removeItem(key)
}

export function getStudentToken(): string | null {
  return readTokens(STUDENT_STORAGE_KEYS.tokens)?.access ?? null
}

export function getStudentRefreshToken(): string | null {
  return readTokens(STUDENT_STORAGE_KEYS.tokens)?.refresh ?? null
}

export function saveStudentTokens(tokens: SessionTokens) {
  writeTokens(STUDENT_STORAGE_KEYS.tokens, tokens)
}

export function clearStudentTokens() {
  clearTokens(STUDENT_STORAGE_KEYS.tokens)
}
