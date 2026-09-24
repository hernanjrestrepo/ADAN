import { useEffect, useRef, useState, type FormEvent } from 'react'
import ReactMarkdown from 'react-markdown'
import Button from '../../components/ui/Button'
import { EmptyState } from '../../components/ui/States'
import type { Message } from '../../types'

interface ChatPanelProps {
  messages: Message[]
  sending: boolean
  onSend: (message: string) => Promise<void>
  onBoardRoom: () => void
  onDiagnosis: () => void
  onGateReview: () => void
}

const MAX_MESSAGE_CHARS = 8000  // mismo límite que el backend (WO-097)

export default function ChatPanel({ messages, sending, onSend, onBoardRoom, onDiagnosis, onGateReview }: ChatPanelProps) {
  const [input, setInput] = useState('')
  const endRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    const text = input.trim()
    if (!text || sending) return
    setInput('')
    await onSend(text)
  }

  return (
    <div className="h-full flex flex-col max-w-4xl mx-auto p-4">
      <div className="flex-1 overflow-y-auto space-y-4 mb-4" aria-live="polite">
        {messages.length === 0 && (
          <EmptyState icon="💬" title="Comienza la conversación">
            Cuéntale a ADÁN sobre el problema que quieres resolver. ADÁN te hará preguntas para entender tu
            dolor a fondo.
          </EmptyState>
        )}
        {messages.map((msg) => (
          <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[80%] rounded-xl px-4 py-3 ${
              msg.role === 'user' ? 'bg-adan-accent text-white' : 'bg-adan-surface border border-adan-border'
            }`}>
              {msg.agent_name && <div className="text-xs font-bold mb-1 text-adan-accent">{msg.agent_name}</div>}
              {msg.role === 'user' ? (
                <div className="text-sm whitespace-pre-wrap">{msg.content}</div>
              ) : (
                <div className="text-sm markdown"><ReactMarkdown>{msg.content}</ReactMarkdown></div>
              )}
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
        <div ref={endRef} />
      </div>

      <form onSubmit={handleSubmit} className="flex gap-3">
        <input
          type="text"
          aria-label="Mensaje para ADÁN"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Cuéntale a ADÁN sobre tu problema..."
          maxLength={MAX_MESSAGE_CHARS}
          className="flex-1 px-4 py-3 bg-adan-surface border border-adan-border rounded-xl text-adan-text focus:outline-none focus:border-adan-accent"
          disabled={sending}
        />
        <Button type="submit" disabled={sending || !input.trim()}>Enviar</Button>
      </form>

      <div className="flex gap-3 mt-4">
        <Button variant="secondary" className="flex-1" onClick={onBoardRoom}>🏛️ Ejecutar Board Room</Button>
        <Button variant="secondary" className="flex-1" onClick={onDiagnosis}>📋 Generar Diagnóstico</Button>
        <Button variant="secondary" className="flex-1 !border-adan-success/50 !text-adan-success" onClick={onGateReview}>
          ✅ Gate Review
        </Button>
      </div>
    </div>
  )
}
