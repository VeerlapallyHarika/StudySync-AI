import GlassCard from '../GlassCard'
import type { StudentNotification } from '../../types/student'

interface NotificationCardProps {
  notifications: StudentNotification[]
}

const toneClasses = {
  info: 'bg-mauve/30 text-ivory/90 border-mauve/50',
  success: 'bg-ivory/10 text-ivory border-ivory/25',
  warning: 'bg-plum/80 text-ivory/90 border-mauve/60',
}

export default function NotificationCard({ notifications }: NotificationCardProps) {
  return (
    <GlassCard className="p-6 h-full">
      <h3 className="text-ivory text-xl font-semibold mb-5">Notifications</h3>
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
