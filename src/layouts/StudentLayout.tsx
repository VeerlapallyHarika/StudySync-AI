import { useState, type ReactNode } from 'react'
import { NavLink, useNavigate } from 'react-router-dom'
import {
  Bell,
  Brain,
  FolderOpen,
  LayoutDashboard,
  LineChart,
  LogOut,
  Menu,
  Settings,
  User,
  Users,
  X,
} from 'lucide-react'
import SkipLink from '../components/SkipLink'
import { clearStudentSession } from '../services/studentService'

interface StudentLayoutProps {
  children: ReactNode
}

const NAV_ITEMS = [
  { label: 'Dashboard', to: '/student/dashboard', icon: LayoutDashboard },
  { label: 'Notifications', to: '/student/notifications', icon: Bell },
  { label: 'Profile', to: '/student/profile', icon: User },
  { label: 'Groups', to: '/student/groups', icon: Users },
  { label: 'Insights', to: '/student/insights', icon: LineChart },
  { label: 'Resources', to: '/student/resources', icon: FolderOpen },
  { label: 'Settings', to: '/student/settings', icon: Settings },
]

function SidebarContent({ onNavigate }: { onNavigate?: () => void }) {
  const navigate = useNavigate()

  const handleLogout = () => {
    clearStudentSession()
    navigate('/', { replace: true })
  }

  return (
    <>
      <div className="flex items-center gap-3 px-2 mb-8">
        <div className="w-10 h-10 rounded-2xl bg-white text-black flex items-center justify-center flex-shrink-0">
          <Brain size={20} />
        </div>
        <div className="min-w-0">
          <p className="text-white font-semibold leading-tight truncate">StudySync AI</p>
          <p className="text-white/50 text-xs">Student Portal</p>
        </div>
      </div>

      <nav className="space-y-1.5 flex-1">
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon
          return (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === '/student/dashboard'}
              onClick={onNavigate}
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-2xl px-4 py-2.5 text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-cyan-400/10 border border-cyan-300/20 text-white'
                    : 'text-white/60 hover:text-white hover:bg-white/5'
                }`
              }
            >
              {({ isActive }) => (
                <>
                  <Icon size={17} className={isActive ? 'text-cyan-300 flex-shrink-0' : 'flex-shrink-0'} />
                  {item.label}
                </>
              )}
            </NavLink>
          )
        })}
      </nav>

      <div className="mt-8">
        <button
          type="button"
          onClick={handleLogout}
          className="w-full flex items-center gap-3 rounded-2xl px-4 py-2.5 text-sm font-medium text-white/60 hover:text-white hover:bg-white/5 transition-colors"
        >
          <LogOut size={17} className="flex-shrink-0" />
          Logout
        </button>
      </div>
    </>
  )
}

export default function StudentLayout({ children }: StudentLayoutProps) {
  const [drawerOpen, setDrawerOpen] = useState(false)

  return (
    <div className="h-screen bg-black overflow-hidden relative flex">
      <div className="absolute inset-0 bg-gradient-to-b from-blue-950/20 via-black to-black pointer-events-none" />
      <SkipLink />

      <aside className="hidden md:flex flex-col md:w-56 lg:w-64 flex-shrink-0 relative z-20 h-screen p-4 lg:p-5">
        <div className="liquid-glass rounded-2xl p-5 flex flex-col h-full">
          <SidebarContent />
        </div>
      </aside>

      {drawerOpen ? (
        <div className="fixed inset-0 z-50 md:hidden">
          <div className="absolute inset-0 bg-black/70 backdrop-blur-sm" onClick={() => setDrawerOpen(false)} />
          <aside className="absolute left-0 top-0 h-full w-72 p-4">
            <div className="liquid-glass rounded-2xl p-5 flex flex-col h-full relative">
              <button
                type="button"
                onClick={() => setDrawerOpen(false)}
                aria-label="Close navigation"
                className="absolute top-4 right-4 z-10 w-9 h-9 rounded-full liquid-glass text-white/70 hover:text-white flex items-center justify-center transition-colors"
              >
                <X size={18} />
              </button>
              <SidebarContent onNavigate={() => setDrawerOpen(false)} />
            </div>
          </aside>
        </div>
      ) : null}

      <div className="flex-1 min-w-0 relative z-10 flex flex-col h-screen overflow-y-auto">
        <header className="md:hidden px-4 pt-4 flex-shrink-0">
          <div className="liquid-glass rounded-2xl px-4 py-3 flex items-center justify-between">
            <div className="flex items-center gap-2 min-w-0">
              <Brain size={18} className="text-white flex-shrink-0" />
              <div className="min-w-0">
                <p className="text-white font-semibold text-sm leading-tight truncate">StudySync AI</p>
                <p className="text-white/50 text-xs">Student Portal</p>
              </div>
            </div>
            <button
              type="button"
              onClick={() => setDrawerOpen(true)}
              aria-label="Open navigation"
              className="text-white/70 hover:text-white transition-colors"
            >
              <Menu size={20} />
            </button>
          </div>
        </header>

        <main id="main-content" className="flex-1 px-4 py-10 md:px-8 md:py-10">
          {children}
        </main>
      </div>
    </div>
  )
}
