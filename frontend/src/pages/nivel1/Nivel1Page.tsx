import { useCallback, useEffect, useState } from 'react'
import { useParams } from 'react-router'
import AppShell from '../../components/AppShell'
import Alert from '../../components/ui/Alert'
import Badge from '../../components/ui/Badge'
import Tabs from '../../components/ui/Tabs'
import { LoadingState } from '../../components/ui/States'
import { api, errorMessage } from '../../lib/api'
import type {
  BoardConsensus, Decision, DocumentRecord, GateReviewResult, LevelStatus, Message, Nivel1Status,
} from '../../types'
import BoardRoomPanel from './BoardRoomPanel'
import ChatPanel from './ChatPanel'
import DiagnosisPanel from './DiagnosisPanel'
import ScoresPanel from './ScoresPanel'

type Tab = 'chat' | 'boardroom' | 'diagnosis' | 'scores'

const TABS: { id: Tab; label: string }[] = [
  { id: 'chat', label: 'Conversación' },
  { id: 'boardroom', label: 'Board Room' },
  { id: 'diagnosis', label: 'Diagnóstico' },
  { id: 'scores', label: 'Scores' },
]

const LEVEL_BADGE: Record<LevelStatus, { text: string; tone: 'green' | 'blue' | 'gray' }> = {
  active: { text: 'En progreso', tone: 'green' },
  completed: { text: 'Completado', tone: 'blue' },
  blocked: { text: 'Bloqueado', tone: 'gray' },
}

export default function Nivel1Page() {
  const { companyId = '' } = useParams()
  const [status, setStatus] = useState<Nivel1Status | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState<Tab>('chat')
  const [sending, setSending] = useState(false)
  const [board, setBoard] = useState<BoardConsensus | null>(null)
  const [boardRunning, setBoardRunning] = useState(false)
  const [diagnosis, setDiagnosis] = useState<DocumentRecord | null>(null)
  const [diagnosing, setDiagnosing] = useState(false)
  const [gate, setGate] = useState<GateReviewResult | null>(null)
  const [pendingDecision, setPendingDecision] = useState<Decision | null>(null)
  const [deciding, setDeciding] = useState(false)

  const applyStatus = useCallback((data: Nivel1Status) => {
    setStatus(data)
    setMessages(data.messages)
  }, [])

  // Carga inicial; se ignora la respuesta si el usuario cambió de empresa antes de que llegara
  useEffect(() => {
    let cancelled = false
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
      await loadStatus()
    } catch (err) {
      setError(errorMessage(err))
      setMessages((prev) => prev.filter((m) => m.id !== tempId))
    } finally {
      setSending(false)
    }
  }

  const handleBoardRoom = async () => {
    setActiveTab('boardroom')
    setBoard(null)
    setBoardRunning(true)
    try {
      setBoard(await api.runBoardRoom(companyId))
    } catch (err) {
      setError(errorMessage(err))
    } finally {
      setBoardRunning(false)
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
      await loadStatus()
    } catch (err) {
      setError(errorMessage(err))
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
      crumbs={[{ label: 'Mis Empresas', to: '/dashboard' }, { label: companyName }, { label: 'Nivel 1 — El Dolor' }]}
      status={<Badge tone={levelBadge.tone}>{levelBadge.text}</Badge>}
      toolbar={<Tabs tabs={TABS} active={activeTab} onChange={setActiveTab} />}
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
            <ChatPanel messages={messages} sending={sending} onSend={handleSend}
              onBoardRoom={handleBoardRoom} onDiagnosis={handleDiagnosis} onGateReview={handleGateReview} />
          )}
          {activeTab === 'boardroom' && <BoardRoomPanel result={board} running={boardRunning} onRun={handleBoardRoom} />}
          {activeTab === 'diagnosis' && (
            <DiagnosisPanel diagnosis={diagnosis} running={diagnosing} onGenerate={handleDiagnosis} />
          )}
          {activeTab === 'scores' && (
            <ScoresPanel scores={status?.scores ?? []} gate={gate} pendingDecision={pendingDecision}
              deciding={deciding} onDecide={handleDecision} />
          )}
        </>
      )}
    </AppShell>
  )
}
