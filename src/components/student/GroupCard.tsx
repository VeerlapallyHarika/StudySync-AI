import GlassCard from '../GlassCard'

interface GroupCardProps {
  groupName: string
  members: string[]
  overallStrength: string
}

export default function GroupCard({ groupName, members, overallStrength }: GroupCardProps) {
  return (
    <GlassCard className="p-6 h-full">
      <p className="text-white/55 text-xs uppercase tracking-wide mb-3">Assigned Study Group</p>
      <h3 className="text-3xl text-white mb-5 tracking-tight" style={{ fontFamily: "'Instrument Serif', serif" }}>
        {groupName}
      </h3>

      <div className="space-y-4">
        <div>
          <p className="text-white/55 text-xs uppercase tracking-wide mb-3">Members</p>
          <div className="flex flex-wrap gap-2">
            {members.map((member) => (
              <span key={member} className="rounded-full px-4 py-2 bg-white/10 text-white text-sm">
                {member}
              </span>
            ))}
          </div>
        </div>

        <div className="liquid-glass rounded-2xl p-4">
          <p className="text-white/55 text-xs uppercase tracking-wide mb-2">Overall Group Strength</p>
          <p className="text-white text-sm leading-relaxed">{overallStrength}</p>
        </div>
      </div>
    </GlassCard>
  )
}
