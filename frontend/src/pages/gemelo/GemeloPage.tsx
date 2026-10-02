import { useCallback, useEffect, useState } from 'react'
import { Link, useParams } from 'react-router'
import AppShell from '../../components/AppShell'
import Alert from '../../components/ui/Alert'
import Badge from '../../components/ui/Badge'
import Tabs from '../../components/ui/Tabs'
import { LoadingState } from '../../components/ui/States'
import { api, errorMessage } from '../../lib/api'
import type { DecideInput, Decision, TimelineEvent, TwinKind, TwinOverview } from '../../types'
import DecisionsPanel from './DecisionsPanel'
import OverviewPanel from './OverviewPanel'
import TimelinePanel from './TimelinePanel'

type Tab = 'overview' | 'decisions' | 'timeline'

const TABS: { id: Tab; label: string }[] = [
  { id: 'overview', label: 'Resumen' },
  { id: 'decisions', label: 'Decisiones' },
  { id: 'timeline', label: 'Timeline' },
]

const PAGE_SIZE = 50

interface TwinData {
  overview: TwinOverview
  kinds: TwinKind[]
  decisions: Decision[]
  events: TimelineEvent[]
}

async function fetchTwin(companyId: string): Promise<TwinData> {
  const [overview, kinds, decisions, events] = await Promise.all([
    api.getTwin(companyId), api.getTwinKinds(), api.getTwinDecisions(companyId), api.getTimeline(companyId),
  ])
  return { overview, kinds, decisions, events }
}

// Gemelo Digital (WO-098): la identidad permanente de la Empresa, sus Decisiones y su historia
export default function GemeloPage() {
  const { companyId = '' } = useParams()
  const [tab, setTab] = useState<Tab>('overview')
  const [twin, setTwin] = useState<TwinOverview | null>(null)
  const [kinds, setKinds] = useState<TwinKind[]>([])
  const [decisions, setDecisions] = useState<Decision[]>([])
  const [events, setEvents] = useState<TimelineEvent[]>([])
  const [hasMore, setHasMore] = useState(false)
  const [loading, setLoading] = useState(true)
  const [loadingMore, setLoadingMore] = useState(false)
  const [busyId, setBusyId] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  const apply = useCallback((data: TwinData) => {
    setTwin(data.overview)
    setKinds(data.kinds)
    setDecisions(data.decisions)
    setEvents(data.events)
    setHasMore(data.events.length === PAGE_SIZE)
  }, [])

  const loadAll = useCallback(async () => apply(await fetchTwin(companyId)), [companyId, apply])

  // Carga inicial; se ignora la respuesta si el usuario cambió de empresa antes de que llegara
  useEffect(() => {
    let cancelled = false
    fetchTwin(companyId)
      .then((data) => { if (!cancelled) apply(data) })
      .catch((err: unknown) => { if (!cancelled) setError(errorMessage(err)) })
      .finally(() => { if (!cancelled) setLoading(false) })
    return () => { cancelled = true }
  }, [companyId, apply])

  // Tras cada acción se recarga todo: la decisión, el Timeline y los conteos cambian juntos
  const run = async (decision: Decision, action: () => Promise<unknown>) => {
    setBusyId(decision.id)
    setError(null)
    try {
      await action()
      await loadAll()
    } catch (err) {
      setError(errorMessage(err))
    } finally {
      setBusyId(null)
    }
  }

  const handlePresent = (d: Decision) => run(d, () => api.presentDecision(companyId, d.id))
  const handleDecide = (d: Decision, input: DecideInput) => run(d, () => api.decideDecision(companyId, d.id, input))
  const handleExecute = (d: Decision, title?: string) => run(d, () => api.executeDecision(companyId, d.id, title))

  const loadMore = async () => {
    const last = events[events.length - 1]
    if (!last) return
    setLoadingMore(true)
    try {
      const older = await api.getTimeline(companyId, last)
      setEvents((prev) => [...prev, ...older])
      setHasMore(older.length === PAGE_SIZE)
    } catch (err) {
      setError(errorMessage(err))
    } finally {
      setLoadingMore(false)
    }
  }

  const name = twin?.company.name ?? 'Empresa'
  const pending = decisions.filter((d) => d.status === 'proposed' || d.status === 'presented').length

  return (
    <AppShell
      crumbs={[{ label: 'Mis Empresas', to: '/dashboard' }, { label: name }, { label: 'Gemelo Digital' }]}
      status={pending > 0 ? <Badge tone="yellow">{pending} por decidir</Badge> : undefined}
      toolbar={<Tabs tabs={TABS} active={tab} onChange={setTab} />}
    >
      <div className="max-w-4xl mx-auto p-6 overflow-y-auto h-full">
        {error && <div className="mb-4"><Alert message={error} onClose={() => setError(null)} /></div>}
        {loading ? (
          <LoadingState label="Cargando el Gemelo Digital..." />
        ) : twin && (
          <>
            <div className="flex items-center justify-between mb-6">
              <h1 className="text-2xl font-bold">{name}</h1>
              <Link to={`/nivel1/${companyId}`} className="text-sm text-adan-accent hover:underline">Ir al Nivel 1</Link>
            </div>
            {tab === 'overview' && <OverviewPanel twin={twin} kinds={kinds} />}
            {tab === 'decisions' && (
              <DecisionsPanel decisions={decisions} busyId={busyId}
                onPresent={handlePresent} onDecide={handleDecide} onExecute={handleExecute} />
            )}
            {tab === 'timeline' && (
              <TimelinePanel events={events} hasMore={hasMore} loadingMore={loadingMore} onLoadMore={loadMore} />
            )}
          </>
        )}
      </div>
    </AppShell>
  )
}
