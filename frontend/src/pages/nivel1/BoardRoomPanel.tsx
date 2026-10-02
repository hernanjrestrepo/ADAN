import { useState, type FormEvent } from 'react'
import VoteBadge from '../../components/VoteBadge'
import Button from '../../components/ui/Button'
import Card from '../../components/ui/Card'
import { Field, TextAreaField } from '../../components/ui/Field'
import { LoadingState } from '../../components/ui/States'
import type { BoardConsensus, BoardRoomInput } from '../../types'

interface BoardRoomPanelProps {
  result: BoardConsensus | null
  running: boolean
  onRun: (input: BoardRoomInput) => void
  onNewSession: () => void
}

function List({ title, items }: { title: string; items: string[] }) {
  if (!items.length) return null
  return (
    <div className="mt-4 text-sm">
      <p className="font-bold">{title}</p>
      <ul className="list-disc ml-5 mt-1 space-y-1">
        {items.map((item) => <li key={item}>{item}</li>)}
      </ul>
    </div>
  )
}

// El cliente participa desde el inicio (AD-FUNC-02 §3): puede plantear la pregunta y su posición
function SessionForm({ onRun }: { onRun: (input: BoardRoomInput) => void }) {
  const [question, setQuestion] = useState('')
  const [position, setPosition] = useState('')
  const submit = (e: FormEvent) => {
    e.preventDefault()
    onRun({ question: question.trim(), position: position.trim() })
  }
  return (
    <Card>
      <form onSubmit={submit} className="space-y-4">
        <p className="text-sm text-adan-muted">
          El CEO abre la sesión y la preside; CTO, CFO, CMO, Legal, Producto y Operaciones votan.
          Puedes plantear tu pregunta y tu posición (opcional).
        </p>
        <Field label="Tu pregunta para el Board" value={question} maxLength={1000}
          onChange={(e) => setQuestion(e.target.value)} placeholder="¿Lanzo primero en una sola ciudad?" />
        <TextAreaField label="Tu posición" value={position} maxLength={2000}
          onChange={(e) => setPosition(e.target.value)} placeholder="Lo que piensas hacer y por qué" />
        <Button type="submit">Ejecutar Board Room</Button>
      </form>
    </Card>
  )
}

// Voto de un especialista: lo esencial a la vista, el análisis completo al desplegar
function VoteCard({ vote }: { vote: BoardConsensus['votes'][number] }) {
  return (
    <Card data-testid="agent-vote">
      <div className="flex items-center gap-3">
        {/* CEO, CTO, CFO y CMO empiezan por "C": la inicial no los distingue */}
        <div data-testid="agent-avatar" className="w-10 h-10 shrink-0 rounded-full bg-adan-accent/20 flex items-center justify-center text-adan-accent text-xs font-bold">
          {vote.agent.slice(0, 3).toUpperCase()}
        </div>
        <div className="flex-1 min-w-0">
          <h3 className="font-bold">{vote.agent}</h3>
          <p className="text-xs text-adan-muted">confianza {vote.confidence.toFixed(0)}%</p>
        </div>
        <VoteBadge vote={vote.vote} />
      </div>
      <p className="text-sm mt-3">{vote.justification}</p>
      <List title="Le preocupa" items={vote.key_concerns ?? []} />
      <List title="Cambiaría su voto si…" items={vote.questions ?? []} />
      {vote.analysis && vote.analysis !== vote.justification && (
        <details className="mt-3 text-sm">
          <summary className="cursor-pointer text-adan-muted">Ver análisis completo</summary>
          <p className="mt-2 whitespace-pre-wrap text-adan-text/90">{vote.analysis}</p>
        </details>
      )}
    </Card>
  )
}

export default function BoardRoomPanel({ result, running, onRun, onNewSession }: BoardRoomPanelProps) {
  return (
    <div className="max-w-4xl mx-auto p-6 overflow-y-auto h-full">
      <div className="flex items-center justify-between gap-3 mb-6">
        <h2 className="text-2xl font-bold">Board Room</h2>
        {result && !running && <Button size="sm" variant="secondary" onClick={onNewSession}>Nueva sesión</Button>}
      </div>
      {running ? (
        <LoadingState label="Seis especialistas están deliberando; suele tardar uno o dos minutos..." />
      ) : !result ? (
        <SessionForm onRun={onRun} />
      ) : (
        <div className="space-y-6">
          {(result.objective || result.client_question || result.client_position) && (
            <Card data-testid="board-opening">
              <h3 className="font-bold">Apertura del CEO</h3>
              {result.objective && <p className="text-sm mt-2"><span className="font-bold">Objetivo:</span> {result.objective}</p>}
              {result.decision_at_stake && (
                <p className="text-sm mt-1"><span className="font-bold">En juego:</span> {result.decision_at_stake}</p>
              )}
              {result.client_question && <p className="text-sm mt-3"><span className="font-bold">Tu pregunta:</span> {result.client_question}</p>}
              {result.client_position && <p className="text-sm mt-1"><span className="font-bold">Tu posición:</span> {result.client_position}</p>}
            </Card>
          )}
          <Card>
            <div className="flex items-center justify-between">
              <h3 className="font-bold">Decisión del Board</h3>
              <VoteBadge vote={result.decision} />
            </div>
            <p className="text-sm text-adan-muted mt-2">
              Score {result.score.toFixed(0)}/100 · Confianza {result.confidence.toFixed(0)}%
            </p>
            {result.synthesis && (
              <div className="mt-4 text-sm whitespace-pre-wrap" data-testid="board-synthesis">
                <span className="font-bold">Síntesis del CEO:</span>{'\n'}{result.synthesis}
              </div>
            )}
            {result.dissent && (
              <div className="mt-4 text-sm whitespace-pre-wrap">
                <span className="font-bold">Disenso:</span>{'\n'}{result.dissent}
              </div>
            )}
            <List title="Evidencia que el Board te pide" items={result.evidence_requests ?? []} />
            <List title="Próximos pasos" items={result.next_steps ?? []} />
            <p className="text-xs text-adan-muted mt-4">Es una propuesta del Board: la decisión final es tuya.</p>
          </Card>
          {result.votes.map((vote) => <VoteCard key={vote.agent} vote={vote} />)}
        </div>
      )}
    </div>
  )
}
