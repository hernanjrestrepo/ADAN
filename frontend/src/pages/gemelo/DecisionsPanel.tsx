import { useState } from 'react'
import Badge from '../../components/ui/Badge'
import Button from '../../components/ui/Button'
import Card from '../../components/ui/Card'
import { Field, TextAreaField } from '../../components/ui/Field'
import { EmptyState } from '../../components/ui/States'
import type { DecideInput, Decision, DecisionOption, DecisionStatus } from '../../types'
import { DECISION_STATUS, EVIDENCE_TONE } from './labels'

// Vista de Decisiones (AD-UX-10): el ciclo del Patrón A, el disenso y lo que exige §2.5

interface DecisionsPanelProps {
  decisions: Decision[]
  busyId: string | null
  onPresent: (decision: Decision) => void
  onDecide: (decision: Decision, input: DecideInput) => void
  onExecute: (decision: Decision, businessDecisionTitle?: string) => void
}

export default function DecisionsPanel({ decisions, busyId, onPresent, onDecide, onExecute }: DecisionsPanelProps) {
  if (decisions.length === 0) {
    return (
      <EmptyState icon="⚖️" title="Todavía no hay decisiones">
        Las propuestas del Board Room y del Gate Review aparecen aquí para que las apruebes o rechaces.
      </EmptyState>
    )
  }
  return (
    <div className="space-y-6">
      {decisions.map((d) => (
        <DecisionCard key={d.id} decision={d} busy={busyId === d.id}
          onPresent={onPresent} onDecide={onDecide} onExecute={onExecute} />
      ))}
    </div>
  )
}

interface DecisionCardProps {
  decision: Decision
  busy: boolean
  onPresent: (decision: Decision) => void
  onDecide: (decision: Decision, input: DecideInput) => void
  onExecute: (decision: Decision, businessDecisionTitle?: string) => void
}

function DecisionCard({ decision, busy, onPresent, onDecide, onExecute }: DecisionCardProps) {
  const [chosen, setChosen] = useState<string | null>(null)
  const [risks, setRisks] = useState('')
  const [responsibility, setResponsibility] = useState('')
  const [businessTitle, setBusinessTitle] = useState('')
  const status = DECISION_STATUS[decision.status]
  const options = decision.options ?? []
  const recommended = decision.recommended_option ?? null
  const open = decision.status === 'proposed' || decision.status === 'presented'
  const diverging = chosen !== null && recommended !== null && chosen !== recommended
  const riskList = risks.split('\n').map((r) => r.trim()).filter(Boolean)
  const canApproveDifferent = riskList.length > 0 && responsibility.trim().length >= 10

  const approve = () => {
    if (diverging) {
      onDecide(decision, { action: 'approve', chosen_option: chosen ?? undefined, risks_assumed: riskList,
        responsibility_statement: responsibility.trim() })
    } else {
      onDecide(decision, { action: 'approve', chosen_option: recommended ?? undefined })
    }
  }

  return (
    <Card data-testid="decision-card">
      <div className="flex items-start justify-between gap-4 mb-2">
        <div>
          <h3 className="font-bold">{decision.title}</h3>
          <p className="text-xs text-adan-muted">
            Propuesta por {decision.proposed_by ?? 'ADÁN'} · {new Date(decision.created_at).toLocaleString('es-CO')}
          </p>
        </div>
        <Badge tone={status.tone}>{status.label}</Badge>
      </div>
      {decision.description && <p className="text-sm whitespace-pre-wrap text-adan-text/90 mt-2">{decision.description}</p>}

      {options.length > 0 && (
        <fieldset className="mt-4" disabled={!open || busy}>
          <legend className="text-sm font-bold mb-2">Opciones</legend>
          <div className="space-y-2">
            {options.map((o) => (
              <OptionRow key={o.key} group={decision.id} option={o} recommended={o.key === recommended}
                chosen={decision.chosen_option === o.key}
                selected={(chosen ?? recommended) === o.key} selectable={open}
                onSelect={() => setChosen(o.key)} />
            ))}
          </div>
        </fieldset>
      )}

      {decision.disagreement && (
        <div className="mt-4 text-sm">
          <span className="font-bold">Disenso del Board:</span>
          <p className="whitespace-pre-wrap text-adan-text/80">{decision.disagreement}</p>
        </div>
      )}

      {decision.prior_decisions && decision.prior_decisions.length > 0 && (
        <div className="mt-4 text-xs text-adan-muted" data-testid="prior-decisions">
          <span className="font-bold">Consulta previa:</span> esta propuesta tuvo en cuenta{' '}
          {decision.prior_decisions.map((p) => p.title).join(' · ')}
        </div>
      )}

      {decision.divergence && (
        <div className="mt-4 p-4 rounded-lg border border-adan-warning/50 bg-adan-warning/10 text-sm" data-testid="divergence">
          <p className="font-bold mb-1">Decidiste distinto a lo recomendado</p>
          <p>
            Elegiste <strong>{decision.divergence.chosen_option.label ?? decision.divergence.chosen_option.key}</strong>{' '}
            (evidencia {decision.divergence.evidence_level.chosen}, confianza {decision.divergence.confidence.chosen}%)
            en lugar de <strong>{decision.divergence.recommended_option.label ?? decision.divergence.recommended_option.key}</strong>{' '}
            (evidencia {decision.divergence.evidence_level.recommended}, confianza {decision.divergence.confidence.recommended}%).
          </p>
          <p className="mt-2 font-bold">Riesgos asumidos</p>
          <ul className="list-disc pl-5">{decision.divergence.risks_assumed.map((r) => <li key={r}>{r}</li>)}</ul>
          <p className="mt-2"><span className="font-bold">Responsabilidad asumida:</span> {decision.divergence.responsibility_assumed}</p>
        </div>
      )}

      {decision.business_decision && (
        <p className="mt-4 text-xs text-adan-muted">
          Originó la Decisión de Negocio «{decision.business_decision.title}»
          {' '}({DECISION_STATUS[decision.business_decision.state as DecisionStatus]?.label.toLowerCase()
            ?? decision.business_decision.state})
        </p>
      )}

      {open && (
        <div className="mt-5 space-y-4">
          {diverging && (
            <div className="p-4 rounded-lg border border-adan-border space-y-3" data-testid="divergence-form">
              <p className="text-sm">
                Estás eligiendo una opción distinta a la que recomienda el Board. Es tu decisión: para que ADÁN
                aprenda de ella, registra los riesgos que asumes y tu responsabilidad.
              </p>
              <TextAreaField label="Riesgos que asumes (uno por línea)" value={risks}
                onChange={(e) => setRisks(e.target.value)} />
              <TextAreaField label="Responsabilidad que asumes" value={responsibility}
                placeholder="Entiendo la recomendación del Board y elijo esta opción porque…"
                onChange={(e) => setResponsibility(e.target.value)} />
            </div>
          )}
          <div className="flex flex-wrap gap-3">
            {decision.status === 'proposed' && (
              <Button variant="secondary" disabled={busy} onClick={() => onPresent(decision)}>Ver con razonamiento</Button>
            )}
            <Button variant="success" disabled={busy || (diverging && !canApproveDifferent)} onClick={approve}>
              {diverging ? 'Aprobar mi opción' : 'Aprobar la recomendación'}
            </Button>
            <Button variant="secondary" disabled={busy} onClick={() => onDecide(decision, { action: 'reject' })}>Rechazar</Button>
          </div>
          {decision.reasoning && decision.status === 'presented' && (
            <details className="text-sm" open>
              <summary className="cursor-pointer text-adan-muted">Razonamiento de los agentes</summary>
              <p className="whitespace-pre-wrap mt-2 text-adan-text/80">{decision.reasoning}</p>
            </details>
          )}
        </div>
      )}

      {decision.status === 'approved' && (
        <div className="mt-5 flex flex-wrap items-end gap-3">
          <Field className="flex-1 min-w-60" label="Decisión de Negocio que origina (opcional)" value={businessTitle}
            placeholder="Ej.: Abrir punto de venta en Bogotá" onChange={(e) => setBusinessTitle(e.target.value)} />
          <Button disabled={busy} onClick={() => onExecute(decision, businessTitle.trim() || undefined)}>
            Marcar como ejecutada
          </Button>
        </div>
      )}
    </Card>
  )
}

interface OptionRowProps {
  group: string
  option: DecisionOption
  recommended: boolean
  chosen: boolean
  selected: boolean
  selectable: boolean
  onSelect: () => void
}

function OptionRow({ group, option, recommended, chosen, selected, selectable, onSelect }: OptionRowProps) {
  return (
    <label className={`flex items-start gap-3 p-3 rounded-lg border ${
      selected && selectable ? 'border-adan-accent' : 'border-adan-border'} ${selectable ? 'cursor-pointer' : ''}`}>
      {selectable && (
        <input type="radio" name={`options-${group}`} className="mt-1" checked={selected} onChange={onSelect}
          aria-label={option.label} />
      )}
      <div className="flex-1 min-w-0">
        <div className="flex flex-wrap items-center gap-2">
          <span className="font-medium">{option.label}</span>
          {recommended && <Badge tone="blue">Recomendada</Badge>}
          {chosen && <Badge tone="green">Elegida</Badge>}
          {option.evidence_level && (
            <Badge tone={EVIDENCE_TONE[option.evidence_level] ?? 'gray'}>Evidencia {option.evidence_level}</Badge>
          )}
          {option.confidence !== undefined && <span className="text-xs text-adan-muted">Confianza {option.confidence}%</span>}
          {option.votes !== undefined && <span className="text-xs text-adan-muted">· {option.votes} votos</span>}
        </div>
        {option.rationale && <p className="text-xs text-adan-muted mt-1">{option.rationale}</p>}
      </div>
    </label>
  )
}
