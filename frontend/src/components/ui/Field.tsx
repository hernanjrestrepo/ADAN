import { useId, type InputHTMLAttributes, type TextareaHTMLAttributes } from 'react'

const CONTROL =
  'w-full px-4 py-3 bg-adan-bg border border-adan-border rounded-lg text-adan-text ' +
  'placeholder:text-adan-muted/70 focus:outline-none focus:border-adan-accent'

interface FieldProps extends InputHTMLAttributes<HTMLInputElement> {
  label: string
  hint?: string
}

export function Field({ label, hint, className = '', ...props }: FieldProps) {
  const id = useId()
  return (
    <div className={className}>
      <label htmlFor={id} className="block text-sm text-adan-muted mb-1">{label}</label>
      <input id={id} className={CONTROL} {...props} />
      {hint && <p className="text-xs text-adan-muted mt-1">{hint}</p>}
    </div>
  )
}

interface TextAreaFieldProps extends TextareaHTMLAttributes<HTMLTextAreaElement> {
  label: string
}

export function TextAreaField({ label, className = '', ...props }: TextAreaFieldProps) {
  const id = useId()
  return (
    <div className={className}>
      <label htmlFor={id} className="block text-sm text-adan-muted mb-1">{label}</label>
      <textarea id={id} className={`${CONTROL} h-20 resize-none`} {...props} />
    </div>
  )
}
