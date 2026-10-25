import '@fontsource-variable/space-grotesk'
import './universo.css'
import { Component, useState, type ReactNode } from 'react'
import { Link } from 'react-router'
import World from './scene/World'
import { useUniverso } from './store'
import { setVoiceOn, voiceOn } from './voice'

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
// Subtítulos de quien habla, como en una película
function Subtitle() {
  const sub = useUniverso((s) => s.subtitle)
  if (!sub) return null
  return (
    <div className="pointer-events-none absolute inset-x-0 bottom-16 flex justify-center px-6" aria-live="polite">
      <p className="max-w-[90%] rounded-xl bg-black/75 px-4 py-2 text-center text-sm text-white shadow-lg">
        <b style={{ color: sub.color }}>{sub.who}:</b> {sub.text}
      </p>
    </div>
  )
}

export default function EmbeddedWorld() {
  const [voice, setVoice] = useState(voiceOn)
  return (
    <div className="universo relative h-full w-full overflow-hidden rounded-2xl">
      <Boundary><World embedded /></Boundary>
      <Subtitle />
      <div className="pointer-events-none absolute left-3 top-3 rounded-full bg-black/50 px-3 py-1 text-[11px] font-semibold tracking-wider text-cyan-200">
        TU EQUIPO EN LA OFICINA
      </div>
 <div className="absolute bottom-3 right-3 flex gap-1" aria-label="Controles de la cámara">
        <button type="button" onClick={() => { setVoiceOn(!voice); setVoice(!voice) }} aria-pressed={voice}
          title={voice ? 'Silenciar la voz de los personajes' : 'Activar la voz de los personajes'} aria-label="Voz de los personajes"
          className="grid h-9 w-9 place-items-center rounded-full bg-black/60 text-lg text-white hover:bg-black/80">{voice ? '🔊' : '🔇'}</button>
        {([['reset', '⟲', 'Vista general de la oficina'], ['in', '＋', 'Acercar'], ['out', '－', 'Alejar']] as const).map(([op, icon, label]) => (
          <button key={op} type="button" onClick={() => useUniverso.getState().camera(op)} title={label} aria-label={label}
            className="grid h-9 w-9 place-items-center rounded-full bg-black/60 text-lg text-white hover:bg-black/80">{icon}</button>
        ))}
      </div>
      <Link to="/universo" className="absolute right-3 top-3 rounded-full bg-black/50 px-3 py-1 text-[11px] text-slate-200 hover:text-white">
        Abrir el Universo ↗
      </Link>
    </div>
  )
}
