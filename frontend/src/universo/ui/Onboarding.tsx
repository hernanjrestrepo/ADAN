import { useState } from 'react'
import { Link } from 'react-router'
import { useAuth } from '../../auth/context'
import { AdanMark } from '../../components/Logo'
import { ARCHETYPES } from '../data'
import { useUniverso } from '../store'

// Entrada al Universo: crear o reinventar, y cualquier tipo de empresa (no solo startups)
export default function Onboarding() {
  const start = useUniverso((s) => s.start)
  const { user } = useAuth()
  const [mode, setMode] = useState<'crear' | 'reinventar'>('crear')
  const [type, setType] = useState('panaderia')
  const [name, setName] = useState('')
  const chosen = ARCHETYPES.find((a) => a.id === type)

  return (
    <div className="fixed inset-0 z-30 flex items-center justify-center p-4 lg:pr-[440px] bg-[radial-gradient(ellipse_at_center,rgba(4,6,15,0.35),rgba(4,6,15,0.92))]">
      <div className="u-glass u-rise w-full max-w-3xl rounded-3xl p-6 sm:p-9 max-h-[94vh] overflow-y-auto u-scroll">
        <div className="flex flex-wrap items-center gap-4">
          <AdanMark size={64} className="drop-shadow-[0_0_18px_rgba(124,155,255,0.55)]" />
          <div className="leading-none">
            <p className="u-brand text-4xl sm:text-5xl">ADAN</p>
            <p className="mt-1.5 text-[11px] font-semibold tracking-[0.35em] text-slate-400">BY PARADIXE · UNIVERSO</p>
          </div>
        </div>
        <h1 className="mt-5 text-3xl sm:text-4xl font-bold leading-tight">
          Hola, soy ADAN. <span className="u-glow-text">Mi equipo y yo te esperamos en la oficina.</span>
        </h1>
        <p className="mt-3 text-slate-300 max-w-2xl">
          Soy el CEO de tu equipo directivo de IA. Te acompaño en siete Niveles, del dolor del cliente al escalamiento, con un
          Board que vota con evidencia. Para cualquier empresa: una panadería, una clínica, una fábrica o una app.
          <b className="text-white"> A la derecha te explico el proceso paso a paso</b>.
        </p>
        <div className="mt-4 rounded-2xl border border-cyan-300/30 bg-cyan-400/5 p-3 text-sm">
          {user ? (
            <p>Entraste como <b>{user.name}</b>. Conversa conmigo en el chat para trabajar con tu empresa real, o recorre aquí la oficina con un ejemplo.</p>
          ) : (
            <p>
              <b>¿Tienes usuario?</b> Para trabajar con tu empresa real necesitas una cuenta gratuita:{' '}
              <Link to="/register?next=/universo" className="font-semibold text-cyan-200 underline">créala aquí</Link> o{' '}
              <Link to="/login?next=/universo" className="font-semibold text-cyan-200 underline">entra si ya la tienes</Link>.
              Sin cuenta puedes recorrer la oficina con una empresa de ejemplo.
            </p>
          )}
        </div>

        <fieldset className="mt-7">
          <legend className="text-sm font-semibold text-slate-200">¿Qué quieres hacer?</legend>
          <div className="mt-2 grid grid-cols-2 gap-3">
            {([['crear', '✨', 'Crear una empresa', 'Desde la idea'], ['reinventar', '🔄', 'Reinventar una empresa', 'Ya existe y quiere cambiar']] as const)
              .map(([id, icon, title, sub]) => (
                <button key={id} type="button" onClick={() => setMode(id)} aria-pressed={mode === id}
                  className={`rounded-2xl border p-4 text-left transition ${mode === id ? 'border-cyan-300 bg-cyan-400/10 shadow-[0_0_30px_rgba(103,232,249,0.2)]' : 'border-white/10 hover:border-white/25'}`}>
                  <span className="text-2xl" aria-hidden="true">{icon}</span>
                  <p className="mt-1 font-semibold">{title}</p>
                  <p className="text-xs text-slate-400">{sub}</p>
                </button>
              ))}
          </div>
        </fieldset>

        <fieldset className="mt-6">
          <legend className="text-sm font-semibold text-slate-200">¿Qué tipo de empresa? <span className="font-normal text-slate-400">(ejemplo para el recorrido)</span></legend>
          <div className="mt-2 grid grid-cols-2 sm:grid-cols-3 gap-3">
            {ARCHETYPES.map((a) => (
              <button key={a.id} type="button" onClick={() => setType(a.id)} aria-pressed={type === a.id}
                className={`rounded-2xl border p-3 text-left transition ${type === a.id ? 'border-violet-300 bg-violet-400/10 shadow-[0_0_30px_rgba(167,139,250,0.25)]' : 'border-white/10 hover:border-white/25'}`}>
                <span className="text-2xl" aria-hidden="true">{a.icon}</span>
                <p className="mt-1 text-sm font-semibold">{a.label}</p>
                <p className="text-[11px] text-slate-400">{a.sector}</p>
              </button>
            ))}
          </div>
        </fieldset>

        <label className="mt-6 block">
          <span className="text-sm font-semibold text-slate-200">Nombre de la empresa</span>
          <input value={name} onChange={(e) => setName(e.target.value)} maxLength={40} placeholder={chosen?.example}
            className="mt-2 w-full rounded-xl border border-white/10 bg-black/30 px-4 py-3 outline-none focus:border-cyan-300" />
        </label>

        <div className="mt-7 flex flex-wrap items-center gap-4">
          <button type="button" onClick={() => start(type, name, mode)}
            className="u-pulse rounded-2xl u-cta px-7 py-3.5 font-bold">
            Recorrer la oficina →
          </button>
          <p className="text-xs text-slate-400 max-w-sm">
            Este recorrido usa datos de ejemplo para que veas cómo trabajamos. Con tu empresa real, todo sale de tu evidencia.
          </p>
        </div>
      </div>
    </div>
  )
}
