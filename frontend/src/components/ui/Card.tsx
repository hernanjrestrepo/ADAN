import type { HTMLAttributes } from 'react'

export default function Card({ className = '', ...props }: HTMLAttributes<HTMLDivElement>) {
  return <div className={`bg-adan-surface border border-adan-border rounded-xl p-6 ${className}`} {...props} />
}
