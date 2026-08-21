import GlassCard from '../GlassCard'
import type { StudentNotification } from '../../types/student'

interface NotificationCardProps {
  notifications: StudentNotification[]
}

const toneClasses = {
  info: 'bg-cyan-400/15 text-cyan-100 border-cyan-300/20',
  success: 'bg-emerald-400/15 text-emerald-100 border-emerald-300/20',
  warning: 'bg-amber-400/15 text-amber-100 border-amber-300/20',
}

export default function NotificationCard({ notifications }: NotificationCardProps) {
  return (
    <GlassCard className="p-6 h-full">
      <h3 className="text-white text-xl font-semibold mb-5">Notifications</h3>
      <div className="space-y-3">
        {notifications.map((notification) => (
          <div key={notification.title} className={`rounded-2xl border px-4 py-3 ${toneClasses[notification.tone ?? 'info']}`}>
            <p className="text-sm font-semibold">{notification.title}</p>
            <p className="text-xs mt-1 opacity-80 leading-relaxed">{notification.description}</p>
          </div>
        ))}
      </div>
    </GlassCard>
  )
}
