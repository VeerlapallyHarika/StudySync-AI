import {
  UserSearch,
  BrainCircuit,
  Users,
  GraduationCap,
  LayoutDashboard,
  FileBarChart,
} from 'lucide-react'
import Reveal from './Reveal'

const FEATURES = [
  {
    icon: UserSearch,
    title: 'Student Profiling',
    description: 'Analyze academic strengths and weaknesses.',
  },
  {
    icon: BrainCircuit,
    title: 'Machine Learning',
    description: 'Use K-Means clustering for intelligent grouping.',
  },
  {
    icon: Users,
    title: 'Complementary Matching',
    description: 'Create balanced groups with diverse skills.',
  },
  {
    icon: GraduationCap,
    title: 'Study Groups',
    description: 'Automatically assign students into optimized teams.',
  },
  {
    icon: LayoutDashboard,
    title: 'Dashboard',
    description: 'Track your group assignments and study progress.',
  },
  {
    icon: FileBarChart,
    title: 'Reports',
    description: 'Generate downloadable group composition reports.',
  },
]

export default function FeaturesSection() {
  return (
    <section id="features" className="relative z-10 px-6 py-20">
      <div className="max-w-5xl mx-auto">
        <Reveal className="text-center mb-14">
          <h2
            className="text-4xl md:text-5xl text-white mb-5 tracking-tight"
            style={{ fontFamily: "'Instrument Serif', serif" }}
          >
            Built to balance every group
          </h2>
          <p className="text-white/60 text-base max-w-[700px] mx-auto leading-relaxed">
            Every stage of the pipeline, from profiling to reporting, works
            together to keep collaboration fair and effective.
          </p>
        </Reveal>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {FEATURES.map((feature, i) => {
            const Icon = feature.icon
            return (
              <Reveal key={feature.title} delayMs={i * 90}>
                <div className="liquid-glass rounded-2xl p-8 h-full hover:bg-white/5 transition-colors">
                  <div className="w-12 h-12 rounded-full liquid-glass flex items-center justify-center mb-6">
                    <Icon size={22} className="text-blue-400" />
                  </div>
                  <h3 className="text-white text-lg font-semibold mb-4">
                    {feature.title}
                  </h3>
                  <p className="text-white/60 text-sm leading-relaxed">
                    {feature.description}
                  </p>
                </div>
              </Reveal>
            )
          })}
        </div>
      </div>
    </section>
  )
}
