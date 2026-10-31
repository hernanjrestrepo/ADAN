import { Html } from '@react-three/drei'
import { useFrame } from '@react-three/fiber'
import { useRef } from 'react'
import { type Group, type Mesh } from 'three'
import { INVESTORS, ZONES, type Investor } from '../data'
import { useUniverso } from '../store'
import { PersonBody } from './Person'
import { MOOD_EMOJI, poseRig, type Rig } from './rig'

// Los espacios humanos de la oficina: la Cafetería, donde el equipo conversa, y La Arena de los inversionistas

export function Cafeteria() {
  const [x, z] = ZONES.cafeteria.position
  const steam = useRef<Group>(null)
  useFrame(({ clock }) => {
    steam.current?.children.forEach((c, i) => {
      const t = (clock.elapsedTime * 0.6 + i * 0.33) % 1
      c.position.y = 1.25 + t * 0.7
      c.scale.setScalar(0.6 + t)
      ;((c as Mesh).material as { opacity: number }).opacity = 0.5 * (1 - t)
    })
  })
  return (
    <group position={[x, 0, z]}>
      {/* Barra con neón ámbar y máquina de café */}
      <group position={[-2.6, 0, 0]} rotation-y={Math.PI / 2}>
        <mesh position-y={0.55} castShadow receiveShadow>
          <boxGeometry args={[3.6, 1.1, 0.7]} />
          <meshStandardMaterial color="#2a1a0c" metalness={0.4} roughness={0.45} />
        </mesh>
        <mesh position={[0, 1.12, 0]}>
          <boxGeometry args={[3.7, 0.05, 0.8]} />
          <meshStandardMaterial color="#f59e0b" emissive="#f59e0b" emissiveIntensity={1.8} toneMapped={false} />
        </mesh>
        <mesh position={[-1, 1.45, -0.05]} castShadow>
          <boxGeometry args={[0.6, 0.6, 0.45]} />
          <meshStandardMaterial color="#1f2937" metalness={0.8} roughness={0.25} />
        </mesh>
        <mesh position={[-1, 1.5, 0.18]}>
          <circleGeometry args={[0.1, 20]} />
          <meshBasicMaterial color="#fbbf24" toneMapped={false} />
        </mesh>
        <Html position={[0.6, 2.1, 0]} center distanceFactor={16} pointerEvents="none" zIndexRange={[5, 0]}>
          <div className="u-holo-level" style={{ color: '#fbbf24', borderColor: '#f59e0b' }}>☕ CAFÉ ADAN</div>
        </Html>
      </group>
      {/* Mesas redondas con taburetes y tazas humeantes */}
      {([[0.4, -1.3], [0.4, 1.4]] as const).map(([tx, tz], ti) => (
        <group key={ti} position={[tx, 0, tz]}>
          <mesh position-y={1.02} castShadow>
            <cylinderGeometry args={[0.55, 0.55, 0.05, 32]} />
            <meshStandardMaterial color="#3b2412" metalness={0.3} roughness={0.4} />
          </mesh>
          <mesh position-y={1.05} rotation-x={Math.PI / 2}>
            <torusGeometry args={[0.55, 0.015, 8, 48]} />
            <meshStandardMaterial color="#f59e0b" emissive="#f59e0b" emissiveIntensity={1.6} toneMapped={false} />
          </mesh>
          <mesh position-y={0.5}>
            <cylinderGeometry args={[0.05, 0.12, 1, 12]} />
            <meshStandardMaterial color="#1f2937" metalness={0.7} />
          </mesh>
          {[0.15, -0.18].map((cx) => (
            <mesh key={cx} position={[cx, 1.1, 0.1]}>
              <cylinderGeometry args={[0.05, 0.04, 0.1, 14]} />
              <meshStandardMaterial color="#f8fafc" roughness={0.3} />
            </mesh>
          ))}
          {[0, 1, 2].map((s) => {
            const a = (s / 3) * Math.PI * 2 + 0.4
            return (
              <mesh key={s} position={[Math.cos(a) * 0.95, 0.38, Math.sin(a) * 0.95]} castShadow>
                <cylinderGeometry args={[0.2, 0.2, 0.06, 18]} />
                <meshStandardMaterial color="#78350f" emissive="#f59e0b" emissiveIntensity={0.12} />
              </mesh>
            )
          })}
        </group>
      ))}
      <group ref={steam}>
        {[0, 1, 2].map((i) => (
          <mesh key={i} position={[0.55, 1.3, -1.2 + (i % 2) * 2.7]}>
            <sphereGeometry args={[0.05, 8, 8]} />
            <meshBasicMaterial color="#ffffff" transparent opacity={0.4} />
          </mesh>
        ))}
      </group>
      {/* Plantas */}
      {[[-1.6, -2.6], [-1.6, 2.6]].map(([px, pz]) => (
        <group key={pz} position={[px as number, 0, pz as number]}>
          <mesh position-y={0.3}>
            <cylinderGeometry args={[0.25, 0.2, 0.6, 16]} />
            <meshStandardMaterial color="#1f2937" />
          </mesh>
          <mesh position-y={0.9}>
            <icosahedronGeometry args={[0.45, 1]} />
            <meshStandardMaterial color="#15803d" emissive="#22c55e" emissiveIntensity={0.15} roughness={0.8} />
          </mesh>
        </group>
      ))}
    </group>
  )
}

function InvestorFigure({ inv, x, z }: { inv: Investor; x: number; z: number }) {
  const rig = useRef<Rig | null>(null)
  const clock = useRef(0)
  const key = `inv-${inv.id}`
  const bubble = useUniverso((s) => s.bubbles[key])
  const mood = useUniverso((s) => s.moods[key])
  useFrame((_, delta) => {
    clock.current += Math.min(delta, 0.05)
    if (rig.current) poseRig(rig.current, { clock: clock.current, moving: false, walk: 0, sit: 1, working: false, mood: useUniverso.getState().moods[key] })
  })
  return (
    <group position={[x, 0, z]} scale={1.25}>
      <PersonBody rigRef={rig} look={inv.look} color={inv.color} />
      <Html position={[0, 2.05, 0]} center distanceFactor={14} zIndexRange={[20, 0]} pointerEvents="none">
        <div className="flex flex-col items-center gap-1 select-none">
          {bubble && <div className={`u-bubble ${bubble.tone ?? ''}`} style={{ borderColor: inv.color }}>{bubble.text}</div>}
          {mood && <div className="u-mood" aria-hidden="true">{MOOD_EMOJI[mood]}</div>}
          <div className="u-tag" style={{ borderColor: inv.color }}><span style={{ color: inv.color }}>●</span> {inv.name}</div>
        </div>
      </Html>
    </group>
  )
}

export function Arena() {
  const [x, z] = ZONES.arena.position
  const spot = useRef<Mesh>(null)
  const live = useUniverso((s) => Boolean(s.arena))
  useFrame(({ clock }) => {
    if (spot.current) spot.current.scale.setScalar(1 + Math.sin(clock.elapsedTime * (live ? 4 : 1.2)) * 0.06)
  })
  return (
    <group>
      <group position={[x, 0, z]}>
        {/* Mesa de los inversionistas, de frente al punto de presentación */}
        <mesh position={[0, 0.72, -1.05]} castShadow receiveShadow>
          <boxGeometry args={[4.8, 0.06, 0.8]} />
          <meshStandardMaterial color="#1a0b0b" metalness={0.8} roughness={0.2} />
        </mesh>
        <mesh position={[0, 0.5, -0.64]}>
          <boxGeometry args={[4.8, 0.5, 0.04]} />
          <meshStandardMaterial color="#ef4444" emissive="#ef4444" emissiveIntensity={1.4} toneMapped={false} />
        </mesh>
        {ARENA_X.map((cx) => (
          <group key={cx} position={[cx, 0, -2.15]}>
            <mesh position-y={0.42}>
              <boxGeometry args={[0.5, 0.08, 0.5]} />
              <meshStandardMaterial color="#1e1b1b" metalness={0.6} />
            </mesh>
            <mesh position={[0, 0.85, -0.26]}>
              <boxGeometry args={[0.5, 0.8, 0.06]} />
              <meshStandardMaterial color="#1e1b1b" emissive="#ef4444" emissiveIntensity={0.2} />
            </mesh>
          </group>
        ))}
        {/* Punto de presentación iluminado */}
        <mesh ref={spot} rotation-x={-Math.PI / 2} position={[0, 0.03, 1.4]}>
          <ringGeometry args={[0.9, 1.05, 48]} />
          <meshBasicMaterial color="#fca5a5" transparent opacity={0.8} toneMapped={false} />
        </mesh>
        <Html position={[0, 3.3, -2.3]} center distanceFactor={16} pointerEvents="none" zIndexRange={[5, 0]}>
          <div className="u-holo-level" style={{ color: '#fca5a5', borderColor: '#ef4444' }}>🥊 LA ARENA</div>
        </Html>
      </group>
      {INVESTORS.map((inv, i) => (
        <InvestorFigure key={inv.id} inv={inv} x={x + (ARENA_X[i] ?? 0)} z={z - 2.05} />
      ))}
    </group>
  )
}

const ARENA_X = [-1.8, -0.6, 0.6, 1.8]
