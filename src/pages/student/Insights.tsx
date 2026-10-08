import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { ArrowLeft, BookOpen, CalendarClock, Lightbulb, TrendingUp, UserRound } from 'lucide-react'
import GlassCard from '../../components/GlassCard'
import StudentLayout from '../../layouts/StudentLayout'
import usePageTitle from '../../hooks/usePageTitle'
import { getStudentInsights } from '../../services/studentService'
import type { StudentInsights } from '../../types/student'

export default function StudentInsightsPage() {
  usePageTitle('AI Insights')
  const [insights, setInsights] = useState<StudentInsights | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let mounted = true

    getStudentInsights()
      .then((response) => {
        if (mounted) setInsights(response)
      })
      .catch((loadError) => {
        if (mounted) setError(loadError instanceof Error ? loadError.message : 'Unable to load insights.')
      })
      .finally(() => {
        if (mounted) setLoading(false)
      })

    return () => {
      mounted = false
    }
  }, [])

  const scoreBar = (label: string, value: number, tone: 'strength' | 'attention') => (
    <GlassCard className="p-6">
      <p className="text-ivory/55 text-xs uppercase tracking-wide mb-3">{label}</p>
      <div className="flex items-center gap-4">
        <div className="text-4xl text-ivory" style={{ fontFamily: "'Instrument Serif', serif" }}>
          {value}
        </div>
        <div className="h-2 flex-1 rounded-full bg-ivory/5 overflow-hidden">
          <div
            className={`h-full rounded-full ${tone === 'strength' ? 'bg-gradient-to-r from-mauve to-blush' : 'bg-gradient-to-r from-blush via-blush/80 to-mauve'}`}
            style={{ width: `${Math.min(100, value)}%` }}
          />
        </div>
      </div>
    </GlassCard>
  )

  return (
    <StudentLayout>
      <section className="px-6 py-14 md:py-20">
        <div className="max-w-6xl mx-auto space-y-8">
          <div className="flex justify-between items-center gap-4 flex-wrap">
            <Link
              to="/student/dashboard"
              className="liquid-glass rounded-full px-5 py-2 text-ivory/80 hover:text-ivory text-sm font-medium flex items-center gap-2 transition-colors"
            >
              <ArrowLeft size={16} />
              Back to Dashboard
            </Link>
          </div>

          <div className="max-w-3xl">
            <h1 className="text-4xl md:text-5xl text-ivory tracking-tight" style={{ fontFamily: "'Instrument Serif', serif" }}>
              AI Insights
            </h1>
            <p className="text-ivory/55 text-sm mt-2">Personalised guidance generated from your academic profile.</p>
          </div>

          {loading ? (
            <GlassCard className="p-8 text-center text-ivory/70">Loading insights...</GlassCard>
          ) : error || !insights ? (
            <GlassCard className="p-8 text-center text-blush border border-blush/35 bg-blush/12">
              {error || 'Unable to load insights.'}
            </GlassCard>
          ) : (
            <>
              <GlassCard className="p-6 md:p-8 border border-mauve/45 shadow-accent-glow">
                <div className="flex items-center gap-3 mb-4 text-ivory">
                  <TrendingUp size={18} className="text-blush" />
                  <h2 className="text-2xl" style={{ fontFamily: "'Instrument Serif', serif" }}>
                    Academic Overview
                  </h2>
                </div>
                <p className="text-ivory/70 text-sm leading-relaxed">{insights.academicSummary}</p>
                <div className="mt-5 inline-flex items-center gap-2 rounded-full px-4 py-2 bg-mauve/30 border border-mauve/50 text-ivory text-sm">
                  <TrendingUp size={14} />
                  Learning trend: {insights.learningTrend}
                </div>
              </GlassCard>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                {scoreBar('Strength Score', insights.strengthScore, 'strength')}
                {scoreBar('Weakness Score', insights.weaknessScore, 'attention')}
              </div>

              <GlassCard className="p-6 md:p-8">
                <div className="flex items-center gap-3 mb-5 text-ivory">
                  <Lightbulb size={18} className="text-blush" />
                  <h2 className="text-2xl" style={{ fontFamily: "'Instrument Serif', serif" }}>
                    Improvement Suggestions
                  </h2>
                </div>
                <ul className="space-y-3">
                  {insights.improvementSuggestions.map((suggestion) => (
                    <li key={suggestion} className="liquid-glass rounded-2xl px-5 py-4 text-ivory/70 text-sm leading-relaxed flex items-start gap-3">
                      <span className="w-6 h-6 rounded-full bg-plum/80 text-blush text-xs flex items-center justify-center flex-shrink-0">
                        •
                      </span>
                      {suggestion}
                    </li>
                  ))}
                </ul>
              </GlassCard>

              <GlassCard className="p-6 md:p-8">
                <div className="flex items-center gap-3 mb-5 text-ivory">
                  <BookOpen size={18} className="text-blush" />
                  <h2 className="text-2xl" style={{ fontFamily: "'Instrument Serif', serif" }}>
                    Recommended Resources
                  </h2>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {insights.learningResources.map((resource) => (
                    <div key={resource.subject} className="liquid-glass rounded-2xl p-5">
                      <p className="text-ivory text-sm font-medium">{resource.subject}</p>
                      <p className="text-ivory/55 text-xs mt-2 leading-relaxed">{resource.resource}</p>
                    </div>
                  ))}
                </div>
              </GlassCard>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <GlassCard className="p-6 md:p-8">
                  <div className="flex items-center gap-3 mb-5 text-ivory">
                    <UserRound size={18} className="text-blush" />
                    <h2 className="text-2xl" style={{ fontFamily: "'Instrument Serif', serif" }}>
                      Peer Mentor
                    </h2>
                  </div>
                  {insights.peerMentor.name ? (
                    <div className="liquid-glass rounded-2xl p-5">
                      <p className="text-ivory font-medium">{insights.peerMentor.name}</p>
                      <p className="text-ivory/55 text-xs mt-1">
                        Strong in {insights.peerMentor.subject ?? 'your focus area'} &middot; {insights.peerMentor.reason}
                      </p>
                    </div>
                  ) : (
                    <p className="text-ivory/50 text-sm leading-relaxed">
                      {insights.peerMentor.reason ?? 'No group mate specialises in your focus area yet.'}
                    </p>
                  )}
                </GlassCard>

                <GlassCard className="p-6 md:p-8">
                  <div className="flex items-center gap-3 mb-5 text-ivory">
                    <CalendarClock size={18} className="text-blush" />
                    <h2 className="text-2xl" style={{ fontFamily: "'Instrument Serif', serif" }}>
                      Suggested Study Sessions
                    </h2>
                  </div>
                  <div className="space-y-3">
                    {insights.studySessions.map((session) => (
                      <div key={session.day} className="liquid-glass rounded-2xl px-5 py-4 flex items-center justify-between gap-4">
                        <div className="min-w-0 flex-1">
                          <p className="text-ivory text-sm font-medium">{session.day}</p>
                          <p className="text-ivory/45 text-xs truncate">{session.focus}</p>
                        </div>
                        <span className="rounded-full bg-ivory/10 text-ivory text-xs px-3 py-1 whitespace-nowrap">
                          {session.slot}
                        </span>
                      </div>
                    ))}
                  </div>
                </GlassCard>
              </div>
            </>
          )}
        </div>
      </section>
    </StudentLayout>
  )
}
