import { useEffect, useState, type FormEvent } from 'react'
import { Link } from 'react-router-dom'
import {
  ArrowLeft,
  Activity,
  CheckCircle2,
  Crown,
  Loader2,
  MessageSquare,
  Send,
  Handshake,
  Sparkles,
  Target,
  TrendingUp,
  UserRound,
  Users,
  XCircle,
} from 'lucide-react'
import GlassCard from '../../components/GlassCard'
import StudentLayout from '../../layouts/StudentLayout'
import usePageTitle from '../../hooks/usePageTitle'
import {
  generateStudentGroup,
  getStudentGroupStatus,
  sendGroupChatMessage,
} from '../../services/studentService'
import type {
  ChatMessageItem,
  GroupActivityItem,
  StudentGroupDetail,
  StudentGroupStatus,
} from '../../types/student'

const PROCESSING_STEPS = [
  'Analyzing your academic performance data…',
  'Identifying strengths and weaknesses…',
  'Finding complementary students…',
  'Forming balanced study groups…',
]

type FormationState = 'need-profile' | 'waiting'

export default function StudentGroupsPage() {
  usePageTitle('My Group')
  const [status, setStatus] = useState<StudentGroupStatus | null>(null)
  const [group, setGroup] = useState<StudentGroupDetail | null>(null)
  const [messages, setMessages] = useState<ChatMessageItem[]>([])
  const [loading, setLoading] = useState(true)
  const [processing, setProcessing] = useState(false)
  const [processingStep, setProcessingStep] = useState(0)
  const [error, setError] = useState('')
  const [draft, setDraft] = useState('')
  const [sending, setSending] = useState(false)

  const fetchStatus = async (quiet = false) => {
    if (!quiet) {
      setLoading(true)
      setError('')
    }
    try {
      const nextStatus = await getStudentGroupStatus()
      setStatus(nextStatus)
      setGroup(nextStatus.group)
      if (nextStatus.group) setMessages(nextStatus.group.chat)
    } catch (loadError) {
      if (!quiet) setError(loadError instanceof Error ? loadError.message : 'Unable to load your group.')
    } finally {
      if (!quiet) setLoading(false)
    }
  }

  useEffect(() => {
    void fetchStatus()
  }, [])

  const handleGenerate = async () => {
    setProcessing(true)
    setError('')
    let step = 0
    const timer = window.setInterval(() => {
      step = (step + 1) % PROCESSING_STEPS.length
      setProcessingStep(step)
    }, 1300)
    try {
      const result = await generateStudentGroup()
      setStatus(result.status)
      if (result.group) {
        setGroup(result.group)
        setMessages(result.group.chat)
      }
    } catch (generateError) {
      setError(generateError instanceof Error ? generateError.message : 'Unable to generate your study group.')
      void fetchStatus(true)
    } finally {
      window.clearInterval(timer)
      setProcessing(false)
      setProcessingStep(0)
    }
  }

  const handleSend = async (event: FormEvent) => {
    event.preventDefault()
    const text = draft.trim()
    if (!text || sending) return

    setSending(true)
    try {
      const sent = await sendGroupChatMessage(text)
      setMessages((current) => [...current, sent])
      setDraft('')
    } catch (sendError) {
      setError(sendError instanceof Error ? sendError.message : 'Unable to send your message.')
    } finally {
      setSending(false)
    }
  }

  const formationState: FormationState | null =
    group || !status
      ? null
      : !status.profileComplete
        ? 'need-profile'
        : 'waiting'

  const inputClass =
    'w-full liquid-glass rounded-2xl px-4 py-3 bg-transparent text-ivory placeholder:text-ivory/40 text-sm outline-none'

  const actionButtonClass =
    'inline-flex items-center gap-2 rounded-full bg-blush text-ink px-6 py-2.5 text-sm font-medium transition-colors hover:bg-blush/90'

  if (loading) {
    return (
      <StudentLayout>
        <section className="px-6 py-14 md:py-20">
          <div className="max-w-6xl mx-auto">
            <GlassCard className="p-8 text-center text-ivory/70">Loading your group...</GlassCard>
          </div>
        </section>
      </StudentLayout>
    )
  }

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
            <h1
              className="text-4xl md:text-5xl text-ivory tracking-tight"
              style={{ fontFamily: "'Instrument Serif', serif" }}
            >
              My Study Group
            </h1>
            <p className="text-ivory/55 text-sm mt-2">Collaborate, chat and stay in sync with your teammates.</p>
          </div>

          {error ? (
            <GlassCard className="p-8 text-center text-blush border border-blush/35 bg-blush/12">
              {error}
            </GlassCard>
          ) : null}

          {processing ? (
            <GlassCard className="py-20 text-center border border-mauve/50 shadow-accent-glow">
              <Loader2 size={36} className="mx-auto text-blush mb-6 animate-spin" />
              <p
                className="text-ivory/80 text-lg"
                style={{ fontFamily: "'Instrument Serif', serif" }}
              >
                {PROCESSING_STEPS[processingStep]}
              </p>
              <p className="text-ivory/45 text-xs mt-2">
                Running the AI matching pipeline — this usually takes a few seconds.
              </p>
            </GlassCard>
          ) : group ? (
            <>
              <GlassCard className="p-6 md:p-8">
                <div className="flex items-center gap-3 mb-5 text-ivory">
                  <Users size={18} className="text-blush" />
                  <h2 className="text-2xl" style={{ fontFamily: "'Instrument Serif', serif" }}>
                    {group.name}
                  </h2>
                  <span className="ml-auto hidden sm:flex items-center gap-1.5 rounded-full bg-plum/80 border border-mauve/60 px-3 py-1 text-ivory text-xs">
                    <Crown size={13} />
                    Leader: {group.teamLeader}
                  </span>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
                  <div>
                    <div className="flex items-center gap-2 text-ivory/55 text-xs uppercase tracking-wide mb-3">
                      <TrendingUp size={14} className="text-blush" />
                      Average Performance
                    </div>
                    <p className="text-3xl text-ivory" style={{ fontFamily: "'Instrument Serif', serif" }}>
                      {group.averagePerformance}%
                    </p>
                  </div>
                  <div>
                    <div className="flex items-center gap-2 text-ivory/55 text-xs uppercase tracking-wide mb-3">
                      <Handshake size={14} className="text-blush" />
                      Compatibility
                    </div>
                    <p className="text-3xl text-ivory" style={{ fontFamily: "'Instrument Serif', serif" }}>
                      {group.complementarySkillScore}%
                    </p>
                    <p className="text-ivory/40 text-xs mt-1">AI-matched complementary pairing</p>
                  </div>
                  <div>
                    <div className="flex items-center gap-2 text-ivory/55 text-xs uppercase tracking-wide mb-3">
                      <Sparkles size={14} className="text-blush" />
                      Recommendation
                    </div>
                    <p className="text-ivory/70 text-sm leading-relaxed">{group.learningRecommendation}</p>
                  </div>
                </div>

                <div className="mt-6 grid grid-cols-1 sm:grid-cols-2 gap-6">
                  <div>
                    <p className="text-ivory/55 text-xs uppercase tracking-wide mb-3">Overall Strengths</p>
                    <div className="flex flex-wrap gap-2">
                      {group.overallStrengths.map((strength) => (
                        <span
                          key={strength}
                          className="rounded-full bg-ivory/10 border border-ivory/25 text-ivory text-xs px-3 py-1"
                        >
                          {strength}
                        </span>
                      ))}
                    </div>
                  </div>
                  <div>
                    <p className="text-ivory/55 text-xs uppercase tracking-wide mb-3">Overall Weaknesses</p>
                    <div className="flex flex-wrap gap-2">
                      {group.overallWeaknesses.map((weakness) => (
                        <span
                          key={weakness}
                          className="rounded-full bg-blush/12 border border-blush/30 text-blush text-xs px-3 py-1"
                        >
                          {weakness}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="mt-6">
                  <p className="text-ivory/55 text-xs uppercase tracking-wide mb-3">Weakness Coverage</p>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    {group.weaknessCoverage.length === 0 ? (
                      <p className="text-ivory/50 text-sm">No weak subjects to cover in this group.</p>
                    ) : (
                      group.weaknessCoverage.map((coverage) => (
                        <div
                          key={coverage.subject}
                          className="liquid-glass rounded-2xl px-4 py-3 flex items-center justify-between gap-3"
                        >
                          <span className="text-ivory text-sm">{coverage.subject}</span>
                          {coverage.covered ? (
                            <span className="inline-flex items-center gap-1.5 rounded-full bg-ivory/10 border border-ivory/25 text-ivory text-xs px-3 py-1 whitespace-nowrap">
                              <CheckCircle2 size={13} />
                              Covered{coverage.coveredBy.length ? ` by ${coverage.coveredBy.join(', ')}` : ''}
                            </span>
                          ) : (
                            <span className="inline-flex items-center gap-1.5 rounded-full bg-blush/12 border border-blush/30 text-blush text-xs px-3 py-1 whitespace-nowrap">
                              <XCircle size={13} />
                              Uncovered
                            </span>
                          )}
                        </div>
                      ))
                    )}
                  </div>
                </div>

                <div className="mt-6">
                  <div className="flex items-center gap-2 text-ivory/55 text-xs uppercase tracking-wide mb-3">
                    <Handshake size={14} className="text-blush" />
                    Why you were grouped together
                  </div>
                  <ul className="space-y-2 text-sm text-ivory/70">
                    {group.weaknessCoverage
                      .filter((coverage) => coverage.covered)
                      .map((coverage) => (
                        <li key={coverage.subject}>
                          <span className="text-ivory">{coverage.coveredBy.join(', ')}</span> is strong in{' '}
                          <span className="text-ivory">{coverage.subject}</span>, where you can get support.
                        </li>
                      ))}
                    {group.weaknessCoverage
                      .filter((coverage) => !coverage.covered)
                      .map((coverage) => (
                        <li key={coverage.subject}>
                          <span className="text-blush">{coverage.subject}</span> is a shared focus area — no one in
                          the group covers it yet, so you can work on it together.
                        </li>
                      ))}
                    <li>
                      Complementary skill score:{' '}
                      <span className="text-ivory">{group.complementarySkillScore}/100</span> — members balance each
                      other's strengths and weaknesses.
                    </li>
                    <li>
                      Average group performance:{' '}
                      <span className="text-ivory">{group.averagePerformance}%</span> across {group.members.length}{' '}
                      members.
                    </li>
                    {group.teamLeader ? (
                      <li>
                        Team leader:{' '}
                        <span className="text-ivory">
                          {group.members.find((member) => member.studentId === group.teamLeader)?.name ?? group.teamLeader}
                        </span>{' '}
                        coordinates sessions and shared resources.
                      </li>
                    ) : null}
                  </ul>
                </div>
              </GlassCard>

              <div>
                <div className="flex items-center gap-3 mb-5 text-ivory">
                  <Target size={18} className="text-blush" />
                  <h2 className="text-2xl" style={{ fontFamily: "'Instrument Serif', serif" }}>
                    Members
                  </h2>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                  {group.members.map((member) => (
                    <GlassCard key={member.studentId} className="p-6">
                      <div className="flex items-center gap-4">
                        <div className="w-12 h-12 rounded-full bg-ivory text-ink flex items-center justify-center font-semibold flex-shrink-0">
                          {member.avatar}
                        </div>
                        <div className="min-w-0 flex-1">
                          <p className="text-ivory font-medium truncate">
                            {member.name}
                            {member.isSelf ? <span className="text-ivory/40 text-xs ml-2">(You)</span> : null}
                          </p>
                          <p className="text-ivory/50 text-xs truncate">{member.department}</p>
                        </div>
                        <span className="rounded-full bg-ivory/10 text-ivory text-xs px-3 py-1 whitespace-nowrap">
                          {member.averageScore}%
                        </span>
                      </div>
                      <div className="mt-5 space-y-2 text-xs">
                        <p className="text-ivory/55">
                          Strong in{' '}
                          <span className="text-ivory">{member.strongSubjects.join(', ')}</span>
                        </p>
                        <p className="text-ivory/55">
                          Weak in{' '}
                          <span className="text-blush">{member.weakSubjects.join(', ') || 'nothing'}</span>
                        </p>
                        {member.learningPreference || member.availability ? (
                          <p className="text-ivory/40">
                            {[member.learningPreference, member.availability].filter(Boolean).join(' · ')}
                          </p>
                        ) : null}
                      </div>
                    </GlassCard>
                  ))}
                </div>
              </div>

              <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
                <GlassCard className="p-6 md:p-8">
                  <div className="flex items-center gap-3 mb-5 text-ivory">
                    <MessageSquare size={18} className="text-blush" />
                    <h2 className="text-2xl" style={{ fontFamily: "'Instrument Serif', serif" }}>
                      Group Chat
                    </h2>
                  </div>

                  <div className="space-y-3 max-h-80 overflow-y-auto pr-1">
                    {messages.length === 0 ? (
                      <p className="text-ivory/50 text-sm">No messages yet. Start the conversation!</p>
                    ) : (
                      messages.map((message) => (
                        <div
                          key={message.id}
                          className={`liquid-glass rounded-2xl px-4 py-3 max-w-[85%] ${
                            message.isSelf ? 'ml-auto bg-ivory/10' : ''
                          }`}
                        >
                          <div className="flex items-center justify-between gap-3 mb-1">
                            <p className="text-ivory text-xs font-medium">{message.sender}</p>
                            <span className="text-ivory/35 text-[10px]">
                              {new Date(message.createdAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                            </span>
                          </div>
                          <p className="text-ivory/70 text-sm leading-relaxed">{message.message}</p>
                        </div>
                      ))
                    )}
                  </div>

                  <form onSubmit={handleSend} className="mt-5 flex items-center gap-3">
                    <input
                      value={draft}
                      onChange={(event) => setDraft(event.target.value)}
                      placeholder="Type a message..."
                      aria-label="Chat message"
                      className={inputClass}
                    />
                    <button
                      type="submit"
                      disabled={sending || !draft.trim()}
                      aria-label="Send message"
                      className="rounded-full w-11 h-11 flex-shrink-0 bg-blush text-ink flex items-center justify-center transition-colors hover:bg-blush/90 disabled:opacity-40 disabled:cursor-not-allowed"
                    >
                      <Send size={17} />
                    </button>
                  </form>
                </GlassCard>

                <GlassCard className="p-6 md:p-8">
                  <div className="flex items-center gap-3 mb-5 text-ivory">
                    <Activity size={18} className="text-blush" />
                    <h2 className="text-2xl" style={{ fontFamily: "'Instrument Serif', serif" }}>
                      Recent Activity
                    </h2>
                  </div>

                  <div className="space-y-3">
                    {group.activity.length === 0 ? (
                      <p className="text-ivory/50 text-sm">No activity yet.</p>
                    ) : (
                      group.activity.map((item: GroupActivityItem, index: number) => (
                        <div
                          key={`${item.type}-${item.createdAt}-${index}`}
                          className="liquid-glass rounded-2xl px-4 py-3 flex items-start gap-3"
                        >
                          <span
                            className={`w-2 h-2 rounded-full mt-1.5 flex-shrink-0 ${
                              item.type === 'message' ? 'bg-ivory/70' : 'bg-blush'
                            }`}
                          />
                          <div className="min-w-0 flex-1">
                            <p className="text-ivory text-xs font-medium">{item.actor}</p>
                            <p className="text-ivory/65 text-xs mt-0.5 leading-relaxed">{item.text}</p>
                            <p className="text-ivory/35 text-[10px] mt-1">
                              {item.detail} · {new Date(item.createdAt).toLocaleString()}
                            </p>
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                </GlassCard>
              </div>
            </>
          ) : !status ? null : formationState === 'need-profile' ? (
            <GlassCard className="py-16 text-center">
              <UserRound size={36} className="mx-auto text-ivory/30 mb-4" />
              <p className="text-ivory/70 text-sm font-medium">Complete your academic profile to join a study group.</p>
              <p className="text-ivory/45 text-xs mt-2">
                We need your subject scores to match you with complementary students.
              </p>
              <Link to="/student/profile" className={`mt-6 ${actionButtonClass}`}>
                <UserRound size={17} />
                Complete Profile
              </Link>
            </GlassCard>
          ) : formationState === 'waiting' ? (
            <GlassCard className="py-16 text-center">
              <Users size={36} className="mx-auto text-ivory/30 mb-4" />
              <p className="text-ivory/70 text-sm font-medium">
                {status?.message ?? 'Waiting for group placement.'}
              </p>
              {!status?.groupsGenerated && (
                <p className="text-ivory/45 text-xs mt-2">
                  Currently {status?.eligibleStudents ?? 0} students are eligible.
                  Check back soon.
                </p>
              )}
              <button type="button" onClick={handleGenerate} className={`mt-6 ${actionButtonClass}`}>
                <Users size={17} />
                Check Again
              </button>
            </GlassCard>
          ) : null}
        </div>
      </section>
    </StudentLayout>
  )
}
