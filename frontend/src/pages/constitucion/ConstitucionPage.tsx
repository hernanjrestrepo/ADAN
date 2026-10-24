import { useEffect, useState } from 'react'
import ReactMarkdown from 'react-markdown'
import { useParams } from 'react-router'
import AppShell from '../../components/AppShell'
import Alert from '../../components/ui/Alert'
import Button from '../../components/ui/Button'
import Card from '../../components/ui/Card'
import { LoadingState } from '../../components/ui/States'
import { api, errorMessage } from '../../lib/api'
import type { Company, DomainCheck, LegalGuide, NameCheck, Partner, Statutes } from '../../types'

const COUNTRIES = ['Colombia', 'México', 'Estados Unidos', 'España', 'Perú', 'Chile', 'Argentina', 'Ecuador', 'Panamá',
  'Costa Rica', 'República Dominicana', 'Brasil', 'Canadá', 'Reino Unido', 'Portugal']

const VERDICT: Record<NameCheck['veredicto'], { label: string; className: string; icon: string }> = {
  libre_probable: { label: 'Probablemente libre', className: 'border-adan-success/40 bg-adan-success/10', icon: '✅' },
  conflicto: { label: 'Hay conflicto', className: 'border-adan-danger/40 bg-adan-danger/10', icon: '⛔' },
  incierto: { label: 'No se pudo confirmar', className: 'border-yellow-500/40 bg-yellow-500/10', icon: '⚠️' },
}
const DOMAIN: Record<DomainCheck['status'], { label: string; className: string }> = {
  disponible: { label: 'Libre', className: 'text-adan-success' },
  probable_libre: { label: 'Probablemente libre (sin DNS)', className: 'text-emerald-300' },
  registrado: { label: 'Ocupado', className: 'text-red-300' },
  sin_confirmar: { label: 'Sin confirmar', className: 'text-yellow-300' },
}

function Searched({ yes }: { yes: boolean }) {
  return yes
    ? <span className="rounded-full bg-adan-success/15 px-2.5 py-1 text-xs text-adan-success">🌐 Investigado en internet</span>
    : <span className="rounded-full bg-yellow-500/15 px-2.5 py-1 text-xs text-yellow-300">Sin búsqueda en internet: verifícalo</span>
}

const input = 'w-full rounded-xl border border-adan-border bg-adan-bg px-3 py-2 text-sm focus:border-adan-accent focus:outline-hidden'

// 1. Nombre y dominio
function NameSection({ companyId, initial, country, onError }: { companyId: string; initial: string; country: string; onError: (m: string) => void }) {
  const [name, setName] = useState(initial)
  const [busy, setBusy] = useState(false)
  const [result, setResult] = useState<NameCheck | null>(null)
  const check = async (value = name) => {
    setName(value)
    setBusy(true)
    try { setResult(await api.checkName(companyId, value, country)) } catch (err) { onError(errorMessage(err)) } finally { setBusy(false) }
  }
  return (
    <Card>
      <p className="text-xs font-semibold tracking-[0.25em] text-adan-accent">PASO 1</p>
      <h2 className="text-xl font-bold mt-1">El nombre y el dominio</h2>
      <p className="text-sm text-adan-muted mt-1">ADÁN busca si ya existe una empresa o marca con ese nombre y qué dominios están libres.</p>
      <div className="mt-4 flex flex-col sm:flex-row gap-3">
        <input aria-label="Nombre de la empresa" value={name} onChange={(e) => setName(e.target.value)} maxLength={120} className={input} />
        <Button onClick={() => check()} loading={busy} disabled={name.trim().length < 2}>Verificar</Button>
      </div>
      {busy && <p className="mt-3 text-sm text-adan-muted animate-pulse">Buscando empresas, marcas y dominios… (unos 30 segundos)</p>}
      {result && !busy && (
        <div className="mt-5 space-y-4" data-testid="name-result">
          <div className={`rounded-xl border p-4 ${VERDICT[result.veredicto].className}`}>
            <div className="flex flex-wrap items-center justify-between gap-2">
              <p className="font-bold">{VERDICT[result.veredicto].icon} {VERDICT[result.veredicto].label}</p>
              <Searched yes={result.searched} />
            </div>
            <p className="text-sm mt-2">{result.explicacion}</p>
            {result.coincidencias.length > 0 && (
              <ul className="mt-3 space-y-1 text-sm">
                {result.coincidencias.map((c) => (
                  <li key={c.nombre + c.fuente}>• <b>{c.nombre}</b> ({c.tipo}, {c.donde}){c.fuente.startsWith('http') && <> · <a href={c.fuente} target="_blank" rel="noreferrer" className="text-adan-accent underline">fuente</a></>}</li>
                ))}
              </ul>
            )}
          </div>
          {result.alternativas.length > 0 && (
            <div>
              <p className="text-sm font-semibold">Otras opciones de nombre</p>
              <div className="mt-2 flex flex-wrap gap-2">
                {result.alternativas.map((a) => (
                  <button key={a} type="button" onClick={() => check(a)} className="rounded-full border border-adan-border px-3 py-1 text-sm hover:border-adan-accent">{a}</button>
                ))}
              </div>
            </div>
          )}
          <div>
            <p className="text-sm font-semibold">Dominios</p>
            <div className="mt-2 grid gap-2 sm:grid-cols-2 lg:grid-cols-4">
              {result.domains.map((d) => (
                <div key={d.domain} className="rounded-xl border border-adan-border p-3" data-testid="domain">
                  <p className="font-mono text-sm break-all">{d.domain}</p>
                  <p className={`text-xs font-semibold ${DOMAIN[d.status].className}`}>{DOMAIN[d.status].label}</p>
                  <p className="text-xs text-adan-muted">USD {d.usd_min}–{d.usd_max} el primer año · {d.nota}</p>
                </div>
              ))}
            </div>
            <p className="mt-2 text-xs text-adan-muted">{result.prices_note}</p>
            <div className="mt-3 flex flex-wrap gap-2">
              {result.registrars.map((r) => (
                <a key={r.name} href={r.url} target="_blank" rel="noreferrer" title={r.nota}
                  className="rounded-lg border border-adan-border px-3 py-1.5 text-sm hover:border-adan-accent">Comprar en {r.name} ↗</a>
              ))}
            </div>
          </div>
          {result.registros_oficiales.length > 0 && (
            <div className="text-sm">
              <p className="font-semibold">Confírmalo en el registro oficial</p>
              <ul className="mt-1 space-y-1">
                {result.registros_oficiales.map((r) => (
                  <li key={r.url}>• <a href={r.url} target="_blank" rel="noreferrer" className="text-adan-accent underline">{r.nombre}</a>: {r.que_verificar}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </Card>
  )
}

// 2. País y ruta legal
function GuideSection({ companyId, guide, setGuide, onError }: { companyId: string; guide: LegalGuide | null; setGuide: (g: LegalGuide) => void; onError: (m: string) => void }) {
  const [country, setCountry] = useState(guide?.pais ?? '')
  const [busy, setBusy] = useState(false)
  const build = async () => {
    setBusy(true)
    try { setGuide(await api.buildLegalGuide(companyId, country)) } catch (err) { onError(errorMessage(err)) } finally { setBusy(false) }
  }
  const toggle = async (i: number) => {
    if (!guide) return
    try { setGuide(await api.markLegalStep(companyId, i, !guide.done[i])) } catch (err) { onError(errorMessage(err)) }
  }
  const done = guide ? guide.done.filter(Boolean).length : 0
  return (
    <Card>
      <p className="text-xs font-semibold tracking-[0.25em] text-adan-accent">PASO 2</p>
      <h2 className="text-xl font-bold mt-1">¿En qué país la vas a crear?</h2>
      <p className="text-sm text-adan-muted mt-1">Escoge el país pensando en tu mercado y en los impuestos. ADÁN arma la ruta legal completa, explicada paso a paso.</p>
      <div className="mt-4 flex flex-col sm:flex-row gap-3">
        <input aria-label="País" list="paises" value={country} onChange={(e) => setCountry(e.target.value)} maxLength={80} placeholder="Colombia" className={input} />
        <datalist id="paises">{COUNTRIES.map((c) => <option key={c} value={c} />)}</datalist>
        <Button onClick={build} loading={busy} disabled={country.trim().length < 2}>{guide ? 'Rehacer la ruta' : 'Armar mi ruta legal'}</Button>
      </div>
      {busy && <div className="mt-4"><LoadingState label="Investigando leyes, entidades, costos y trámites del país… (1 a 2 minutos)" /></div>}
      {guide && !busy && (
        <div className="mt-6 space-y-5" data-testid="legal-guide">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <h3 className="text-lg font-bold">Ruta legal en {guide.pais}</h3>
            <Searched yes={guide.searched} />
          </div>
          <p className="text-sm">{guide.resumen}</p>
          <div className="grid gap-3 md:grid-cols-2">
            <div className="rounded-xl border border-adan-accent/40 bg-adan-accent/5 p-4">
              <p className="text-xs text-adan-muted">Tipo de sociedad recomendado</p>
              <p className="text-lg font-bold">{guide.recomendada.nombre}</p>
              <p className="text-sm mt-1">{guide.recomendada.por_que}</p>
            </div>
            <div className="rounded-xl border border-adan-accent/40 bg-adan-accent/5 p-4">
              <p className="text-xs text-adan-muted">Régimen tributario recomendado</p>
              <p className="text-lg font-bold">{guide.regimen_recomendado.nombre}</p>
              <p className="text-sm mt-1">{guide.regimen_recomendado.por_que}</p>
            </div>
          </div>
          <details>
            <summary className="cursor-pointer text-sm font-semibold">Comparar los tipos de sociedad ({guide.tipos_sociedad.length})</summary>
            <div className="mt-3 grid gap-3 md:grid-cols-2">
              {guide.tipos_sociedad.map((t) => (
                <div key={t.nombre} className="rounded-xl border border-adan-border p-3 text-sm">
                  <p className="font-bold">{t.nombre}</p>
                  <p className="text-xs text-adan-muted">{t.para_quien} · Socios: {t.socios} · {t.responsabilidad}</p>
                  <p className="mt-2 text-adan-success text-xs">+ {t.ventajas.join(' · ')}</p>
                  <p className="text-red-300 text-xs">− {t.desventajas.join(' · ')}</p>
                </div>
              ))}
            </div>
          </details>
          <details>
            <summary className="cursor-pointer text-sm font-semibold">Comparar los regímenes tributarios ({guide.regimenes.length})</summary>
            <div className="mt-3 grid gap-3 md:grid-cols-2">
              {guide.regimenes.map((r) => (
                <div key={r.nombre} className="rounded-xl border border-adan-border p-3 text-sm">
                  <p className="font-bold">{r.nombre}</p>
                  <p className="text-xs text-adan-muted">Quién puede: {r.quien_puede}</p>
                  <p className="mt-1">{r.como_funciona}</p>
                  <p className="text-xs mt-1 text-adan-accent">Te conviene si: {r.conviene_si}</p>
                </div>
              ))}
            </div>
          </details>
          <div>
            <div className="flex items-center justify-between">
              <h3 className="font-bold">Paso a paso</h3>
              <span className="text-sm text-adan-muted">{done} de {guide.pasos.length} hechos</span>
            </div>
            <div className="mt-2 h-2 rounded-full bg-adan-bg overflow-hidden">
              <div className="h-full bg-adan-success transition-all" style={{ width: `${(done / Math.max(1, guide.pasos.length)) * 100}%` }} />
            </div>
            <ol className="mt-3 space-y-2">
              {guide.pasos.map((p, i) => (
                <li key={p.titulo + i} className={`rounded-xl border p-3 ${guide.done[i] ? 'border-adan-success/40 bg-adan-success/5' : 'border-adan-border'}`} data-testid="legal-step">
                  <div className="flex items-start gap-3">
                    <input type="checkbox" checked={guide.done[i] ?? false} onChange={() => toggle(i)} aria-label={`Marcar como hecho: ${p.titulo}`} className="mt-1 h-4 w-4" />
                    <details className="flex-1 min-w-0">
                      <summary className="cursor-pointer font-medium">{i + 1}. {p.titulo} <span className="text-xs text-adan-muted">· {p.costo} · {p.tiempo}</span></summary>
                      <div className="mt-2 space-y-2 text-sm">
                        <p>{p.que_es}</p>
                        <p><b>Dónde:</b> {p.donde}{p.url.startsWith('http') && <> · <a href={p.url} target="_blank" rel="noreferrer" className="text-adan-accent underline">sitio oficial ↗</a></>}</p>
                        {p.documentos.length > 0 && <p><b>Documentos:</b> {p.documentos.join(' · ')}</p>}
                        {p.errores_comunes.length > 0 && <p className="text-yellow-300"><b>Errores comunes:</b> {p.errores_comunes.join(' · ')}</p>}
                      </div>
                    </details>
                  </div>
                </li>
              ))}
            </ol>
          </div>
          <div className="grid gap-3 md:grid-cols-2 text-sm">
            <div className="rounded-xl bg-adan-bg p-3"><b>Costo total estimado:</b> {guide.costo_total}</div>
            <div className="rounded-xl bg-adan-bg p-3"><b>Tiempo total estimado:</b> {guide.tiempo_total}</div>
          </div>
          {guide.obligaciones.length > 0 && (
            <div className="text-sm"><p className="font-semibold">Obligaciones del primer año</p>
              <ul className="list-disc pl-5 mt-1 space-y-1">{guide.obligaciones.map((o) => <li key={o}>{o}</li>)}</ul></div>
          )}
          {guide.fuentes.length > 0 && (
            <p className="text-xs text-adan-muted">Fuentes: {guide.fuentes.map((f, i) => (
              <span key={f.url}>{i > 0 && ' · '}<a href={f.url} target="_blank" rel="noreferrer" className="underline">{f.nombre}</a></span>
            ))}</p>
          )}
          <p className="text-xs text-adan-warning">{guide.disclaimer}</p>
        </div>
      )}
    </Card>
  )
}

// 3. Estatutos
function StatutesSection({ companyId, company, guide, onError }: { companyId: string; company: Company | null; guide: LegalGuide | null; onError: (m: string) => void }) {
  const [form, setForm] = useState({ nombre: company?.name ?? '', domicilio: '', objeto: company?.description ?? '', capital: '', administracion: '' })
  const [socios, setSocios] = useState<Partner[]>([{ nombre: '', documento: '', aporte: '', porcentaje: 100 }])
  const [busy, setBusy] = useState(false)
  const [result, setResult] = useState<Statutes | null>(null)
  const pais = guide?.pais ?? ''
  const tipo = guide?.recomendada.nombre ?? ''
  const generate = async () => {
    setBusy(true)
    try {
      setResult(await api.draftStatutes(companyId, { pais, tipo, ...form, socios: socios.filter((s) => s.nombre.trim()) }))
    } catch (err) { onError(errorMessage(err)) } finally { setBusy(false) }
  }
  const field = (key: keyof typeof form, label: string, placeholder = '') => (
    <label className="block text-sm">
      <span className="text-adan-muted">{label}</span>
      <input value={form[key]} onChange={(e) => setForm({ ...form, [key]: e.target.value })} placeholder={placeholder} className={`${input} mt-1`} />
    </label>
  )
  return (
    <Card>
      <p className="text-xs font-semibold tracking-[0.25em] text-adan-accent">PASO 3</p>
      <h2 className="text-xl font-bold mt-1">Los estatutos de tu empresa</h2>
      {!guide ? (
        <p className="text-sm text-adan-muted mt-2">Primero arma la ruta legal: los estatutos dependen del país y del tipo de sociedad.</p>
      ) : (
        <>
          <p className="text-sm text-adan-muted mt-1">Borrador para {tipo} en {pais}. Donde falte un dato quedará marcado para completar; revísalo con un abogado antes de firmarlo.</p>
          <div className="mt-4 grid gap-3 md:grid-cols-2">
            {field('nombre', 'Razón social')}
            {field('domicilio', 'Domicilio (ciudad)', 'Barranquilla')}
            {field('capital', 'Capital', 'COP 10.000.000')}
            {field('administracion', 'Quién la administra', 'Un gerente que es el representante legal')}
          </div>
          <label className="block text-sm mt-3"><span className="text-adan-muted">Objeto social (a qué se dedica)</span>
            <textarea value={form.objeto} onChange={(e) => setForm({ ...form, objeto: e.target.value })} rows={2} className={`${input} mt-1`} /></label>
          <p className="text-sm font-semibold mt-4">Socios o accionistas</p>
          <div className="mt-2 space-y-2">
            {socios.map((s, i) => (
              <div key={i} className="grid gap-2 sm:grid-cols-[2fr_1fr_1fr_80px_auto]">
                <input aria-label={`Socio ${i + 1}: nombre`} placeholder="Nombre completo" value={s.nombre} className={input}
                  onChange={(e) => setSocios(socios.map((x, j) => (j === i ? { ...x, nombre: e.target.value } : x)))} />
                <input aria-label={`Socio ${i + 1}: documento`} placeholder="Documento" value={s.documento} className={input}
                  onChange={(e) => setSocios(socios.map((x, j) => (j === i ? { ...x, documento: e.target.value } : x)))} />
                <input aria-label={`Socio ${i + 1}: aporte`} placeholder="Aporte" value={s.aporte} className={input}
                  onChange={(e) => setSocios(socios.map((x, j) => (j === i ? { ...x, aporte: e.target.value } : x)))} />
                <input aria-label={`Socio ${i + 1}: porcentaje`} type="number" min={0} max={100} value={s.porcentaje ?? ''} className={input}
                  onChange={(e) => setSocios(socios.map((x, j) => (j === i ? { ...x, porcentaje: Number(e.target.value) } : x)))} />
                <Button variant="ghost" onClick={() => setSocios(socios.filter((_, j) => j !== i))} disabled={socios.length === 1}>Quitar</Button>
              </div>
            ))}
            <Button variant="secondary" size="sm" onClick={() => setSocios([...socios, { nombre: '', documento: '', aporte: '', porcentaje: 0 }])}>+ Agregar socio</Button>
          </div>
          <Button className="mt-4" onClick={generate} loading={busy}>Redactar los estatutos</Button>
          {busy && <p className="mt-2 text-sm text-adan-muted animate-pulse">Redactando según la ley de {pais}… (1 a 2 minutos)</p>}
          {result && !busy && (
            <div className="mt-5" data-testid="statutes">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <p className="font-semibold">{result.title}</p>
                <Button size="sm" variant="secondary" onClick={() => api.downloadStatutes(companyId, result.id).catch((err: unknown) => onError(errorMessage(err)))}>⬇ Descargar en Word</Button>
              </div>
              <div className="mt-3 max-h-[60vh] overflow-y-auto rounded-xl bg-adan-bg p-4 text-sm markdown"><ReactMarkdown>{result.markdown}</ReactMarkdown></div>
            </div>
          )}
        </>
      )}
    </Card>
  )
}

// Constitución de la empresa: nombre, país y ruta legal, estatutos (para quien no sabe nada de empresas)
export default function ConstitucionPage() {
  const { companyId = '' } = useParams()
  const [company, setCompany] = useState<Company | null>(null)
  const [guide, setGuide] = useState<LegalGuide | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    Promise.all([
      api.getCompany(companyId).then((c) => { if (!cancelled) setCompany(c) }),
      api.getLegalGuide(companyId).then((g) => { if (!cancelled) setGuide(g) }).catch(() => undefined),
    ]).catch((err: unknown) => { if (!cancelled) setError(errorMessage(err)) })
      .finally(() => { if (!cancelled) setLoading(false) })
    return () => { cancelled = true }
  }, [companyId])

  return (
    <AppShell crumbs={[{ label: 'Mis Empresas', to: '/dashboard' }, { label: company?.name ?? 'Empresa', to: `/ruta/${companyId}` }, { label: 'Constitución' }]}>
      <div className="max-w-5xl mx-auto p-4 sm:p-6 overflow-y-auto h-full space-y-6">
        {error && <Alert message={error} onClose={() => setError(null)} />}
        <div>
          <h1 className="text-3xl font-bold">Constituye tu empresa</h1>
          <p className="text-adan-muted mt-1">El nombre, el país, la ruta legal y los estatutos, explicados como si fuera la primera vez. Nada se da por sabido.</p>
        </div>
        {loading ? <LoadingState label="Cargando..." /> : (
          <>
            <NameSection companyId={companyId} initial={company?.name ?? ''} country={guide?.pais ?? company?.country ?? ''} onError={setError} />
            <GuideSection companyId={companyId} guide={guide} setGuide={setGuide} onError={setError} />
            <StatutesSection key={guide?.id ?? 'sin-guia'} companyId={companyId} company={company} guide={guide} onError={setError} />
          </>
        )}
      </div>
    </AppShell>
  )
}
