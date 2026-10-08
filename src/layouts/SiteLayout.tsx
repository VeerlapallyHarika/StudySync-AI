import type { ReactNode } from 'react'
import Navbar from '../components/Navbar'
import SkipLink from '../components/SkipLink'

interface SiteLayoutProps {
  children: ReactNode
}

export default function SiteLayout({ children }: SiteLayoutProps) {
  return (
    <div className="min-h-screen bg-ink overflow-hidden relative flex flex-col">
      <div className="absolute inset-0 bg-gradient-to-b from-plum/40 via-ink to-ink">
        <div className="aurora-blob -top-40 -left-32 h-[440px] w-[440px] bg-mauve/30" />
        <div className="aurora-blob top-1/3 -right-40 h-[420px] w-[420px] bg-plum/60" />
        <div className="aurora-blob bottom-0 left-1/4 h-[380px] w-[380px] bg-blush/10" />
      </div>
      <SkipLink />
      <Navbar />
      <main id="main-content" className="relative z-10 flex-1 pt-24 md:pt-28">{children}</main>
    </div>
  )
}
