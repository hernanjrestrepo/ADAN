import { useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../lib/api'
import AiDisclaimer from '../components/AiDisclaimer'

export default function RegisterPage({ onRegister }) {
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const data = await api.register(email, name, password)
      onRegister(data.user)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-adan-bg">
      <div className="w-full max-w-md p-8">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-adan-text mb-2">ADÁN</h1>
          <p className="text-adan-muted">Crea tu cuenta</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm text-adan-muted mb-1">Nombre</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full px-4 py-3 bg-adan-surface border border-adan-border rounded-lg text-adan-text focus:outline-none focus:border-adan-accent"
              required
            />
          </div>

          <div>
            <label className="block text-sm text-adan-muted mb-1">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-4 py-3 bg-adan-surface border border-adan-border rounded-lg text-adan-text focus:outline-none focus:border-adan-accent"
              required
            />
          </div>

          <div>
            <label className="block text-sm text-adan-muted mb-1">Contraseña</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-3 bg-adan-surface border border-adan-border rounded-lg text-adan-text focus:outline-none focus:border-adan-accent"
              minLength={6}
              required
            />
          </div>

          {error && (
            <div className="text-red-400 text-sm">{error}</div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 bg-adan-accent text-white rounded-lg font-medium hover:bg-blue-600 disabled:opacity-50"
          >
            {loading ? 'Creando cuenta...' : 'Crear cuenta'}
          </button>
        </form>

        <AiDisclaimer className="mt-4 text-center" />

        <p className="text-center text-adan-muted mt-6">
          ¿Ya tienes cuenta?{' '}
          <Link to="/login" className="text-adan-accent hover:underline">
            Inicia sesión
          </Link>
        </p>
      </div>
    </div>
  )
}
