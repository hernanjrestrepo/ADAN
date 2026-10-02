import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router'
import AppShell from '../components/AppShell'
import Alert from '../components/ui/Alert'
import Badge, { type Tone } from '../components/ui/Badge'
import { LoadingState } from '../components/ui/States'
import { api, errorMessage } from '../lib/api'
import type { Company, LevelStatus, LevelView } from '../types'

// Vista de Nivel y Cards (AD-FUNC-01, AD-UX-05; WO-108): los 7 Niveles como una sola ruta
const STATUS: Record<LevelStatus, { label: string; tone: Tone; dot: string }> = {
  completed: { label: 'Completado', tone: 'green', dot: 'bg-adan-success border-adan-success' },
  active: { label: 'En progreso', tone: 'blue', dot: 'bg-adan-accent border-adan-accent ring-4 ring-adan-accent/20' },
  blocked: { label: 'Bloqueado', tone: 'gray', dot: 'bg-adan-bg border-adan-border' },
}

const CARD_STATUS: Record<string, string> = { active: 'En curso', completed: 'Lista', blocked: 'Pendiente' }

export default function RoutePage() {
  const { companyId = '' } = useParams()
  const [levels, setLevels] = useState<LevelView[] | null>(null)
  const [company, setCompany] = useState<Company | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    api.getLevels(companyId)
      .then((lv) => { if (!cancelled) setLevels(lv) })
      .catch((err: unknown) => { if (!cancelled) setError(errorMessage(err)) })
    // El nombre solo adorna la miga de pan: si falla, la ruta igual se muestra
    api.getCompany(companyId).then((co) => { if (!cancelled) setCompany(co) }).catch(() => undefined)
    return () => { cancelled = true }
  }, [companyId])

  const name = company?.name ?? 'Empresa'
  const done = levels?.filter((l) => l.status === 'completed').length ?? 0

  return (
    <AppShell crumbs={[{ label: 'Mis Empresas', to: '/dashboard' }, { label: name, to: `/gemelo/${companyId}` },
      { label: 'Ruta' }]}>
      <div className="max-w-3xl mx-auto p-4 sm:p-6 overflow-y-auto h-full">
        {error && <Alert message={error} onClose={() => setError(null)} />}
        {levels === null ? (error ? null : <LoadingState label="Cargando la ruta..." />) : (
          <>
            <div className="mb-8">
              <h1 className="text-3xl font-bold">Tu ruta de 7 Niveles</h1>
              <p className="text-adan-muted mt-1">
                {done} de 7 completados. Cada Nivel se cierra con evidencia y con tu aprobación.
              </p>
              <div className="mt-4 h-2 rounded-full bg-adan-surface overflow-hidden" role="progressbar"
                aria-label="Niveles completados" aria-valuenow={done} aria-valuemin={0} aria-valuemax={7}>
                <div className="h-full bg-gradient-to-r from-adan-accent to-indigo-400" style={{ width: `${(done / 7) * 100}%` }} />
              </div>
            </div>
            <ol className="relative border-l-2 border-adan-border ml-3 space-y-8" aria-label="Niveles">
              {levels.map((level) => {
                const st = STATUS[level.status]
                return (
                  <li key={level.id} className="ml-8" data-testid="level-step">
                    <span aria-hidden="true"
                      className={`absolute -left-[11px] mt-1 h-5 w-5 rounded-full border-2 ${st.dot}`} />
                    <div className={level.status === 'blocked' ? 'opacity-60' : ''}>
                      <div className="flex flex-wrap items-center gap-2">
                        <h2 className="text-lg font-bold">Nivel {level.number} — {level.name}</h2>
                        <Badge tone={st.tone}>{st.label}</Badge>
                        {level.score && (
                          <span className="text-xs text-adan-muted">
                            Score {level.score.value.toFixed(0)} · confianza {level.score.confidence.toFixed(0)} %
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-adan-muted mt-1">{level.discovers}</p>
                      <p className="text-xs mt-1">Entregable: <span className="font-medium">{level.deliverable}</span></p>
                      {level.cards.length > 0 && (
                        <ul className="mt-3 grid gap-2 sm:grid-cols-2">
                          {level.cards.map((card) => (
                            <li key={card.id} className="rounded-xl border border-adan-border bg-adan-surface p-3">
                              <div className="flex items-center justify-between gap-2">
                                <span className="text-sm font-medium">{card.title}</span>
                                <span className="text-xs text-adan-muted">{CARD_STATUS[card.status] ?? card.status}</span>
                              </div>
                              {card.description && <p className="text-xs text-adan-muted mt-1">{card.description}</p>}
                            </li>
                          ))}
                        </ul>
                      )}
                      {level.status === 'active' && level.number === 1 && (
                        <Link to={`/nivel1/${companyId}`}
                          className="inline-block mt-3 rounded-lg bg-adan-accent px-4 py-2 text-sm font-medium text-white hover:bg-blue-500">
                          Continuar el Nivel 1 →
                        </Link>
                      )}
                      {level.status === 'active' && level.number > 1 && (
                        <p className="mt-3 text-sm text-adan-muted">
                          Este Nivel ya está abierto; su espacio de trabajo llega en una próxima versión de ADÁN.
                        </p>
                      )}
                    </div>
                  </li>
                )
              })}
            </ol>
          </>
        )}
      </div>
    </AppShell>
  )
}
