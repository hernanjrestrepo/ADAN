import { useCallback, useEffect, useRef, useState } from 'react'
import ReactMarkdown from 'react-markdown'
import { Link, useParams } from 'react-router'
import AppShell from '../../components/AppShell'
import Portrait from '../../components/Portrait'
import Alert from '../../components/ui/Alert'
import Button from '../../components/ui/Button'
import Card from '../../components/ui/Card'
import { LoadingState } from '../../components/ui/States'
import { api, errorMessage } from '../../lib/api'
import type { Graduation } from '../../types'
import { laugh } from '../../universo/voice'

// El cierre de todo el proceso: la graduación (certificado, celebración, Libro de la Empresa y Board final) y el modo
// continuo (los indicadores de cada mes, leídos contra el plan, y el Board cada trimestre).

const TEAM = ['ceo', 'cfo', 'cmo', 'cto', 'producto', 'legal', 'operaciones', 'investigador', 'genexis']
const CONFETTI = ['#f472b6', '#38bdf8', '#facc15', '#4ade80', '#a78bfa', '#fb923c']

function Confetti() {
  return (
    <div className="pointer-events-none fixed inset-0 z-40 overflow-hidden" aria-hidden="true">
      {Array.from({ length: 90 }, (_, i) => (
        <span key={i} className="adan-confetti" style={{
          left: `${(i * 37) % 100}%`, background: CONFETTI[i % CONFETTI.length],
          animationDelay: `${(i % 15) * 0.12}s`, animationDuration: `${2.6 + (i % 7) * 0.35}s`,
          transform: `rotate(${i * 23}deg)`,
        }} />
      ))}
    </div>
  )
}

function Certificate({ g }: { g: Graduation }) {
  const color = g.identidad?.color || '#2563eb'
  return (
    <div id="certificado" className="relative overflow-hidden rounded-2xl border-4 bg-white p-6 text-center text-slate-800 sm:p-10"
      style={{ borderColor: color }}>
      <p className="text-xs font-semibold uppercase tracking-[0.3em] text-slate-500">ADÁN by Paradixe certifica que</p>
      {g.identidad?.logo && <img src={g.identidad.logo} alt="" className="mx-auto mt-4 h-16 max-w-[180px] object-contain" />}
      <h2 className="mt-3 text-3xl font-bold sm:text-4xl" style={{ color }}>{g.empresa}</h2>
      <p className="mt-2 text-sm">fundada por <b>{g.fundador}</b></p>
      <p className="mx-auto mt-4 max-w-xl text-base">completó los <b>7 Niveles</b> de creación de empresa de ADÁN: el dolor, la propuesta de valor, el modelo de negocio y los números, el MVP, la validación, el lanzamiento y el escalamiento.</p>
      {g.frase && <p className="mt-4 text-lg italic" style={{ color }}>«{g.frase}»</p>}
      <div className="mt-6 flex flex-wrap items-end justify-center gap-8 text-xs text-slate-500">
        <span>{g.fecha ? new Date(g.fecha).toLocaleDateString('es-CO', { day: 'numeric', month: 'long', year: 'numeric' }) : ''}</span>
        <span className="font-mono">{g.certificado}</span>
        <span>♾️ Modo continuo activo</span>
      </div>
    </div>
  )
}

export default function GraduacionPage() {
  const { companyId = '' } = useParams()
  const [g, setG] = useState<Graduation | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [values, setValues] = useState<Record<string, string>>({})
  const [note, setNote] = useState('')
  const [busy, setBusy] = useState('')
  const [party, setParty] = useState(false)
  const celebrated = useRef(false)

  const load = useCallback(() => api.getGraduation(companyId).then(setG).catch((e: unknown) => setError(errorMessage(e))), [companyId])
  useEffect(() => { void load() }, [load])
  useEffect(() => {
    if (g?.estado !== 'preparando') return
    const id = window.setInterval(() => { void load() }, 8000)
    return () => window.clearInterval(id)
  }, [g?.estado, load])
  // La celebración: confeti y el equipo riéndose a carcajadas, una vez por visita
  useEffect(() => {
    if (!g?.graduada || celebrated.current) return
    celebrated.current = true
    const on = window.setTimeout(() => setParty(true), 0)
    TEAM.forEach((a, i) => window.setTimeout(() => laugh(a), 300 + i * 260))
    const off = window.setTimeout(() => setParty(false), 7000)
    return () => { window.clearTimeout(on); window.clearTimeout(off) }
  }, [g?.graduada])

  const start = async () => {
    setBusy('grad')
    try { setG(await api.graduate(companyId)) } catch (e) { setError(errorMessage(e)) } finally { setBusy('') }
  }
  const report = async () => {
    const valores = Object.fromEntries(Object.entries(values).filter(([, v]) => v.trim() !== '').map(([k, v]) => [k, Number(v)]))
    if (!Object.keys(valores).length) return
    setBusy('check')
    try {
      await api.checkIn(companyId, valores, note)
      setValues({})
      setNote('')
      await load()
    } catch (e) { setError(errorMessage(e)) } finally { setBusy('') }
  }

  if (!g) return <AppShell crumbs={[{ label: 'Graduación' }]}>{error ? <Alert message={error} /> : <LoadingState label="Abriendo…" />}</AppShell>
  return (
    <AppShell crumbs={[{ label: 'Mis Empresas', to: '/dashboard' }, { label: g.empresa ?? 'Empresa', to: `/gemelo/${companyId}` }, { label: 'Graduación' }]}>
      {party && <Confetti />}
      <main className="h-full overflow-y-auto">
        <div className="mx-auto max-w-4xl space-y-5 p-4 sm:p-6">
          <Alert message={error} onClose={() => setError(null)} />
          {!g.nivel7_cerrado ? (
            <Card>
              <h1 className="text-2xl font-bold">🎓 La graduación</h1>
              <p className="mt-2">Cuando cierres el Nivel 7, ADÁN convoca la sesión final del Board, te entrega el <b>Libro de la Empresa</b> con todo lo construido y el plan de 90 días, emite tu certificado y pasa a <b>modo continuo</b>.</p>
              <Link to={`/nivel/7/${companyId}`} className="mt-4 inline-block rounded-xl bg-adan-accent px-4 py-2 font-semibold text-white">Ir al Nivel 7</Link>
            </Card>
          ) : g.estado === 'preparando' ? (
            <Card>
              <h1 className="text-2xl font-bold">🎓 Preparando tu graduación…</h1>
              <p className="mt-2 animate-pulse text-sm">El Board sesiona por última vez y ADÁN escribe el Libro de la Empresa. Toma unos minutos; esta página se actualiza sola.</p>
            </Card>
          ) : !g.graduada ? (
            <Card>
              <h1 className="text-2xl font-bold">🎓 ¡Cerraste los 7 Niveles!</h1>
              <p className="mt-2 text-sm">{g.estado === 'error' ? 'La preparación anterior no terminó. ' : ''}Prepara tu graduación: Board final, Libro de la Empresa y certificado.</p>
              <Button className="mt-4" onClick={start} loading={busy === 'grad'}>Preparar mi graduación</Button>
            </Card>
          ) : (
            <>
              <div className="flex flex-wrap items-center justify-center gap-2">
                {TEAM.map((a) => <span key={a} className="animate-bounce" style={{ animationDelay: `${TEAM.indexOf(a) * 0.1}s` }}><Portrait agent={a} size={44} /></span>)}
              </div>
              <Certificate g={g} />
              <div className="flex flex-wrap justify-center gap-2 print:hidden">
                <Button variant="secondary" onClick={() => window.print()}>🖨️ Imprimir o guardar en PDF</Button>
                <Button variant="secondary" onClick={() => { setParty(true); TEAM.forEach((a, i) => window.setTimeout(() => laugh(a), i * 220)); window.setTimeout(() => setParty(false), 6000) }}>🎉 Celebrar otra vez</Button>
              </div>

              {g.board && (
                <Card className="print:hidden">
                  <h2 className="text-lg font-bold">🏛️ Sesión final del Board</h2>
                  <p className="text-sm">Resultado: <b>{g.board.decision}</b> · preparación para operar y crecer: <b>{g.board.preparacion}/100</b>. El acta completa está en la Sala del Nivel 7 y en el Libro.</p>
                </Card>
              )}

              {g.libro && (
                <Card className="print:hidden">
                  <div className="flex flex-wrap items-start justify-between gap-2">
                    <h2 className="text-lg font-bold">📘 Libro de la Empresa</h2>
                    <Button size="sm" variant="secondary" onClick={() => api.downloadFile(`/empresa/${companyId}/biblioteca/${g.libro!.id}.docx`, `Libro de la Empresa - ${g.empresa}.docx`).catch((e: unknown) => setError(errorMessage(e)))}>Descargar Word</Button>
                  </div>
                  <details className="mt-2">
                    <summary className="cursor-pointer text-sm font-semibold">Leerlo aquí</summary>
                    <div className="markdown mt-2 max-h-[70vh] overflow-y-auto text-sm"><ReactMarkdown>{g.libro.markdown}</ReactMarkdown></div>
                  </details>
                </Card>
              )}

              <Card className="print:hidden">
                <h2 className="text-lg font-bold">♾️ Modo continuo</h2>
                <p className="text-sm text-adan-muted">Cada mes reporta tus indicadores: Camila los compara con el plan y te propone qué ajustar. Cada trimestre convoca el Board desde la Sala del Nivel 7.</p>
                {(g.kpis ?? []).length > 0 && (
                  <div className="mt-3 grid gap-2 sm:grid-cols-2">
                    {g.kpis!.map((k) => (
                      <label key={k.nombre} className="text-sm">
                        {k.nombre} <span className="text-xs text-adan-muted">(meta {k.meta} {k.unidad}, {k.frecuencia})</span>
                        <input type="number" value={values[k.nombre] ?? ''} onChange={(e) => setValues((v) => ({ ...v, [k.nombre]: e.target.value }))}
                          className="mt-1 w-full rounded-lg border border-adan-border bg-adan-bg px-3 py-1.5" />
                      </label>
                    ))}
                  </div>
                )}
                <textarea value={note} onChange={(e) => setNote(e.target.value)} rows={2} maxLength={500} placeholder="Nota del mes (opcional)"
                  aria-label="Nota del mes" className="mt-2 w-full rounded-lg border border-adan-border bg-adan-bg px-3 py-2 text-sm" />
                <div className="mt-2 flex flex-wrap gap-2">
                  <Button onClick={report} loading={busy === 'check'} disabled={!Object.values(values).some((v) => v.trim() !== '')}>Reportar el mes</Button>
                  <Link to={`/nivel/7/${companyId}`} className="rounded-xl border border-adan-border px-4 py-2 text-sm">🏛️ Board trimestral en la Sala</Link>
                </div>
                {g.seguimientos.length > 0 && (
                  <ul className="mt-4 space-y-3">
                    {[...g.seguimientos].reverse().map((s) => (
                      <li key={s.fecha} className="rounded-xl border border-adan-border p-3 text-sm">
                        <p className="text-xs text-adan-muted">{new Date(s.fecha).toLocaleDateString('es-CO', { month: 'long', year: 'numeric', day: 'numeric' })} · {Object.entries(s.valores).map(([k, v]) => `${k}: ${v}`).join(' · ')}</p>
                        {s.lectura && <div className="markdown mt-1"><ReactMarkdown>{s.lectura}</ReactMarkdown></div>}
                      </li>
                    ))}
                  </ul>
                )}
              </Card>
            </>
          )}
        </div>
      </main>
    </AppShell>
  )
}
