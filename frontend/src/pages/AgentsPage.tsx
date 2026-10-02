import { useCallback, useEffect, useState, type FormEvent } from 'react'
import { useParams } from 'react-router'
import AppShell from '../components/AppShell'
import Alert from '../components/ui/Alert'
import Badge, { type Tone } from '../components/ui/Badge'
import Button from '../components/ui/Button'
import Card from '../components/ui/Card'
import { Field, TextAreaField } from '../components/ui/Field'
import { EmptyState, LoadingState } from '../components/ui/States'
import { api, errorMessage } from '../lib/api'
import type { AgentContract, AgentOffering, AgentTask, Company, HirePeriod } from '../types'

// Agentes por tiempo (WO-109, AD-DEC-0002 decisión 1): contratar, encargar, revisar y medir
const PERIODS: { id: HirePeriod; label: string; hours: number }[] = [
  { id: 'hour', label: 'Horas', hours: 1 }, { id: 'day', label: 'Días', hours: 8 },
  { id: 'week', label: 'Semanas', hours: 40 }, { id: 'month', label: 'Meses', hours: 160 },
]
const STATE: Record<AgentContract['state'], { label: string; tone: Tone }> = {
  active: { label: 'Activo', tone: 'green' }, expired: { label: 'Vencido', tone: 'gray' },
  exhausted: { label: 'Sin horas', tone: 'yellow' }, cancelled: { label: 'Cancelado', tone: 'gray' },
}
const TASK: Record<AgentTask['status'], { label: string; tone: Tone }> = {
  assigned: { label: 'Por hacer', tone: 'gray' }, in_progress: { label: 'Trabajando', tone: 'blue' },
  review: { label: 'Para revisar', tone: 'yellow' }, completed: { label: 'Aprobada', tone: 'green' },
}

function HireCard({ offering, onHire }: { offering: AgentOffering; onHire: (p: HirePeriod, u: number) => Promise<void> }) {
  const [period, setPeriod] = useState<HirePeriod>('day')
  const [units, setUnits] = useState(1)
  const [busy, setBusy] = useState(false)
  const hours = (PERIODS.find((p) => p.id === period)?.hours ?? 1) * units
  return (
    <Card className="flex flex-col gap-3" data-testid="offering">
      <div>
        <h3 className="font-bold">{offering.name}</h3>
        <p className="text-xs text-adan-muted">{offering.role}</p>
      </div>
      <p className="text-sm text-adan-text/80">{offering.description}</p>
      <div className="flex flex-wrap gap-1">
        {offering.skills.map((s) => <Badge key={s} tone="blue">{s}</Badge>)}
        {offering.tools.map((t) => <Badge key={t} tone="gray">herramienta: {t}</Badge>)}
      </div>
      <div className="grid grid-cols-2 gap-2 mt-auto">
        <label className="text-xs text-adan-muted">Período
          <select value={period} onChange={(e) => setPeriod(e.target.value as HirePeriod)} aria-label={`Período ${offering.name}`}
            className="mt-1 w-full px-3 py-2 bg-adan-bg border border-adan-border rounded-lg text-sm text-adan-text">
            {PERIODS.map((p) => <option key={p.id} value={p.id}>{p.label}</option>)}
          </select>
        </label>
        <label className="text-xs text-adan-muted">Cantidad
          <input type="number" min={1} max={200} value={units} aria-label={`Cantidad ${offering.name}`}
            onChange={(e) => setUnits(Math.max(1, Number(e.target.value) || 1))}
            className="mt-1 w-full px-3 py-2 bg-adan-bg border border-adan-border rounded-lg text-sm text-adan-text" />
        </label>
      </div>
      <p className="text-xs text-adan-muted">{hours} h de trabajo efectivo · {offering.price_note}</p>
      <Button loading={busy} onClick={async () => { setBusy(true); try { await onHire(period, units) } finally { setBusy(false) } }}>
        Contratar
      </Button>
    </Card>
  )
}

function ContractPanel({ companyId, contract, onChanged, onError }: {
  companyId: string; contract: AgentContract; onChanged: () => void; onError: (m: string) => void
}) {
  const [tasks, setTasks] = useState<AgentTask[] | null>(null)
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [busy, setBusy] = useState<string | null>(null)
  const [feedback, setFeedback] = useState<Record<string, string>>({})

  const load = useCallback(() => api.getContractTasks(companyId, contract.id), [companyId, contract.id])
  useEffect(() => {
    let cancelled = false
    load().then((t) => { if (!cancelled) setTasks(t) }).catch((err: unknown) => onError(errorMessage(err)))
    return () => { cancelled = true }
  }, [load, onError])

  const act = async (key: string, fn: () => Promise<unknown>) => {
    setBusy(key)
    try {
      await fn()
      setTasks(await load())
      onChanged()
    } catch (err) {
      onError(errorMessage(err))
    } finally {
      setBusy(null)
    }
  }

  const assign = (e: FormEvent) => {
    e.preventDefault()
    void act('assign', async () => {
      await api.assignTask(companyId, contract.id, title.trim(), description.trim())
      setTitle('')
      setDescription('')
    })
  }

  const pct = Math.min(100, (contract.hours_used / contract.hours_capacity) * 100)
  const active = contract.state === 'active'
  return (
    <Card data-testid="contract">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h3 className="font-bold">{contract.offering.name}</h3>
          <p className="text-xs text-adan-muted">
            {contract.units} {PERIODS.find((p) => p.id === contract.period)?.label.toLowerCase()} · hasta{' '}
            {new Date(contract.ends_at).toLocaleDateString('es-CO')}
          </p>
        </div>
        <Badge tone={STATE[contract.state].tone}>{STATE[contract.state].label}</Badge>
      </div>
      <div className="mt-3">
        <div className="flex justify-between text-xs text-adan-muted mb-1">
          <span>Trabajo usado</span>
          <span>{contract.hours_used.toFixed(2)} de {contract.hours_capacity} h</span>
        </div>
        <div className="h-1.5 rounded-full bg-adan-bg overflow-hidden" role="progressbar" aria-label="Horas usadas"
          aria-valuenow={Math.round(pct)} aria-valuemin={0} aria-valuemax={100}>
          <div className="h-full bg-adan-accent" style={{ width: `${pct}%` }} />
        </div>
      </div>

      {active && (
        <form onSubmit={assign} className="mt-4 space-y-3">
          <Field label="Nueva tarea" value={title} onChange={(e) => setTitle(e.target.value)} minLength={5} required
            placeholder="Ej.: Investigar 5 competidores de viajes corporativos en Colombia" />
          <TextAreaField label="Detalles (opcional)" value={description} onChange={(e) => setDescription(e.target.value)} />
          <Button type="submit" size="sm" loading={busy === 'assign'}>Encargar</Button>
        </form>
      )}

      {tasks === null ? <LoadingState label="Cargando tareas..." /> : tasks.length > 0 && (
        <ul className="mt-4 space-y-3" aria-label={`Tareas de ${contract.offering.name}`}>
          {tasks.map((t) => (
            <li key={t.id} className="rounded-xl border border-adan-border p-3" data-testid="agent-task">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <span className="text-sm font-medium">{t.title}</span>
                <Badge tone={TASK[t.status].tone}>{TASK[t.status].label}</Badge>
              </div>
              {t.blocking_reason && t.status === 'assigned' && (
                <p className="text-xs text-adan-warning mt-1">{t.blocking_reason}</p>
              )}
              {t.result && t.status !== 'assigned' && (
                <div className="mt-2 text-sm whitespace-pre-wrap bg-adan-bg rounded-lg p-3">{t.result}</div>
              )}
              {t.status === 'assigned' && active && (
                <Button size="sm" className="mt-2" loading={busy === t.id}
                  onClick={() => act(t.id, () => api.runTask(companyId, contract.id, t.id))}>
                  Poner a trabajar
                </Button>
              )}
              {t.status === 'review' && (
                <div className="mt-2 flex flex-wrap items-end gap-2">
                  <Button size="sm" variant="success" loading={busy === `ok-${t.id}`}
                    onClick={() => act(`ok-${t.id}`, () => api.reviewTask(companyId, contract.id, t.id, true))}>
                    Aprobar
                  </Button>
                  <Field className="flex-1 min-w-48" label="Correcciones" value={feedback[t.id] ?? ''}
                    onChange={(e) => setFeedback({ ...feedback, [t.id]: e.target.value })} />
                  <Button size="sm" variant="secondary" disabled={(feedback[t.id] ?? '').trim().length < 5}
                    onClick={() => act(`fb-${t.id}`, () => api.reviewTask(companyId, contract.id, t.id, false, feedback[t.id]))}>
                    Pedir cambios
                  </Button>
                </div>
              )}
            </li>
          ))}
        </ul>
      )}
      {active && (
        <Button size="sm" variant="ghost" className="mt-3 -ml-3"
          onClick={() => act('cancel', () => api.cancelContract(companyId, contract.id))}>
          Cancelar contrato
        </Button>
      )}
    </Card>
  )
}

export default function AgentsPage() {
  const { companyId = '' } = useParams()
  const [catalog, setCatalog] = useState<AgentOffering[] | null>(null)
  const [contracts, setContracts] = useState<AgentContract[]>([])
  const [company, setCompany] = useState<Company | null>(null)
  const [error, setError] = useState<string | null>(null)
  const showError = useCallback((m: string) => setError(m), [])

  const reload = useCallback(async () => setContracts(await api.getContracts(companyId)), [companyId])
  useEffect(() => {
    let cancelled = false
    Promise.all([api.getHireCatalog(), api.getContracts(companyId)])
      .then(([cat, list]) => { if (!cancelled) { setCatalog(cat); setContracts(list) } })
      .catch((err: unknown) => { if (!cancelled) setError(errorMessage(err)) })
    api.getCompany(companyId).then((c) => { if (!cancelled) setCompany(c) }).catch(() => undefined)
    return () => { cancelled = true }
  }, [companyId])

  const hire = async (offering: AgentOffering, period: HirePeriod, units: number) => {
    setError(null)
    try {
      await api.hireAgent(companyId, offering.code, period, units)
      await reload()
    } catch (err) {
      setError(errorMessage(err))
    }
  }

  return (
    <AppShell crumbs={[{ label: 'Mis Empresas', to: '/dashboard' }, { label: company?.name ?? 'Empresa', to: `/gemelo/${companyId}` },
      { label: 'Agentes' }]}>
      <div className="max-w-6xl mx-auto p-4 sm:p-6 overflow-y-auto h-full space-y-8">
        <div>
          <h1 className="text-3xl font-bold">Agentes por tiempo</h1>
          <p className="text-adan-muted mt-1">
            Contrata agentes por horas, días, semanas o meses para tareas concretas. Cada entrega la apruebas tú, y el
            tiempo de trabajo real se descuenta de lo contratado.
          </p>
        </div>
        {error && <Alert message={error} onClose={() => setError(null)} />}
        {catalog === null ? <LoadingState label="Cargando agentes..." /> : (
          <>
            <section>
              <h2 className="text-lg font-bold mb-3">Tus agentes</h2>
              {contracts.length === 0 ? (
                <EmptyState icon="🤝" title="Todavía no has contratado agentes">
                  Elige uno del catálogo y encárgale su primera tarea.
                </EmptyState>
              ) : (
                <div className="grid gap-4 lg:grid-cols-2">
                  {contracts.map((c) => (
                    <ContractPanel key={c.id} companyId={companyId} contract={c} onChanged={reload} onError={showError} />
                  ))}
                </div>
              )}
            </section>
            <section>
              <h2 className="text-lg font-bold mb-3">Catálogo</h2>
              <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
                {catalog.map((o) => <HireCard key={o.code} offering={o} onHire={(p, u) => hire(o, p, u)} />)}
              </div>
            </section>
          </>
        )}
      </div>
    </AppShell>
  )
}
