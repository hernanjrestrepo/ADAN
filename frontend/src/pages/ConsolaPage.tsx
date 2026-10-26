import { useCallback, useEffect, useState, type ReactNode } from 'react'
import { Navigate } from 'react-router'
import { useAuth } from '../auth/context'
import AppShell from '../components/AppShell'
import Alert from '../components/ui/Alert'
import Button from '../components/ui/Button'
import Card from '../components/ui/Card'
import { LoadingState } from '../components/ui/States'
import Tabs from '../components/ui/Tabs'
import { api, errorMessage } from '../lib/api'
import WorldMap from '../components/WorldMap'
import { countryName } from '../lib/paises'
import type { AdminCompany, AdminMovement, AdminPurchase, AdminSummary, AdminUser, AdminVisits } from '../types'

// Consola de Paradixe (solo superadministradores): ver y controlar ADÁN, como la consola de Xmart Travel

type Tab = 'resumen' | 'visitas' | 'usuarios' | 'compras' | 'movimientos' | 'empresas'
const TABS: { id: Tab; label: string }[] = [
  { id: 'resumen', label: '📊 Resumen' }, { id: 'visitas', label: '🌎 Visitas' }, { id: 'usuarios', label: '👥 Usuarios y regalos' },
  { id: 'compras', label: '💳 Compras' }, { id: 'movimientos', label: '🍎 Movimientos' }, { id: 'empresas', label: '🏢 Empresas' },
]

const cop = (n: number) => n.toLocaleString('es-CO', { style: 'currency', currency: 'COP', maximumFractionDigits: 0 })
const num = (n: number) => n.toLocaleString('es-CO', { maximumFractionDigits: 2 })
const date = (s: string | null) => (s ? new Date(s).toLocaleString('es-CO', { dateStyle: 'short', timeStyle: 'short' }) : '—')

function Kpi({ label, value, hint }: { label: string; value: string; hint?: string }) {
  return (
    <Card className="p-4!">
      <p className="text-xs text-adan-muted">{label}</p>
      <p className="mt-1 text-2xl font-bold">{value}</p>
      {hint && <p className="text-[11px] text-adan-muted mt-0.5">{hint}</p>}
    </Card>
  )
}

function Summary({ s }: { s: AdminSummary }) {
  return (
    <div className="space-y-5">
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        <Kpi label="Usuarios" value={num(s.users)} hint={`${s.users_30d} en los últimos 30 días`} />
        <Kpi label="Empresas" value={num(s.companies)} />
        <Kpi label="Llegaron por invitación" value={num(s.referred_users)} />
        <Kpi label="Ventas reales" value={cop(s.purchases_cop)} hint={`${s.purchases} compras · ${s.apples_sold} @pples`} />
        <Kpi label="@pples en billeteras" value={num(s.apples_in_wallets)} />
        <Kpi label="@pples regaladas" value={num(s.apples_gifted)} hint="bienvenidas y regalos" />
        <Kpi label="Pagado a la red" value={num(s.apples_referral)} hint="0,5 % × 7 niveles" />
        <Kpi label="Margen de los Niveles" value={s.levels_margin === null ? '—' : `${(s.levels_margin * 100).toFixed(1)} %`}
          hint={`${num(s.levels_revenue)} @pples vendidas · costo USD ${num(s.levels_cost)}`} />
      </div>
      <Card>
        <h2 className="font-bold">Niveles pagados</h2>
        <table className="mt-3 w-full text-sm">
          <thead className="text-left text-xs text-adan-muted"><tr><th className="py-2">Nivel</th><th>Precio</th><th>Pagados</th><th>Ingreso</th><th>Costo</th></tr></thead>
          <tbody>
            {s.levels.map((l) => (
              <tr key={l.level} className="border-t border-adan-border">
                <td className="py-2">{l.level}. {l.name}</td><td>🍎 {l.apples}</td><td>{l.paid}</td><td>🍎 {num(l.revenue)}</td><td>USD {num(l.cost)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>
      <Card>
        <h2 className="font-bold">Configuración en producción</h2>
        <ul className="mt-2 grid sm:grid-cols-2 gap-2 text-sm">
          <li>Pasarela: <b>{s.config.provider === 'wompi' ? 'Wompi' : 'Simulador'}</b></li>
          <li>Cobro real: <b className={s.config.live ? 'text-adan-success' : 'text-adan-warning'}>{s.config.live ? 'Encendido' : 'Apagado'}</b></li>
          <li>Exigir pago del Nivel: <b>{s.config.required ? 'Sí' : 'No (todavía no se bloquea)'}</b></li>
          <li>Regalo por invitación: <b>🍎 {s.config.welcome_referral}</b> · TRM de cobro: <b>{cop(s.config.trm)}</b></li>
        </ul>
      </Card>
    </div>
  )
}

function Visits() {
  const [days, setDays] = useState(30)
  const [v, setV] = useState<AdminVisits | null>(null)
  const [error, setError] = useState<string | null>(null)
  useEffect(() => { api.adminVisits(days).then(setV).catch((e: unknown) => setError(errorMessage(e))) }, [days])
  if (error) return <Alert message={error} />
  if (!v) return <LoadingState label="Cargando las visitas…" />
  const pct = (n: number) => (v.visitas ? `${Math.round((100 * n) / v.visitas)} %` : '—')
  const maxDay = Math.max(...v.por_dia.map((d) => d.visitas), 1)
  const maxCountry = Math.max(...v.paises.map((p) => p.visitas), 1)
  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center gap-2">
        {[7, 30, 90, 365].map((d) => (
          <Button key={d} size="sm" variant={days === d ? 'primary' : 'secondary'} onClick={() => setDays(d)}>Últimos {d} días</Button>
        ))}
      </div>
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <Kpi label="Visitas a la página" value={v.visitas.toLocaleString('es-CO')} />
        <Kpi label="Visitantes" value={v.visitantes.toLocaleString('es-CO')} hint={`${v.paises.length} países · ${pct(v.con_cuenta)} con cuenta`} />
        <Kpi label="En línea ahora" value={String(v.ahora)} hint="Últimos 5 minutos" />
        <Kpi label="Desde el celular" value={pct(v.moviles)} hint={`${pct(v.visitas - v.moviles)} desde computador`} />
      </div>
      <div className="grid gap-4 lg:grid-cols-[2fr_1fr]">
        <Card><h3 className="mb-2 font-bold">De qué parte del mundo nos ven</h3><WorldMap countries={v.paises} /></Card>
        <Card>
          <h3 className="mb-2 font-bold">Países</h3>
          {v.paises.length === 0 && <p className="text-sm text-adan-muted">Todavía no hay visitas en el periodo.</p>}
          <ul className="space-y-2">
            {v.paises.slice(0, 12).map((p) => (
              <li key={p.pais} className="text-sm">
                <div className="flex justify-between"><span>{countryName(p.pais)}</span><b>{p.visitas}</b></div>
                <div className="h-1.5 rounded-full bg-adan-surface-2"><div className="h-full rounded-full bg-adan-accent" style={{ width: `${(100 * p.visitas) / maxCountry}%` }} /></div>
              </li>
            ))}
          </ul>
        </Card>
      </div>
      <div className="grid gap-4 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <h3 className="mb-2 font-bold">Visitas por día</h3>
          <div className="flex h-36 items-end gap-1 border-b border-adan-border">
            {v.por_dia.map((d) => (
              <div key={d.dia} title={`${d.dia}: ${d.visitas} visitas · ${d.visitantes} visitantes`} className="flex-1 rounded-t bg-adan-accent hover:opacity-80"
                style={{ height: `${Math.max(3, (100 * d.visitas) / maxDay)}%`, maxWidth: 40 }} />
            ))}
          </div>
        </Card>
        <Card>
          <h3 className="mb-2 font-bold">De dónde llegan</h3>
          <p className="flex justify-between text-sm"><span>Directo</span><b>{v.directas}</b></p>
          {v.referentes.map((r) => <p key={r.origen} className="flex justify-between text-sm"><span>{r.origen}</span><b>{r.visitas}</b></p>)}
          <h3 className="mb-2 mt-4 font-bold">Páginas más vistas</h3>
          {v.paginas.map((p) => <p key={p.ruta} className="flex justify-between text-sm"><span className="truncate">{p.ruta}</span><b>{p.visitas}</b></p>)}
        </Card>
      </div>
    </div>
  )
}

// Confirmación de borrado: hay que escribir el correo o el nombre exacto
function ConfirmDelete({ what, expected, onConfirm, onCancel }: {
  what: string; expected: string; onConfirm: (typed: string) => Promise<void>; onCancel: () => void
}) {
  const [typed, setTyped] = useState('')
  const [busy, setBusy] = useState(false)
  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center bg-black/60 p-3" role="dialog" aria-label={`Borrar ${what}`}>
      <div className="mt-24 w-full max-w-md space-y-3 rounded-2xl border border-adan-danger/50 bg-adan-bg p-5">
        <p className="text-lg font-bold">🗑️ Borrar {what}</p>
        <p className="text-sm text-adan-muted">Se borra definitivamente con todo lo suyo (Niveles, conversaciones, documentos). No se puede deshacer. Escribe <b className="text-adan-text">{expected}</b> para confirmar.</p>
        <input value={typed} onChange={(e) => setTyped(e.target.value)} aria-label="Confirmación" autoFocus
          className="w-full rounded-xl border border-adan-border bg-adan-surface px-3 py-2 text-sm" />
        <div className="flex justify-end gap-2">
          <Button variant="ghost" onClick={onCancel}>Cancelar</Button>
          <Button variant="danger" loading={busy} disabled={typed.trim().toLowerCase() !== expected.trim().toLowerCase()}
            onClick={async () => { setBusy(true); try { await onConfirm(typed) } finally { setBusy(false) } }}>Borrar definitivamente</Button>
        </div>
      </div>
    </div>
  )
}

function Companies() {
  const [rows, setRows] = useState<AdminCompany[] | null>(null)
  const [del, setDel] = useState<AdminCompany | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [msg, setMsg] = useState<string | null>(null)
  const load = useCallback(() => api.adminCompanies().then(setRows).catch((e: unknown) => setError(errorMessage(e))), [])
  useEffect(() => { void load() }, [load])
  if (!rows) return error ? <Alert message={error} /> : <LoadingState label="Cargando empresas…" />
  return (
    <div className="space-y-3">
      <Alert message={error} onClose={() => setError(null)} />
      {msg && <p className="rounded-lg bg-adan-success/10 p-2 text-sm text-adan-success">{msg}</p>}
      <Card className="p-0! overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="text-left text-xs text-adan-muted"><tr>
            <th className="p-3">Empresa</th><th>Dueño</th><th>Origen</th><th>Estado</th><th>Niveles pagados</th><th>Creada</th><th></th>
          </tr></thead>
          <tbody>
            {rows.map((c) => (
              <tr key={c.id} className="border-t border-adan-border">
                <td className="p-3 font-semibold">{c.name}</td><td>{c.owner}</td><td>{c.stage ?? '—'}</td><td>{c.status}</td>
                <td>{c.levels_paid.length ? c.levels_paid.join(', ') : '—'}</td><td>{date(c.created_at)}</td>
                <td className="pr-3"><Button size="sm" variant="ghost" className="text-adan-danger!" onClick={() => { setMsg(null); setDel(c) }}>🗑️ Borrar</Button></td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>
      {del && (
        <ConfirmDelete what={`la empresa «${del.name}»`} expected={del.name} onCancel={() => setDel(null)}
          onConfirm={async (typed) => {
            try {
              await api.adminDeleteCompany(del.id, typed)
              setMsg(`Se borró «${del.name}».`)
              setDel(null)
              await load()
            } catch (e) { setError(errorMessage(e)); setDel(null) }
          }} />
      )}
    </div>
  )
}

function Users() {
  const [q, setQ] = useState('')
  const [rows, setRows] = useState<AdminUser[] | null>(null)
  const [gift, setGift] = useState<{ id: string; apples: string; reason: string } | null>(null)
  const [msg, setMsg] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [del, setDel] = useState<AdminUser | null>(null)

  const enter = async (u: AdminUser) => {
    try {
      await api.adminImpersonate(u.id)
      window.location.assign('/dashboard')
    } catch (e) {
      setError(errorMessage(e))
    }
  }

  const load = useCallback((query: string) => api.adminUsers(query).then(setRows).catch((e: unknown) => setError(errorMessage(e))), [])
  useEffect(() => { void load('') }, [load])

  const send = async () => {
    if (!gift) return
    setError(null)
    try {
      const r = await api.adminGift(gift.id, Number(gift.apples), gift.reason)
      setMsg(`Regalo enviado. Nuevo saldo: 🍎 ${num(r.balance)}`)
      setGift(null)
      await load(q)
    } catch (e) {
      setError(errorMessage(e))
    }
  }

  return (
    <div className="space-y-3">
      <form className="flex gap-2" onSubmit={(e) => { e.preventDefault(); void load(q) }}>
        <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Buscar por nombre o correo" aria-label="Buscar usuarios"
          className="flex-1 rounded-xl border border-adan-border bg-adan-bg px-3 py-2 text-sm" />
        <Button type="submit">Buscar</Button>
      </form>
      <Alert message={error} />
      {msg && <p className="rounded-lg bg-adan-success/10 p-2 text-sm text-adan-success">{msg}</p>}
      {!rows ? <LoadingState label="Cargando usuarios…" /> : (
        <Card className="p-0! overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="text-left text-xs text-adan-muted"><tr>
              <th className="p-3">Usuario</th><th>Saldo</th><th>Empresas</th><th>Niveles</th><th>Compró</th><th>Red</th><th>Registro</th><th></th>
            </tr></thead>
            <tbody>
              {rows.map((u) => (
                <tr key={u.id} className="border-t border-adan-border align-top">
                  <td className="p-3"><b>{u.name}</b><br /><span className="text-xs text-adan-muted">{u.email}</span></td>
                  <td className="py-3">🍎 {num(u.balance)}{u.gift_balance > 0 && <span className="block text-[11px] text-adan-muted">{num(u.gift_balance)} regaladas</span>}</td>
                  <td className="py-3">{u.companies}</td><td className="py-3">{u.levels_paid}</td><td className="py-3">{cop(u.purchased_cop)}</td>
                  <td className="py-3 text-xs">{u.invited} invitados{u.sponsor && <span className="block text-adan-muted">vino de {u.sponsor}</span>}</td>
                  <td className="py-3 text-xs">{date(u.created_at)}</td>
                  <td className="py-3 pr-3">
                    {gift?.id === u.id ? (
                      <div className="flex flex-col gap-1 w-44">
                        <input type="number" min={1} max={10000} value={gift.apples} onChange={(e) => setGift({ ...gift, apples: e.target.value })}
                          aria-label="@pples a regalar" className="rounded-lg border border-adan-border bg-adan-bg px-2 py-1 text-xs" />
                        <input value={gift.reason} onChange={(e) => setGift({ ...gift, reason: e.target.value })} placeholder="Motivo (pruebas…)" maxLength={120}
                          aria-label="Motivo del regalo" className="rounded-lg border border-adan-border bg-adan-bg px-2 py-1 text-xs" />
                        <div className="flex gap-1">
                          <Button size="sm" onClick={send} disabled={!(Number(gift.apples) >= 1)}>Regalar</Button>
                          <Button size="sm" variant="ghost" onClick={() => setGift(null)}>Cancelar</Button>
                        </div>
                      </div>
                    ) : (
                      <div className="flex flex-wrap gap-1">
                        <Button size="sm" variant="secondary" onClick={() => { setMsg(null); setGift({ id: u.id, apples: '20', reason: 'pruebas' }) }}>🎁 Regalar</Button>
                        <Button size="sm" variant="secondary" onClick={() => enter(u)} title="Entrar a su cuenta para revisarla (solo lectura)">👁️ Entrar</Button>
                        <Button size="sm" variant="ghost" className="text-adan-danger!" onClick={() => { setMsg(null); setDel(u) }}>🗑️ Borrar</Button>
                      </div>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>
      )}
      {del && (
        <ConfirmDelete what={`la cuenta de ${del.email}`} expected={del.email} onCancel={() => setDel(null)}
          onConfirm={async (typed) => {
            try {
              await api.adminDeleteUser(del.id, typed)
              setMsg(`Se borró la cuenta ${del.email} y sus empresas.`)
              setDel(null)
              await load(q)
            } catch (e) { setError(errorMessage(e)); setDel(null) }
          }} />
      )}
    </div>
  )
}

function Table<T>({ load, cols, empty }: { load: () => Promise<T[]>; cols: [string, (r: T) => ReactNode][]; empty: string }) {
  const [rows, setRows] = useState<T[] | null>(null)
  const [error, setError] = useState<string | null>(null)
  useEffect(() => { load().then(setRows).catch((e: unknown) => setError(errorMessage(e))) }, [load])
  if (error) return <Alert message={error} />
  if (!rows) return <LoadingState label="Cargando…" />
  if (rows.length === 0) return <p className="text-sm text-adan-muted">{empty}</p>
  return (
    <Card className="p-0! overflow-x-auto">
      <table className="w-full text-sm">
        <thead className="text-left text-xs text-adan-muted"><tr>{cols.map(([h]) => <th key={h} className="p-3">{h}</th>)}</tr></thead>
        <tbody>{rows.map((r, i) => <tr key={i} className="border-t border-adan-border">{cols.map(([h, f]) => <td key={h} className="p-3">{f(r)}</td>)}</tr>)}</tbody>
      </table>
    </Card>
  )
}

export default function ConsolaPage() {
  const { user } = useAuth()
  const [tab, setTab] = useState<Tab>('resumen')
  const [summary, setSummary] = useState<AdminSummary | null>(null)
  const [error, setError] = useState<string | null>(null)
  useEffect(() => { if (user?.is_superadmin) api.adminSummary().then(setSummary).catch((e: unknown) => setError(errorMessage(e))) }, [user])
  if (!user?.is_superadmin) return <Navigate to="/dashboard" replace />

  return (
    <AppShell crumbs={[{ label: 'Consola Paradixe' }]} toolbar={<Tabs tabs={TABS} active={tab} onChange={setTab} />}>
      <main className="h-full overflow-y-auto">
        <div className="max-w-7xl mx-auto p-4 sm:p-6">
          {tab === 'resumen' && (error ? <Alert message={error} /> : summary ? <Summary s={summary} /> : <LoadingState label="Cargando el resumen…" />)}
          {tab === 'visitas' && <Visits />}
          {tab === 'usuarios' && <Users />}
          {tab === 'compras' && <Table<AdminPurchase> load={api.adminPurchases} empty="Aún no hay compras." cols={[
            ['Fecha', (p) => date(p.created_at)], ['Usuario', (p) => p.email], ['@pples', (p) => `🍎 ${p.apples}`], ['Valor', (p) => cop(p.amount_cop)],
            ['Pasarela', (p) => p.provider], ['Estado', (p) => p.status], ['Transacción', (p) => p.external_id ?? '—'],
          ]} />}
          {tab === 'movimientos' && <Table<AdminMovement> load={api.adminMovements} empty="Aún no hay movimientos." cols={[
            ['Fecha', (m) => date(m.created_at)], ['Usuario', (m) => m.email], ['Tipo', (m) => m.kind],
            ['@pples', (m) => <span className={m.amount >= 0 ? 'text-adan-success' : ''}>{m.amount >= 0 ? '+' : ''}{num(m.amount)}</span>], ['Detalle', (m) => m.detail],
          ]} />}
          {tab === 'empresas' && <Companies />}
        </div>
      </main>
    </AppShell>
  )
}
