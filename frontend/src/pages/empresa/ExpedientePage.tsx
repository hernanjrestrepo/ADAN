import { useEffect, useRef, useState } from 'react'
import ReactMarkdown from 'react-markdown'
import { Link, useParams } from 'react-router'
import AppShell from '../../components/AppShell'
import Alert from '../../components/ui/Alert'
import Button from '../../components/ui/Button'
import Card from '../../components/ui/Card'
import { LoadingState } from '../../components/ui/States'
import { api, errorMessage } from '../../lib/api'
import type { Dossier, DossierItem } from '../../types'

// El Expediente de creación: todo lo que necesita la empresa para existir según su país. ADÁN prepara cada trámite
// (formularios, borradores, lista de requisitos y costos oficiales con su fuente), el fundador lo radica y sube el
// soporte, y ADÁN lo lee y valida. En Colombia la Cámara de Comercio es presencial; en Estados Unidos todo es en línea.

const GROUPS: { id: DossierItem['grupo']; label: string; icon: string }[] = [
  { id: 'identidad', label: 'Identidad', icon: '🏷️' },
  { id: 'numeros', label: 'Números', icon: '🧮' },
  { id: 'legal', label: 'Legal y registro', icon: '⚖️' },
  { id: 'operacion', label: 'Operación', icon: '⚙️' },
]

const STATE: Record<DossierItem['estado'], { label: string; className: string }> = {
  pendiente: { label: 'Pendiente', className: 'bg-adan-surface-2 text-adan-muted' },
  en_curso: { label: 'En curso', className: 'bg-sky-500/15 text-sky-500' },
  preparado: { label: 'Preparado', className: 'bg-violet-500/15 text-violet-500' },
  validado: { label: '✓ Validado', className: 'bg-adan-success/15 text-adan-success' },
  observado: { label: 'Con observaciones', className: 'bg-adan-warning/15 text-adan-warning' },
  no_aplica: { label: 'No aplica', className: 'bg-adan-surface-2 text-adan-muted line-through' },
}

const MODE: Record<DossierItem['modo'], string> = {
  adan: 'Lo hace ADÁN contigo',
  cliente_presencial: 'ADÁN lo deja listo · tú lo radicas en persona',
  cliente_en_linea: 'ADÁN lo deja listo · tú lo envías en línea y pagas la tarifa oficial',
}

const COUNTRIES = [
  { id: 'CO', label: '🇨🇴 Colombia' },
  { id: 'US', label: '🇺🇸 Estados Unidos' },
  { id: 'OTRO', label: '🌎 Otro país' },
]

// La herramienta de ADÁN que produce el ítem (por ejemplo /marca), abierta para esta empresa
const toolLink = (tool: string, companyId: string): string | null => (tool ? `${tool}/${companyId}` : null)

function ItemCard({ item, companyId, onChange, onError }: {
  item: DossierItem; companyId: string; onChange: (d: Dossier) => void; onError: (m: string) => void
}) {
  const [open, setOpen] = useState(false)
  const [pack, setPack] = useState<{ id: string; title: string; markdown: string } | null>(null)
  const [busy, setBusy] = useState('')
  const file = useRef<HTMLInputElement>(null)
  const st = STATE[item.estado]
  const link = toolLink(item.herramienta, companyId)

  const prepare = async () => {
    setBusy('prep')
    try {
      setPack(await api.prepareDossierItem(companyId, item.id))
      setOpen(true)
      onChange(await api.getDossier(companyId))
    } catch (e) { onError(errorMessage(e)) } finally { setBusy('') }
  }
  const showPack = async () => {
    if (!item.preparado_doc) return
    if (pack) { setOpen(!open); return }
    try { setPack(await api.getDossierPack(companyId, item.preparado_doc)); setOpen(true) } catch (e) { onError(errorMessage(e)) }
  }
  const upload = async (f: File) => {
    setBusy('up')
    try { onChange((await api.uploadDossierDoc(companyId, item.id, f)).expediente) } catch (e) { onError(errorMessage(e)) } finally {
      setBusy('')
      if (file.current) file.current.value = ''
    }
  }
  const mark = async (estado: string) => {
    setBusy(estado)
    try { onChange(await api.setDossierStatus(companyId, item.id, estado)) } catch (e) { onError(errorMessage(e)) } finally { setBusy('') }
  }

  return (
    <div className="rounded-xl border border-adan-border bg-adan-surface p-4" data-testid={`item-${item.id}`}>
      <div className="flex flex-wrap items-start justify-between gap-2">
        <div className="min-w-0">
          <p className="font-semibold">{item.titulo}</p>
          <p className="text-xs text-adan-muted">{MODE[item.modo]}</p>
        </div>
        <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${st.className}`}>{st.label}</span>
      </div>
      <p className="mt-2 text-sm">{item.que_es}</p>
      {item.documento && <p className="mt-1 text-xs text-adan-muted">Soporte que valida: <b>{item.documento}</b></p>}
      {item.validacion && (
        <div className={`mt-2 rounded-lg p-2 text-xs ${item.validacion.valido ? 'bg-adan-success/10' : 'bg-adan-warning/10'}`}>
          <p><b>{item.validacion.valido ? 'Documento validado' : 'Revisa el documento'}</b> · {item.validacion.tipo_detectado}
            {item.validacion.numero_identificacion && <> · N.º {item.validacion.numero_identificacion}</>}
            {item.validacion.fecha && <> · {item.validacion.fecha}</>}</p>
          {item.validacion.observaciones.length > 0 && <ul className="mt-1 list-disc pl-4">{item.validacion.observaciones.map((o) => <li key={o}>{o}</li>)}</ul>}
        </div>
      )}
      <div className="mt-3 flex flex-wrap gap-2">
        {link && <Link to={link} className="rounded-lg border border-adan-border px-3 py-1.5 text-sm hover:border-adan-accent">Abrir herramienta</Link>}
        {(item.modo !== 'adan' || !link) && (
          <Button size="sm" onClick={prepare} loading={busy === 'prep'} disabled={Boolean(busy) && busy !== 'prep'}>
            {item.preparado_doc ? 'Preparar de nuevo' : 'Preparar con ADÁN'}
          </Button>
        )}
        {item.preparado_doc && <Button size="sm" variant="secondary" onClick={showPack}>{open ? 'Ocultar paquete' : 'Ver paquete'}</Button>}
        {item.documento && (
          <>
            <input ref={file} type="file" className="hidden" accept=".pdf,.png,.jpg,.jpeg,.webp,.docx,.txt"
              onChange={(e) => { const f = e.target.files?.[0]; if (f) void upload(f) }} aria-label={`Subir ${item.documento}`} />
            <Button size="sm" variant="secondary" onClick={() => file.current?.click()} loading={busy === 'up'} disabled={Boolean(busy) && busy !== 'up'}>
              📎 Subir soporte
            </Button>
          </>
        )}
        {item.estado !== 'validado' && item.estado !== 'no_aplica' && (
          <>
            <Button size="sm" variant="ghost" onClick={() => mark('validado')} disabled={Boolean(busy)}>Ya lo tengo</Button>
            <Button size="sm" variant="ghost" onClick={() => mark('no_aplica')} disabled={Boolean(busy)}>No aplica</Button>
          </>
        )}
        {(item.estado === 'no_aplica' || item.estado === 'validado') && !item.validacion && (
          <Button size="sm" variant="ghost" onClick={() => mark('pendiente')} disabled={Boolean(busy)}>Reabrir</Button>
        )}
      </div>
      {open && pack && (
        <div className="mt-3 rounded-xl border border-adan-border bg-adan-bg p-3">
          <div className="flex items-center justify-between gap-2">
            <p className="text-sm font-semibold">{pack.title}</p>
            <Button size="sm" variant="secondary" onClick={() => api.downloadFile(`/empresa/${companyId}/expediente/paquete/${pack.id}.docx`, `${item.id}.docx`).catch((e: unknown) => onError(errorMessage(e)))}>
              Descargar Word
            </Button>
          </div>
          <div className="markdown mt-2 text-sm"><ReactMarkdown>{pack.markdown}</ReactMarkdown></div>
        </div>
      )}
    </div>
  )
}

export default function ExpedientePage() {
  const { companyId = '' } = useParams()
  const [dossier, setDossier] = useState<Dossier | null>(null)
  const [name, setName] = useState('Empresa')
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    let cancelled = false
    api.getDossier(companyId).then((d) => { if (!cancelled) setDossier(d) }).catch((e: unknown) => setError(errorMessage(e)))
    api.getIdentity(companyId).then((i) => { if (!cancelled) setName(i.nombre) }).catch(() => undefined)
    return () => { cancelled = true }
  }, [companyId])

  const country = async (pais: string) => {
    setBusy(true)
    try { setDossier(await api.setDossierCountry(companyId, pais)) } catch (e) { setError(errorMessage(e)) } finally { setBusy(false) }
  }

  const crumbs = [{ label: 'Mis Empresas', to: '/dashboard' }, { label: name, to: `/gemelo/${companyId}` }, { label: 'Expediente' }]
  if (!dossier) return <AppShell crumbs={crumbs}>{error ? <Alert message={error} /> : <LoadingState label="Abriendo el expediente…" />}</AppShell>
  const pct = dossier.total ? Math.round((dossier.hechos / dossier.total) * 100) : 0

  return (
    <AppShell crumbs={crumbs}>
      <main className="h-full overflow-y-auto">
        <div className="max-w-5xl mx-auto p-4 sm:p-6 space-y-5">
          <Alert message={error} onClose={() => setError(null)} />
          <Card>
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <h1 className="text-2xl font-bold">📁 Expediente de creación</h1>
                <p className="text-sm text-adan-muted mt-1">
                  Todo lo que {name} necesita para existir legalmente y operar. ADÁN prepara cada trámite; tú lo radicas, pagas las tarifas
                  oficiales y subes el soporte para dejarlo validado.
                </p>
              </div>
              <div className="flex gap-1" role="group" aria-label="País de constitución">
                {COUNTRIES.map((c) => (
                  <Button key={c.id} size="sm" variant={dossier.pais === c.id ? 'primary' : 'secondary'} disabled={busy} onClick={() => country(c.id)}>{c.label}</Button>
                ))}
              </div>
            </div>
            <div className="mt-4">
              <div className="flex justify-between text-xs text-adan-muted"><span>{dossier.hechos} de {dossier.total} listos</span><span>{pct} %</span></div>
              <div className="mt-1 h-2 rounded-full bg-adan-surface-2 overflow-hidden"><div className="h-full bg-adan-success transition-all" style={{ width: `${pct}%` }} /></div>
            </div>
            {dossier.pais === 'CO' && <p className="mt-3 text-xs text-adan-muted">En Colombia el registro en la Cámara de Comercio se hace en persona (o en su portal si tu cámara lo permite): ADÁN te deja estatutos, formularios y lista de requisitos listos para llevar.</p>}
            {dossier.pais === 'US' && <p className="mt-3 text-xs text-adan-muted">En Estados Unidos todo es en línea: ADÁN te deja cada formulario con los campos ya respondidos para que solo lo revises, lo envíes y pagues la tarifa del estado o del IRS.</p>}
            {dossier.pais === 'OTRO' && <p className="mt-3 text-xs text-adan-muted">Elige Colombia o Estados Unidos para ver el expediente completo de ese país. Por ahora ves los pasos que aplican en cualquier país.</p>}
          </Card>

          {GROUPS.map((g) => {
            const items = dossier.items.filter((i) => i.grupo === g.id)
            if (!items.length) return null
            return (
              <section key={g.id}>
                <h2 className="text-sm font-semibold uppercase tracking-widest text-adan-muted">{g.icon} {g.label}</h2>
                <div className="mt-2 grid gap-3 md:grid-cols-2">
                  {items.map((i) => <ItemCard key={i.id} item={i} companyId={companyId} onChange={setDossier} onError={setError} />)}
                </div>
              </section>
            )
          })}
          <p className="text-xs text-adan-muted">ADÁN no compra dominios, no radica ni paga trámites por ti: te deja todo listo y valida lo que subes. Las tarifas que ves vienen de fuentes oficiales; confírmalas antes de pagar.</p>
        </div>
      </main>
    </AppShell>
  )
}
