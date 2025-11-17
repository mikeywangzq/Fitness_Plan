import { Routes, Route } from 'react-router-dom'
import ChatPage from './pages/ChatPage'
import DashboardPage from './pages/DashboardPage'
import OnboardingPage from './pages/OnboardingPage'
import WorkoutPage from './pages/WorkoutPage'
import NutritionPage from './pages/NutritionPage'
import ProgressPage from './pages/ProgressPage'
import Layout from './components/Layout'

function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<ChatPage />} />
        <Route path="onboarding" element={<OnboardingPage />} />
        <Route path="dashboard" element={<DashboardPage />} />
        <Route path="workout" element={<WorkoutPage />} />
        <Route path="nutrition" element={<NutritionPage />} />
        <Route path="progress" element={<ProgressPage />} />
      </Route>
    </Routes>
  )
}

export default App
