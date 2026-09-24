import type { Vote } from '../types'
import Badge, { type Tone } from './ui/Badge'

const VOTE_LABELS: Record<Vote, { text: string; tone: Tone }> = {
  PROCEED: { text: 'Avanzar', tone: 'green' },
  PIVOT: { text: 'Pivotar', tone: 'yellow' },
  STOP: { text: 'Detener', tone: 'red' },
  ABSTAIN: { text: 'Abstención', tone: 'gray' },
  NO_CONSENSUS: { text: 'Sin consenso', tone: 'gray' },
}

export default function VoteBadge({ vote }: { vote: Vote | string }) {
  const label = VOTE_LABELS[vote as Vote] ?? { text: vote, tone: 'gray' as Tone }
  return <Badge tone={label.tone}>{label.text}</Badge>
}
