import { useCallback, useEffect, useMemo, useState, type ReactNode } from 'react'
import { api } from '../lib/api'
import type { User } from '../types'
import { AuthContext } from './context'
import { LoadingState } from '../components/ui/States'

export default function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Si hay cookie de sesión válida, /auth/me devuelve el usuario
    api.getMe()
      .then(setUser)
      .catch(() => setUser(null))
      .finally(() => setLoading(false))
  }, [])

  const logout = useCallback(async () => {
    await api.logout()
    setUser(null)
  }, [])

  const value = useMemo(() => ({ user, setUser, logout }), [user, logout])

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingState label="Cargando..." />
      </div>
    )
  }
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
