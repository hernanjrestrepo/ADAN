import { useState, type FormEvent } from 'react'
import { Link } from 'react-router'
import { useAuth } from '../auth/context'
import AuthLayout from '../components/AuthLayout'
import Alert from '../components/ui/Alert'
import Button from '../components/ui/Button'
import { Field } from '../components/ui/Field'
import { api, errorMessage } from '../lib/api'

export default function LoginPage() {
  const { setUser } = useAuth()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      const data = await api.login(email, password)
      setUser(data.user)
    } catch (err) {
      setError(errorMessage(err))
    } finally {
      setLoading(false)
    }
  }

  return (
    <AuthLayout subtitle="Sistema Operativo Empresarial">
      <form onSubmit={handleSubmit} className="space-y-4">
        <Field label="Email" type="email" autoComplete="email" value={email}
          onChange={(e) => setEmail(e.target.value)} required />
        <Field label="Contraseña" type="password" autoComplete="current-password" value={password}
          onChange={(e) => setPassword(e.target.value)} required />
        <Alert message={error} />
        <Button type="submit" block disabled={loading}>{loading ? 'Ingresando...' : 'Ingresar'}</Button>
      </form>
      <p className="text-center text-adan-muted mt-6">
        ¿No tienes cuenta?{' '}
        <Link to="/register" className="text-adan-accent hover:underline">Regístrate</Link>
      </p>
    </AuthLayout>
  )
}
