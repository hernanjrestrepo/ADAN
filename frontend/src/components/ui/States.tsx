import type { ReactNode } from 'react'
import Spinner from './Spinner'

export function LoadingState({ label }: { label: string }) {
  return (
    <div className="flex flex-col items-center gap-3 text-adan-muted py-16" role="status" aria-busy="true">
      <Spinner className="h-6 w-6 text-adan-accent" />
      <span className="text-sm">{label}</span>
    </div>
  )
}

interface EmptyStateProps {
  icon: string
  title: string
  children?: ReactNode
  action?: ReactNode
}

export function EmptyState({ icon, title, children, action }: EmptyStateProps) {
  return (
    <div className="text-center py-14 px-6 rounded-2xl border border-dashed border-adan-border bg-adan-surface/40">
      <div className="text-5xl mb-4" aria-hidden="true">{icon}</div>
      <h3 className="text-lg font-bold mb-2">{title}</h3>
      {children && <div className="text-adan-muted text-sm mb-5 max-w-md mx-auto">{children}</div>}
      {action}
    </div>
  )
}
