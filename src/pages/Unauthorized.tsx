import { Link } from 'react-router-dom'
import { LogIn, ShieldAlert } from 'lucide-react'
import SiteLayout from '../layouts/SiteLayout'
import GlassCard from '../components/GlassCard'
import usePageTitle from '../hooks/usePageTitle'

export default function UnauthorizedPage() {
  usePageTitle('Unauthorized Access')

  return (
    <SiteLayout>
      <section className="px-6 py-20 md:py-28">
        <div className="max-w-2xl mx-auto">
          <GlassCard className="p-12 text-center">
            <ShieldAlert size={48} className="mx-auto text-ivory/30 mb-6" />
            <p className="text-ivory/50 text-sm uppercase tracking-widest mb-3">Access Denied</p>
            <h1 className="text-5xl text-ivory mb-4 tracking-tight" style={{ fontFamily: "'Instrument Serif', serif" }}>
              You're not authorized to view this page
            </h1>
            <p className="text-ivory/55 text-sm leading-relaxed mb-8">
              This area is reserved for signed-in students. Please sign in to continue.
            </p>
            <div className="flex flex-wrap items-center justify-center gap-3">
              <Link
                to="/student/login"
                className="inline-flex items-center gap-2 rounded-full bg-blush text-ink px-6 py-3 text-sm font-medium transition-colors hover:bg-blush/90"
              >
                <LogIn size={16} />
                Student sign in
              </Link>
              <Link
                to="/"
                className="inline-flex items-center gap-2 rounded-full border border-mauve/70 text-ivory px-6 py-3 text-sm font-medium transition-colors hover:bg-mauve/20"
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
