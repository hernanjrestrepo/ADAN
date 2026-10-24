import { AGENT_BY_ID, type AgentId } from '../data'

export default function Avatar({ id, size = 36, ring = false }: { id: AgentId; size?: number; ring?: boolean }) {
  const a = AGENT_BY_ID[id]
  return (
    <span aria-hidden="true" className="relative inline-flex shrink-0 items-center justify-center rounded-full font-bold"
      style={{ width: size, height: size, fontSize: size * 0.38, color: '#04060f',
        background: `radial-gradient(circle at 35% 30%, #fff 0%, ${a.color} 55%, ${a.color}88 100%)`,
        boxShadow: ring ? `0 0 0 2px #04060f, 0 0 0 4px ${a.color}, 0 0 22px ${a.color}` : `0 0 14px ${a.color}66` }}>
      {a.name.slice(0, 1)}
    </span>
  )
}
