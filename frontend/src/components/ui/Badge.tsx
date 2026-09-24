import type { ReactNode } from 'react'

export type Tone = 'green' | 'yellow' | 'red' | 'blue' | 'gray'

const TONES: Record<Tone, string> = {
  green: 'bg-green-500/20 text-green-400',
  yellow: 'bg-yellow-500/20 text-yellow-400',
  red: 'bg-red-500/20 text-red-400',
  blue: 'bg-blue-500/20 text-blue-400',
  gray: 'bg-gray-500/20 text-gray-400',
}

export default function Badge({ tone = 'gray', children }: { tone?: Tone; children: ReactNode }) {
  return <span className={`text-xs px-2 py-1 rounded ${TONES[tone]}`}>{children}</span>
}
