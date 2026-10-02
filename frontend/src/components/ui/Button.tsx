import type { ButtonHTMLAttributes } from 'react'
import Spinner from './Spinner'

type Variant = 'primary' | 'secondary' | 'success' | 'danger' | 'ghost'
type Size = 'sm' | 'md'

const VARIANTS: Record<Variant, string> = {
  primary: 'bg-adan-accent text-white hover:bg-blue-500 shadow-sm shadow-adan-accent/20',
  secondary: 'bg-adan-surface border border-adan-border text-adan-text hover:border-adan-accent hover:bg-adan-surface-2',
  success: 'bg-adan-success text-white hover:bg-emerald-500',
  danger: 'bg-adan-danger text-white hover:bg-red-500',
  ghost: 'text-adan-muted hover:text-adan-text hover:bg-adan-surface',
}

const SIZES: Record<Size, string> = { sm: 'px-3 py-1.5 text-sm', md: 'px-5 py-2.5 text-sm' }

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant
  size?: Size
  block?: boolean
  loading?: boolean
}

export default function Button({
  variant = 'primary', size, block = false, loading = false, className = '', type = 'button', disabled, children,
  ...props
}: ButtonProps) {
  const sizing = SIZES[size ?? (variant === 'ghost' ? 'sm' : 'md')]
  return (
    <button
      type={type}
      disabled={disabled || loading}
      aria-busy={loading || undefined}
      className={`inline-flex items-center justify-center gap-2 rounded-lg font-medium ${sizing} ${VARIANTS[variant]} ${
        block ? 'w-full' : ''} transition-colors disabled:opacity-50 disabled:cursor-not-allowed ${className}`}
      {...props}
    >
      {loading && <Spinner />}
      {children}
    </button>
  )
}
