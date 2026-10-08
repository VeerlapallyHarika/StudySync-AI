import {
  UserPlus,
  Database,
  ScanSearch,
  Grid3x3,
  Network,
  Puzzle,
  UsersRound,
  LayoutPanelTop,
} from 'lucide-react'
import Reveal from './Reveal'

const STEPS = [
  { icon: UserPlus, label: 'Student Registration' },
  { icon: Database, label: 'Academic Data Collection' },
  { icon: ScanSearch, label: 'Strength & Weakness Detection' },
  { icon: Grid3x3, label: 'Feature Vector Generation' },
  { icon: Network, label: 'K-Means Clustering' },
  { icon: Puzzle, label: 'Complementary Matching' },
  { icon: UsersRound, label: 'Study Group Assignment' },
  { icon: LayoutPanelTop, label: 'Dashboard & Reports' },
]

export default function WorkflowSection() {
  return (
    <section id="workflow" className="relative z-10 px-6 py-20">
      <div className="max-w-3xl mx-auto">
        <Reveal className="text-center mb-16">
          <h2
            className="text-4xl md:text-5xl text-ivory mb-4 tracking-tight"
            style={{ fontFamily: "'Instrument Serif', serif" }}
          >
            How it works
          </h2>
          <p className="text-ivory/60 text-base max-w-xl mx-auto leading-relaxed">
            A single pipeline carries every student from registration to a
            finished, balanced study group.
          </p>
        </Reveal>

        <div className="flex flex-col items-center">
          {STEPS.map((step, i) => {
            const Icon = step.icon
            const isLast = i === STEPS.length - 1
            return (
              <div key={step.label} className="flex flex-col items-center w-full">
                <Reveal delayMs={i * 100} className="w-full max-w-md">
                  <div className="liquid-glass rounded-2xl px-6 py-4 flex items-center gap-4 hover:bg-mauve/20 transition-colors">
                    <div className="w-10 h-10 rounded-full liquid-glass flex items-center justify-center flex-shrink-0">
                      <Icon size={18} className="text-blush" />
                    </div>
                    <span className="text-ivory text-sm font-medium">
                      {step.label}
                    </span>
                  </div>
                </Reveal>
                {!isLast && (
                  <div className="text-ivory/30 text-lg my-2 leading-none">
                    ↓
                  </div>
                )}
              </div>
            )
          })}
        </div>
      </div>
    </section>
  )
}
