import Navbar from '../components/Navbar'
import LandingBackground from '../components/LandingBackground'
import Hero from '../components/Hero'
import FeaturesSection from '../components/FeaturesSection'
import WorkflowSection from '../components/WorkflowSection'
import AboutSection from '../components/AboutSection'
import TechStackSection from '../components/TechStackSection'
import Footer from '../components/Footer'

export default function HomePage() {
  return (
    <div className="relative bg-ink min-h-screen overflow-hidden">
      <LandingBackground />
      <div className="absolute inset-0 pointer-events-none" aria-hidden="true">
        <div className="aurora-blob -top-32 -left-24 h-[460px] w-[460px] bg-mauve/30" />
        <div className="aurora-blob top-[38%] -right-40 h-[440px] w-[440px] bg-plum/60" />
        <div className="aurora-blob bottom-[8%] left-[15%] h-[400px] w-[400px] bg-blush/10" />
      </div>
      <div className="relative z-10">
        <Hero navSlot={<Navbar />} />
        <FeaturesSection />
        <WorkflowSection />
        <AboutSection />
        <TechStackSection />
        <Footer />
      </div>
    </div>
  )
}
