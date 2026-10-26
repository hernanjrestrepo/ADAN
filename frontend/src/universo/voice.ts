// La voz de los personajes, al estilo de R2-D2: pitidos, trinos y silbidos ininteligibles que expresan la emoción
// (alegría que sube, preocupación que cae, duda que burbujea, susto que chilla). Cada personaje tiene su propio
// timbre, su tono y su risa robótica. Se puede silenciar; la preferencia queda en este navegador.

const KEY = 'adan-voz'
let ctx: AudioContext | null = null
let master: AudioNode | null = null
let busyUntil = 0

export type Emotion = 'feliz' | 'riendo' | 'preocupado' | 'estresado' | 'celebrando' | 'pensando' | 'hablando'

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

function hashOf(agent: string): number {
  let h = 0
  for (const ch of agent) h = (h * 31 + ch.charCodeAt(0)) % 9973
  return h
}

// La «personalidad sonora» de cada uno: tono base, timbre y qué tan rápido trina
function persona(agent: string) {
  const h = hashOf(agent)
  const types: OscillatorType[] = ['sine', 'triangle', 'square', 'sine', 'triangle']
  return {
    base: 900 + (h % 11) * 110,             // entre 900 y 2000 Hz: el registro de R2-D2
    type: types[h % types.length] ?? 'sine',
    speed: 0.055 + ((h >> 3) % 5) * 0.012,   // duración de cada nota
    seed: h,
  }
}

// Números pseudoaleatorios repetibles: la misma frase suena parecida, pero cada personaje distinto
function rng(seed: number) {
  let s = seed % 2147483647 || 1
  return () => (s = (s * 16807) % 2147483647) / 2147483647
}

function audio(): AudioContext | null {
  if (typeof window === 'undefined') return null
  const AC = window.AudioContext ?? (window as unknown as { webkitAudioContext?: typeof AudioContext }).webkitAudioContext
  if (!AC) return null
  ctx = ctx ?? new AC()
  if (ctx.state === 'suspended') void ctx.resume()
  if (!master) {
    // Canal maestro: sube el volumen y un compresor evita que sature cuando suenan varios a la vez
    const gain = ctx.createGain()
    gain.gain.value = 1.6
    const comp = ctx.createDynamicsCompressor()
    comp.threshold.value = -14
    comp.ratio.value = 6
    gain.connect(comp).connect(ctx.destination)
    master = gain
  }
  return ctx
}

function out(c: AudioContext): AudioNode {
  return master ?? c.destination
}

// El navegador solo deja sonar audio después de un gesto de la persona: el primer clic o tecla lo desbloquea, y
// desde ahí las voces suenan aunque lleguen después (cuando responde el equipo)
if (typeof window !== 'undefined') {
  const unlock = () => {
    const c = audio()
    if (c) {
      const src = c.createBufferSource()
      src.buffer = c.createBuffer(1, 1, 22050)
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

// Una nota con glissando: de `from` a `to` Hz en `dur` segundos (el «uuii» o el «uuuu» del droide)
function chirp(c: AudioContext, t: number, from: number, to: number, dur: number, vol: number, type: OscillatorType,
               vibrato = 0) {
  const osc = c.createOscillator()
  const gain = c.createGain()
  osc.type = type
  osc.frequency.setValueAtTime(from, t)
  osc.frequency.exponentialRampToValueAtTime(Math.max(60, to), t + dur)
  if (vibrato) {
    const lfo = c.createOscillator()
    const depth = c.createGain()
    lfo.frequency.value = 18 + vibrato * 10
    depth.gain.value = from * 0.06 * vibrato
    lfo.connect(depth).connect(osc.frequency)
    lfo.start(t)
    lfo.stop(t + dur + 0.02)
  }
  gain.gain.setValueAtTime(0, t)
  gain.gain.linearRampToValueAtTime(vol, t + Math.min(0.012, dur / 3))
  gain.gain.setValueAtTime(vol, t + dur * 0.7)
  gain.gain.exponentialRampToValueAtTime(0.0005, t + dur)
  osc.connect(gain).connect(out(c))
  osc.start(t)
  osc.stop(t + dur + 0.02)
}

const VOL = 0.22

// Cómo suena cada emoción: forma de la frase (sube, cae, burbujea…) y ritmo
function phrase(c: AudioContext, agent: string, emotion: Emotion, length: number, start: number): number {
  const p = persona(agent)
  const r = rng(p.seed + length * 7 + emotion.length)
  let t = start
  const notes = Math.max(4, Math.min(16, length))
  for (let i = 0; i < notes; i++) {
    const k = i / Math.max(1, notes - 1)
    let from = p.base * (0.7 + r() * 0.8)
    let to: number
    let dur = p.speed * (0.7 + r() * 0.9)
    let vib = 0
    if (emotion === 'feliz' || emotion === 'celebrando') {
      to = from * (1.3 + r() * 0.5)                 // trinos que suben
      from *= 0.9 + k * 0.4
      if (emotion === 'celebrando' && i % 3 === 2) vib = 1
    } else if (emotion === 'preocupado' || emotion === 'estresado') {
      from = p.base * (1.2 - k * 0.6) * (0.9 + r() * 0.2)
      to = from * 0.6                              // silbidos que caen, lentos
      dur *= 1.8
      if (emotion === 'estresado') vib = 1.5
    } else if (emotion === 'pensando') {
      to = from * (r() > 0.5 ? 1.15 : 0.85)       // burbujeo corto, dudoso
      dur *= 0.6
      vib = 0.5
    } else if (emotion === 'riendo') {
      to = from * 0.8
      dur *= 0.5
    } else {
      to = from * (0.75 + r() * 0.6)               // conversación: notas que van y vienen
    }
    chirp(c, t, from, to, dur, VOL * (0.7 + r() * 0.3), p.type, vib)
    t += dur + (r() < 0.25 ? 0.07 : 0.015)
  }
  // Remate de la frase: pregunta (sube) o afirmación (baja), como R2-D2
  if (emotion === 'feliz' || emotion === 'celebrando') chirp(c, t, p.base, p.base * 2.2, 0.18, VOL, 'sine', 0.6)
  else if (emotion === 'preocupado') chirp(c, t, p.base * 1.1, p.base * 0.45, 0.35, VOL * 0.8, 'sine')
  return t + 0.2
}

// Lo que «dice» un personaje: una frase de pitidos con su emoción, de duración parecida al mensaje
export function talk(agent: string, text: string, emotion: Emotion = 'hablando'): void {
  if (!voiceOn() || !text.trim()) return
  const c = audio()
  if (!c) return
  // Si hay frases en cola no se acumulan más de 1,5 s de espera
  const start = Math.max(c.currentTime + 0.03, Math.min(busyUntil, c.currentTime + 1.5))
  busyUntil = phrase(c, agent, emotion, Math.round(text.length / 18), start)
}

// La risa de cada uno: trinos rápidos con su propio ritmo y tono (nadie se ríe igual)
export function laugh(agent: string): void {
  const c = voiceOn() ? audio() : null
  if (!c) return
  const p = persona(agent)
  const r = rng(p.seed * 3)
  const beats = 5 + (p.seed % 4)
  const gap = 0.07 + (p.seed % 5) * 0.015
  let t = c.currentTime + 0.02
  for (let i = 0; i < beats; i++) {
    const f = p.base * 1.3 * (1 - i * (0.04 + (p.seed % 3) * 0.02)) * (0.95 + r() * 0.1)
    chirp(c, t, f, f * 0.7, gap * 0.8, VOL, p.seed % 2 ? 'square' : 'triangle', 0.4)
    t += gap
  }
  chirp(c, t, p.base * 0.9, p.base * 1.6, 0.14, VOL * 0.8, 'sine')  // el «¡uii!» final
}

// Susto: un chillido que sube muy alto y cae temblando
export function yelp(agent: string): void {
  const c = voiceOn() ? audio() : null
  if (!c) return
  const p = persona(agent)
  const t = c.currentTime + 0.01
  chirp(c, t, p.base * 0.8, p.base * 3.2, 0.12, VOL * 1.2, 'sawtooth')
  chirp(c, t + 0.12, p.base * 3, p.base * 0.5, 0.45, VOL, 'sine', 2)
}

// Compatibilidad: el balbuceo de antes ahora es una frase de pitidos
export function babble(agent: string, text: string): void {
  talk(agent, text)
}

export function hush(): void {
  busyUntil = 0
}
