import { useState, type ReactNode } from 'react'
import { ArrowRight } from 'lucide-react'
import Reveal from './Reveal'

const STATS = [
  {
    icon: '👨\u200d🎓',
    label: 'Students Supported',
    value: '1000+',
  },
  {
    icon: '🤖',
    label: 'AI Clustering',
    value: 'K-Means',
  },
  {
    icon: '📚',
    label: 'Learning Groups',
    value: 'Automated',
  },
  {
    icon: '⚡',
    label: 'Processing',
    value: 'Real-Time',
  },
]

interface HeroProps {
  navSlot?: ReactNode
}

export default function Hero({ navSlot }: HeroProps) {
  const [studentId, setStudentId] = useState('')

  return (
    <div className="relative flex flex-col">
      {navSlot}

      <div className="relative z-10 flex flex-col items-center px-6 pb-0 text-center pt-[140px]">
        <div className="w-full flex flex-col items-center">
          <h1
            className="text-4xl md:text-5xl lg:text-7xl text-white mb-8 tracking-tight max-w-[900px]"
            style={{ fontFamily: "'Instrument Serif', serif" }}
          >
            Peer-to-Peer Study Group Agent
          </h1>

          <p className="text-white/70 text-base md:text-lg max-w-[700px] mb-6 leading-relaxed">
            Automatically create balanced study groups using Machine Learning
            and K-Means Clustering. Analyze academic strengths and weaknesses to
            build collaborative learning teams.
          </p>

          <div className="max-w-[680px] w-full">
            <div className="liquid-glass rounded-full pl-6 pr-2 py-2 flex items-center gap-3">
              <input
                type="text"
                value={studentId}
                onChange={(e) => setStudentId(e.target.value)}
                placeholder="Enter Student ID or Explore the Project"
                className="bg-transparent flex-1 outline-none text-white placeholder:text-white/40 text-base min-w-0"
              />
              <button className="bg-white rounded-full px-5 py-3 text-black text-sm font-semibold flex items-center gap-2 whitespace-nowrap hover:bg-white/90 transition-colors">
                Get Started
                <ArrowRight size={18} />
              </button>
            </div>

            <button className="liquid-glass rounded-full px-8 py-3 text-white text-sm font-medium hover:bg-white/5 transition-colors mx-auto block mt-6">
              Explore Features
            </button>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-4xl w-full mt-[60px]">
            {STATS.map((stat, i) => (
              <Reveal key={stat.label} delayMs={i * 120}>
                <div className="liquid-glass stat-float rounded-2xl px-4 py-6 flex flex-col items-center gap-2 text-center h-full">
                  <span className="text-2xl">{stat.icon}</span>
                  <span className="text-white/60 text-xs font-medium uppercase tracking-wide">
                    {stat.label}
                  </span>
                  <span className="text-white text-lg font-semibold">
                    {stat.value}
                  </span>
                </div>
              </Reveal>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
