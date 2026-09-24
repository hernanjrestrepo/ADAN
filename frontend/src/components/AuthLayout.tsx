import type { ReactNode } from 'react'
import AiDisclaimer from './AiDisclaimer'

export default function AuthLayout({ subtitle, children }: { subtitle: string; children: ReactNode }) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-adan-bg">
      <main className="w-full max-w-md p-8">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-adan-text mb-2">ADÁN</h1>
          <p className="text-adan-muted">{subtitle}</p>
        </div>
        {children}
        <AiDisclaimer className="mt-6 text-center" />
      </main>
    </div>
  )
}
