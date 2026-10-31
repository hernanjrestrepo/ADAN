import '@fontsource-variable/space-grotesk'
import './universo.css'
import { Component, type ReactNode, useCallback, useEffect, useState } from 'react'
import World from './scene/World'
import { useUniverso } from './store'
import AdanChat from './ui/AdanChat'
import AgentCard from './ui/AgentCard'
import ArenaOverlay from './ui/ArenaOverlay'
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
  // ADAN recibe a la persona con el chat abierto; se recoge cuando sesiona el Board, La Arena o se mira a alguien
  const [chatOpen, setChatOpen] = useState(true)
  useEffect(() => useUniverso.subscribe((s, prev) => {
    if ((s.board && !prev.board) || (s.arena && !prev.arena) || (s.selected && !prev.selected)) setChatOpen(false)
  }), [])

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
          {/* En el celular, con el chat abierto, la misión se recoge: arriba la oficina, abajo la conversación */}
          <div className={chatOpen ? 'max-md:hidden' : ''}>
            {panel === 'ruta' ? <RoutePanel /> : panel === 'ecosistema' ? <EcosystemPanel /> : panel === 'insignias' ? <BadgesPanel /> : <MissionPanel />}
          </div>
          <AgentCard />
          <BoardOverlay />
          <ArenaOverlay />
          {!chatOpen && <Feed />}
          <Celebration />
          <ReportModal />
        </>
      ) : (
        <Onboarding />
      )}
      <AdanChat open={chatOpen} onToggle={() => setChatOpen((v) => !v)} />
    </div>
  )
}
