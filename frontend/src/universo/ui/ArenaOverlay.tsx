import { useEffect } from 'react'
import { INVESTORS } from '../data'
import { useUniverso } from '../store'

const PACE = { gathering: 3200, pitch: 4400, deciding: 2300 } as const

// La Arena: ADÁN presenta y cuatro inversionistas exigentes deciden uno por uno. Sin convencerlos no se cierra el Nivel 5.
export default function ArenaOverlay() {
  const arena = useUniverso((s) => s.arena)
  const advance = useUniverso((s) => s.advanceArena)
  const leave = useUniverso((s) => s.leaveArena)
  const approve = useUniverso((s) => s.approveLevel)

  useEffect(() => {
    if (!arena || arena.phase === 'decided') return
    const t = window.setTimeout(advance, PACE[arena.phase])
    return () => window.clearTimeout(t)
  }, [arena, advance])

  if (!arena) return null
  const shown = arena.phase === 'deciding' || arena.phase === 'decided' ? arena.verdicts.slice(0, arena.step) : []
  const yes = shown.filter((v) => v.invests).length

  return (
    <section aria-label="La Arena" aria-live="polite"
      className="u-no-print u-glass u-rise fixed z-30 bottom-3 left-2 right-2 md:left-[410px] md:right-3 lg:left-1/2 lg:right-auto lg:-translate-x-1/2 lg:w-[760px] rounded-3xl p-5 ring-1 ring-red-400/40">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div>
          <p className="text-[11px] font-semibold tracking-[0.3em] text-red-300">LA ARENA · NIVEL 5</p>
          <h2 className="text-lg font-bold">Convence a cuatro inversionistas</h2>
        </div>
        <span className="rounded-full bg-white/5 px-3 py-1 text-xs">
          {arena.phase === 'gathering' ? 'Los inversionistas toman asiento…' : arena.phase === 'pitch' ? 'ADÁN presenta tu empresa' : `${yes} invierten · ${shown.length - yes} no`}
        </span>
      </div>
      <div className="mt-4 grid grid-cols-2 sm:grid-cols-4 gap-2">
        {INVESTORS.map((inv, i) => {
          const v = arena.verdicts.find((x) => x.investor === inv.id)
          const visible = i < shown.length
          return (
            <div key={inv.id} className={`rounded-2xl border p-3 transition-all duration-500 ${visible ? (v?.invests ? 'border-emerald-400/40 bg-emerald-400/10' : 'border-red-400/40 bg-red-500/10') : 'border-white/10 opacity-60'}`}>
              <p className="text-sm font-bold" style={{ color: inv.color }}>{inv.name}</p>
              <p className="text-[11px] text-slate-400">{inv.role}</p>
              <p className={`mt-1 text-xs font-bold ${visible ? (v?.invests ? 'text-emerald-300' : 'text-red-300') : 'text-slate-500'}`}>
                {visible ? (v?.invests ? '💰 INVIERTE' : '❌ NO INVIERTE') : '…'}
              </p>
              {visible && v?.fatal && <p className="mt-1 text-[11px] text-red-200">Falla fatal: {v.fatal}</p>}
            </div>
          )
        })}
      </div>
      {arena.phase === 'decided' && (
        <div className="mt-4 u-rise">
          <p className={`rounded-2xl p-3 text-sm ${arena.passed ? 'bg-emerald-400/10 text-emerald-100' : 'bg-red-500/10 text-red-100'}`}>
            <b>ADÁN (CEO):</b> {arena.passed
              ? 'Pasamos La Arena: hay inversionistas dispuestos a entrar. Ya puedes cerrar el Nivel 5.'
              : 'No convencimos a nadie. Lo que señalaron es lo que haría cerrar la empresa: blíndalo y volvemos a entrar.'}
          </p>
          <div className="mt-3 flex flex-wrap justify-end gap-2">
            <button type="button" onClick={leave} className="rounded-xl bg-white/10 px-4 py-2 text-sm font-semibold hover:bg-white/20">
              {arena.passed ? 'Todavía no' : 'Volver a trabajar'}
            </button>
            {arena.passed && (
              <button type="button" onClick={approve}
                className="u-pulse rounded-xl bg-linear-to-r from-emerald-400 to-cyan-400 px-5 py-2 text-sm font-bold text-slate-950">
                ✓ Apruebo el cierre del Nivel 5
              </button>
            )}
          </div>
        </div>
      )}
    </section>
  )
}
