import { AGENTS, ZONES, type AgentId, type ZoneId } from '../data'

// Geometría de la oficina (metros, plano XZ). La Sala de Juntas es un cilindro de vidrio con una puerta al frente.
export const BOARD_CENTER: [number, number] = ZONES.board.position
export const BOARD_RADIUS = 4.6
export const TABLE_RADIUS = 2.1
export const SEAT_RADIUS = 2.85
const DOOR_Z_OUT = BOARD_CENTER[1] + BOARD_RADIUS + 1.2
const DOOR_Z_IN = BOARD_CENTER[1] + BOARD_RADIUS - 1.4

// Siete puestos: la cabecera (CEO) al fondo, mirando a la cámara; los demás en arco.
export function seatPosition(seat: number): [number, number] {
  const angle = -Math.PI / 2 + (seat * 2 * Math.PI) / 7
  return [BOARD_CENTER[0] + Math.cos(angle) * SEAT_RADIUS, BOARD_CENTER[1] + Math.sin(angle) * SEAT_RADIUS]
}

export function seatFacing(seat: number): number {
  const [x, z] = seatPosition(seat)
  return Math.atan2(BOARD_CENTER[0] - x, BOARD_CENTER[1] - z)
}

function insideBoard(p: [number, number]): boolean {
  return Math.hypot(p[0] - BOARD_CENTER[0], p[1] - BOARD_CENTER[1]) < BOARD_RADIUS
}

// Ruta con puntos intermedios: nadie atraviesa el vidrio de la Sala de Juntas. `lane` reparte a cada quien
// en un carril distinto de la puerta para que no se amontonen al entrar todos juntos.
export function planPath(from: [number, number], to: [number, number], lane = 0): [number, number][] {
  const a = insideBoard(from)
  const b = insideBoard(to)
  const doorX = BOARD_CENTER[0] + lane * 0.35
  const doorOut: [number, number] = [doorX * 1.6, DOOR_Z_OUT + Math.abs(lane) * 0.25]
  const doorIn: [number, number] = [doorX, DOOR_Z_IN]
  if (a && !b) return [doorIn, doorOut, to]
  if (!a && b) return [doorOut, doorIn, to]
  if (!a && !b && crossesBoard(from, to)) {
    const side = (from[0] + to[0]) / 2 >= BOARD_CENTER[0] ? 1 : -1
    const around: [number, number] = [BOARD_CENTER[0] + side * (BOARD_RADIUS + 1.5), BOARD_CENTER[1]]
    return [around, to]
  }
  return [to]
}

function crossesBoard(p: [number, number], q: [number, number]): boolean {
  const [cx, cz] = BOARD_CENTER
  const dx = q[0] - p[0]
  const dz = q[1] - p[1]
  const len2 = dx * dx + dz * dz || 1
  const t = Math.max(0, Math.min(1, ((cx - p[0]) * dx + (cz - p[1]) * dz) / len2))
  return Math.hypot(p[0] + t * dx - cx, p[1] + t * dz - cz) < BOARD_RADIUS + 0.4
}

// Cada agente tiene su lugar en cada zona, para que no se amontonen.
export function zoneSpot(zone: ZoneId, agent: AgentId): [number, number] {
  const [x, z] = ZONES[zone].position
  if (zone === 'board') {
    const seat = AGENTS.find((a) => a.id === agent)?.seat ?? 3
    return seatPosition(seat)
  }
  const i = AGENTS.findIndex((a) => a.id === agent)
  const angle = (i / AGENTS.length) * Math.PI * 2
  const r = zone === 'gemelo' ? 2.9 : 2.2
  return [x + Math.cos(angle) * r, z + Math.sin(angle) * r]
}

// Posición actual de cada agente (la escribe la escena en cada frame; la usa la cámara para seguirlo)
export const livePositions = new Map<AgentId, [number, number]>()

// Punto al frente de la oficina, mirando a la cámara, donde se para quien habla
export const STAGE: [number, number] = [0, 10.4]
