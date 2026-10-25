import { useCallback, useEffect, useState } from 'react'
import Button from '../../components/ui/Button'
import Card from '../../components/ui/Card'
import { LoadingState } from '../../components/ui/States'
import { api, errorMessage } from '../../lib/api'
import type { SurveyInsights, SurveyResults, SurveySimulation, SurveySummary } from '../../types'

// Enlace de WhatsApp armado en el navegador: los contactos nunca llegan al servidor (Ley 1581, mínimo dato)
function waLink(phone: string, message: string) {
  const digits = phone.replace(/\D/g, '')
  return `https://wa.me/${digits}?text=${encodeURIComponent(message)}`
}

interface Contact { name: string; email: string; phone: string }

// Lista pegada o cargada (CSV o texto): una persona por línea, con nombre, correo y/o celular en cualquier orden
function parseContacts(text: string): Contact[] {
  return text.split(/\r?\n/).map((line) => {
    const email = line.match(/[\w.+-]+@[\w-]+\.[\w.]+/)?.[0] ?? ''
    const phone = (line.replace(email, '').match(/\+?\d[\d\s().-]{8,}\d/)?.[0] ?? '').replace(/\D/g, '')
    const name = line.replace(email, '').replace(/\+?\d[\d\s().-]{8,}\d/, '').replace(/[,;\t|]+/g, ' ').trim()
    return { name, email, phone }
  }).filter((c) => c.email || c.phone.length >= 10)
}

// Comparación con la simulación: diferencia en puntos porcentuales por opción
function SimBars({ sim, real, total }: { sim: Record<string, number>; real?: Record<string, number>; total: number }) {
  const simTotal = Object.values(sim).reduce((a, b) => a + b, 0) || 1
  return (
    <div className="mt-2 space-y-1">
      {Object.entries(sim).map(([label, n]) => {
        const sp = Math.round((n / simTotal) * 100)
        const rp = real && total ? Math.round(((real[label] ?? 0) / total) * 100) : null
        const gap = rp !== null && Math.abs(sp - rp) >= 20
        return (
          <div key={label} className="text-xs">
            <div className="flex justify-between"><span>{label}</span>
              <span className={gap ? 'text-adan-warning font-semibold' : 'text-adan-muted'}>simulada {sp} %{rp !== null ? ` · real ${rp} %` : ''}{gap ? ' ⚠️' : ''}</span></div>
            <div className="h-2 rounded-full bg-adan-bg overflow-hidden"><div className="h-full bg-violet-400/80" style={{ width: `${sp}%` }} /></div>
          </div>
        )
      })}
    </div>
  )
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
  const [contactsText, setContactsText] = useState('')
  const [simulation, setSimulation] = useState<SurveySimulation | null>(null)
  const [sender, setSender] = useState('')
  const [busy, setBusy] = useState<string | null>(null)
  const [registered, setRegistered] = useState<string[]>([])

  const open = useCallback(async (token: string) => {
    try {
      const r = await api.getSurveyResults(companyId, token)
      setResults(r)
      setSimulation(r.simulation ?? null)
      setInsights(null)
    } catch (err) { onError(errorMessage(err)) }
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
  // Las conclusiones de la encuesta real se registran solas como evidencia
  const analyze = async () => {
    if (!results) return
    setBusy('insights')
    try {
      const ins = await api.getSurveyInsights(companyId, results.token)
      setInsights(ins)
      for (const e of ins.evidencia_sugerida) {
        try {
          await api.addEvidence(companyId, { claim: e.afirmacion, kind: 'testimony', polarity: e.polaridad, source: e.fuente })
          setRegistered((r) => [...r, e.afirmacion])
        } catch { /* ya registrada o no válida */ }
      }
      onChanged()
    } catch (err) { onError(errorMessage(err)) } finally { setBusy(null) }
  }
  // Encuesta simulada: el Simulador de Mercado responde ya para no detener el avance
  const simulate = async () => {
    if (!results) return
    setBusy('simulate')
    try { setSimulation(await api.simulateSurvey(companyId, results.token)) } catch (err) { onError(errorMessage(err)) } finally { setBusy(null) }
  }

  if (list === null) return <LoadingState label="Cargando encuestas..." />
  const url = results ? `${window.location.origin}/encuesta/${results.token}` : ''
  const message = `Hola${sender ? `, soy ${sender}` : ''}. Estoy investigando cómo resolver un problema y tu opinión me ayudaría mucho. ` +
    `Son 2 minutos, anónimo, sin datos personales: ${url}`
  const contacts = parseContacts(contactsText)
  const emails = contacts.filter((c) => c.email).map((c) => c.email)
  const mailAll = `mailto:?bcc=${encodeURIComponent(emails.join(','))}&subject=${encodeURIComponent('¿Me ayudas con 2 minutos?')}&body=${encodeURIComponent(message)}`

  return (
    <div className="max-w-5xl mx-auto p-6 overflow-y-auto h-full space-y-6">
      <Card>
        <h2 className="text-2xl font-bold">Encuestas a clientes reales</h2>
        <p className="text-sm text-adan-muted mt-1">
          ADÁN diseña la encuesta con lo que ya entendió de tu idea, preguntando por lo que la gente hizo y pagó (no por lo que haría).
          Mientras la real llega, la simulada te deja avanzar; las conclusiones se registran solas como evidencia.
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
            <h3 className="font-bold">🧪 Encuesta simulada (para avanzar ya)</h3>
            <p className="text-xs text-adan-muted mt-1">
              El Simulador de Mercado responde como 50 personas del segmento. Sirve para no perder el ritmo mientras llegan las
              respuestas reales; cuando lleguen, ADÁN las contrasta y marca con ⚠️ las diferencias fuertes.
            </p>
            {simulation ? (
              <p className="mt-2 text-xs">Simulada con {simulation.size} personas: {simulation.perfil}. {simulation.supuestos.join(' · ')}</p>
            ) : (
              <Button className="mt-3" onClick={simulate} loading={busy === 'simulate'}>Simular 50 respuestas</Button>
            )}
          </Card>

          <Card>
            <h3 className="font-bold">📨 Encuesta real: tus contactos</h3>
            <p className="text-xs text-adan-muted mt-1">
              Pega o carga tu lista (una persona por línea, con nombre, correo y/o celular). Se queda en tu navegador: no se guarda.
              Escríbele solo a quien te conoce o aceptó recibirla.
            </p>
            <input aria-label="Tu nombre" value={sender} onChange={(e) => setSender(e.target.value)} placeholder="Tu nombre (para el saludo)"
              className="mt-3 w-full sm:w-80 rounded-xl border border-adan-border bg-adan-bg px-3 py-2 text-sm" />
            <textarea aria-label="Lista de contactos" value={contactsText} onChange={(e) => setContactsText(e.target.value)} rows={4}
              placeholder={'Ana Pérez, ana@correo.com, 573001234567\nCarlos Ruiz; 573109876543'}
              className="mt-2 w-full rounded-xl border border-adan-border bg-adan-bg px-3 py-2 text-sm font-mono" />
            <label className="mt-2 inline-block cursor-pointer text-xs text-adan-accent underline">
              Cargar archivo CSV o TXT
              <input type="file" accept=".csv,.txt" className="hidden" aria-label="Cargar contactos"
                onChange={async (e) => { const f = e.target.files?.[0]; e.target.value = ''; if (f) setContactsText(await f.text()) }} />
            </label>
            {contacts.length > 0 && (
              <div className="mt-3 space-y-2">
                <div className="flex flex-wrap items-center gap-3 text-xs">
                  <span>{contacts.length} contactos · {emails.length} con correo</span>
                  {emails.length > 0 && <a href={mailAll} className="rounded-xl bg-adan-accent px-3 py-1.5 font-semibold text-white">✉️ Enviar a todos por correo</a>}
                </div>
                <ul className="max-h-56 overflow-y-auto divide-y divide-adan-border text-sm">
                  {contacts.map((c, i) => (
                    <li key={i} className="flex items-center justify-between gap-2 py-1.5">
                      <span className="min-w-0 truncate">{c.name || c.email || c.phone}</span>
                      <span className="flex shrink-0 gap-1">
                        {c.phone.length >= 10 && <a href={waLink(c.phone, message)} target="_blank" rel="noreferrer" data-testid="wa-link"
                          className="rounded-lg bg-[#25D366] px-2 py-1 text-xs font-semibold text-black">WhatsApp ↗</a>}
                        {c.email && <a href={`mailto:${c.email}?subject=${encodeURIComponent('¿Me ayudas con 2 minutos?')}&body=${encodeURIComponent(message)}`}
                          className="rounded-lg border border-adan-border px-2 py-1 text-xs">Correo ↗</a>}
                      </span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
            <div className="mt-3 flex flex-wrap items-center gap-3 text-xs text-adan-muted">
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
                  {(() => {
                    const sq = simulation?.questions.find((x) => x.id === q.id)
                    if (!sq) return null
                    return (
                      <div className="mt-2 rounded-lg bg-violet-400/5 p-2">
                        <p className="text-[11px] font-semibold text-violet-300">Simulada</p>
                        {sq.counts && <SimBars sim={sq.counts} real={q.answered ? q.counts : undefined} total={q.answered} />}
                        {sq.average ? <p className="text-xs">Promedio simulado: <b>{sq.average}</b></p> : null}
                        {sq.texts && sq.texts.length > 0 && <ul className="text-xs">{sq.texts.map((t, k) => <li key={k}>“{t}”</li>)}</ul>}
                      </div>
                    )
                  })()}
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
                    {registered.includes(e.afirmacion) && <p className="mt-1 text-xs text-adan-success">✓ Registrada como evidencia</p>}
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
