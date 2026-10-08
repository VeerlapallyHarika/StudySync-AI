import { useState, type FormEvent } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { ArrowLeft, Eye, EyeOff, Lock, UserPlus } from 'lucide-react'
import GlassCard from '../../components/GlassCard'
import SiteLayout from '../../layouts/SiteLayout'
import usePageTitle from '../../hooks/usePageTitle'
import {
  STUDENT_AVAILABILITY_OPTIONS,
  STUDENT_PREFERENCE_OPTIONS,
  STUDENT_SUBJECTS,
} from '../../utils/studentConstants'
import { registerStudent } from '../../services/studentService'
import type { StudentFormErrors } from '../../utils/studentValidation'
import { validateRegistrationForm } from '../../utils/studentValidation'
import type { StudentRegistrationFormValues } from '../../types/student'

function createEmptyScores(): StudentRegistrationFormValues['scores'] {
  return {
    Mathematics: 0,
    Physics: 0,
    Programming: 0,
    'Database Management': 0,
    'Operating Systems': 0,
  }
}

function createInitialState(): StudentRegistrationFormValues {
  return {
    fullName: '',
    studentId: '',
    email: '',
    department: '',
    year: '',
    section: '',
    scores: createEmptyScores(),
    availability: 'Morning',
    learningPreference: 'Mixed',
    password: '',
    confirmPassword: '',
  }
}

export default function StudentRegisterPage() {
  usePageTitle('Student Registration')
  const navigate = useNavigate()
  const [formValues, setFormValues] = useState<StudentRegistrationFormValues>(createInitialState)
  const [errors, setErrors] = useState<StudentFormErrors>({})
  const [submitMessage, setSubmitMessage] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)

  // Form should always start completely empty on a new registration.
  // We do not load from cache here.

  const updateScore = (subject: keyof StudentRegistrationFormValues['scores'], value: string) => {
    setFormValues((currentValues) => ({
      ...currentValues,
      scores: {
        ...currentValues.scores,
        [subject]: Number(value),
      },
    }))
  }

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault()
    const validationErrors = validateRegistrationForm(formValues, null, { requirePassword: true })
    setErrors(validationErrors)

    if (Object.keys(validationErrors).length > 0) {
      return
    }

    setSubmitting(true)
    setSubmitMessage('')

    try {
      await registerStudent(formValues)
      setFormValues(createInitialState())
      navigate('/student/login', { replace: true, state: { registered: true } })
    } catch (error) {
      setSubmitMessage(error instanceof Error ? error.message : 'Unable to register student right now.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <SiteLayout>
      <section className="px-6 py-14 md:py-20">
        <div className="max-w-6xl mx-auto space-y-8">
          <div className="flex justify-start">
            <Link
              to="/"
              className="liquid-glass rounded-full px-5 py-2 text-ivory/80 hover:text-ivory text-sm font-medium flex items-center gap-2 transition-colors"
            >
              <ArrowLeft size={16} />
              Back home
            </Link>
          </div>

          <div className="max-w-3xl mx-auto text-center">
            <h1
              className="text-4xl md:text-5xl text-ivory mb-4 tracking-tight"
              style={{ fontFamily: "'Instrument Serif', serif" }}
            >
              Student Registration
            </h1>
            <p className="text-ivory/60 text-base leading-relaxed">
              Capture academic data once and use it to build balanced study groups automatically.
            </p>
          </div>

          <GlassCard className="p-6 md:p-8">
            <form onSubmit={handleSubmit} className="space-y-8">
              <div className="space-y-4">
                <div className="flex items-center justify-between gap-4 flex-wrap">
                  <div>
                    <h2 className="text-xl text-ivory font-semibold">Personal Information</h2>
                    <p className="text-ivory/50 text-sm">Student identity and academic context.</p>
                  </div>
                  <Link
                    to="/student/login"
                    className="text-ivory/70 text-sm font-medium hover:text-ivory transition-colors"
                  >
                    Already registered? Login
                  </Link>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {[
                    { key: 'fullName', label: 'Full Name', autoComplete: 'name' },
                    { key: 'studentId', label: 'Student ID', autoComplete: 'off' },
                    { key: 'email', label: 'Email', autoComplete: 'email' },
                    { key: 'department', label: 'Department', autoComplete: 'organization-title' },
                    { key: 'year', label: 'Year', autoComplete: 'off' },
                    { key: 'section', label: 'Section', autoComplete: 'off' },
                  ].map((field) => (
                    <div key={field.key} className="space-y-2">
                      <label className="text-ivory/60 text-xs font-medium uppercase tracking-wide">
                        {field.label}
                      </label>
                      <input
                        type={field.key === 'email' ? 'email' : 'text'}
                        autoComplete={field.autoComplete}
                        value={formValues[field.key as keyof typeof formValues] as string}
                        onChange={(event) =>
                          setFormValues((currentValues) => ({
                            ...currentValues,
                            [field.key]: event.target.value,
                          }))
                        }
                        placeholder={`Enter ${field.label.toLowerCase()}`}
                        className="w-full liquid-glass rounded-full px-5 py-3 bg-transparent text-ivory placeholder:text-ivory/40 text-sm outline-none"
                        required
                      />
                      {errors[field.key] ? (
                        <div className="liquid-glass rounded-2xl border border-blush/35 bg-blush/12 px-4 py-2 text-xs text-blush">
                          {errors[field.key]}
                        </div>
                      ) : null}
                    </div>
                  ))}
                </div>
              </div>

              <div className="space-y-4">
                <div className="flex items-center gap-3 text-ivory">
                  <Lock size={18} className="text-blush" />
                  <h2 className="text-xl font-semibold">Account Security</h2>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {[
                    {
                      key: 'password',
                      label: 'Password',
                      placeholder: 'At least 8 characters',
                      show: showPassword,
                      setShow: setShowPassword,
                    },
                    {
                      key: 'confirmPassword',
                      label: 'Confirm Password',
                      placeholder: 'Re-enter your password',
                      show: showConfirmPassword,
                      setShow: setShowConfirmPassword,
                    },
                  ].map((field) => (
                    <div key={field.key} className="space-y-2">
                      <label className="text-ivory/60 text-xs font-medium uppercase tracking-wide">
                        {field.label}
                      </label>
                      <div className="relative">
                        <input
                          type={field.show ? 'text' : 'password'}
                          autoComplete="new-password"
                          value={formValues[field.key as keyof typeof formValues] as string}
                          onChange={(event) =>
                            setFormValues((currentValues) => ({
                              ...currentValues,
                              [field.key]: event.target.value,
                            }))
                          }
                          placeholder={field.placeholder}
                          className="w-full liquid-glass rounded-full px-5 py-3 pr-12 bg-transparent text-ivory placeholder:text-ivory/40 text-sm outline-none"
                          required
                        />
                        <button
                          type="button"
                          onClick={() => field.setShow(!field.show)}
                          className="absolute right-4 top-1/2 -translate-y-1/2 text-ivory/50 hover:text-ivory transition-colors z-10"
                          aria-label={field.show ? `Hide ${field.label}` : `Show ${field.label}`}
                        >
                          {field.show ? <EyeOff size={16} /> : <Eye size={16} />}
                        </button>
                      </div>
                      {errors[field.key] ? (
                        <div className="liquid-glass rounded-2xl border border-blush/35 bg-blush/12 px-4 py-2 text-xs text-blush">
                          {errors[field.key]}
                        </div>
                      ) : null}
                    </div>
                  ))}
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="flex items-center gap-3 text-ivory">
                  <UserPlus size={18} className="text-blush" />
                  <h2 className="text-xl font-semibold">Academic Information</h2>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {STUDENT_SUBJECTS.map((field) => (
                    <div key={field} className="space-y-2">
                      <label className="text-ivory/60 text-xs font-medium uppercase tracking-wide">
                        {field}
                      </label>
                      <input
                        type="number"
                        min="0"
                        max="100"
                        value={formValues.scores[field]}
                        onChange={(event) => updateScore(field, event.target.value)}
                        placeholder="0 - 100"
                        className="w-full liquid-glass rounded-full px-5 py-3 bg-transparent text-ivory placeholder:text-ivory/40 text-sm outline-none"
                        required
                      />
                      {errors[`scores.${field}`] ? (
                        <div className="liquid-glass rounded-2xl border border-blush/35 bg-blush/12 px-4 py-2 text-xs text-blush">
                          {errors[`scores.${field}`]}
                        </div>
                      ) : null}
                    </div>
                  ))}
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <h2 className="text-xl text-ivory font-semibold">Availability</h2>
                  <div className="flex flex-wrap gap-3">
                    {STUDENT_AVAILABILITY_OPTIONS.map((option) => (
                      <button
                        key={option}
                        type="button"
                        onClick={() => setFormValues((currentValues) => ({ ...currentValues, availability: option }))}
                        className={`rounded-full px-5 py-3 text-sm font-medium transition-colors ${
                          formValues.availability === option
                            ? 'bg-blush text-ink'
                            : 'liquid-glass text-ivory hover:bg-mauve/20'
                        }`}
                      >
                        {option}
                      </button>
                    ))}
                  </div>
                  {errors.availability ? (
                    <div className="liquid-glass rounded-2xl border border-blush/35 bg-blush/12 px-4 py-2 text-xs text-blush">
                      {errors.availability}
                    </div>
                  ) : null}
                </div>

                <div className="space-y-4">
                  <h2 className="text-xl text-ivory font-semibold">Learning Preference</h2>
                  <div className="flex flex-wrap gap-3">
                    {STUDENT_PREFERENCE_OPTIONS.map((option) => (
                      <button
                        key={option}
                        type="button"
                        onClick={() =>
                          setFormValues((currentValues) => ({ ...currentValues, learningPreference: option }))
                        }
                        className={`rounded-full px-5 py-3 text-sm font-medium transition-colors ${
                          formValues.learningPreference === option
                            ? 'bg-blush text-ink'
                            : 'liquid-glass text-ivory hover:bg-mauve/20'
                        }`}
                      >
                        {option}
                      </button>
                    ))}
                  </div>
                  {errors.learningPreference ? (
                    <div className="liquid-glass rounded-2xl border border-blush/35 bg-blush/12 px-4 py-2 text-xs text-blush">
                      {errors.learningPreference}
                    </div>
                  ) : null}
                </div>
              </div>

              <button
                type="submit"
                disabled={submitting}
                className="w-full bg-blush rounded-full px-5 py-3 text-ink text-sm font-semibold flex items-center justify-center gap-2 hover:bg-blush/90 transition-colors disabled:opacity-70 disabled:cursor-not-allowed"
              >
                {submitting ? 'Registering...' : 'Register'}
              </button>

              {submitMessage ? (
                <div className="liquid-glass rounded-2xl border border-blush/35 bg-blush/12 px-4 py-3 text-xs text-blush text-center">
                  {submitMessage}
                </div>
              ) : null}
            </form>
          </GlassCard>
        </div>
      </section>
    </SiteLayout>
  )
}
