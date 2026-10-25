import { AGENT_BY_ID, INVESTORS, type AgentId, type Look } from '../universo/data'

// Retrato del personaje tal como se ve en la oficina: piel, pelo, barba, bigote, gafas y el color de su rol
export default function Portrait({ agent, size = 36 }: { agent: string; size?: number }) {
  const inv = agent.startsWith('inv-') ? INVESTORS.find((i) => `inv-${i.id}` === agent) : undefined
  const a = AGENT_BY_ID[agent as AgentId] ?? AGENT_BY_ID.ceo
  const look: Look = inv?.look ?? a.look
  const color = inv?.color ?? a.color
  const name = inv?.name ?? a.name
  const hair = look.hair
  return (
    <svg viewBox="0 0 40 40" width={size} height={size} role="img" aria-label={name} className="shrink-0 rounded-full shadow">
      <circle cx="20" cy="20" r="20" fill={color} opacity="0.35" />
      <path d="M8 40 Q20 27 32 40 Z" fill={color} />
      {hair === 'largo' && <rect x="10" y="12" width="20" height="20" rx="9" fill={look.hairColor} />}
      <circle cx="20" cy="18" r="9" fill={look.skin} />
      {hair !== 'calvo' && <path d="M11 17 Q11 8 20 8 Q29 8 29 17 Q24 12 20 13 Q15 12 11 17 Z" fill={look.hairColor} />}
      {hair === 'mono' && <circle cx="20" cy="7" r="3.2" fill={look.hairColor} />}
      {hair === 'rizado' && [12, 16, 20, 24, 28].map((x) => <circle key={x} cx={x} cy={10} r="2.6" fill={look.hairColor} />)}
      <circle cx="16.8" cy="18" r="1.1" fill="#1f1611" />
      <circle cx="23.2" cy="18" r="1.1" fill="#1f1611" />
      {look.glasses && (
        <g fill="none" stroke={color} strokeWidth="1">
          <circle cx="16.8" cy="18" r="2.6" /><circle cx="23.2" cy="18" r="2.6" /><path d="M19.4 18 H20.6" />
        </g>
      )}
      {look.beard && <path d="M12.5 20 Q20 31 27.5 20 Q24 25 20 25 Q16 25 12.5 20 Z" fill={look.hairColor} />}
      {look.mustache && <path d="M16.5 22 Q20 20.5 23.5 22" stroke={look.hairColor} strokeWidth="1.6" fill="none" strokeLinecap="round" />}
      <path d="M17.5 23 Q20 24.8 22.5 23" stroke="#7f1d1d" strokeWidth="0.9" fill="none" strokeLinecap="round" />
    </svg>
  )
}
