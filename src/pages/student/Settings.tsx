import { useEffect, useState, type FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { ArrowLeft, BellRing, KeyRound, Save, UserRound } from 'lucide-react'
import GlassCard from '../../components/GlassCard'
import StudentLayout from '../../layouts/StudentLayout'
import usePageTitle from '../../hooks/usePageTitle'
import { changeStudentPassword, getCachedStudentProfile } from '../../services/studentService'
import { STUDENT_STORAGE_KEYS } from '../../utils/studentConstants'
import { DEFAULT_STUDENT_NOTIFICATION_PREFERENCES, type StudentNotificationPreferences } from '../../types/student'

const PREFERENCE_OPTIONS: Array<{ key: keyof StudentNotificationPreferences; label: string; description: string }> = [
  { key: 'emailNotifications', label: 'Email Notifications', description: 'Receive important account updates by email.' },
  { key: 'groupUpdates', label: 'Group Updates', description: 'Get notified when your study group changes.' },
  { key: 'aiInsights', label: 'AI Insights', description: 'Weekly AI-generated performance insights.' },
  { key: 'weeklyDigest', label: 'Weekly Digest', description: 'A summary of your academic progress each week.' },
]

export default function StudentSettingsPage() {
  usePageTitle('Settings')
  const [currentPassword, setCurrentPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [saving, setSaving] = useState(false)
  const [notice, setNotice] = useState('')
  const [error, setError] = useState('')

  const [preferences, setPreferences] = useState<StudentNotificationPreferences>(DEFAULT_STUDENT_NOTIFICATION_PREFERENCES)
  const [prefsNotice, setPrefsNotice] = useState('')
  const cachedProfile = getCachedStudentProfile()

  useEffect(() => {
    if (typeof window === 'undefined') return
    const raw = window.localStorage.getItem(STUDENT_STORAGE_KEYS.preferences)
    if (!raw) return
    try {
      setPreferences((current) => ({ ...current, ...(JSON.parse(raw) as Partial<StudentNotificationPreferences>) }))
    } catch {
      // ignore corrupt storage
    }
  }, [])

  const togglePreference = (key: keyof StudentNotificationPreferences) => {
    const next = { ...preferences, [key]: !preferences[key] }
    setPreferences(next)
    window.localStorage.setItem(STUDENT_STORAGE_KEYS.preferences, JSON.stringify(next))
    setPrefsNotice('Notification preferences saved.')
    window.setTimeout(() => setPrefsNotice(''), 3000)
  }

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault()
    setNotice('')
    setError('')

    if (newPassword.length < 6) {
      setError('New password must be at least 6 characters.')
      return
    }
    if (newPassword !== confirmPassword) {
      setError('New password and confirmation do not match.')
      return
    }

    setSaving(true)
    try {
      await changeStudentPassword(currentPassword, newPassword)
      setNotice('Password updated successfully.')
      setCurrentPassword('')
      setNewPassword('')
      setConfirmPassword('')
    } catch (changeError) {
      setError(changeError instanceof Error ? changeError.message : 'Unable to change password.')
    } finally {
      setSaving(false)
    }
  }

  const inputClass =
    'w-full liquid-glass rounded-2xl px-4 py-3 bg-transparent text-white placeholder:text-white/40 text-sm outline-none'
  const labelClass = 'block text-white/55 text-xs uppercase tracking-wide mb-2'

  return (
    <StudentLayout>
      <section className="px-6 py-14 md:py-20">
        <div className="max-w-3xl mx-auto space-y-8">
          <div>
            <Link
              to="/student/dashboard"
              className="liquid-glass rounded-full px-5 py-2 text-white/80 hover:text-white text-sm font-medium flex items-center gap-2 transition-colors"
            >
              <ArrowLeft size={16} />
              Back to Dashboard
            </Link>
          </div>

          <div>
            <h1 className="text-4xl md:text-5xl text-white tracking-tight" style={{ fontFamily: "'Instrument Serif', serif" }}>
              Settings
            </h1>
            <p className="text-white/55 text-sm mt-2">Manage your account, preferences and credentials.</p>
          </div>

          <GlassCard className="p-6 md:p-8">
            <div className="flex flex-wrap items-center gap-4">
              <div className="w-12 h-12 rounded-full bg-white text-black flex items-center justify-center font-semibold flex-shrink-0">
                {(cachedProfile?.fullName ?? 'S').charAt(0)}
              </div>
              <div className="min-w-0 flex-1">
                <p className="text-white font-medium">{cachedProfile?.fullName ?? 'Student'}</p>
                <p className="text-white/50 text-sm truncate">{cachedProfile?.email ?? 'Sign in to view your profile'}</p>
              </div>
              <Link
                to="/student/profile"
                className="inline-flex items-center gap-2 rounded-full border border-white/15 text-white px-5 py-2.5 text-sm font-medium transition-colors hover:bg-white/5"
              >
                <UserRound size={15} />
                View Profile
              </Link>
            </div>
          </GlassCard>

          <GlassCard className="p-6 md:p-8">
            <div className="flex items-center gap-3 mb-6 text-white">
              <BellRing size={18} className="text-violet-400" />
              <h2 className="text-2xl" style={{ fontFamily: "'Instrument Serif', serif" }}>
                Notification Preferences
              </h2>
            </div>

            {prefsNotice ? (
              <div className="liquid-glass rounded-2xl border border-emerald-400/25 px-4 py-3 text-xs text-emerald-100 mb-5">
                {prefsNotice}
              </div>
            ) : null}

            <div className="space-y-3">
              {PREFERENCE_OPTIONS.map((option) => {
                const enabled = preferences[option.key]
                return (
                  <button
                    key={option.key}
                    type="button"
                    onClick={() => togglePreference(option.key)}
                    aria-pressed={enabled}
                    className="w-full flex items-center gap-4 liquid-glass rounded-2xl p-4 text-left hover:bg-white/5 transition-colors"
                  >
                    <span className="flex-1">
                      <span className="block text-white text-sm font-medium">{option.label}</span>
                      <span className="block text-white/50 text-xs mt-0.5">{option.description}</span>
                    </span>
                    <span
                      className={`w-12 h-7 rounded-full flex items-center px-1 transition-colors ${
                        enabled ? 'bg-white' : 'bg-white/15'
                      }`}
                      aria-hidden="true"
                    >
                      <span
                        className={`w-5 h-5 rounded-full transition-transform ${
                          enabled ? 'translate-x-5 bg-black' : 'translate-x-0 bg-white/60'
                        }`}
                      />
                    </span>
                  </button>
                )
              })}
            </div>
          </GlassCard>

          <GlassCard className="p-6 md:p-8">
            <div className="flex items-center gap-3 mb-6 text-white">
              <KeyRound size={18} className="text-cyan-400" />
              <h2 className="text-2xl" style={{ fontFamily: "'Instrument Serif', serif" }}>
                Change Password
              </h2>
            </div>

            {notice ? (
              <div className="liquid-glass rounded-2xl border border-emerald-400/25 px-4 py-3 text-xs text-emerald-100 mb-5">
                {notice}
              </div>
            ) : null}
            {error ? (
              <div className="liquid-glass rounded-2xl border border-rose-400/25 px-4 py-3 text-xs text-rose-100 mb-5">
                {error}
              </div>
            ) : null}

            <form onSubmit={handleSubmit} className="space-y-5">
              <div>
                <label className={labelClass} htmlFor="currentPassword">Current Password</label>
                <input
                  id="currentPassword"
                  type="password"
                  value={currentPassword}
                  onChange={(event) => setCurrentPassword(event.target.value)}
                  required
                  className={inputClass}
                />
              </div>
              <div>
                <label className={labelClass} htmlFor="newPassword">New Password</label>
                <input
                  id="newPassword"
                  type="password"
                  value={newPassword}
                  onChange={(event) => setNewPassword(event.target.value)}
                  required
                  className={inputClass}
                />
              </div>
              <div>
                <label className={labelClass} htmlFor="confirmPassword">Confirm New Password</label>
                <input
                  id="confirmPassword"
                  type="password"
                  value={confirmPassword}
                  onChange={(event) => setConfirmPassword(event.target.value)}
                  required
                  className={inputClass}
                />
              </div>

              <button
                type="submit"
                disabled={saving}
                className="rounded-full px-6 py-3 bg-white text-black text-sm font-medium flex items-center gap-2 transition-colors hover:bg-white/90 disabled:opacity-40 disabled:cursor-not-allowed"
              >
                <Save size={16} />
                {saving ? 'Saving...' : 'Update Password'}
              </button>
            </form>
          </GlassCard>
        </div>
      </section>
    </StudentLayout>
  )
}
