import { AGENT_BY_ID } from '../data'
import { buildReport } from '../reports'
import { archetypeOf, levelOf, taskById, useUniverso } from '../store'

// El entregable del Nivel como documento: cada sección aparece cuando su evidencia fue entregada
export default function ReportModal() {
  const n = useUniverso((s) => s.report)
  const done = useUniverso((s) => s.doneTasks)
  const company = useUniverso((s) => s.companyName)
  const archetypeId = useUniverso((s) => s.archetypeId)
  const close = useUniverso((s) => s.openReport)
  if (n === null) return null
  const level = levelOf(n)
  const report = buildReport(n, archetypeOf(archetypeId), company)
  const ready = report.sections.filter((s) => !s.task || done.includes(s.task)).length

  return (
    <div className="fixed inset-0 z-50 flex items-start sm:items-center justify-center p-3 bg-black/60" role="dialog" aria-modal="true" aria-label={report.title}
      onClick={() => close(null)}>
      <article className="u-report u-glass u-rise relative w-full max-w-3xl max-h-[92vh] overflow-y-auto u-scroll rounded-3xl p-6 sm:p-9"
        onClick={(e) => e.stopPropagation()}>
        <div className="u-no-print absolute right-4 top-4 flex gap-2">
          <button type="button" onClick={() => window.print()} className="rounded-xl bg-white/10 px-3 py-1.5 text-xs font-semibold hover:bg-white/20">🖨️ Imprimir / PDF</button>
          <button type="button" onClick={() => close(null)} aria-label="Cerrar" className="rounded-xl bg-white/10 px-3 py-1.5 text-xs hover:bg-white/20">✕</button>
        </div>
        <p className="text-[11px] font-semibold tracking-[0.3em] text-violet-300">ADÁN · NIVEL {level.number} · {level.name.toUpperCase()}</p>
        <h2 className="mt-2 text-3xl font-bold">{report.title}</h2>
        <p className="text-slate-400">{report.subtitle}</p>
        <div className="mt-3 flex flex-wrap gap-2 text-[11px]">
          <span className="rounded-full bg-amber-400/15 px-2.5 py-1 text-amber-200">Ejemplo ilustrativo</span>
          <span className="rounded-full bg-white/5 px-2.5 py-1">{ready} de {report.sections.length} secciones con evidencia</span>
          <span className="rounded-full bg-white/5 px-2.5 py-1">{level.score}</span>
        </div>

        <div className="mt-6 space-y-5">
          {report.sections.map((s) => {
            const ok = !s.task || done.includes(s.task)
            const task = s.task ? taskById(s.task) : undefined
            return (
              <section key={s.title} className={`rounded-2xl border p-4 ${ok ? 'border-white/10' : 'border-dashed border-white/15 opacity-70'}`}>
                <h3 className="flex items-center gap-2 font-semibold">
                  <span className={ok ? 'text-emerald-300' : 'text-slate-500'}>{ok ? '✓' : '○'}</span>{s.title}
                </h3>
                {ok ? (
                  <div className="mt-2 text-sm text-slate-300 space-y-2">
                    {s.paragraphs?.map((p) => <p key={p}>{p}</p>)}
                    {s.bullets && <ul className="list-disc pl-5 space-y-1">{s.bullets.map((b) => <li key={b}>{b}</li>)}</ul>}
                    {s.table && (
                      <div className="overflow-x-auto">
                        <table className="w-full text-left text-xs">
                          <thead><tr>{s.table.head.map((h) => <th key={h} className="border-b border-white/10 px-2 py-1.5 font-semibold text-slate-400">{h}</th>)}</tr></thead>
                          <tbody>{s.table.rows.map((r) => <tr key={r.join()}>{r.map((c, i) => <td key={i} className="border-b border-white/5 px-2 py-1.5">{c}</td>)}</tr>)}</tbody>
                        </table>
                      </div>
                    )}
                  </div>
                ) : (
                  <p className="mt-2 text-sm text-slate-500">
                    Pendiente: {task ? `${task.label.toLowerCase()} (lo hace ${AGENT_BY_ID[task.agent].name}, ${AGENT_BY_ID[task.agent].role})` : 'evidencia'}.
                  </p>
                )}
              </section>
            )
          })}
        </div>
        <p className="mt-6 text-[11px] text-slate-500">
          ADÁN es una inteligencia artificial. Sus análisis no reemplazan la asesoría profesional (legal, tributaria, financiera u otra),
          y Paradixe no responde por las decisiones que se tomen con base en ellos.
        </p>
      </article>
    </div>
  )
}
