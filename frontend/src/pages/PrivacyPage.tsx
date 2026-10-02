import { useEffect, useState } from 'react'
import { Link } from 'react-router'
import { useAuth } from '../auth/context'
import Logo from '../components/Logo'
import Alert from '../components/ui/Alert'
import Card from '../components/ui/Card'
import { api, errorMessage } from '../lib/api'
import type { OnboardingState } from '../types'

// Política de tratamiento de datos (Ley 1581 de 2012, AD-DEC-0002 decisión 8). Versión 2026-10.
const SECTIONS: { title: string; body: string }[] = [
  { title: 'Quién trata tus datos', body: 'Paradixe, a través de ADÁN, es responsable del tratamiento de los datos que registras: tu nombre, tu correo y la información de tus empresas.' },
  { title: 'Para qué', body: 'Para prestarte el servicio: acompañarte nivel por nivel, guardar el Gemelo Digital de tus empresas y producir los análisis que ves. Las respuestas las genera una inteligencia artificial.' },
  { title: 'Inteligencia agregada (opcional)', body: 'Solo si lo autorizas, tus datos se usan anonimizados y agregados con los de otras empresas para producir inteligencia de mercado. Nunca se venden datos crudos ni se identifica a tu empresa.' },
  { title: 'Tus derechos', body: 'Puedes conocer, actualizar y rectificar tus datos, pedir prueba de esta autorización, revocarla y pedir la supresión de tus datos. Cada cambio de consentimiento queda registrado con su fecha; nada se borra en silencio.' },
  { title: 'Cómo ejercerlos', body: 'Desde esta misma página, si tienes sesión, o por el canal de atención de Paradixe. Retirar la autorización de tratamiento equivale a pedir la supresión de la cuenta.' },
]

export default function PrivacyPage() {
  const { user } = useAuth()
  const [state, setState] = useState<OnboardingState | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!user) return
    let cancelled = false
    api.getOnboarding()
      .then((data) => { if (!cancelled) setState(data) })
      .catch((err: unknown) => { if (!cancelled) setError(errorMessage(err)) })
    return () => { cancelled = true }
  }, [user])

  const toggle = async (granted: boolean) => {
    setError(null)
    try {
      const consents = await api.setConsent('aggregated_intelligence', granted)
      setState((prev) => prev && { ...prev, consents })
    } catch (err) {
      setError(errorMessage(err))
    }
  }

  return (
    <div className="min-h-screen">
      <main className="max-w-3xl mx-auto p-4 sm:p-8 space-y-6">
        <Link to={user ? '/dashboard' : '/login'} aria-label="Volver a ADÁN"><Logo /></Link>
        <div>
          <h1 className="text-3xl font-bold">Política de tratamiento de datos</h1>
          <p className="text-sm text-adan-muted mt-1">Versión 2026-10 · Ley 1581 de 2012</p>
        </div>
        {error && <Alert message={error} onClose={() => setError(null)} />}
        {state && (
          <Card data-testid="my-consents">
            <h2 className="font-bold mb-3">Tus autorizaciones</h2>
            <ul className="space-y-3 text-sm">
              <li className="flex items-start justify-between gap-4">
                <span>{state.consents.data_processing.text}</span>
                <span className={state.consents.data_processing.granted ? 'text-adan-success' : 'text-adan-muted'}>
                  {state.consents.data_processing.granted ? 'Autorizado' : 'Sin autorizar'}
                </span>
              </li>
              <li className="flex items-start justify-between gap-4">
                <label className="flex gap-3 items-start">
                  <input type="checkbox" className="mt-1" checked={state.consents.aggregated_intelligence.granted}
                    onChange={(e) => toggle(e.target.checked)} />
                  <span>{state.consents.aggregated_intelligence.text}</span>
                </label>
              </li>
            </ul>
          </Card>
        )}
        {SECTIONS.map((s) => (
          <section key={s.title}>
            <h2 className="text-lg font-bold mb-1">{s.title}</h2>
            <p className="text-adan-text/80">{s.body}</p>
          </section>
        ))}
      </main>
    </div>
  )
}
