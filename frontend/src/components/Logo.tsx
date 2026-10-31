import { useId } from 'react'

// Marca de ADAN, alineada con la oficina virtual: un hexágono de neón (como los pisos de las zonas), una "A" que
// sube hacia una chispa (la idea que nace) y un anillo orbital como travesaño (la mesa del Board Room).
export function AdanMark({ size = 40, className = '' }: { size?: number; className?: string }) {
  const id = useId().replace(/:/g, '')
  return (
    <svg viewBox="0 0 64 64" width={size} height={size} className={className} role="img" aria-label="ADAN">
      <defs>
        <linearGradient id={`g${id}`} x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor="#67e8f9" />
          <stop offset="0.5" stopColor="#7c9bff" />
          <stop offset="1" stopColor="#e879f9" />
        </linearGradient>
        <radialGradient id={`c${id}`} cx="0.5" cy="0.45" r="0.6">
          <stop offset="0" stopColor="#12224b" />
          <stop offset="1" stopColor="#0a0a0f" />
        </radialGradient>
        <filter id={`f${id}`} x="-40%" y="-40%" width="180%" height="180%">
          <feGaussianBlur stdDeviation="1.6" result="b" />
          <feMerge><feMergeNode in="b" /><feMergeNode in="SourceGraphic" /></feMerge>
        </filter>
      </defs>
      <path d="M32 3 L57 17.5 V46.5 L32 61 L7 46.5 V17.5 Z" fill={`url(#c${id})`} stroke={`url(#g${id})`} strokeWidth="2.2"
        strokeLinejoin="round" />
      <g filter={`url(#f${id})`} fill="none" stroke={`url(#g${id})`} strokeLinecap="round" strokeLinejoin="round">
        <path d="M19 47 L32 16 L45 47" strokeWidth="4.2" />
        <ellipse cx="32" cy="37" rx="14.5" ry="4.2" strokeWidth="2.2" transform="rotate(-8 32 37)" />
      </g>
      <circle cx="32" cy="14.5" r="3.4" fill="#ffffff" filter={`url(#f${id})`} />
      <circle cx="45.6" cy="35" r="1.6" fill="#e879f9" />
    </svg>
  )
}

// Logo completo: símbolo + ADAN + "by Paradixe". `compact` muestra solo el símbolo (móvil)
export default function Logo({ compact = false, size = 'md' }: { compact?: boolean; size?: 'md' | 'lg' }) {
  const lg = size === 'lg'
  return (
    <span className="flex items-center gap-2.5">
      <AdanMark size={lg ? 52 : 34} className="drop-shadow-[0_0_12px_rgba(124,155,255,0.45)]" />
      {!compact && (
        <span className="flex flex-col leading-none">
          <span className={`${lg ? 'text-4xl' : 'text-xl'} font-black tracking-[0.18em] bg-linear-to-r from-cyan-200 via-indigo-300 to-fuchsia-300 bg-clip-text text-transparent`}>
            ADAN
          </span>
          <span className={`${lg ? 'text-xs mt-1.5' : 'text-[9px] mt-1'} font-semibold tracking-[0.32em] text-adan-muted`}>BY PARADIXE</span>
        </span>
      )}
    </span>
  )
}
