import { useEffect, useRef, useState, type FormEvent, type KeyboardEvent } from 'react'
import ReactMarkdown from 'react-markdown'
import Badge from '../../components/ui/Badge'
import Button from '../../components/ui/Button'
import { EmptyState } from '../../components/ui/States'
import type { DiscoveryProgress, DiscoveryTopic, EvidenceSuggestion, Message } from '../../types'

interface ChatPanelProps {
  messages: Message[]
  sending: boolean
  discovery?: DiscoveryProgress
  onSend: (message: string) => Promise<void>
  onRegisterEvidence: (suggestion: EvidenceSuggestion) => Promise<void>
  onBoardRoom: () => void
  onDiagnosis: () => void
  onGateReview: () => void
}

const MAX_MESSAGE_CHARS = 8000  // mismo límite que el backend (WO-097)

const TOPIC_ICON: Record<DiscoveryTopic['estado'], { icon: string; label: string; className: string }> = {
  respondido: { icon: '✓', label: 'Entendido', className: 'bg-adan-success/20 text-adan-success' },
  parcial: { icon: '◐', label: 'Falta precisar', className: 'bg-yellow-500/20 text-yellow-400' },
  sin_dato: { icon: '?', label: 'Sin dato: por validar', className: 'bg-gray-500/20 text-gray-300' },
  pendiente: { icon: '○', label: 'Pendiente', className: 'bg-adan-bg text-adan-muted' },
}

function useElapsed(running: boolean) {
  const [seconds, setSeconds] = useState(0)
  useEffect(() => {
    if (!running) return
    const started = Date.now()
    const id = setInterval(() => setSeconds(Math.floor((Date.now() - started) / 1000)), 1000)
    return () => { clearInterval(id); setSeconds(0) }
  }, [running])
  return seconds
}

// Lo que ADÁN ya entendió: el guion de siete temas con su avance (Nivel 1)
function DiscoveryPanel({ discovery, onRegisterEvidence, onBoardRoom }: {
  discovery: DiscoveryProgress
  onRegisterEvidence: (s: EvidenceSuggestion) => Promise<void>
  onBoardRoom: () => void
}) {
  const [registering, setRegistering] = useState<string | null>(null)
  const pct = Math.round((discovery.done / discovery.total) * 100)
  return (
    <aside className="space-y-4" aria-label="Lo que ADÁN ya entendió">
      <div className="rounded-xl border border-adan-border bg-adan-surface p-4">
        <div className="flex items-center justify-between gap-2">
          <h2 className="text-sm font-bold">Lo que ADÁN ya entendió</h2>
          <span className="text-xs text-adan-muted" data-testid="discovery-count">{discovery.done} de {discovery.total}</span>
        </div>
        <div className="mt-2 h-1.5 rounded-full bg-adan-bg overflow-hidden" role="progressbar" aria-label="Avance del descubrimiento"
          aria-valuenow={pct} aria-valuemin={0} aria-valuemax={100}>
          <div className="h-full bg-adan-accent transition-all" style={{ width: `${pct}%` }} />
        </div>
        <ol className="mt-3 space-y-2">
          {discovery.topics.map((t, i) => {
            const look = TOPIC_ICON[t.estado]
            const isNext = discovery.next === t.id
            return (
              <li key={t.id} data-testid="discovery-topic"
                className={`flex gap-2 rounded-lg p-2 ${isNext ? 'ring-1 ring-adan-accent bg-adan-accent/5' : ''}`}>
                <span className={`shrink-0 grid place-items-center h-6 w-6 rounded-full text-xs font-bold ${look.className}`}
                  aria-label={look.label} title={look.label}>{look.icon}</span>
                <div className="min-w-0">
                  <div className="text-sm font-medium flex flex-wrap items-center gap-1">
                    {i + 1}. {t.label}
                    {isNext && <Badge tone="blue">Siguiente</Badge>}
                    {t.resumen && t.base === 'supuesto' && <Badge tone="yellow">Supuesto</Badge>}
                    {t.resumen && t.base === 'dato' && <Badge tone="green">Dato</Badge>}
                  </div>
                  {t.resumen && <p className="text-xs text-adan-muted mt-0.5">{t.resumen}</p>}
                </div>
              </li>
            )
          })}
        </ol>
        {discovery.complete && (
          <div className="mt-3 rounded-lg bg-adan-success/10 p-3 text-xs">
            <p className="mb-2">ADÁN ya entendió los siete temas. El siguiente paso es que el Board Room lo evalúe.</p>
            <Button size="sm" onClick={onBoardRoom}>🏛️ Ejecutar Board Room</Button>
          </div>
        )}
      </div>

      {discovery.evidence_suggestions.length > 0 && (
        <div className="rounded-xl border border-adan-border bg-adan-surface p-4" aria-label="Evidencia detectada">
          <h2 className="text-sm font-bold">Evidencia que mencionaste</h2>
          <p className="text-xs text-adan-muted mt-1">Regístrala para que cuente en el Gate del Nivel 1. Tú decides.</p>
          <ul className="mt-3 space-y-3">
            {discovery.evidence_suggestions.map((s) => (
              <li key={s.afirmacion} className="text-xs border-t border-adan-border pt-3 first:border-0 first:pt-0"
                data-testid="evidence-suggestion">
                <p className="text-adan-text">{s.afirmacion}</p>
                <p className="text-adan-muted mt-1">
                  {s.tipo === 'testimony' ? 'Testimonio de clientes' : 'Fuente externa'}{s.fuente ? ` · ${s.fuente}` : ''}
                </p>
                <Button size="sm" variant="secondary" className="mt-2" loading={registering === s.afirmacion}
                  onClick={async () => {
                    setRegistering(s.afirmacion)
                    try { await onRegisterEvidence(s) } finally { setRegistering(null) }
                  }}>
                  Registrar como evidencia
                </Button>
              </li>
            ))}
          </ul>
        </div>
      )}
    </aside>
  )
}

export default function ChatPanel({
  messages, sending, discovery, onSend, onRegisterEvidence, onBoardRoom, onDiagnosis, onGateReview,
}: ChatPanelProps) {
  const [input, setInput] = useState('')
  const [showProgress, setShowProgress] = useState(false)
  const endRef = useRef<HTMLDivElement>(null)
  const elapsed = useElapsed(sending)

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, sending])

  const submit = async () => {
    const text = input.trim()
    if (!text || sending) return
    setInput('')
    await onSend(text)
  }

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    await submit()
  }

  // Enter envía; Shift+Enter hace un salto de línea (respuestas largas)
  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey && !e.nativeEvent.isComposing) {
      e.preventDefault()
      void submit()
    }
  }

  return (
    <div className="h-full flex gap-6 max-w-6xl mx-auto p-4">
      <div className="flex-1 min-w-0 flex flex-col">
        {discovery && (
          <button type="button" onClick={() => setShowProgress((v) => !v)} aria-expanded={showProgress}
            className="lg:hidden mb-3 text-left text-sm rounded-xl border border-adan-border bg-adan-surface px-4 py-2">
            Lo que ADÁN ya entendió: <strong>{discovery.done} de {discovery.total}</strong>
            <span className="text-adan-muted"> · {showProgress ? 'ocultar' : 'ver'}</span>
          </button>
        )}
        {discovery && showProgress && (
          <div className="lg:hidden mb-3 max-h-[50vh] overflow-y-auto">
            <DiscoveryPanel discovery={discovery} onRegisterEvidence={onRegisterEvidence} onBoardRoom={onBoardRoom} />
          </div>
        )}

        <div className="flex-1 overflow-y-auto space-y-4 mb-4" aria-live="polite">
          {messages.length === 0 && (
            <EmptyState icon="💬" title="Comienza la conversación">
              Cuéntale a ADÁN sobre el problema que quieres resolver. ADÁN sigue un guion de siete temas y te
              muestra lo que va entendiendo.
            </EmptyState>
          )}
          {messages.map((msg) => (
            <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[85%] rounded-xl px-4 py-3 ${
                msg.role === 'user' ? 'bg-adan-accent text-white' : 'bg-adan-surface border border-adan-border'
              }`}>
                {msg.agent_name && <div className="text-xs font-bold mb-1 text-adan-accent">{msg.agent_name}</div>}
                {msg.role === 'user' ? (
                  <div className="text-sm whitespace-pre-wrap">{msg.content}</div>
                ) : (
                  <div className="text-sm markdown"><ReactMarkdown>{msg.content}</ReactMarkdown></div>
                )}
                {msg.metadata_json?.degraded && (
                  <p className="mt-2 text-xs text-adan-warning" data-testid="degraded-note">
                    ⚠️ Respondió el modelo local de respaldo ({msg.metadata_json.degraded}). La calidad es baja y esta
                    respuesta no avanzó el guion: revisa la clave de Anthropic y vuelve a enviar tu mensaje.
                  </p>
                )}
              </div>
            </div>
          ))}
          {sending && (
            <div className="flex justify-start">
              <div className="bg-adan-surface border border-adan-border rounded-xl px-4 py-3">
                <div className="text-sm text-adan-muted animate-pulse">
                  ADÁN está leyendo tu respuesta…{elapsed >= 5 ? ` (${elapsed} s)` : ''}
                </div>
              </div>
            </div>
          )}
          <div ref={endRef} />
        </div>

        <form onSubmit={handleSubmit} className="flex gap-3 items-end">
          <textarea
            aria-label="Mensaje para ADÁN"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Escribe tu respuesta… (Enter envía, Shift+Enter salto de línea)"
            maxLength={MAX_MESSAGE_CHARS}
            rows={Math.min(6, Math.max(2, input.split('\n').length))}
            className="flex-1 resize-none px-4 py-3 bg-adan-surface border border-adan-border rounded-xl text-adan-text focus:outline-none focus:border-adan-accent"
            disabled={sending}
          />
          <Button type="submit" disabled={sending || !input.trim()}>Enviar</Button>
        </form>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mt-4">
          <Button variant="secondary" className="flex-1" onClick={onBoardRoom}>🏛️ Ejecutar Board Room</Button>
          <Button variant="secondary" className="flex-1" onClick={onDiagnosis}>📋 Generar Diagnóstico</Button>
          <Button variant="secondary" className="flex-1 !border-adan-success/50 !text-adan-success" onClick={onGateReview}>
            ✅ Gate Review
          </Button>
        </div>
      </div>

      {discovery && (
        <div className="hidden lg:block w-80 shrink-0 overflow-y-auto">
          <DiscoveryPanel discovery={discovery} onRegisterEvidence={onRegisterEvidence} onBoardRoom={onBoardRoom} />
        </div>
      )}
    </div>
  )
}
