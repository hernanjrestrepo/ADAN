import { useState, type FormEvent } from 'react'
import { Link } from 'react-router'
import { useAuth } from '../auth/context'
import AuthLayout from '../components/AuthLayout'
import Alert from '../components/ui/Alert'
import Button from '../components/ui/Button'
import { Field } from '../components/ui/Field'
import { api, errorMessage } from '../lib/api'

export default function RegisterPage() {
  const { setUser } = useAuth()
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [acceptDataPolicy, setAcceptDataPolicy] = useState(false)
  const [shareAggregated, setShareAggregated] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      const data = await api.register(email, name, password, { acceptDataPolicy, shareAggregated })
      setUser(data.user)
    } catch (err) {
      setError(errorMessage(err))
    } finally {
      setLoading(false)
    }
  }

  return (
    <AuthLayout subtitle="Crea tu cuenta">
      <form onSubmit={handleSubmit} className="space-y-4">
        <Field label="Nombre" type="text" autoComplete="name" value={name}
          onChange={(e) => setName(e.target.value)} required />
        <Field label="Email" type="email" autoComplete="email" value={email}
          onChange={(e) => setEmail(e.target.value)} required />
        {/* La política completa la valida el backend (WO-097): 10+ caracteres, máx. 72 bytes */}
        <Field label="Contraseña" type="password" autoComplete="new-password" value={password}
          onChange={(e) => setPassword(e.target.value)} minLength={10} maxLength={72} required
          hint="Mínimo 10 caracteres." />
        {/* Consentimiento explícito (Ley 1581 de 2012, AD-DEC-0002 decisión 8) */}
        <div className="space-y-3 rounded-lg border border-adan-border p-4 text-sm">
          <label className="flex gap-3 items-start">
            <input type="checkbox" className="mt-1" checked={acceptDataPolicy} required
              onChange={(e) => setAcceptDataPolicy(e.target.checked)} />
            <span>
              Acepto la{' '}
              <Link to="/privacidad" target="_blank" className="text-adan-accent hover:underline">
                política de tratamiento de datos
              </Link>{' '}
              para que ADÁN me preste el servicio. <span className="text-adan-muted">(Obligatorio)</span>
            </span>
          </label>
          <label className="flex gap-3 items-start">
            <input type="checkbox" className="mt-1" checked={shareAggregated}
              onChange={(e) => setShareAggregated(e.target.checked)} />
            <span>
              Autorizo usar mis datos <strong>anonimizados y agregados</strong> para inteligencia de mercado. Nunca
              se venden datos crudos. <span className="text-adan-muted">(Opcional; puedes cambiarlo cuando quieras)</span>
            </span>
          </label>
        </div>
        <Alert message={error} />
        <Button type="submit" block loading={loading} disabled={!acceptDataPolicy}>Crear cuenta</Button>
      </form>
      <p className="text-center text-adan-muted mt-6">
        ¿Ya tienes cuenta?{' '}
        <Link to="/login" className="text-adan-accent hover:underline">Inicia sesión</Link>
      </p>
    </AuthLayout>
  )
}
