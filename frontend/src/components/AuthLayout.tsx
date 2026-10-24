import type { ReactNode } from 'react'
import { Link } from 'react-router'
import AiDisclaimer from './AiDisclaimer'
import Logo from './Logo'

const HIGHLIGHTS = [
  { icon: '🧭', title: '7 Niveles', text: 'Del dolor del cliente al escalamiento, con un cierre que solo tú apruebas.' },
  { icon: '🏛️', title: 'Board Room de 7 roles', text: 'CEO, CTO, CFO, CMO, Legal, Producto y Operaciones; el disenso queda visible.' },
  { icon: '🧬', title: 'Gemelo Digital', text: 'Tu empresa con historia completa: cada decisión y cada cambio quedan registrados.' },
]

// Pantallas de acceso: en escritorio, propuesta de valor a la izquierda y formulario a la derecha
export default function AuthLayout({ subtitle, children }: { subtitle: string; children: ReactNode }) {
  return (
    <div className="min-h-screen grid lg:grid-cols-2">
      <aside className="hidden lg:flex flex-col justify-between p-12 border-r border-adan-border bg-linear-to-br from-adan-primary/60 via-adan-bg to-adan-bg">
        <Logo size="lg" />
        <div>
          <h2 className="text-4xl font-bold leading-tight mb-4">Crea o reinventa tu empresa con un equipo directivo de IA.</h2>
          <p className="text-adan-muted mb-10 max-w-lg">
            ADÁN te acompaña nivel por nivel con evidencia, y tú tomas cada decisión.
          </p>
          <ul className="space-y-6">
            {HIGHLIGHTS.map((h) => (
              <li key={h.title} className="flex gap-4">
                <span className="text-2xl" aria-hidden="true">{h.icon}</span>
                <div>
                  <p className="font-semibold">{h.title}</p>
                  <p className="text-sm text-adan-muted">{h.text}</p>
                </div>
              </li>
            ))}
          </ul>
          <Link to="/universo" className="mt-10 inline-flex items-center gap-2 rounded-xl border border-adan-accent/50 bg-adan-accent/10 px-5 py-3 font-semibold hover:bg-adan-accent/20">
            🌌 Recorre el Universo ADÁN en 3D →
          </Link>
        </div>
        <p className="text-xs text-adan-muted">Paradixe · Sistema Operativo Empresarial</p>
      </aside>
      <div className="flex items-center justify-center p-6">
        <main className="w-full max-w-md">
          <div className="mb-8">
            <div className="lg:hidden mb-6"><Logo size="lg" /></div>
            <h1 className="text-2xl font-bold">{subtitle}</h1>
          </div>
          <div className="bg-adan-surface/70 border border-adan-border rounded-2xl p-6 sm:p-8 shadow-xl shadow-black/30">
            {children}
          </div>
          <Link to="/universo" className="lg:hidden mt-6 block text-center text-sm text-adan-accent hover:underline">🌌 Recorre el Universo ADÁN en 3D →</Link>
          <AiDisclaimer className="mt-6" />
        </main>
      </div>
    </div>
  )
}
