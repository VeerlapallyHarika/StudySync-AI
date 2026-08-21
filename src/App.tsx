import { lazy, Suspense } from 'react'
import { Navigate, Route, Routes } from 'react-router-dom'
import ErrorBoundary from './components/ErrorBoundary'
import PageLoader from './components/PageLoader'
import RequireStudent from './components/student/RequireStudent'

const HomePage = lazy(() => import('./pages/Home'))
const AboutPage = lazy(() => import('./pages/About'))
const FeaturesPage = lazy(() => import('./pages/Features'))
const ContactPage = lazy(() => import('./pages/Contact'))
const NotFoundPage = lazy(() => import('./pages/NotFound'))
const ServerErrorPage = lazy(() => import('./pages/ServerError'))
const UnauthorizedPage = lazy(() => import('./pages/Unauthorized'))
const StudentRegisterPage = lazy(() => import('./pages/student/Register'))
const StudentDashboardPage = lazy(() => import('./pages/student/Dashboard'))
const StudentLoginPage = lazy(() => import('./pages/student/Login'))
const StudentProfilePage = lazy(() => import('./pages/student/Profile'))
const StudentInsightsPage = lazy(() => import('./pages/student/Insights'))
const StudentNotificationsPage = lazy(() => import('./pages/student/Notifications'))
const StudentSettingsPage = lazy(() => import('./pages/student/Settings'))
const StudentGroupsPage = lazy(() => import('./pages/student/Groups'))
const StudentResourcesPage = lazy(() => import('./pages/student/Resources'))

export default function App() {
  return (
    <ErrorBoundary>
      <Suspense fallback={<PageLoader />}>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/about" element={<AboutPage />} />
          <Route path="/features" element={<FeaturesPage />} />
          <Route path="/student/register" element={<StudentRegisterPage />} />
          <Route path="/student/profile" element={<RequireStudent><StudentProfilePage /></RequireStudent>} />
          <Route path="/student/dashboard" element={<RequireStudent><StudentDashboardPage /></RequireStudent>} />
          <Route path="/student/insights" element={<RequireStudent><StudentInsightsPage /></RequireStudent>} />
          <Route path="/student/notifications" element={<RequireStudent><StudentNotificationsPage /></RequireStudent>} />
          <Route path="/student/settings" element={<RequireStudent><StudentSettingsPage /></RequireStudent>} />
          <Route path="/student/groups" element={<RequireStudent><StudentGroupsPage /></RequireStudent>} />
          <Route path="/student/resources" element={<RequireStudent><StudentResourcesPage /></RequireStudent>} />
          <Route path="/student/login" element={<StudentLoginPage />} />
          <Route path="/contact" element={<ContactPage />} />
          <Route path="/500" element={<ServerErrorPage />} />
          <Route path="/unauthorized" element={<UnauthorizedPage />} />
          <Route path="/student-login" element={<Navigate to="/student/login" replace />} />
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </Suspense>
    </ErrorBoundary>
  )
}
