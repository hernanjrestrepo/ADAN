import { useCallback, useEffect, useState } from 'react'
import AppShell from '../components/AppShell'
import Alert from '../components/ui/Alert'
import Button from '../components/ui/Button'
import Card from '../components/ui/Card'
import { LoadingState } from '../components/ui/States'
import { api, errorMessage } from '../lib/api'
import type { AppleNetwork, ApplePrices, ApplePurchase, AppleWallet } from '../types'

// Billetera de @pples: 1 @pple = USD 1. Se compran con dinero real (Wompi) y se gastan en los Niveles y servicios de
// ADÁN y Paradixe; no se convierten de vuelta en dinero. También la red: 0,5 % por cada uno de 7 niveles hacia arriba.

const KIND_LABEL: Record<string, string> = {
  compra: '💳 Compra', nivel: '🏁 Nivel', nivel_bono: '🏁 Nivel (regaladas)', referido: '🌳 Red', bienvenida: '🎁 Bienvenida',
  regalo: '🎁 Regalo de Paradixe', ajuste: '⚙️ Ajuste',
}

function cop(n: number) {
  return n.toLocaleString('es-CO', { style: 'currency', currency: 'COP', maximumFractionDigits: 0 })
}

function apples(n: number) {
  return n.toLocaleString('es-CO', { maximumFractionDigits: 3 })
}

export default function ApplesPage() {
  const params = new URLSearchParams(window.location.search)
  const purchaseId = params.get('compra')
  const simulated = params.get('simulador') === '1'
  const [wallet, setWallet] = useState<AppleWallet | null>(null)
  const [prices, setPrices] = useState<ApplePrices | null>(null)
  const [net, setNet] = useState<AppleNetwork | null>(null)
  const [purchase, setPurchase] = useState<ApplePurchase | null>(null)
  const [custom, setCustom] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [copied, setCopied] = useState(false)
  const [showCosts, setShowCosts] = useState(false)

  const refresh = useCallback(() => Promise.all([api.getAppleWallet(), api.getApplePrices(), api.getAppleNetwork()])
    .then(([w, p, n]) => { setWallet(w); setPrices(p); setNet(n) })
    .catch((err: unknown) => setError(errorMessage(err))), [])

  useEffect(() => {
    void refresh()
    if (purchaseId) api.getApplePurchase(purchaseId).then(setPurchase).catch((err: unknown) => setError(errorMessage(err)))
  }, [refresh, purchaseId])

  const buy = async (n: number) => {
    setBusy(true)
    setError(null)
    try {
      const p = await api.buyApples(n)
      // A la página de pago de la pasarela (o a la pantalla del simulador)
      window.location.assign(p.checkout_url)
    } catch (err) {
      setError(errorMessage(err))
      setBusy(false)
    }
  }

  const simulate = async (approve: boolean) => {
    if (!purchase) return
    setBusy(true)
    try {
      setPurchase(await api.simulateApplePurchase(purchase.id, approve))
      await refresh()
    } catch (err) {
      setError(errorMessage(err))
    } finally {
      setBusy(false)
    }
  }

  if (!wallet || !prices || !net) {
    return <AppShell crumbs={[{ label: '@pples' }]}>{error ? <Alert message={error} /> : <LoadingState label="Abriendo tu billetera…" />}</AppShell>
  }
  const customN = Number.parseInt(custom, 10)

  return (
    <AppShell crumbs={[{ label: '@pples' }]}>
      <main className="h-full overflow-y-auto">
        <div className="max-w-6xl mx-auto p-4 sm:p-6 space-y-6">
          <Alert message={error} />

          {purchase && (
            <Card className={purchase.status === 'aprobada' ? 'border-adan-success/50' : purchase.status === 'rechazada' ? 'border-adan-danger/50' : 'border-adan-accent/50'}>
              {purchase.status === 'pendiente' && simulated ? (
                <div>
                  <p className="text-xs font-semibold uppercase tracking-wider text-adan-warning">Pasarela de prueba (simulador)</p>
                  <h2 className="mt-1 text-xl font-bold">Pagar {purchase.apples} @pples · {cop(purchase.amount_cop)}</h2>
                  <p className="mt-1 text-sm text-adan-muted">Aún no hay llaves de Wompi: este paso simula la página de pago. No se cobra dinero real.</p>
                  <div className="mt-4 flex gap-2">
                    <Button onClick={() => simulate(true)} loading={busy}>Aprobar pago de prueba</Button>
                    <Button variant="secondary" onClick={() => simulate(false)} disabled={busy}>Rechazar</Button>
                  </div>
                </div>
              ) : (
                <p className="text-sm">
                  {purchase.status === 'aprobada' ? `✅ Listo: se acreditaron ${purchase.apples} @pples a tu billetera.`
                    : purchase.status === 'rechazada' ? '❌ El pago no se aprobó. No se te cobró nada; puedes intentarlo de nuevo.'
                      : '⏳ Estamos esperando la confirmación de la pasarela. Recarga en unos segundos.'}
                </p>
              )}
            </Card>
          )}

          <section className="grid gap-4 md:grid-cols-3">
            <Card className="md:col-span-1">
              <p className="text-sm text-adan-muted">Tu saldo</p>
              <p className="mt-1 text-5xl font-black">🍎 {apples(wallet.balance)}</p>
              <p className="mt-1 text-xs text-adan-muted">@pples · 1 @pple = USD 1 · se gastan dentro de ADÁN y Paradixe</p>
              {wallet.provider === 'simulador' && <p className="mt-3 rounded-lg bg-adan-warning/10 p-2 text-xs text-adan-warning">Modo de prueba: los pagos se simulan hasta conectar Wompi.</p>}
            </Card>
            <Card className="md:col-span-2">
              <h2 className="font-bold">Cargar @pples</h2>
              <p className="text-xs text-adan-muted mt-1">Pagas en pesos con tarjeta, PSE o Nequi en la página segura de Wompi. TRM de cobro: {cop(prices.trm)} por @pple.</p>
              <div className="mt-4 grid grid-cols-2 sm:grid-cols-4 gap-2">
                {prices.packs.map((n) => (
                  <button key={n} type="button" disabled={busy} onClick={() => buy(n)}
                    className="rounded-xl border border-adan-border p-3 text-left hover:border-adan-accent disabled:opacity-50">
                    <span className="block text-lg font-bold">🍎 {n}</span>
                    <span className="block text-xs text-adan-muted">{cop(n * prices.trm)}</span>
                  </button>
                ))}
              </div>
              <form className="mt-3 flex gap-2" onSubmit={(e) => { e.preventDefault(); if (customN >= 5) void buy(customN) }}>
                <input type="number" min={5} max={5000} value={custom} onChange={(e) => setCustom(e.target.value)} placeholder="Otra cantidad (mín. 5)"
                  aria-label="Cantidad de @pples" className="flex-1 rounded-xl border border-adan-border bg-adan-bg px-3 py-2 text-sm" />
                <Button type="submit" disabled={busy || !(customN >= 5)}>Comprar{customN >= 5 ? ` · ${cop(customN * prices.trm)}` : ''}</Button>
              </form>
            </Card>
          </section>

          <Card>
            <div className="flex flex-wrap items-center justify-between gap-2">
              <div>
                <h2 className="font-bold">Precio de cada Nivel</h2>
                <p className="text-xs text-adan-muted">Los 7 Niveles completos: {prices.total_apples} @pples. Cada Nivel se paga una sola vez por empresa.</p>
              </div>
              <button type="button" onClick={() => setShowCosts((v) => !v)} className="text-xs text-adan-accent hover:underline">
                {showCosts ? 'Ocultar costos' : 'Ver de qué se compone'}
              </button>
            </div>
            <div className="mt-3 overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="text-left text-xs text-adan-muted">
                  <tr><th className="py-2">Nivel</th>{showCosts && <><th>Costo</th><th>Utilidad</th><th>Margen</th></>}<th className="text-right">@pples</th></tr>
                </thead>
                <tbody>
                  {prices.levels.map((l) => (
                    <tr key={l.level} className="border-t border-adan-border">
                      <td className="py-2">{l.level}. {l.name}{l.level === 4 ? ' (planeación)' : ''}</td>
                      {showCosts && <>
                        <td>${l.cost_usd.toFixed(1)}</td><td>${l.profit_usd.toFixed(1)}</td><td>{(l.margin * 100).toFixed(1)} %</td>
                      </>}
                      <td className="text-right font-bold">🍎 {l.apples}</td>
                    </tr>
                  ))}
                  {showCosts && (
                    <tr className="border-t border-adan-border font-semibold">
                      <td className="py-2">Total</td><td>${prices.total_cost_usd.toFixed(1)}</td><td>${prices.total_profit_usd.toFixed(1)}</td>
                      <td>{(prices.margin * 100).toFixed(1)} %</td><td className="text-right">🍎 {prices.total_apples}</td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
            <p className="mt-3 text-xs text-adan-muted">
              Se cotiza aparte: {prices.apart.join(', ').toLowerCase()}. Ejemplo de MVP listo: una landing ~🍎 {prices.mvp_examples.landing?.apples},
              una app sencilla ~🍎 {prices.mvp_examples.app?.apples}; ADÁN te cotiza antes de construir.
            </p>
          </Card>

          <section className="grid gap-4 md:grid-cols-2">
            <Card>
              <h2 className="font-bold">Tu red de @pples</h2>
              <p className="text-xs text-adan-muted mt-1">
                Ganas {(net.rate_per_level * 100).toFixed(1)} % en @pples cada vez que alguien de tu red paga un Nivel, hasta {net.depth} niveles
                hacia abajo (el nivel 1 son las personas que invitas tú). Invitar no da @pples por sí solo: se gana con lo que la red de verdad usa.
              </p>
              <div className="mt-3 flex gap-2">
                <input readOnly value={net.link} aria-label="Tu enlace de invitación" className="flex-1 rounded-xl border border-adan-border bg-adan-bg px-3 py-2 text-xs" />
                <Button variant="secondary" onClick={() => { void navigator.clipboard.writeText(net.link); setCopied(true) }}>{copied ? '¡Copiado!' : 'Copiar'}</Button>
              </div>
              <p className="mt-2 text-xs text-adan-muted">Tu código: <b className="text-adan-text">{net.code}</b>{net.sponsor ? ` · Te invitó ${net.sponsor}` : ''}</p>
              <ol className="mt-4 grid grid-cols-7 gap-1 text-center text-xs">
                {net.levels.map((l) => (
                  <li key={l.depth} className="rounded-lg bg-adan-bg p-2">
                    <span className="block text-adan-muted">N{l.depth}</span>
                    <span className="block text-base font-bold">{l.people}</span>
                    <span className="block text-[10px] text-adan-success">+{apples(l.earned)}</span>
                  </li>
                ))}
              </ol>
              <p className="mt-2 text-right text-sm">Ganado con tu red: <b>🍎 {apples(net.total_earned)}</b></p>
            </Card>
            <Card>
              <h2 className="font-bold">Movimientos</h2>
              {wallet.movements.length === 0 ? (
                <p className="mt-2 text-sm text-adan-muted">Aún no hay movimientos.</p>
              ) : (
                <ul className="mt-2 divide-y divide-adan-border text-sm">
                  {wallet.movements.map((m) => (
                    <li key={m.id} className="flex items-center justify-between gap-3 py-2">
                      <span className="min-w-0">
                        <span className="block text-xs text-adan-muted">{KIND_LABEL[m.kind] ?? m.kind} · {new Date(m.created_at).toLocaleDateString('es-CO')}</span>
                        <span className="block truncate">{m.detail}</span>
                      </span>
                      <span className={`shrink-0 font-semibold ${m.amount >= 0 ? 'text-adan-success' : 'text-adan-text'}`}>{m.amount >= 0 ? '+' : ''}{apples(m.amount)}</span>
                    </li>
                  ))}
                </ul>
              )}
            </Card>
          </section>
        </div>
      </main>
    </AppShell>
  )
}
