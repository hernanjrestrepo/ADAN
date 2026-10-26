import { useEffect, useState } from 'react'
import ReactMarkdown from 'react-markdown'
import { useParams } from 'react-router'
import AppShell from '../../components/AppShell'
import Alert from '../../components/ui/Alert'
import Button from '../../components/ui/Button'
import Card from '../../components/ui/Card'
import { LoadingState } from '../../components/ui/States'
import { api, errorMessage } from '../../lib/api'
import { logoSvg, svgDataUrl, type LogoConcept } from '../../lib/logo'
import type { BrandData } from '../../types'

// La marca de la empresa, construida con el equipo: nombres pegajosos (ciencia del naming), logos en vector para
// escoger, slogan y manual de marca. Lo elegido se vuelve la identidad en todo ADÁN y en las oficinas.

const STYLE_LABEL: Record<string, string> = { icono_texto: 'Ícono + nombre', monograma: 'Monograma', emblema: 'Emblema', solo_texto: 'Solo texto' }

function Score({ label, value }: { label: string; value: number }) {
  return (
    <span className="text-[11px] text-adan-muted" title={label}>
      {label} {'●'.repeat(Math.max(0, Math.min(5, value)))}{'○'.repeat(5 - Math.max(0, Math.min(5, value)))}
    </span>
  )
}

function LogoPreview({ concept, name, slogan, selected, onPick, busy }: {
  concept: LogoConcept; name: string; slogan: string; selected: boolean; onPick: (img: string) => void; busy: boolean
}) {
  const [src, setSrc] = useState<string | null>(null)
  useEffect(() => {
    let cancelled = false
    void logoSvg(concept, name, slogan).then((svg) => { if (!cancelled) setSrc(svgDataUrl(svg)) })
    return () => { cancelled = true }
  }, [concept, name, slogan])
  return (
    <Card className={`p-3! ${selected ? 'ring-2 ring-adan-accent' : ''}`}>
      <div className="aspect-[4/3] rounded-xl bg-white grid place-items-center overflow-hidden">
        {src ? <img src={src} alt={`Logo ${concept.nombre_concepto}`} className="max-h-full max-w-full object-contain" /> : <span className="text-xs text-slate-400">Dibujando…</span>}
      </div>
      <p className="mt-2 text-sm font-semibold">{concept.nombre_concepto} <span className="text-xs font-normal text-adan-muted">· {STYLE_LABEL[concept.estilo]}</span></p>
      <p className="text-xs text-adan-muted">{concept.por_que}</p>
      <div className="mt-2 flex items-center gap-1">
        {[concept.primario, concept.acento, concept.fondo].map((c) => <span key={c} className="h-4 w-4 rounded-full border border-adan-border" style={{ background: c }} title={c} />)}
        <span className="ml-1 text-[11px] text-adan-muted">{concept.tipografia}</span>
      </div>
      <div className="mt-2 flex gap-2">
        <Button size="sm" onClick={() => src && onPick(src)} disabled={!src || busy}>{selected ? '✓ Elegido' : 'Elegir este'}</Button>
        {src && <a href={src} download={`logo-${concept.id}.svg`} className="rounded-lg border border-adan-border px-2 py-1 text-xs">Descargar SVG</a>}
      </div>
    </Card>
  )
}

export default function MarcaPage() {
  const { companyId = '' } = useParams()
  const [brand, setBrand] = useState<BrandData | null>(null)
  const [ideas, setIdeas] = useState('')
  const [busy, setBusy] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [company, setCompany] = useState('Empresa')
  const [logoUrl, setLogoUrl] = useState('')

  // La empresa ya tiene logo: se adopta subiéndolo o desde la dirección de la imagen en su web
  const adoptOwn = (logo: { url?: string; imagen?: string }) => run('own', async () => {
    const data = await api.adoptExistingLogo(companyId, logo)
    window.dispatchEvent(new Event('adan-identidad'))
    return data
  })
  const uploadOwn = (file: File | undefined) => {
    if (!file) return
    if (file.size > 600_000) { setError('La imagen del logo es muy pesada (máximo 600 KB).'); return }
    const reader = new FileReader()
    reader.onload = () => adoptOwn({ imagen: String(reader.result) })
    reader.readAsDataURL(file)
  }

  useEffect(() => {
    let cancelled = false
    api.getBrand(companyId).then((b) => { if (!cancelled) { setBrand(b); setCompany(b.identidad?.nombre ?? 'Empresa') } }).catch((e: unknown) => setError(errorMessage(e)))
    return () => { cancelled = true }
  }, [companyId])

  const run = async (key: string, fn: () => Promise<BrandData>) => {
    setBusy(key)
    setError(null)
    try {
      const b = await fn()
      setBrand((prev) => ({ ...prev, ...b }))
    } catch (e) {
      setError(errorMessage(e))
    } finally {
      setBusy('')
    }
  }

  if (!brand) return <AppShell crumbs={[{ label: 'Marca' }]}>{error ? <Alert message={error} /> : <LoadingState label="Abriendo la marca…" />}</AppShell>
  const name = brand.nombre_elegido || company
  const slogan = brand.slogan ?? ''

  return (
    <AppShell crumbs={[{ label: 'Mis Empresas', to: '/dashboard' }, { label: company, to: `/gemelo/${companyId}` }, { label: 'Marca' }]}>
      <main className="h-full overflow-y-auto">
        <div className="max-w-6xl mx-auto p-4 sm:p-6 space-y-6">
          <Alert message={error} onClose={() => setError(null)} />

          <Card>
            <h2 className="text-xl font-bold">1. Nombre</h2>
            <p className="text-sm text-adan-muted mt-1">
              Nombres pegajosos y fáciles de mercadear, con ciencia: fluidez (fáciles de decir y recordar), simbolismo fonético
              (el sonido transmite rapidez, solidez o calidez), distintividad y las pruebas SMILE y SCRATCH. Primero salen los que
              tienen dominio libre.
            </p>
            <div className="mt-3 flex flex-col sm:flex-row gap-2">
              <input value={ideas} onChange={(e) => setIdeas(e.target.value)} maxLength={1000} aria-label="Qué quieres transmitir"
                placeholder="Opcional: qué quieres transmitir (confianza, rapidez, aventura…)" className="flex-1 rounded-xl border border-adan-border bg-adan-bg px-3 py-2 text-sm" />
              <Button onClick={() => run('names', () => api.brandNames(companyId, ideas))} loading={busy === 'names'}>
                {brand.nombres?.length ? 'Proponer otros' : 'Proponer nombres'}
              </Button>
            </div>
            {brand.nombres && brand.nombres.length > 0 && (
              <div className="mt-4 grid gap-3 sm:grid-cols-2">
                {brand.nombres.map((n) => (
                  <div key={n.nombre} className={`rounded-xl border p-3 ${brand.nombre_elegido === n.nombre ? 'border-adan-accent bg-adan-accent/5' : 'border-adan-border'}`}>
                    <div className="flex items-center justify-between gap-2">
                      <p className="text-lg font-bold">{n.nombre} <span className="text-xs font-normal text-adan-muted">{n.tipo}</span></p>
                      <Button size="sm" variant={brand.nombre_elegido === n.nombre ? 'primary' : 'secondary'} disabled={Boolean(busy)}
                        onClick={() => run('pick', () => api.chooseBrandName(companyId, n.nombre, true))}>
                        {brand.nombre_elegido === n.nombre ? '✓ Elegido' : 'Elegir'}
                      </Button>
                    </div>
                    <p className="text-sm">{n.por_que}</p>
                    <p className="text-xs text-adan-muted">Sonido: {n.sonido}</p>
                    <div className="mt-1 flex flex-wrap gap-3"><Score label="Fluidez" value={n.fluidez} /><Score label="Memorable" value={n.memorabilidad} /><Score label="Distinto" value={n.distintividad} /></div>
                    <p className={`mt-1 text-xs ${n.dominios_libres.length ? 'text-adan-success' : 'text-adan-warning'}`}>
                      {n.dominios_libres.length ? `Dominio libre: ${n.dominios_libres.join(', ')}` : 'Sin dominio libre en las extensiones revisadas'}
                    </p>
                  </div>
                ))}
              </div>
            )}
            <details className="mt-4 text-sm">
              <summary className="cursor-pointer font-semibold">¿Cómo compro el dominio?</summary>
              <ol className="mt-2 list-decimal pl-5 space-y-1 text-adan-muted">
                <li>Entra a un registrador (Namecheap, Cloudflare, GoDaddy o, para .co, uno acreditado en Colombia).</li>
                <li>Busca el dominio exacto que salió libre (por ejemplo <b>{(name || 'tumarca').toLowerCase().replace(/[^a-z0-9]/g, '')}.com</b>).</li>
                <li>Cómpralo a tu nombre o al de la empresa, por 1 a 2 años; activa la protección de privacidad (WHOIS) y la renovación automática.</li>
                <li>Si puedes, compra también la versión del país (.co) para que nadie la tome.</li>
                <li>Guarda la factura y súbela en el Expediente, ítem «Dominio web».</li>
              </ol>
            </details>
          </Card>

          <Card>
            <h2 className="text-xl font-bold">2. Logo</h2>
            <p className="text-sm text-adan-muted mt-1">El director de arte propone 4 conceptos distintos (ícono, monograma, emblema y solo texto) con psicología del color y contraste para leer. Elige uno: queda como identidad de tu empresa en ADÁN y en las oficinas.</p>
            <div className="mt-3 rounded-xl border border-adan-border bg-adan-bg p-3" data-testid="logo-propio">
              <p className="text-sm font-semibold">¿Tu empresa ya tiene logo?</p>
              <p className="text-xs text-adan-muted">Súbelo o pega la dirección de la imagen en tu web: lo adopto tal cual y saco tu paleta de colores.</p>
              {brand.logo_elegido?.id === 'actual' && <p className="mt-1 text-xs text-adan-success">✓ Estás usando el logo actual de tu empresa.</p>}
              <div className="mt-2 flex flex-col gap-2 sm:flex-row">
                <label className="inline-flex cursor-pointer items-center justify-center rounded-lg border border-adan-border px-3 py-1.5 text-sm hover:border-adan-accent">
                  📤 Ya tengo logo: subirlo
                  <input type="file" accept="image/png,image/jpeg,image/webp,image/svg+xml" className="hidden"
                    onChange={(e) => { uploadOwn(e.target.files?.[0]); e.target.value = '' }} />
                </label>
                <input value={logoUrl} onChange={(e) => setLogoUrl(e.target.value)} placeholder="https://tuweb.com/logo.png" aria-label="Dirección del logo"
                  className="flex-1 rounded-lg border border-adan-border bg-adan-surface px-3 py-1.5 text-sm" />
                <Button size="sm" variant="secondary" disabled={!/^https?:\/\//.test(logoUrl) || Boolean(busy)} loading={busy === 'own'}
                  onClick={() => adoptOwn({ url: logoUrl.trim() })}>Usar este</Button>
              </div>
            </div>
            <Button className="mt-3" onClick={() => run('logos', () => api.brandLogos(companyId))} loading={busy === 'logos'}>
              {brand.logos?.length ? 'Proponer otros logos' : `Diseñar logos para «${name}»`}
            </Button>
            {brand.logos && brand.logos.length > 0 && (
              <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                {brand.logos.map((c) => (
                  <LogoPreview key={c.id} concept={c} name={name} slogan={slogan} selected={brand.logo_elegido?.id === c.id} busy={Boolean(busy)}
                    onPick={(img) => run('logo', () => api.chooseBrandLogo(companyId, c.id, img))} />
                ))}
              </div>
            )}
          </Card>

          <Card>
            <h2 className="text-xl font-bold">3. Slogan</h2>
            <Button className="mt-3" onClick={() => run('slogans', () => api.brandSlogans(companyId))} loading={busy === 'slogans'}>
              {brand.slogans?.length ? 'Proponer otros' : 'Proponer slogans'}
            </Button>
            {brand.slogans && (
              <ul className="mt-3 space-y-2">
                {brand.slogans.map((s) => (
                  <li key={s.texto} className="flex items-center justify-between gap-3 rounded-xl border border-adan-border p-3">
                    <span><b>{s.texto}</b><span className="block text-xs text-adan-muted">{s.por_que}</span></span>
                    <Button size="sm" variant={slogan === s.texto ? 'primary' : 'secondary'} disabled={Boolean(busy)} onClick={() => run('slogan', () => api.chooseBrandSlogan(companyId, s.texto))}>
                      {slogan === s.texto ? '✓ Elegido' : 'Elegir'}
                    </Button>
                  </li>
                ))}
              </ul>
            )}
          </Card>

          <Card>
            <h2 className="text-xl font-bold">4. Manual de marca</h2>
            <p className="text-sm text-adan-muted mt-1">Esencia, tono de voz, colores, tipografías y uso del logo, listo para tu equipo y proveedores.</p>
            <div className="mt-3 flex gap-2">
              <Button onClick={() => run('manual', () => api.brandManual(companyId))} loading={busy === 'manual'} disabled={!brand.logo_elegido}>
                {brand.manual ? 'Rehacer el manual' : 'Generar el manual'}
              </Button>
              {brand.manual && (
                <Button variant="secondary" onClick={() => api.downloadFile(`/empresa/${companyId}/marca/manual.docx`, `manual-de-marca-${name}.docx`).catch((e: unknown) => setError(errorMessage(e)))}>
                  Descargar Word
                </Button>
              )}
            </div>
            {!brand.logo_elegido && <p className="mt-2 text-xs text-adan-muted">Primero elige un logo.</p>}
            {brand.manual && <div className="mt-4 markdown text-sm"><ReactMarkdown>{brand.manual}</ReactMarkdown></div>}
          </Card>
        </div>
      </main>
    </AppShell>
  )
}
