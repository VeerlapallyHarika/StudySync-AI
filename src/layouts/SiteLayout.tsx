import type { ReactNode } from 'react'
import Navbar from '../components/Navbar'
import SkipLink from '../components/SkipLink'

interface SiteLayoutProps {
  children: ReactNode
}

export default function SiteLayout({ children }: SiteLayoutProps) {
  return (
    <div className="min-h-screen bg-black overflow-hidden relative flex flex-col">
      <div className="absolute inset-0 bg-gradient-to-b from-blue-950/20 via-black to-black" />
      <SkipLink />
      <Navbar />
      <main id="main-content" className="relative z-10 flex-1 pt-24 md:pt-28">{children}</main>
    </div>
  )
}
