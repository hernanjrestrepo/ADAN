import { useEffect, useRef, useState } from 'react'

// Dictado por voz con el reconocimiento del navegador (Chrome, Edge, Safari). El audio no pasa por ADAN:
// el navegador lo convierte a texto y ese texto queda en la caja para que la persona lo revise antes de enviar.

interface Recognition {
  lang: string
  continuous: boolean
  interimResults: boolean
  start: () => void
  stop: () => void
  onresult: ((e: { resultIndex: number; results: ArrayLike<{ isFinal: boolean; 0: { transcript: string } }> }) => void) | null
  onend: (() => void) | null
  onerror: ((e: { error: string }) => void) | null
}

type RecognitionCtor = new () => Recognition

function recognitionCtor(): RecognitionCtor | null {
  const w = window as unknown as { SpeechRecognition?: RecognitionCtor; webkitSpeechRecognition?: RecognitionCtor }
  return w.SpeechRecognition ?? w.webkitSpeechRecognition ?? null
}

export default function MicButton({ onText, disabled = false, className = '' }: {
  onText: (text: string) => void
  disabled?: boolean
  className?: string
}) {
  const [listening, setListening] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const rec = useRef<Recognition | null>(null)
  const supported = recognitionCtor() !== null

  useEffect(() => () => rec.current?.stop(), [])

  if (!supported) return null

  const toggle = () => {
    if (listening) {
      rec.current?.stop()
      return
    }
    const Ctor = recognitionCtor()
    if (!Ctor) return
    const r = new Ctor()
    r.lang = 'es-CO'
    r.continuous = true
    r.interimResults = false
    r.onresult = (e) => {
      let text = ''
      for (let i = e.resultIndex; i < e.results.length; i++) {
        const res = e.results[i]
        if (res?.isFinal) text += res[0].transcript
      }
      if (text.trim()) onText(text.trim())
    }
    r.onerror = (e) => setError(e.error === 'not-allowed' ? 'Permite el micrófono en tu navegador para dictar.' : 'No pude escucharte; intenta de nuevo.')
    r.onend = () => setListening(false)
    rec.current = r
    setError(null)
    r.start()
    setListening(true)
  }

  return (
    <span className="relative inline-flex">
      <button type="button" onClick={toggle} disabled={disabled} aria-pressed={listening}
        title={listening ? 'Detener el dictado' : 'Hablar en vez de escribir'} aria-label={listening ? 'Detener el dictado' : 'Dictar por voz'}
        className={`${className} ${listening ? 'animate-pulse ring-2 ring-red-400 text-red-300' : ''}`}>
        {listening ? '⏺' : '🎤'}
      </button>
      {error && <span role="alert" className="absolute bottom-full right-0 mb-2 w-56 rounded-lg bg-black/80 p-2 text-xs text-orange-200">{error}</span>}
    </span>
  )
}
