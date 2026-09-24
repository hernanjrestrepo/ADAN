import { createContext, useContext } from 'react'
import type { User } from '../types'

export interface AuthState {
  user: User | null
  setUser: (user: User | null) => void
  logout: () => Promise<void>
}

export const AuthContext = createContext<AuthState | null>(null)

export function useAuth(): AuthState {
  const auth = useContext(AuthContext)
  if (!auth) throw new Error('useAuth debe usarse dentro de <AuthProvider>')
  return auth
}
