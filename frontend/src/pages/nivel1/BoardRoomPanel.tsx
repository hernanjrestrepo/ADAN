import { useEffect, useState, type FormEvent } from 'react'
import ReactMarkdown from 'react-markdown'
import MicButton from '../../components/MicButton'
import VoteBadge from '../../components/VoteBadge'
import Button from '../../components/ui/Button'
import Card from '../../components/ui/Card'
import { Field, TextAreaField } from '../../components/ui/Field'
import { LoadingState } from '../../components/ui/States'
import { api, errorMessage } from '../../lib/api'
import type { BoardConsensus, BoardDialogue, BoardDialogueTurn, BoardRoomInput } from '../../types'

interface BoardRoomPanelProps {
  companyId: string
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
// Caja para escribir o dictar: se usa en el diálogo general y en cada especialista
function Composer({ placeholder, busy, onSend, autoFocus = false }: {
  placeholder: string; busy: boolean; onSend: (text: string) => Promise<boolean>; autoFocus?: boolean
}) {
  const [text, setText] = useState('')
  const send = async (e?: FormEvent) => {
    e?.preventDefault()
    const t = text.trim()
    if (!t || busy) return
    if (await onSend(t)) setText('')
  }
  return (
    <form onSubmit={send} className="mt-3 flex items-end gap-2">
      <textarea value={text} onChange={(e) => setText(e.target.value)} rows={2} maxLength={4000} placeholder={placeholder}
        aria-label={placeholder} autoFocus={autoFocus} disabled={busy}
        onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey && !e.nativeEvent.isComposing) { e.preventDefault(); void send() } }}
        className="flex-1 resize-none rounded-xl border border-adan-border bg-adan-bg px-3 py-2 text-sm focus:border-adan-accent focus:outline-hidden" />
      <MicButton onText={(t) => setText((v) => (v ? `${v} ${t}` : t))} disabled={busy}
        className="rounded-xl border border-adan-border px-3 py-2 hover:border-adan-accent disabled:opacity-40" />
      <Button type="submit" loading={busy} disabled={!text.trim()}>Enviar</Button>
    </form>
  )
}

// Un intercambio del diálogo: lo que dijo el fundador, lo que respondió el Board y la moderación del CEO
function Turn({ turn, only }: { turn: BoardDialogueTurn; only?: string }) {
  const replies = only ? turn.replies.filter((r) => r.agent === only) : turn.replies
  return (
    <div className="space-y-2 text-sm">
      <div className="flex justify-end">
        <p className="max-w-[85%] rounded-2xl bg-adan-accent px-3 py-2 text-white whitespace-pre-wrap">
          {turn.agent && !only && <span className="block text-[11px] opacity-80">A {turn.agent}</span>}{turn.message}
        </p>
      </div>
      {replies.map((r, i) => (
        <div key={i} className="max-w-[90%] rounded-2xl border border-adan-border bg-adan-bg px-3 py-2">
          <p className="text-xs font-bold text-adan-accent">{r.agent}
            {r.changed && <span className="ml-2 font-normal text-adan-success">cambió su voto a {r.vote === 'PROCEED' ? 'A FAVOR' : r.vote}{r.reason ? `: ${r.reason}` : ''}</span>}
          </p>
          <div className="markdown"><ReactMarkdown>{r.reply}</ReactMarkdown></div>
        </div>
      ))}
      {!only && turn.ceo && (
        <div className="max-w-[90%] rounded-2xl border border-adan-accent/40 bg-adan-accent/5 px-3 py-2">
          <p className="text-xs font-bold">CEO (modera)</p>
          <p>{turn.ceo}</p>
          {turn.consensus && <p className="mt-1 text-xs text-adan-muted">Consenso: {turn.consensus}</p>}
        </div>
      )}
    </div>
  )
}

function VoteCard({ vote, current, turns, busy, onReply }: {
  vote: BoardConsensus['votes'][number]
  current?: BoardConsensus['votes'][number]['vote']
  turns: BoardDialogueTurn[]
  busy: boolean
  onReply: (agent: string, text: string) => Promise<boolean>
}) {
  const [open, setOpen] = useState(false)
  const mine = turns.filter((t) => t.agent === vote.agent || t.replies.some((r) => r.agent === vote.agent))
  const changed = current && current !== vote.vote
  return (
    <Card data-testid="agent-vote">
      <div className="flex items-center gap-3">
        {/* CEO, CTO, CFO y CMO empiezan por "C": la inicial no los distingue */}
        <div data-testid="agent-avatar" className="w-10 h-10 shrink-0 rounded-full bg-adan-accent/20 flex items-center justify-center text-adan-accent text-xs font-bold">
          {vote.agent.slice(0, 3).toUpperCase()}
        </div>
        <div className="flex-1 min-w-0">
          <h3 className="font-bold">
            {vote.agent}
            {vote.devils_advocate && <span className="ml-2 text-xs font-normal text-orange-300" title="Su trabajo en esta sesión es construir el caso en contra">😈 Abogado del diablo</span>}
          </h3>
          <p className="text-xs text-adan-muted">
            confianza {vote.confidence.toFixed(0)}%
            {vote.bulletproof !== undefined && (vote.bulletproof
              ? <span className="ml-2 text-adan-success">· su área está a prueba de balas</span>
              : <span className="ml-2 text-adan-warning">· su área todavía no está a prueba de balas</span>)}
          </p>
        </div>
        <div className="text-right">
          <VoteBadge vote={current ?? vote.vote} />
          {changed && <p className="mt-1 text-[11px] text-adan-muted">antes: {vote.vote === 'PROCEED' ? 'a favor' : vote.vote.toLowerCase()}</p>}
        </div>
      </div>
      <p className="text-sm mt-3">{vote.justification}</p>
      {vote.failure_mode && (
        <p className="text-sm mt-2 rounded-lg bg-adan-danger/10 px-3 py-2"><span className="font-bold">Podría cerrar por:</span> {vote.failure_mode}</p>
      )}
      <List title="Le preocupa" items={vote.key_concerns ?? []} />
      <List title="Cambiaría su voto si…" items={vote.questions ?? []} />
      {vote.analysis && vote.analysis !== vote.justification && (
        <details className="mt-3 text-sm">
          <summary className="cursor-pointer text-adan-muted">Ver análisis completo</summary>
          <p className="mt-2 whitespace-pre-wrap text-adan-text/90">{vote.analysis}</p>
        </details>
      )}
      {mine.length > 0 && (
        <div className="mt-4 space-y-3 border-t border-adan-border pt-3">
          {mine.map((t, i) => <Turn key={i} turn={t} only={vote.agent} />)}
        </div>
      )}
      {open ? (
        <Composer placeholder={`Responder a ${vote.agent}: explica, pregunta o aporta evidencia…`} busy={busy} autoFocus
          onSend={(t) => onReply(vote.agent, t)} />
      ) : (
        <button type="button" onClick={() => setOpen(true)} className="mt-3 text-sm font-semibold text-adan-accent hover:underline">
          💬 Responder a {vote.agent}
        </button>
      )}
    </Card>
  )
}

export default function BoardRoomPanel({ companyId, result, running, onRun, onNewSession }: BoardRoomPanelProps) {
  const [dialogue, setDialogue] = useState<BoardDialogue | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [override, setOverride] = useState<'closed' | 'open' | { objections: number }>('closed')
  const [reason, setReason] = useState('')

  // El hilo es el de la última sesión: se recarga cuando hay un resultado nuevo
  useEffect(() => {
    if (!result) return
    let cancelled = false
    api.getBoardDialogue(companyId).then((d) => { if (!cancelled) setDialogue(d) }).catch(() => undefined)
    return () => { cancelled = true }
  }, [companyId, result])

  const talk = async (text: string, agent: string | null) => {
    setBusy(true)
    setError(null)
    try {
      const d = await api.talkToBoard(companyId, text, agent)
      setDialogue({ thread: d.thread, tally: d.tally })
      return true
    } catch (err) {
      setError(errorMessage(err))
      return false
    } finally {
      setBusy(false)
    }
  }

  // El fundador decide seguir aunque el Board no aprobó: queda escrito y baja la calificación
  const continueAnyway = async () => {
    setBusy(true)
    setError(null)
    try {
      const r = await api.continueDespiteBoard(companyId, reason.trim())
      setOverride({ objections: r.open_objections.length })
    } catch (err) {
      setError(errorMessage(err))
    } finally {
      setBusy(false)
    }
  }

  const turns = dialogue?.thread ?? []
  const tally = dialogue?.tally
  const general = turns.filter((t) => !t.agent)

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
            {(result.failure_modes ?? []).length > 0 && (
              <div className="mt-4 rounded-xl border border-adan-danger/30 bg-adan-danger/5 p-4" data-testid="failure-modes">
                <p className="text-sm font-bold">Por qué esta empresa podría cerrar (y cómo blindarla)</p>
                <p className="text-xs text-adan-muted mt-1">9 de cada 10 empresas cierran en sus primeros cinco años. El Board te lo dice a tiempo.</p>
                <ul className="mt-2 list-disc pl-5 space-y-1 text-sm">{(result.failure_modes ?? []).map((f) => <li key={f}>{f}</li>)}</ul>
              </div>
            )}
            {(result.bulletproof_gaps ?? []).length > 0 && (
              <p className="mt-3 text-sm text-adan-warning">
                Todavía no está a prueba de balas en: {(result.bulletproof_gaps ?? []).join(', ')}. Para avanzar, el Board exige 5 de 6 a favor y cada área blindada.
              </p>
            )}
            <List title="Evidencia que el Board te pide" items={result.evidence_requests ?? []} />
            <List title="Próximos pasos" items={result.next_steps ?? []} />
            <p className="text-xs text-adan-muted mt-4">Es una propuesta del Board: la decisión final es tuya.</p>
          </Card>
          <Card data-testid="board-dialogue">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <h3 className="font-bold">💬 Conversa con el Board</h3>
              {tally && (
                <span className="text-xs text-adan-muted">
                  Consenso actual: <b className="text-adan-text">{tally.proceed} de {tally.total}</b> a favor ·{' '}
                  <VoteBadge vote={tally.recommendation} />
                </span>
              )}
            </div>
            <p className="mt-1 text-sm text-adan-muted">
              Pregunta lo que no entiendas, explica tu posición o aporta evidencia. Responde el especialista al que le
              toca y el CEO modera. Un voto solo cambia con datos verificables, no por insistencia. Para responderle a
              uno en particular, usa “Responder” en su tarjeta.
            </p>
            {general.length > 0 && <div className="mt-4 space-y-4">{general.map((t, i) => <Turn key={i} turn={t} />)}</div>}
            {busy && <p className="mt-3 text-sm text-adan-muted animate-pulse">El Board está pensando su respuesta…</p>}
            {error && <p role="alert" className="mt-3 text-sm text-adan-danger">{error}</p>}
            <Composer placeholder="Escríbele al Board…" busy={busy} onSend={(t) => talk(t, null)} />
            {tally && tally.recommendation !== 'PROCEED' && (
              <div className="mt-4 border-t border-adan-border pt-3 text-sm" data-testid="continue-anyway">
                {typeof override === 'object' ? (
                  <p className="rounded-lg bg-adan-warning/10 p-3 text-adan-warning">
                    Quedó registrado: decidiste continuar con {override.objections} objeción(es) abiertas del Board. Afecta la
                    calificación de la empresa (Problem Score). Para cerrar el Nivel, ve a Scores y aprueba el cierre.
                  </p>
                ) : override === 'open' ? (
                  <div className="space-y-2">
                    <p className="text-adan-muted">Escribe por qué decides seguir. Queda en el acta junto con las objeciones abiertas y baja la calificación.</p>
                    <textarea value={reason} onChange={(e) => setReason(e.target.value)} rows={2} maxLength={2000}
                      aria-label="Motivo para continuar" placeholder="Ya expliqué los tres temas; el mercado solo se valida lanzando…"
                      className="w-full rounded-xl border border-adan-border bg-adan-bg px-3 py-2" />
                    <div className="flex gap-2">
                      <Button onClick={continueAnyway} loading={busy} disabled={reason.trim().length < 3}>Continuar bajo mi responsabilidad</Button>
                      <Button variant="ghost" onClick={() => setOverride('closed')}>Cancelar</Button>
                    </div>
                  </div>
                ) : (
                  <button type="button" onClick={() => setOverride('open')} className="font-semibold text-adan-warning hover:underline">
                    ⚖️ No tengo más que aportar: continuar bajo mi responsabilidad
                  </button>
                )}
              </div>
            )}
          </Card>
          {result.votes.map((vote) => (
            <VoteCard key={vote.agent} vote={vote} current={tally?.votes[vote.agent]} turns={turns} busy={busy}
              onReply={(agent, t) => talk(t, agent)} />
          ))}
        </div>
      )}
    </div>
  )
}
