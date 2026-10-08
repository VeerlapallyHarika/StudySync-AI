import { useState } from 'react'
import { Brain, Menu, X } from 'lucide-react'
import { Link } from 'react-router-dom'

const NAV_LINKS = [
  { label: 'Home', to: '/' },
  { label: 'Features', to: '/features' },
  { label: 'Workflow', to: '/#workflow' },
  { label: 'About', to: '/about' },
  { label: 'Contact', to: '/contact' },
]

export default function Navbar() {
  const [open, setOpen] = useState(false)

  return (
    <nav className="fixed inset-x-0 top-0 z-50 px-4 py-4 sm:px-6 sm:py-6">
      <div className="liquid-glass rounded-full px-4 sm:px-6 py-2.5 sm:py-3 flex items-center justify-between max-w-5xl mx-auto">
        <div className="flex items-center gap-4 sm:gap-8 min-w-0">
          <Link to="/" className="flex items-center gap-2 min-w-0" onClick={() => setOpen(false)}>
            <Brain size={24} className="text-ivory flex-shrink-0" />
            <span className="text-ivory font-semibold text-lg truncate">
              StudySync AI
            </span>
          </Link>
          <div className="hidden md:flex items-center gap-8">
            {NAV_LINKS.map((link) => (
              <Link
                key={link.label}
                to={link.to}
                className="text-ivory/80 hover:text-ivory transition-colors text-sm font-medium"
              >
                {link.label}
              </Link>
            ))}
          </div>
        </div>

        <div className="hidden md:flex items-center gap-4">
          <Link
            to="/student/login"
            className="text-ivory text-sm font-medium hover:text-ivory/80 transition-colors"
          >
            Student Login
          </Link>
          <Link
            to="/student/register"
            className="bg-blush rounded-full px-6 py-2 text-ink text-sm font-semibold hover:bg-blush/90 transition-colors"
          >
            Get Started
          </Link>
        </div>

        <button
          type="button"
          className="md:hidden text-ivory p-2 -mr-1 flex-shrink-0"
          onClick={() => setOpen((current) => !current)}
          aria-label={open ? 'Close navigation' : 'Open navigation'}
          aria-expanded={open}
        >
          {open ? <X size={22} /> : <Menu size={22} />}
        </button>
      </div>

      {open && (
        <div className="md:hidden mt-3">
          <div className="liquid-glass rounded-3xl p-4 max-w-5xl mx-auto flex flex-col gap-1">
            {NAV_LINKS.map((link) => (
              <Link
                key={link.label}
                to={link.to}
                onClick={() => setOpen(false)}
                className="text-ivory/85 hover:text-ivory transition-colors text-sm font-medium px-4 py-3 rounded-xl hover:bg-mauve/20"
              >
                {link.label}
              </Link>
            ))}
            <div className="h-px bg-ivory/10 my-2" />
            <div className="flex flex-col gap-2">
              <Link
                to="/student/login"
                onClick={() => setOpen(false)}
                className="text-ivory/85 hover:text-ivory transition-colors text-sm font-medium px-4 py-3 rounded-xl hover:bg-mauve/20"
              >
                Student Login
              </Link>
              <Link
                to="/student/register"
                onClick={() => setOpen(false)}
                className="bg-blush rounded-full px-4 py-3 text-ink text-sm font-semibold text-center transition-colors hover:bg-blush/90"
              >
                Get Started
              </Link>
            </div>
          </div>
        </div>
      )}
    </nav>
  )
}
