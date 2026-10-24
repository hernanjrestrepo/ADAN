import { AGENT_BY_ID, ZONES } from '../data'
import { levelOf, taskById, useUniverso } from '../store'
import Avatar from './Avatar'

// Al tocar a alguien en la oficina: quién es, qué hace ahora y qué se le puede pedir
export default function AgentCard() {
  const id = useUniverso((s) => s.selected)
  const job = useUniverso((s) => (s.selected ? s.jobs[s.selected] : undefined))
  const inBoard = useUniverso((s) => Boolean(s.board))
  const levelNumber = useUniverso((s) => s.level)
  const done = useUniverso((s) => s.doneTasks)
  const select = useUniverso((s) => s.select)
  const say = useUniverso((s) => s.say)
  const assign = useUniverso((s) => s.assign)
  const focus = useUniverso((s) => s.focus)
  if (!id) return null
  const a = AGENT_BY_ID[id]
  const level = levelOf(levelNumber)
  const pending = level.tasks.find((t) => t.agent === id && !done.includes(t.id))
  const task = job ? taskById(job.taskId) : undefined
  const status = task
    ? `${job?.phase === 'working' ? 'Trabajando en' : job?.phase === 'going' ? 'Va a' : 'Terminó'}: ${task.label.toLowerCase()} · ${ZONES[task.zone].name}`
    : inBoard && a.board ? 'Sentado en el Board Room' : 'En su puesto, disponible'
  const levelLine = level.focus[id]

  return (
    <aside aria-label={`${a.name}, ${a.role}`}
      className="u-no-print u-glass u-rise fixed z-30 right-2 left-2 top-[7.5rem] sm:left-auto sm:right-3 sm:top-24 sm:w-[340px] rounded-3xl p-5">
      <button type="button" onClick={() => select(null)} aria-label="Cerrar" className="absolute right-4 top-3 text-slate-400 hover:text-white">✕</button>
      <div className="flex items-center gap-4">
        <Avatar id={id} size={56} ring />
        <div>
          <p className="text-lg font-bold">{a.name}</p>
          <p className="text-sm" style={{ color: a.color }}>{a.role} · {a.title}</p>
        </div>
      </div>
      <p className="mt-4 text-sm text-slate-300">{a.focus}</p>
      <p className="mt-3 rounded-xl bg-white/[0.04] px-3 py-2 text-xs text-slate-300">
        <span className="inline-block h-2 w-2 rounded-full mr-2 align-middle" style={{ background: task ? '#67e8f9' : '#64748b' }} />{status}
      </p>
      {levelLine && <p className="mt-3 text-sm"><span className="text-slate-400">En el Nivel {level.number}:</span> {levelLine}</p>}
      {!a.board && <p className="mt-2 text-[11px] text-slate-500">{a.role === 'Agente por hora' || a.role === 'Agente por día'
        ? 'Se contrata por tiempo en el Marketplace. Tú apruebas cada entrega.' : 'Componente del ecosistema Paradixe.'}</p>}
      <div className="mt-4 flex flex-wrap gap-2">
        <button type="button" onClick={() => say(id, levelLine ? `${a.hello} ${levelLine}` : a.hello, 7000, 'info')}
          className="rounded-xl bg-white/10 px-3 py-2 text-xs font-semibold hover:bg-white/20">💬 Hablar</button>
        {pending && !job && !inBoard && (
          <button type="button" onClick={() => { assign(pending.id); focus(pending.zone) }}
            className="rounded-xl bg-cyan-400/20 px-3 py-2 text-xs font-semibold text-cyan-100 hover:bg-cyan-400/30">
            ⚡ Encargar: {pending.label}
          </button>
        )}
      </div>
    </aside>
  )
}
