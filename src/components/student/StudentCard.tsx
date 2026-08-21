import type { ReactNode } from 'react'
import GlassCard from '../GlassCard'

interface StudentCardProps {
  title: string
  value?: string
  subtitle?: string
  description?: string
  avatar?: string
  items?: Array<{ label: string; value: string }>
  footer?: ReactNode
  className?: string
}

export default function StudentCard({
  title,
  value,
  subtitle,
  description,
  avatar,
  items = [],
  footer,
  className = '',
}: StudentCardProps) {
  return (
    <GlassCard className={`p-6 h-full ${className}`}>
      <div className="flex items-start gap-4">
        {avatar ? (
          <div className="w-14 h-14 rounded-full bg-white text-black flex items-center justify-center text-lg font-semibold flex-shrink-0">
            {avatar}
          </div>
        ) : null}
        <div className="min-w-0 flex-1">
          <p className="text-white/50 text-xs uppercase tracking-wide">{title}</p>
          {value ? (
            <div className="text-2xl text-white mt-1" style={{ fontFamily: "'Instrument Serif', serif" }}>
              {value}
            </div>
          ) : null}
          {subtitle ? <p className="text-white/70 text-sm mt-1">{subtitle}</p> : null}
          {description ? <p className="text-white/55 text-sm mt-2 leading-relaxed">{description}</p> : null}
        </div>
      </div>

      {items.length > 0 ? (
        <div className="mt-5 space-y-3">
          {items.map((item) => (
            <div key={item.label} className="liquid-glass rounded-2xl px-4 py-3 text-sm text-white/70 flex items-center justify-between gap-4">
              <span className="text-white/55">{item.label}</span>
              <span className="text-white text-right">{item.value}</span>
            </div>
          ))}
        </div>
      ) : null}

      {footer ? <div className="mt-5">{footer}</div> : null}
    </GlassCard>
  )
}
