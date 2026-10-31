import { Link } from 'react-router'
import { AdanMark } from '../../components/Logo'
import { LEVELS, TOTAL_XP } from '../data'
import { archetypeOf, useUniverso, xpOf } from '../store'

export default function TopBar({ autopilot, onAutopilot }: { autopilot: boolean; onAutopilot: () => void }) {
  const level = useUniverso((s) => s.level)
  const closed = useUniverso((s) => s.closedLevels)
  const done = useUniverso((s) => s.doneTasks)
  const company = useUniverso((s) => s.companyName)
  const a = archetypeOf(useUniverso((s) => s.archetypeId))
  const goToLevel = useUniverso((s) => s.goToLevel)
  const setPanel = useUniverso((s) => s.setPanel)
  const panel = useUniverso((s) => s.panel)
  const reset = useUniverso((s) => s.reset)
  const xp = xpOf(done, closed)
  const maxXp = TOTAL_XP + 700

  return (
    <header className="u-no-print fixed inset-x-2 top-2 z-30 flex flex-wrap items-center gap-2 sm:gap-3">
      <div className="u-glass flex items-center gap-3 rounded-2xl px-3 py-2">
        <AdanMark size={34} className="drop-shadow-[0_0_10px_rgba(124,155,255,0.5)]" />
        <div className="leading-tight">
          <p className="text-[11px] u-brand">ADAN <span className="font-semibold tracking-[0.2em] text-slate-500" style={{ WebkitTextFillColor: 'currentColor' }}>BY PARADIXE</span></p>
          <p className="text-sm font-bold max-w-[11rem] truncate">{a.icon} {company}</p>
        </div>
      </div>

      <nav aria-label="Los 7 Niveles" className="u-glass order-3 w-full lg:order-none lg:w-auto flex items-center gap-1 rounded-2xl px-2 py-1.5 overflow-x-auto u-scroll">
        {LEVELS.map((l) => {
          const isClosed = closed.includes(l.number)
          const unlocked = l.number === 1 || closed.includes(l.number - 1)
          const current = l.number === level
          return (
            <button key={l.number} type="button" disabled={!unlocked} onClick={() => goToLevel(l.number)}
              title={`Nivel ${l.number}: ${l.name}${unlocked ? '' : ' (bloqueado)'}`} aria-current={current ? 'step' : undefined}
              className={`group flex items-center gap-1.5 rounded-xl px-2.5 py-1.5 text-xs font-semibold transition whitespace-nowrap
                ${current ? 'bg-cyan-400/15 text-cyan-200 ring-1 ring-cyan-300/60' : isClosed ? 'text-emerald-300 hover:bg-white/5' : unlocked ? 'text-slate-200 hover:bg-white/5' : 'text-slate-600 cursor-not-allowed'}`}>
              <span className={`flex h-5 w-5 items-center justify-center rounded-full text-[10px] ${isClosed ? 'bg-emerald-400 text-slate-950' : current ? 'bg-cyan-300 text-slate-950' : 'bg-white/10'}`}>
                {isClosed ? '✓' : unlocked ? l.number : '🔒'}
              </span>
              <span className={current ? '' : 'hidden xl:inline'}>{l.name}</span>
            </button>
          )
        })}
      </nav>

      <div className="ml-auto flex items-center gap-2">
        <div className="u-glass hidden sm:block rounded-2xl px-3 py-2 min-w-[11rem]" title="El XP solo sale de evidencia entregada y Niveles cerrados (AD-FUNC-04)">
          <div className="flex justify-between text-[11px]">
            <span className="text-slate-400">Evidencia</span>
            <span className="font-bold text-cyan-200">{xp} XP</span>
          </div>
          <div className="mt-1 h-1.5 rounded-full bg-white/10 overflow-hidden">
            <div className="h-full rounded-full bg-linear-to-r from-cyan-400 via-violet-400 to-fuchsia-400 transition-all duration-700"
              style={{ width: `${Math.min(100, (xp / maxXp) * 100)}%` }} />
          </div>
        </div>
        <button type="button" onClick={onAutopilot} aria-pressed={autopilot}
          className={`u-glass rounded-2xl px-3 py-2 text-xs font-semibold ${autopilot ? 'text-fuchsia-200 ring-1 ring-fuchsia-300/60' : 'text-slate-200'}`}>
          {autopilot ? '⏸ Pausar demo' : '▶ Demo automática'}
        </button>
        {(['ruta', 'ecosistema', 'insignias'] as const).map((p) => (
          <button key={p} type="button" onClick={() => setPanel(panel === p ? 'mision' : p)} aria-pressed={panel === p}
            className={`u-glass hidden md:block rounded-2xl px-3 py-2 text-xs font-semibold capitalize ${panel === p ? 'text-cyan-200 ring-1 ring-cyan-300/50' : 'text-slate-200'}`}>
            {p === 'ruta' ? '🗺️ Ruta' : p === 'ecosistema' ? '🌐 Ecosistema' : `🏅 ${closed.length}/7`}
          </button>
        ))}
        <details className="relative">
          <summary className="u-glass list-none cursor-pointer rounded-2xl px-3 py-2 text-xs font-semibold" aria-label="Más opciones">⋯</summary>
          <div className="u-glass absolute right-0 mt-2 w-56 rounded-2xl p-2 text-sm">
            {(['ruta', 'ecosistema', 'insignias'] as const).map((p) => (
              <button key={p} type="button" onClick={() => setPanel(p)} className="md:hidden block w-full rounded-lg px-3 py-2 text-left hover:bg-white/5 capitalize">{p}</button>
            ))}
            <button type="button" onClick={reset} className="block w-full rounded-lg px-3 py-2 text-left hover:bg-white/5">Empezar otra empresa</button>
            <Link to="/dashboard" className="block rounded-lg px-3 py-2 hover:bg-white/5">Ir a mi ADAN →</Link>
          </div>
        </details>
      </div>
    </header>
  )
}
