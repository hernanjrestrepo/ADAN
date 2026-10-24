import { useEffect, useState, type CSSProperties, type ReactNode } from 'react'
import { Link, useNavigate, useParams } from 'react-router'
import { useAuth } from '../auth/context'
import { api } from '../lib/api'
import type { Company } from '../types'
import CompanyBar from './CompanyBar'
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

// Los colores de la empresa reemplazan los de ADÁN mientras trabajas en ella
function brandStyle(company: Company | null): CSSProperties | undefined {
  if (!company?.brand_color) return undefined
  return { '--color-adan-accent': company.brand_color, '--color-adan-secondary': company.brand_accent ?? company.brand_color } as CSSProperties
}

// Marco común de las páginas autenticadas: marca, migas de pan, usuario, salir y aviso de IA. Dentro de una empresa
// muestra su identidad, el selector de empresas y la checklist de los 7 Niveles.
export default function AppShell({ crumbs = [], status, toolbar, children }: AppShellProps) {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const { companyId } = useParams()
  const [company, setCompany] = useState<Company | null>(null)
  const [apples, setApples] = useState<number | null>(null)

  useEffect(() => {
    if (!companyId) return
    let cancelled = false
    api.getCompany(companyId).then((c) => { if (!cancelled) setCompany(c) }).catch(() => undefined)
    return () => { cancelled = true }
  }, [companyId])

  useEffect(() => {
    let cancelled = false
    api.getAppleWallet().then((w) => { if (!cancelled) setApples(w.balance) }).catch(() => undefined)
    return () => { cancelled = true }
  }, [])

  const handleLogout = async () => {
    await logout()
    navigate('/login')
  }

  return (
    <div className="min-h-screen flex flex-col" style={companyId ? brandStyle(company) : undefined}>
      <a href="#contenido" className="sr-only focus:not-sr-only focus:fixed focus:top-2 focus:left-2 focus:z-50 focus:rounded-lg focus:bg-adan-accent focus:px-4 focus:py-2 focus:text-white">
        Saltar al contenido
      </a>
      <header className="sticky top-0 z-40 border-b border-adan-border bg-adan-bg/85 backdrop-blur-sm px-4 sm:px-6 py-3">
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
            <Link to="/apples" title="Tu billetera de @pples (1 @pple = USD 1)"
              className="flex items-center gap-1 rounded-full border border-adan-border px-3 py-1 text-sm hover:border-adan-accent">
              <span aria-hidden="true">🍎</span><span className="font-semibold">{apples === null ? '…' : apples.toLocaleString('es-CO', { maximumFractionDigits: 2 })}</span>
              <span className="hidden lg:inline text-adan-muted">@pples</span>
            </Link>
            <Link to="/comunidad" className="hidden md:inline text-sm text-adan-muted hover:text-adan-text" title="La red de empresas e inversionistas">🤝 Comunidad</Link>
            <Link to="/universo" className="hidden md:inline text-sm text-adan-muted hover:text-adan-text" title="La oficina 3D de ADÁN">🌌 Universo</Link>
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
      {companyId && <CompanyBar companyId={companyId} company={company} onCompany={setCompany} />}
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
