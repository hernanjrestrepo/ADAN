import { useEffect, useState } from 'react'
import { useParams } from 'react-router'
import { api, errorMessage } from '../lib/api'
import type { PublicSurvey, SurveyAnswer } from '../types'

// Encuesta pública: quien recibe el enlace por WhatsApp responde sin cuenta y sin datos personales
export default function SurveyPublicPage() {
  const { token = '' } = useParams()
  const [survey, setSurvey] = useState<PublicSurvey | null>(null)
  const [answers, setAnswers] = useState<Record<string, SurveyAnswer>>({})
  const [consent, setConsent] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [sent, setSent] = useState(false)
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    api.getPublicSurvey(token).then(setSurvey).catch((err: unknown) => setError(errorMessage(err)))
  }, [token])

  const set = (id: string, value: SurveyAnswer) => setAnswers((a) => ({ ...a, [id]: value }))
  const submit = async () => {
    setBusy(true)
    setError(null)
    try {
      await api.answerSurvey(token, answers, consent)
      setSent(true)
    } catch (err) { setError(errorMessage(err)) } finally { setBusy(false) }
  }

  return (
    <div className="min-h-screen bg-adan-bg px-4 py-8">
      <main className="mx-auto max-w-xl">
        <p className="text-xs font-semibold tracking-[0.25em] text-adan-accent">ENCUESTA · ADAN by Paradixe</p>
        {error && !survey && <p className="mt-6 rounded-xl bg-adan-danger/10 p-4 text-sm">{error}</p>}
        {survey && (sent ? (
          <div className="mt-6 rounded-2xl border border-adan-success/40 bg-adan-success/10 p-6 text-center" data-testid="survey-thanks">
            <p className="text-4xl">🙌</p>
            <h1 className="mt-2 text-xl font-bold">¡Gracias por tu tiempo!</h1>
            <p className="mt-2 text-sm text-adan-muted">Tus respuestas quedaron registradas de forma anónima y ayudan a {survey.company} a construir algo que de verdad sirva.</p>
          </div>
        ) : !survey.open ? (
          <p className="mt-6 rounded-xl bg-adan-surface p-4 text-sm">Esta encuesta ya está cerrada. ¡Gracias por tu interés!</p>
        ) : (
          <>
            <h1 className="mt-2 text-2xl font-bold">{survey.titulo}</h1>
            <p className="mt-2 text-sm text-adan-muted">{survey.intro}</p>
            <p className="mt-1 text-xs text-adan-muted">Toma unos 2 minutos. No te pedimos nombre, teléfono ni correo.</p>
            <ol className="mt-6 space-y-5">
              {survey.preguntas.map((q, i) => (
                <li key={q.id} className="rounded-2xl border border-adan-border bg-adan-surface p-4">
                  <p className="font-medium">{i + 1}. {q.texto}</p>
                  {q.tipo === 'opcion' && (
                    <div className="mt-3 space-y-2">
                      {q.opciones.map((o) => (
                        <label key={o} className="flex items-center gap-2 text-sm">
                          <input type="radio" name={q.id} checked={answers[q.id] === o} onChange={() => set(q.id, o)} /> {o}
                        </label>
                      ))}
                    </div>
                  )}
                  {q.tipo === 'multiple' && (
                    <div className="mt-3 space-y-2">
                      {q.opciones.map((o) => {
                        const current = (answers[q.id] as string[] | undefined) ?? []
                        return (
                          <label key={o} className="flex items-center gap-2 text-sm">
                            <input type="checkbox" checked={current.includes(o)}
                              onChange={(e) => set(q.id, e.target.checked ? [...current, o] : current.filter((x) => x !== o))} /> {o}
                          </label>
                        )
                      })}
                    </div>
                  )}
                  {q.tipo === 'escala' && (
                    <div className="mt-3 flex gap-2" role="radiogroup" aria-label={q.texto}>
                      {[1, 2, 3, 4, 5].map((n) => (
                        <button key={n} type="button" role="radio" aria-checked={answers[q.id] === n} onClick={() => set(q.id, n)}
                          className={`h-10 w-10 rounded-full border text-sm font-bold ${answers[q.id] === n ? 'border-adan-accent bg-adan-accent text-white' : 'border-adan-border'}`}>{n}</button>
                      ))}
                      <span className="self-center text-xs text-adan-muted">1 = nada · 5 = muchísimo</span>
                    </div>
                  )}
                  {q.tipo === 'numero' && (
                    <input type="number" inputMode="decimal" aria-label={q.texto} value={(answers[q.id] as number | undefined) ?? ''}
                      onChange={(e) => set(q.id, e.target.value === '' ? '' : Number(e.target.value))}
                      className="mt-3 w-full rounded-xl border border-adan-border bg-adan-bg px-3 py-2 text-sm" />
                  )}
                  {q.tipo === 'texto' && (
                    <textarea aria-label={q.texto} rows={3} maxLength={1000} value={(answers[q.id] as string | undefined) ?? ''}
                      onChange={(e) => set(q.id, e.target.value)} className="mt-3 w-full rounded-xl border border-adan-border bg-adan-bg px-3 py-2 text-sm" />
                  )}
                </li>
              ))}
            </ol>
            <label className="mt-6 flex items-start gap-3 text-xs text-adan-muted">
              <input type="checkbox" checked={consent} onChange={(e) => setConsent(e.target.checked)} className="mt-0.5" />
              <span>Autorizo que {survey.company} use mis respuestas, de forma anónima, solo para investigación de mercado, según la
                Ley 1581 de 2012 de protección de datos. Puedo no responder las preguntas que no quiera.</span>
            </label>
            {error && <p className="mt-3 text-sm text-red-300">{error}</p>}
            <button type="button" onClick={submit} disabled={!consent || busy}
              className="mt-4 w-full rounded-xl bg-adan-accent px-5 py-3 font-semibold text-white disabled:opacity-50">
              {busy ? 'Enviando…' : 'Enviar mis respuestas'}
            </button>
          </>
        ))}
      </main>
    </div>
  )
}
