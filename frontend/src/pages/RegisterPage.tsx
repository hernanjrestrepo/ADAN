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
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      const data = await api.register(email, name, password)
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
        <Alert message={error} />
        <Button type="submit" block disabled={loading}>{loading ? 'Creando cuenta...' : 'Crear cuenta'}</Button>
      </form>
      <p className="text-center text-adan-muted mt-6">
        ¿Ya tienes cuenta?{' '}
        <Link to="/login" className="text-adan-accent hover:underline">Inicia sesión</Link>
      </p>
    </AuthLayout>
  )
}
