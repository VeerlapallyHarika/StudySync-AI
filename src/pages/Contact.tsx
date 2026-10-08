import { useState, type FormEvent } from 'react'
import GlassCard from '../components/GlassCard'
import SiteLayout from '../layouts/SiteLayout'
import usePageTitle from '../hooks/usePageTitle'

export default function ContactPage() {
  usePageTitle('Contact')
  const [sent, setSent] = useState(false)

  const handleSubmit = (event: FormEvent) => {
    event.preventDefault()
    setSent(true)
  }

  return (
    <SiteLayout>
      <section className="px-6 py-14 md:py-20">
        <div className="max-w-6xl mx-auto space-y-8">
          <div className="max-w-3xl mx-auto text-center">
            <h1
              className="text-4xl md:text-5xl text-ivory mb-4 tracking-tight"
              style={{ fontFamily: "'Instrument Serif', serif" }}
            >
              Contact
            </h1>
            <p className="text-ivory/60 text-base leading-relaxed">
              Reach the project team, view the source links, or send a note through the same glassmorphism language used everywhere else.
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-[1fr_1.1fr] gap-6">
            <GlassCard className="p-6 space-y-5">
              <div>
                <p className="text-ivory/50 text-xs uppercase tracking-wide">Project Details</p>
                <div className="mt-3 space-y-3 text-ivory/75 text-sm">
                  <p>Email: support@studysync.ai</p>
                  <p>GitHub: github.com/studysync-ai</p>
                  <p>College: MotionSites Institute of Technology</p>
                </div>
              </div>

              <div className="liquid-glass rounded-2xl p-5 text-ivory/70 text-sm">
                StudySync AI builds balanced groups using student performance, complementary skills, and ML-driven matching.
              </div>
            </GlassCard>

            <GlassCard className="p-6">
              <form onSubmit={handleSubmit} className="space-y-4">
                {['Name', 'Email', 'Subject'].map((field) => (
                  <div key={field} className="space-y-2">
                    <label className="text-ivory/60 text-xs font-medium uppercase tracking-wide">{field}</label>
                    <input
                      type="text"
                      placeholder={`Enter ${field.toLowerCase()}`}
                      className="w-full liquid-glass rounded-full px-5 py-3 bg-transparent text-ivory placeholder:text-ivory/40 text-sm outline-none"
                      required
                    />
                  </div>
                ))}
                <div className="space-y-2">
                  <label className="text-ivory/60 text-xs font-medium uppercase tracking-wide">Message</label>
                  <textarea
                    placeholder="Write your message"
                    rows={5}
                    className="w-full liquid-glass rounded-3xl px-5 py-4 bg-transparent text-ivory placeholder:text-ivory/40 text-sm outline-none resize-none"
                    required
                  />
                </div>
                <button
                  type="submit"
                  className="w-full bg-blush rounded-full px-5 py-3 text-ink text-sm font-semibold hover:bg-blush/90 transition-colors"
                >
                  Send Message
                </button>
                {sent && <p className="text-blush text-xs text-center">Your message form is ready for backend wiring.</p>}
              </form>
            </GlassCard>
          </div>
        </div>
      </section>
    </SiteLayout>
  )
}
