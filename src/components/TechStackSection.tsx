import Reveal from './Reveal'

const TECHNOLOGIES = [
  'Python',
  'Django',
  'SQLite',
  'Scikit-learn',
  'React',
  'TypeScript',
  'Tailwind CSS',
  'MotionSites',
]

export default function TechStackSection() {
  return (
    <section className="relative z-10 px-6 py-20">
      <div className="max-w-4xl mx-auto">
        <Reveal className="text-center mb-14">
          <h2
            className="text-4xl md:text-5xl text-ivory mb-4 tracking-tight"
            style={{ fontFamily: "'Instrument Serif', serif" }}
          >
            Built with a modern stack
          </h2>
          <p className="text-ivory/60 text-base max-w-xl mx-auto leading-relaxed">
            A production-grade foundation for both the clustering engine and
            the interface students use every day.
          </p>
        </Reveal>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          {TECHNOLOGIES.map((tech, i) => (
            <Reveal key={tech} delayMs={i * 70}>
              <div className="liquid-glass rounded-xl px-4 py-6 text-center hover:bg-mauve/20 transition-colors">
                <span className="text-ivory/80 text-sm font-medium">
                  {tech}
                </span>
              </div>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  )
}
