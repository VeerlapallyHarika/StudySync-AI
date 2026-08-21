import GlassCard from '../GlassCard'

interface StrengthCardProps {
  strengths: string[]
  weaknesses: string[]
}

export default function StrengthCard({ strengths, weaknesses }: StrengthCardProps) {
  return (
    <GlassCard className="p-6 h-full">
      <h3 className="text-white text-xl font-semibold mb-5">Strength Analysis</h3>

      <div className="space-y-5">
        <div>
          <p className="text-white/55 text-xs uppercase tracking-wide mb-3">Strengths</p>
          <div className="flex flex-wrap gap-2">
            {strengths.map((item) => (
              <span key={item} className="rounded-full px-4 py-2 bg-emerald-400/15 text-emerald-200 text-xs font-medium border border-emerald-300/20">
                {item}
              </span>
            ))}
          </div>
        </div>

        <div>
          <p className="text-white/55 text-xs uppercase tracking-wide mb-3">Weaknesses</p>
          <div className="flex flex-wrap gap-2">
            {weaknesses.map((item) => (
              <span key={item} className="rounded-full px-4 py-2 bg-rose-400/15 text-rose-200 text-xs font-medium border border-rose-300/20">
                {item}
              </span>
            ))}
          </div>
        </div>
      </div>
    </GlassCard>
  )
}
