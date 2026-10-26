import { useEffect, useMemo, useState } from 'react'
import ReactMarkdown from 'react-markdown'
import { Link, useParams } from 'react-router'
import AppShell from '../../components/AppShell'
import Alert from '../../components/ui/Alert'
import Button from '../../components/ui/Button'
import Card from '../../components/ui/Card'
import { LoadingState } from '../../components/ui/States'
import { api, errorMessage } from '../../lib/api'
import type { Library, LibraryDoc } from '../../types'

// La Biblioteca de la empresa: la identidad viva (logo, paleta, tipografía, slogan) y todos los documentos que se
// van construyendo Nivel a Nivel, para encontrarlos, leerlos y descargarlos en un solo lugar.

const ICON: Record<LibraryDoc['seccion'], string> = {
  marca: '🏷️', legal: '⚖️', numeros: '🧮', estrategia: '🧭', board: '🏛️', cliente: '📎',
}

// Qué falta en cada sección vacía y dónde se construye
const EMPTY: Record<LibraryDoc['seccion'], string> = {
  marca: 'Aún no hay documentos de marca: el manual y el logo se crean en Marca.',
  legal: 'Aún no hay documentos legales: los estatutos, la ruta legal y los trámites se preparan en Constitución y en el Expediente.',
  numeros: 'Aún no hay documentos de números: el flujo de caja, el organigrama y el informe se construyen en Finanzas (Nivel 3).',
  estrategia: 'Aún no hay documentos de estrategia: los entregables de cada Nivel aparecen aquí al cerrarlo.',
  board: 'Aún no hay actas: aparecen cuando sesionan el Board (desde el Nivel 3) y La Arena (Nivel 5).',
  cliente: 'Aún no has subido archivos ni enlaces: súbelos o pégalos en el chat de la Sala.',
}
const LINKS: Partial<Record<LibraryDoc['seccion'], (id: string) => string>> = {
  marca: (id) => `/marca/${id}`, legal: (id) => `/expediente/${id}`, numeros: (id) => `/finanzas/${id}`,
}
const LINK_LABEL: Partial<Record<LibraryDoc['seccion'], string>> = { marca: 'Ir a Marca', legal: 'Ir al Expediente', numeros: 'Ir a Finanzas' }

const date = (iso: string | null) => (iso ? new Date(iso).toLocaleDateString('es-CO', { day: 'numeric', month: 'short', year: 'numeric' }) : '')

function contrast(hex: string): string {
  const n = parseInt(hex.replace('#', '').padEnd(6, '0').slice(0, 6), 16)
  const lum = (0.299 * ((n >> 16) & 255) + 0.587 * ((n >> 8) & 255) + 0.114 * (n & 255)) / 255
  return lum > 0.6 ? '#0f172a' : '#ffffff'
}

function Swatch({ nombre, hex }: { nombre: string; hex: string }) {
  const [copied, setCopied] = useState(false)
  const copy = () => {
    void navigator.clipboard?.writeText(hex).then(() => { setCopied(true); window.setTimeout(() => setCopied(false), 1200) })
  }
  return (
    <button type="button" onClick={copy} title={`Copiar ${hex}`}
      className="flex h-24 w-28 flex-col justify-end rounded-xl border border-adan-border p-2 text-left text-xs"
      style={{ background: hex, color: contrast(hex) }}>
      <b>{nombre}</b>
      <span className="font-mono">{copied ? '¡Copiado!' : hex.toUpperCase()}</span>
    </button>
  )
}

// La ficha de la empresa: los parámetros que usa todo el equipo (comisión, pasarela, mercado…). El fundador la
// corrige aquí y ADÁN la puede reconstruir releyendo todas las conversaciones.
function Ficha({ companyId, initial, onError }: { companyId: string; initial: Record<string, string>; onError: (m: string) => void }) {
  const [rows, setRows] = useState<[string, string][]>(() => Object.entries(initial))
  const [editing, setEditing] = useState(false)
  const [busy, setBusy] = useState('')
  const save = async () => {
    setBusy('save')
    try {
      const res = await api.updateFicha(companyId, Object.fromEntries(rows.filter(([k, v]) => k.trim() && v.trim())))
      setRows(Object.entries(res.ficha))
      setEditing(false)
    } catch (e) { onError(errorMessage(e)) } finally { setBusy('') }
  }
  const rebuild = async () => {
    setBusy('rebuild')
    try { setRows(Object.entries((await api.consolidateMemory(companyId)).ficha)) } catch (e) { onError(errorMessage(e)) } finally { setBusy('') }
  }
  return (
    <Card>
      <div className="flex flex-wrap items-start justify-between gap-2">
        <div>
          <h2 className="text-lg font-bold">📋 Ficha de la empresa</h2>
          <p className="text-sm text-adan-muted">La fuente única de verdad: todas las cuentas del equipo, el Board y La Arena salen de aquí. Si algo está mal, corrígelo.</p>
        </div>
        <div className="flex gap-2">
          <Button size="sm" variant="secondary" onClick={rebuild} loading={busy === 'rebuild'} disabled={Boolean(busy)}
            title="ADÁN relee todas las conversaciones, recupera los acuerdos y quita contradicciones">🧠 Reordenar la memoria</Button>
          {editing
            ? <Button size="sm" onClick={save} loading={busy === 'save'}>Guardar</Button>
            : <Button size="sm" variant="secondary" onClick={() => setEditing(true)}>✏️ Editar</Button>}
        </div>
      </div>
      {rows.length === 0 && !editing && <p className="mt-3 text-sm text-adan-muted">Todavía no hay ficha: toca «Reordenar la memoria» para que ADÁN la arme con lo que han hablado.</p>}
      <div className="mt-3 grid gap-2 sm:grid-cols-2">
        {rows.map(([k, v], i) => editing ? (
          <div key={i} className="flex gap-1">
            <input value={k} onChange={(e) => setRows((r) => r.map((x, j) => (j === i ? [e.target.value, x[1]] : x)))} aria-label="Campo"
              className="w-1/3 rounded-lg border border-adan-border bg-adan-bg px-2 py-1 text-xs font-semibold" />
            <input value={v} onChange={(e) => setRows((r) => r.map((x, j) => (j === i ? [x[0], e.target.value] : x)))} aria-label="Valor"
              className="flex-1 rounded-lg border border-adan-border bg-adan-bg px-2 py-1 text-xs" />
            <button type="button" onClick={() => setRows((r) => r.filter((_, j) => j !== i))} aria-label="Quitar" className="px-1 text-adan-muted">✕</button>
          </div>
        ) : (
          <p key={i} className="rounded-lg border border-adan-border px-3 py-2 text-sm"><b>{k}:</b> {v}</p>
        ))}
      </div>
      {editing && <Button size="sm" variant="ghost" className="mt-2" onClick={() => setRows((r) => [...r, ['', '']])}>+ Agregar campo</Button>}
    </Card>
  )
}

export default function BibliotecaPage() {
  const { companyId = '' } = useParams()
  const [lib, setLib] = useState<Library | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [query, setQuery] = useState('')
  const [section, setSection] = useState<LibraryDoc['seccion'] | 'todo'>('todo')
  const [open, setOpen] = useState<{ id: string; titulo: string; markdown: string } | null>(null)
  const [loadingDoc, setLoadingDoc] = useState('')
  const [writing, setWriting] = useState(0)

  useEffect(() => {
    let cancelled = false
    let timer = 0
    const load = () => api.getLibrary(companyId).then((l) => { if (!cancelled) setLib(l); return l })
    void load().then(async (l) => {
      const pending = (l.faltan ?? []).reduce((n, f) => n + f.entregables.length, 0)
      if (!pending || cancelled) return
      // Niveles cerrados sin sus entregables: ADÁN los redacta y se van mostrando a medida que quedan listos
      const res = await api.prepareDeliverables(companyId)
      if (cancelled || !res.pendientes) return
      setWriting(res.pendientes)
      let rounds = 0
      const poll = async () => {
        rounds += 1
        const fresh = await load().catch(() => null)
        const left = (fresh?.faltan ?? []).reduce((n, f) => n + f.entregables.length, 0)
        if (cancelled) return
        setWriting(left)
        if (left && rounds < 40) timer = window.setTimeout(poll, 8000)
      }
      timer = window.setTimeout(poll, 8000)
    }).catch((e: unknown) => setError(errorMessage(e)))
    return () => { cancelled = true; window.clearTimeout(timer) }
  }, [companyId])

  const docs = useMemo(() => {
    const q = query.trim().toLowerCase()
    return (lib?.documentos ?? []).filter((d) => (section === 'todo' || d.seccion === section)
      && (!q || `${d.titulo} ${d.tipo}`.toLowerCase().includes(q)))
  }, [lib, query, section])

  const read = async (d: LibraryDoc) => {
    if (open?.id === d.id) { setOpen(null); return }
    setLoadingDoc(d.id)
    try { setOpen(await api.getLibraryDoc(companyId, d.id)) } catch (e) { setError(errorMessage(e)) } finally { setLoadingDoc('') }
  }
  const download = (d: LibraryDoc) => {
    if (!d.descarga) return
    const safe = d.titulo.replace(/[^\p{L}\p{N} _-]/gu, '').trim().slice(0, 60) || 'documento'
    void api.downloadFile(d.descarga, `${safe}.${d.ext}`).catch((e: unknown) => setError(errorMessage(e)))
  }

  const crumbs = [{ label: 'Mis Empresas', to: '/dashboard' }, { label: lib?.marca.nombre ?? 'Empresa', to: `/gemelo/${companyId}` }, { label: 'Biblioteca' }]
  if (!lib) return <AppShell crumbs={crumbs}>{error ? <Alert message={error} /> : <LoadingState label="Abriendo la biblioteca…" />}</AppShell>
  const m = lib.marca
  const counts = lib.documentos.reduce<Record<string, number>>((acc, d) => ({ ...acc, [d.seccion]: (acc[d.seccion] ?? 0) + 1 }), {})

  return (
    <AppShell crumbs={crumbs}>
      <main className="h-full overflow-y-auto">
        <div className="max-w-6xl mx-auto p-4 sm:p-6 space-y-6">
          <Alert message={error} onClose={() => setError(null)} />
          <div>
            <h1 className="text-2xl font-bold">📚 Biblioteca de {m.nombre}</h1>
            <p className="text-sm text-adan-muted mt-1">Todo lo que tu empresa va construyendo, Nivel a Nivel: identidad, documentos legales, números, actas y tus archivos.</p>
          </div>

          {/* Identidad viva: se actualiza sola cada vez que eliges algo en Marca */}
          <Card>
            <div className="flex flex-wrap items-start justify-between gap-3">
              <h2 className="text-lg font-bold">🏷️ Identidad de marca</h2>
              <Link to={`/marca/${companyId}`} className="rounded-lg border border-adan-border px-3 py-1.5 text-sm hover:border-adan-accent">Editar en Marca</Link>
            </div>
            <div className="mt-4 grid gap-6 md:grid-cols-[minmax(0,280px)_1fr]">
              <div className="rounded-xl bg-white p-3 grid place-items-center min-h-40">
                {m.logo ? <img src={m.logo} alt={`Logo de ${m.nombre}`} className="max-h-48 max-w-full object-contain" />
                  : <p className="text-sm text-slate-500 text-center">Aún no hay logo.<br /><Link to={`/marca/${companyId}`} className="text-blue-600 underline">Diseñarlo</Link></p>}
              </div>
              <div className="space-y-4 min-w-0">
                <div>
                  <p className="text-2xl font-bold">{m.nombre}</p>
                  <p className="text-adan-muted">{m.slogan || 'Sin slogan todavía'}</p>
                </div>
                <div>
                  <p className="text-xs font-semibold uppercase tracking-widest text-adan-muted">Paleta de colores</p>
                  <div className="mt-2 flex flex-wrap gap-2">
                    {m.paleta.length ? m.paleta.map((p) => <Swatch key={p.nombre} {...p} />) : <p className="text-sm text-adan-muted">Se define al elegir el logo.</p>}
                  </div>
                </div>
                <div className="flex flex-wrap gap-6 text-sm">
                  <p><span className="text-adan-muted">Tipografía:</span> <b>{m.tipografia || '—'}</b></p>
                  <p><span className="text-adan-muted">Concepto del logo:</span> <b>{m.logo_concepto || '—'}</b></p>
                </div>
                <div className="flex flex-wrap gap-2">
                  {m.logo && <a href={m.logo} download={`logo-${m.nombre}.svg`} className="rounded-lg border border-adan-border px-3 py-1.5 text-sm">Descargar logo (SVG)</a>}
                  {m.manual && <Button size="sm" variant="secondary" onClick={() => api.downloadFile(`/empresa/${companyId}/marca/manual.docx`, `manual-de-marca-${m.nombre}.docx`).catch((e: unknown) => setError(errorMessage(e)))}>Manual de marca (Word)</Button>}
                </div>
                {(m.nombres_considerados.length > 0 || m.slogans_considerados.length > 0) && (
                  <details className="text-sm">
                    <summary className="cursor-pointer text-adan-muted">Lo que se consideró</summary>
                    {m.nombres_considerados.length > 0 && <p className="mt-1"><b>Nombres:</b> {m.nombres_considerados.join(' · ')}</p>}
                    {m.slogans_considerados.length > 0 && <p className="mt-1"><b>Slogans:</b> {m.slogans_considerados.join(' · ')}</p>}
                  </details>
                )}
              </div>
            </div>
          </Card>

          <Ficha key={JSON.stringify(lib.ficha ?? {})} companyId={companyId} initial={lib.ficha ?? {}} onError={setError} />

          {lib.memoria && lib.memoria.length > 0 && (
            <Card>
              <h2 className="text-lg font-bold">🧠 Lo que ADÁN recuerda de tu proyecto</h2>
              <p className="text-sm text-adan-muted">Los acuerdos de las conversaciones: todo el equipo los conoce y no los vuelve a preguntar.</p>
              <ul className="mt-3 grid gap-2 sm:grid-cols-2">
                {lib.memoria.slice(0, 40).map((a) => (
                  <li key={`${a.tipo}-${a.texto}`} className="rounded-lg border border-adan-border px-3 py-2 text-sm">
                    <span className={`mr-2 rounded-full px-2 py-0.5 text-[11px] font-semibold ${
                      a.tipo === 'decidido' ? 'bg-adan-success/15 text-adan-success' : a.tipo === 'descartado' ? 'bg-adan-danger/15 text-adan-danger'
                        : a.tipo === 'dato' ? 'bg-sky-500/15 text-sky-500' : 'bg-adan-warning/15 text-adan-warning'}`}>
                      {a.tipo === 'decidido' ? 'Decidido' : a.tipo === 'descartado' ? 'Descartado' : a.tipo === 'dato' ? 'Dato' : 'Pendiente'}
                    </span>
                    {a.texto}{a.nivel ? <span className="text-xs text-adan-muted"> · Nivel {a.nivel}</span> : null}
                  </li>
                ))}
              </ul>
            </Card>
          )}

          <Card>
            <div className="flex flex-col sm:flex-row gap-3 sm:items-center sm:justify-between">
              <h2 className="text-lg font-bold">Documentos ({lib.documentos.length})</h2>
              <input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Buscar…" aria-label="Buscar documentos"
                className="rounded-xl border border-adan-border bg-adan-bg px-3 py-2 text-sm sm:w-64" />
            </div>
            <div className="mt-3 flex flex-wrap gap-1.5" role="tablist" aria-label="Secciones">
              <Button size="sm" variant={section === 'todo' ? 'primary' : 'secondary'} onClick={() => setSection('todo')}>Todo</Button>
              {(Object.keys(lib.secciones) as LibraryDoc['seccion'][]).map((s) => (
                <Button key={s} size="sm" variant={section === s ? 'primary' : 'secondary'} onClick={() => setSection(s)}>
                  {ICON[s]} {lib.secciones[s]} {counts[s] ? `(${counts[s]})` : ''}
                </Button>
              ))}
            </div>
            {writing > 0 && (
              <p className="mt-4 rounded-xl border border-adan-accent/40 bg-adan-accent/5 p-3 text-sm animate-pulse" data-testid="redactando">
                ✍️ ADÁN está redactando {writing} entregable{writing === 1 ? '' : 's'} de los Niveles que ya cerraste. Van apareciendo aquí solos.
              </p>
            )}
            {docs.length === 0 ? (
              <div className="mt-6 text-sm text-adan-muted">
                {query ? 'Nada coincide con la búsqueda.' : section !== 'todo' ? (
                  <p>{EMPTY[section]} {LINKS[section] && <Link to={LINKS[section]!(companyId)} className="text-adan-accent underline">{LINK_LABEL[section]}</Link>}</p>
                ) : 'Todavía no hay documentos: se irán guardando aquí a medida que avances en los Niveles.'}
              </div>
            ) : (
              <ul className="mt-4 divide-y divide-adan-border">
                {docs.map((d) => (
                  <li key={d.id} className="py-3">
                    <div className="flex flex-wrap items-center gap-3">
                      <span className="text-xl" aria-hidden="true">{ICON[d.seccion]}</span>
                      <div className="min-w-0 flex-1">
                        <p className="font-medium truncate">{d.titulo}</p>
                        <p className="text-xs text-adan-muted">
                          {d.tipo}{d.nivel ? ` · Nivel ${d.nivel}` : ''} · {d.origen === 'tuyo' ? 'lo subiste tú' : 'hecho con ADÁN'}
                          {d.actualizado ? ` · ${date(d.actualizado)}` : ''}{d.palabras ? ` · ${d.palabras.toLocaleString('es-CO')} palabras` : ''}
                        </p>
                      </div>
                      <div className="flex flex-wrap gap-1.5">
                        {d.legible && <Button size="sm" variant="secondary" onClick={() => read(d)} loading={loadingDoc === d.id}>{open?.id === d.id ? 'Cerrar' : 'Leer'}</Button>}
                        {d.descarga && <Button size="sm" variant="secondary" onClick={() => download(d)}>Descargar</Button>}
                        {d.herramienta && <Link to={d.herramienta} className="rounded-lg px-3 py-1.5 text-sm text-adan-muted hover:text-adan-text">Abrir ↗</Link>}
                      </div>
                    </div>
                    {open?.id === d.id && (
                      <div className="markdown mt-3 max-h-[60vh] overflow-y-auto rounded-xl border border-adan-border bg-adan-bg p-4 text-sm">
                        <ReactMarkdown>{open.markdown}</ReactMarkdown>
                      </div>
                    )}
                  </li>
                ))}
              </ul>
            )}
          </Card>
        </div>
      </main>
    </AppShell>
  )
}
