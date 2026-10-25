import { lazy, Suspense, type ReactNode } from 'react'
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
import ConstitucionPage from './pages/constitucion/ConstitucionPage'
import SurveyPublicPage from './pages/SurveyPublicPage'
import FinanzasPage from './pages/finanzas/FinanzasPage'
import ComunidadPage from './pages/comunidad/ComunidadPage'
import ApplesPage from './pages/ApplesPage'
import ConsolaPage from './pages/ConsolaPage'
import LevelPage from './pages/nivel/LevelPage'
import MarcaPage from './pages/empresa/MarcaPage'
import ExpedientePage from './pages/empresa/ExpedientePage'

// La oficina 3D pesa (three.js): se carga solo al entrar a /universo
const UniversoPage = lazy(() => import('./universo/UniversoPage'))

function Private({ children }: { children: ReactNode }) {
  const { user } = useAuth()
  return user ? children : <Navigate to="/login" replace />
}

// `?next=/universo` vuelve a donde estaba la persona tras entrar o registrarse (solo rutas internas)
function PublicOnly({ children }: { children: ReactNode }) {
  const { user } = useAuth()
  const next = new URLSearchParams(window.location.search).get('next') ?? ''
  const safe = next.startsWith('/') && !next.startsWith('//') ? next : '/dashboard'
  return user ? <Navigate to={safe} replace /> : children
}

export default function App() {
  const { user } = useAuth()
  return (
    <Routes>
      <Route path="/login" element={<PublicOnly><LoginPage /></PublicOnly>} />
      <Route path="/register" element={<PublicOnly><RegisterPage /></PublicOnly>} />
      <Route path="/privacidad" element={<PrivacyPage />} />
      <Route path="/encuesta/:token" element={<SurveyPublicPage />} />
      <Route path="/universo" element={
        <Suspense fallback={<div className="fixed inset-0 flex items-center justify-center bg-[#0a0a0f] text-sm text-slate-400">Abriendo la oficina de ADÁN…</div>}>
          <UniversoPage />
        </Suspense>} />
      <Route path="/bienvenida" element={<Private><WelcomePage /></Private>} />
      <Route path="/dashboard" element={<Private><DashboardPage /></Private>} />
      <Route path="/ruta/:companyId" element={<Private><RoutePage /></Private>} />
      <Route path="/agentes/:companyId" element={<Private><AgentsPage /></Private>} />
      <Route path="/nivel1/:companyId" element={<Private><Nivel1Page /></Private>} />
      <Route path="/nivel/:n/:companyId" element={<Private><LevelPage /></Private>} />
      <Route path="/gemelo/:companyId" element={<Private><GemeloPage /></Private>} />
      <Route path="/constitucion/:companyId" element={<Private><ConstitucionPage /></Private>} />
      <Route path="/finanzas/:companyId" element={<Private><FinanzasPage /></Private>} />
      <Route path="/marca/:companyId" element={<Private><MarcaPage /></Private>} />
      <Route path="/expediente/:companyId" element={<Private><ExpedientePage /></Private>} />
      <Route path="/comunidad" element={<Private><ComunidadPage /></Private>} />
      <Route path="/apples" element={<Private><ApplesPage /></Private>} />
      <Route path="/consola" element={<Private><ConsolaPage /></Private>} />
      <Route path="*" element={<Navigate to={user ? '/dashboard' : '/login'} replace />} />
    </Routes>
  )
}
