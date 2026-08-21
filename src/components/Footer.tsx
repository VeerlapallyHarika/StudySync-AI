import { Github, Linkedin, Mail } from 'lucide-react'

const SOCIALS = [
  { icon: Github, label: 'GitHub', href: '#' },
  { icon: Linkedin, label: 'LinkedIn', href: '#' },
  { icon: Mail, label: 'Email', href: '#' },
]

export default function Footer() {
  return (
    <footer id="contact" className="relative z-10 px-6 pb-16 pt-8">
      <div className="flex justify-center gap-4 mb-8">
        {SOCIALS.map(({ icon: Icon, label, href }) => (
          <a
            key={label}
            href={href}
            aria-label={label}
            className="liquid-glass rounded-full p-4 text-white/80 hover:text-white hover:bg-white/5 transition-all"
          >
            <Icon size={20} />
          </a>
        ))}
      </div>
      <div className="text-center text-white/40 text-sm space-y-1">
        <p>© 2026 StudySync AI</p>
        <p>Peer-to-Peer Study Group Agent</p>
      </div>
    </footer>
  )
}
