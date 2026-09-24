import type { ButtonHTMLAttributes } from 'react'

type Variant = 'primary' | 'secondary' | 'success' | 'ghost'

const VARIANTS: Record<Variant, string> = {
  primary: 'bg-adan-accent text-white hover:bg-blue-600',
  secondary: 'bg-adan-surface border border-adan-border text-adan-text hover:border-adan-accent',
  success: 'bg-adan-success text-white hover:bg-emerald-600',
  ghost: 'text-adan-muted hover:text-adan-text',
}

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant
  block?: boolean
}

export default function Button({ variant = 'primary', block = false, className = '', type = 'button', ...props }: ButtonProps) {
  const size = variant === 'ghost' ? 'text-sm' : 'px-5 py-3 rounded-lg text-sm font-medium'
  return (
    <button
      type={type}
      className={`${size} ${VARIANTS[variant]} ${block ? 'w-full' : ''} transition-colors disabled:opacity-50 disabled:cursor-not-allowed ${className}`}
      {...props}
    />
  )
}
