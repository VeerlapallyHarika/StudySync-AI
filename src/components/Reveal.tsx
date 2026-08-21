import { useEffect, useRef, useState, type ReactNode } from 'react'

interface RevealProps {
  children: ReactNode
  className?: string
  delayMs?: number
  as?: 'div' | 'section'
}

export default function Reveal({
  children,
  className = '',
  delayMs = 0,
  as = 'div',
}: RevealProps) {
  const ref = useRef<HTMLDivElement | null>(null)
  const [visible, setVisible] = useState(false)

  useEffect(() => {
    const node = ref.current
    if (!node) return

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            window.setTimeout(() => setVisible(true), delayMs)
            observer.unobserve(entry.target)
          }
        })
      },
      { threshold: 0.15 },
    )

    observer.observe(node)
    return () => observer.disconnect()
  }, [delayMs])

  const Tag = as as any

  return (
    <Tag
      ref={ref}
      className={`animate-on-scroll ${visible ? 'is-visible' : ''} ${className}`}
    >
      {children}
    </Tag>
  )
}
