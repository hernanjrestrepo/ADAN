import { useState, useEffect, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import ReactMarkdown from 'react-markdown'
import { api } from '../lib/api'

export default function Nivel1Page({ user }) {
  const { companyId } = useParams()
  const navigate = useNavigate()
  const [status, setStatus] = useState(null)
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(true)
  const [sending, setSending] = useState(false)
  const [boardResults, setBoardResults] = useState(null)
  const [diagnosis, setDiagnosis] = useState(null)
  const [scores, setScores] = useState([])
  const [gateResult, setGateResult] = useState(null)
  const [activeTab, setActiveTab] = useState('chat')
  const messagesEndRef = useRef(null)

  useEffect(() => {
    loadStatus()
  }, [companyId])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const loadStatus = async () => {
    try {
      const data = await api.getNivel1Status(companyId)
      setStatus(data)
      setMessages(data.messages || [])
      setScores(data.scores || [])
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleSend = async (e) => {
    e.preventDefault()
    if (!input.trim() || sending) return

    const msg = input
    setInput('')
    setSending(true)

    // Add user message optimistically
    const userMsg = {
      id: 'temp-' + Date.now(),
      role: 'user',
      content: msg,
      created_at: new Date().toISOString(),
    }
    setMessages((prev) => [...prev, userMsg])

    try {
      const data = await api.chat(companyId, msg, status?.conversation?.id)
      // Replace optimistic message with real ones
      setMessages((prev) => {
        const withoutTemp = prev.filter((m) => !m.id.startsWith('temp-'))
        return [...withoutTemp, data.message]
      })
      // Reload to get full state
      loadStatus()
    } catch (err) {
      alert(err.message)
      setMessages((prev) => prev.filter((m) => !m.id.startsWith('temp-')))
    } finally {
      setSending(false)
    }
  }

  const handleBoardRoom = async () => {
    setActiveTab('boardroom')
    setBoardResults(null)
    try {
      const data = await api.runBoardRoom(companyId)
      setBoardResults(data.board_results)
    } catch (err) {
      alert(err.message)
    }
  }

  const handleDiagnosis = async () => {
    setActiveTab('diagnosis')
    setDiagnosis(null)
    try {
      const data = await api.generateDiagnosis(companyId)
      setDiagnosis(data)
      loadStatus()
    } catch (err) {
      alert(err.message)
    }
  }

  const handleGateReview = async () => {
    try {
      const data = await api.gateReview(companyId)
      setGateResult(data)
      loadStatus()
    } catch (err) {
      alert(err.message)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-adan-bg">
        <div className="text-adan-muted">Cargando Nivel 1...</div>
      </div>
    )
  }

  const company = status?.company
  const level = status?.level

  return (
    <div className="min-h-screen bg-adan-bg flex flex-col">
      {/* Header */}
      <header className="border-b border-adan-border px-6 py-3">
        <div className="flex items-center justify-between max-w-7xl mx-auto">
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate('/dashboard')}
              className="text-adan-muted hover:text-adan-text"
            >
              ← Volver
            </button>
            <div>
              <h1 className="text-lg font-bold">{company?.name || 'Empresa'}</h1>
              <p className="text-xs text-adan-muted">Nivel 1 — El Dolor</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <span className={`text-xs px-2 py-1 rounded ${
              level?.status === 'active' ? 'bg-green-500/20 text-green-400' :
              level?.status === 'completed' ? 'bg-blue-500/20 text-blue-400' :
              'bg-gray-500/20 text-gray-400'
            }`}>
              {level?.status === 'active' ? 'En progreso' :
               level?.status === 'completed' ? 'Completado' : 'Bloqueado'}
            </span>
          </div>
        </div>
      </header>

      {/* Tabs */}
      <div className="border-b border-adan-border px-6">
        <div className="max-w-7xl mx-auto flex gap-1">
          {['chat', 'boardroom', 'diagnosis', 'scores'].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
                activeTab === tab
                  ? 'border-adan-accent text-adan-accent'
                  : 'border-transparent text-adan-muted hover:text-adan-text'
              }`}
            >
              {tab === 'chat' ? 'Conversación' :
               tab === 'boardroom' ? 'Board Room' :
               tab === 'diagnosis' ? 'Diagnóstico' : 'Scores'}
            </button>
          ))}
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-hidden">
        {activeTab === 'chat' && (
          <div className="h-full flex flex-col max-w-4xl mx-auto p-4">
            {/* Messages */}
            <div className="flex-1 overflow-y-auto space-y-4 mb-4">
              {messages.length === 0 && (
                <div className="text-center py-12">
                  <div className="text-4xl mb-3">💬</div>
                  <h3 className="text-lg font-bold mb-2">Comienza la conversación</h3>
                  <p className="text-adan-muted text-sm">
                    Cuéntale a ADÁN sobre el problema que quieres resolver.
                    ADÁN te hará preguntas para entender tu dolor a fondo.
                  </p>
                </div>
              )}
              {messages.map((msg) => (
                <div
                  key={msg.id}
                  className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[80%] rounded-xl px-4 py-3 ${
                      msg.role === 'user'
                        ? 'bg-adan-accent text-white'
                        : 'bg-adan-surface border border-adan-border'
                    }`}
                  >
                    {msg.agent_name && (
                      <div className="text-xs font-bold mb-1 text-adan-accent">
                        {msg.agent_name}
                      </div>
                    )}
                    <div className="text-sm whitespace-pre-wrap">{msg.content}</div>
                  </div>
                </div>
              ))}
              {sending && (
                <div className="flex justify-start">
                  <div className="bg-adan-surface border border-adan-border rounded-xl px-4 py-3">
                    <div className="text-sm text-adan-muted animate-pulse">Pensando...</div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <form onSubmit={handleSend} className="flex gap-3">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Cuéntale a ADÁN sobre tu problema..."
                className="flex-1 px-4 py-3 bg-adan-surface border border-adan-border rounded-xl text-adan-text focus:outline-none focus:border-adan-accent"
                disabled={sending}
              />
              <button
                type="submit"
                disabled={sending || !input.trim()}
                className="px-6 py-3 bg-adan-accent text-white rounded-xl font-medium hover:bg-blue-600 disabled:opacity-50"
              >
                Enviar
              </button>
            </form>

            {/* Action Buttons */}
            <div className="flex gap-3 mt-4">
              <button
                onClick={handleBoardRoom}
                className="flex-1 py-3 bg-adan-surface border border-adan-border rounded-xl text-sm font-medium hover:border-adan-accent"
              >
                🏛️ Ejecutar Board Room
              </button>
              <button
                onClick={handleDiagnosis}
                className="flex-1 py-3 bg-adan-surface border border-adan-border rounded-xl text-sm font-medium hover:border-adan-accent"
              >
                📋 Generar Diagnóstico
              </button>
              <button
                onClick={handleGateReview}
                className="flex-1 py-3 bg-adan-success/20 border border-adan-success/50 rounded-xl text-sm font-medium text-adan-success hover:bg-adan-success/30"
              >
                ✅ Gate Review
              </button>
            </div>
          </div>
        )}

        {activeTab === 'boardroom' && (
          <div className="max-w-4xl mx-auto p-6">
            <h2 className="text-2xl font-bold mb-6">Board Room</h2>
            {!boardResults ? (
              <div className="text-center py-12">
                <p className="text-adan-muted mb-4">
                  Ejecuta el Board Room para que cada agente analice tu problema.
                </p>
                <button
                  onClick={handleBoardRoom}
                  className="px-6 py-3 bg-adan-accent text-white rounded-lg font-medium hover:bg-blue-600"
                >
                  Ejecutar Board Room
                </button>
              </div>
            ) : (
              <div className="space-y-6">
                {boardResults.map((result) => (
                  <div key={result.agent} className="bg-adan-surface border border-adan-border rounded-xl p-6">
                    <div className="flex items-center gap-3 mb-4">
                      <div className="w-10 h-10 rounded-full bg-adan-accent/20 flex items-center justify-center text-adan-accent font-bold">
                        {result.agent[0]}
                      </div>
                      <div>
                        <h3 className="font-bold">{result.agent}</h3>
                        <p className="text-xs text-adan-muted">Agente del Board Room</p>
                      </div>
                    </div>
                    <div className="text-sm whitespace-pre-wrap text-adan-text/90">
                      {result.analysis}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === 'diagnosis' && (
          <div className="max-w-4xl mx-auto p-6">
            <h2 className="text-2xl font-bold mb-6">Diagnóstico del Dolor</h2>
            {!diagnosis ? (
              <div className="text-center py-12">
                <p className="text-adan-muted mb-4">
                  Genera el diagnóstico formal basado en la conversación y el Board Room.
                </p>
                <button
                  onClick={handleDiagnosis}
                  className="px-6 py-3 bg-adan-accent text-white rounded-lg font-medium hover:bg-blue-600"
                >
                  Generar Diagnóstico
                </button>
              </div>
            ) : (
              <div className="bg-adan-surface border border-adan-border rounded-xl p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-bold">{diagnosis.title}</h3>
                  <span className="text-xs text-adan-muted">
                    v{diagnosis.version} · {diagnosis.origin}
                  </span>
                </div>
                <div className="prose prose-invert max-w-none">
                  <ReactMarkdown>{diagnosis.content}</ReactMarkdown>
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'scores' && (
          <div className="max-w-4xl mx-auto p-6">
            <h2 className="text-2xl font-bold mb-6">Scores</h2>
            {scores.length === 0 ? (
              <div className="text-center py-12 text-adan-muted">
                No hay scores calculados aún. Genera el diagnóstico primero.
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {scores.map((score) => (
                  <div key={score.id} className="bg-adan-surface border border-adan-border rounded-xl p-6">
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="font-bold capitalize">{score.score_type} Score</h3>
                      <span className="text-2xl font-bold text-adan-accent">
                        {score.value.toFixed(0)}
                      </span>
                    </div>
                    <div className="w-full bg-adan-bg rounded-full h-2 mb-3">
                      <div
                        className="bg-adan-accent h-2 rounded-full transition-all"
                        style={{ width: `${score.value}%` }}
                      />
                    </div>
                    <div className="text-xs text-adan-muted mb-2">
                      Confianza: {score.confidence_level.toFixed(0)}%
                    </div>
                    {score.reasoning && (
                      <p className="text-sm text-adan-text/80">{score.reasoning}</p>
                    )}
                  </div>
                ))}
              </div>
            )}

            {/* Gate Review Result */}
            {gateResult && (
              <div className={`mt-6 p-6 rounded-xl border ${
                gateResult.approved
                  ? 'bg-adan-success/10 border-adan-success/50'
                  : 'bg-adan-danger/10 border-adan-danger/50'
              }`}>
                <h3 className={`text-lg font-bold mb-2 ${
                  gateResult.approved ? 'text-adan-success' : 'text-adan-danger'
                }`}>
                  {gateResult.approved ? '✅ Gate Review Aprobado' : '❌ Gate Review No Aprobado'}
                </h3>
                <p className="text-sm">{gateResult.message}</p>
                <p className="text-xs text-adan-muted mt-2">
                  Estado del nivel: {gateResult.level_status}
                </p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
