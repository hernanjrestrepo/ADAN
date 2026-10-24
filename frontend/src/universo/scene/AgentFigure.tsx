import { Html } from '@react-three/drei'
import { useFrame } from '@react-three/fiber'
import { useMemo, useRef, useState } from 'react'
import { Color, type Group, type Mesh, type MeshStandardMaterial } from 'three'
import { type Agent } from '../data'
import { levelOf, useUniverso } from '../store'
import { livePositions, planPath, seatFacing, seatPosition, zoneSpot } from './layout'

const SPEED = 2.4

type Vec2 = [number, number]

// Un integrante del equipo de ADÁN: camina por la oficina, trabaja en las zonas y se sienta en el Board.
export default function AgentFigure({ agent }: { agent: Agent }) {
  const root = useRef<Group>(null)
  const body = useRef<Group>(null)
  const legL = useRef<Group>(null)
  const legR = useRef<Group>(null)
  const armL = useRef<Group>(null)
  const armR = useRef<Group>(null)
  const screen = useRef<Mesh>(null)
  const ring = useRef<Mesh>(null)
  const visor = useRef<MeshStandardMaterial>(null)
  const nav = useRef({
    pos: [agent.home[0], agent.home[1]] as Vec2, path: [] as Vec2[], targetKey: '', heading: 0, walk: 0,
    wanderUntil: 0, wanderAt: 6 + ((agent.home[0] * 7 + agent.home[1] * 13 + 140) % 14), wanderTarget: null as Vec2 | null, clock: 0, seated: 0,
  })
  const [hover, setHover] = useState(false)
  const selected = useUniverso((s) => s.selected === agent.id)
  const bubble = useUniverso((s) => s.bubbles[agent.id])
  const select = useUniverso((s) => s.select)
  // Traje teñido del color del rol: se distingue a cada quien desde lejos
  const suit = useMemo(() => '#' + new Color(agent.color).lerp(new Color('#1e293b'), 0.62).getHexString(), [agent.color])

  useFrame((_, rawDelta) => {
    const delta = Math.min(rawDelta, 0.05)
    const n = nav.current
    n.clock += delta
    const s = useUniverso.getState()
    const job = s.jobs[agent.id]
    const inBoard = Boolean(s.board) && agent.board && agent.seat !== undefined
    const now = Date.now()

    // 1. ¿A dónde debe ir?
    let target: Vec2 = agent.home
    let key = 'home'
    if (inBoard && agent.seat !== undefined) {
      target = seatPosition(agent.seat)
      key = 'seat'
    } else if (job && job.phase !== 'returning') {
      target = zoneSpot(job.zone, agent.id)
      key = `job:${job.zone}`
    } else if (!job && n.wanderTarget && n.clock < n.wanderUntil) {
      target = n.wanderTarget
      key = `wander:${target[0].toFixed(1)}`
    }
    // Vida en la oficina: quien está libre a veces va a colaborar a una zona activa del Nivel
    if (!job && !inBoard && agent.id !== 'ceo') {
      if (n.wanderTarget && n.clock >= n.wanderUntil) {
        n.wanderTarget = null
        n.wanderAt = n.clock + 12 + Math.random() * 18
      } else if (!n.wanderTarget && n.clock >= n.wanderAt) {
        const zones = levelOf(s.level).zones.filter((z) => z !== 'board')
        const zone = zones[Math.floor(Math.random() * zones.length)]
        if (zone) {
          n.wanderTarget = zoneSpot(zone, agent.id)
          n.wanderUntil = n.clock + 9 + Math.random() * 6
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
        const step = Math.min(dist, SPEED * (key === 'seat' ? 1.5 : 1) * delta)
        n.pos = [n.pos[0] + (dx / dist) * step, n.pos[1] + (dz / dist) * step]
        const want = Math.atan2(dx, dz)
        n.heading += angleDiff(want, n.heading) * Math.min(1, delta * 10)
        moving = true
      }
    }
    const arrived = n.path.length === 0

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
    } else if (arrived && !moving && !working) {
      const face = Math.atan2(-n.pos[0], 2 - n.pos[1])
      n.heading += angleDiff(face, n.heading) * Math.min(1, delta * 2)
    }
    n.seated += ((seatedNow ? 1 : 0) - n.seated) * Math.min(1, delta * 6)

    // 4. Animación
    n.walk += moving ? delta * 9 : 0
    const swing = moving ? Math.sin(n.walk) * 0.6 : 0
    const sit = n.seated
    if (root.current) {
      root.current.position.set(n.pos[0], 0, n.pos[1])
      root.current.rotation.y = n.heading
    }
    livePositions.set(agent.id, n.pos)
    if (body.current) {
      body.current.position.y = -0.42 * sit + (moving ? Math.abs(Math.sin(n.walk)) * 0.05 : Math.sin(n.clock * 1.6) * 0.012)
    }
    if (legL.current) legL.current.rotation.x = swing * (1 - sit) - 1.45 * sit
    if (legR.current) legR.current.rotation.x = -swing * (1 - sit) - 1.45 * sit
    const typing = working ? Math.sin(n.clock * 14) * 0.12 : 0
    if (armL.current) armL.current.rotation.x = working ? -1.1 + typing : -swing * 0.8 - 0.3 * sit
    if (armR.current) armR.current.rotation.x = working ? -1.1 - typing : swing * 0.8 - 0.3 * sit
    if (screen.current) {
      screen.current.visible = working
      screen.current.rotation.y = Math.sin(n.clock * 2) * 0.05
    }
    if (ring.current) {
      const pulse = selected || hover ? 1.15 + Math.sin(n.clock * 5) * 0.08 : 1
      ring.current.scale.setScalar(pulse)
    }
    if (visor.current) visor.current.emissiveIntensity = (working ? 3.2 : 2) + Math.sin(n.clock * 3) * 0.3
  })

  const showTag = hover || selected || Boolean(bubble)

  return (
    <group ref={root} scale={1.25}
      onClick={(e) => { e.stopPropagation(); select(agent.id) }}
      onPointerOver={(e) => { e.stopPropagation(); setHover(true); document.body.style.cursor = 'pointer' }}
      onPointerOut={() => { setHover(false); document.body.style.cursor = '' }}>
      <mesh ref={ring} rotation-x={-Math.PI / 2} position-y={0.02}>
        <ringGeometry args={[0.42, 0.55, 40]} />
        <meshBasicMaterial color={agent.color} transparent opacity={selected ? 0.95 : 0.55} toneMapped={false} />
      </mesh>
      <group ref={body}>
        <group ref={legL} position={[-0.12, 0.78, 0]}>
          <mesh position-y={-0.38} castShadow>
            <capsuleGeometry args={[0.085, 0.55, 4, 10]} />
            <meshStandardMaterial color={suit} emissive={agent.color} emissiveIntensity={0.12} roughness={0.5} metalness={0.4} />
          </mesh>
        </group>
        <group ref={legR} position={[0.12, 0.78, 0]}>
          <mesh position-y={-0.38} castShadow>
            <capsuleGeometry args={[0.085, 0.55, 4, 10]} />
            <meshStandardMaterial color={suit} emissive={agent.color} emissiveIntensity={0.12} roughness={0.5} metalness={0.4} />
          </mesh>
        </group>
        <mesh position-y={1.16} castShadow>
          <capsuleGeometry args={[0.24, 0.42, 6, 16]} />
          <meshStandardMaterial color={suit} emissive={agent.color} emissiveIntensity={0.12} roughness={0.35} metalness={0.55} />
        </mesh>
        <mesh position={[0, 1.3, 0.2]}>
          <boxGeometry args={[0.2, 0.05, 0.02]} />
          <meshStandardMaterial color={agent.color} emissive={agent.color} emissiveIntensity={2.4} toneMapped={false} />
        </mesh>
        <mesh position-y={0.93} rotation-x={Math.PI / 2}>
          <torusGeometry args={[0.25, 0.025, 8, 32]} />
          <meshStandardMaterial color={agent.color} emissive={agent.color} emissiveIntensity={2.2} toneMapped={false} />
        </mesh>
        <group ref={armL} position={[-0.32, 1.42, 0]}>
          <mesh position-y={-0.27} castShadow>
            <capsuleGeometry args={[0.065, 0.42, 4, 10]} />
            <meshStandardMaterial color={suit} emissive={agent.color} emissiveIntensity={0.12} roughness={0.45} metalness={0.5} />
          </mesh>
        </group>
        <group ref={armR} position={[0.32, 1.42, 0]}>
          <mesh position-y={-0.27} castShadow>
            <capsuleGeometry args={[0.065, 0.42, 4, 10]} />
            <meshStandardMaterial color={suit} emissive={agent.color} emissiveIntensity={0.12} roughness={0.45} metalness={0.5} />
          </mesh>
        </group>
        <mesh position-y={1.8} castShadow>
          <sphereGeometry args={[0.2, 24, 24]} />
          <meshStandardMaterial color="#e2e8f0" roughness={0.25} metalness={0.2} />
        </mesh>
        <mesh position={[0, 1.82, 0.13]} scale={[1, 0.45, 0.6]}>
          <sphereGeometry args={[0.17, 24, 12]} />
          <meshStandardMaterial ref={visor} color={agent.color} emissive={agent.color} emissiveIntensity={2} toneMapped={false} />
        </mesh>
        <mesh ref={screen} position={[0, 1.25, 0.55]} visible={false}>
          <planeGeometry args={[0.7, 0.42]} />
          <meshBasicMaterial color={agent.color} transparent opacity={0.35} toneMapped={false} side={2} />
        </mesh>
        <Html position={[0, 2.35, 0]} center distanceFactor={14} zIndexRange={[20, 0]} pointerEvents="none">
          {showTag && (
            <div className="flex flex-col items-center gap-1 select-none">
              {bubble && (
                <div className={`u-bubble ${bubble.tone ?? ''}`} style={{ borderColor: agent.color }}>{bubble.text}</div>
              )}
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

function angleDiff(a: number, b: number): number {
  let d = a - b
  while (d > Math.PI) d -= Math.PI * 2
  while (d < -Math.PI) d += Math.PI * 2
  return d
}
