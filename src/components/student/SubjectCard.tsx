import GlassCard from '../GlassCard'

interface SubjectCardProps {
  subject: string
  score: number
  label: string
  description?: string
}

export default function SubjectCard({ subject, score, label, description }: SubjectCardProps) {
  return (
    <GlassCard className="p-5 h-full">
      <p className="text-white/55 text-xs uppercase tracking-wide">{subject}</p>
      <div className="flex items-end justify-between gap-4 mt-2">
        <div className="text-3xl text-white" style={{ fontFamily: "'Instrument Serif', serif" }}>
          {score}
        </div>
        <span className="rounded-full px-3 py-1 text-xs font-medium bg-white/10 text-white/80">
          {label}
        </span>
      </div>
      <div className="h-2 rounded-full bg-white/10 overflow-hidden mt-4">
        <div className="h-full rounded-full bg-gradient-to-r from-cyan-300 to-white" style={{ width: `${score}%` }} />
      </div>
      {description ? <p className="text-white/55 text-sm mt-4 leading-relaxed">{description}</p> : null}
    </GlassCard>
  )
}
