import Reveal from './Reveal'

export default function AboutSection() {
  return (
    <section id="about" className="relative z-10 px-6 py-20">
      <div className="max-w-3xl mx-auto text-center">
        <Reveal>
          <h2
            className="text-4xl md:text-5xl text-white mb-8 tracking-tight"
            style={{ fontFamily: "'Instrument Serif', serif" }}
          >
            Why Peer-to-Peer Study Group Agent?
          </h2>
        </Reveal>
        <Reveal delayMs={120}>
          <div className="liquid-glass rounded-2xl p-8 md:p-10 text-left space-y-4">
            <p className="text-white/70 text-base leading-relaxed">
              Traditional study groups are often created manually or
              randomly, resulting in unbalanced collaboration.
            </p>
            <p className="text-white/70 text-base leading-relaxed">
              This platform analyzes academic performance using Machine
              Learning to automatically build balanced teams where students
              can learn from each other's strengths.
            </p>
          </div>
        </Reveal>
      </div>
    </section>
  )
}
