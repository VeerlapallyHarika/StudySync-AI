import type { ReactNode } from 'react'

interface ActionButtonProps {
  label: string
  icon?: ReactNode
  onClick?: () => void
  variant?: 'glass' | 'solid' | 'danger'
  disabled?: boolean
}

export default function ActionButton({
  label,
  icon,
  onClick,
  variant = 'glass',
  disabled = false,
}: ActionButtonProps) {
  const base = 'rounded-full px-5 py-3 text-sm font-medium flex items-center gap-2 transition-colors'

  const styles: Record<NonNullable<ActionButtonProps['variant']>, string> = {
    glass: 'liquid-glass text-white hover:bg-white/5',
    solid: 'bg-white text-black hover:bg-white/90',
    danger: 'liquid-glass text-rose-200 hover:bg-rose-500/10',
  }

  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled}
      className={`${base} ${styles[variant]} ${
        disabled ? 'opacity-40 cursor-not-allowed' : ''
      }`}
    >
      {icon}
      {label}
    </button>
  )
}
