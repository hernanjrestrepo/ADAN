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
import type { AdminCompany, AdminMovement, AdminPurchase, AdminSummary, AdminUser } from '../types'

// Consola de Paradixe (solo superadministradores): ver y controlar ADÁN, como la consola de Xmart Travel

type Tab = 'resumen' | 'usuarios' | 'compras' | 'movimientos' | 'empresas'
const TABS: { id: Tab; label: string }[] = [
  { id: 'resumen', label: '📊 Resumen' }, { id: 'usuarios', label: '👥 Usuarios y regalos' },
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

function Users() {
  const [q, setQ] = useState('')
  const [rows, setRows] = useState<AdminUser[] | null>(null)
  const [gift, setGift] = useState<{ id: string; apples: string; reason: string } | null>(null)
  const [msg, setMsg] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

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
                      <Button size="sm" variant="secondary" onClick={() => { setMsg(null); setGift({ id: u.id, apples: '20', reason: 'pruebas' }) }}>🎁 Regalar @pples</Button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>
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
          {tab === 'usuarios' && <Users />}
          {tab === 'compras' && <Table<AdminPurchase> load={api.adminPurchases} empty="Aún no hay compras." cols={[
            ['Fecha', (p) => date(p.created_at)], ['Usuario', (p) => p.email], ['@pples', (p) => `🍎 ${p.apples}`], ['Valor', (p) => cop(p.amount_cop)],
            ['Pasarela', (p) => p.provider], ['Estado', (p) => p.status], ['Transacción', (p) => p.external_id ?? '—'],
          ]} />}
          {tab === 'movimientos' && <Table<AdminMovement> load={api.adminMovements} empty="Aún no hay movimientos." cols={[
            ['Fecha', (m) => date(m.created_at)], ['Usuario', (m) => m.email], ['Tipo', (m) => m.kind],
            ['@pples', (m) => <span className={m.amount >= 0 ? 'text-adan-success' : ''}>{m.amount >= 0 ? '+' : ''}{num(m.amount)}</span>], ['Detalle', (m) => m.detail],
          ]} />}
          {tab === 'empresas' && <Table<AdminCompany> load={api.adminCompanies} empty="Aún no hay empresas." cols={[
            ['Empresa', (c) => c.name], ['Dueño', (c) => c.owner], ['Origen', (c) => c.stage ?? '—'],
            ['Niveles pagados', (c) => (c.levels_paid.length ? c.levels_paid.join(', ') : '—')], ['Creada', (c) => date(c.created_at)],
          ]} />}
        </div>
      </main>
    </AppShell>
  )
}
