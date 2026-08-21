import { Link } from 'react-router-dom'
import { RotateCcw, ServerCrash } from 'lucide-react'
import SiteLayout from '../layouts/SiteLayout'
import GlassCard from '../components/GlassCard'
import usePageTitle from '../hooks/usePageTitle'

export default function ServerErrorPage() {
  usePageTitle('Server Error')

  return (
    <SiteLayout>
      <section className="px-6 py-20 md:py-28">
        <div className="max-w-2xl mx-auto">
          <GlassCard className="p-12 text-center">
            <ServerCrash size={48} className="mx-auto text-white/30 mb-6" />
            <p className="text-white/50 text-sm uppercase tracking-widest mb-3">Error 500</p>
            <h1 className="text-5xl text-white mb-4 tracking-tight" style={{ fontFamily: "'Instrument Serif', serif" }}>
              Something went wrong
            </h1>
            <p className="text-white/55 text-sm leading-relaxed mb-8">
              Our servers hit a snag while processing your request. Please try again in a moment.
            </p>
            <div className="flex flex-wrap items-center justify-center gap-3">
              <button
                type="button"
                onClick={() => window.location.reload()}
                className="inline-flex items-center gap-2 rounded-full bg-white text-black px-6 py-3 text-sm font-medium transition-colors hover:bg-white/90"
              >
                <RotateCcw size={16} />
                Try again
              </button>
              <Link
                to="/"
                className="inline-flex items-center gap-2 rounded-full border border-white/15 text-white px-6 py-3 text-sm font-medium transition-colors hover:bg-white/5"
              >
                Back to Home
              </Link>
            </div>
          </GlassCard>
        </div>
      </section>
    </SiteLayout>
  )
}
