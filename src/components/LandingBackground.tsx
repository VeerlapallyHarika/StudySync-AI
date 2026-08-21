import { useEffect, useRef } from 'react'

const VIDEO_SRC =
  'https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260328_115001_bcdaa3b4-03de-47e7-ad63-ae3e392c32d4.mp4'

const FADE_MS = 500
const FADE_OUT_THRESHOLD = 0.55

export default function LandingBackground() {
  const videoRef = useRef<HTMLVideoElement | null>(null)
  const rafRef = useRef<number | null>(null)
  const fadingOutRef = useRef(false)

  useEffect(() => {
    const video = videoRef.current
    if (!video) return

    const cancelRunningFade = () => {
      if (rafRef.current !== null) {
        cancelAnimationFrame(rafRef.current)
        rafRef.current = null
      }
    }

    const fadeTo = (target: number, duration: number, onComplete?: () => void) => {
      cancelRunningFade()
      const startOpacity = parseFloat(video.style.opacity || '1')
      const startTime = performance.now()

      const step = (now: number) => {
        const elapsed = now - startTime
        const progress = Math.min(elapsed / duration, 1)
        const nextOpacity = startOpacity + (target - startOpacity) * progress
        video.style.opacity = String(nextOpacity)

        if (progress < 1) {
          rafRef.current = requestAnimationFrame(step)
        } else {
          rafRef.current = null
          if (onComplete) onComplete()
        }
      }

      rafRef.current = requestAnimationFrame(step)
    }

    const handleLoadOrLoopStart = () => {
      fadingOutRef.current = false
      fadeTo(1, FADE_MS)
    }

    const handleTimeUpdate = () => {
      if (!video.duration) return
      const remaining = video.duration - video.currentTime
      if (remaining <= FADE_OUT_THRESHOLD && !fadingOutRef.current) {
        fadingOutRef.current = true
        fadeTo(0, FADE_MS)
      }
    }

    const handleEnded = () => {
      video.style.opacity = '0'
      window.setTimeout(() => {
        video.currentTime = 0
        video.play()
        fadingOutRef.current = false
        fadeTo(1, FADE_MS)
      }, 100)
    }

    video.addEventListener('loadeddata', handleLoadOrLoopStart)
    video.addEventListener('timeupdate', handleTimeUpdate)
    video.addEventListener('ended', handleEnded)

    return () => {
      cancelRunningFade()
      video.removeEventListener('loadeddata', handleLoadOrLoopStart)
      video.removeEventListener('timeupdate', handleTimeUpdate)
      video.removeEventListener('ended', handleEnded)
    }
  }, [])

  return (
    <>
      <video
        ref={videoRef}
        className="fixed inset-0 w-full h-full object-cover"
        src={VIDEO_SRC}
        autoPlay
        muted
        playsInline
        style={{ opacity: 0 }}
      />
      <div className="fixed inset-0 bg-black/45 backdrop-blur-[2px]" />
    </>
  )
}
