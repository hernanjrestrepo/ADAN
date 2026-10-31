import { useEffect, useState, type FormEvent } from 'react'
import { Navigate, useNavigate } from 'react-router'
import { useAuth } from '../auth/context'
import Logo from '../components/Logo'
import AiDisclaimer from '../components/AiDisclaimer'
import Alert from '../components/ui/Alert'
import Button from '../components/ui/Button'
import { Field } from '../components/ui/Field'
import { LoadingState } from '../components/ui/States'
import { api, errorMessage } from '../lib/api'

// Onboarding (AD-FUNC-06): una sola pregunta y directo a la conversación con ADAN.
// Si la persona vuelve a medio camino, se retoma desde el último paso real (§3.3).
export default function WelcomePage() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [resumeTo, setResumeTo] = useState<string | null>(null)
  // ?nueva=1: crear otra empresa aunque ya tenga una en curso
  const nueva = new URLSearchParams(window.location.search).get('nueva') === '1'
  const [checking, setChecking] = useState(!nueva)
  const [name, setName] = useState('')
  const [stage, setStage] = useState<'idea' | 'existing' | 'explore'>('idea')
  const [starting, setStarting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    if (nueva) return
    api.getOnboarding()
      .then((state) => {
        if (cancelled) return
        if (state.next.step !== 'company' && state.next.company_id) setResumeTo(`/nivel1/${state.next.company_id}`)
      })
      .catch((err: unknown) => { if (!cancelled) setError(errorMessage(err)) })
      .finally(() => { if (!cancelled) setChecking(false) })
    return () => { cancelled = true }
  }, [nueva])

  const start = async (e: FormEvent) => {
    e.preventDefault()
    setStarting(true)
    setError(null)
    try {
      const { company_id } = await api.startOnboarding(name.trim(), stage)
      navigate(`/nivel1/${company_id}`)
    } catch (err) {
      setError(errorMessage(err))
      setStarting(false)
    }
  }

  if (checking) return <LoadingState label="Preparando tu espacio..." />
  if (resumeTo) return <Navigate to={resumeTo} replace />

  const firstName = user?.name.split(' ')[0] ?? ''
  return (
    <div className="min-h-screen flex flex-col">
      <header className="flex items-center justify-end gap-3 p-4 text-sm">
        <span className="text-adan-muted">{user?.name}</span>
        <Button variant="ghost" onClick={async () => { await logout(); navigate('/login') }}>Salir</Button>
      </header>
      <div className="flex-1 flex items-center justify-center p-4">
      <main className="w-full max-w-lg">
        <div className="mb-8"><Logo size="lg" /></div>
        <p className="text-adan-muted">Hola{firstName ? `, ${firstName}` : ''}. Soy ADAN. Solo una pregunta antes de empezar.</p>
        <h1 className="text-3xl font-bold mt-2 mb-6">¿Desde dónde arrancamos?</h1>
        <form onSubmit={start} className="space-y-5">
          <fieldset>
            <legend className="sr-only">¿Desde dónde arrancamos?</legend>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              {([['idea', '💡', 'Tengo una idea'], ['existing', '🏢', 'Ya tengo una empresa'], ['explore', '🧭', 'Quiero explorar opciones']] as const)
                .map(([value, icon, label]) => (
                  <label key={value} className={`flex flex-col gap-1 p-3 rounded-lg border cursor-pointer text-sm ${
                    stage === value ? 'border-adan-accent bg-adan-accent/5' : 'border-adan-border'}`}>
                    <span className="flex items-center gap-2">
                      <input type="radio" name="stage" checked={stage === value} onChange={() => setStage(value)} />
                      <span aria-hidden="true">{icon}</span>
                    </span>
                    {label}
                  </label>
                ))}
            </div>
          </fieldset>
          {stage === 'explore' ? (
            <p className="rounded-lg bg-adan-surface p-3 text-sm text-adan-muted">
              No necesitas una idea. ADAN te pregunta por tu experiencia, lo que sabes hacer, tu tiempo y tu capital, y te
              propone oportunidades que te calcen. Si quieres, ponle un nombre a esta exploración.
            </p>
          ) : null}
          <Field label={stage === 'explore' ? 'Nombre de la exploración (opcional)' : stage === 'existing' ? 'Nombre de la empresa' : 'Nombre de la idea'}
            value={name} onChange={(e) => setName(e.target.value)} required={stage !== 'explore'} maxLength={255}
            placeholder={stage === 'explore' ? 'Ej.: Mi próxima empresa' : 'Ej.: Café Andino'} />
          <Alert message={error} />
          <Button type="submit" block loading={starting} disabled={stage !== 'explore' && !name.trim()}>Empezar con ADAN</Button>
          <p className="text-xs text-adan-muted text-center">
            Lo demás (industria, país, equipo, finanzas) lo iremos completando juntos cuando haga falta.
          </p>
        </form>
        <AiDisclaimer className="mt-10" />
      </main>
      </div>
    </div>
  )
}
