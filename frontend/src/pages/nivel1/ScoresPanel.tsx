import { useEffect, useState } from 'react'
import { Link } from 'react-router'
import Button from '../../components/ui/Button'
import Card from '../../components/ui/Card'
import { LoadingState } from '../../components/ui/States'
import { api, errorMessage } from '../../lib/api'
import type { Decision, EvidenceKind, GateReviewResult, ScoreOverview } from '../../types'
import { KIND } from './evidenceLabels'

interface ScoresPanelProps {
  companyId: string
  refreshKey: number
  gate: GateReviewResult | null
  pendingDecision: Decision | null
  deciding: boolean
  advancing: boolean
  onDecide: (action: 'approve' | 'reject') => void
  onAdvanceAnyway: () => void
  onGoToEvidence: () => void
  onError: (message: string) => void
}

function ScoreCard({ score, onCalculate, busy }: { score: ScoreOverview; onCalculate: () => void; busy: boolean }) {
  const latest = score.latest
  return (
    <Card className={`!p-5 ${score.available ? '' : 'opacity-60'}`} data-testid="score-card">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <h3 className="font-bold">{score.label}</h3>
          <p className="text-xs text-adan-muted">{score.measures}</p>
        </div>
        <span className="text-2xl font-bold text-adan-accent tabular-nums">
          {latest ? latest.value.toFixed(0) : '—'}
        </span>
      </div>
      {score.available ? (
        <>
          <div className="mt-3">
            <div className="flex justify-between text-xs text-adan-muted mb-1">
              <span>Confianza</span><span>{latest ? `${latest.confidence.toFixed(0)} %` : 'sin calcular'}</span>
            </div>
            <div className="h-1.5 rounded-full bg-adan-bg overflow-hidden" role="progressbar" aria-label="Confianza"
              aria-valuenow={latest?.confidence ?? 0} aria-valuemin={0} aria-valuemax={100}>
              <div className="h-full rounded-full bg-adan-accent" style={{ width: `${latest?.confidence ?? 0}%` }} />
            </div>
          </div>
          {latest?.breakdown && (
            <p className="text-xs text-adan-muted mt-3">
              {(Object.keys(KIND) as EvidenceKind[])
                .map((k) => `${latest.breakdown![k].supports + latest.breakdown![k].contradicts} ${KIND[k].short}`)
                .join(' · ')}
            </p>
          )}
          {latest?.reasoning && <p className="text-xs text-adan-text/70 mt-2">{latest.reasoning}</p>}
          <Button size="sm" variant="ghost" className="mt-2 -ml-3" loading={busy} onClick={onCalculate}>
            {latest ? 'Recalcular' : 'Calcular'}
          </Button>
        </>
      ) : (
        <p className="text-xs text-adan-muted mt-3">{score.unavailable_reason}</p>
      )}
    </Card>
  )
}

export default function ScoresPanel({
  companyId, refreshKey, gate, pendingDecision, deciding, advancing, onDecide, onAdvanceAnyway, onGoToEvidence,
  onError,
}: ScoresPanelProps) {
  const [scores, setScores] = useState<ScoreOverview[] | null>(null)
  const [busy, setBusy] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    api.getScoresOverview(companyId)
      .then((data) => { if (!cancelled) setScores(data) })
      .catch((err: unknown) => { if (!cancelled) onError(errorMessage(err)) })
    return () => { cancelled = true }
  }, [companyId, refreshKey, onError])

  const calculate = async (key: string) => {
    setBusy(key)
    try {
      const updated = await api.calculateScore(companyId, key)
      setScores((prev) => prev?.map((s) => (s.key === key ? updated : s)) ?? prev)
    } catch (err) {
      onError(errorMessage(err))
    } finally {
      setBusy(null)
    }
  }

  const advancedDecision = pendingDecision?.recommended_option === 'CONTINUE' ? pendingDecision : null

  return (
    <div className="max-w-5xl mx-auto p-4 sm:p-6 overflow-y-auto h-full space-y-6">
      <div>
        <h2 className="text-2xl font-bold">Scores</h2>
        <p className="text-sm text-adan-muted mt-1">
          Cada Score sale de la evidencia registrada y declara su confianza. Seis acompañan a los Niveles; el del
          Responsable y el Venture Score siguen a la persona y a la empresa en el tiempo.
        </p>
      </div>

      {gate && (
        <div className={`p-5 rounded-2xl border ${
          gate.approved ? 'bg-adan-success/10 border-adan-success/50' : 'bg-adan-warning/10 border-adan-warning/40'}`}
          data-testid="gate-result">
          <h3 className={`text-lg font-bold mb-1 ${gate.approved ? 'text-adan-success' : 'text-adan-warning'}`}>
            {gate.approved ? '✅ La evidencia alcanza' : 'Todavía falta evidencia'}
          </h3>
          <p className="text-sm">{gate.message}</p>
          {!gate.approved && gate.missing && gate.missing.length > 0 && (
            <ul className="mt-3 space-y-1 text-sm list-disc pl-5">
              {gate.missing.map((m) => <li key={m}>{m}</li>)}
            </ul>
          )}
          {/* El Nivel solo se cierra con la aprobación explícita del cliente (AD-FUNC-01, Patrón A) */}
          {gate.approved && pendingDecision && pendingDecision.recommended_option !== 'CONTINUE' && (
            <div className="flex flex-col sm:flex-row gap-3 mt-4">
              <Button variant="success" className="flex-1" disabled={deciding} onClick={() => onDecide('approve')}>
                Aprobar cierre del Nivel 1
              </Button>
              <Button variant="secondary" className="flex-1" disabled={deciding} onClick={() => onDecide('reject')}>
                Todavía no
              </Button>
            </div>
          )}
          {!gate.approved && !advancedDecision && (
            <div className="flex flex-col sm:flex-row gap-3 mt-4">
              <Button className="flex-1" onClick={onGoToEvidence}>Registrar evidencia</Button>
              <Button variant="secondary" className="flex-1" loading={advancing} onClick={onAdvanceAnyway}>
                Avanzar bajo mi responsabilidad
              </Button>
            </div>
          )}
          {advancedDecision && (
            <div className="mt-4 text-sm">
              ADÁN recomienda seguir trabajando el Nivel, pero la decisión es tuya. Para cerrarlo igual, elige
              «Cerrar el Nivel 1» y registra los riesgos y la responsabilidad que asumes.{' '}
              <Link to={`/gemelo/${companyId}?tab=decisions`} className="text-adan-accent hover:underline font-medium">
                Ir a Decisiones →
              </Link>
            </div>
          )}
        </div>
      )}

      {scores === null ? (
        <LoadingState label="Cargando Scores..." />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {scores.map((s) => (
            <ScoreCard key={s.key} score={s} busy={busy === s.key} onCalculate={() => calculate(s.key)} />
          ))}
        </div>
      )}
    </div>
  )
}
