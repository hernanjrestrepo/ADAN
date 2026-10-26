import { Html } from '@react-three/drei'
import { useFrame } from '@react-three/fiber'
import { useRef, useState } from 'react'
import { type Group, type Mesh } from 'three'
import { CAFE_LINES, ZONES, type Agent } from '../data'
import { scold, tellJoke } from '../humor'
import { levelOf, useUniverso } from '../store'
import { STAGE, livePositions, planPath, seatFacing, seatPosition, zoneSpot } from './layout'
import { PersonBody } from './Person'
import { MOOD_EMOJI, poseRig, type Rig } from './rig'

const SPEED = 2.4
const ARENA_TEAM: string[] = ['ceo', 'cfo', 'cmo']

type Vec2 = [number, number]

// Un integrante del equipo de ADÁN: camina por la oficina, trabaja en las zonas y se sienta en el Board.
export default function AgentFigure({ agent }: { agent: Agent }) {
  const root = useRef<Group>(null)
  const rig = useRef<Rig | null>(null)
  const screen = useRef<Mesh>(null)
  const ring = useRef<Mesh>(null)
  const nav = useRef({
    pos: [agent.home[0], agent.home[1]] as Vec2, path: [] as Vec2[], targetKey: '', heading: 0, walk: 0,
    wanderUntil: 0, wanderAt: 6 + ((agent.home[0] * 7 + agent.home[1] * 13 + 140) % 14), wanderTarget: null as Vec2 | null, clock: 0, seated: 0,
    chatted: false,
  })
  const [hover, setHover] = useState(false)
  const selected = useUniverso((s) => s.selected === agent.id)
  const bubble = useUniverso((s) => s.bubbles[agent.id])
  const mood = useUniverso((s) => s.moods[agent.id])
  // Quien habla al frente no necesita burbuja: lo que dice va en los subtítulos
  const onStage = useUniverso((s) => s.stage?.agent === agent.id)
  const floor = useUniverso((s) => s.floor ?? s.level)

  useFrame((_, rawDelta) => {
    const delta = Math.min(rawDelta, 0.05)
    const n = nav.current
    n.clock += delta
    const s = useUniverso.getState()
    const job = s.jobs[agent.id]
    const inBoard = Boolean(s.board) && agent.board && agent.seat !== undefined
    // En La Arena presentan el CEO, la CFO y el CMO
    const arenaSlot = s.arena ? ARENA_TEAM.indexOf(agent.id) : -1
    const now = Date.now()

    // 1. ¿A dónde debe ir?
    let target: Vec2 = agent.home
    let key = 'home'
    if (inBoard && agent.seat !== undefined) {
      target = seatPosition(agent.seat)
      key = 'seat'
    } else if (arenaSlot >= 0) {
      const [ax, az] = ZONES.arena.position
      target = [ax + [0, -1.1, 1.1][arenaSlot]!, az + 1.4 + (arenaSlot === 0 ? 0 : 0.5)]
      key = 'arena'
    } else if (s.stage && s.stage.agent === agent.id && now < s.stage.until) {
      target = STAGE
      key = 'stage'
    } else if (job && job.phase !== 'returning') {
      target = zoneSpot(job.zone, agent.id)
      key = `job:${job.zone}`
    } else if (!job && n.wanderTarget && n.clock < n.wanderUntil) {
      target = n.wanderTarget
      key = `wander:${target[0].toFixed(1)}`
    }
    // Vida en la oficina: quien está libre va a colaborar a una zona activa o a tomarse un café y conversar
    if (!job && !inBoard && arenaSlot < 0) {
      if (n.wanderTarget && n.clock >= n.wanderUntil) {
        n.wanderTarget = null
        n.wanderAt = n.clock + 12 + Math.random() * 18
      } else if (!n.wanderTarget && n.clock >= n.wanderAt) {
        const cafe = agent.id === 'ceo' || Math.random() < 0.45
        const zones = levelOf(s.floor ?? s.level).zones.filter((z) => z !== 'board')
        const zone = cafe ? 'cafeteria' : zones[Math.floor(Math.random() * zones.length)]
        if (zone) {
          n.wanderTarget = zoneSpot(zone, agent.id)
          n.wanderUntil = n.clock + (cafe ? 14 : 9) + Math.random() * 6
          n.chatted = !cafe
        }
      }
    }
    if (key !== n.targetKey) {
      n.targetKey = key
      n.path = planPath(n.pos, target, agent.seat !== undefined ? agent.seat - 3 : 0)
    }

    // 2. Caminar por la ruta
    let moving = false
    const next = n.path[0]
    if (next) {
      const dx = next[0] - n.pos[0]
      const dz = next[1] - n.pos[1]
      const dist = Math.hypot(dx, dz)
      if (dist < 0.06) {
        n.path.shift()
      } else {
        const step = Math.min(dist, SPEED * (key === 'seat' ? 1.5 : key === 'stage' ? 2.6 : 1) * delta)
        n.pos = [n.pos[0] + (dx / dist) * step, n.pos[1] + (dz / dist) * step]
        const want = Math.atan2(dx, dz)
        n.heading += angleDiff(want, n.heading) * Math.min(1, delta * 10)
        moving = true
      }
    }
    const arrived = n.path.length === 0
    // En la cafetería se cuenta algo y se ríe
    if (arrived && !n.chatted && key.startsWith('wander')) {
      n.chatted = true
      const line = CAFE_LINES[Math.floor(Math.random() * CAFE_LINES.length)]
      if (line && !s.bubbles[agent.id]) {
        s.say(agent.id, line, 4200)
        s.feel(agent.id, Math.random() < 0.5 ? 'riendo' : 'hablando', 4200)
      }
    }

    // 3. El trabajo avanza solo cuando el agente llega a la zona
    if (job && arrived && !inBoard) {
      if (job.phase === 'going') s.setPhase(agent.id, 'working', now + 3200)
      else if (job.phase === 'working' && now >= job.until) {
        s.completeTask(agent.id)
        s.setPhase(agent.id, 'returning')
      } else if (job.phase === 'returning') s.setPhase(agent.id, null)
    }
    const working = Boolean(job && job.phase === 'working' && arrived && !inBoard)
    const seatedNow = inBoard && arrived

    if (arrived && seatedNow && agent.seat !== undefined) {
      n.heading += angleDiff(seatFacing(agent.seat), n.heading) * Math.min(1, delta * 6)
    } else if (arrived && key === 'stage') {
      n.heading += angleDiff(0, n.heading) * Math.min(1, delta * 8)
    } else if (arrived && key === 'arena') {
      n.heading += angleDiff(Math.PI, n.heading) * Math.min(1, delta * 6)
    } else if (arrived && key.startsWith('wander')) {
      // Mirarse entre ellos alrededor de la mesa del café o de la zona
      const [cx, cz] = nearestZoneCenter(n.pos)
      n.heading += angleDiff(Math.atan2(cx - n.pos[0], cz - n.pos[1]), n.heading) * Math.min(1, delta * 4)
    } else if (arrived && !moving && !working) {
      const face = Math.atan2(-n.pos[0], 2 - n.pos[1])
      n.heading += angleDiff(face, n.heading) * Math.min(1, delta * 2)
    }
    n.seated += ((seatedNow ? 1 : 0) - n.seated) * Math.min(1, delta * 6)

    // 4. Animación
    n.walk += moving ? delta * 9 : 0
    const sit = n.seated
    // Susto (clic derecho): brinca y tiembla
    const jolt = (s.jolts[agent.id] ?? 0) > now
    if (root.current) {
      root.current.position.set(n.pos[0] + (jolt ? Math.sin(n.clock * 60) * 0.05 : 0),
        jolt ? Math.abs(Math.sin(n.clock * 14)) * 0.45 : 0, n.pos[1])
      root.current.rotation.y = n.heading + (jolt ? Math.sin(n.clock * 45) * 0.25 : 0)
    }
    livePositions.set(agent.id, n.pos)
    if (rig.current) poseRig(rig.current, { clock: n.clock, moving, walk: n.walk, sit, working, mood: s.moods[agent.id] })
    if (screen.current) {
      screen.current.visible = working
      screen.current.rotation.y = Math.sin(n.clock * 2) * 0.05
    }
    if (ring.current) {
      const pulse = selected || hover ? 1.15 + Math.sin(n.clock * 5) * 0.08 : 1
      ring.current.scale.setScalar(pulse)
    }
  })

  const showTag = hover || selected || Boolean(bubble) || Boolean(mood)

  return (
    <group ref={root} scale={1.25}
      onClick={(e) => { e.stopPropagation(); tellJoke(agent.id) }}
      onContextMenu={(e) => { e.stopPropagation(); e.nativeEvent.preventDefault(); scold(agent.id) }}
      onPointerOver={(e) => { e.stopPropagation(); setHover(true); document.body.style.cursor = 'pointer' }}
      onPointerOut={() => { setHover(false); document.body.style.cursor = '' }}>
      <mesh ref={ring} rotation-x={-Math.PI / 2} position-y={0.02}>
        <ringGeometry args={[0.42, 0.55, 40]} />
        <meshBasicMaterial color={agent.color} transparent opacity={selected ? 0.95 : 0.55} toneMapped={false} />
      </mesh>
      <PersonBody rigRef={rig} look={agent.look} color={agent.color} />
      <Outfit floor={floor} color={agent.color} />
      <group>
        <mesh ref={screen} position={[0, 1.25, 0.55]} visible={false}>
          <planeGeometry args={[0.7, 0.42]} />
          <meshBasicMaterial color={agent.color} transparent opacity={0.35} toneMapped={false} side={2} />
        </mesh>
        <Html position={[0, 2.35, 0]} center distanceFactor={10} zIndexRange={[20, 0]} pointerEvents="none">
          {showTag && (
            <div className="flex flex-col items-center gap-1 select-none">
              {bubble && !onStage && (
                <div className={`u-bubble ${bubble.tone ?? ''}`} style={{ borderColor: agent.color }}>{bubble.text}</div>
              )}
              {mood && <div className="u-mood" aria-hidden="true">{MOOD_EMOJI[mood]}</div>}
              <div className="u-tag" style={{ borderColor: agent.color }}>
                <span style={{ color: agent.color }}>●</span> {agent.name} · {agent.role}
              </div>
            </div>
          )}
        </Html>
      </group>
    </group>
  )
}

// Vestuario del piso: boina en el estudio de diseño, casco en el taller, gafas en el laboratorio,
// gorro de fiesta en el lanzamiento y corbata en el piso ejecutivo
function Outfit({ floor, color }: { floor: number; color: string }) {
  if (floor === 2) {
    return (
      <mesh position={[0.04, 2.08, 0]} rotation-z={-0.18}>
        <cylinderGeometry args={[0.2, 0.22, 0.07, 20]} />
        <meshStandardMaterial color="#be123c" />
      </mesh>
    )
  }
  if (floor === 4) {
    return (
      <group position-y={2.0}>
        <mesh><sphereGeometry args={[0.23, 20, 12, 0, Math.PI * 2, 0, Math.PI / 2]} /><meshStandardMaterial color="#facc15" /></mesh>
        <mesh position-y={0.005}><cylinderGeometry args={[0.28, 0.28, 0.025, 24]} /><meshStandardMaterial color="#eab308" /></mesh>
      </group>
    )
  }
  if (floor === 5) {
    return (
      <mesh position={[0, 1.86, 0.17]}>
        <boxGeometry args={[0.34, 0.08, 0.04]} />
        <meshStandardMaterial color="#22d3ee" emissive="#22d3ee" emissiveIntensity={1.2} transparent opacity={0.8} toneMapped={false} />
      </mesh>
    )
  }
  if (floor === 6) {
    return (
      <mesh position-y={2.18} rotation-z={0.15}>
        <coneGeometry args={[0.12, 0.34, 16]} />
        <meshStandardMaterial color={color} emissive={color} emissiveIntensity={0.6} />
      </mesh>
    )
  }
  if (floor === 7) {
    return (
      <mesh position={[0, 1.3, 0.21]}>
        <boxGeometry args={[0.07, 0.32, 0.02]} />
        <meshStandardMaterial color="#b91c1c" />
      </mesh>
    )
  }
  return null
}

function nearestZoneCenter(p: [number, number]): [number, number] {
  let best: [number, number] = [0, 0]
  let d = Infinity
  for (const z of Object.values(ZONES)) {
    const dd = Math.hypot(z.position[0] - p[0], z.position[1] - p[1])
    if (dd < d) {
      d = dd
      best = z.position
    }
  }
  return best
}

function angleDiff(a: number, b: number): number {
  let d = a - b
  while (d > Math.PI) d -= Math.PI * 2
  while (d < -Math.PI) d += Math.PI * 2
  return d
}
