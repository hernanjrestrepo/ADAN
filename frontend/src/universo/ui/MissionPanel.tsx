import { useState } from 'react'
import { AGENT_BY_ID } from '../data'
import { levelOf, tasksOf, useUniverso } from '../store'
import Avatar from './Avatar'

// La misión del Nivel: qué descubre ADAN, qué aprendes, qué cambia en el Gemelo, y las tareas del Gate
export default function MissionPanel() {
  const levelNumber = useUniverso((s) => s.level)
  const done = useUniverso((s) => s.doneTasks)
  const jobs = useUniverso((s) => s.jobs)
  const board = useUniverso((s) => s.board)
  const arena = useUniverso((s) => s.arena)
  const revealed = useUniverso((s) => s.revealed)
  const arenaPassed = useUniverso((s) => s.arenaPassed)
  const enterArena = useUniverso((s) => s.enterArena)
  const closed = useUniverso((s) => s.closedLevels.includes(levelNumber))
  const assign = useUniverso((s) => s.assign)
  const convene = useUniverso((s) => s.convene)
  const openReport = useUniverso((s) => s.openReport)
  const focus = useUniverso((s) => s.focus)
  const select = useUniverso((s) => s.select)
  const [open, setOpen] = useState(true)
  const level = levelOf(levelNumber)
  const tasks = tasksOf(level, revealed)
  const doneCount = tasks.filter((t) => done.includes(t.id)).length
  const riskOpen = revealed.includes(level.number) && !done.includes(level.riesgo.task.id)
  const busy = Object.keys(jobs).length > 0
  // En el celular el panel se recoge mientras sesiona el Board, para ver la sala
  const expanded = open && !board

  return (
    <aside aria-label={`Misión del Nivel ${level.number}`}
      className={`u-no-print u-glass fixed z-20 flex flex-col rounded-3xl transition-all
        inset-x-2 bottom-2 ${expanded ? 'max-h-[46vh]' : 'max-h-14'} ${board ? 'max-md:hidden' : ''}
        md:inset-x-auto md:left-3 md:top-[5.5rem] lg:top-20 md:bottom-3 md:w-[390px] md:max-h-none`}>
      <button type="button" onClick={() => setOpen(!open)} className="md:hidden flex items-center justify-between px-5 py-3 text-sm font-semibold">
        <span>Nivel {level.number} · {level.name} <span className="text-slate-400">({doneCount}/{tasks.length})</span></span>
        <span aria-hidden="true">{expanded ? '▾' : '▴'}</span>
      </button>
      <div className={`${expanded ? 'flex' : 'hidden'} md:flex flex-col min-h-0 flex-1 overflow-y-auto u-scroll px-5 pb-5 md:pt-5`}>
        <div className="u-rise" key={level.number}>
          <p className="text-[11px] font-semibold tracking-[0.3em] u-kicker">NIVEL {level.number} DE 7</p>
          <h2 className="mt-1 text-2xl font-bold">{level.name}</h2>
          <p className="mt-1 text-slate-300">{level.tagline}</p>
          <div className="mt-3 flex flex-wrap gap-1.5 text-[11px]">
            <span className="rounded-full bg-white/5 px-2.5 py-1">Ritmo: <b>{level.ritmo}</b></span>
            <span className="rounded-full bg-white/5 px-2.5 py-1">Te debe hacer sentir: <b>{level.emocion}</b></span>
            <span className="rounded-full bg-white/5 px-2.5 py-1">{level.score}</span>
          </div>

          <dl className="mt-4 space-y-2.5 text-sm">
            {[['🔍', 'Qué descubre ADAN', level.descubre], ['💡', 'Qué aprendes', level.aprende], ['🧬', 'Qué cambia en el Gemelo', level.gemelo]].map(([icon, k, v]) => (
              <div key={k} className="rounded-xl bg-white/[0.03] p-3">
                <dt className="text-xs font-semibold text-slate-400"><span aria-hidden="true">{icon}</span> {k}</dt>
                <dd className="mt-0.5 text-slate-200">{v}</dd>
              </div>
            ))}
          </dl>

          <div className="mt-5 flex items-center justify-between">
            <h3 className="text-sm font-bold">Evidencia para el Gate</h3>
            <span className="text-xs text-slate-400">{doneCount} de {tasks.length}</span>
          </div>
          <div className="mt-2 h-1.5 rounded-full bg-white/10 overflow-hidden">
            <div className="h-full bg-linear-to-r from-emerald-400 to-cyan-400 transition-all duration-700" style={{ width: `${(doneCount / tasks.length) * 100}%` }} />
          </div>
          {riskOpen && (
            <div className="mt-3 rounded-2xl border border-red-400/40 bg-red-500/10 p-3 text-sm u-rise" role="alert">
              <p className="font-bold text-red-200">😈 Riesgo crítico descubierto por el Board</p>
              <p className="mt-1 text-red-100/90">{level.riesgo.texto}</p>
              <p className="mt-1 text-xs text-red-200/80">Blíndalo con la tarea nueva y vuelve a convocar al Board.</p>
            </div>
          )}
          <ul className="mt-3 space-y-2">
            {tasks.map((t) => {
              const a = AGENT_BY_ID[t.agent]
              const isDone = done.includes(t.id)
              const isRisk = t.id === level.riesgo.task.id
              const job = jobs[t.agent]
              const running = job?.taskId === t.id
              const agentBusy = Boolean(job) && !running
              return (
                <li key={t.id} className={`flex items-center gap-3 rounded-2xl border p-3 transition ${isDone ? 'border-emerald-400/30 bg-emerald-400/5' : running ? 'border-cyan-300/40 bg-cyan-400/5' : isRisk ? 'border-red-400/50 bg-red-500/5' : 'border-white/10'}`}>
                  <button type="button" onClick={() => select(t.agent)} title={`Ver a ${a.name}`}><Avatar id={t.agent} size={34} ring={running} /></button>
                  <div className="min-w-0 flex-1">
                    <p className={`text-sm font-medium ${isDone ? 'text-emerald-200' : ''}`}>{isRisk && '🛡️ '}{t.label}</p>
                    <p className="text-[11px] text-slate-400">
                      {isDone ? `✓ ${t.done}` : running ? `${a.name} ${job?.phase === 'working' ? 'está trabajando…' : job?.phase === 'going' ? 'va en camino…' : 'vuelve a su puesto…'}` : `${a.name} · ${a.role} · +${t.xp} XP`}
                    </p>
                  </div>
                  {!isDone && !running && (
                    <button type="button" disabled={agentBusy || Boolean(board) || Boolean(arena) || closed} onClick={() => { assign(t.id); focus(t.zone) }}
                      className="shrink-0 rounded-xl bg-white/10 px-3 py-1.5 text-xs font-semibold hover:bg-white/20 disabled:opacity-40">
                      Encargar
                    </button>
                  )}
                  {running && <span className="h-4 w-4 shrink-0 rounded-full border-2 border-cyan-300 border-t-transparent animate-spin" aria-label="En curso" />}
                </li>
              )
            })}
          </ul>

          <button type="button" onClick={() => openReport(level.number)}
            className="mt-4 flex w-full items-center gap-3 rounded-2xl border border-violet-300/30 bg-violet-400/5 p-3 text-left hover:bg-violet-400/10">
            <span className="text-2xl" aria-hidden="true">📄</span>
            <span className="flex-1">
              <span className="block text-xs text-slate-400">Entregable del Nivel</span>
              <span className="block text-sm font-semibold">{level.entregable}</span>
            </span>
            <span className="text-xs text-violet-200">Ver reporte →</span>
          </button>

          <p className="mt-4 text-xs text-slate-400"><b className="text-slate-300">Para cerrar:</b> {level.avance}</p>

          {closed ? (
            <p className="mt-4 rounded-2xl bg-emerald-400/10 p-3 text-sm text-emerald-200">✓ Nivel cerrado con tu aprobación. Insignia: {level.badge.icon} {level.badge.name}</p>
          ) : (
            <>
            {level.number === 5 && (
              <button type="button" disabled={Boolean(board) || Boolean(arena) || busy} onClick={enterArena}
                className={`mt-4 w-full rounded-2xl border px-5 py-3 font-bold disabled:opacity-50 ${arenaPassed ? 'border-emerald-400/50 text-emerald-200' : 'border-red-400/60 text-red-200 hover:bg-red-500/10'}`}>
                {arenaPassed ? '✓ La Arena superada' : '🥊 Entrar a La Arena (4 inversionistas)'}
              </button>
            )}
            <button type="button" disabled={Boolean(board) || Boolean(arena) || busy} onClick={convene}
              className="mt-4 w-full rounded-2xl u-cta px-5 py-3 font-bold disabled:opacity-50">
              🏛️ Convocar el Board Room
            </button>
            </>
          )}
          {busy && !board && !closed && <p className="mt-2 text-center text-[11px] text-slate-500">El Board se convoca cuando el equipo termine las tareas en curso.</p>}
        </div>
      </div>
    </aside>
  )
}
