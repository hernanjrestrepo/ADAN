// La voz de los personajes: un balbuceo robótico corto (como en los videojuegos) mientras aparecen sus subtítulos.
// Cada personaje tiene su tono. Se puede silenciar; la preferencia queda en este navegador.

const KEY = 'adan-voz'
let ctx: AudioContext | null = null
let busyUntil = 0

export function voiceOn(): boolean {
  try {
    return localStorage.getItem(KEY) !== 'off'
  } catch {
    return true
  }
}

export function setVoiceOn(on: boolean): void {
  try {
    localStorage.setItem(KEY, on ? 'on' : 'off')
  } catch {
    // sin almacenamiento: solo dura esta visita
  }
}

function pitchOf(agent: string): number {
  let h = 0
  for (const ch of agent) h = (h * 31 + ch.charCodeAt(0)) % 997
  return 170 + (h % 9) * 28  // entre 170 y 394 Hz
}

export function babble(agent: string, text: string): void {
  if (!voiceOn() || typeof window === 'undefined') return
  const AC = window.AudioContext ?? (window as unknown as { webkitAudioContext?: typeof AudioContext }).webkitAudioContext
  if (!AC) return
  ctx = ctx ?? new AC()
  if (ctx.state === 'suspended') void ctx.resume()
  const base = pitchOf(agent)
  const syllables = Math.min(28, Math.max(4, Math.round(text.length / 6)))
  let t = Math.max(ctx.currentTime, busyUntil) + 0.02
  for (let i = 0; i < syllables; i++) {
    const osc = ctx.createOscillator()
    const gain = ctx.createGain()
    osc.type = 'square'
    osc.frequency.value = base * (0.85 + ((i * 7919) % 30) / 100)
    gain.gain.setValueAtTime(0, t)
    gain.gain.linearRampToValueAtTime(0.035, t + 0.01)
    gain.gain.exponentialRampToValueAtTime(0.0005, t + 0.07)
    osc.connect(gain).connect(ctx.destination)
    osc.start(t)
    osc.stop(t + 0.08)
    t += 0.085 + (i % 3 === 2 ? 0.05 : 0)
  }
  busyUntil = t
}
