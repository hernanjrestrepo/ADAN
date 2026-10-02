import { useRef, type KeyboardEvent } from 'react'

interface Tab<T extends string> {
  id: T
  label: string
}

interface TabsProps<T extends string> {
  tabs: Tab<T>[]
  active: T
  onChange: (id: T) => void
}

// Pestañas accesibles: flechas, Inicio y Fin mueven el foco (patrón WAI-ARIA); en móvil se desplazan
export default function Tabs<T extends string>({ tabs, active, onChange }: TabsProps<T>) {
  const refs = useRef<(HTMLButtonElement | null)[]>([])

  const onKeyDown = (e: KeyboardEvent, index: number) => {
    const last = tabs.length - 1
    const moves: Record<string, number> = { ArrowRight: index === last ? 0 : index + 1,
      ArrowLeft: index === 0 ? last : index - 1, Home: 0, End: last }
    const next = moves[e.key]
    const target = next === undefined ? undefined : tabs[next]
    if (next === undefined || !target) return
    e.preventDefault()
    onChange(target.id)
    refs.current[next]?.focus()
  }

  return (
    <div role="tablist" className="flex gap-1 overflow-x-auto -mb-px">
      {tabs.map((tab, i) => (
        <button
          key={tab.id}
          ref={(el) => { refs.current[i] = el }}
          type="button"
          role="tab"
          aria-selected={active === tab.id}
          tabIndex={active === tab.id ? 0 : -1}
          onClick={() => onChange(tab.id)}
          onKeyDown={(e) => onKeyDown(e, i)}
          className={`whitespace-nowrap px-4 py-3 text-sm font-medium border-b-2 ${
            active === tab.id
              ? 'border-adan-accent text-adan-text'
              : 'border-transparent text-adan-muted hover:text-adan-text hover:border-adan-border'
          }`}
        >
          {tab.label}
        </button>
      ))}
    </div>
  )
}
