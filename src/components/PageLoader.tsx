import { Brain } from 'lucide-react'
import GlassCard from './GlassCard'
import { SkeletonBlock, SkeletonStat } from './Skeleton'

export default function PageLoader() {
  return (
    <div className="min-h-screen bg-black relative overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-b from-blue-950/20 via-black to-black" />
      <div className="relative z-10 min-h-screen flex flex-col items-center justify-center px-6">
        <GlassCard className="p-8 mb-8 text-center stat-float">
          <Brain size={28} className="mx-auto text-white mb-3" />
          <p className="text-white/60 text-xs uppercase tracking-widest">StudySync AI</p>
          <p className="text-white text-sm font-medium mt-1">Loading experience</p>
        </GlassCard>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-5 w-full max-w-3xl">
          <SkeletonStat />
          <SkeletonStat />
          <SkeletonStat />
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-5 w-full max-w-3xl mt-5">
          <SkeletonBlock className="h-40" />
          <SkeletonBlock className="h-40" />
        </div>
        <p className="sr-only" role="status" aria-live="polite">
          Loading page
        </p>
      </div>
    </div>
  )
}
