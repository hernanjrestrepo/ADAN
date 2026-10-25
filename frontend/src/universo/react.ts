import { lastChart } from '../lib/chart'
import type { Message } from '../types'
import { useUniverso } from './store'

// El equipo de la oficina reacciona a lo que se habla: quien responde, su emoción y una frase corta
const AGENT_IDS = new Set(['ceo', 'cto', 'cfo', 'cmo', 'legal', 'producto', 'operaciones', 'csi', 'eva', 'investigador', 'analista'])
type Mood = 'feliz' | 'riendo' | 'preocupado' | 'estresado' | 'celebrando' | 'pensando' | 'hablando'
const MOODS = new Set<Mood>(['feliz', 'riendo', 'preocupado', 'estresado', 'celebrando', 'pensando', 'hablando'])

export function reactTo(message: Message) {
  const u = useUniverso.getState()
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
  u.feel('ceo', 'hablando', 3000)
}
