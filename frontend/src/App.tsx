import type { ReactNode } from 'react'
import { Navigate, Route, Routes } from 'react-router'
import { useAuth } from './auth/context'
import DashboardPage from './pages/DashboardPage'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import Nivel1Page from './pages/nivel1/Nivel1Page'
import GemeloPage from './pages/gemelo/GemeloPage'
import AgentsPage from './pages/AgentsPage'
import PrivacyPage from './pages/PrivacyPage'
import RoutePage from './pages/RoutePage'
import WelcomePage from './pages/WelcomePage'

function Private({ children }: { children: ReactNode }) {
  const { user } = useAuth()
  return user ? children : <Navigate to="/login" replace />
}

function PublicOnly({ children }: { children: ReactNode }) {
  const { user } = useAuth()
  return user ? <Navigate to="/dashboard" replace /> : children
}

export default function App() {
  const { user } = useAuth()
  return (
    <Routes>
      <Route path="/login" element={<PublicOnly><LoginPage /></PublicOnly>} />
      <Route path="/register" element={<PublicOnly><RegisterPage /></PublicOnly>} />
      <Route path="/privacidad" element={<PrivacyPage />} />
      <Route path="/bienvenida" element={<Private><WelcomePage /></Private>} />
      <Route path="/dashboard" element={<Private><DashboardPage /></Private>} />
      <Route path="/ruta/:companyId" element={<Private><RoutePage /></Private>} />
      <Route path="/agentes/:companyId" element={<Private><AgentsPage /></Private>} />
      <Route path="/nivel1/:companyId" element={<Private><Nivel1Page /></Private>} />
      <Route path="/gemelo/:companyId" element={<Private><GemeloPage /></Private>} />
      <Route path="*" element={<Navigate to={user ? '/dashboard' : '/login'} replace />} />
    </Routes>
  )
}
