import type { ReactNode } from 'react'
import { Navigate } from 'react-router-dom'
import { getStudentToken } from '../../utils/authStorage'
import { getCachedStudentSession } from '../../services/studentService'

export default function RequireStudent({ children }: { children: ReactNode }) {
  const token = getStudentToken()
  const session = getCachedStudentSession()

  if (!token && !session) {
    return <Navigate to="/student/login" replace />
  }

  return <>{children}</>
}
