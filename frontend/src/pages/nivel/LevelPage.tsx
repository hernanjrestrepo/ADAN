import { Suspense, lazy, useCallback, useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router'
import AppShell from '../../components/AppShell'
import Alert from '../../components/ui/Alert'
import Badge from '../../components/ui/Badge'
import Button from '../../components/ui/Button'
import Card from '../../components/ui/Card'
import { LoadingState } from '../../components/ui/States'
import { api, errorMessage } from '../../lib/api'
import { waitForResearch } from '../../lib/research'
import type { LevelRoom, Message } from '../../types'
import { reactTo } from '../../universo/react'
import ChatPanel from '../nivel1/ChatPanel'

// La Sala de los Niveles 2 a 7: la misma oficina y la misma conversación con el equipo que en el Nivel 1, con el
// guion, los entregables y los indicadores de cada Nivel (metodología acordada con Hernán).

const EmbeddedWorld = lazy(() => import('../../universo/EmbeddedWorld'))

// Herramientas que ya existen y alimentan los entregables del Nivel
const TOOLS: Record<number, { label: string; to: (id: string) => string }[]> = {
  2: [{ label: '🏷️ Nombre, logo y slogan', to: (id) => `/marca/${id}` }],
  3: [{ label: '🏷️ Marca', to: (id) => `/marca/${id}` },
      { label: '📁 Expediente de creación', to: (id) => `/expediente/${id}` },
      { label: '🧮 Flujo de caja y organigrama', to: (id) => `/finanzas/${id}` },
      { label: '⚖️ Nombre, ruta legal y estatutos', to: (id) => `/constitucion/${id}` }],
  4: [{ label: '🤖 Agentes por tiempo', to: (id) => `/agentes/${id}` }],
}

export default function LevelPage() {
  const { n = '2', companyId = '' } = useParams()
  const nivel = Number(n)
  const navigate = useNavigate()
  const [room, setRoom] = useState<LevelRoom | null>(null)
  const [company, setCompany] = useState('Empresa')
  const [error, setError] = useState<string | null>(null)
  const [sending, setSending] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [researching, setResearching] = useState(false)
  const [closing, setClosing] = useState(false)
  const [reason, setReason] = useState('')
  const [closingBusy, setClosingBusy] = useState(false)
  const [numbers, setNumbers] = useState(false)

  const load = useCallback(async () => {
    try {
      setRoom(await api.getLevelStatus(nivel, companyId))
    } catch (err) {
      setError(errorMessage(err))
    }
  }, [nivel, companyId])

  useEffect(() => {
    let cancelled = false
    api.getLevelStatus(nivel, companyId).then((r) => { if (!cancelled) setRoom(r) }).catch((err: unknown) => { if (!cancelled) setError(errorMessage(err)) })
    api.getCompany(companyId).then((c) => { if (!cancelled) setCompany(c.name) }).catch(() => undefined)
    return () => { cancelled = true }
  }, [nivel, companyId])

  const afterReply = async (message: Message) => {
    reactTo(message)
    const fresh = await api.getLevelStatus(nivel, companyId)
    setRoom(fresh)
    const at = fresh.messages.findIndex((m) => m.id === message.id)
    fresh.messages.slice(at + 1).filter((m) => m.role !== 'user').forEach((m, i) => window.setTimeout(() => reactTo(m), 2600 * (i + 1)))
    if (message.metadata_json?.investigando || message.metadata_json?.trabajando) {
      setResearching(true)
      void waitForResearch(companyId, message.id, 300_000, nivel).then((msgs) => {
        setResearching(false)
        const found = msgs?.[msgs.length - 1]
        if (found) reactTo(found)
        void load()
      })
    }
  }

  const send = async (text: string) => {
    setSending(true)
    const temp: Message = { id: `temp-${text.length}-${room?.messages.length ?? 0}`, role: 'user', content: text, created_at: new Date().toISOString() }
    setRoom((r) => (r ? { ...r, messages: [...r.messages, temp] } : r))
    try {
      const data = await api.chatLevel(nivel, companyId, text)
      await afterReply(data.message)
      // El fundador dijo que sí al cierre que propuso ADÁN: subimos al siguiente piso
      if (data.closed?.next) window.setTimeout(() => navigate(`/nivel/${data.closed!.next}/${companyId}`), 3500)
    } catch (err) {
      setError(errorMessage(err))
      await load()
    } finally {
      setSending(false)
    }
  }

  const upload = async (files: File[]) => {
    setUploading(true)
    try {
      const result = await api.uploadDocuments(companyId, files, nivel)
      if (result.errors.length) setError(result.errors.join(' '))
      await load()
    } catch (err) {
      setError(errorMessage(err))
    } finally {
      setUploading(false)
    }
  }

  // Con todos los temas cubiertos no hace falta motivo: se cierra directo y se sube al siguiente piso
  const closeNow = async () => {
    setClosingBusy(true)
    try {
      const res = await api.closeLevel(nivel, companyId, '')
      await load()
      if (res.next) window.setTimeout(() => navigate(`/nivel/${res.next}/${companyId}`), 2500)
    } catch (err) {
      setError(errorMessage(err))
    } finally {
      setClosingBusy(false)
    }
  }

  const close = async () => {
    setClosingBusy(true)
    try {
      const res = await api.closeLevel(nivel, companyId, reason.trim())
      setClosing(false)
      await load()
      if (res.next) navigate(`/nivel/${res.next}/${companyId}`)
    } catch (err) {
      setError(errorMessage(err))
    } finally {
      setClosingBusy(false)
    }
  }

  // Camila arma presupuesto y flujo de caja y los presenta en la misma Sala del Nivel 3
  const buildNumbers = async () => {
    setNumbers(true)
    try {
      await api.buildNumbers(companyId)
      const fresh = await api.getLevelStatus(nivel, companyId)
      setRoom(fresh)
      const last = fresh.messages[fresh.messages.length - 1]
      if (last) reactTo(last)
    } catch (err) {
      setError(errorMessage(err))
    } finally {
      setNumbers(false)
    }
  }

  const level = room?.level
  const complete = room?.discovery?.complete ?? false
  const prevPath = nivel - 1 === 1 ? `/nivel1/${companyId}` : `/nivel/${nivel - 1}/${companyId}`
  return (
    <AppShell
      crumbs={[{ label: 'Mis Empresas', to: '/dashboard' }, { label: company, to: `/gemelo/${companyId}` },
        { label: `Nivel ${nivel}${level ? ` — ${level.name}` : ''}` }]}
      status={room && <Badge tone={room.status === 'completed' ? 'blue' : room.status === 'active' ? 'green' : 'gray'}>
        {room.status === 'completed' ? 'Cerrado' : room.status === 'active' ? 'En progreso' : 'Bloqueado'}</Badge>}
      fixedHeight={room?.status !== 'blocked'}
    >
      {error && <div className="max-w-4xl mx-auto px-4 pt-3"><Alert message={error} onClose={() => setError(null)} /></div>}
      {!room ? <LoadingState label={`Abriendo el Nivel ${nivel}…`} /> : room.status === 'blocked' ? (
        <div className="max-w-2xl mx-auto p-6">
          <Card>
            <p className="text-sm text-adan-muted">Nivel {nivel}</p>
            <h1 className="text-2xl font-bold">🔒 {room.level.name}</h1>
            <p className="mt-2">Aquí vamos a {room.level.goal}. Se abre cuando cierres el Nivel {nivel - 1}.</p>
            <p className="mt-3 text-sm"><b>Entregables:</b> {room.level.deliverables.join('; ')}.</p>
            <Link to={prevPath} className="mt-4 inline-block rounded-xl bg-adan-accent px-4 py-2 font-semibold text-white">Ir al Nivel {nivel - 1}</Link>
          </Card>
        </div>
      ) : (
        <div className="h-full flex flex-col">
          {/* Entregables del Nivel y herramientas que los alimentan */}
          <div className="max-w-[1800px] w-full mx-auto px-3 sm:px-4 pt-2 flex flex-wrap items-center gap-2 text-xs">
            <b className="text-adan-text">Entregables:</b>
            {level?.deliverables.map((d) => <span key={d} className="rounded-full border border-adan-border px-2 py-0.5 text-adan-muted">{d}</span>)}
            {(TOOLS[nivel] ?? []).map((t) => (
              <Link key={t.label} to={t.to(companyId)} className="rounded-full bg-adan-accent/15 px-2 py-0.5 font-semibold text-adan-accent hover:bg-adan-accent/25">{t.label}</Link>
            ))}
            {nivel === 3 && room.status === 'active' && (
              <button type="button" onClick={buildNumbers} disabled={numbers}
                className="rounded-full bg-adan-success/15 px-2 py-0.5 font-semibold text-adan-success hover:bg-adan-success/25 disabled:opacity-50">
                {numbers ? 'Camila está armando los números… (1-2 min)' : '🧮 Construir presupuesto y flujo de caja aquí'}
              </button>
            )}
            {room.status === 'completed' && <span className="ml-auto rounded-full bg-adan-success/15 px-2 py-0.5 font-semibold text-adan-success">✓ Nivel cerrado</span>}
          </div>
          <div className="flex-1 min-h-0">
            <ChatPanel companyId={companyId} level={nivel} messages={room.messages} sending={sending} researching={researching}
              discovery={room.discovery ?? undefined} onSend={send} onReload={load} uploading={uploading} onUpload={upload}
              onClose={() => (complete ? void closeNow() : setClosing(true))} onError={setError}
              world={<Suspense fallback={<div className="h-full rounded-2xl bg-adan-surface animate-pulse" />}><EmbeddedWorld level={nivel} companyId={companyId} /></Suspense>} />
          </div>
        </div>
      )}

      {closing && level && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-3" role="dialog" aria-label="Cerrar el Nivel">
          <Card className="w-full max-w-lg">
            <h2 className="text-lg font-bold">Cerrar el Nivel {nivel}: {level.name}</h2>
            {complete ? (
              <p className="mt-2 text-sm">Todos los temas están cubiertos. Entregables: {level.deliverables.join('; ')}. ¿Apruebas el cierre?</p>
            ) : (
              <>
                <p className="mt-2 text-sm">
                  Faltan temas: {room?.discovery?.topics.filter((t) => t.estado === 'pendiente' || t.estado === 'parcial').map((t) => t.label).join('; ')}.
                  Puedes cerrarlo bajo tu responsabilidad: queda en el acta y baja la calificación.
                </p>
                <textarea value={reason} onChange={(e) => setReason(e.target.value)} rows={3} maxLength={2000} aria-label="Motivo para cerrar"
                  className="mt-3 w-full rounded-xl border border-adan-border bg-adan-bg px-3 py-2 text-sm" placeholder="Por qué decides cerrarlo ahora…" />
              </>
            )}
            <div className="mt-4 flex justify-end gap-2">
              <Button variant="ghost" onClick={() => setClosing(false)}>Cancelar</Button>
              <Button onClick={close} loading={closingBusy} disabled={!complete && reason.trim().length < 10}>
                {complete ? 'Aprobar el cierre' : 'Cerrar bajo mi responsabilidad'}
              </Button>
            </div>
          </Card>
        </div>
      )}
    </AppShell>
  )
}
