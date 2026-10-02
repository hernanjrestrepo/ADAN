import Card from '../../components/ui/Card'
import type { TwinKind, TwinOverview } from '../../types'

// Identidad del Gemelo (AD-005 §4, AD-007): dimensiones derivadas, entidades y linaje
const STAGE_LABELS: Record<string, string> = {
  nacimiento: 'Nacimiento', temprana: 'Etapa temprana', crecimiento: 'Crecimiento', madurez: 'Madurez',
  estancamiento: 'Estancamiento (Edad sin Madurez)',
}

const STATUS_LABELS: Record<string, string> = { active: 'Activo', paused: 'Pausado', archived: 'Archivado' }

// "0.0 años" no dice nada: menos de un mes es "Recién nacida"; menos de un año, en meses
function formatAge(years: number): string {
  if (years < 1 / 12) return 'Recién nacida'
  if (years < 1) {
    const months = Math.round(years * 12)
    return `${months} ${months === 1 ? 'mes' : 'meses'}`
  }
  return `${years.toFixed(1)} años`
}

interface OverviewPanelProps {
  twin: TwinOverview
  kinds: TwinKind[]
}

export default function OverviewPanel({ twin, kinds }: OverviewPanelProps) {
  const { identity } = twin
  const clusters = Array.from(new Set(kinds.map((k) => k.cluster_label)))
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4" data-testid="twin-identity">
        <Stat label="Estado" value={STATUS_LABELS[twin.company.status] ?? twin.company.status} />
        <Stat label="Edad" value={formatAge(identity.age_years)} />
        <Stat label="Madurez" value={`${Math.round(identity.maturity * 100)}%`} />
        <Stat label="Etapa del ciclo de vida" value={STAGE_LABELS[identity.lifecycle_stage] ?? identity.lifecycle_stage} />
      </div>
      {identity.maturation_velocity_per_year !== null && (
        <p className="text-sm text-adan-muted">
          Velocidad de maduración: {(identity.maturation_velocity_per_year * 100).toFixed(1)} puntos por año
        </p>
      )}

      {twin.lineage.length > 0 && (
        <Card>
          <h3 className="font-bold mb-2">Linaje</h3>
          <ul className="text-sm space-y-1">
            {twin.lineage.map((l) => (
              <li key={`${l.company_id}-${l.source_company_id}`}>
                {l.relation === 'split_from'
                  ? (l.company_id === twin.company.id ? 'Se separó de otra Empresa' : 'Una Iniciativa se separó como Empresa nueva')
                  : (l.company_id === twin.company.id ? 'Nació de una fusión' : 'Se fusionó en una Empresa nueva')}
                {l.note ? ` — ${l.note}` : ''}
              </li>
            ))}
          </ul>
        </Card>
      )}

      {clusters.map((cluster) => (
        <Card key={cluster}>
          <h3 className="font-bold mb-3">{cluster}</h3>
          <dl className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-x-6 gap-y-2 text-sm">
            {kinds.filter((k) => k.cluster_label === cluster).map((k) => (
              <div key={k.key} className="flex justify-between gap-2">
                <dt className="text-adan-muted">{k.label_plural}</dt>
                <dd className="font-medium">{twin.counts[k.key] ?? 0}</dd>
              </div>
            ))}
          </dl>
        </Card>
      ))}
    </div>
  )
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <Card className="!p-4">
      <p className="text-xs text-adan-muted">{label}</p>
      <p className="text-lg font-bold">{value}</p>
    </Card>
  )
}
