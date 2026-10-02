// Marca de ADÁN: monograma + nombre. `compact` muestra solo el monograma (móvil)
export default function Logo({ compact = false, size = 'md' }: { compact?: boolean; size?: 'md' | 'lg' }) {
  const box = size === 'lg' ? 'h-12 w-12 text-2xl' : 'h-8 w-8 text-base'
  return (
    <span className="flex items-center gap-2">
      <span aria-hidden="true"
        className={`${box} grid place-items-center rounded-lg bg-gradient-to-br from-adan-accent to-indigo-500 font-black text-white shadow-lg shadow-adan-accent/20`}>
        A
      </span>
      {!compact && <span className={`${size === 'lg' ? 'text-3xl' : 'text-lg'} font-bold tracking-tight text-adan-text`}>ADÁN</span>}
    </span>
  )
}
