import { Routes, Route } from 'react-router-dom'
import LandingPage from './pages/LandingPage'
import AnalyzePage from './pages/AnalyzePage'
import HowItWorksPage from './pages/HowItWorksPage'

export default function App() {
  return (
    <Routes>
      <Route path="/"             element={<LandingPage />} />
      <Route path="/analyze"      element={<AnalyzePage />} />
      <Route path="/how-it-works" element={<HowItWorksPage />} />
    </Routes>
  )
}
