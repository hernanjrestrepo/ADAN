import { useEffect } from 'react'
import { AGENT_BY_ID } from '../data'
import { levelOf, useUniverso } from '../store'
import Avatar from './Avatar'

const PACE = { gathering: 3800, opening: 4300, voting: 1900, closing: 1100 } as const

// La sesión del Board Room (AD-FUNC-02): el CEO abre, seis especialistas votan y el cliente decide
export default function BoardOverlay() {
  const board = useUniverso((s) => s.board)
  const advance = useUniverso((s) => s.advanceBoard)
  const approve = useUniverso((s) => s.approveLevel)
  const dismiss = useUniverso((s) => s.dismissBoard)
  const log = useUniverso((s) => s.log)
  const arenaPassed = useUniverso((s) => s.arenaPassed)

  useEffect(() => {
    if (!board || board.phase === 'decided') return
    const t = window.setTimeout(advance, PACE[board.phase])
    return () => window.clearTimeout(t)
  }, [board, advance])

  if (!board) return null
  const level = levelOf(board.level)
  const shown = board.phase === 'voting' || board.phase === 'closing' || board.phase === 'decided' ? board.votes.slice(0, board.step) : []
  const yes = shown.filter((v) => v.vote === 'PROCEED').length

  return (
    <section aria-label="Sesión del Board Room" aria-live="polite"
      className="u-no-print u-glass u-rise fixed z-30 bottom-3 left-2 right-2 md:left-[410px] md:right-3 lg:left-1/2 lg:right-auto lg:-translate-x-1/2 lg:w-[760px] rounded-3xl p-5">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div>
          <p className="text-[11px] font-semibold tracking-[0.3em] text-sky-300">BOARD ROOM · NIVEL {level.number}</p>
          <h2 className="text-lg font-bold">{level.name}: {level.tagline}</h2>
        </div>
        <span className="rounded-full bg-white/5 px-3 py-1 text-xs">
          {board.phase === 'gathering' ? 'El equipo llega a la sala…' : board.phase === 'opening' ? 'ADÁN abre la sesión' : `${yes} a favor · ${shown.length - yes} pivotar`}
        </span>
      </div>

      <div className="mt-4 grid grid-cols-3 sm:grid-cols-6 gap-2">
        {board.votes.map((v, i) => {
          const a = AGENT_BY_ID[v.agent]
          const visible = i < shown.length
          return (
            <div key={v.agent} className={`rounded-2xl border p-2 text-center transition-all duration-500 ${visible ? (v.vote === 'PROCEED' ? 'border-emerald-400/40 bg-emerald-400/10' : 'border-orange-400/40 bg-orange-400/10') : 'border-white/10 opacity-50'}`}>
              <div className="flex justify-center"><Avatar id={v.agent} size={30} ring={visible} /></div>
              <p className="mt-1 text-[11px] font-semibold">{a.role}</p>
              <p className={`text-[10px] font-bold ${visible ? (v.vote === 'PROCEED' ? 'text-emerald-300' : 'text-orange-300') : 'text-slate-500'}`}>
                {visible ? (v.vote === 'PROCEED' ? 'A FAVOR' : 'PIVOTAR') : '…'}
              </p>
            </div>
          )
        })}
      </div>

      {board.phase === 'decided' && (
        <div className="mt-4 u-rise">
          <div className={`flex gap-3 rounded-2xl p-3 ${board.revealsRisk ? 'bg-red-500/10 ring-1 ring-red-400/40' : 'bg-white/[0.04]'}`}>
            <Avatar id="ceo" size={34} />
            <p className="text-sm text-slate-200"><b>ADÁN (CEO):</b> {board.synthesis}</p>
          </div>
          <div className="mt-3 flex flex-wrap justify-end gap-2">
            <button type="button" onClick={dismiss} className="rounded-xl bg-white/10 px-4 py-2 text-sm font-semibold hover:bg-white/20">
              {board.recommendation === 'PROCEED' ? 'Todavía no' : 'Seguir trabajando'}
            </button>
            {board.recommendation === 'PROCEED' ? (
              <button type="button" onClick={approve}
                className="u-pulse rounded-xl bg-linear-to-r from-emerald-400 to-cyan-400 px-5 py-2 text-sm font-bold text-slate-950">
                {level.number === 5 && !arenaPassed ? '🥊 Ir a La Arena' : `✓ Apruebo el cierre del Nivel ${level.number}`}
              </button>
            ) : (
              <button type="button" onClick={() => { log(`Decidiste avanzar distinto a lo recomendado. Queda documentado: riesgos asumidos y responsabilidad (AD-FUNC-02 §2.5).`, '#fb923c'); approve() }}
                className="rounded-xl border border-orange-300/50 px-4 py-2 text-sm font-semibold text-orange-200 hover:bg-orange-400/10">
                Avanzar bajo mi responsabilidad
              </button>
            )}
          </div>
        </div>
      )}
    </section>
  )
}
