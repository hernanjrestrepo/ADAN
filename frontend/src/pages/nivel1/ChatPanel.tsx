import { useEffect, useRef, useState, useSyncExternalStore, type FormEvent, type KeyboardEvent, type ReactNode } from 'react'
import MicButton from '../../components/MicButton'
import Portrait from '../../components/Portrait'
import RichMessage from '../../components/RichMessage'
import VoteBadge from '../../components/VoteBadge'
import Button from '../../components/ui/Button'
import { api, errorMessage } from '../../lib/api'
import { waitForResearch } from '../../lib/research'
import { FILE_ICON, pastedFiles } from '../../lib/clipboard'
import type { DiscoveryProgress, Message } from '../../types'
import { reactTo } from '../../universo/react'
import { useUniverso } from '../../universo/store'
import SurveysPanel from './SurveysPanel'
import ToolDialog, { type Tool } from './ToolDialog'

// Una sola sala: la oficina a la izquierda y la conversación a la derecha. Hablas con todo el equipo (responde a quien
// le toca el tema) y, cuando toca, la escena se mueve al Board Room o a La Arena sin salir de la conversación.

export type Scene = 'oficina' | 'board' | 'arena'

interface ChatPanelProps {
  companyId: string
  messages: Message[]
  sending: boolean
  discovery?: DiscoveryProgress
  onSend: (message: string) => Promise<void>
  onReload: () => Promise<void>
  uploading?: boolean
  onUpload?: (files: File[]) => Promise<void>
  onDiagnosis?: () => void
  onClose: () => void
  onError: (message: string) => void
  // Nivel en que se trabaja: define qué espacios se abren (Board desde el 3, Arena en el 5)
  level?: number
  world?: ReactNode
  researching?: boolean
}

const MAX_MESSAGE_CHARS = 8000
const ACCEPTED_DOCS = '.pdf,.docx,.xlsx,.pptx,.txt,.md,.csv,.json,.png,.jpg,.jpeg,.webp,.gif,' +
  '.mp3,.m4a,.wav,.ogg,.opus,.aac,.flac,.amr,.mp4,.mov,.webm,.mkv,.avi,.3gp,image/*,audio/*,video/*'

// Si el mensaje empieza nombrando a alguien del Board, le responde esa persona
const MENTIONS: Record<string, string> = {
  camila: 'CFO', cfo: 'CFO', santiago: 'CMO', cmo: 'CMO', 'lucía': 'Legal', lucia: 'Legal', legal: 'Legal',
  'andrés': 'Producto', andres: 'Producto', producto: 'Producto', 'sofía': 'Operaciones', sofia: 'Operaciones',
  operaciones: 'Operaciones', mateo: 'CTO', cto: 'CTO',
}
function mentioned(text: string): string | null {
  const first = text.trim().toLowerCase().split(/[\s,:;.!¿?]+/)[0] ?? ''
  return MENTIONS[first] ?? null
}

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

// Retrato del personaje de la oficina que habla
function Speaker({ message }: { message: Message }) {
  return <Portrait agent={String(message.metadata_json?.agente ?? 'ceo')} size={36} />
}

const SCENE_CHIP: Record<string, string> = { board: '🏛️ Board Room', arena: '🥊 La Arena' }

// El mundo 3D sigue a la conversación: escena, quién habla y qué siente
function setWorldScene(scene: Scene) {
  if (scene === 'board') {
    useUniverso.setState({
      board: { level: 1, phase: 'decided', step: 0, votes: [], recommendation: 'PIVOT', opening: '', synthesis: '', missing: [], revealsRisk: false },
      arena: null, focusZone: 'board', selected: null,
    })
  } else if (scene === 'arena') {
    useUniverso.setState({ board: null, arena: { phase: 'pitch', step: 0, verdicts: [], passed: false }, focusZone: 'arena', selected: null })
  } else {
    useUniverso.setState({ board: null, arena: null, focusZone: null })
  }
}

export default function ChatPanel({
  companyId, messages, sending, discovery, onSend, onReload, uploading = false, onUpload, onDiagnosis, onClose, onError, world,
  researching = false, level = 1,
}: ChatPanelProps) {
  const [input, setInput] = useState('')
  const desktop = useDesktop()
  const lastScene = (messages[messages.length - 1]?.metadata_json?.escena as Scene | undefined) ?? 'oficina'
  const [scene, setScene] = useState<Scene>(lastScene === 'arena' ? 'oficina' : lastScene)
  const [arenaId, setArenaId] = useState<string | null>(null)
  const [arenaIds, setArenaIds] = useState<string[]>([])
  const [working, setWorking] = useState<'' | 'board' | 'board-talk' | 'arena' | 'arena-answer'>('')
  const [surveys, setSurveys] = useState(false)
  const [continuing, setContinuing] = useState(false)
  const [reason, setReason] = useState('')
  const [tool, setTool] = useState<Tool | null>(null)
  const [toolBusy, setToolBusy] = useState<Tool | null>(null)
  const [logoDone, setLogoDone] = useState<Record<string, 'si' | 'no'>>({})
  const fileInput = useRef<HTMLInputElement>(null)
  const busy = sending || uploading || Boolean(working)
  const pickFiles = () => fileInput.current?.click()
  const [sendingFiles, setSendingFiles] = useState<string[]>([])
  const endRef = useRef<HTMLDivElement>(null)
  const formRef = useRef<HTMLFormElement>(null)
  const elapsed = useElapsed(busy)

  useEffect(() => { setWorldScene(scene) }, [scene])
  useEffect(() => () => setWorldScene('oficina'), [])

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
    if (!desktop) formRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' })
  }, [messages, busy, desktop, researching])

  const upload = async (files: File[]) => {
    if (!onUpload || !files.length) return
    setSendingFiles(files.map((f) => f.name))
    try { await onUpload(files) } finally { setSendingFiles([]) }
  }

  // Cada personaje que habló toma la palabra en la oficina, uno tras otro
  const playSince = (count: number, latest: Message[]) => {
    latest.slice(count).filter((m) => m.role !== 'user').forEach((m, i) => window.setTimeout(() => reactTo(m), i * 2200))
  }

  const runBoard = async () => {
    setScene('board')
    setWorking('board')
    const before = messages.length
    try {
      await api.runBoardRoom(companyId, undefined, level)
      await onReload()
      const status = level > 1 ? await api.getLevelStatus(level, companyId) : await api.getNivel1Status(companyId)
      playSince(before, status.messages)
    } catch (err) {
      onError(errorMessage(err))
    } finally {
      setWorking('')
    }
  }

  const enterArena = async () => {
    setScene('arena')
    setWorking('arena')
    const before = messages.length
    try {
      const session = await api.startArena(companyId, '', level)
      setArenaId(session.id)
      setArenaIds(session.investors.map((i) => i.id))
      await onReload()
      const status = level > 1 ? await api.getLevelStatus(level, companyId) : await api.getNivel1Status(companyId)
      playSince(before, status.messages)
    } catch (err) {
      onError(errorMessage(err))
      setScene('oficina')
    } finally {
      setWorking('')
    }
  }

  const continueAnyway = async () => {
    setWorking('board-talk')
    try {
      await api.continueDespiteBoard(companyId, reason.trim(), level)
      setContinuing(false)
      setReason('')
      await onReload()
    } catch (err) {
      onError(errorMessage(err))
    } finally {
      setWorking('')
    }
  }

  const submit = async () => {
    const text = input.trim()
    if (!text || busy) return
    setInput('')
    const before = messages.length + 1
    if (scene === 'board') {
      setWorking('board-talk')
      try {
        await api.talkToBoard(companyId, text, mentioned(text), level)
        await onReload()
        playSince(before, (level > 1 ? await api.getLevelStatus(level, companyId) : await api.getNivel1Status(companyId)).messages)
      } catch (err) {
        setInput(text)
        onError(errorMessage(err))
      } finally {
        setWorking('')
      }
    } else if (scene === 'arena' && arenaId) {
      setWorking('arena-answer')
      try {
        await api.answerArena(companyId, arenaId, Object.fromEntries(arenaIds.map((id) => [id, text])), level)
        setArenaId(null)
        await onReload()
        playSince(before, (level > 1 ? await api.getLevelStatus(level, companyId) : await api.getNivel1Status(companyId)).messages)
      } catch (err) {
        setInput(text)
        onError(errorMessage(err))
      } finally {
        setWorking('')
      }
    } else {
      // En la oficina: ADÁN se acerca y saluda mientras el equipo piensa la respuesta
      if (scene !== 'oficina') setScene('oficina')
      const u = useUniverso.getState()
      u.select('ceo')
      u.feel('ceo', 'feliz', 3000)
      u.say('ceo', '👋 Te escucho…', 2500)
      await onSend(text)
    }
  }

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    await submit()
  }

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey && !e.nativeEvent.isComposing) {
      e.preventDefault()
      void submit()
    }
  }

  const lastAssistantId = [...messages].reverse().find((m) => m.role !== 'user')?.id
  const lastWork = [...messages].reverse().find((m) => m.role !== 'user')?.metadata_json?.trabajando
  const workText = lastWork?.tipo === 'recorrido' ? '🧭 Andrés está recorriendo la página con clics; te cuenta aquí lo que encuentre.'
    : lastWork?.tipo === 'repositorio' ? '💻 Mateo está leyendo tu código; su revisión llega aquí en un par de minutos.'
      : '🔎 El equipo está investigando en internet; los datos te llegan aquí en un momento. Puedes seguir escribiendo.'

  const adoptLogo = async (id: string, url: string) => {
    try {
      await api.adoptExistingLogo(companyId, { url })
      setLogoDone((d) => ({ ...d, [id]: 'si' }))
      window.dispatchEvent(new Event('adan-identidad'))
    } catch (err) {
      onError(errorMessage(err))
    }
  }

  // Recorrido con clics o revisión de código: corren aparte y la respuesta llega como mensaje nuevo
  const startTool = async (kind: Tool, data: Record<string, string>) => {
    setTool(null)
    setToolBusy(kind)
    const before = messages.length
    try {
      const res = kind === 'recorrido'
        ? await api.startWalk(companyId, { url: data.url ?? '', objetivo: data.objetivo ?? '', usuario: data.usuario, clave: data.clave, nivel: level })
        : await api.startCodeReview(companyId, { url: data.url ?? '', objetivo: data.objetivo, token: data.token, nivel: level })
      await onReload()
      const latest = await waitForResearch(companyId, res.after, 300_000, level)
      await onReload()
      if (latest) playSince(before + 1, latest)
    } catch (err) {
      onError(errorMessage(err))
    } finally {
      setToolBusy(null)
    }
  }

  const waiting = working === 'board' ? 'El Board está deliberando: cada especialista revisa tu empresa (uno o dos minutos)…'
    : working === 'board-talk' ? 'El Board está pensando su respuesta…'
      : working === 'arena' ? 'Los inversionistas están revisando tu empresa…'
        : working === 'arena-answer' ? 'Los inversionistas están decidiendo…'
          : uploading ? 'ADÁN está leyendo lo que cargaste…' : 'El equipo está pensando tu respuesta…'
  const placeholder = scene === 'board' ? 'Respóndele al Board (a todos, o «Camila, …» a uno)…'
    : scene === 'arena' ? (arenaId ? 'Responde a los inversionistas con datos…' : 'La Arena terminó. Vuelve a la oficina o entra de nuevo.')
      : 'Escribe, dicta 🎤 o pega una captura (Ctrl+V). Enter envía.'

  const chat = (
    <div className="flex-1 min-w-0 min-h-0 flex flex-col">
      {/* Avance del guion: siete puntos, sin ocupar espacio */}
      <div className="mb-2 flex items-center gap-2 text-xs text-adan-muted">
        <span className={`rounded-full px-2 py-0.5 font-semibold ${scene === 'oficina' ? 'bg-adan-surface' : 'bg-adan-accent/20 text-adan-accent'}`}>
          {scene === 'board' ? '🏛️ Board Room' : scene === 'arena' ? '🥊 La Arena' : '🏢 Oficina'}
        </span>
        {discovery && (
          <span className="flex items-center gap-1" title="Temas del Nivel 1 que el equipo ya entendió">
            {discovery.topics.map((t) => (
              <span key={t.id} title={t.label}
                className={`h-2 w-2 rounded-full ${t.estado === 'respondido' ? 'bg-adan-success' : t.estado === 'pendiente' ? 'bg-adan-border' : 'bg-adan-warning'}`} />
            ))}
            <span className="ml-1">{discovery.done}/7</span>
          </span>
        )}
        {scene !== 'oficina' && (
          <button type="button" onClick={() => setScene('oficina')} className="ml-auto rounded-full border border-adan-border px-2 py-0.5 hover:border-adan-accent">
            🏢 Volver a la oficina
          </button>
        )}
      </div>

      <div className="flex-1 min-h-0 max-lg:min-h-[45vh] max-lg:max-h-[60vh] overflow-y-auto space-y-3 mb-3 pr-1" aria-live="polite">
        {onUpload && messages.length < 4 && !uploading && (
          <button type="button" onClick={pickFiles} data-testid="upload-invite"
            className="w-full rounded-xl border border-dashed border-adan-accent/50 bg-adan-accent/5 p-3 text-left text-sm hover:bg-adan-accent/10">
            📎 <b>¿Tienes documentos, capturas, audios o videos?</b> Súbelos o pega una captura con Ctrl+V: el equipo aprende de ellos.
          </button>
        )}
        {messages.map((msg) => {
          const user = msg.role === 'user'
          const sceneChip = SCENE_CHIP[String(msg.metadata_json?.escena ?? '')]
          const vote = msg.metadata_json?.voto as 'PROCEED' | 'PIVOT' | 'STOP' | undefined
          return (
            <div key={msg.id} className={`flex gap-2 ${user ? 'justify-end' : 'justify-start'}`}>
              {!user && <Speaker message={msg} />}
              <div className={`max-w-[85%] rounded-xl px-4 py-3 ${user ? 'bg-adan-accent text-white' : 'bg-adan-surface border border-adan-border cursor-pointer hover:border-adan-accent/60'}`}
                onClick={user ? undefined : (e) => { if (!(e.target as HTMLElement).closest('a,button')) reactTo(msg) }}
                title={user ? undefined : 'Clic: que lo diga en la oficina'}>
                {!user && (
                  <div className="mb-1 flex flex-wrap items-center gap-2 text-xs">
                    <b className="text-adan-accent">{msg.agent_name ?? 'ADÁN'}</b>
                    {sceneChip && <span className="text-adan-muted">{sceneChip}</span>}
                    {vote && <VoteBadge vote={vote} />}
                  </div>
                )}
                {user ? <div className="text-sm whitespace-pre-wrap">{msg.content}</div>
                  : <div className="text-sm markdown"><RichMessage text={msg.content} /></div>}
                {!user && msg.metadata_json?.logo_sugerido && !logoDone[msg.id] && (
                  <div className="mt-3 flex flex-wrap items-center gap-3 rounded-xl border border-adan-border bg-white p-2" data-testid="logo-sugerido">
                    <img src={msg.metadata_json.logo_sugerido.url} alt="Logo encontrado en tu web" className="h-14 max-w-[160px] object-contain" />
                    <div className="flex gap-2">
                      <Button size="sm" onClick={() => adoptLogo(msg.id, msg.metadata_json!.logo_sugerido!.url)}>✅ Sí, es mi logo</Button>
                      <Button size="sm" variant="ghost" className="text-slate-600!" onClick={() => setLogoDone((d) => ({ ...d, [msg.id]: 'no' }))}>No es</Button>
                    </div>
                  </div>
                )}
                {!user && logoDone[msg.id] === 'si' && <p className="mt-2 text-xs text-adan-success">✓ Logo adoptado: ya brilla en tu oficina y en la Biblioteca.</p>}
                {!user && msg.metadata_json?.propone_cierre && msg.id === lastAssistantId && (
                  <div className="mt-3 flex flex-wrap gap-2" data-testid="propone-cierre">
                    <Button size="sm" variant="success" onClick={onClose} disabled={busy}>✅ Sí, cerramos el Nivel</Button>
                    <Button size="sm" variant="secondary" onClick={() => void onSend('Todavía no; antes quiero ajustar algo.')} disabled={busy}>Todavía no</Button>
                  </div>
                )}
                {msg.metadata_json?.degraded && (
                  <p className="mt-2 text-xs text-adan-warning" data-testid="degraded-note">
                    ⚠️ Respondió el modelo local de respaldo ({msg.metadata_json.degraded}); vuelve a enviar tu mensaje.
                  </p>
                )}
              </div>
            </div>
          )
        })}
        {sendingFiles.length > 0 && (
          <div className="flex justify-end" data-testid="sending-files">
            <div className="flex max-w-[85%] flex-wrap gap-2 rounded-xl bg-adan-accent/80 px-3 py-2 text-sm text-white">
              {sendingFiles.map((n) => <span key={n} className="rounded-lg bg-white/15 px-2 py-0.5">{FILE_ICON(n)} {n}</span>)}
            </div>
          </div>
        )}
        {busy && (
          <div className="flex justify-start">
            <div className="bg-adan-surface border border-adan-border rounded-xl px-4 py-3 text-sm text-adan-muted animate-pulse">
              {waiting}{elapsed >= 5 ? ` (${elapsed} s)` : ''}
            </div>
          </div>
        )}
        {toolBusy && (
          <div className="flex justify-start" data-testid="tool-working">
            <div className="rounded-xl border border-adan-accent/40 bg-adan-accent/5 px-4 py-3 text-sm animate-pulse">
              {toolBusy === 'recorrido' ? '🧭 Andrés está recorriendo la página con clics (uno o dos minutos)…' : '💻 Mateo está leyendo el código (uno o dos minutos)…'}
            </div>
          </div>
        )}
        {researching && !busy && (
          <div className="flex justify-start" data-testid="researching">
            <div className="rounded-xl border border-adan-accent/40 bg-adan-accent/5 px-4 py-3 text-sm animate-pulse">
              {workText}
            </div>
          </div>
        )}
        <div ref={endRef} />
      </div>

      {continuing && (
        <div className="mb-2 rounded-xl border border-adan-warning/40 bg-adan-warning/5 p-3 text-sm space-y-2" data-testid="continue-anyway">
          <p className="text-adan-muted">¿Por qué decides seguir? Queda en el acta con las objeciones abiertas y baja la calificación de la empresa.</p>
          <textarea value={reason} onChange={(e) => setReason(e.target.value)} rows={2} maxLength={2000} aria-label="Motivo para continuar"
            className="w-full rounded-xl border border-adan-border bg-adan-bg px-3 py-2" placeholder="Ya expliqué los temas; el mercado solo se valida lanzando…" />
          <div className="flex gap-2">
            <Button size="sm" onClick={continueAnyway} disabled={reason.trim().length < 3 || busy}>Continuar bajo mi responsabilidad</Button>
            <Button size="sm" variant="ghost" onClick={() => setContinuing(false)}>Cancelar</Button>
          </div>
        </div>
      )}

      <form ref={formRef} onSubmit={handleSubmit} className="flex gap-2 items-end">
        <textarea aria-label="Mensaje para ADÁN" value={input} onChange={(e) => setInput(e.target.value)} onKeyDown={handleKeyDown}
          onPaste={(e) => { const files = pastedFiles(e); if (files.length && onUpload) { e.preventDefault(); void upload(files) } }}
          placeholder={placeholder} maxLength={MAX_MESSAGE_CHARS} rows={Math.min(6, Math.max(2, input.split('\n').length))}
          disabled={busy || (scene === 'arena' && !arenaId)}
          className="flex-1 resize-none px-4 py-3 bg-adan-surface border border-adan-border rounded-xl text-adan-text focus:outline-hidden focus:border-adan-accent" />
        {onUpload && (
          <>
            <input ref={fileInput} type="file" multiple accept={ACCEPTED_DOCS} className="hidden" data-testid="upload-input" aria-label="Cargar documentos"
              onChange={async (e) => { const files = Array.from(e.target.files ?? []); e.target.value = ''; await upload(files) }} />
            <Button type="button" variant="secondary" onClick={pickFiles} disabled={busy} title="Cargar documentos, imágenes, audio o video">📎</Button>
          </>
        )}
        <MicButton onText={(t) => setInput((v) => (v ? `${v} ${t}` : t))} disabled={busy}
          className="px-3 py-3 rounded-xl border border-adan-border bg-adan-surface hover:border-adan-accent disabled:opacity-40" />
        <Button type="submit" disabled={busy || !input.trim()}>Enviar</Button>
      </form>

      <div className="mt-2 flex flex-wrap gap-2 text-sm">
        {/* Metodología: el Board entra desde el Nivel 3 y La Arena en el 5; el Nivel 1 se valida con encuestas */}
        <Button size="sm" onClick={() => setSurveys(true)} disabled={busy}>🧪 Validar con encuesta simulada</Button>
        {level >= 3 && (
          <Button size="sm" variant="secondary" onClick={runBoard} disabled={busy}>🏛️ {scene === 'board' ? 'Nueva sesión del Board' : 'Board Room'}</Button>
        )}
        {scene === 'board' && (
          <Button size="sm" variant="secondary" onClick={() => setContinuing(true)} disabled={busy}>⚖️ Continuar bajo mi responsabilidad</Button>
        )}
        {level >= 5 && <Button size="sm" variant="secondary" onClick={enterArena} disabled={busy}>🥊 La Arena</Button>}
        <Button size="sm" variant="secondary" onClick={() => setTool('recorrido')} disabled={busy || Boolean(toolBusy)}>🧭 Recorrer una página</Button>
        <Button size="sm" variant="secondary" onClick={() => setTool('repositorio')} disabled={busy || Boolean(toolBusy)}>💻 Revisar código</Button>
        {onDiagnosis && <Button size="sm" variant="secondary" onClick={onDiagnosis} disabled={busy}>📄 Diagnóstico</Button>}
        <Button size="sm" variant="secondary" className="border-adan-success/50! text-adan-success!" onClick={onClose} disabled={busy}>✅ Cerrar el Nivel</Button>
      </div>

      {tool && <ToolDialog tool={tool} onCancel={() => setTool(null)} onStart={startTool} />}
      {surveys && (
        <div className="fixed inset-0 z-50 flex items-start justify-center bg-black/60 p-3 overflow-y-auto" role="dialog" aria-label="Encuesta">
          <div className="w-full max-w-3xl rounded-2xl border border-adan-border bg-adan-bg">
            <div className="flex items-center justify-between border-b border-adan-border px-4 py-3">
              <p className="font-bold">🧪 Validar con el Simulador de Mercado</p>
              <button type="button" onClick={() => setSurveys(false)} aria-label="Cerrar" className="text-adan-muted hover:text-adan-text">✕</button>
            </div>
            <SurveysPanel companyId={companyId} onError={onError} onChanged={() => void onReload()} simulatedOnly />
          </div>
        </div>
      )}
    </div>
  )

  return (
    <div className="h-full min-h-0 flex flex-col lg:flex-row gap-4 max-w-[1800px] mx-auto p-3 sm:p-4">
      {world && (desktop
        ? <div className="flex-[1.35] min-w-0 min-h-0">{world}</div>
        : <div className="h-[30vh] shrink-0">{world}</div>)}
      <div className={`${world && desktop ? 'w-[42%] max-w-[760px]' : 'flex-1'} min-h-0 flex flex-col`}>{chat}</div>
    </div>
  )
}
