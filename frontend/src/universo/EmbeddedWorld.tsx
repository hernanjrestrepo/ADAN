import '@fontsource-variable/space-grotesk'
import './universo.css'
import { Component, useEffect, useState, type ReactNode } from 'react'
import { Link } from 'react-router'
import { api } from '../lib/api'
import { FLOORS, type Identity } from './scene/pisos'
import World from './scene/World'
import { useUniverso } from './store'
import { hush, setVoiceOn, voiceOn } from './voice'

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

// La oficina de ADAN al lado de la conversación: el equipo reacciona a lo que hablas y los gráficos salen en pantalla
// Subtítulos de quien habla, como en una película
function Subtitle() {
  const sub = useUniverso((s) => s.subtitle)
  if (!sub) return null
  return (
    <div className="pointer-events-none absolute inset-x-0 bottom-14 z-10 flex justify-center px-3" aria-live="polite">
      <p className="max-w-[min(94%,46rem)] whitespace-normal break-words rounded-xl bg-black/80 px-4 py-2 text-center text-[13px] leading-snug text-white shadow-lg sm:text-[15px]">
        <b style={{ color: sub.color }}>{sub.who}:</b> {sub.text}
      </p>
    </div>
  )
}

// Cada Nivel es un piso del edificio: se puede visitar otro piso, y al cambiar se ve el ascensor
export default function EmbeddedWorld({ level = 1, companyId }: { level?: number; companyId?: string }) {
  const [voice, setVoice] = useState(voiceOn)
  const [visit, setVisit] = useState<{ level: number; floor: number } | null>(null)
  const [identity, setIdentity] = useState<Identity | null>(null)
  const floor = visit && visit.level === level ? visit.floor : level
  const closeUp = useUniverso((s) => Boolean(s.stage) || Boolean(s.selected))
  const info = FLOORS[floor] ?? FLOORS[1]!

  useEffect(() => {
    if (!companyId) return
    let cancelled = false
    const load = () => api.getIdentity(companyId).then((i) => { if (!cancelled) setIdentity(i) }).catch(() => undefined)
    void load()
    // La marca se construye en otras pantallas: al volver a la pestaña el letrero se actualiza
    const onFocus = () => { void load() }
    window.addEventListener('focus', onFocus)
    // Cuando se adopta un logo o cambia la marca en la Sala, el letrero se actualiza al instante
    window.addEventListener('adan-identidad', onFocus)
    // Las bromas del equipo sobre este proyecto (para los clics en los personajes)
    api.getJokes(companyId).then((j) => { if (!cancelled) useUniverso.getState().setJokes(j.chistes) }).catch(() => undefined)
    return () => {
      cancelled = true
      window.removeEventListener('focus', onFocus)
      window.removeEventListener('adan-identidad', onFocus)
    }
  }, [companyId])

  // El piso que se ve decide qué zonas trabajan y el vestuario del equipo
  useEffect(() => {
    useUniverso.getState().setFloor(floor)
    return () => useUniverso.getState().setFloor(null)
  }, [floor])

  return (
    <div className={`universo relative h-full w-full overflow-hidden rounded-2xl ${closeUp ? 'u-closeup' : ''}`}>
      <Boundary><World embedded floor={floor} identity={identity} /></Boundary>
      <Subtitle />
      {/* La marca que el fundador va construyendo, como letrero de neón de la oficina */}
      <div className="u-brand-sign u-brand-compact pointer-events-none absolute left-3 top-11"
        style={{ ['--brand' as string]: identity?.color || info.color, ['--brand-accent' as string]: identity?.acento || '#ffffff' }}>
        {identity?.logo
          ? <img src={identity.logo} alt="" className="u-brand-logo" />
          : <span className="u-brand-initial">{(identity?.nombre || 'T').slice(0, 1).toUpperCase()}</span>}
        <span className="u-brand-text">
          <b>{identity?.nombre || 'Tu empresa'}</b>
          <i>{identity?.slogan || 'Elige tu marca en 🏷️ Marca'}</i>
        </span>
      </div>
      <div key={floor} className="u-elevator" aria-hidden="true">
        <div className="u-elevator-doors"><i /><i /></div>
        <div className="u-elevator-card relative"><b>PISO {floor}</b><span>{info.name}</span></div>
      </div>
      <div className="absolute left-3 top-3 flex items-center gap-2">
        <span className="pointer-events-none rounded-full bg-black/50 px-3 py-1 text-[11px] font-semibold tracking-wider" style={{ color: info.color }}>
          PISO {floor} · {info.name.toUpperCase()}
        </span>
        <label className="sr-only" htmlFor="u-floor">Visitar otro piso</label>
        <select id="u-floor" value={floor} onChange={(e) => setVisit({ level, floor: Number(e.target.value) })}
          title="Visitar otro piso del edificio" className="w-24 rounded-full bg-black/60 px-2 py-1 text-[11px] text-slate-200">
          {Object.entries(FLOORS).map(([n, f]) => <option key={n} value={n}>🛗 Piso {n}{Number(n) === level ? ' (tu Nivel)' : ''} · {f.name}</option>)}
        </select>
      </div>
 <div className="absolute bottom-3 right-3 flex gap-1" aria-label="Controles de la cámara">
        <button type="button" onClick={() => { if (voice) hush(); setVoiceOn(!voice); setVoice(!voice) }} aria-pressed={voice}
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
      <p className="pointer-events-none absolute bottom-3 left-3 hidden rounded-full bg-black/50 px-3 py-1 text-[11px] text-slate-300 sm:block">
        Clic en alguien: te habla · clic derecho: lo regañas
      </p>
    </div>
  )
}
