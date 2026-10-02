import type { HTMLAttributes } from 'react'

export default function Card({ className = '', ...props }: HTMLAttributes<HTMLDivElement>) {
  return <div className={`bg-adan-surface border border-adan-border rounded-2xl p-6 shadow-sm shadow-black/20 ${className}`} {...props} />
}
