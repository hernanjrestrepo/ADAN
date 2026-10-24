import { useEffect, useState } from 'react'
import { useParams } from 'react-router'
import AppShell from '../../components/AppShell'
import Alert from '../../components/ui/Alert'
import Button from '../../components/ui/Button'
import Card from '../../components/ui/Card'
import { LoadingState } from '../../components/ui/States'
import Tabs from '../../components/ui/Tabs'
import { api, errorMessage } from '../../lib/api'
import type { Company, ExecutiveReport, FinancialModel, OrgChart, OrgRole } from '../../types'

type Tab = 'org' | 'cash' | 'report'
const TABS: { id: Tab; label: string }[] = [
  { id: 'org', label: 'Organigrama' }, { id: 'cash', label: 'Flujo de caja' }, { id: 'report', label: 'Informe ejecutivo' },
]

const money = (n: number | null | undefined, cur = '') =>
  n === null || n === undefined ? '—' : `${cur ? cur + ' ' : ''}${Math.round(n).toLocaleString('es-CO')}`

const ROLE: Record<OrgRole['tipo'], { label: string; className: string }> = {
  humano: { label: 'Persona', className: 'border-sky-400/50 bg-sky-400/10' },
  agente_adan: { label: 'Agente ADÁN', className: 'border-violet-400/50 bg-violet-400/10' },
  servicio_paradixe: { label: 'Servicio Paradixe', className: 'border-orange-400/50 bg-orange-400/10' },
}

function OrgSection({ companyId, org, setOrg, onError }: { companyId: string; org: OrgChart | null; setOrg: (o: OrgChart) => void; onError: (m: string) => void }) {
  const [busy, setBusy] = useState(false)
  const build = async () => {
    setBusy(true)
    try { setOrg(await api.buildOrg(companyId)) } catch (err) { onError(errorMessage(err)) } finally { setBusy(false) }
  }
  const areas = org ? [...new Set(org.roles.map((r) => r.area))] : []
  return (
    <div className="space-y-5">
      <Card>
        <h2 className="text-xl font-bold">Organigrama híbrido</h2>
        <p className="text-sm text-adan-muted mt-1">
          Quién compone tu empresa en sus primeros 24 meses: personas donde hace falta criterio, firma o trabajo físico; agentes de ADÁN y
          servicios de Paradixe (EVA, Omnicanal, BPO…) donde hacen el trabajo mejor y más barato. Su costo entra solo al flujo de caja.
        </p>
        <Button className="mt-4" onClick={build} loading={busy}>{org ? 'Rediseñar el organigrama' : 'Diseñar mi organigrama'}</Button>
      </Card>
      {busy && <LoadingState label="El CFO está diseñando tu organización… (1 minuto)" />}
      {org && !busy && (
        <>
          <div className="grid gap-3 sm:grid-cols-3" data-testid="org-summary">
            <Card className="p-4!"><p className="text-xs text-adan-muted">Costo mensual (con todos los roles activos)</p><p className="text-2xl font-bold">{money(org.costo_mensual_total, org.moneda)}</p></Card>
            <Card className="p-4!"><p className="text-xs text-adan-muted">Si todo fuera con personas</p><p className="text-2xl font-bold">{money(org.costo_todo_humano, org.moneda)}</p></Card>
            <Card className="p-4! border-adan-success/40!"><p className="text-xs text-adan-muted">Ahorro mensual</p><p className="text-2xl font-bold text-adan-success">{money(org.ahorro_mensual)} <span className="text-sm">({org.ahorro_pct} %)</span></p></Card>
          </div>
          <p className="text-sm">{org.resumen}</p>
          <div className="flex flex-wrap gap-3 text-xs">
            {Object.entries(ROLE).map(([k, v]) => <span key={k} className={`rounded-full border px-3 py-1 ${v.className}`}>{v.label}</span>)}
          </div>
          <div className="grid gap-4 lg:grid-cols-3 md:grid-cols-2">
            {areas.map((area) => (
              <div key={area}>
                <p className="text-xs font-semibold uppercase tracking-widest text-adan-muted">{area}</p>
                <div className="mt-2 space-y-2">
                  {org.roles.filter((r) => r.area === area).map((r) => (
                    <div key={r.cargo} className={`rounded-xl border p-3 ${ROLE[r.tipo].className}`} data-testid="org-role">
                      <div className="flex items-start justify-between gap-2">
                        <p className="font-semibold text-sm">{r.cargo}</p>
                        <span className="text-[10px] whitespace-nowrap">{r.servicio || ROLE[r.tipo].label}</span>
                      </div>
                      <p className="text-xs text-adan-muted mt-1">{r.responsabilidades.join(' · ')}</p>
                      <p className="text-xs mt-2">{money(r.costo_mensual)}/mes desde el mes {r.desde_mes}
                        {r.tipo !== 'humano' && r.costo_humano_equivalente > r.costo_mensual && <span className="text-adan-success"> · con una persona: {money(r.costo_humano_equivalente)}</span>}</p>
                      <p className="text-[11px] text-adan-muted mt-1">{r.por_que}</p>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
          <p className="text-xs text-adan-muted">Los costos de agentes y servicios son estimados de mercado: Paradixe los cotiza para tu empresa.</p>
        </>
      )}
    </div>
  )
}

function CashChart({ model }: { model: FinancialModel }) {
  const rows = model.base.rows
  const W = 720, H = 220, P = 30
  const values = rows.flatMap((r) => [r.caja, r.ingresos, -(r.gastos_fijos + r.marketing + r.costo_variable)])
  const max = Math.max(...values, 1), min = Math.min(...values, 0)
  const y = (v: number) => P + ((max - v) / (max - min || 1)) * (H - 2 * P)
  const x = (i: number) => P + (i / (rows.length - 1)) * (W - 2 * P)
  const line = rows.map((r, i) => `${i ? 'L' : 'M'}${x(i).toFixed(1)},${y(r.caja).toFixed(1)}`).join(' ')
  const bw = (W - 2 * P) / rows.length * 0.35
  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full h-auto" role="img" aria-label="Caja, ingresos y gastos mes a mes">
      <line x1={P} x2={W - P} y1={y(0)} y2={y(0)} stroke="currentColor" strokeOpacity={0.3} />
      {rows.map((r, i) => (
        <g key={r.mes}>
          <rect x={x(i) - bw} y={y(r.ingresos)} width={bw} height={Math.max(0, y(0) - y(r.ingresos))} fill="#10b981" fillOpacity={0.7} />
          <rect x={x(i)} y={y(0)} width={bw} height={Math.max(0, y(-(r.gastos_fijos + r.marketing + r.costo_variable)) - y(0))} fill="#ef4444" fillOpacity={0.5} />
        </g>
      ))}
      <path d={line} fill="none" stroke="#3e6bff" strokeWidth={2.5} />
      {[1, 6, 12, 18, 24].map((m) => <text key={m} x={x(m - 1)} y={H - 6} fontSize={10} textAnchor="middle" fill="currentColor" opacity={0.6}>mes {m}</text>)}
    </svg>
  )
}

const NUMBER_FIELDS: [keyof FinancialModel['assumptions'], string][] = [
  ['precio_unitario', 'Precio por unidad'], ['mes_inicio_ventas', 'Mes de la primera venta'], ['unidades_mes_1', 'Unidades en ese primer mes'], ['crecimiento_mensual_pct', 'Crecimiento mensual (%)'],
  ['unidades_max_mes', 'Capacidad máxima (unidades/mes)'], ['costo_variable_pct', 'Costo variable (% del precio)'],
  ['comision_pagos_pct', 'Comisión de pagos (%)'], ['marketing_mensual', 'Marketing mensual'], ['impuesto_renta_pct', 'Impuesto de renta (%)'],
  ['capital_inicial', 'Capital inicial'],
]

function CashSection({ companyId, model, setModel, hasOrg, onError }: { companyId: string; model: FinancialModel | null; setModel: (m: FinancialModel) => void; hasOrg: boolean; onError: (m: string) => void }) {
  const [busy, setBusy] = useState(false)
  const [draft, setDraft] = useState<FinancialModel['assumptions'] | null>(model?.assumptions ?? null)
  const build = async () => {
    setBusy(true)
    try { const m = await api.buildFinancialModel(companyId); setModel(m); setDraft(m.assumptions) } catch (err) { onError(errorMessage(err)) } finally { setBusy(false) }
  }
  const recompute = async () => {
    if (!draft) return
    try { const m = await api.recomputeFinancialModel(companyId, draft); setModel(m); setDraft(m.assumptions) } catch (err) { onError(errorMessage(err)) }
  }
  const cur = model?.assumptions.moneda ?? ''
  const k = model?.base.kpis
  return (
    <div className="space-y-5">
      <Card>
        <h2 className="text-xl font-bold">Estructura de costos y flujo de caja</h2>
        <p className="text-sm text-adan-muted mt-1">
          El CFO de ADÁN propone los supuestos contrastados con datos del sector; las cuentas las hace el sistema, mes a mes, a 24 meses.
          Cambia cualquier supuesto y se recalcula al instante. {!hasOrg && 'Consejo: diseña primero el organigrama para que su costo entre al flujo.'}
        </p>
        <Button className="mt-4" onClick={build} loading={busy}>{model ? 'Rehacer los supuestos con ADÁN' : 'Armar mi flujo de caja'}</Button>
      </Card>
      {busy && <LoadingState label="Buscando benchmarks del sector y armando los supuestos… (1 a 2 minutos)" />}
      {model && k && !busy && (
        <>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4" data-testid="cash-kpis">
            <Card className="p-4!"><p className="text-xs text-adan-muted">Punto de equilibrio</p><p className="text-2xl font-bold">{k.punto_equilibrio_mes ? `Mes ${k.punto_equilibrio_mes}` : 'No en 24 meses'}</p></Card>
            <Card className={`p-4! ${k.se_queda_sin_caja ? 'border-adan-danger/50!' : ''}`}><p className="text-xs text-adan-muted">Caja mínima (mes {k.caja_minima_mes})</p><p className={`text-2xl font-bold ${k.caja_minima < 0 ? 'text-red-300' : ''}`}>{money(k.caja_minima, cur)}</p></Card>
            <Card className="p-4!"><p className="text-xs text-adan-muted">Capital que necesitas</p><p className="text-2xl font-bold">{money(k.capital_necesario, cur)}</p></Card>
            <Card className="p-4!"><p className="text-xs text-adan-muted">Margen de contribución</p><p className="text-2xl font-bold">{k.margen_contribucion_pct} %</p></Card>
          </div>
          {k.se_queda_sin_caja && <Alert message={`Con estos supuestos la caja se acaba en el mes ${k.mes_sin_caja ?? k.caja_minima_mes} y toca fondo en el mes ${k.caja_minima_mes}. Necesitas ${money(k.capital_necesario, cur)} de capital o cambiar el plan.`} />}
          <Card>
            <div className="flex flex-wrap items-center justify-between gap-2">
              <h3 className="font-bold">Mes a mes (escenario base)</h3>
              <div className="flex gap-3 text-xs"><span className="text-emerald-400">■ Ingresos</span><span className="text-red-400">■ Gastos</span><span className="text-[#3e6bff]">— Caja</span></div>
            </div>
            <CashChart model={model} />
            <div className="mt-3 overflow-x-auto">
              <table className="w-full text-right text-xs">
                <thead><tr className="text-adan-muted">{['Mes', 'Ingresos', 'Costo var.', 'Gastos fijos', 'Marketing', 'EBITDA', 'Caja'].map((h) => <th key={h} className="px-2 py-1 font-semibold">{h}</th>)}</tr></thead>
                <tbody>{model.base.rows.map((r) => (
                  <tr key={r.mes} className="border-t border-adan-border/50">
                    <td className="px-2 py-1">{r.mes}</td><td className="px-2">{money(r.ingresos)}</td><td className="px-2">{money(r.costo_variable)}</td>
                    <td className="px-2">{money(r.gastos_fijos)}</td><td className="px-2">{money(r.marketing)}</td>
                    <td className={`px-2 ${r.ebitda < 0 ? 'text-red-300' : 'text-adan-success'}`}>{money(r.ebitda)}</td>
                    <td className={`px-2 font-semibold ${r.caja < 0 ? 'text-red-300' : ''}`}>{money(r.caja)}</td>
                  </tr>))}</tbody>
              </table>
            </div>
          </Card>
          <Card>
            <h3 className="font-bold">Escenarios</h3>
            <div className="mt-2 overflow-x-auto">
              <table className="w-full text-sm">
                <thead><tr className="text-adan-muted text-xs"><th className="text-left py-1">Indicador</th>{Object.keys(model.scenarios).map((s) => <th key={s} className="text-right capitalize">{s}</th>)}</tr></thead>
                <tbody>
                  {([['punto_equilibrio_mes', 'Punto de equilibrio (mes)'], ['ingresos_ano_1', 'Ingresos año 1'], ['ingresos_ano_2', 'Ingresos año 2'],
                    ['caja_minima', 'Caja mínima'], ['capital_necesario', 'Capital necesario']] as const).map(([key, label]) => (
                    <tr key={key} className="border-t border-adan-border/50"><td className="py-1">{label}</td>
                      {Object.values(model.scenarios).map((s, i) => <td key={i} className="text-right">{key === 'punto_equilibrio_mes' ? (s[key] ?? '—') : money(s[key] as number)}</td>)}</tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
          {model.advertencias.length > 0 && (
            <Card className="border-yellow-500/40!"><h3 className="font-bold">⚠️ Lo que hay que validar primero</h3>
              <ul className="mt-2 list-disc pl-5 text-sm space-y-1">{model.advertencias.map((a) => <li key={a}>{a}</li>)}</ul></Card>
          )}
          {draft && (
            <Card>
              <div className="flex flex-wrap items-center justify-between gap-2">
                <h3 className="font-bold">Supuestos ({cur})</h3>
                <div className="flex gap-2">
                  <Button size="sm" variant="secondary" onClick={() => api.downloadFile(`/finanzas/${companyId}/modelo.xlsx`, 'flujo-de-caja.xlsx').catch((err: unknown) => onError(errorMessage(err)))}>⬇ Excel</Button>
                  <Button size="sm" onClick={recompute}>Recalcular</Button>
                </div>
              </div>
              <div className="mt-3 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
                {NUMBER_FIELDS.map(([key, label]) => (
                  <label key={key} className="text-sm">
                    <span className="text-adan-muted">{label}</span>
                    <input type="number" value={draft[key] as number} onChange={(e) => setDraft({ ...draft, [key]: Number(e.target.value) })}
                      className="mt-1 w-full rounded-xl border border-adan-border bg-adan-bg px-3 py-2" />
                    {draft.bases[key] && <span className="block text-[11px] text-adan-muted mt-1">{draft.bases[key]}</span>}
                  </label>
                ))}
              </div>
              <h4 className="mt-5 text-sm font-semibold">Gastos fijos mensuales</h4>
              <div className="mt-2 space-y-2">
                {draft.gastos_fijos.map((g, i) => (
                  <div key={i} className="grid gap-2 sm:grid-cols-[2fr_1fr_100px] items-center text-sm">
                    <span>{g.concepto} <span className="text-[11px] text-adan-muted">{g.base}</span></span>
                    <input type="number" aria-label={`Monto de ${g.concepto}`} value={g.monto_mensual} className="rounded-xl border border-adan-border bg-adan-bg px-3 py-1.5"
                      onChange={(e) => setDraft({ ...draft, gastos_fijos: draft.gastos_fijos.map((x, j) => (j === i ? { ...x, monto_mensual: Number(e.target.value) } : x)) })} />
                    <input type="number" aria-label={`Mes de inicio de ${g.concepto}`} min={1} max={24} value={g.desde_mes} className="rounded-xl border border-adan-border bg-adan-bg px-3 py-1.5"
                      onChange={(e) => setDraft({ ...draft, gastos_fijos: draft.gastos_fijos.map((x, j) => (j === i ? { ...x, desde_mes: Number(e.target.value) } : x)) })} />
                  </div>
                ))}
              </div>
            </Card>
          )}
        </>
      )}
    </div>
  )
}

function ReportSection({ companyId, report, setReport, onError }: { companyId: string; report: ExecutiveReport | null; setReport: (r: ExecutiveReport) => void; onError: (m: string) => void }) {
  const [busy, setBusy] = useState(false)
  const build = async () => {
    setBusy(true)
    try { setReport(await api.buildReport(companyId)) } catch (err) { onError(errorMessage(err)) } finally { setBusy(false) }
  }
  const lc = report?.lean_canvas
  return (
    <div className="space-y-5">
      <Card className="print:hidden">
        <h2 className="text-xl font-bold">Informe ejecutivo</h2>
        <p className="text-sm text-adan-muted mt-1">
          Al estilo de una consultora de primer nivel: la respuesta primero y luego los argumentos con evidencia. Incluye Lean Canvas,
          benchmark, matriz de riesgos, Six Sigma y el plan de 90 días. Usa todo lo que ADÁN sabe: documentos, Board, La Arena, finanzas y ruta legal.
        </p>
        <div className="mt-4 flex flex-wrap gap-2">
          <Button onClick={build} loading={busy}>{report ? 'Actualizar el informe' : 'Escribir el informe'}</Button>
          {report && <Button variant="secondary" onClick={() => api.downloadFile(`/finanzas/${companyId}/informe.docx`, 'informe-ejecutivo.docx').catch((err: unknown) => onError(errorMessage(err)))}>⬇ Word</Button>}
          {report && <Button variant="secondary" onClick={() => window.print()}>🖨 Imprimir / PDF</Button>}
        </div>
      </Card>
      {busy && <LoadingState label="Escribiendo el informe… (1 a 2 minutos)" />}
      {report && lc && !busy && (
        <article className="space-y-5" data-testid="executive-report">
          <Card className="border-adan-accent/40!">
            <p className="text-xs font-semibold tracking-[0.25em] text-adan-accent">LA RESPUESTA</p>
            <h2 className="text-2xl font-bold mt-1">{report.titulo}</h2>
            <p className="mt-3 text-lg">{report.respuesta}</p>
          </Card>
          <Card>
            <div className="grid gap-3 md:grid-cols-4 text-sm">
              {(['situacion', 'complicacion', 'pregunta', 'respuesta'] as const).map((key) => (
                <div key={key}><p className="text-xs font-semibold uppercase text-adan-muted">{key === 'situacion' ? 'Situación' : key === 'complicacion' ? 'Complicación' : key === 'pregunta' ? 'Pregunta' : 'Respuesta'}</p><p className="mt-1">{report.scqa[key]}</p></div>
              ))}
            </div>
          </Card>
          <div className="grid gap-4 md:grid-cols-3">
            {report.argumentos.map((a, i) => (
              <Card key={a.titulo}><p className="text-adan-accent font-bold">{i + 1}</p><p className="font-semibold">{a.titulo}</p>
                <ul className="mt-2 list-disc pl-5 text-sm space-y-1">{a.evidencia.map((e) => <li key={e}>{e}</li>)}</ul></Card>
            ))}
          </div>
          <Card>
            <h3 className="font-bold">Lean Canvas</h3>
            <div className="mt-3 grid gap-2 text-sm md:grid-cols-5">
              {([['problema', 'Problema'], ['solucion', 'Solución'], ['propuesta_unica', 'Propuesta única'], ['ventaja_injusta', 'Ventaja injusta'], ['segmentos', 'Segmentos'],
                ['metricas_clave', 'Métricas clave'], ['canales', 'Canales'], ['costos', 'Estructura de costos'], ['ingresos', 'Fuentes de ingreso']] as const).map(([key, label]) => (
                <div key={key} className={`rounded-xl border border-adan-border p-3 ${key === 'costos' || key === 'ingresos' ? 'md:col-span-2' : ''} ${key === 'propuesta_unica' ? 'bg-adan-accent/5' : ''}`}>
                  <p className="text-xs font-semibold uppercase text-adan-muted">{label}</p><p className="mt-1">{lc[key]}</p>
                </div>
              ))}
            </div>
          </Card>
          <Card>
            <h3 className="font-bold">Benchmark</h3>
            <div className="mt-2 overflow-x-auto"><table className="w-full text-sm">
              <thead><tr className="text-left text-xs text-adan-muted"><th className="py-1">Competidor</th><th>Fortalezas</th><th>Debilidades</th><th>Cómo ganarle</th></tr></thead>
              <tbody>{report.benchmark.map((b) => <tr key={b.competidor} className="border-t border-adan-border/50 align-top"><td className="py-2 font-semibold pr-2">{b.competidor}</td><td className="pr-2">{b.fortalezas}</td><td className="pr-2">{b.debilidades}</td><td>{b.como_ganarle}</td></tr>)}</tbody>
            </table></div>
          </Card>
          <Card>
            <h3 className="font-bold">Matriz de riesgos</h3>
            <div className="mt-2 space-y-2 text-sm">{report.riesgos.map((r) => (
              <div key={r.riesgo} className="flex gap-3 rounded-xl border border-adan-border p-3">
                <span className={`h-fit rounded-full px-2 py-0.5 text-[11px] whitespace-nowrap ${r.probabilidad === 'alta' && r.impacto === 'alto' ? 'bg-adan-danger/20 text-red-300' : 'bg-yellow-500/15 text-yellow-300'}`}>{r.probabilidad} / {r.impacto}</span>
                <div><p className="font-semibold">{r.riesgo}</p><p className="text-adan-muted">{r.mitigacion}</p></div>
              </div>))}</div>
          </Card>
          <Card>
            <h3 className="font-bold">Six Sigma: mejora continua (DMAIC)</h3>
            <p className="text-sm mt-2"><b>Crítico para la calidad:</b> {report.six_sigma.ctq.join(' · ')}</p>
            <div className="mt-3 grid gap-2 md:grid-cols-5 text-sm">
              {(['definir', 'medir', 'analizar', 'mejorar', 'controlar'] as const).map((s) => <div key={s} className="rounded-xl bg-adan-bg p-3"><p className="text-xs font-semibold uppercase text-adan-accent">{s}</p><p className="mt-1">{report.six_sigma[s]}</p></div>)}
            </div>
          </Card>
          <Card>
            <h3 className="font-bold">Plan de 90 días</h3>
            <ol className="mt-2 space-y-2 text-sm">{report.plan_90_dias.map((p, i) => (
              <li key={i} className="grid gap-1 md:grid-cols-[90px_1fr_160px_1fr] rounded-xl border border-adan-border p-3"><span className="font-semibold">Sem. {p.semanas}</span><span>{p.accion}</span><span className="text-adan-muted">{p.responsable}</span><span className="text-adan-muted">→ {p.entregable}</span></li>))}</ol>
          </Card>
          <Card className="border-adan-success/40!"><p className="text-xs font-semibold tracking-[0.25em] text-adan-success">RECOMENDACIÓN</p><p className="mt-2">{report.recomendacion}</p></Card>
          <p className="text-xs text-adan-muted">ADÁN es una inteligencia artificial: este informe orienta y no reemplaza la asesoría profesional.</p>
        </article>
      )}
    </div>
  )
}

// Finanzas y estrategia: organigrama híbrido, flujo de caja e informe ejecutivo
export default function FinanzasPage() {
  const { companyId = '' } = useParams()
  const [tab, setTab] = useState<Tab>('org')
  const [company, setCompany] = useState<Company | null>(null)
  const [org, setOrg] = useState<OrgChart | null>(null)
  const [model, setModel] = useState<FinancialModel | null>(null)
  const [report, setReport] = useState<ExecutiveReport | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    const quiet = <T,>(p: Promise<T>, set: (v: T) => void) => p.then((v) => { if (!cancelled) set(v) }).catch(() => undefined)
    Promise.all([quiet(api.getCompany(companyId), setCompany), quiet(api.getOrg(companyId), setOrg),
      quiet(api.getFinancialModel(companyId), setModel), quiet(api.getReport(companyId), setReport)])
      .finally(() => { if (!cancelled) setLoading(false) })
    return () => { cancelled = true }
  }, [companyId])

  return (
    <AppShell crumbs={[{ label: 'Mis Empresas', to: '/dashboard' }, { label: company?.name ?? 'Empresa', to: `/ruta/${companyId}` }, { label: 'Finanzas y estrategia' }]}
      toolbar={<Tabs tabs={TABS} active={tab} onChange={setTab} />}>
      <div className="max-w-6xl mx-auto p-4 sm:p-6 overflow-y-auto h-full">
        {error && <div className="mb-4"><Alert message={error} onClose={() => setError(null)} /></div>}
        {loading ? <LoadingState label="Cargando..." /> : (
          <>
            {tab === 'org' && <OrgSection companyId={companyId} org={org} setOrg={setOrg} onError={setError} />}
            {tab === 'cash' && <CashSection key={model?.generated_at ?? 'sin-modelo'} companyId={companyId} model={model} setModel={setModel} hasOrg={Boolean(org)} onError={setError} />}
            {tab === 'report' && <ReportSection companyId={companyId} report={report} setReport={setReport} onError={setError} />}
          </>
        )}
      </div>
    </AppShell>
  )
}
