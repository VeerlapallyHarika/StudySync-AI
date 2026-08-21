import { useEffect, useState, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { ArrowLeft, Save } from 'lucide-react'
import GlassCard from '../../components/GlassCard'
import StudentLayout from '../../layouts/StudentLayout'
import usePageTitle from '../../hooks/usePageTitle'
import { getStudentProfile, updateStudentProfile } from '../../services/studentService'
import { STUDENT_AVAILABILITY_OPTIONS, STUDENT_PREFERENCE_OPTIONS, STUDENT_SUBJECTS } from '../../utils/studentConstants'
import type { StudentFormErrors } from '../../utils/studentValidation'
import { validateProfileForm } from '../../utils/studentValidation'
import type { StudentProfileData, StudentRegistrationFormValues } from '../../types/student'
import { clearStudentSession } from '../../services/studentService'

function createDefaultProfile(): StudentRegistrationFormValues {
  return {
    fullName: '',
    studentId: '',
    email: '',
    department: '',
    year: '',
    section: '',
    availability: 'Morning',
    learningPreference: 'Mixed',
    password: '',
    confirmPassword: '',
    scores: {
      Mathematics: 0,
      Physics: 0,
      Programming: 0,
      'Database Management': 0,
      'Operating Systems': 0,
    },
  }
}

export default function StudentProfilePage() {
  usePageTitle('Student Profile')
  const [profile, setProfile] = useState<StudentProfileData | null>(null)
  const [formValues, setFormValues] = useState<StudentRegistrationFormValues>(createDefaultProfile)
  const [errors, setErrors] = useState<StudentFormErrors>({})
  const [notice, setNotice] = useState('')
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [loadError, setLoadError] = useState('')
  const navigate = useNavigate()

  const handleLogout = () => {
    clearStudentSession()
    navigate('/')
  }

  useEffect(() => {
    let mounted = true

    const loadProfile = async () => {
      setLoading(true)
      setLoadError('')

      try {
        const response = await getStudentProfile()
        if (!mounted) return

        setProfile(response)
        setFormValues({
          fullName: response.fullName,
          studentId: response.studentId,
          email: response.email,
          department: response.department,
          year: response.year,
          section: response.section,
          availability: response.availability,
          learningPreference: response.learningPreference,
          password: '',
          confirmPassword: '',
          scores: response.scores,
        })
      } catch (error) {
        if (mounted) {
          setLoadError(error instanceof Error ? error.message : 'Unable to load student profile.')
        }
      } finally {
        if (mounted) {
          setLoading(false)
        }
      }
    }

    loadProfile()

    return () => {
      mounted = false
    }
  }, [])

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
    const validationErrors = validateProfileForm(formValues)
    setErrors(validationErrors)

    if (Object.keys(validationErrors).length > 0) {
      return
    }

    setSaving(true)
    setNotice('')

    try {
      const response = await updateStudentProfile(formValues)
      setProfile(response)
      setNotice('Profile saved successfully.')
    } catch (error) {
      setNotice(error instanceof Error ? error.message : 'Unable to save profile right now.')
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return (
    <StudentLayout>
      <section className="px-6 py-14 md:py-20">
        <div className="max-w-4xl mx-auto">
          <GlassCard className="p-8 text-center text-white/70">Loading student profile...</GlassCard>
        </div>
      </section>
    </StudentLayout>
    )
  }

  if (loadError && !profile) {
    return (
    <StudentLayout>
      <section className="px-6 py-14 md:py-20">
        <div className="max-w-4xl mx-auto">
          <GlassCard className="p-8 text-center text-rose-100 border border-rose-400/25 bg-rose-500/10">
            {loadError}
          </GlassCard>
        </div>
      </section>
    </StudentLayout>
    )
  }

  const currentProfile = profile!

  return (
    <StudentLayout>
      <section className="px-6 py-14 md:py-20">
        <div className="max-w-6xl mx-auto space-y-8">
          <div className="flex justify-between items-center gap-4 flex-wrap">
            <Link
              to="/student/dashboard"
              className="liquid-glass rounded-full px-5 py-2 text-white/80 hover:text-white text-sm font-medium flex items-center gap-2 transition-colors"
            >
              <ArrowLeft size={16} />
              Back to Dashboard
            </Link>

            <button
              onClick={handleLogout}
              className="text-white/55 text-sm font-medium hover:text-white transition-colors"
            >
              Logout
            </button>
          </div>

          <div className="max-w-3xl">
            <h1 className="text-4xl md:text-5xl text-white tracking-tight" style={{ fontFamily: "'Instrument Serif', serif" }}>
              Student Profile
            </h1>
            <p className="text-white/55 text-sm mt-2">Edit the fields that feed the group-matching and dashboard APIs.</p>
          </div>

          <div className="grid grid-cols-1 xl:grid-cols-[1.2fr_0.8fr] gap-6">
            <GlassCard className="p-6 md:p-8">
              <form onSubmit={handleSubmit} className="space-y-8">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {[
                    { key: 'fullName', label: 'Name' },
                    { key: 'department', label: 'Department' },
                    { key: 'year', label: 'Year' },
                    { key: 'section', label: 'Section' },
                  ].map((field) => (
                    <div key={field.key} className="space-y-2">
                      <label className="text-white/60 text-xs font-medium uppercase tracking-wide">{field.label}</label>
                      <input
                        type="text"
                        value={formValues[field.key as keyof StudentRegistrationFormValues] as string}
                        onChange={(event) =>
                          setFormValues((currentValues) => ({
                            ...currentValues,
                            [field.key]: event.target.value,
                          }))
                        }
                        className="w-full liquid-glass rounded-full px-5 py-3 bg-transparent text-white placeholder:text-white/40 text-sm outline-none"
                        required
                      />
                      {errors[field.key] ? (
                        <div className="liquid-glass rounded-2xl border border-rose-400/25 bg-rose-500/10 px-4 py-2 text-xs text-rose-100">
                          {errors[field.key]}
                        </div>
                      ) : null}
                    </div>
                  ))}
                </div>

                <div className="space-y-4">
                  <h2 className="text-xl text-white font-semibold">Scores</h2>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {STUDENT_SUBJECTS.map((subject) => (
                      <div key={subject} className="space-y-2">
                        <label className="text-white/60 text-xs font-medium uppercase tracking-wide">{subject}</label>
                        <input
                          type="number"
                          min="0"
                          max="100"
                          value={formValues.scores[subject]}
                          onChange={(event) => updateScore(subject, event.target.value)}
                          className="w-full liquid-glass rounded-full px-5 py-3 bg-transparent text-white placeholder:text-white/40 text-sm outline-none"
                          required
                        />
                        {errors[`scores.${subject}`] ? (
                          <div className="liquid-glass rounded-2xl border border-rose-400/25 bg-rose-500/10 px-4 py-2 text-xs text-rose-100">
                            {errors[`scores.${subject}`]}
                          </div>
                        ) : null}
                      </div>
                    ))}
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <h2 className="text-xl text-white font-semibold">Availability</h2>
                    <div className="flex flex-wrap gap-3">
                      {STUDENT_AVAILABILITY_OPTIONS.map((option) => (
                        <button
                          key={option}
                          type="button"
                          onClick={() => setFormValues((currentValues) => ({ ...currentValues, availability: option }))}
                          className={`rounded-full px-5 py-3 text-sm font-medium transition-colors ${
                            formValues.availability === option
                              ? 'bg-white text-black'
                              : 'liquid-glass text-white hover:bg-white/5'
                          }`}
                        >
                          {option}
                        </button>
                      ))}
                    </div>
                  </div>

                  <div className="space-y-4">
                    <h2 className="text-xl text-white font-semibold">Learning Preference</h2>
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
                              ? 'bg-white text-black'
                              : 'liquid-glass text-white hover:bg-white/5'
                          }`}
                        >
                          {option}
                        </button>
                      ))}
                    </div>
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={saving}
                  className="w-full bg-white rounded-full px-5 py-3 text-black text-sm font-semibold flex items-center justify-center gap-2 hover:bg-white/90 transition-colors disabled:opacity-70 disabled:cursor-not-allowed"
                >
                  {saving ? 'Saving...' : 'Save'}
                  <Save size={16} />
                </button>

                {notice ? (
                  <div className="liquid-glass rounded-2xl border border-emerald-400/25 bg-emerald-500/10 px-4 py-3 text-xs text-emerald-100 text-center">
                    {notice}
                  </div>
                ) : null}
              </form>
            </GlassCard>

            <div className="space-y-6">
              <GlassCard className="p-6">
                <p className="text-white/55 text-xs uppercase tracking-wide mb-3">Profile Snapshot</p>
                <div className="space-y-3 text-white/75 text-sm">
                  <div className="liquid-glass rounded-2xl p-4">Student ID: {currentProfile.studentId}</div>
                  <div className="liquid-glass rounded-2xl p-4">Email: {currentProfile.email}</div>
                  <div className="liquid-glass rounded-2xl p-4">Availability: {currentProfile.availability}</div>
                  <div className="liquid-glass rounded-2xl p-4">Preference: {currentProfile.learningPreference}</div>
                </div>
              </GlassCard>

              <GlassCard className="p-6">
                <p className="text-white/55 text-xs uppercase tracking-wide mb-3">Ready for Backend</p>
                <p className="text-white/70 text-sm leading-relaxed">
                  These fields map directly to the Django student profile endpoints and can be persisted without changing the UI.
                </p>
              </GlassCard>
            </div>
          </div>
        </div>
      </section>
    </StudentLayout>
  )
}