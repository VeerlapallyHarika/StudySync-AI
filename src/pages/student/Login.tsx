import { useEffect, useState, type FormEvent } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { ArrowLeft, LogIn } from 'lucide-react'
import GlassCard from '../../components/GlassCard'
import SiteLayout from '../../layouts/SiteLayout'
import usePageTitle from '../../hooks/usePageTitle'
import { getCachedStudentProfile, getCachedStudentSession, loginStudent } from '../../services/studentService'
import type { StudentLoginFormValues } from '../../types/student'
import { validateLoginForm, type StudentFormErrors } from '../../utils/studentValidation'

function createInitialState(): StudentLoginFormValues {
  return {
    email: '',
    password: '',
    rememberMe: false,
  }
}

export default function StudentLoginPage() {
  usePageTitle('Student Login')
  const navigate = useNavigate()
  const location = useLocation()
  const [formValues, setFormValues] = useState<StudentLoginFormValues>(createInitialState)
  const [errors, setErrors] = useState<StudentFormErrors>({})
  const [notice, setNotice] = useState('')
  const [successMessage] = useState(
    (location.state as { registered?: boolean } | null)?.registered
      ? 'Registration successful! Please sign in to continue.'
      : '',
  )
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    const cachedSession = getCachedStudentSession()
    const cachedProfile = getCachedStudentProfile()

    if (cachedSession?.email) {
      setFormValues((currentValues) => ({
        ...currentValues,
        email: cachedSession.email,
        rememberMe: true,
      }))
      return
    }

    if (cachedProfile?.email) {
      setFormValues((currentValues) => ({
        ...currentValues,
        email: cachedProfile.email,
      }))
    }
  }, [])

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault()
    const validationErrors = validateLoginForm(formValues)
    setErrors(validationErrors)

    if (Object.keys(validationErrors).length > 0) {
      return
    }

    setSubmitting(true)
    setNotice('')

    try {
      await loginStudent(formValues)
      navigate('/student/dashboard', { replace: true })
    } catch (error) {
      setNotice(error instanceof Error ? error.message : 'Unable to sign in right now.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <SiteLayout>
      <section className="min-h-[calc(100vh-96px)] px-6 py-14 md:py-20 flex items-center justify-center">
        <div className="w-full max-w-md space-y-8">
          <div className="flex justify-start">
            <Link
              to="/"
              className="liquid-glass rounded-full px-5 py-2 text-ivory/80 hover:text-ivory text-sm font-medium flex items-center gap-2 transition-colors"
            >
              <ArrowLeft size={16} />
              Back home
            </Link>
          </div>

          <GlassCard className="p-6 md:p-8">
            <div className="text-center mb-8">
              <h1
                className="text-4xl text-ivory mb-3 tracking-tight"
                style={{ fontFamily: "'Instrument Serif', serif" }}
              >
                Student Login
              </h1>
              <p className="text-ivory/55 text-sm leading-relaxed">
                Sign in to reach your dashboard, profile, and assigned study group.
              </p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <label className="text-ivory/60 text-xs font-medium uppercase tracking-wide">Email</label>
                <input
                  type="email"
                  value={formValues.email}
                  onChange={(event) => setFormValues((currentValues) => ({ ...currentValues, email: event.target.value }))}
                  placeholder="Enter your email"
                  className="w-full liquid-glass rounded-full px-5 py-3 bg-transparent text-ivory placeholder:text-ivory/40 text-sm outline-none"
                  required
                />
                {errors.email ? (
                  <div className="liquid-glass rounded-2xl border border-blush/35 bg-blush/12 px-4 py-2 text-xs text-blush">
                    {errors.email}
                  </div>
                ) : null}
              </div>

              <div className="space-y-2">
                <div className="flex items-center justify-between gap-4">
                  <label className="text-ivory/60 text-xs font-medium uppercase tracking-wide">Password</label>
                  <a
                    href="mailto:support@studysync.ai?subject=Student%20Password%20Reset"
                    className="text-ivory/55 text-xs hover:text-ivory transition-colors"
                  >
                    Forgot Password?
                  </a>
                </div>
                <input
                  type="password"
                  value={formValues.password}
                  onChange={(event) => setFormValues((currentValues) => ({ ...currentValues, password: event.target.value }))}
                  placeholder="Enter your password"
                  className="w-full liquid-glass rounded-full px-5 py-3 bg-transparent text-ivory placeholder:text-ivory/40 text-sm outline-none"
                  required
                />
                {errors.password ? (
                  <div className="liquid-glass rounded-2xl border border-blush/35 bg-blush/12 px-4 py-2 text-xs text-blush">
                    {errors.password}
                  </div>
                ) : null}
              </div>

              <label className="flex items-center gap-3 text-sm text-ivory/70 cursor-pointer select-none pt-1">
                <input
                  type="checkbox"
                  checked={formValues.rememberMe}
                  onChange={(event) => setFormValues((currentValues) => ({ ...currentValues, rememberMe: event.target.checked }))}
                  className="h-4 w-4 rounded border-mauve/70 bg-transparent accent-blush"
                />
                Remember Me
              </label>

              <button
                type="submit"
                disabled={submitting}
                className="w-full bg-blush rounded-full px-5 py-3 text-ink text-sm font-semibold flex items-center justify-center gap-2 hover:bg-blush/90 transition-colors disabled:opacity-70 disabled:cursor-not-allowed"
              >
                {submitting ? 'Signing In...' : 'Log In'}
                <LogIn size={16} />
              </button>

              <div className="flex items-center justify-between gap-4 text-xs text-ivory/60 pt-1">
                <Link to="/student/register" className="hover:text-ivory transition-colors">
                  New here? Register first
                </Link>
                <Link to="/student/profile" className="hover:text-ivory transition-colors">
                  Profile
                </Link>
              </div>

              {successMessage ? (
                <div className="liquid-glass rounded-2xl border border-ivory/30 bg-ivory/10 px-4 py-3 text-xs text-ivory text-center">
                  {successMessage}
                </div>
              ) : null}

              {notice ? (
                <div className="liquid-glass rounded-2xl border border-blush/35 bg-blush/12 px-4 py-3 text-xs text-blush text-center">
                  {notice}
                </div>
              ) : null}
            </form>
          </GlassCard>
        </div>
      </section>
    </SiteLayout>
  )
}
