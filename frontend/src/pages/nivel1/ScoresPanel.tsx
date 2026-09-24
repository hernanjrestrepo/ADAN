import Button from '../../components/ui/Button'
import Card from '../../components/ui/Card'
import type { Decision, GateReviewResult, Score } from '../../types'

interface ScoresPanelProps {
  scores: Score[]
  gate: GateReviewResult | null
  pendingDecision: Decision | null
  deciding: boolean
  onDecide: (action: 'approve' | 'reject') => void
}

export default function ScoresPanel({ scores, gate, pendingDecision, deciding, onDecide }: ScoresPanelProps) {
  return (
    <div className="max-w-4xl mx-auto p-6 overflow-y-auto h-full">
      <h2 className="text-2xl font-bold mb-6">Scores</h2>
      {scores.length === 0 ? (
        <div className="text-center py-12 text-adan-muted">No hay scores calculados aún. Genera el diagnóstico primero.</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {scores.map((score) => (
            <Card key={score.id}>
              <div className="flex items-center justify-between mb-3">
                <h3 className="font-bold capitalize">{score.score_type} Score</h3>
                <span className="text-2xl font-bold text-adan-accent">{score.value.toFixed(0)}</span>
              </div>
              <div className="w-full bg-adan-bg rounded-full h-2 mb-3" role="progressbar"
                aria-valuenow={score.value} aria-valuemin={0} aria-valuemax={100}>
                <div className="bg-adan-accent h-2 rounded-full transition-all" style={{ width: `${score.value}%` }} />
              </div>
              <div className="text-xs text-adan-muted mb-2">Confianza: {score.confidence_level.toFixed(0)}%</div>
              {score.reasoning && <p className="text-sm text-adan-text/80">{score.reasoning}</p>}
            </Card>
          ))}
        </div>
      )}

      {gate && (
        <div className={`mt-6 p-6 rounded-xl border ${
          gate.approved ? 'bg-adan-success/10 border-adan-success/50' : 'bg-adan-danger/10 border-adan-danger/50'
        }`}>
          <h3 className={`text-lg font-bold mb-2 ${gate.approved ? 'text-adan-success' : 'text-adan-danger'}`}>
            {gate.approved ? '✅ Gate Review Aprobado' : '❌ Gate Review No Aprobado'}
          </h3>
          <p className="text-sm">{gate.message}</p>
          <p className="text-xs text-adan-muted mt-2">Estado del nivel: {gate.level_status}</p>
          {/* El Nivel solo se cierra con la aprobación explícita del cliente (AD-FUNC-01, Patrón A) */}
          {pendingDecision && (
            <div className="flex gap-3 mt-4">
              <Button variant="success" className="flex-1" disabled={deciding} onClick={() => onDecide('approve')}>
                Aprobar cierre del Nivel 1
              </Button>
              <Button variant="secondary" className="flex-1" disabled={deciding} onClick={() => onDecide('reject')}>
                Todavía no
              </Button>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
