import { useUniverso } from '../store'

// Bitácora en vivo de lo que pasa en la oficina
export default function Feed() {
  const feed = useUniverso((s) => s.feed)
  const panel = useUniverso((s) => s.panel)
  if (feed.length === 0) return null
  return (
    <ol aria-label="Actividad de la oficina" aria-live="polite"
      className={`u-no-print pointer-events-none fixed z-10 hidden lg:flex flex-col-reverse gap-1.5 bottom-3 w-[380px] ${panel === 'mision' ? 'right-3' : 'left-[450px]'}`}>
      {feed.slice(0, 5).map((f, i) => (
        <li key={f.id} className="u-glass u-rise rounded-xl px-3 py-2 text-xs" style={{ opacity: 1 - i * 0.17, borderLeft: `3px solid ${f.color}` }}>
          {f.text}
        </li>
      ))}
    </ol>
  )
}
