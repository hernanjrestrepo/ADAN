import { lastChart } from '../lib/chart'
import type { Message } from '../types'
import { AGENT_BY_ID, INVESTORS, type AgentId } from './data'
import { useUniverso } from './store'
import { babble } from './voice'

// El equipo de la oficina reacciona a lo que se habla: quien responde, su emoción y una frase corta
const AGENT_IDS = new Set(['ceo', 'cto', 'cfo', 'cmo', 'legal', 'producto', 'operaciones', 'csi', 'eva', 'investigador', 'analista'])
type Mood = 'feliz' | 'riendo' | 'preocupado' | 'estresado' | 'celebrando' | 'pensando' | 'hablando'
const MOODS = new Set<Mood>(['feliz', 'riendo', 'preocupado', 'estresado', 'celebrando', 'pensando', 'hablando'])

function snippet(text: string) {
  const plain = text.replace(/```[\s\S]*?```/g, '').replace(/[*_#>|`]/g, '').replace(/\s+/g, ' ').trim()
  return plain.length > 110 ? `${plain.slice(0, 107)}…` : plain
}

export function reactTo(message: Message) {
  const u = useUniverso.getState()
  const speaker = String(message.metadata_json?.agente ?? '')
  if (speaker && (AGENT_IDS.has(speaker) || speaker.startsWith('inv-'))) {
    u.say(speaker, snippet(message.content), 7000)
    const mood = message.metadata_json?.reaccion?.emocion
    u.feel(speaker, mood === 'riendo' || mood === 'preocupado' || mood === 'pensando' || mood === 'feliz' ? mood : 'hablando', 6000)
    // Voz robótica y subtítulos: lo esencial de lo que dice, mientras la transcripción completa queda en el chat
    const inv = INVESTORS.find((i) => `inv-${i.id}` === speaker)
    const agent = AGENT_BY_ID[speaker as AgentId]
    babble(speaker, snippet(message.content))
    u.caption(message.agent_name ?? agent?.name ?? inv?.name ?? 'ADÁN', snippet(message.content), inv?.color ?? agent?.color ?? '#60a5fa', 6500)
    if (message.metadata_json?.escena === 'oficina' && AGENT_IDS.has(speaker)) u.select(speaker as never)
  }
  const r = message.metadata_json?.reaccion
  const chart = lastChart(message.content)
  if (chart) u.showHolo(chart)
  if (message.metadata_json?.investigado) {
    u.say('csi', '🔎 Investigué en internet: ' + message.metadata_json.investigado.consulta.slice(0, 60), 5000, 'info')
    u.feel('csi', 'feliz', 4000)
  }
  if (r && AGENT_IDS.has(r.agente)) {
    const mood = MOODS.has(r.emocion as Mood) ? (r.emocion as Mood) : 'hablando'
    u.feel(r.agente, mood, 5000)
    if (r.frase) u.say(r.agente, r.frase, 5000)
  }
  if (!speaker) u.feel('ceo', 'hablando', 3000)
}
