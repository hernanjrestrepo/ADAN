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

export default function BibliotecaPage() {
  const { companyId = '' } = useParams()
  const [lib, setLib] = useState<Library | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [query, setQuery] = useState('')
  const [section, setSection] = useState<LibraryDoc['seccion'] | 'todo'>('todo')
  const [open, setOpen] = useState<{ id: string; titulo: string; markdown: string } | null>(null)
  const [loadingDoc, setLoadingDoc] = useState('')

  useEffect(() => {
    let cancelled = false
    api.getLibrary(companyId).then((l) => { if (!cancelled) setLib(l) }).catch((e: unknown) => setError(errorMessage(e)))
    return () => { cancelled = true }
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
            {docs.length === 0 ? (
              <p className="mt-6 text-sm text-adan-muted">
                {lib.documentos.length ? 'Nada coincide con la búsqueda.' : 'Todavía no hay documentos: se irán guardando aquí a medida que avances en los Niveles.'}
              </p>
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
