import type { HTMLAttributes, ReactNode } from 'react'

interface GlassCardProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode
}

export default function GlassCard({ children, className = '', ...props }: GlassCardProps) {
  return (
    <div className={`liquid-glass rounded-2xl ${className}`} {...props}>
      {children}
    </div>
  )
}
