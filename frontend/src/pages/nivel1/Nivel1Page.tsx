import { Suspense, lazy, useCallback, useEffect, useState } from 'react'
import { useParams } from 'react-router'
import AppShell from '../../components/AppShell'
import Alert from '../../components/ui/Alert'
import Badge from '../../components/ui/Badge'
import Tabs from '../../components/ui/Tabs'
import { LoadingState } from '../../components/ui/States'
import { api, errorMessage } from '../../lib/api'
import type {
  Decision, DocumentRecord, GateReviewResult, LevelStatus, Message, Nivel1Status,
} from '../../types'
import ChatPanel from './ChatPanel'
import { reactTo } from '../../universo/react'
import { waitForResearch } from '../../lib/research'
import DiagnosisPanel from './DiagnosisPanel'
import EvidencePanel from './EvidencePanel'
import ScoresPanel from './ScoresPanel'

// Una sola sala: la conversación (con el Board y La Arena dentro), el cierre del Nivel y el diagnóstico
type Tab = 'chat' | 'scores' | 'diagnosis'

const TABS: { id: Tab; label: string }[] = [
  { id: 'chat', label: 'Sala' },
  { id: 'scores', label: 'Avance y cierre' },
  { id: 'diagnosis', label: 'Diagnóstico' },
]

const LEVEL_BADGE: Record<LevelStatus, { text: string; tone: 'green' | 'blue' | 'gray' }> = {
  active: { text: 'En progreso', tone: 'green' },
  completed: { text: 'Completado', tone: 'blue' },
  blocked: { text: 'Bloqueado', tone: 'gray' },
}

const EmbeddedWorld = lazy(() => import('../../universo/EmbeddedWorld'))

export default function Nivel1Page() {
  const { companyId = '' } = useParams()
  const [status, setStatus] = useState<Nivel1Status | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState<Tab>('chat')
  const [sending, setSending] = useState(false)
  const [researching, setResearching] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [diagnosis, setDiagnosis] = useState<DocumentRecord | null>(null)
  const [diagnosing, setDiagnosing] = useState(false)
  const [gate, setGate] = useState<GateReviewResult | null>(null)
  const [pendingDecision, setPendingDecision] = useState<Decision | null>(null)
  const [deciding, setDeciding] = useState(false)
  const [advancing, setAdvancing] = useState(false)
  // Cambia cuando cambia la evidencia o una decisión: los Scores se vuelven a leer
  const [refreshKey, setRefreshKey] = useState(0)
  const bump = useCallback(() => setRefreshKey((k) => k + 1), [])
  const showError = useCallback((message: string) => setError(message), [])

  const applyStatus = useCallback((data: Nivel1Status) => {
    setStatus(data)
    setMessages(data.messages)
  }, [])

  // Carga inicial; se ignora la respuesta si el usuario cambió de empresa antes de que llegara
  useEffect(() => {
    let cancelled = false
    // La última sesión del Board se ve sin volver a ejecutarla (404 si todavía no hay ninguna)
    api.getNivel1Status(companyId)
      .then((data) => { if (!cancelled) applyStatus(data) })
      .catch((err: unknown) => { if (!cancelled) setError(errorMessage(err)) })
      .finally(() => { if (!cancelled) setLoading(false) })
    return () => { cancelled = true }
  }, [companyId, applyStatus])

  const loadStatus = async () => {
    try {
      applyStatus(await api.getNivel1Status(companyId))
    } catch (err) {
      setError(errorMessage(err))
    }
  }

  const handleSend = async (text: string) => {
    setSending(true)
    const tempId = `temp-${Date.now()}`
    // Mensaje optimista mientras responde el modelo
    setMessages((prev) => [...prev, { id: tempId, role: 'user', content: text, created_at: new Date().toISOString() }])
    try {
      const data = await api.chat(companyId, text, status?.conversation?.id)
      setMessages((prev) => [...prev.filter((m) => m.id !== tempId), data.message])
      reactTo(data.message)
      await loadStatus()
      const fresh = await api.getNivel1Status(companyId)
      const at = fresh.messages.findIndex((m) => m.id === data.message.id)
      fresh.messages.slice(at + 1).filter((m) => m.role !== 'user')
        .forEach((m, i) => window.setTimeout(() => reactTo(m), 2600 * (i + 1)))
      if (data.message.metadata_json?.investigando) {
        setResearching(true)
        void waitForResearch(companyId, data.message.id).then((msgs) => {
          setResearching(false)
          if (!msgs) return
          const found = msgs[msgs.length - 1]
          if (found) reactTo(found)
          void loadStatus()
        })
      }
    } catch (err) {
      setError(errorMessage(err))
      setMessages((prev) => prev.filter((m) => m.id !== tempId))
      await loadStatus()  // el backend pudo guardar el mensaje aunque la respuesta no llegara
    } finally {
      setSending(false)
    }
  }

  // Documentación del cliente: ADÁN la lee, la guarda en la memoria de la empresa y aprende de ella
  const handleUpload = async (files: File[]) => {
    setUploading(true)
    try {
      const result = await api.uploadDocuments(companyId, files)
      if (result.errors.length) setError(result.errors.join(' '))
      await loadStatus()
      // Audio y video se transcriben aparte: lo que entendió ADÁN llega en un momento
      const status = await api.getNivel1Status(companyId)
      const last = status.messages[status.messages.length - 1]
      if (last?.metadata_json?.investigando) {
        setResearching(true)
        void waitForResearch(companyId, last.id, 600_000).then((msgs) => {
          setResearching(false)
          const found = msgs?.[msgs.length - 1]
          if (found) reactTo(found)
          void loadStatus()
        })
      }
    } catch (err) {
      setError(errorMessage(err))
    } finally {
      setUploading(false)
    }
  }

  const handleDiagnosis = async () => {
    setActiveTab('diagnosis')
    setDiagnosis(null)
    setDiagnosing(true)
    try {
      setDiagnosis(await api.generateDiagnosis(companyId))
      await loadStatus()
    } catch (err) {
      setError(errorMessage(err))
    } finally {
      setDiagnosing(false)
    }
  }

  const handleGateReview = async () => {
    setActiveTab('scores')
    try {
      const result = await api.gateReview(companyId)
      setGate(result)
      setPendingDecision(result.decisions[0] ?? null)
      bump()
      await loadStatus()
    } catch (err) {
      setError(errorMessage(err))
    }
  }

  // Sin evidencia suficiente, el cliente puede avanzar bajo su responsabilidad (AD-CMP-01 §3)
  const handleAdvanceAnyway = async () => {
    setAdvancing(true)
    try {
      const result = await api.advanceAnyway(companyId)
      setGate(result)
      setPendingDecision(result.decisions[0] ?? null)
    } catch (err) {
      setError(errorMessage(err))
    } finally {
      setAdvancing(false)
    }
  }

  // El Nivel solo se cierra con la aprobación explícita del cliente (AD-FUNC-01)
  const handleDecision = async (action: 'approve' | 'reject') => {
    if (!pendingDecision || deciding) return
    setDeciding(true)
    try {
      await api.decide(companyId, pendingDecision.id, action)
      setPendingDecision(null)
      setGate((prev) => prev && {
        ...prev,
        level_status: action === 'approve' ? 'completed' : prev.level_status,
        message: action === 'approve'
          ? 'Aprobaste el cierre del Nivel 1. El Nivel 2 quedó activo.'
          : 'Rechazaste el cierre del Nivel 1. Puedes seguir trabajando en él.',
      })
      await loadStatus()
    } catch (err) {
      setError(errorMessage(err))
    } finally {
      setDeciding(false)
    }
  }

  const levelBadge = status?.level ? LEVEL_BADGE[status.level.status] : LEVEL_BADGE.blocked
  const companyName = status?.company.name ?? 'Empresa'

  return (
    <AppShell
      crumbs={[{ label: 'Mis Empresas', to: '/dashboard' }, { label: companyName, to: `/gemelo/${companyId}` },
        { label: 'Nivel 1 — El Dolor' }]}
      status={<Badge tone={levelBadge.tone}>{levelBadge.text}</Badge>}
      toolbar={<Tabs tabs={TABS} active={activeTab} onChange={setActiveTab} />}
      fixedHeight={activeTab === 'chat'}
    >
      {error && (
        <div className="max-w-4xl mx-auto px-4 pt-4">
          <Alert message={error} onClose={() => setError(null)} />
        </div>
      )}
      {loading ? (
        <LoadingState label="Cargando Nivel 1..." />
      ) : (
        <>
          {activeTab === 'chat' && (
            <ChatPanel companyId={companyId} messages={messages} sending={sending} researching={researching}
              discovery={status?.discovery} onSend={handleSend} onReload={loadStatus} uploading={uploading} onUpload={handleUpload}
              onDiagnosis={handleDiagnosis} onClose={handleGateReview} onError={showError}
              world={<Suspense fallback={<div className="h-full rounded-2xl bg-adan-surface animate-pulse" />}><EmbeddedWorld /></Suspense>} />
          )}
          {activeTab === 'diagnosis' && (
            <DiagnosisPanel diagnosis={diagnosis} running={diagnosing} onGenerate={handleDiagnosis} />
          )}
          {activeTab === 'scores' && (
            <div className="h-full overflow-y-auto">
            <ScoresPanel companyId={companyId} refreshKey={refreshKey} gate={gate} pendingDecision={pendingDecision}
              deciding={deciding} advancing={advancing} onDecide={handleDecision} onAdvanceAnyway={handleAdvanceAnyway}
              onGoToEvidence={() => setActiveTab('scores')} onError={showError} />
              <div className="max-w-4xl mx-auto px-4 pb-8"><EvidencePanel companyId={companyId} onChanged={bump} /></div>
            </div>
          )}
        </>
      )}
    </AppShell>
  )
}
