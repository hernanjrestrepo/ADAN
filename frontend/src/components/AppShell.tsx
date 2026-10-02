import type { ReactNode } from 'react'
import { Link, useNavigate } from 'react-router'
import { useAuth } from '../auth/context'
import AiDisclaimer from './AiDisclaimer'
import Logo from './Logo'
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

function initials(name = '') {
  return name.split(/\s+/).filter(Boolean).slice(0, 2).map((p) => p[0]?.toUpperCase()).join('') || '·'
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
    <div className="min-h-screen flex flex-col">
      <a href="#contenido" className="sr-only focus:not-sr-only focus:fixed focus:top-2 focus:left-2 focus:z-50 focus:rounded-lg focus:bg-adan-accent focus:px-4 focus:py-2 focus:text-white">
        Saltar al contenido
      </a>
      <header className="sticky top-0 z-40 border-b border-adan-border bg-adan-bg/85 backdrop-blur px-4 sm:px-6 py-3">
        <div className="flex items-center justify-between max-w-7xl mx-auto gap-4">
          <nav aria-label="Ubicación" className="flex items-center gap-2 text-sm min-w-0">
            <Link to="/dashboard" aria-label="ADÁN, ir a Mis Empresas" className="shrink-0">
              <span className="sm:hidden"><Logo compact /></span>
              <span className="hidden sm:inline"><Logo /></span>
            </Link>
            {crumbs.map((crumb, i) => (
              <span key={crumb.label}
                className={`items-center gap-2 min-w-0 ${i < crumbs.length - 1 ? 'hidden md:flex' : 'flex'}`}>
                <span className="text-adan-border" aria-hidden="true">/</span>
                {crumb.to ? (
                  <Link to={crumb.to} className="text-adan-muted hover:text-adan-text truncate">{crumb.label}</Link>
                ) : (
                  <span className="text-adan-text font-medium truncate" aria-current="page">{crumb.label}</span>
                )}
              </span>
            ))}
          </nav>
          <div className="flex items-center gap-3 shrink-0">
            {status}
            <span className="hidden sm:flex items-center gap-2" title={user?.email}>
              <span aria-hidden="true"
                className="grid h-8 w-8 place-items-center rounded-full bg-adan-surface-2 text-xs font-semibold text-adan-text">
                {initials(user?.name)}
              </span>
              <span className="text-adan-muted text-sm">{user?.name}</span>
            </span>
            <Button variant="ghost" onClick={handleLogout}>Salir</Button>
          </div>
        </div>
      </header>
      {toolbar && (
        <div className="border-b border-adan-border px-4 sm:px-6 bg-adan-bg/60">
          <div className="max-w-7xl mx-auto">{toolbar}</div>
        </div>
      )}
      <div id="contenido" className="flex-1 overflow-hidden">{children}</div>
      <footer className="border-t border-adan-border px-4 sm:px-6 py-2">
        <AiDisclaimer className="max-w-7xl mx-auto" />
      </footer>
    </div>
  )
}
