import { Html } from '@react-three/drei'
import { useFrame } from '@react-three/fiber'
import { useMemo, useRef } from 'react'
import { Color, Object3D, type Group, type InstancedMesh, type Mesh, type MeshStandardMaterial } from 'three'
import { AGENTS, ZONES, type ZoneId } from '../data'
import { levelOf, useUniverso } from '../store'
import { BOARD_CENTER, BOARD_RADIUS, TABLE_RADIUS, seatFacing, seatPosition } from './layout'
import { Arena, Cafeteria } from './Lounge'

function useActive(zone: ZoneId): boolean {
  return useUniverso((s) => levelOf(s.level).zones.includes(zone))
}

// Disco de piso con anillo de neón y etiqueta: brilla más cuando la zona trabaja en el Nivel actual
function ZoneBase({ zone, radius = 3.2, labelBack = false }: { zone: ZoneId; radius?: number; labelBack?: boolean }) {
  const z = ZONES[zone]
  const active = useActive(zone)
  const focus = useUniverso((s) => s.focus)
  const ring = useRef<MeshStandardMaterial>(null)
  useFrame(({ clock }) => {
    if (ring.current) ring.current.emissiveIntensity = active ? 2.4 + Math.sin(clock.elapsedTime * 2.5) * 0.8 : 0.6
  })
  return (
    <group position={[z.position[0], 0, z.position[1]]}>
      <mesh rotation-x={-Math.PI / 2} position-y={0.01} receiveShadow>
        <circleGeometry args={[radius, 64]} />
        <meshStandardMaterial color="#0c1426" metalness={0.7} roughness={0.3} transparent opacity={0.9} />
      </mesh>
      <mesh rotation-x={-Math.PI / 2} position-y={0.025}>
        <ringGeometry args={[radius - 0.08, radius, 96]} />
        <meshStandardMaterial ref={ring} color={z.color} emissive={z.color} emissiveIntensity={1} toneMapped={false} />
      </mesh>
      <Html position={[0, labelBack ? 2.9 : 0.05, labelBack ? -radius - 0.3 : radius + 0.55]} center distanceFactor={labelBack ? 15 : 20} zIndexRange={[10, 0]}>
        <button type="button" className={`u-zone ${active ? 'is-active' : ''}`} style={{ borderColor: z.color }}
          onClick={() => focus(zone)}>
          <span className="u-zone-name" style={{ color: z.color }}>{z.name}</span>
          <span className="u-zone-short">{z.short}</span>
        </button>
      </Html>
    </group>
  )
}

function BoardRoom() {
  const holo = useRef<Group>(null)
  const level = useUniverso((s) => s.level)
  const session = useUniverso((s) => Boolean(s.board))
  useFrame(({ clock }) => {
    if (holo.current) {
      holo.current.rotation.y = clock.elapsedTime * (session ? 1.2 : 0.35)
      holo.current.position.y = 1.55 + Math.sin(clock.elapsedTime * 1.5) * 0.05
    }
  })
  return (
    <group position={[BOARD_CENTER[0], 0, BOARD_CENTER[1]]}>
      {/* Vidrio con puerta al frente (+z) */}
      <mesh position-y={1.6}>
        <cylinderGeometry args={[BOARD_RADIUS, BOARD_RADIUS, 3.2, 64, 1, true, Math.PI / 2 + 0.32, Math.PI * 2 - 0.64]} />
        <meshStandardMaterial color="#60a5fa" transparent opacity={0.09} metalness={0.9} roughness={0.05} side={2} />
      </mesh>
      <mesh position-y={3.2} rotation-x={Math.PI / 2}>
        <torusGeometry args={[BOARD_RADIUS, 0.03, 8, 96]} />
        <meshStandardMaterial color="#60a5fa" emissive="#60a5fa" emissiveIntensity={2.2} toneMapped={false} />
      </mesh>
      <mesh position-y={0.04} rotation-x={Math.PI / 2}>
        <torusGeometry args={[BOARD_RADIUS, 0.04, 8, 96]} />
        <meshStandardMaterial color="#60a5fa" emissive="#60a5fa" emissiveIntensity={1.6} toneMapped={false} />
      </mesh>
      {/* Mesa */}
      <mesh position-y={0.74} castShadow receiveShadow>
        <cylinderGeometry args={[TABLE_RADIUS, TABLE_RADIUS, 0.06, 64]} />
        <meshStandardMaterial color="#0f1b33" metalness={0.8} roughness={0.15} transparent opacity={0.92} />
      </mesh>
      <mesh position-y={0.77} rotation-x={Math.PI / 2}>
        <torusGeometry args={[TABLE_RADIUS, 0.025, 8, 96]} />
        <meshStandardMaterial color="#93c5fd" emissive="#60a5fa" emissiveIntensity={2.6} toneMapped={false} />
      </mesh>
      <mesh position-y={0.37}>
        <cylinderGeometry args={[0.35, 0.5, 0.72, 24]} />
        <meshStandardMaterial color="#0b1222" metalness={0.8} roughness={0.3} />
      </mesh>
      {/* Holograma del Nivel en el centro de la mesa */}
      <group ref={holo}>
        <mesh rotation-x={Math.PI / 2}>
          <torusGeometry args={[0.55, 0.015, 8, 64]} />
          <meshBasicMaterial color="#7dd3fc" toneMapped={false} />
        </mesh>
        <mesh rotation-x={Math.PI / 3}>
          <torusGeometry args={[0.42, 0.012, 8, 64]} />
          <meshBasicMaterial color="#a78bfa" toneMapped={false} />
        </mesh>
        <mesh>
          <icosahedronGeometry args={[0.22, 1]} />
          <meshBasicMaterial color="#38bdf8" wireframe toneMapped={false} />
        </mesh>
      </group>
      <Html position={[0, 2.25, 0]} center distanceFactor={18} pointerEvents="none" zIndexRange={[5, 0]}>
        <div className="u-holo-level">NIVEL {level}</div>
      </Html>
      {/* Sillas */}
      {AGENTS.filter((a) => a.seat !== undefined).map((a) => {
        const [x, z] = seatPosition(a.seat as number)
        const rot = seatFacing(a.seat as number)
        return (
          <group key={a.id} position={[x - BOARD_CENTER[0], 0, z - BOARD_CENTER[1]]} rotation-y={rot}>
            <mesh position-y={0.42} castShadow>
              <boxGeometry args={[0.5, 0.08, 0.5]} />
              <meshStandardMaterial color="#1e293b" metalness={0.6} roughness={0.35} />
            </mesh>
            <mesh position={[0, 0.8, -0.26]} castShadow>
              <boxGeometry args={[0.5, 0.7, 0.06]} />
              <meshStandardMaterial color="#1e293b" metalness={0.6} roughness={0.35} emissive={a.color} emissiveIntensity={0.15} />
            </mesh>
            <mesh position-y={0.2}>
              <cylinderGeometry args={[0.04, 0.04, 0.4, 8]} />
              <meshStandardMaterial color="#334155" />
            </mesh>
          </group>
        )
      })}
    </group>
  )
}

function Radar() {
  const dish = useRef<Group>(null)
  const sweep = useRef<Mesh>(null)
  const active = useActive('csi')
  const [x, z] = ZONES.csi.position
  useFrame(({ clock }, delta) => {
    if (dish.current) dish.current.rotation.y += delta * (active ? 0.9 : 0.25)
    if (sweep.current) sweep.current.rotation.z = -clock.elapsedTime * (active ? 2.2 : 0.6)
  })
  return (
    <group position={[x, 0, z]}>
      <mesh ref={sweep} rotation-x={-Math.PI / 2} position-y={0.04}>
        <circleGeometry args={[2.9, 48, 0, Math.PI / 4]} />
        <meshBasicMaterial color="#22d3ee" transparent opacity={0.22} toneMapped={false} />
      </mesh>
      <mesh position-y={0.6} castShadow>
        <cylinderGeometry args={[0.18, 0.3, 1.2, 16]} />
        <meshStandardMaterial color="#1e293b" metalness={0.8} roughness={0.3} />
      </mesh>
      <group ref={dish} position-y={1.4}>
        <mesh rotation-x={-0.6}>
          <sphereGeometry args={[0.9, 32, 16, 0, Math.PI * 2, 0, Math.PI / 3.2]} />
          <meshStandardMaterial color="#cbd5e1" metalness={0.9} roughness={0.2} side={2} />
        </mesh>
        <mesh position={[0, 0.3, 0.35]}>
          <sphereGeometry args={[0.07, 12, 12]} />
          <meshStandardMaterial color="#22d3ee" emissive="#22d3ee" emissiveIntensity={4} toneMapped={false} />
        </mesh>
      </group>
      <DataMotes color="#22d3ee" count={24} radius={2.4} />
    </group>
  )
}

function DataMotes({ color, count, radius }: { color: string; count: number; radius: number }) {
  const mesh = useRef<InstancedMesh>(null)
  const seeds = useMemo(() => Array.from({ length: count }, (_, i) => ({ a: (i / count) * Math.PI * 2, r: radius * (0.4 + ((i * 37) % 10) / 16), s: 0.3 + ((i * 13) % 7) / 10 })), [count, radius])
  const dummy = useMemo(() => new Object3D(), [])
  useFrame(({ clock }) => {
    const m = mesh.current
    if (!m) return
    seeds.forEach((p, i) => {
      const t = clock.elapsedTime * p.s + p.a
      dummy.position.set(Math.cos(t) * p.r, 0.6 + ((t * 0.4) % 2.6), Math.sin(t) * p.r)
      dummy.scale.setScalar(0.05)
      dummy.updateMatrix()
      m.setMatrixAt(i, dummy.matrix)
    })
    m.instanceMatrix.needsUpdate = true
  })
  return (
    <instancedMesh ref={mesh} args={[undefined, undefined, count]}>
      <octahedronGeometry args={[1, 0]} />
      <meshBasicMaterial color={color} toneMapped={false} />
    </instancedMesh>
  )
}

function Memoria() {
  const [x, z] = ZONES.memoria.position
  const lights = useRef<(MeshStandardMaterial | null)[]>([])
  const layers = useRef<Group>(null)
  useFrame(({ clock }) => {
    lights.current.forEach((m, i) => {
      if (m) m.emissiveIntensity = 1 + Math.max(0, Math.sin(clock.elapsedTime * 3 + i * 1.7)) * 3
    })
    if (layers.current) layers.current.rotation.y = clock.elapsedTime * 0.3
  })
  return (
    <group position={[x, 0, z]}>
      {[-2.6, -1.3, 0, 1.3, 2.6].map((dx, i) => (
        <group key={dx} position={[dx, 0, -1.2 + Math.abs(dx) * 0.25]} rotation-y={-dx * 0.12}>
          <mesh position-y={1.2} castShadow>
            <boxGeometry args={[0.9, 2.4, 0.8]} />
            <meshStandardMaterial color="#0f172a" metalness={0.8} roughness={0.25} />
          </mesh>
          {[0.5, 0.9, 1.3, 1.7, 2.1].map((y, j) => (
            <mesh key={y} position={[0, y, 0.41]}>
              <boxGeometry args={[0.7, 0.04, 0.01]} />
              <meshStandardMaterial ref={(m) => { lights.current[i * 5 + j] = m }} color="#a78bfa" emissive="#a78bfa"
                emissiveIntensity={2} toneMapped={false} />
            </mesh>
          ))}
        </group>
      ))}
      {/* Las cinco capas de memoria (AD-CMP-04) */}
      <group ref={layers} position={[0, 0, 1]}>
        {[0, 1, 2, 3, 4].map((i) => (
          <mesh key={i} position-y={0.6 + i * 0.45} rotation-x={Math.PI / 2}>
            <torusGeometry args={[1.1 - i * 0.14, 0.018, 8, 64]} />
            <meshBasicMaterial color={i % 2 ? '#c4b5fd' : '#8b5cf6'} toneMapped={false} />
          </mesh>
        ))}
      </group>
    </group>
  )
}

function Genexis() {
  const [x, z] = ZONES.genexis.position
  const model = useRef<Mesh>(null)
  const scan = useRef<Mesh>(null)
  const progress = useUniverso((s) => ['l4-alcance', 'l4-blueprint', 'l4-construir'].filter((t) => s.doneTasks.includes(t)).length)
  const active = useActive('genexis')
  useFrame(({ clock }, delta) => {
    if (model.current) {
      model.current.rotation.y += delta * 0.6
      const target = 0.35 + progress * 0.22
      model.current.scale.setScalar(model.current.scale.x + (target - model.current.scale.x) * Math.min(1, delta * 2))
    }
    if (scan.current) {
      scan.current.position.y = 0.4 + ((clock.elapsedTime * (active ? 0.9 : 0.3)) % 2.2)
    }
  })
  return (
    <group position={[x, 0, z]}>
      <mesh position-y={0.15} receiveShadow>
        <cylinderGeometry args={[1.5, 1.7, 0.3, 48]} />
        <meshStandardMaterial color="#1a1030" metalness={0.8} roughness={0.25} />
      </mesh>
      <mesh ref={model} position-y={1.5}>
        <torusKnotGeometry args={[0.9, 0.26, 128, 16]} />
        <meshStandardMaterial color="#f472b6" emissive="#db2777" emissiveIntensity={progress >= 3 ? 1.6 : 0.6}
          wireframe={progress < 3} toneMapped={false} />
      </mesh>
      <mesh ref={scan} rotation-x={-Math.PI / 2}>
        <ringGeometry args={[0.2, 1.6, 48]} />
        <meshBasicMaterial color="#f9a8d4" transparent opacity={0.25} toneMapped={false} side={2} />
      </mesh>
      {[-1, 1].map((s) => (
        <mesh key={s} position={[s * 2, 1.4, -0.4]} castShadow>
          <boxGeometry args={[0.12, 2.8, 0.12]} />
          <meshStandardMaterial color="#f472b6" emissive="#f472b6" emissiveIntensity={1.5} toneMapped={false} />
        </mesh>
      ))}
    </group>
  )
}

function Simulador() {
  const [x, z] = ZONES.simulador.position
  const crowd = useRef<InstancedMesh>(null)
  const active = useActive('simulador')
  const COUNT = 54
  const seeds = useMemo(() => Array.from({ length: COUNT }, (_, i) => ({ a: (i / COUNT) * Math.PI * 2, r: 1 + (i % 3) * 0.75, s: (i % 2 ? 1 : -1) * (0.2 + (i % 5) * 0.05) })), [])
  const dummy = useMemo(() => new Object3D(), [])
  const colors = useMemo(() => {
    const yes = new Color('#4ade80')
    const no = new Color('#f87171')
    const maybe = new Color('#fbbf24')
    return seeds.map((_, i) => (i % 5 === 0 ? no : i % 3 === 0 ? maybe : yes))
  }, [seeds])
  useFrame(({ clock }) => {
    const m = crowd.current
    if (!m) return
    const speed = active ? 1 : 0.25
    seeds.forEach((p, i) => {
      const t = clock.elapsedTime * p.s * speed + p.a
      dummy.position.set(Math.cos(t) * p.r, 0.22 + Math.abs(Math.sin(t * 6)) * 0.04, Math.sin(t) * p.r)
      dummy.rotation.y = -t
      dummy.updateMatrix()
      m.setMatrixAt(i, dummy.matrix)
      m.setColorAt(i, colors[i] as Color)
    })
    m.instanceMatrix.needsUpdate = true
    if (m.instanceColor) m.instanceColor.needsUpdate = true
  })
  return (
    <group position={[x, 0, z]}>
      <mesh rotation-x={-Math.PI / 2} position-y={0.03}>
        <ringGeometry args={[0.6, 2.9, 64, 4]} />
        <meshBasicMaterial color="#fbbf24" wireframe transparent opacity={0.18} toneMapped={false} />
      </mesh>
      <instancedMesh ref={crowd} args={[undefined, undefined, COUNT]}>
        <capsuleGeometry args={[0.07, 0.22, 4, 8]} />
        <meshStandardMaterial emissiveIntensity={1.4} toneMapped={false} />
      </instancedMesh>
    </group>
  )
}

function Gemelo() {
  const [x, z] = ZONES.gemelo.position
  const tower = useRef<Group>(null)
  const closed = useUniverso((s) => s.closedLevels)
  useFrame(({ clock }) => {
    if (tower.current) tower.current.rotation.y = clock.elapsedTime * 0.25
  })
  return (
    <group position={[x, 0, z]}>
      <mesh position-y={0.12}>
        <cylinderGeometry args={[1.5, 1.7, 0.24, 6]} />
        <meshStandardMaterial color="#06281f" metalness={0.8} roughness={0.25} emissive="#34d399" emissiveIntensity={0.15} />
      </mesh>
      <group ref={tower} position-y={0.3}>
        {[1, 2, 3, 4, 5, 6, 7].map((n) => {
          const lit = closed.includes(n)
          const w = 1.25 - n * 0.12
          return (
            <mesh key={n} position-y={(n - 1) * 0.42 + 0.2}>
              <boxGeometry args={[w, 0.34, w]} />
              <meshStandardMaterial color={lit ? '#34d399' : '#10b981'} emissive="#34d399" emissiveIntensity={lit ? 1.8 : 0.08}
                wireframe={!lit} transparent opacity={lit ? 0.9 : 0.5} toneMapped={false} />
            </mesh>
          )
        })}
      </group>
      <DataMotes color="#6ee7b7" count={18} radius={1.6} />
    </group>
  )
}

function Eva() {
  const [x, z] = ZONES.eva.position
  const bars = useRef<InstancedMesh>(null)
  const active = useActive('eva')
  const N = 24
  const dummy = useMemo(() => new Object3D(), [])
  useFrame(({ clock }) => {
    const m = bars.current
    if (!m) return
    for (let i = 0; i < N; i++) {
      const h = 0.15 + Math.abs(Math.sin(clock.elapsedTime * (active ? 5 : 1.5) + i * 0.6) * Math.cos(i * 0.3)) * (active ? 1.6 : 0.5)
      dummy.position.set((i - N / 2) * 0.16, 1 + h / 2, -1.5)
      dummy.scale.set(0.09, h, 0.09)
      dummy.updateMatrix()
      m.setMatrixAt(i, dummy.matrix)
    }
    m.instanceMatrix.needsUpdate = true
  })
  return (
    <group position={[x, 0, z]}>
      <mesh position={[0, 1.7, -1.62]}>
        <planeGeometry args={[4.4, 2.2]} />
        <meshStandardMaterial color="#1c0f05" emissive="#fb923c" emissiveIntensity={0.12} metalness={0.6} roughness={0.3} />
      </mesh>
      <instancedMesh ref={bars} args={[undefined, undefined, N]}>
        <boxGeometry args={[1, 1, 1]} />
        <meshBasicMaterial color="#fb923c" toneMapped={false} />
      </instancedMesh>
      <mesh position={[0, 0.5, 0.6]} castShadow>
        <cylinderGeometry args={[0.6, 0.7, 1, 32]} />
        <meshStandardMaterial color="#1e293b" metalness={0.7} roughness={0.3} />
      </mesh>
      <mesh position={[0, 1.15, 0.6]}>
        <sphereGeometry args={[0.18, 16, 16]} />
        <meshStandardMaterial color="#fb923c" emissive="#fb923c" emissiveIntensity={3} toneMapped={false} />
      </mesh>
    </group>
  )
}

function Mercado() {
  const [x, z] = ZONES.mercado.position
  const badges = useRef<Group>(null)
  useFrame(({ clock }) => {
    if (badges.current) {
      badges.current.children.forEach((c, i) => {
        c.rotation.y = clock.elapsedTime * 1.2 + i
        c.position.y = 2 + Math.sin(clock.elapsedTime * 1.5 + i) * 0.15
      })
    }
  })
  return (
    <group position={[x, 0, z]}>
      {[-2.4, 0, 2.4].map((dx) => (
        <group key={dx} position={[dx, 0, -0.6]}>
          <mesh position-y={0.55} castShadow>
            <boxGeometry args={[1.4, 1.1, 0.7]} />
            <meshStandardMaterial color="#1b1030" metalness={0.7} roughness={0.3} />
          </mesh>
          <mesh position={[0, 1.12, 0]}>
            <boxGeometry args={[1.45, 0.05, 0.75]} />
            <meshStandardMaterial color="#c084fc" emissive="#c084fc" emissiveIntensity={2} toneMapped={false} />
          </mesh>
        </group>
      ))}
      <group ref={badges}>
        {['#c084fc', '#a3e635', '#22d3ee', '#fb923c', '#f472b6'].map((c, i) => (
          <mesh key={c} position={[(i - 2) * 1.2, 2, -0.6]}>
            <octahedronGeometry args={[0.22, 0]} />
            <meshStandardMaterial color={c} emissive={c} emissiveIntensity={2.2} toneMapped={false} />
          </mesh>
        ))}
      </group>
    </group>
  )
}

export default function Zones() {
  return (
    <>
      <ZoneBase zone="board" radius={BOARD_RADIUS + 0.4} />
      <BoardRoom />
      <ZoneBase zone="csi" />
      <Radar />
      <ZoneBase zone="memoria" radius={3.6} labelBack />
      <Memoria />
      <ZoneBase zone="genexis" />
      <Genexis />
      <ZoneBase zone="simulador" />
      <Simulador />
      <ZoneBase zone="gemelo" radius={2.6} />
      <Gemelo />
      <ZoneBase zone="eva" />
      <Eva />
      <ZoneBase zone="mercado" radius={3.6} />
      <Mercado />
      <ZoneBase zone="cafeteria" radius={3.4} />
      <Cafeteria />
      <ZoneBase zone="arena" radius={3.6} />
      <Arena />
    </>
  )
}
