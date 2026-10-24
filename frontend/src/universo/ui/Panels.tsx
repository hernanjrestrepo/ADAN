import { AGENT_BY_ID, ECOSYSTEM, LEVELS } from '../data'
import { useUniverso } from '../store'
import Avatar from './Avatar'

function Shell({ title, kicker, children }: { title: string; kicker: string; children: React.ReactNode }) {
  const setPanel = useUniverso((s) => s.setPanel)
  return (
    <aside className="u-no-print u-glass u-rise fixed z-30 inset-x-2 bottom-2 top-[7.5rem] md:inset-x-auto md:left-3 md:top-[5.5rem] lg:top-20 md:bottom-3 md:w-[430px] rounded-3xl flex flex-col">
      <div className="flex items-start justify-between px-5 pt-5">
        <div>
          <p className="text-[11px] font-semibold tracking-[0.3em] u-kicker">{kicker}</p>
          <h2 className="text-xl font-bold">{title}</h2>
        </div>
        <button type="button" onClick={() => setPanel('mision')} className="rounded-xl bg-white/10 px-3 py-1.5 text-xs hover:bg-white/20">Volver a la misión</button>
      </div>
      <div className="mt-3 flex-1 min-h-0 overflow-y-auto u-scroll px-5 pb-5">{children}</div>
    </aside>
  )
}

// El paso a paso completo: los 7 Niveles con su entregable, su Gate y su Score
export function RoutePanel() {
  const closed = useUniverso((s) => s.closedLevels)
  const level = useUniverso((s) => s.level)
  const openReport = useUniverso((s) => s.openReport)
  return (
    <Shell kicker="EL PASO A PASO" title="La ruta de 7 Niveles">
      <p className="text-sm text-slate-400">Se avanza por evidencia, nunca por pago, y cada cierre lo apruebas tú.</p>
      <ol className="relative mt-4 border-l border-white/10 ml-3 space-y-5">
        {LEVELS.map((l) => {
          const isClosed = closed.includes(l.number)
          const current = l.number === level
          return (
            <li key={l.number} className="ml-6">
              <span className={`absolute -left-3 flex h-6 w-6 items-center justify-center rounded-full text-[11px] font-bold ${isClosed ? 'bg-emerald-400 text-slate-950' : current ? 'bg-cyan-300 text-slate-950 u-pulse' : 'bg-slate-800 text-slate-300'}`}>
                {isClosed ? '✓' : l.number}
              </span>
              <h3 className="font-semibold">{l.name} <span className="text-xs font-normal text-slate-400">· {l.ritmo}</span></h3>
              <p className="text-xs text-slate-400">{l.tagline}</p>
              <div className="mt-2 grid gap-1.5 text-xs">
                <p><span className="text-slate-500">Entregable:</span> {l.entregable}</p>
                <p><span className="text-slate-500">Para cerrar:</span> {l.avance}</p>
                <p><span className="text-slate-500">Score:</span> {l.score} · <span className="text-slate-500">Insignia:</span> {l.badge.icon} {l.badge.name}</p>
              </div>
              <div className="mt-2 flex items-center gap-1">
                {l.tasks.map((t) => <span key={t.id} title={`${AGENT_BY_ID[t.agent].name}: ${t.label}`}><Avatar id={t.agent} size={22} /></span>)}
                <button type="button" onClick={() => openReport(l.number)} className="ml-auto rounded-lg bg-white/5 px-2.5 py-1 text-[11px] hover:bg-white/10">Ver reporte</button>
              </div>
            </li>
          )
        })}
      </ol>
    </Shell>
  )
}

export function EcosystemPanel() {
  const focus = useUniverso((s) => s.focus)
  return (
    <Shell kicker="PARADIXE" title="El ecosistema de ADÁN">
      <p className="text-sm text-slate-400">ADÁN orquesta; cada componente hace lo suyo. Toca una zona de la oficina para verla trabajar.</p>
      <ul className="mt-4 grid gap-2">
        {ECOSYSTEM.map((e) => (
          <li key={e.name} className="flex gap-3 rounded-2xl bg-white/[0.03] p-3">
            <span className="text-2xl" aria-hidden="true">{e.icon}</span>
            <div><p className="font-semibold">{e.name}</p><p className="text-xs text-slate-400">{e.text}</p></div>
          </li>
        ))}
      </ul>
      <div className="mt-5 grid grid-cols-2 gap-2 text-xs">
        {([['board', 'Sala de Juntas'], ['csi', 'Radar CSI'], ['memoria', 'Memoria'], ['genexis', 'Genexis'], ['simulador', 'Simulador'], ['gemelo', 'Gemelo Digital'], ['eva', 'Estudio EVA'], ['mercado', 'Marketplace']] as const).map(([id, label]) => (
          <button key={id} type="button" onClick={() => focus(id)} className="rounded-xl border border-white/10 px-3 py-2 hover:border-cyan-300/50">📍 {label}</button>
        ))}
      </div>
      <p className="mt-5 text-[11px] text-slate-500">ADÁN nunca decide por ti, no vende desarrollo de software y no se presenta como asesoría profesional (AD-000 §6).</p>
    </Shell>
  )
}

export function BadgesPanel() {
  const closed = useUniverso((s) => s.closedLevels)
  return (
    <Shell kicker="LOGROS REALES" title="Insignias">
      <p className="text-sm text-slate-400">Cada insignia corresponde a un hito real del Gemelo Digital. Sin rachas, sin rankings entre empresarios: te comparas contigo mismo.</p>
      <ul className="mt-4 grid grid-cols-2 gap-3">
        {LEVELS.map((l) => {
          const got = closed.includes(l.number)
          return (
            <li key={l.number} className={`rounded-2xl border p-4 text-center ${got ? 'border-emerald-400/30 bg-emerald-400/5' : 'border-white/10 opacity-50'}`}>
              <p className={`text-4xl ${got ? '' : 'grayscale'}`} aria-hidden="true">{l.badge.icon}</p>
              <p className="mt-2 text-sm font-semibold">{l.badge.name}</p>
              <p className="text-[11px] text-slate-400">{got ? l.badge.meaning : `Se gana al cerrar el Nivel ${l.number}`}</p>
            </li>
          )
        })}
      </ul>
    </Shell>
  )
}
