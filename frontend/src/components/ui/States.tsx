import type { ReactNode } from 'react'

export function LoadingState({ label }: { label: string }) {
  return <div className="text-center text-adan-muted py-12" aria-busy="true">{label}</div>
}

interface EmptyStateProps {
  icon: string
  title: string
  children?: ReactNode
  action?: ReactNode
}

export function EmptyState({ icon, title, children, action }: EmptyStateProps) {
  return (
    <div className="text-center py-12">
      <div className="text-5xl mb-3" aria-hidden="true">{icon}</div>
      <h3 className="text-lg font-bold mb-2">{title}</h3>
      {children && <div className="text-adan-muted text-sm mb-4">{children}</div>}
      {action}
    </div>
  )
}
