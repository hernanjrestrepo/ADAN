import { useCallback, useEffect, useState } from 'react'
import Button from '../../components/ui/Button'
import Card from '../../components/ui/Card'
import { LoadingState } from '../../components/ui/States'
import { api, errorMessage } from '../../lib/api'
import type { SurveyInsights, SurveyResults, SurveySummary } from '../../types'

const PHONES = 10

// Enlace de WhatsApp armado en el navegador: los números nunca llegan al servidor (Ley 1581, mínimo dato)
function waLink(phone: string, message: string) {
  const digits = phone.replace(/\D/g, '')
  return `https://wa.me/${digits}?text=${encodeURIComponent(message)}`
}

function Bars({ counts, total }: { counts: Record<string, number>; total: number }) {
  return (
    <div className="mt-2 space-y-1">
      {Object.entries(counts).map(([label, n]) => (
        <div key={label} className="text-xs">
          <div className="flex justify-between"><span>{label}</span><span className="text-adan-muted">{n} ({total ? Math.round((n / total) * 100) : 0} %)</span></div>
          <div className="h-2 rounded-full bg-adan-bg overflow-hidden"><div className="h-full bg-adan-accent" style={{ width: `${total ? (n / total) * 100 : 0}%` }} /></div>
        </div>
      ))}
    </div>
  )
}

export default function SurveysPanel({ companyId, onError, onChanged }: {
  companyId: string; onError: (m: string) => void; onChanged: () => void
}) {
  const [list, setList] = useState<SurveySummary[] | null>(null)
  const [results, setResults] = useState<SurveyResults | null>(null)
  const [insights, setInsights] = useState<SurveyInsights | null>(null)
  const [objective, setObjective] = useState('')
  const [phones, setPhones] = useState<string[]>(Array(PHONES).fill(''))
  const [sender, setSender] = useState('')
  const [busy, setBusy] = useState<string | null>(null)
  const [registered, setRegistered] = useState<string[]>([])

  const open = useCallback(async (token: string) => {
    try { setResults(await api.getSurveyResults(companyId, token)); setInsights(null) } catch (err) { onError(errorMessage(err)) }
  }, [companyId, onError])

  useEffect(() => {
    let cancelled = false
    api.listSurveys(companyId).then((l) => {
      if (cancelled) return
      setList(l)
      if (l[0]) void open(l[0].token)
    }).catch((err: unknown) => { if (!cancelled) { onError(errorMessage(err)); setList([]) } })
    return () => { cancelled = true }
  }, [companyId, onError, open])

  const create = async () => {
    setBusy('create')
    try {
      const s = await api.createSurvey(companyId, objective)
      setList((l) => [{ token: s.token, titulo: s.titulo, created_at: s.created_at, open: true, responses: 0 }, ...(l ?? [])])
      await open(s.token)
    } catch (err) { onError(errorMessage(err)) } finally { setBusy(null) }
  }
  const analyze = async () => {
    if (!results) return
    setBusy('insights')
    try { setInsights(await api.getSurveyInsights(companyId, results.token)) } catch (err) { onError(errorMessage(err)) } finally { setBusy(null) }
  }

  if (list === null) return <LoadingState label="Cargando encuestas..." />
  const url = results ? `${window.location.origin}/encuesta/${results.token}` : ''
  const message = `Hola${sender ? `, soy ${sender}` : ''}. Estoy investigando cómo resolver un problema y tu opinión me ayudaría mucho. ` +
    `Son 2 minutos, anónimo, sin datos personales: ${url}`
  const filled = phones.filter((p) => p.replace(/\D/g, '').length >= 10)

  return (
    <div className="max-w-5xl mx-auto p-6 overflow-y-auto h-full space-y-6">
      <Card>
        <h2 className="text-2xl font-bold">Encuestas a clientes reales</h2>
        <p className="text-sm text-adan-muted mt-1">
          ADÁN diseña la encuesta con lo que ya entendió de tu idea, preguntando por lo que la gente hizo y pagó (no por lo que haría).
          Tú la envías por WhatsApp a quien quieras y las respuestas se vuelven evidencia para el Gate.
        </p>
        <div className="mt-4 flex flex-col sm:flex-row gap-3">
          <input aria-label="Qué quieres averiguar" value={objective} onChange={(e) => setObjective(e.target.value)} maxLength={1000}
            placeholder="Opcional: qué quieres averiguar (ej. si pagarían por domicilio antes de las 7 a. m.)"
            className="flex-1 rounded-xl border border-adan-border bg-adan-bg px-3 py-2 text-sm" />
          <Button onClick={create} loading={busy === 'create'}>{list.length ? 'Crear otra encuesta' : 'Crear la encuesta'}</Button>
        </div>
        {list.length > 1 && (
          <div className="mt-3 flex flex-wrap gap-2 text-xs">
            {list.map((s) => (
              <button key={s.token} type="button" onClick={() => open(s.token)}
                className={`rounded-full border px-3 py-1 ${results?.token === s.token ? 'border-adan-accent' : 'border-adan-border'}`}>
                {s.titulo} · {s.responses}
              </button>
            ))}
          </div>
        )}
      </Card>

      {results && (
        <>
          <Card>
            <h3 className="font-bold">Envíala por WhatsApp</h3>
            <p className="text-xs text-adan-muted mt-1">
              Escribe hasta 10 números con indicativo (ej. 573001234567). Cada botón abre WhatsApp con el mensaje listo; tú decides enviarlo.
              Los números no se guardan. Escríbele solo a personas que conoces o que aceptaron recibirlo, y en horario razonable.
            </p>
            <input aria-label="Tu nombre" value={sender} onChange={(e) => setSender(e.target.value)} placeholder="Tu nombre (opcional, para el saludo)"
              className="mt-3 w-full sm:w-80 rounded-xl border border-adan-border bg-adan-bg px-3 py-2 text-sm" />
            <div className="mt-3 grid gap-2 sm:grid-cols-2">
              {phones.map((p, i) => (
                <div key={i} className="flex gap-2">
                  <input aria-label={`Teléfono ${i + 1}`} inputMode="tel" value={p} placeholder={`Teléfono ${i + 1}`}
                    onChange={(e) => setPhones(phones.map((x, j) => (j === i ? e.target.value : x)))}
                    className="flex-1 rounded-xl border border-adan-border bg-adan-bg px-3 py-2 text-sm" />
                  {p.replace(/\D/g, '').length >= 10 && (
                    <a href={waLink(p, message)} target="_blank" rel="noreferrer" data-testid="wa-link"
                      className="rounded-xl bg-[#25D366] px-3 py-2 text-sm font-semibold text-black">WhatsApp ↗</a>
                  )}
                </div>
              ))}
            </div>
            <div className="mt-3 flex flex-wrap items-center gap-3 text-xs text-adan-muted">
              <span>{filled.length} listos para enviar</span>
              <button type="button" onClick={() => navigator.clipboard?.writeText(url)} className="underline">Copiar el enlace de la encuesta</button>
              <a href={url} target="_blank" rel="noreferrer" className="underline">Ver como la ve el encuestado ↗</a>
            </div>
          </Card>

          <Card>
            <div className="flex flex-wrap items-center justify-between gap-2">
              <h3 className="font-bold">{results.titulo}</h3>
              <span className="text-sm text-adan-muted" data-testid="survey-count">{results.responses} respuestas</span>
            </div>
            <div className="mt-4 grid gap-4 md:grid-cols-2">
              {results.questions.map((q) => (
                <div key={q.id} className="rounded-xl border border-adan-border p-3">
                  <p className="text-sm font-medium">{q.texto}</p>
                  <p className="text-[11px] text-adan-muted">Valida: {q.por_que} · {q.answered} respuestas</p>
                  {q.counts && <Bars counts={q.counts} total={q.answered} />}
                  {q.average !== undefined && q.average !== null && <p className="mt-1 text-sm">Promedio: <b>{q.average}</b></p>}
                  {q.texts && q.texts.length > 0 && (
                    <ul className="mt-2 max-h-32 overflow-y-auto space-y-1 text-xs">{q.texts.map((t, i) => <li key={i}>“{t}”</li>)}</ul>
                  )}
                </div>
              ))}
            </div>
            <Button className="mt-4" onClick={analyze} loading={busy === 'insights'} disabled={results.responses < 3}>
              {results.responses < 3 ? 'Se necesitan al menos 3 respuestas para analizar' : 'Analizar con ADÁN'}
            </Button>
            {insights && (
              <div className="mt-4 space-y-3 text-sm" data-testid="survey-insights">
                <p>{insights.resumen}</p>
                {insights.hallazgos.length > 0 && <ul className="list-disc pl-5">{insights.hallazgos.map((h) => <li key={h}>{h}</li>)}</ul>}
                {insights.alertas.length > 0 && <p className="text-xs text-adan-warning">⚠️ {insights.alertas.join(' · ')}</p>}
                {insights.evidencia_sugerida.map((e) => (
                  <div key={e.afirmacion} className="rounded-xl border border-adan-border p-3">
                    <p>{e.afirmacion}</p>
                    <p className="text-xs text-adan-muted">{e.polaridad === 'contradicts' ? 'Va en contra del problema · ' : ''}{e.fuente}</p>
                    <Button size="sm" variant="secondary" className="mt-2" disabled={registered.includes(e.afirmacion)}
                      onClick={async () => {
                        try {
                          await api.addEvidence(companyId, { claim: e.afirmacion, kind: 'testimony', polarity: e.polaridad, source: e.fuente })
                          setRegistered((r) => [...r, e.afirmacion])
                          onChanged()
                        } catch (err) { onError(errorMessage(err)) }
                      }}>
                      {registered.includes(e.afirmacion) ? '✓ Registrada' : 'Registrar como evidencia'}
                    </Button>
                  </div>
                ))}
              </div>
            )}
          </Card>
        </>
      )}
    </div>
  )
}
