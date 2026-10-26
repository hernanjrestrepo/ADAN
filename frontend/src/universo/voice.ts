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

function audio(): AudioContext | null {
  if (typeof window === 'undefined') return null
  const AC = window.AudioContext ?? (window as unknown as { webkitAudioContext?: typeof AudioContext }).webkitAudioContext
  if (!AC) return null
  ctx = ctx ?? new AC()
  if (ctx.state === 'suspended') void ctx.resume()
  return ctx
}

// El navegador solo deja sonar audio después de un gesto de la persona: el primer clic o tecla lo desbloquea, y
// desde ahí las voces suenan aunque lleguen después (cuando responde el equipo)
if (typeof window !== 'undefined') {
  const unlock = () => {
    const c = audio()
    if (c) {
      const buf = c.createBuffer(1, 1, 22050)
      const src = c.createBufferSource()
      src.buffer = buf
      src.connect(c.destination)
      src.start(0)
    }
    if (c && c.state === 'running') {
      window.removeEventListener('pointerdown', unlock)
      window.removeEventListener('keydown', unlock)
    }
  }
  window.addEventListener('pointerdown', unlock)
  window.addEventListener('keydown', unlock)
}

function blip(c: AudioContext, t: number, freq: number, dur: number, vol: number, type: OscillatorType = 'square') {
  const osc = c.createOscillator()
  const gain = c.createGain()
  osc.type = type
  osc.frequency.setValueAtTime(freq, t)
  gain.gain.setValueAtTime(0, t)
  gain.gain.linearRampToValueAtTime(vol, t + 0.01)
  gain.gain.exponentialRampToValueAtTime(0.0005, t + dur)
  osc.connect(gain).connect(c.destination)
  osc.start(t)
  osc.stop(t + dur + 0.01)
  return osc
}

// Risa robótica: «ja-ja-ja» agudo y rápido
export function laugh(agent: string): void {
  const c = voiceOn() ? audio() : null
  if (!c) return
  const base = pitchOf(agent) * 1.4
  let t = c.currentTime + 0.02
  for (let i = 0; i < 5; i++) {
    blip(c, t, base * (1.1 - i * 0.06), 0.07, 0.03)
    t += 0.11
  }
}

// Grito de susto: un «¡ay!» que sube y baja
export function yelp(agent: string): void {
  const c = voiceOn() ? audio() : null
  if (!c) return
  const t = c.currentTime + 0.01
  const osc = blip(c, t, pitchOf(agent) * 1.6, 0.35, 0.05, 'sawtooth')
  osc.frequency.linearRampToValueAtTime(pitchOf(agent) * 2.6, t + 0.08)
  osc.frequency.linearRampToValueAtTime(pitchOf(agent) * 0.9, t + 0.33)
}

export function babble(agent: string, text: string): void {
  if (!voiceOn()) return
  const c = audio()
  if (!c) return
  const base = pitchOf(agent)
  const syllables = Math.min(28, Math.max(4, Math.round(text.length / 6)))
  let t = Math.max(c.currentTime, busyUntil) + 0.02
  for (let i = 0; i < syllables; i++) {
    const osc = c.createOscillator()
    const gain = c.createGain()
    osc.type = 'square'
    osc.frequency.value = base * (0.85 + ((i * 7919) % 30) / 100)
    gain.gain.setValueAtTime(0, t)
    gain.gain.linearRampToValueAtTime(0.035, t + 0.01)
    gain.gain.exponentialRampToValueAtTime(0.0005, t + 0.07)
    osc.connect(gain).connect(c.destination)
    osc.start(t)
    osc.stop(t + 0.08)
    t += 0.085 + (i % 3 === 2 ? 0.05 : 0)
  }
  busyUntil = t
}
