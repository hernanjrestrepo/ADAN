import { useCallback, useEffect, useState } from 'react'
import AppShell from '../../components/AppShell'
import Alert from '../../components/ui/Alert'
import Button from '../../components/ui/Button'
import Card from '../../components/ui/Card'
import { LoadingState } from '../../components/ui/States'
import Tabs from '../../components/ui/Tabs'
import { api, errorMessage } from '../../lib/api'
import type { Company, CommunityConnection, CommunityListing, CommunityProfile } from '../../types'

type Tab = 'empresas' | 'personas' | 'mio' | 'conexiones'
const TABS: { id: Tab; label: string }[] = [
  { id: 'empresas', label: 'Empresas' }, { id: 'personas', label: 'Personas' }, { id: 'mio', label: 'Mi perfil y mis empresas' }, { id: 'conexiones', label: 'Conexiones' },
]
const STAGE: Record<string, string> = { idea: 'Idea', validacion: 'Validando', operando: 'Operando', escalando: 'Escalando' }
const LOOKING: Record<string, string> = { inversion: 'Inversión', socios: 'Socios', clientes: 'Clientes', proveedores: 'Proveedores', talento: 'Talento', mentoria: 'Mentoría' }
const KIND: Record<string, string> = { emprendedor: 'Emprendedor', empresa: 'Empresa', inversionista: 'Inversionista', mentor: 'Mentor', proveedor: 'Proveedor' }
const input = 'w-full rounded-xl border border-adan-border bg-adan-bg px-3 py-2 text-sm focus:border-adan-accent focus:outline-hidden'

function Seal({ seal }: { seal: CommunityListing['seal'] }) {
  if (!seal || seal.current_level === undefined) return null
  const items = [
    seal.levels_closed.length ? `${seal.levels_closed.length} de 7 Niveles cerrados` : `Nivel ${seal.current_level ?? 1} en curso`,
    seal.problem_score !== null && seal.problem_score !== undefined ? `Problem Score ${seal.problem_score}` : null,
    seal.testimonies ? `${seal.testimonies} testimonios` : null,
    seal.board_decision ? `Board: ${seal.board_decision}` : null,
    seal.arena_passed === true ? 'Pasó La Arena' : seal.arena_passed === false ? 'No ha pasado La Arena' : null,
    seal.breakeven_month ? `Equilibrio en el mes ${seal.breakeven_month}` : null,
  ].filter(Boolean)
  return (
    <div className="mt-3 rounded-xl border border-adan-accent/30 bg-adan-accent/5 p-3" title="Lo calcula ADÁN desde el Gemelo Digital: la empresa no lo puede editar">
      <p className="text-[10px] font-semibold tracking-[0.25em] text-adan-accent">SELLO ADÁN</p>
      <p className="mt-1 text-xs">{items.join(' · ')}</p>
    </div>
  )
}

function ListingCard({ item, onConnect }: { item: CommunityListing; onConnect: (kind: string, message: string) => Promise<void> }) {
  const [open, setOpen] = useState(false)
  const [msg, setMsg] = useState('')
  return (
    <Card className={`p-5! ${item.paradixe_selection ? 'border-amber-400/60! shadow-[0_0_30px_rgba(251,191,36,0.15)]' : ''}`} data-testid="listing">
      <div className="flex items-start justify-between gap-2">
        <div>
          <h3 className="font-bold text-lg">{item.name}</h3>
          <p className="text-sm text-adan-muted">{item.tagline || item.sector}</p>
        </div>
        {item.paradixe_selection && <span className="rounded-full bg-amber-400/15 px-2.5 py-1 text-[11px] font-semibold text-amber-300 whitespace-nowrap">★ Selección Paradixe</span>}
      </div>
      <div className="mt-2 flex flex-wrap gap-1.5 text-[11px]">
        <span className="rounded-full bg-adan-bg px-2 py-0.5">{STAGE[item.stage] ?? item.stage}</span>
        {item.sector && <span className="rounded-full bg-adan-bg px-2 py-0.5">{item.sector}</span>}
        {(item.city || item.country) && <span className="rounded-full bg-adan-bg px-2 py-0.5">{[item.city, item.country].filter(Boolean).join(', ')}</span>}
        {item.looking_for.map((l) => <span key={l} className="rounded-full bg-emerald-500/15 px-2 py-0.5 text-emerald-300">Busca {LOOKING[l]?.toLowerCase() ?? l}</span>)}
      </div>
      {item.description && <p className="mt-3 text-sm line-clamp-3">{item.description}</p>}
      {item.amount_sought_usd && <p className="mt-2 text-sm">Busca USD {item.amount_sought_usd.toLocaleString('es-CO')}</p>}
      {item.paradixe_selection && item.selection_note && <p className="mt-2 text-xs text-amber-200">Por qué la seleccionó Paradixe: {item.selection_note}</p>}
      <Seal seal={item.seal} />
      {!item.mine && (open ? (
        <div className="mt-3 space-y-2">
          <textarea value={msg} onChange={(e) => setMsg(e.target.value)} rows={2} maxLength={2000} placeholder="Cuéntales quién eres y qué te interesa" className={input} aria-label={`Mensaje para ${item.name}`} />
          <div className="flex flex-wrap gap-2">
            <Button size="sm" onClick={async () => { await onConnect('contacto', msg); setOpen(false) }}>Pedir contacto</Button>
            {item.looking_for.includes('inversion') && <Button size="sm" variant="secondary" onClick={async () => { await onConnect('interes_inversion', msg); setOpen(false) }}>💰 Me interesa invertir</Button>}
          </div>
        </div>
      ) : (
        <div className="mt-3 flex gap-2">
          <Button size="sm" onClick={() => setOpen(true)}>Conectar</Button>
          <Button size="sm" variant="ghost" onClick={() => onConnect('seguir', '')}>Seguir</Button>
        </div>
      ))}
    </Card>
  )
}

function Empresas({ onError, notify }: { onError: (m: string) => void; notify: (m: string) => void }) {
  const [items, setItems] = useState<CommunityListing[] | null>(null)
  const [filters, setFilters] = useState({ q: '', stage: '', looking_for: '', seleccion: false })
  const load = useCallback(() => {
    api.listCommunityCompanies(filters).then(setItems).catch((err: unknown) => onError(errorMessage(err)))
  }, [filters, onError])
  useEffect(() => { load() }, [load])
  return (
    <div className="space-y-4">
      <Card className="p-4!">
        <div className="grid gap-2 md:grid-cols-[2fr_1fr_1fr_auto]">
          <input aria-label="Buscar empresas" placeholder="Buscar por nombre o tema" value={filters.q} onChange={(e) => setFilters({ ...filters, q: e.target.value })} className={input} />
          <select aria-label="Etapa" value={filters.stage} onChange={(e) => setFilters({ ...filters, stage: e.target.value })} className={input}>
            <option value="">Todas las etapas</option>{Object.entries(STAGE).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
          </select>
          <select aria-label="Qué busca" value={filters.looking_for} onChange={(e) => setFilters({ ...filters, looking_for: e.target.value })} className={input}>
            <option value="">Busca cualquier cosa</option>{Object.entries(LOOKING).map(([k, v]) => <option key={k} value={k}>Busca {v.toLowerCase()}</option>)}
          </select>
          <label className="flex items-center gap-2 text-sm whitespace-nowrap"><input type="checkbox" checked={filters.seleccion} onChange={(e) => setFilters({ ...filters, seleccion: e.target.checked })} /> ★ Selección Paradixe</label>
        </div>
      </Card>
      {items === null ? <LoadingState label="Cargando empresas..." /> : items.length === 0 ? (
        <p className="text-sm text-adan-muted">Todavía no hay empresas con esos filtros. Publica la tuya en "Mi perfil y mis empresas".</p>
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          {items.map((it) => (
            <ListingCard key={it.id} item={it} onConnect={async (kind, message) => {
              try { await api.connectCommunity({ kind, message, listing_id: it.id }); notify(kind === 'seguir' ? `Ahora sigues a ${it.name}` : `Solicitud enviada a ${it.name}`) } catch (err) { onError(errorMessage(err)) }
            }} />
          ))}
        </div>
      )}
    </div>
  )
}

function Personas({ onError, notify }: { onError: (m: string) => void; notify: (m: string) => void }) {
  const [people, setPeople] = useState<CommunityProfile[] | null>(null)
  const [kind, setKind] = useState('')
  useEffect(() => { api.listCommunityPeople(kind).then(setPeople).catch((err: unknown) => onError(errorMessage(err))) }, [kind, onError])
  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-2">
        {[['', 'Todos'], ...Object.entries(KIND)].map(([k, v]) => (
          <button key={k} type="button" onClick={() => setKind(k ?? '')} className={`rounded-full border px-3 py-1 text-sm ${kind === k ? 'border-adan-accent bg-adan-accent/10' : 'border-adan-border'}`}>{v}</button>
        ))}
      </div>
      {people === null ? <LoadingState label="Cargando..." /> : people.length === 0 ? <p className="text-sm text-adan-muted">Nadie ha publicado su perfil en esta categoría todavía.</p> : (
        <div className="grid gap-4 md:grid-cols-3">
          {people.map((p) => (
            <Card key={p.id} className="p-4!" data-testid="person">
              <div className="flex items-center gap-3">
                <span className="grid h-11 w-11 place-items-center rounded-full bg-linear-to-br from-adan-accent to-violet-500 font-bold text-white">{p.display_name.slice(0, 1)}</span>
                <div><p className="font-semibold">{p.display_name}</p><p className="text-xs text-adan-muted">{KIND[p.kind]}{p.city ? ` · ${p.city}` : ''}</p></div>
              </div>
              {p.headline && <p className="mt-2 text-sm">{p.headline}</p>}
              {p.kind === 'inversionista' && (p.ticket_min_usd || p.ticket_max_usd) && <p className="mt-1 text-xs text-emerald-300">Ticket: USD {(p.ticket_min_usd ?? 0).toLocaleString('es-CO')}–{(p.ticket_max_usd ?? 0).toLocaleString('es-CO')}</p>}
              <Button size="sm" className="mt-3" onClick={async () => {
                try { await api.connectCommunity({ kind: 'contacto', message: '', to_profile_id: p.id }); notify(`Solicitud enviada a ${p.display_name}`) } catch (err) { onError(errorMessage(err)) }
              }}>Conectar</Button>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}

function ListingForm({ company, onError, notify }: { company: Company; onError: (m: string) => void; notify: (m: string) => void }) {
  const [item, setItem] = useState<Partial<CommunityListing>>({ name: company.name, stage: 'idea', looking_for: [] })
  const [published, setPublished] = useState<CommunityListing | null>(null)
  useEffect(() => { api.getMyListing(company.id).then((l) => { setPublished(l); setItem(l) }).catch(() => undefined) }, [company.id])
  const save = async () => {
    try { const l = await api.publishListing(company.id, item); setPublished(l); setItem(l); notify(`${company.name} quedó publicada en la Comunidad`) } catch (err) { onError(errorMessage(err)) }
  }
  const set = (k: keyof CommunityListing, v: unknown) => setItem({ ...item, [k]: v })
  return (
    <Card className="p-5!">
      <div className="flex items-center justify-between"><h3 className="font-bold">{company.name}</h3>{published?.published && <span className="text-xs text-adan-success">● Publicada</span>}</div>
      <div className="mt-3 grid gap-2 md:grid-cols-2">
        <input aria-label="Frase corta" placeholder="Frase corta (qué hace, en una línea)" value={item.tagline ?? ''} onChange={(e) => set('tagline', e.target.value)} className={input} />
        <input aria-label="Sector" placeholder="Sector" value={item.sector ?? ''} onChange={(e) => set('sector', e.target.value)} className={input} />
        <input aria-label="Ciudad" placeholder="Ciudad" value={item.city ?? ''} onChange={(e) => set('city', e.target.value)} className={input} />
        <select aria-label="Etapa de la empresa" value={item.stage ?? 'idea'} onChange={(e) => set('stage', e.target.value)} className={input}>{Object.entries(STAGE).map(([k, v]) => <option key={k} value={k}>{v}</option>)}</select>
      </div>
      <textarea aria-label="Descripción" placeholder="Descripción para la Comunidad" rows={3} value={item.description ?? ''} onChange={(e) => set('description', e.target.value)} className={`${input} mt-2`} />
      <div className="mt-2 flex flex-wrap gap-2 text-sm">
        {Object.entries(LOOKING).map(([k, v]) => (
          <label key={k} className="flex items-center gap-1"><input type="checkbox" checked={(item.looking_for ?? []).includes(k)}
            onChange={(e) => set('looking_for', e.target.checked ? [...(item.looking_for ?? []), k] : (item.looking_for ?? []).filter((x) => x !== k))} /> {v}</label>
        ))}
      </div>
      {(item.looking_for ?? []).includes('inversion') && (
        <input aria-label="Monto que busca" type="number" min={0} placeholder="Monto que buscas (USD)" value={item.amount_sought_usd ?? ''} onChange={(e) => set('amount_sought_usd', e.target.value ? Number(e.target.value) : null)} className={`${input} mt-2 md:w-64`} />
      )}
      {published && <Seal seal={published.seal} />}
      <Button className="mt-3" onClick={save}>{published ? 'Actualizar' : 'Publicar en la Comunidad'}</Button>
      <p className="mt-2 text-[11px] text-adan-muted">El Sello ADÁN se calcula de tu avance real (Niveles, evidencia, Board, La Arena): no se puede editar.</p>
    </Card>
  )
}

function Mio({ onError, notify }: { onError: (m: string) => void; notify: (m: string) => void }) {
  const [profile, setProfile] = useState<CommunityProfile | null>(null)
  const [companies, setCompanies] = useState<Company[]>([])
  useEffect(() => {
    api.getCommunityProfile().then(setProfile).catch((err: unknown) => onError(errorMessage(err)))
    api.getCompanies().then(setCompanies).catch(() => undefined)
  }, [onError])
  if (!profile) return <LoadingState label="Cargando..." />
  const set = (k: keyof CommunityProfile, v: unknown) => setProfile({ ...profile, [k]: v })
  return (
    <div className="space-y-5">
      <Card className="p-5!">
        <h3 className="font-bold">Mi perfil</h3>
        <div className="mt-3 grid gap-2 md:grid-cols-2">
          <input aria-label="Nombre visible" value={profile.display_name ?? ''} onChange={(e) => set('display_name', e.target.value)} className={input} />
          <select aria-label="Qué eres" value={profile.kind} onChange={(e) => set('kind', e.target.value)} className={input}>{Object.entries(KIND).map(([k, v]) => <option key={k} value={k}>{v}</option>)}</select>
          <input aria-label="Titular" placeholder="Titular (ej. Fundadora de Masa Madre)" value={profile.headline ?? ''} onChange={(e) => set('headline', e.target.value)} className={input} />
          <input aria-label="Ciudad del perfil" placeholder="Ciudad" value={profile.city ?? ''} onChange={(e) => set('city', e.target.value)} className={input} />
          <input aria-label="LinkedIn" placeholder="LinkedIn (opcional)" value={profile.linkedin ?? ''} onChange={(e) => set('linkedin', e.target.value)} className={input} />
          <input aria-label="Sitio web" placeholder="Sitio web (opcional)" value={profile.website ?? ''} onChange={(e) => set('website', e.target.value)} className={input} />
        </div>
        <textarea aria-label="Sobre mí" placeholder="Sobre ti" rows={3} value={profile.bio ?? ''} onChange={(e) => set('bio', e.target.value)} className={`${input} mt-2`} />
        {profile.kind === 'inversionista' && (
          <div className="mt-2 grid gap-2 md:grid-cols-2">
            <input aria-label="Ticket mínimo" type="number" placeholder="Ticket mínimo (USD)" value={profile.ticket_min_usd ?? ''} onChange={(e) => set('ticket_min_usd', e.target.value ? Number(e.target.value) : null)} className={input} />
            <input aria-label="Ticket máximo" type="number" placeholder="Ticket máximo (USD)" value={profile.ticket_max_usd ?? ''} onChange={(e) => set('ticket_max_usd', e.target.value ? Number(e.target.value) : null)} className={input} />
          </div>
        )}
        <label className="mt-3 flex items-center gap-2 text-sm"><input type="checkbox" checked={profile.public} onChange={(e) => set('public', e.target.checked)} /> Mostrar mi perfil en la Comunidad (tu correo nunca es público)</label>
        <Button className="mt-3" onClick={async () => { try { setProfile({ ...(await api.saveCommunityProfile(profile)), is_curator: profile.is_curator }); notify('Perfil guardado') } catch (err) { onError(errorMessage(err)) } }}>Guardar perfil</Button>
      </Card>
      <h3 className="font-bold">Mis empresas en la Comunidad</h3>
      {companies.map((c) => <ListingForm key={c.id} company={c} onError={onError} notify={notify} />)}
    </div>
  )
}

function Conexiones({ onError }: { onError: (m: string) => void }) {
  const [box, setBox] = useState<{ received: CommunityConnection[]; sent: CommunityConnection[] } | null>(null)
  const load = useCallback(() => { api.getConnections().then(setBox).catch((err: unknown) => onError(errorMessage(err))) }, [onError])
  useEffect(() => { load() }, [load])
  if (!box) return <LoadingState label="Cargando..." />
  const label = (c: CommunityConnection) => c.kind === 'interes_inversion' ? '💰 Interés de inversión' : c.kind === 'seguir' ? 'Te sigue' : 'Pide contacto'
  return (
    <div className="grid gap-5 md:grid-cols-2">
      {(['received', 'sent'] as const).map((side) => (
        <div key={side}>
          <h3 className="font-bold">{side === 'received' ? 'Recibidas' : 'Enviadas'}</h3>
          <div className="mt-2 space-y-2">
            {box[side].length === 0 && <p className="text-sm text-adan-muted">Nada por ahora.</p>}
            {box[side].map((c) => (
              <Card key={c.id} className="p-4!" data-testid="connection">
                <p className="text-sm font-semibold">{c.other_name}{c.listing_name ? ` · ${c.listing_name}` : ''}</p>
                <p className="text-xs text-adan-muted">{label(c)} · {c.status}</p>
                {c.message && <p className="mt-1 text-sm">“{c.message}”</p>}
                {c.other_email && <p className="mt-1 text-sm text-adan-success">Contacto: {c.other_email}</p>}
                {side === 'received' && c.status === 'pendiente' && (
                  <div className="mt-2 flex gap-2">
                    <Button size="sm" onClick={async () => { await api.respondConnection(c.id, true); load() }}>Aceptar</Button>
                    <Button size="sm" variant="ghost" onClick={async () => { await api.respondConnection(c.id, false); load() }}>Rechazar</Button>
                  </div>
                )}
              </Card>
            ))}
          </div>
        </div>
      ))}
    </div>
  )
}

// La Comunidad ADÁN: empresas con Sello ADÁN, personas, inversionistas y las Selecciones Paradixe
export default function ComunidadPage() {
  const [tab, setTab] = useState<Tab>('empresas')
  const [error, setError] = useState<string | null>(null)
  const [notice, setNotice] = useState<string | null>(null)
  const onError = useCallback((m: string) => setError(m), [])
  const notify = useCallback((m: string) => { setNotice(m); window.setTimeout(() => setNotice(null), 3500) }, [])
  return (
    <AppShell crumbs={[{ label: 'Comunidad' }]} toolbar={<Tabs tabs={TABS} active={tab} onChange={setTab} />}>
      <div className="max-w-6xl mx-auto p-4 sm:p-6 overflow-y-auto h-full">
        <div className="mb-5">
          <h1 className="text-3xl font-bold">Comunidad ADÁN</h1>
          <p className="text-adan-muted mt-1">Empresas que se construyen con evidencia, emprendedores, inversionistas y mentores. El Sello ADÁN muestra el avance real de cada empresa.</p>
        </div>
        {error && <div className="mb-4"><Alert message={error} onClose={() => setError(null)} /></div>}
        {notice && <p className="mb-4 rounded-xl bg-adan-success/15 px-4 py-2 text-sm text-adan-success">{notice}</p>}
        {tab === 'empresas' && <Empresas onError={onError} notify={notify} />}
        {tab === 'personas' && <Personas onError={onError} notify={notify} />}
        {tab === 'mio' && <Mio onError={onError} notify={notify} />}
        {tab === 'conexiones' && <Conexiones onError={onError} />}
      </div>
    </AppShell>
  )
}
