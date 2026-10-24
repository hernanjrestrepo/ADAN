import { type Group, type Mesh } from 'three'
import { type Mood } from '../store'

// Esqueleto animable de cada personaje (lo dibuja Person.tsx) y su postura según lo que hace y lo que siente

export interface Rig {
  body: Group | null
  head: Group | null
  legL: Group | null
  legR: Group | null
  armL: Group | null
  armR: Group | null
  browL: Mesh | null
  browR: Mesh | null
  smile: Mesh | null
  frown: Mesh | null
  laugh: Mesh | null
}

export const MOOD_EMOJI: Record<Mood, string> = {
  feliz: '🙂', riendo: '😂', preocupado: '😟', estresado: '😫', celebrando: '🎉', pensando: '🤔', hablando: '💬',
}

interface Pose { clock: number; moving: boolean; walk: number; sit: number; working: boolean; mood?: Mood }

// Postura de cada cuadro: caminar, sentarse, teclear y, encima, la emoción del momento
export function poseRig(r: Rig, p: Pose): void {
  const { clock, moving, walk, sit, working, mood } = p
  const swing = moving ? Math.sin(walk) * 0.6 : 0
  let bob = moving ? Math.abs(Math.sin(walk)) * 0.05 : Math.sin(clock * 1.6) * 0.012
  let ax = { l: -swing * 0.8 - 0.3 * sit, r: swing * 0.8 - 0.3 * sit }
  let az = { l: 0, r: 0 }
  let headX = 0
  let headZ = 0
  if (working) {
    const typing = Math.sin(clock * 14) * 0.12
    ax = { l: -1.1 + typing, r: -1.1 - typing }
  }
  if (mood && !moving) {
    if (mood === 'celebrando') {
      // Brazos arriba, saltando
      const wave = Math.sin(clock * 9) * 0.25
      az = { l: -2.7 + wave, r: 2.7 - wave }
      ax = { l: 0, r: 0 }
      bob += Math.abs(Math.sin(clock * 7)) * 0.12
    } else if (mood === 'estresado') {
      // Manos a la cabeza
      az = { l: 2.45, r: -2.45 }
      ax = { l: -0.35, r: -0.35 }
      headZ = Math.sin(clock * 11) * 0.08
    } else if (mood === 'riendo') {
      ax = { l: -0.7, r: -0.7 }
      az = { l: 0.35, r: -0.35 }
      headX = -0.22
      bob += Math.abs(Math.sin(clock * 16)) * 0.03
    } else if (mood === 'preocupado' || mood === 'pensando') {
      // Mano al mentón
      ax = { l: -0.2, r: -2.1 }
      az = { l: 0, r: -0.55 }
      headX = mood === 'preocupado' ? 0.18 : 0
      headZ = mood === 'pensando' ? 0.14 : 0
    } else if (mood === 'hablando') {
      ax = { l: -0.3, r: -1.0 + Math.sin(clock * 5) * 0.35 }
      az = { l: 0, r: -0.2 + Math.sin(clock * 3.3) * 0.15 }
      headZ = Math.sin(clock * 2.4) * 0.05
    } else if (mood === 'feliz') {
      headZ = Math.sin(clock * 3) * 0.06
    }
  }
  if (r.body) r.body.position.y = -0.42 * sit + bob
  if (r.legL) r.legL.rotation.x = swing * (1 - sit) - 1.45 * sit
  if (r.legR) r.legR.rotation.x = -swing * (1 - sit) - 1.45 * sit
  if (r.armL) r.armL.rotation.set(ax.l, 0, az.l)
  if (r.armR) r.armR.rotation.set(ax.r, 0, az.r)
  if (r.head) r.head.rotation.set(headX, 0, headZ)
  // Cara: cejas y boca según la emoción
  const worried = mood === 'preocupado' || mood === 'estresado'
  const brow = worried ? 0.4 : mood === 'pensando' ? 0.15 : 0
  const lift = mood === 'feliz' || mood === 'celebrando' || mood === 'riendo' ? 0.012 : 0
  if (r.browL) { r.browL.rotation.z = brow; r.browL.position.y = 0.085 + lift }
  if (r.browR) { r.browR.rotation.z = -brow; r.browR.position.y = 0.085 + lift }
  if (r.smile) {
    r.smile.visible = !worried
    r.smile.scale.y = mood === 'feliz' || mood === 'celebrando' || mood === 'hablando' ? 1 : mood === 'pensando' ? 0.25 : 0.6
  }
  if (r.frown) r.frown.visible = worried
  if (r.laugh) {
    r.laugh.visible = mood === 'riendo' || mood === 'celebrando' || (mood === 'hablando' && Math.sin(clock * 18) > 0)
  }
}
