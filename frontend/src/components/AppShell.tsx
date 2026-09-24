import type { ReactNode } from 'react'
import { Link, useNavigate } from 'react-router'
import { useAuth } from '../auth/context'
import AiDisclaimer from './AiDisclaimer'
import Button from './ui/Button'

export interface Crumb {
  label: string
  to?: string
}

interface AppShellProps {
  crumbs?: Crumb[]
  status?: ReactNode
  toolbar?: ReactNode
  children: ReactNode
}

// Marco común de las páginas autenticadas: marca, migas de pan, usuario, salir y aviso de IA
export default function AppShell({ crumbs = [], status, toolbar, children }: AppShellProps) {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = async () => {
    await logout()
    navigate('/login')
  }

  return (
    <div className="min-h-screen bg-adan-bg flex flex-col">
      <header className="border-b border-adan-border px-6 py-3">
        <div className="flex items-center justify-between max-w-7xl mx-auto gap-4">
          <nav aria-label="Ubicación" className="flex items-center gap-2 text-sm min-w-0">
            <Link to="/dashboard" className="text-xl font-bold text-adan-text">ADÁN</Link>
            {crumbs.map((crumb) => (
              <span key={crumb.label} className="flex items-center gap-2 min-w-0">
                <span className="text-adan-muted" aria-hidden="true">/</span>
                {crumb.to ? (
                  <Link to={crumb.to} className="text-adan-muted hover:text-adan-text truncate">{crumb.label}</Link>
                ) : (
                  <span className="text-adan-text font-medium truncate" aria-current="page">{crumb.label}</span>
                )}
              </span>
            ))}
          </nav>
          <div className="flex items-center gap-4 shrink-0">
            {status}
            <span className="text-adan-muted text-sm">{user?.name}</span>
            <Button variant="ghost" onClick={handleLogout}>Salir</Button>
          </div>
        </div>
      </header>
      {toolbar && (
        <div className="border-b border-adan-border px-6">
          <div className="max-w-7xl mx-auto">{toolbar}</div>
        </div>
      )}
      <div className="flex-1 overflow-hidden">{children}</div>
      <footer className="border-t border-adan-border px-6 py-2">
        <AiDisclaimer className="max-w-7xl mx-auto" />
      </footer>
    </div>
  )
}
