import { useEffect, useState } from 'react'
import MicButton from '../../components/MicButton'
import Button from '../../components/ui/Button'
import Card from '../../components/ui/Card'
import { LoadingState } from '../../components/ui/States'
import { api, errorMessage } from '../../lib/api'
import type { ArenaInvestor, ArenaSession } from '../../types'

const DECISION: Record<string, { label: string; className: string }> = {
  INVIERTE: { label: 'Invierte', className: 'bg-adan-success/20 text-adan-success' },
  CON_CONDICIONES: { label: 'Invierte con condiciones', className: 'bg-yellow-500/20 text-yellow-300' },
  NO_INVIERTE: { label: 'No invierte', className: 'bg-adan-danger/20 text-red-300' },
  SIN_RESPUESTA: { label: 'No respondió', className: 'bg-gray-500/20 text-gray-300' },
}

const usd = (n: number) => `USD ${n.toLocaleString('es-CO')}`

function InvestorCard({ inv, answer, onAnswer, decided }: {
  inv: ArenaInvestor; answer: string; onAnswer: (v: string) => void; decided: boolean
}) {
  const d = inv.decision ? DECISION[inv.decision] : undefined
  return (
    <Card data-testid="arena-investor">
      <div className="flex items-start gap-3">
        <span className="text-3xl" aria-hidden="true">{inv.avatar}</span>
        <div className="flex-1 min-w-0">
          <h3 className="font-bold">{inv.name}</h3>
          <p className="text-xs text-adan-muted">{inv.role}</p>
        </div>
        {d && <span className={`rounded-full px-3 py-1 text-xs font-semibold ${d.className}`}>{d.label}</span>}
      </div>
      <p className="text-sm mt-3 italic text-adan-text/90">“{inv.first_impression}”</p>
      {inv.red_flags.length > 0 && (
        <ul className="mt-2 space-y-1 text-xs text-orange-300">{inv.red_flags.map((f) => <li key={f}>🚩 {f}</li>)}</ul>
      )}
      <div className="mt-3 space-y-1">
        {inv.questions.map((q) => <p key={q} className="text-sm font-medium">❓ {q}</p>)}
      </div>
      {decided ? (
        <div className="mt-3 space-y-2 text-sm">
          {inv.answer && <p className="text-xs text-adan-muted">Tu respuesta: {inv.answer}</p>}
          <p>{inv.reason}</p>
          {(inv.amount_usd ?? 0) > 0 && <p className="font-semibold text-adan-success">{usd(inv.amount_usd ?? 0)} · {inv.terms}</p>}
          {(inv.conditions ?? []).length > 0 && (
            <ul className="list-disc pl-5 text-xs text-adan-muted">{(inv.conditions ?? []).map((c) => <li key={c}>{c}</li>)}</ul>
          )}
          {inv.fatal_flaw && <p className="rounded-lg bg-adan-danger/10 px-3 py-2 text-xs text-red-300">☠️ Falla fatal: {inv.fatal_flaw}</p>}
        </div>
      ) : (
        <textarea aria-label={`Tu respuesta a ${inv.name}`} value={answer} onChange={(e) => onAnswer(e.target.value)} rows={3}
          maxLength={4000} placeholder="Responde con datos: cifras, clientes, ventas, contratos…"
          className="mt-3 w-full resize-y rounded-xl border border-adan-border bg-adan-bg px-3 py-2 text-sm focus:border-adan-accent focus:outline-hidden" />
      )}
      {!decided && (
        <div className="mt-2 flex justify-end">
          <MicButton onText={(t) => onAnswer(answer ? `${answer} ${t}` : t)} className="rounded-lg border border-adan-border px-3 py-1.5 text-sm hover:border-adan-accent" />
        </div>
      )}
    </Card>
  )
}

// La Arena: cuatro inversionistas exigentes. No se pasa hasta convencerlos (como un nivel de videojuego)
export default function ArenaPanel({ companyId, onError }: { companyId: string; onError: (m: string) => void }) {
  const [session, setSession] = useState<ArenaSession | null>(null)
  const [loading, setLoading] = useState(true)
  const [busy, setBusy] = useState(false)
  const [pitch, setPitch] = useState('')
  const [answers, setAnswers] = useState<Record<string, string>>({})

  useEffect(() => {
    let cancelled = false
    api.getLastArena(companyId).then((s) => { if (!cancelled) setSession(s) }).catch(() => undefined)
      .finally(() => { if (!cancelled) setLoading(false) })
    return () => { cancelled = true }
  }, [companyId])

  const start = async () => {
    setBusy(true)
    try {
      setSession(await api.startArena(companyId, pitch))
      setAnswers({})
    } catch (err) { onError(errorMessage(err)) } finally { setBusy(false) }
  }
  const respond = async () => {
    if (!session) return
    setBusy(true)
    try { setSession(await api.answerArena(companyId, session.id, answers)) } catch (err) { onError(errorMessage(err)) } finally { setBusy(false) }
  }

  if (loading) return <LoadingState label="Abriendo La Arena..." />
  const decided = session?.phase === 'decided'

  return (
    <div className="max-w-5xl mx-auto p-6 overflow-y-auto h-full">
      <div className="rounded-2xl border border-orange-400/30 bg-linear-to-br from-orange-500/10 via-adan-surface to-adan-surface p-6">
        <p className="text-xs font-semibold tracking-[0.3em] text-orange-300">⚔️ LA ARENA</p>
        <h2 className="text-2xl font-bold mt-1">Cuatro inversionistas. Ninguno regala su dinero.</h2>
        <p className="text-sm text-adan-muted mt-2 max-w-3xl">
          Presenta tu empresa a un ángel, un fondo de capital de riesgo, un banco y un inversionista estratégico del sector.
          Primero te hacen sus preguntas más difíciles; después cada uno decide. Pasas con al menos 2 respaldos y ninguna falla
          fatal. Es una simulación para que llegues preparado a los inversionistas reales.
        </p>
        {(!session || decided) && (
          <div className="mt-4">
            <textarea aria-label="Tu pitch" value={pitch} onChange={(e) => setPitch(e.target.value)} rows={3} maxLength={8000}
              placeholder="Opcional: tu pitch en tus palabras. Si lo dejas vacío, los inversionistas leen lo que ADAN ya sabe de tu empresa."
              className="w-full resize-y rounded-xl border border-adan-border bg-adan-bg px-3 py-2 text-sm focus:border-adan-accent focus:outline-hidden" />
            <MicButton onText={(t) => setPitch((v) => (v ? `${v} ${t}` : t))} className="mt-3 mr-2 rounded-lg border border-adan-border px-3 py-2 text-sm hover:border-adan-accent" />
            <Button className="mt-3" onClick={start} loading={busy}>{session ? 'Volver a entrar a La Arena' : 'Entrar a La Arena'}</Button>
          </div>
        )}
      </div>

      {busy && <div className="mt-6"><LoadingState label={session && !decided ? 'Los inversionistas están deliberando...' : 'Los inversionistas leen tu empresa...'} /></div>}

      {session && !busy && (
        <>
          {decided && (
            <div data-testid="arena-verdict" className={`mt-6 rounded-2xl p-5 ${session.passed ? 'bg-adan-success/15 border border-adan-success/40' : 'bg-adan-danger/10 border border-adan-danger/40'}`}>
              <p className="text-lg font-bold">{session.passed ? '🏆 ' : '🛡️ '}{session.verdict}</p>
              {session.passed && (session.total_usd ?? 0) > 0 && <p className="text-sm mt-1">Respaldo simulado total: {usd(session.total_usd ?? 0)}</p>}
            </div>
          )}
          <div className="mt-6 grid gap-4 md:grid-cols-2">
            {session.investors.map((inv) => (
              <InvestorCard key={inv.id} inv={inv} decided={decided} answer={answers[inv.id] ?? ''}
                onAnswer={(v) => setAnswers((a) => ({ ...a, [inv.id]: v }))} />
            ))}
          </div>
          {!decided && (
            <div className="mt-6 flex justify-end">
              <Button onClick={respond} loading={busy}>Responder a los inversionistas</Button>
            </div>
          )}
        </>
      )}
    </div>
  )
}
