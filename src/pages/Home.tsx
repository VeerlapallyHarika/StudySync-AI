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
    <div className="relative bg-black min-h-screen overflow-hidden">
      <LandingBackground />
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
