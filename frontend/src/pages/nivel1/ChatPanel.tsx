import { useEffect, useRef, useState, useSyncExternalStore, type FormEvent, type KeyboardEvent, type ReactNode } from 'react'
import RichMessage from '../../components/RichMessage'
import Badge from '../../components/ui/Badge'
import { FILE_ICON, pastedFiles } from '../../lib/clipboard'
import Button from '../../components/ui/Button'
import MicButton from '../../components/MicButton'
import { EmptyState } from '../../components/ui/States'
import type { DiscoveryProgress, DiscoveryTopic, Message } from '../../types'

interface ChatPanelProps {
  messages: Message[]
  sending: boolean
  discovery?: DiscoveryProgress
  onSend: (message: string) => Promise<void>
  uploading?: boolean
  onUpload?: (files: File[]) => Promise<void>
  onBoardRoom: () => void
  onDiagnosis: () => void
  onGateReview: () => void
  world?: ReactNode
  researching?: boolean
}

const MAX_MESSAGE_CHARS = 8000  // mismo límite que el backend (WO-097)
const ACCEPTED_DOCS = '.pdf,.docx,.xlsx,.pptx,.txt,.md,.csv,.json,.png,.jpg,.jpeg,.webp,.gif,.mp3,.m4a,.wav,.ogg,.opus,.aac,.flac,.amr,.mp4,.mov,.webm,.mkv,.avi,.3gp,image/*,audio/*,video/*'

const TOPIC_ICON: Record<DiscoveryTopic['estado'], { icon: string; label: string; className: string }> = {
  respondido: { icon: '✓', label: 'Entendido', className: 'bg-adan-success/20 text-adan-success' },
  parcial: { icon: '◐', label: 'Falta precisar', className: 'bg-yellow-500/20 text-yellow-400' },
  sin_dato: { icon: '?', label: 'Sin dato: por validar', className: 'bg-gray-500/20 text-gray-300' },
  pendiente: { icon: '○', label: 'Pendiente', className: 'bg-adan-bg text-adan-muted' },
}

// Escritorio o celular: la oficina 3D se dibuja una sola vez, al lado (escritorio) o arriba (celular)
const DESKTOP = '(min-width: 1024px)'
function useDesktop() {
  return useSyncExternalStore(
    (cb) => { const m = window.matchMedia(DESKTOP); m.addEventListener('change', cb); return () => m.removeEventListener('change', cb) },
    () => window.matchMedia(DESKTOP).matches,
  )
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
function DiscoveryPanel({ discovery, onBoardRoom }: {
  discovery: DiscoveryProgress
  onBoardRoom: () => void
}) {
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

      <p className="rounded-xl border border-adan-border bg-adan-surface p-3 text-xs text-adan-muted">
        ✓ La evidencia que mencionas o que ADÁN encuentra investigando se registra sola. La ves completa en la pestaña
        Evidencia.
      </p>
    </aside>
  )
}

export default function ChatPanel({
  messages, sending, discovery, onSend, onBoardRoom, onDiagnosis, onGateReview, uploading = false, onUpload, world, researching = false,
}: ChatPanelProps) {
  const [input, setInput] = useState('')
  const desktop = useDesktop()
  const fileInput = useRef<HTMLInputElement>(null)
  const busy = sending || uploading
  const pickFiles = () => fileInput.current?.click()
  // Lo que se está cargando se ve de inmediato, con su ícono
  const [sendingFiles, setSendingFiles] = useState<string[]>([])
  const upload = async (files: File[]) => {
    if (!onUpload || !files.length) return
    setSendingFiles(files.map((f) => f.name))
    try { await onUpload(files) } finally { setSendingFiles([]) }
  }
  const [showProgress, setShowProgress] = useState(false)
  const endRef = useRef<HTMLDivElement>(null)
  const formRef = useRef<HTMLFormElement>(null)
  const elapsed = useElapsed(busy)

  useEffect(() => {
    // El último mensaje y la caja de texto siempre a la vista (en el celular la página baja hasta la caja)
    endRef.current?.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
    if (!desktop) formRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' })
  }, [messages, busy, desktop, researching])

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
    <div className="h-full min-h-0 flex flex-col lg:flex-row gap-4 max-w-[1600px] mx-auto p-3 sm:p-4">
      {world && !desktop && <div className="h-[30vh] shrink-0">{world}</div>}
      <div className="flex-1 min-w-0 min-h-0 flex flex-col">
        {discovery && (
          <button type="button" onClick={() => setShowProgress((v) => !v)} aria-expanded={showProgress}
            className="lg:hidden mb-3 text-left text-sm rounded-xl border border-adan-border bg-adan-surface px-4 py-2">
            Lo que ADÁN ya entendió: <strong>{discovery.done} de {discovery.total}</strong>
            <span className="text-adan-muted"> · {showProgress ? 'ocultar' : 'ver'}</span>
          </button>
        )}
        {discovery && showProgress && (
          <div className="lg:hidden mb-3 max-h-[50vh] overflow-y-auto">
            <DiscoveryPanel discovery={discovery} onBoardRoom={onBoardRoom} />
          </div>
        )}

        <div className="flex-1 min-h-0 max-lg:min-h-[45vh] max-lg:max-h-[60vh] overflow-y-auto space-y-4 mb-3 pr-1" aria-live="polite">
          {messages.length === 0 && (
            <EmptyState icon="💬" title="Comienza la conversación">
              Cuéntale a ADÁN sobre el problema que quieres resolver. ADÁN sigue un guion de siete temas y te
              muestra lo que va entendiendo.
            </EmptyState>
          )}
          {onUpload && messages.length < 4 && !uploading && (
            <button type="button" onClick={pickFiles} data-testid="upload-invite"
              className="w-full rounded-xl border border-dashed border-adan-accent/50 bg-adan-accent/5 p-4 text-left hover:bg-adan-accent/10">
              <p className="text-sm font-semibold">📎 ¿Ya tienes documentos? Súbelos y ADÁN aprende de tu idea o de tu empresa</p>
              <p className="text-xs text-adan-muted mt-1">
                Plan de negocio, estados financieros, presentaciones, actas, capturas de pantalla, fotos, grabaciones de audio o
                video… (hasta 10 archivos; documentos e imágenes de 15 MB, audio y video de 50 MB). También puedes pegar una
                captura con Ctrl+V. ADÁN distingue lo que está respaldado de lo que es supuesto.
              </p>
            </button>
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
                  <div className="text-sm markdown"><RichMessage text={msg.content} /></div>
                )}
                {msg.metadata_json?.degraded && (
                  <p className="mt-2 text-xs text-adan-warning" data-testid="degraded-note">
                    ⚠️ Respondió el modelo local de respaldo ({msg.metadata_json.degraded}). La calidad es baja y esta
                    respuesta no avanzó el guion: el modelo principal (Claude o Kimi) no respondió; vuelve a enviar tu mensaje.
                  </p>
                )}
              </div>
            </div>
          ))}
          {sendingFiles.length > 0 && (
            <div className="flex justify-end" data-testid="sending-files">
              <div className="flex max-w-[85%] flex-wrap gap-2 rounded-xl bg-adan-accent/80 px-3 py-2 text-sm text-white">
                {sendingFiles.map((n) => <span key={n} className="rounded-lg bg-white/15 px-2 py-0.5">{FILE_ICON(n)} {n}</span>)}
              </div>
            </div>
          )}
          {busy && (
            <div className="flex justify-start">
              <div className="bg-adan-surface border border-adan-border rounded-xl px-4 py-3">
                <div className="text-sm text-adan-muted animate-pulse">
                  {uploading ? 'ADÁN está leyendo lo que cargaste' : 'ADÁN está pensando tu respuesta'}…{elapsed >= 5 ? ` (${elapsed} s)` : ''}
                </div>
              </div>
            </div>
          )}
          {researching && !busy && (
            <div className="flex justify-start" data-testid="researching">
              <div className="rounded-xl border border-adan-accent/40 bg-adan-accent/5 px-4 py-3 text-sm animate-pulse">
                🔎 ADÁN está investigando en internet; los datos te llegan aquí en un momento. Puedes seguir escribiendo.
              </div>
            </div>
          )}
          <div ref={endRef} />
        </div>

        <form ref={formRef} onSubmit={handleSubmit} className="flex gap-3 items-end">
          <textarea
            aria-label="Mensaje para ADÁN"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            onPaste={(e) => {
              const files = pastedFiles(e)
              if (files.length && onUpload) {
                e.preventDefault()
                void upload(files)
              }
            }}
            placeholder="Escribe, dicta 🎤 o pega una captura (Ctrl+V). Enter envía."
            maxLength={MAX_MESSAGE_CHARS}
            rows={Math.min(6, Math.max(2, input.split('\n').length))}
            className="flex-1 resize-none px-4 py-3 bg-adan-surface border border-adan-border rounded-xl text-adan-text focus:outline-hidden focus:border-adan-accent"
            disabled={busy}
          />
          {onUpload && (
            <>
              <input ref={fileInput} type="file" multiple accept={ACCEPTED_DOCS} className="hidden" data-testid="upload-input"
                aria-label="Cargar documentos"
                onChange={async (e) => {
                  const files = Array.from(e.target.files ?? [])
                  e.target.value = ''
                  await upload(files)
                }} />
              <Button type="button" variant="secondary" onClick={pickFiles} disabled={busy} title="Cargar documentos, imágenes, audio o video">📎</Button>
            </>
          )}
          <MicButton onText={(t) => setInput((v) => (v ? `${v} ${t}` : t))} disabled={busy}
            className="px-3 py-3 rounded-xl border border-adan-border bg-adan-surface hover:border-adan-accent disabled:opacity-40" />
          <Button type="submit" disabled={busy || !input.trim()}>Enviar</Button>
        </form>

        <div className="grid grid-cols-3 gap-2 mt-3 text-sm">
          <Button variant="secondary" className="flex-1" onClick={onBoardRoom}>🏛️ Ejecutar Board Room</Button>
          <Button variant="secondary" className="flex-1" onClick={onDiagnosis}>📋 Generar Diagnóstico</Button>
          <Button variant="secondary" className="flex-1 border-adan-success/50! text-adan-success!" onClick={onGateReview}>
            ✅ Gate Review
          </Button>
        </div>
      </div>

      {(world || discovery) && (
        <div className="hidden lg:flex w-[44%] max-w-[720px] shrink-0 min-h-0 flex-col gap-3">
          {world && desktop && <div className="flex-1 min-h-[280px]">{world}</div>}
          {discovery && (
            <div className={`${world ? 'max-h-[42%]' : 'flex-1'} min-h-0 overflow-y-auto`}>
              <DiscoveryPanel discovery={discovery} onBoardRoom={onBoardRoom} />
            </div>
          )}
        </div>
      )}
    </div>
  )
}
