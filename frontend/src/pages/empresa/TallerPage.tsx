import { useCallback, useEffect, useState } from 'react'
import ReactMarkdown from 'react-markdown'
import { useParams } from 'react-router'
import AppShell from '../../components/AppShell'
import Alert from '../../components/ui/Alert'
import Button from '../../components/ui/Button'
import Card from '../../components/ui/Card'
import { LoadingState } from '../../components/ui/States'
import { api, errorMessage } from '../../lib/api'
import type { Lead, Workshop, WorkshopSite } from '../../types'

// El Taller de Genexis (Nivel 4): Genexis construye de verdad el MVP. Especificación del producto, landing de
// validación (incluida en el Nivel 4, capta interesados reales con su autorización), prototipo navegable (se cotiza
// en @pples y se aprueba antes) y el código para seguir desarrollando. Si la empresa ya tiene producto, lo recorre
// y deja un plan de mejoras.

type Tipo = 'landing' | 'prototipo'

function SiteCard({ companyId, tipo, site, ws, onChange, onError }: {
  companyId: string; tipo: Tipo; site: WorkshopSite | null; ws: Workshop; onChange: (w: Workshop) => void; onError: (m: string) => void
}) {
  const [instruction, setInstruction] = useState('')
  const [busy, setBusy] = useState(false)
  const isLanding = tipo === 'landing'
  const building = site?.estado === 'construyendo'
  const extraTweak = (site?.ajustes ?? 0) >= ws.ajustes_gratis
  const build = async () => {
    if (!isLanding && !window.confirm(`El prototipo cuesta ${ws.precio_prototipo} @pples. ¿Lo construimos?`)) return
    setBusy(true)
    try { onChange(await api.buildSite(companyId, tipo, !isLanding)) } catch (e) { onError(errorMessage(e)) } finally { setBusy(false) }
  }
  const tweak = async () => {
    if (extraTweak && !window.confirm(`Este ajuste cuesta ${ws.precio_ajuste} @pples (los primeros ${ws.ajustes_gratis} van incluidos). ¿Seguimos?`)) return
    setBusy(true)
    try {
      onChange(await api.tweakSite(companyId, tipo, instruction.trim(), extraTweak))
      setInstruction('')
    } catch (e) { onError(errorMessage(e)) } finally { setBusy(false) }
  }
  const full = site?.url ? `${window.location.origin}${site.url}` : ''
  return (
    <Card>
      <div className="flex flex-wrap items-start justify-between gap-2">
        <div>
          <h2 className="text-lg font-bold">{isLanding ? '🌐 Landing de validación' : '📱 Prototipo navegable'}</h2>
          <p className="text-sm text-adan-muted">
            {isLanding
              ? 'Una página con tu marca que explica la promesa y capta interesados reales (con su autorización de datos). Incluida en el Nivel 4.'
              : `Las pantallas principales de tu producto, navegables, para mostrar y probar con clientes. Cuesta ${ws.precio_prototipo} @pples; se aprueba antes de construir.`}
          </p>
        </div>
        {site?.version ? <span className="rounded-full bg-adan-surface-2 px-2 py-0.5 text-xs">Versión {site.version}</span> : null}
      </div>
      {building && <p className="mt-3 animate-pulse text-sm">🛠️ Genexis está construyendo… (uno a tres minutos). Te aviso también en la Sala.</p>}
      {site?.estado === 'error' && <p className="mt-3 text-sm text-adan-danger">No se pudo terminar: {site.error}. Inténtalo de nuevo.</p>}
      {site?.url && !building && (
        <>
          <div className="mt-3 flex flex-wrap items-center gap-2 text-sm">
            <a href={site.url} target="_blank" rel="noreferrer" className="rounded-lg bg-adan-accent px-3 py-1.5 font-semibold text-white">Abrir ↗</a>
            <button type="button" onClick={() => void navigator.clipboard?.writeText(full)} className="rounded-lg border border-adan-border px-3 py-1.5">Copiar enlace</button>
            <span className="truncate text-xs text-adan-muted">{full}</span>
          </div>
          <div className="mt-3 overflow-hidden rounded-xl border border-adan-border bg-white">
            <iframe title={`Vista de la ${tipo}`} src={site.url} sandbox="allow-scripts allow-forms" className="h-[420px] w-full" />
          </div>
          <div className="mt-3 flex flex-col gap-2 sm:flex-row">
            <input value={instruction} onChange={(e) => setInstruction(e.target.value)} maxLength={1000} aria-label="Cambio que quieres"
              placeholder="Pídele un cambio a Genexis: «el botón más grande», «agrega precios», «más fotos de playa»…"
              className="flex-1 rounded-xl border border-adan-border bg-adan-bg px-3 py-2 text-sm" />
            <Button onClick={tweak} disabled={instruction.trim().length < 3 || busy} loading={busy}>
              Ajustar{extraTweak ? ` · ${ws.precio_ajuste} @pples` : ''}
            </Button>
          </div>
          {site.ultimo_ajuste && <p className="mt-1 text-xs text-adan-muted">Último ajuste: {site.ultimo_ajuste}</p>}
        </>
      )}
      {!building && (
        <Button className="mt-3" variant={site?.url ? 'secondary' : 'primary'} onClick={build} loading={busy}
          disabled={!ws.especificacion && !isLanding}>
          {site?.url ? 'Construir de nuevo' : isLanding ? 'Construir la landing' : `Construir el prototipo · ${ws.precio_prototipo} @pples`}
        </Button>
      )}
      {!isLanding && !ws.especificacion && <p className="mt-1 text-xs text-adan-muted">Primero escribe la especificación del producto.</p>}
    </Card>
  )
}

export default function TallerPage() {
  const { companyId = '' } = useParams()
  const [ws, setWs] = useState<Workshop | null>(null)
  const [leads, setLeads] = useState<Lead[] | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState('')
  const [url, setUrl] = useState('')

  const load = useCallback(() => api.getWorkshop(companyId).then(setWs).catch((e: unknown) => setError(errorMessage(e))), [companyId])
  useEffect(() => { void load() }, [load])
  // Mientras Genexis construye, la página se actualiza sola
  const building = ws && (ws.sitios.landing?.estado === 'construyendo' || ws.sitios.prototipo?.estado === 'construyendo')
  useEffect(() => {
    if (!building) return
    const id = window.setInterval(() => { void load() }, 8000)
    return () => window.clearInterval(id)
  }, [building, load])

  const spec = async () => {
    setBusy('spec')
    try { setWs(await api.writeSpec(companyId)) } catch (e) { setError(errorMessage(e)) } finally { setBusy('') }
  }
  const evaluate = async () => {
    setBusy('eval')
    try {
      await api.evaluateProduct(companyId, url.trim())
      setError(null)
      window.alert('Genexis está recorriendo tu producto (unos minutos). El plan de mejoras llega a la Sala del Nivel 4 y aquí.')
    } catch (e) { setError(errorMessage(e)) } finally { setBusy('') }
  }

  if (!ws) return <AppShell crumbs={[{ label: 'Taller Genexis' }]}>{error ? <Alert message={error} /> : <LoadingState label="Abriendo el taller…" />}</AppShell>
  return (
    <AppShell crumbs={[{ label: 'Mis Empresas', to: '/dashboard' }, { label: 'Nivel 4', to: `/nivel/4/${companyId}` }, { label: 'Taller Genexis' }]}>
      <main className="h-full overflow-y-auto">
        <div className="mx-auto max-w-5xl space-y-5 p-4 sm:p-6">
          <Alert message={error} onClose={() => setError(null)} />
          <div>
            <h1 className="text-2xl font-bold">🛠️ Taller de Genexis</h1>
            <p className="mt-1 text-sm text-adan-muted">Aquí el MVP se construye de verdad: especificación, landing, prototipo y código. Después, el software de producción lo cotiza Paradixe con esta especificación.</p>
          </div>

          {ws.empresa_existente && (
            <Card>
              <h2 className="text-lg font-bold">🔎 Tu empresa ya tiene producto</h2>
              <p className="text-sm text-adan-muted">Genexis lo recorre como un cliente nuevo (y usa la revisión de código si la pediste en la Sala) y te deja un plan de mejoras priorizado con cotización.</p>
              <div className="mt-3 flex flex-col gap-2 sm:flex-row">
                <input value={url} onChange={(e) => setUrl(e.target.value)} placeholder="https://tuproducto.com" aria-label="Dirección del producto"
                  className="flex-1 rounded-xl border border-adan-border bg-adan-bg px-3 py-2 text-sm" />
                <Button onClick={evaluate} loading={busy === 'eval'} disabled={url.trim().length < 4}>Evaluar mi producto</Button>
              </div>
              {ws.plan_mejoras && (
                <details className="mt-3" open>
                  <summary className="cursor-pointer text-sm font-semibold">Plan de mejoras</summary>
                  <div className="markdown mt-2 text-sm"><ReactMarkdown>{ws.plan_mejoras.markdown}</ReactMarkdown></div>
                </details>
              )}
            </Card>
          )}

          <Card>
            <div className="flex flex-wrap items-start justify-between gap-2">
              <div>
                <h2 className="text-lg font-bold">📐 Especificación del producto</h2>
                <p className="text-sm text-adan-muted">Historias de usuario, pantallas, datos, integraciones y métricas: la base de todo lo que se construye.</p>
              </div>
              <Button onClick={spec} loading={busy === 'spec'} variant={ws.especificacion ? 'secondary' : 'primary'}>
                {ws.especificacion ? 'Reescribirla' : 'Escribir la especificación'}
              </Button>
            </div>
            {ws.especificacion && (
              <details className="mt-3">
                <summary className="cursor-pointer text-sm font-semibold">Ver la especificación</summary>
                <div className="markdown mt-2 max-h-[60vh] overflow-y-auto text-sm"><ReactMarkdown>{ws.especificacion.markdown}</ReactMarkdown></div>
              </details>
            )}
          </Card>

          <SiteCard companyId={companyId} tipo="landing" site={ws.sitios.landing} ws={ws} onChange={setWs} onError={setError} />
          <SiteCard companyId={companyId} tipo="prototipo" site={ws.sitios.prototipo} ws={ws} onChange={setWs} onError={setError} />

          <Card>
            <div className="flex flex-wrap items-start justify-between gap-2">
              <div>
                <h2 className="text-lg font-bold">🙋 Interesados ({ws.interesados})</h2>
                <p className="text-sm text-adan-muted">Personas reales que dejaron sus datos en tu landing, con autorización (Ley 1581). Solo tú los ves.</p>
              </div>
              <div className="flex gap-2">
                <Button size="sm" variant="secondary" onClick={() => api.getLeads(companyId).then(setLeads).catch((e: unknown) => setError(errorMessage(e)))}>Ver</Button>
                <Button size="sm" variant="secondary" onClick={() => api.downloadFile(`/genexis/${companyId}/interesados.csv`, 'interesados.csv').catch((e: unknown) => setError(errorMessage(e)))}>Descargar CSV</Button>
              </div>
            </div>
            {leads && (leads.length === 0 ? <p className="mt-3 text-sm text-adan-muted">Todavía no llega nadie: comparte el enlace de tu landing.</p> : (
              <div className="mt-3 overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="text-left text-xs text-adan-muted"><tr><th className="py-1">Fecha</th><th>Nombre</th><th>Correo</th><th>Celular</th><th>Mensaje</th></tr></thead>
                  <tbody>{leads.map((l) => (
                    <tr key={l.id} className="border-t border-adan-border"><td className="py-1">{new Date(l.fecha).toLocaleDateString('es-CO')}</td>
                      <td>{l.nombre}</td><td>{l.correo}</td><td>{l.celular}</td><td className="max-w-xs truncate">{l.mensaje}</td></tr>
                  ))}</tbody>
                </table>
              </div>
            ))}
          </Card>

          <Card>
            <h2 className="text-lg font-bold">💾 Código</h2>
            <p className="text-sm text-adan-muted">Las páginas, la especificación y cómo publicarlas, en un .zip para seguir desarrollando o subir a tu hosting.</p>
            <Button className="mt-3" variant="secondary" disabled={!ws.sitios.landing?.url && !ws.sitios.prototipo?.url}
              onClick={() => api.downloadFile(`/genexis/${companyId}/codigo.zip`, 'mvp.zip').catch((e: unknown) => setError(errorMessage(e)))}>
              Descargar el código
            </Button>
          </Card>
        </div>
      </main>
    </AppShell>
  )
}
