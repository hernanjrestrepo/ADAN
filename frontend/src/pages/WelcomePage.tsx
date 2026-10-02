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

// Onboarding (AD-FUNC-06): una sola pregunta y directo a la conversación con ADÁN.
// Si la persona vuelve a medio camino, se retoma desde el último paso real (§3.3).
export default function WelcomePage() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [resumeTo, setResumeTo] = useState<string | null>(null)
  const [checking, setChecking] = useState(true)
  const [name, setName] = useState('')
  const [stage, setStage] = useState<'idea' | 'existing'>('idea')
  const [starting, setStarting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    api.getOnboarding()
      .then((state) => {
        if (cancelled) return
        if (state.next.step !== 'company' && state.next.company_id) setResumeTo(`/nivel1/${state.next.company_id}`)
      })
      .catch((err: unknown) => { if (!cancelled) setError(errorMessage(err)) })
      .finally(() => { if (!cancelled) setChecking(false) })
    return () => { cancelled = true }
  }, [])

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
        <p className="text-adan-muted">Hola{firstName ? `, ${firstName}` : ''}. Solo una pregunta antes de empezar.</p>
        <h1 className="text-3xl font-bold mt-2 mb-6">¿Cómo se llama tu empresa o tu idea?</h1>
        <form onSubmit={start} className="space-y-5">
          <Field label="Nombre de la empresa o de la idea" value={name} onChange={(e) => setName(e.target.value)}
            required maxLength={255} autoFocus placeholder="Ej.: Café Andino" />
          <fieldset>
            <legend className="sr-only">¿Ya existe?</legend>
            <div className="grid grid-cols-2 gap-3">
              {([['idea', 'Es una idea'], ['existing', 'Ya existe']] as const).map(([value, label]) => (
                <label key={value} className={`flex items-center gap-2 p-3 rounded-lg border cursor-pointer text-sm ${
                  stage === value ? 'border-adan-accent bg-adan-accent/5' : 'border-adan-border'}`}>
                  <input type="radio" name="stage" checked={stage === value} onChange={() => setStage(value)} />
                  {label}
                </label>
              ))}
            </div>
          </fieldset>
          <Alert message={error} />
          <Button type="submit" block loading={starting} disabled={!name.trim()}>Empezar con ADÁN</Button>
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
