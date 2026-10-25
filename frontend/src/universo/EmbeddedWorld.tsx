import '@fontsource-variable/space-grotesk'
import './universo.css'
import { Component, type ReactNode } from 'react'
import { Link } from 'react-router'
import World from './scene/World'

// Si el navegador no puede con WebGL, el chat sigue igual
class Boundary extends Component<{ children: ReactNode }, { failed: boolean }> {
  state = { failed: false }
  static getDerivedStateFromError() {
    return { failed: true }
  }
  render() {
    if (this.state.failed) return <p className="p-4 text-xs text-slate-400">Tu navegador no pudo mostrar la oficina 3D.</p>
    return this.props.children
  }
}

// La oficina de ADÁN al lado de la conversación: el equipo reacciona a lo que hablas y los gráficos salen en pantalla
export default function EmbeddedWorld() {
  return (
    <div className="universo relative h-full w-full overflow-hidden rounded-2xl">
      <Boundary><World embedded /></Boundary>
      <div className="pointer-events-none absolute left-3 top-3 rounded-full bg-black/50 px-3 py-1 text-[11px] font-semibold tracking-wider text-cyan-200">
        TU EQUIPO EN LA OFICINA
      </div>
      <Link to="/universo" className="absolute right-3 top-3 rounded-full bg-black/50 px-3 py-1 text-[11px] text-slate-200 hover:text-white">
        Abrir el Universo ↗
      </Link>
    </div>
  )
}
