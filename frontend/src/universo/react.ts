import { lastChart } from '../lib/chart'
import type { Message } from '../types'
import { AGENT_BY_ID, INVESTORS, type AgentId } from './data'
import { useUniverso } from './store'
import { talk, type Emotion } from './voice'

// El equipo de la oficina reacciona a lo que se habla: quien responde, su emoción y una frase corta
const AGENT_IDS = new Set(['ceo', 'cto', 'cfo', 'cmo', 'legal', 'producto', 'operaciones', 'csi', 'eva', 'investigador', 'analista'])
type Mood = 'feliz' | 'riendo' | 'preocupado' | 'estresado' | 'celebrando' | 'pensando' | 'hablando'
const MOODS = new Set<Mood>(['feliz', 'riendo', 'preocupado', 'estresado', 'celebrando', 'pensando', 'hablando'])

function plain(text: string) {
  return text.replace(/```[\s\S]*?```/g, '').replace(/\[([^\]]+)\]\([^)]+\)/g, '$1').replace(/https?:\/\/\S+/g, '')
    .replace(/[*_#>|`]/g, '').replace(/\s+/g, ' ').trim()
}

// Lo que cabe en la burbuja sobre la cabeza: la primera frase completa
function snippet(text: string) {
  const p = plain(text)
  const first = p.match(/^.{20,140}?[.!?](\s|$)/)?.[0]?.trim()
  return first ?? (p.length > 140 ? `${p.slice(0, p.lastIndexOf(' ', 137))}…` : p)
}

export function reactTo(message: Message, force = false) {
  const u = useUniverso.getState()
  const speaker = String(message.metadata_json?.agente ?? (force ? 'ceo' : ''))
  if (speaker && (AGENT_IDS.has(speaker) || speaker.startsWith('inv-'))) {
    u.say(speaker, snippet(message.content), 7000)
    const mood = message.metadata_json?.reaccion?.emocion
    u.feel(speaker, mood === 'riendo' || mood === 'preocupado' || mood === 'pensando' || mood === 'feliz' ? mood : 'hablando', 6000)
    // Voz robótica y subtítulos: lo esencial de lo que dice, mientras la transcripción completa queda en el chat
    const inv = INVESTORS.find((i) => `inv-${i.id}` === speaker)
    const agent = AGENT_BY_ID[speaker as AgentId]
    // Subtítulos completos (frase por frase) y voz; quien habla pasa al frente mientras dura
    const said = plain(message.content).slice(0, 900)
    const emotion = message.metadata_json?.reaccion?.agente === speaker ? message.metadata_json?.reaccion?.emocion : undefined
    talk(speaker, said.slice(0, 320), (emotion as Emotion | undefined) ?? 'hablando')
    u.caption(message.agent_name ?? agent?.name ?? inv?.name ?? 'ADÁN', said, inv?.color ?? agent?.color ?? '#60a5fa')
    if ((force || message.metadata_json?.escena === 'oficina') && AGENT_IDS.has(speaker)) {
      if (force) useUniverso.setState({ board: null, arena: null, focusZone: null })
      u.present(speaker, Math.min(26000, Math.max(7000, said.length * 60)))
    }
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
