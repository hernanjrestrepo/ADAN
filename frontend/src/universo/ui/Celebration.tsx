import { useMemo } from 'react'
import { useUniverso, levelOf } from '../store'

const COLORS = ['#67e8f9', '#a78bfa', '#f0abfc', '#4ade80', '#fbbf24', '#fb923c']

// Celebración proporcional al logro (AD-FUNC-04): solo al cerrar un Nivel con tu aprobación
export default function Celebration() {
  const n = useUniverso((s) => s.celebration)
  const close = useUniverso((s) => s.closeCelebration)
  const pieces = useMemo(() => Array.from({ length: 70 }, (_, i) => ({
    left: (i * 37) % 100, delay: ((i * 13) % 20) / 10, duration: 2.6 + ((i * 7) % 15) / 10, color: COLORS[i % COLORS.length],
  })), [])
  if (n === null) return null
  const level = levelOf(n)
  const last = n === 7
  const next = last ? null : levelOf(n + 1)

  return (
    <div className="u-no-print fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 overflow-hidden" role="dialog" aria-modal="true"
      aria-label={`Nivel ${n} completado`}>
      {pieces.map((p, i) => (
        <span key={i} className="u-confetti" style={{ left: `${p.left}%`, background: p.color, animationDelay: `${p.delay}s`, animationDuration: `${p.duration}s` }} />
      ))}
      <div className="u-glass u-rise relative w-full max-w-md rounded-3xl p-8 text-center">
        <div className="mx-auto flex h-28 w-28 items-center justify-center rounded-full text-6xl shadow-[0_0_80px_rgba(103,232,249,0.5)] bg-[radial-gradient(circle,rgba(103,232,249,0.25),transparent_70%)]">
          {level.badge.icon}
        </div>
        <p className="mt-5 text-[11px] font-semibold tracking-[0.35em] text-emerald-300">NIVEL {n} COMPLETADO</p>
        <h2 className="mt-1 text-3xl font-bold u-glow-text">{level.badge.name}</h2>
        <p className="mt-2 text-slate-300">{level.badge.meaning}</p>
        <div className="mt-5 grid grid-cols-2 gap-3 text-sm">
          <div className="rounded-2xl bg-white/5 p-3"><p className="text-slate-400 text-xs">Entregable</p><p className="font-semibold">{level.entregable}</p></div>
          <div className="rounded-2xl bg-white/5 p-3"><p className="text-slate-400 text-xs">Gemelo Digital</p><p className="font-semibold">Piso {n} de 7 encendido</p></div>
        </div>
        <button type="button" onClick={close} autoFocus
          className="mt-6 w-full rounded-2xl u-cta px-5 py-3 font-bold">
          {last ? 'ADAN te acompaña en modo continuo ♾️' : `Continuar al Nivel ${n + 1}: ${next?.name} →`}
        </button>
      </div>
    </div>
  )
}
