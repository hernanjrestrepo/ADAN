import { useCallback, useEffect, useRef, useState, type FormEvent } from 'react'
import { Link } from 'react-router'
import { useAuth } from '../../auth/context'
import { AdanMark } from '../../components/Logo'
import MicButton from '../../components/MicButton'
import { pastedFiles } from '../../lib/clipboard'
import RichMessage from '../../components/RichMessage'
import { waitForResearch } from '../../lib/research'
import { reactTo } from '../react'
import { useUniverso } from '../store'
import { api, errorMessage } from '../../lib/api'
import type { Company, Message } from '../../types'

// ADAN, el CEO, lleva el control desde que entras: saluda, explica el proceso, aclara lo de la cuenta y empieza a
// conocer a la persona, la empresa y los socios. Con sesión iniciada conversa de verdad (el guion del Nivel 1),
// lee los documentos que subas y te deja hablar por micrófono.

const COMPANY_KEY = 'adan-universo-company'
const ACCEPTED_DOCS = '.pdf,.docx,.xlsx,.pptx,.txt,.md,.csv,.json,.png,.jpg,.jpeg,.webp,.gif,.mp3,.m4a,.wav,.ogg,.opus,.aac,.flac,.amr,.mp4,.mov,.webm,.mkv,.avi,.3gp,image/*,audio/*,video/*'

interface Line { id: string; from: 'adan' | 'tu'; text: string }

const PROCESO = `Hola, ¿cómo estás? Soy **ADAN**, el CEO de tu equipo directivo de inteligencia artificial. Así vamos a trabajar:

1. **Te conozco a ti, a tu empresa y a tus socios.** Te hago preguntas una por una y, si tienes documentos (plan de negocio, estados financieros, presentaciones, actas), los subes con 📎 y yo los leo.
2. **Recorremos 7 Niveles**, del dolor del cliente al escalamiento. En cada uno mi equipo trabaja y te entrega un reporte.
3. **El Board Room vota con evidencia.** No pasas de Nivel hasta que esté blindado; en el Nivel 5 te toca convencer a 4 inversionistas en **La Arena**.
4. **Tú decides siempre.** Yo te digo la verdad, aunque no guste: 9 de cada 10 empresas cierran en 5 años y vinimos a que la tuya no sea una de ellas.

Puedes escribir o hablar con 🎤. ¿Tienes alguna pregunta antes de empezar?`

function readCompany(): string | null {
  try {
    return localStorage.getItem(COMPANY_KEY)
  } catch {
    return null
  }
}

function rememberCompany(id: string | null): void {
  try {
    if (id) localStorage.setItem(COMPANY_KEY, id)
    else localStorage.removeItem(COMPANY_KEY)
  } catch {
    // sin almacenamiento: se vuelve a elegir la empresa la próxima vez
  }
}

function toLines(messages: Message[]): Line[] {
  return messages
    .filter((m) => m.role === 'user' || m.role === 'assistant' || m.role === 'agent')
    .map((m) => ({ id: m.id, from: m.role === 'user' ? 'tu' : 'adan', text: m.content }))
}

export default function AdanChat({ open, onToggle }: { open: boolean; onToggle: () => void }) {
  const { user } = useAuth()
  const [companies, setCompanies] = useState<Company[] | null>(null)
  const [companyId, setCompanyId] = useState<string | null>(readCompany)
  const [conversationId, setConversationId] = useState<string | undefined>()
  const [lines, setLines] = useState<Line[]>([])
  const [input, setInput] = useState('')
  const [busy, setBusy] = useState<'' | 'pensando' | 'leyendo' | 'cargando'>('')
  const [error, setError] = useState<string | null>(null)
  const [newName, setNewName] = useState('')
  const [stage, setStage] = useState<'idea' | 'existing'>('idea')
  const fileInput = useRef<HTMLInputElement>(null)
  const endRef = useRef<HTMLDivElement>(null)

  // Empresas de la persona
  useEffect(() => {
    if (!user) return
    let cancelled = false
    api.getCompanies()
      .then((list) => {
        if (cancelled) return
        setCompanies(list)
        setCompanyId((current) => (current && list.some((c) => c.id === current) ? current : list.length === 1 ? (list[0]?.id ?? null) : null))
      })
      .catch((err: unknown) => { if (!cancelled) setError(errorMessage(err)) })
    return () => { cancelled = true }
  }, [user])

  // Trae la conversación del Nivel 1 de la empresa (solo actualiza el estado cuando responde el servidor)
  const fetchConversation = useCallback((id: string) => api.getNivel1Status(id)
    .then((status) => {
      setConversationId(status.conversation?.id)
      setLines(toLines(status.messages))
    })
    .catch((err: unknown) => setError(errorMessage(err))), [])

  useEffect(() => {
    rememberCompany(companyId)
    if (user && companyId) void fetchConversation(companyId).finally(() => setBusy(''))
  }, [user, companyId, fetchConversation])

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [lines, busy, open])

  const createCompany = async (e: FormEvent) => {
    e.preventDefault()
    if (!newName.trim()) return
    setBusy('cargando')
    setError(null)
    try {
      const { company_id } = await api.startOnboarding(newName.trim(), stage)
      setCompanies((prev) => [...(prev ?? []), { id: company_id, name: newName.trim() } as Company])
      setCompanyId(company_id)
      setNewName('')
      setBusy('cargando')
    } catch (err) {
      setError(errorMessage(err))
      setBusy('')
    }
  }

  const send = async (e?: FormEvent) => {
    e?.preventDefault()
    const text = input.trim()
    if (!text || !companyId || busy) return
    setInput('')
    setError(null)
    const tempId = `t-${lines.length}-${text.length}`
    setLines((prev) => [...prev, { id: tempId, from: 'tu', text }])
    setBusy('pensando')
    useUniverso.getState().feel('ceo', 'pensando', 60000)
    try {
      const data = await api.chat(companyId, text, conversationId)
      setConversationId(data.conversation_id)
      setLines((prev) => [...prev, { id: data.message.id, from: 'adan', text: data.message.content }])
      reactTo(data.message)
      if (data.message.metadata_json?.investigando) {
        useUniverso.getState().say('csi', '🔎 Voy a investigar eso en internet…', 6000, 'info')
        useUniverso.getState().feel('csi', 'pensando', 60000)
        const cid = companyId
        void waitForResearch(cid, data.message.id).then((msgs) => {
          if (!msgs) return
          setLines(toLines(msgs))
          const found = msgs[msgs.length - 1]
          if (found) reactTo(found)
        })
      }
    } catch (err) {
      setLines((prev) => prev.filter((l) => l.id !== tempId))
      setInput(text)
      setError(errorMessage(err))
    } finally {
      setBusy('')
    }
  }

  const upload = async (files: File[]) => {
    if (!companyId || files.length === 0) return
    setBusy('leyendo')
    setError(null)
    try {
      const result = await api.uploadDocuments(companyId, files)
      if (result.errors.length) setError(result.errors.join(' '))
      await fetchConversation(companyId)
    } catch (err) {
      setError(errorMessage(err))
    } finally {
      setBusy('')
    }
  }

  const company = companies?.find((c) => c.id === companyId)

  if (!open) {
    return (
      <button type="button" onClick={onToggle} aria-label="Hablar con ADAN"
        className="u-no-print u-glass u-pulse fixed z-40 bottom-12 right-4 flex items-center gap-2 rounded-full py-2 pl-2 pr-4 text-sm font-bold">
        <AdanMark size={34} /> Hablar con ADAN
      </button>
    )
  }

  return (
    <section aria-label="Conversación con ADAN"
      className="u-no-print u-glass u-rise fixed z-40 flex flex-col rounded-3xl inset-x-1 bottom-10 h-[52dvh] md:h-auto md:inset-x-auto md:right-3 md:top-32 2xl:top-20 md:bottom-12 md:w-[420px]">
      <header className="flex items-center gap-3 border-b border-white/10 px-4 py-3">
        <AdanMark size={38} />
        <div className="min-w-0 flex-1 leading-tight">
          <p className="font-bold">ADAN <span className="text-xs font-normal text-slate-400">· CEO de tu equipo</span></p>
          <p className="truncate text-[11px] text-slate-400">
            {user ? (company ? `Trabajando en ${company.name}` : `Sesión de ${user.name.split(' ')[0]}`) : 'Sin sesión: modo demostración'}
          </p>
        </div>
        <button type="button" onClick={onToggle} aria-label="Minimizar" className="rounded-lg px-2 py-1 text-slate-400 hover:bg-white/10">—</button>
      </header>

      <div className="flex-1 min-h-0 overflow-y-auto u-scroll space-y-3 px-4 py-4 text-sm" aria-live="polite">
        <Bubble from="adan" text={PROCESO} />

        {!user && (
          <div className="rounded-2xl border border-cyan-300/30 bg-cyan-400/5 p-3">
            <p><b>Sobre tu usuario:</b> para que trabaje con <b>tu empresa real</b> (guardar lo que me cuentes, leer tus documentos y
              hacer los reportes) necesitas una cuenta. Toma un minuto y es gratis.</p>
            <div className="mt-3 flex flex-wrap gap-2">
              <Link to="/register?next=/universo" className="rounded-xl u-cta px-4 py-2 text-xs font-bold">Crear mi cuenta</Link>
              <Link to="/login?next=/universo" className="rounded-xl bg-white/10 px-4 py-2 text-xs font-semibold hover:bg-white/20">Ya tengo cuenta</Link>
            </div>
            <p className="mt-2 text-xs text-slate-400">Mientras tanto puedes recorrer la oficina con una empresa de ejemplo.</p>
          </div>
        )}

        {user && companies && !companyId && (
          <div className="rounded-2xl border border-white/10 p-3 space-y-3">
            {companies.length > 0 && (
              <div>
                <p>¿Con cuál empresa trabajamos hoy?</p>
                <div className="mt-2 flex flex-wrap gap-2">
                  {companies.map((c) => (
                    <button key={c.id} type="button" onClick={() => { setBusy('cargando'); setCompanyId(c.id) }}
                      className="rounded-xl bg-white/10 px-3 py-1.5 text-xs font-semibold hover:bg-white/20">{c.name}</button>
                  ))}
                </div>
              </div>
            )}
            <form onSubmit={createCompany} className="space-y-2">
              <p>{companies.length > 0 ? 'O empecemos una nueva:' : 'Empecemos. ¿Cómo se llama tu empresa o tu idea?'}</p>
              <input value={newName} onChange={(e) => setNewName(e.target.value)} maxLength={255} placeholder="Ej.: Café Andino"
                className="w-full rounded-xl border border-white/10 bg-black/30 px-3 py-2 outline-none focus:border-cyan-300" />
              <div className="flex gap-2 text-xs">
                {([['idea', 'Es una idea'], ['existing', 'Ya existe']] as const).map(([v, label]) => (
                  <button key={v} type="button" onClick={() => setStage(v)} aria-pressed={stage === v}
                    className={`flex-1 rounded-xl border px-3 py-2 ${stage === v ? 'border-cyan-300 bg-cyan-400/10' : 'border-white/10'}`}>{label}</button>
                ))}
              </div>
              <button type="submit" disabled={!newName.trim() || Boolean(busy)} className="w-full rounded-xl u-cta px-4 py-2 text-xs font-bold disabled:opacity-50">
                Empezar con ADAN
              </button>
            </form>
          </div>
        )}

        {lines.map((l) => <Bubble key={l.id} from={l.from} text={l.text} />)}
        {busy && (
          <p className="text-xs text-slate-400 animate-pulse">
            {busy === 'leyendo' ? 'ADAN está leyendo tus documentos…' : busy === 'cargando' ? 'Preparando la conversación…' : 'ADAN está pensando…'}
          </p>
        )}
        {error && <p role="alert" className="rounded-xl bg-orange-500/10 p-2 text-xs text-orange-200">{error}</p>}
        <div ref={endRef} />
      </div>

      {user && companyId ? (
        <div className="border-t border-white/10 p-3">
          <form onSubmit={send} className="flex items-end gap-2">
            <textarea aria-label="Mensaje para ADAN" value={input} onChange={(e) => setInput(e.target.value)} rows={2} maxLength={8000}
              onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey && !e.nativeEvent.isComposing) { e.preventDefault(); void send() } }}
              placeholder="Escribe, dicta o pega una captura…"
              onPaste={(e) => { const files = pastedFiles(e); if (files.length) { e.preventDefault(); void upload(files) } }} disabled={Boolean(busy)}
              className="flex-1 resize-none rounded-xl border border-white/10 bg-black/30 px-3 py-2 text-sm outline-none focus:border-cyan-300" />
            <input ref={fileInput} type="file" multiple accept={ACCEPTED_DOCS} className="hidden" aria-label="Cargar documentos"
              onChange={(e) => { const files = Array.from(e.target.files ?? []); e.target.value = ''; void upload(files) }} />
            <button type="button" onClick={() => fileInput.current?.click()} disabled={Boolean(busy)} title="Cargar documentos"
              aria-label="Cargar documentos" className="rounded-xl bg-white/10 px-3 py-2 hover:bg-white/20 disabled:opacity-40">📎</button>
            <MicButton onText={(t) => setInput((v) => (v ? `${v} ${t}` : t))} disabled={Boolean(busy)}
              className="rounded-xl bg-white/10 px-3 py-2 hover:bg-white/20 disabled:opacity-40" />
            <button type="submit" disabled={!input.trim() || Boolean(busy)} className="rounded-xl u-cta px-3 py-2 text-xs font-bold disabled:opacity-40">Enviar</button>
          </form>
          <div className="mt-2 flex justify-between text-[11px] text-slate-400">
            <button type="button" onClick={() => { setCompanyId(null); setLines([]) }} className="hover:text-white">Cambiar de empresa</button>
            <Link to={`/nivel1/${companyId}`} className="hover:text-white">Abrir el espacio completo →</Link>
          </div>
        </div>
      ) : null}
    </section>
  )
}

function Bubble({ from, text }: { from: Line['from']; text: string }) {
  return (
    <div className={`flex ${from === 'tu' ? 'justify-end' : 'justify-start'}`}>
      <div className={`max-w-[90%] rounded-2xl px-3 py-2 ${from === 'tu' ? 'bg-[#3e6bff] text-white' : 'bg-white/[0.05] border border-white/10'}`}>
        {from === 'tu' ? <p className="whitespace-pre-wrap">{text}</p> : <div className="u-md"><RichMessage text={text} /></div>}
      </div>
    </div>
  )
}
