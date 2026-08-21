import { useEffect, useState } from 'react'
import GlassCard from '../../components/GlassCard'
import StudentLayout from '../../layouts/StudentLayout'
import usePageTitle from '../../hooks/usePageTitle'
import StudentCard from '../../components/student/StudentCard'
import SubjectCard from '../../components/student/SubjectCard'
import StrengthCard from '../../components/student/StrengthCard'
import GroupCard from '../../components/student/GroupCard'
import NotificationCard from '../../components/student/NotificationCard'
import { getStudentDashboard } from '../../services/studentService'
import type { StudentDashboardData } from '../../types/student'

export default function StudentDashboardPage() {
  usePageTitle('Student Dashboard')
  const [dashboard, setDashboard] = useState<StudentDashboardData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let mounted = true

    const loadDashboard = async () => {
      setLoading(true)
      setError('')

      try {
        const response = await getStudentDashboard()
        if (mounted) {
          setDashboard(response)
        }
      } catch (loadError) {
        if (mounted) {
          setError(loadError instanceof Error ? loadError.message : 'Unable to load the dashboard.')
        }
      } finally {
        if (mounted) {
          setLoading(false)
        }
      }
    }

    loadDashboard()

    return () => {
      mounted = false
    }
  }, [])

  if (loading) {
    return (
    <StudentLayout>
      <section className="px-2 md:px-6 py-8 md:py-14">
        <div className="max-w-6xl mx-auto">
          <GlassCard className="p-8 text-center text-white/70">Loading student dashboard...</GlassCard>
        </div>
      </section>
    </StudentLayout>
    )
  }

  if (error && !dashboard) {
    return (
    <StudentLayout>
      <section className="px-2 md:px-6 py-8 md:py-14">
        <div className="max-w-6xl mx-auto">
          <GlassCard className="p-8 text-center text-rose-100 border border-rose-400/25 bg-rose-500/10">
            {error}
          </GlassCard>
        </div>
      </section>
    </StudentLayout>
    )
  }

  const currentDashboard = dashboard!

  return (
    <StudentLayout>
      <section className="px-2 md:px-6 py-8 md:py-14">
        <div className="max-w-6xl mx-auto space-y-8">
          <div className="max-w-3xl">
            <h1
              className="text-4xl md:text-5xl text-white tracking-tight"
              style={{ fontFamily: "'Instrument Serif', serif" }}
            >
              Welcome, {currentDashboard.welcomeName}
            </h1>
            <p className="text-white/55 text-sm mt-3">Here is an overview of your academic standing and study group.</p>
          </div>

          {error ? (
            <div className="liquid-glass rounded-2xl border border-rose-400/25 bg-rose-500/10 px-4 py-3 text-xs text-rose-100">
              {error}
            </div>
          ) : null}

          <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-6">
            {currentDashboard.stats.map((stat) => (
              <StudentCard key={stat.label} title={stat.label} value={stat.value} description={stat.note} />
            ))}
          </div>

          <div className="space-y-5">
            <div>
              <h2
                className="text-2xl text-white mb-2 tracking-tight"
                style={{ fontFamily: "'Instrument Serif', serif" }}
              >
                Academic Summary
              </h2>
              <p className="text-white/55 text-sm">Subject performance with live progress bars.</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
              {currentDashboard.academicSummary.map((subject) => (
                <SubjectCard
                  key={subject.subject}
                  subject={subject.subject}
                  score={subject.score}
                  label={subject.status}
                  description={subject.description}
                />
              ))}
            </div>
          </div>

          <div className="grid grid-cols-1 xl:grid-cols-[1fr_1.05fr] gap-6">
            <StrengthCard
              strengths={currentDashboard.strengthAnalysis.strengths}
              weaknesses={currentDashboard.strengthAnalysis.weaknesses}
            />

            <GroupCard
              groupName={currentDashboard.assignedGroup.name}
              members={currentDashboard.assignedGroup.members}
              overallStrength={currentDashboard.assignedGroup.overallStrength}
            />
          </div>

          <div className="space-y-5">
            <div>
              <h2
                className="text-2xl text-white mb-2 tracking-tight"
                style={{ fontFamily: "'Instrument Serif', serif" }}
              >
                Group Members
              </h2>
              <p className="text-white/55 text-sm">Each member card is ready for backend data.</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
              {currentDashboard.groupMembers.map((member) => (
                <StudentCard
                  key={member.name}
                  title={member.status}
                  avatar={member.avatar}
                  subtitle={member.name}
                  description={member.department}
                  items={[
                    { label: 'Strong Subject', value: member.strongSubject },
                    { label: 'Weak Subject', value: member.weakSubject },
                  ]}
                />
              ))}
            </div>
          </div>

          <NotificationCard notifications={currentDashboard.notifications} />
        </div>
      </section>
    </StudentLayout>
  )
}
