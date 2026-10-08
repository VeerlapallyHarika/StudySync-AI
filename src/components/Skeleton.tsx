interface SkeletonProps {
  lines?: number
  className?: string
}

export function Skeleton({ lines = 3, className = '' }: SkeletonProps) {
  return (
    <div className={`space-y-3 ${className}`} aria-hidden="true">
      {Array.from({ length: lines }, (_, index) => (
        <div
          key={index}
          className="skeleton-shimmer h-4 skeleton-text"
          style={{ width: `${100 - index * 15}%`, animationDelay: `${index * 120}ms` }}
        />
      ))}
    </div>
  )
}

export function SkeletonBlock({ className = '' }: { className?: string }) {
  return <div className={`skeleton-shimmer rounded-2xl ${className}`} aria-hidden="true" />
}

export function SkeletonCard({ lines = 4, className = '' }: { lines?: number; className?: string }) {
  return (
    <div className={`liquid-glass rounded-2xl p-6 ${className}`}>
      <div className="skeleton-shimmer h-3 w-24 skeleton-text mb-4" />
      <Skeleton lines={lines} />
    </div>
  )
}

export function SkeletonStat({ className = '' }: { className?: string }) {
  return (
    <div className={`liquid-glass rounded-2xl p-6 h-full ${className}`} aria-hidden="true">
      <div className="skeleton-shimmer h-3 w-28 skeleton-text mb-4" />
      <div className="skeleton-shimmer h-8 w-20 skeleton-text mb-3" />
      <div className="skeleton-shimmer h-3 w-36 skeleton-text" />
    </div>
  )
}

export function SkeletonChart({ className = '' }: { className?: string }) {
  return (
    <div className={`liquid-glass rounded-2xl p-6 h-full ${className}`} aria-hidden="true">
      <div className="skeleton-shimmer h-5 w-40 skeleton-text mb-2" />
      <div className="skeleton-shimmer h-3 w-56 skeleton-text mb-6" />
      <div className="flex items-end gap-3 h-40">
        {Array.from({ length: 6 }, (_, index) => (
          <div
            key={index}
            className="flex-1 skeleton-shimmer rounded-t-xl"
            style={{ height: `${35 + ((index * 13) % 45)}%`, animationDelay: `${index * 90}ms` }}
          />
        ))}
      </div>
    </div>
  )
}

export function SkeletonTable({ rows = 6, columns = 4, className = '' }: { rows?: number; columns?: number; className?: string }) {
  return (
    <div className={`liquid-glass rounded-2xl overflow-hidden ${className}`} aria-hidden="true">
      <div className="border-b border-plum/80 px-5 py-4">
        <div className="skeleton-shimmer h-5 w-36 skeleton-text" />
      </div>
      {Array.from({ length: rows }, (_, rowIndex) => (
        <div key={rowIndex} className="flex items-center gap-6 border-b border-plum/60 px-5 py-4">
          {Array.from({ length: columns }, (_, columnIndex) => (
            <div
              key={columnIndex}
              className="skeleton-shimmer skeleton-text"
              style={{ width: `${40 + ((rowIndex + columnIndex) * 11) % 45}%`, height: 14 }}
            />
          ))}
        </div>
      ))}
    </div>
  )
}

export function SkeletonAvatar({ className = '' }: { className?: string }) {
  return <div className={`skeleton-shimmer rounded-full ${className}`} aria-hidden="true" />
}
