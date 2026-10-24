import '@fontsource-variable/space-grotesk'
import './universo.css'
import { Component, type ReactNode, useCallback, useState } from 'react'
import { Link } from 'react-router'
import World from './scene/World'
import { useUniverso } from './store'
import AgentCard from './ui/AgentCard'
import BoardOverlay from './ui/BoardOverlay'
import Celebration from './ui/Celebration'
import Feed from './ui/Feed'
import MissionPanel from './ui/MissionPanel'
import Onboarding from './ui/Onboarding'
import { BadgesPanel, EcosystemPanel, RoutePanel } from './ui/Panels'
import ReportModal from './ui/ReportModal'
import TopBar from './ui/TopBar'
import { useAutopilot } from './useAutopilot'

// Si el navegador no tiene WebGL, el recorrido sigue sin la oficina 3D
class SceneBoundary extends Component<{ children: ReactNode }, { failed: boolean }> {
  state = { failed: false }
  static getDerivedStateFromError() {
    return { failed: true }
  }
  render() {
    if (this.state.failed) {
      return (
        <div className="absolute inset-0 flex items-center justify-center bg-[radial-gradient(ellipse_at_center,#12224b,#0a0a0f)]">
          <p className="max-w-sm text-center text-sm text-slate-400">Tu navegador no pudo mostrar la oficina 3D. El recorrido de los 7 Niveles funciona igual.</p>
        </div>
      )
    }
    return this.props.children
  }
}

// `?escena=0` muestra el recorrido sin la oficina 3D: equipos de poca potencia y pruebas sin GPU
const SIN_ESCENA = new URLSearchParams(window.location.search).get('escena') === '0'

function Fondo() {
  return <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,#12224b,#0a0a0f)]" />
}

export default function UniversoPage() {
  const started = useUniverso((s) => s.started)
  const panel = useUniverso((s) => s.panel)
  const [autopilot, setAutopilot] = useState(false)
  const stop = useCallback(() => setAutopilot(false), [])
  useAutopilot(autopilot && started, stop)

  return (
    <div className="universo fixed inset-0 overflow-hidden">
      {SIN_ESCENA ? <Fondo /> : (
        <SceneBoundary>
          <div className="absolute inset-0" data-testid="universo-scene"><World /></div>
        </SceneBoundary>
      )}
      {started ? (
        <>
          <TopBar autopilot={autopilot} onAutopilot={() => setAutopilot((v) => !v)} />
          {panel === 'ruta' ? <RoutePanel /> : panel === 'ecosistema' ? <EcosystemPanel /> : panel === 'insignias' ? <BadgesPanel /> : <MissionPanel />}
          <AgentCard />
          <BoardOverlay />
          <Feed />
          <Celebration />
          <ReportModal />
        </>
      ) : (
        <>
          <Onboarding />
          <Link to="/login" className="u-no-print fixed right-4 top-4 z-50 text-xs text-slate-400 hover:text-white">Ya tengo cuenta →</Link>
        </>
      )}
    </div>
  )
}
