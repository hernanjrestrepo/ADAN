import Button from '../../components/ui/Button'
import { EmptyState } from '../../components/ui/States'
import type { TimelineEvent } from '../../types'
import { ACTOR_LABELS, describeEvent } from './labels'

// Timeline (AD-UX-08): cada transición, alta o archivo del Gemelo genera un Evento (AD-008 §4)
function actorOf(e: TimelineEvent): string {
  if (!e.actor_type) return 'ADÁN'
  if (e.actor_type === 'agent' && e.actor_id) return e.actor_id
  return ACTOR_LABELS[e.actor_type] ?? e.actor_type
}

interface TimelinePanelProps {
  events: TimelineEvent[]
  hasMore: boolean
  loadingMore: boolean
  onLoadMore: () => void
}

export default function TimelinePanel({ events, hasMore, loadingMore, onLoadMore }: TimelinePanelProps) {
  if (events.length === 0) {
    return <EmptyState icon="🕒" title="Sin eventos todavía">Cada cambio del Gemelo quedará registrado aquí.</EmptyState>
  }
  return (
    <div>
      <ol className="relative border-l border-adan-border ml-2" aria-label="Timeline del Gemelo">
        {events.map((e) => (
          <li key={e.id} className="ml-6 pb-5" data-testid="timeline-event">
            <span className="absolute -left-1.5 mt-1.5 h-3 w-3 rounded-full bg-adan-accent" aria-hidden="true" />
            <p className="text-sm">{describeEvent(e)}</p>
            <p className="text-xs text-adan-muted">
              {new Date(e.created_at).toLocaleString('es-CO')} · {actorOf(e)}
              {typeof e.data.reason === 'string' && e.data.reason ? ` · ${e.data.reason}` : ''}
            </p>
          </li>
        ))}
      </ol>
      {hasMore && (
        <Button variant="secondary" disabled={loadingMore} onClick={onLoadMore}>
          {loadingMore ? 'Cargando…' : 'Ver eventos anteriores'}
        </Button>
      )}
    </div>
  )
}
