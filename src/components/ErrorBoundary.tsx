import { Component, type ErrorInfo, type ReactNode } from 'react'
import GlassCard from './GlassCard'

interface ErrorBoundaryProps {
  children: ReactNode
}

interface ErrorBoundaryState {
  hasError: boolean
}

export default class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  state: ErrorBoundaryState = { hasError: false }

  static getDerivedStateFromError(): ErrorBoundaryState {
    return { hasError: true }
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error('StudySync UI error:', error, info)
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-black flex items-center justify-center px-6">
          <div className="max-w-md w-full">
            <GlassCard className="p-8 text-center">
              <p className="text-white/50 text-sm uppercase tracking-widest mb-3">Something went wrong</p>
              <h1 className="text-3xl text-white mb-4" style={{ fontFamily: "'Instrument Serif', serif" }}>
                An unexpected error occurred
              </h1>
              <button
                type="button"
                onClick={() => {
                  this.setState({ hasError: false })
                }}
                className="rounded-full bg-white text-black px-6 py-3 text-sm font-medium transition-colors hover:bg-white/90"
              >
                Try again
              </button>
            </GlassCard>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}
