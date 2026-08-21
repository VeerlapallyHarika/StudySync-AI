import { Link } from 'react-router-dom'
import { Home, SearchX } from 'lucide-react'
import SiteLayout from '../layouts/SiteLayout'
import GlassCard from '../components/GlassCard'
import usePageTitle from '../hooks/usePageTitle'

export default function NotFoundPage() {
  usePageTitle('Page Not Found')

  return (
    <SiteLayout>
      <section className="px-6 py-20 md:py-28">
        <div className="max-w-2xl mx-auto">
          <GlassCard className="p-12 text-center">
            <SearchX size={48} className="mx-auto text-white/30 mb-6" />
            <p className="text-white/50 text-sm uppercase tracking-widest mb-3">Error 404</p>
            <h1 className="text-5xl text-white mb-4 tracking-tight" style={{ fontFamily: "'Instrument Serif', serif" }}>
              Page not found
            </h1>
            <p className="text-white/55 text-sm leading-relaxed mb-8">
              The page you're looking for doesn't exist or may have been moved. Let's get you back on track.
            </p>
            <Link
              to="/"
              className="inline-flex items-center gap-2 rounded-full bg-white text-black px-6 py-3 text-sm font-medium transition-colors hover:bg-white/90"
            >
              <Home size={16} />
              Back to Home
            </Link>
          </GlassCard>
        </div>
      </section>
    </SiteLayout>
  )
}
