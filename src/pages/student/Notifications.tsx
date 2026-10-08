import { useCallback, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { ArrowLeft, BellOff, CheckCheck, Inbox } from 'lucide-react'
import GlassCard from '../../components/GlassCard'
import StudentLayout from '../../layouts/StudentLayout'
import ActionButton from '../../components/student/ActionButton'
import usePageTitle from '../../hooks/usePageTitle'
import {
  clearStudentNotifications,
  getStudentNotifications,
  markAllStudentNotificationsRead,
} from '../../services/studentService'
import type { NotificationItem } from '../../types/admin'

const toneClasses: Record<NotificationItem['tone'], string> = {
  info: 'bg-mauve/30 text-ivory/90 border-mauve/50',
  success: 'bg-ivory/10 text-ivory border-ivory/25',
  warning: 'bg-plum/80 text-ivory/90 border-mauve/60',
}

export default function StudentNotificationsPage() {
  usePageTitle('Notifications')
  const [notifications, setNotifications] = useState<NotificationItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const load = useCallback(async () => {
    setLoading(true)
    setError('')
    try {
      setNotifications(await getStudentNotifications())
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : 'Unable to load notifications.')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    load()
  }, [load])

  const handleMarkAll = async () => {
    await markAllStudentNotificationsRead()
    setNotifications((current) => current.map((item) => ({ ...item, read: true })))
  }

  const handleClear = async () => {
    await clearStudentNotifications()
    setNotifications([])
  }

  const unread = notifications.filter((item) => !item.read).length

  return (
    <StudentLayout>
      <section className="px-6 py-14 md:py-20">
        <div className="max-w-4xl mx-auto space-y-8">
          <div className="flex justify-between items-center gap-4 flex-wrap">
            <Link
              to="/student/dashboard"
              className="liquid-glass rounded-full px-5 py-2 text-ivory/80 hover:text-ivory text-sm font-medium flex items-center gap-2 transition-colors"
            >
              <ArrowLeft size={16} />
              Back to Dashboard
            </Link>

            <div className="flex gap-3">
              <ActionButton
                label="Mark all read"
                icon={<CheckCheck size={16} />}
                disabled={unread === 0}
                onClick={handleMarkAll}
              />
              <ActionButton
                label="Clear all"
                icon={<BellOff size={16} />}
                disabled={notifications.length === 0}
                onClick={handleClear}
              />
            </div>
          </div>

          <div className="max-w-3xl">
            <h1 className="text-4xl md:text-5xl text-ivory tracking-tight" style={{ fontFamily: "'Instrument Serif', serif" }}>
              Notifications
            </h1>
            <p className="text-ivory/55 text-sm mt-2">
              {notifications.length > 0 ? `${unread} unread of ${notifications.length} total` : 'Stay tuned for updates about your study groups.'}
            </p>
          </div>

          {error ? (
            <GlassCard className="p-8 text-center text-blush border border-blush/35 bg-blush/12">{error}</GlassCard>
          ) : loading ? (
            <GlassCard className="p-8 text-center text-ivory/70">Loading notifications...</GlassCard>
          ) : notifications.length === 0 ? (
            <GlassCard className="py-16 text-center">
              <Inbox size={36} className="mx-auto text-ivory/30 mb-4" />
              <p className="text-ivory/55 text-sm">You have no notifications.</p>
            </GlassCard>
          ) : (
            <div className="space-y-3">
              {notifications.map((notification) => (
                <div
                  key={notification.id}
                  className={`rounded-2xl border px-5 py-4 ${toneClasses[notification.tone]} ${
                    notification.read ? 'opacity-60' : ''
                  }`}
                >
                  <div className="flex items-center justify-between gap-4">
                    <p className="text-sm font-semibold min-w-0 flex-1 truncate">{notification.title}</p>
                    <span className="text-[11px] uppercase tracking-wide opacity-70 whitespace-nowrap">
                      {new Date(notification.createdAt).toLocaleString()}
                    </span>
                  </div>
                  <p className="text-xs mt-1.5 opacity-80 leading-relaxed">{notification.message}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      </section>
    </StudentLayout>
  )
}
