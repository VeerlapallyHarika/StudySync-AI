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
    glass: 'liquid-glass text-ivory hover:bg-mauve/20',
    solid: 'bg-blush text-ink hover:bg-blush/90',
    danger: 'liquid-glass text-blush hover:bg-blush/12',
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
