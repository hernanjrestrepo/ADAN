import { Html } from '@react-three/drei'
import { useFrame } from '@react-three/fiber'
import { useRef, type ReactNode } from 'react'
import type { Group, Mesh, MeshStandardMaterial } from 'three'
import { FLOORS, type Identity } from './pisos'

// Cada Nivel tiene su propio piso: la oficina cambia de mobiliario y de luz según la etapa en que va la empresa,
// y en la pared del fondo brilla la marca que el fundador ha ido construyendo (nombre, logo y slogan).

const STICKY = ['#fde047', '#f9a8d4', '#86efac', '#93c5fd', '#fdba74']

function Glow({ color, intensity = 2, children }: { color: string; intensity?: number; children: ReactNode }) {
  return (
    <mesh>
      {children}
      <meshStandardMaterial color={color} emissive={color} emissiveIntensity={intensity} toneMapped={false} />
    </mesh>
  )
}

// Tablero con notas adhesivas (Nivel 1): las hipótesis del problema pegadas en la pared
function Whiteboard({ x, z, rot = 0 }: { x: number; z: number; rot?: number }) {
  return (
    <group position={[x, 0, z]} rotation-y={rot}>
      <mesh position-y={1.9} castShadow>
        <boxGeometry args={[4, 2.2, 0.08]} />
        <meshStandardMaterial color="#e2e8f0" roughness={0.5} />
      </mesh>
      {Array.from({ length: 12 }, (_, i) => (
        <mesh key={i} position={[-1.5 + (i % 4) * 1, 2.6 - Math.floor(i / 4) * 0.65, 0.05]} rotation-z={((i * 37) % 9 - 4) * 0.03}>
          <planeGeometry args={[0.55, 0.5]} />
          <meshStandardMaterial color={STICKY[i % STICKY.length]} />
        </mesh>
      ))}
      {[-1.7, 1.7].map((lx) => (
        <mesh key={lx} position={[lx, 0.4, 0]}><boxGeometry args={[0.08, 0.8, 0.08]} /><meshStandardMaterial color="#334155" /></mesh>
      ))}
    </group>
  )
}

// Lienzo de Propuesta de Valor (Nivel 2): el cuadrado del producto frente al círculo del cliente
function ValueCanvas({ x, z }: { x: number; z: number }) {
  return (
    <group position={[x, 0, z]}>
      <mesh position-y={2.2}><boxGeometry args={[7, 3.2, 0.1]} /><meshStandardMaterial color="#111827" /></mesh>
      <group position={[-1.7, 2.2, 0.07]}>
        <mesh><planeGeometry args={[2.4, 2.4]} /><meshStandardMaterial color="#1e293b" /></mesh>
        <mesh position-z={0.01}><ringGeometry args={[1.14, 1.2, 4, 1, Math.PI / 4]} /><meshStandardMaterial color="#f472b6" emissive="#f472b6" emissiveIntensity={2} toneMapped={false} /></mesh>
      </group>
      <group position={[1.7, 2.2, 0.08]}>
        <mesh><ringGeometry args={[1.12, 1.2, 64]} /><meshStandardMaterial color="#38bdf8" emissive="#38bdf8" emissiveIntensity={2} toneMapped={false} /></mesh>
        {[0, 1, 2].map((i) => (
          <mesh key={i} rotation-z={(i * 2 * Math.PI) / 3}><planeGeometry args={[0.03, 2.3]} /><meshStandardMaterial color="#38bdf8" /></mesh>
        ))}
      </group>
    </group>
  )
}

function Easel({ x, z, color }: { x: number; z: number; color: string }) {
  return (
    <group position={[x, 0, z]} rotation-y={0.4}>
      <mesh position={[0, 0.8, 0]} rotation-x={-0.15}><boxGeometry args={[0.06, 1.7, 0.06]} /><meshStandardMaterial color="#78350f" /></mesh>
      <mesh position={[0, 1.35, 0.08]} rotation-x={-0.15}><boxGeometry args={[1, 0.8, 0.04]} /><meshStandardMaterial color="#f8fafc" /></mesh>
      <mesh position={[0, 1.35, 0.11]} rotation-x={-0.15}><circleGeometry args={[0.25, 32]} /><meshStandardMaterial color={color} /></mesh>
    </group>
  )
}

// Pantalla con barras que crecen (Nivel 3 y 7): el flujo de caja en vivo
function ChartScreen({ x, z, rot = 0, color }: { x: number; z: number; rot?: number; color: string }) {
  const bars = useRef<(Mesh | null)[]>([])
  useFrame(({ clock }) => {
    bars.current.forEach((b, i) => {
      if (b) b.scale.y = 0.4 + Math.abs(Math.sin(clock.elapsedTime * 0.5 + i * 0.7)) * (0.3 + i * 0.1)
    })
  })
  return (
    <group position={[x, 0, z]} rotation-y={rot}>
      <mesh position-y={2.3}><boxGeometry args={[3.6, 2, 0.08]} /><meshStandardMaterial color="#020617" emissive={color} emissiveIntensity={0.12} /></mesh>
      {Array.from({ length: 6 }, (_, i) => (
        <mesh key={i} ref={(m) => { bars.current[i] = m }} position={[-1.3 + i * 0.52, 1.55, 0.06]}>
          <boxGeometry args={[0.32, 1.2, 0.02]} />
          <meshStandardMaterial color={color} emissive={color} emissiveIntensity={1.6} toneMapped={false} />
        </mesh>
      ))}
      <mesh position-y={0.65}><boxGeometry args={[0.12, 1.3, 0.12]} /><meshStandardMaterial color="#1e293b" /></mesh>
    </group>
  )
}

// Escritorio de notaría con el sello y el Expediente que se va llenando (Nivel 3)
function NotaryDesk({ x, z, identity }: { x: number; z: number; identity: Identity | null }) {
  const done = identity?.expediente?.hechos ?? 0
  const total = identity?.expediente?.total ?? 0
  return (
    <group position={[x, 0, z]}>
      <mesh position-y={0.75} castShadow><boxGeometry args={[2.6, 0.12, 1.2]} /><meshStandardMaterial color="#3f2a1d" roughness={0.6} /></mesh>
      <mesh position-y={0.36}><boxGeometry args={[2.4, 0.7, 1]} /><meshStandardMaterial color="#2a1b12" /></mesh>
      <mesh position={[0.7, 0.95, 0]}><cylinderGeometry args={[0.16, 0.2, 0.3, 24]} /><meshStandardMaterial color="#b91c1c" /></mesh>
      {[0, 1, 2].map((i) => (
        <mesh key={i} position={[-0.5, 0.83 + i * 0.04, 0.05 * i]} rotation-y={i * 0.1}><boxGeometry args={[0.8, 0.03, 1]} /><meshStandardMaterial color="#f8fafc" /></mesh>
      ))}
      <Html position={[0, 2.1, 0]} center distanceFactor={16} pointerEvents="none" zIndexRange={[5, 0]}>
        <div className="u-floor-tag">📁 Expediente · {done} de {total || '—'} listos</div>
      </Html>
    </group>
  )
}

// Impresora 3D con el cabezal en movimiento (Nivel 4)
function Printer({ x, z }: { x: number; z: number }) {
  const head = useRef<Group>(null)
  useFrame(({ clock }) => {
    if (head.current) head.current.position.x = Math.sin(clock.elapsedTime * 2 + x) * 0.45
  })
  return (
    <group position={[x, 0, z]}>
      <mesh position-y={0.45}><boxGeometry args={[1.4, 0.9, 1.2]} /><meshStandardMaterial color="#1f2937" /></mesh>
      <mesh position-y={1.45}><boxGeometry args={[1.4, 1.1, 1.2]} /><meshStandardMaterial color="#0f172a" transparent opacity={0.35} /></mesh>
      <group ref={head} position-y={1.75}><Glow color="#f59e0b" intensity={2.5}><boxGeometry args={[0.2, 0.15, 0.2]} /></Glow></group>
      <mesh position-y={1.02}><cylinderGeometry args={[0.25, 0.3, 0.15, 6]} /><meshStandardMaterial color="#fb923c" /></mesh>
    </group>
  )
}

function CodeScreen({ x, z, rot = 0 }: { x: number; z: number; rot?: number }) {
  return (
    <group position={[x, 0, z]} rotation-y={rot}>
      <mesh position-y={2.2}><boxGeometry args={[3, 1.8, 0.08]} /><meshStandardMaterial color="#020617" /></mesh>
      {Array.from({ length: 7 }, (_, i) => (
        <mesh key={i} position={[-1.2 + ((i * 3) % 5) * 0.12 + ((i % 3) * 0.6) / 2, 2.85 - i * 0.22, 0.05]}>
          <planeGeometry args={[0.6 + ((i * 7) % 5) * 0.25, 0.08]} />
          <meshStandardMaterial color={i % 3 === 0 ? '#f472b6' : i % 3 === 1 ? '#34d399' : '#60a5fa'} emissive={i % 3 === 0 ? '#f472b6' : i % 3 === 1 ? '#34d399' : '#60a5fa'} emissiveIntensity={1.4} toneMapped={false} />
        </mesh>
      ))}
    </group>
  )
}

// Tubos de ensayo que burbujean (Nivel 5): donde se rompe el modelo antes de arriesgar capital
function Beakers({ x, z }: { x: number; z: number }) {
  const mats = useRef<(MeshStandardMaterial | null)[]>([])
  useFrame(({ clock }) => {
    mats.current.forEach((m, i) => { if (m) m.emissiveIntensity = 1.2 + Math.sin(clock.elapsedTime * 3 + i) * 0.8 })
  })
  const colors = ['#ef4444', '#22d3ee', '#a3e635', '#f472b6']
  return (
    <group position={[x, 0, z]}>
      <mesh position-y={0.8}><boxGeometry args={[3, 0.1, 1]} /><meshStandardMaterial color="#e2e8f0" metalness={0.3} /></mesh>
      <mesh position-y={0.4}><boxGeometry args={[2.8, 0.8, 0.9]} /><meshStandardMaterial color="#334155" /></mesh>
      {colors.map((c, i) => (
        <mesh key={c} position={[-1.05 + i * 0.7, 1.15, 0]}>
          <cylinderGeometry args={[0.13, 0.13, 0.6, 16]} />
          <meshStandardMaterial ref={(m) => { mats.current[i] = m }} color={c} emissive={c} emissiveIntensity={1.5} transparent opacity={0.85} toneMapped={false} />
        </mesh>
      ))}
    </group>
  )
}

// Cohete sobre la tarima (Nivel 6): el lanzamiento con clientes reales
function Rocket({ x, z }: { x: number; z: number }) {
  const rocket = useRef<Group>(null)
  const flame = useRef<Mesh>(null)
  useFrame(({ clock }) => {
    const t = clock.elapsedTime
    if (rocket.current) rocket.current.position.y = 1.2 + Math.sin(t * 1.5) * 0.15
    if (flame.current) flame.current.scale.setScalar(0.8 + Math.abs(Math.sin(t * 12)) * 0.4)
  })
  return (
    <group position={[x, 0, z]}>
      <mesh position-y={0.2} receiveShadow><cylinderGeometry args={[2.4, 2.6, 0.4, 48]} /><meshStandardMaterial color="#1e1b4b" metalness={0.6} /></mesh>
      <mesh position-y={0.41} rotation-x={-Math.PI / 2}><ringGeometry args={[2.25, 2.4, 64]} /><meshStandardMaterial color="#a78bfa" emissive="#a78bfa" emissiveIntensity={2.4} toneMapped={false} /></mesh>
      <group ref={rocket}>
        <mesh position-y={1.4} castShadow><cylinderGeometry args={[0.45, 0.45, 2, 24]} /><meshStandardMaterial color="#f8fafc" metalness={0.4} /></mesh>
        <mesh position-y={2.85}><coneGeometry args={[0.45, 0.9, 24]} /><meshStandardMaterial color="#ef4444" /></mesh>
        <mesh position={[0, 1.8, 0.44]}><circleGeometry args={[0.18, 24]} /><meshStandardMaterial color="#38bdf8" emissive="#38bdf8" emissiveIntensity={1.5} /></mesh>
        {[0, 1, 2].map((i) => (
          <mesh key={i} position={[Math.sin((i * 2 * Math.PI) / 3) * 0.5, 0.6, Math.cos((i * 2 * Math.PI) / 3) * 0.5]} rotation-y={(i * 2 * Math.PI) / 3}>
            <boxGeometry args={[0.06, 0.7, 0.4]} /><meshStandardMaterial color="#ef4444" />
          </mesh>
        ))}
        <mesh ref={flame} position-y={0.2} rotation-x={Math.PI}><coneGeometry args={[0.3, 0.8, 16]} /><meshStandardMaterial color="#f59e0b" emissive="#f97316" emissiveIntensity={3} toneMapped={false} /></mesh>
      </group>
    </group>
  )
}

// Globo que gira (Nivel 7): crecer a otros mercados
function Globe({ x, z }: { x: number; z: number }) {
  const globe = useRef<Mesh>(null)
  useFrame((_, dt) => { if (globe.current) globe.current.rotation.y += dt * 0.3 })
  return (
    <group position={[x, 0, z]}>
      <mesh position-y={0.5}><cylinderGeometry args={[0.5, 0.7, 1, 24]} /><meshStandardMaterial color="#1f2937" metalness={0.7} /></mesh>
      <mesh ref={globe} position-y={2.1}>
        <sphereGeometry args={[1.1, 24, 16]} />
        <meshStandardMaterial color="#fbbf24" emissive="#fbbf24" emissiveIntensity={1.3} wireframe toneMapped={false} />
      </mesh>
    </group>
  )
}

function Plant({ x, z }: { x: number; z: number }) {
  return (
    <group position={[x, 0, z]}>
      <mesh position-y={0.3}><cylinderGeometry args={[0.35, 0.28, 0.6, 16]} /><meshStandardMaterial color="#78350f" /></mesh>
      <mesh position-y={1.05}><sphereGeometry args={[0.6, 16, 12]} /><meshStandardMaterial color="#15803d" roughness={0.8} /></mesh>
    </group>
  )
}

// Panel de neón con el color de la marca en la pared del fondo (el letrero con nombre, logo y slogan va encima
// de la escena, en EmbeddedWorld, para que siempre se vea)
function BrandSign({ identity, color }: { identity: Identity | null; color: string }) {
  const tint = identity?.color || color
  return (
    <>
      <group position={[0, 0, -18.7]}>
        <mesh position-y={4.2}><boxGeometry args={[13, 3.6, 0.2]} /><meshStandardMaterial color="#050814" metalness={0.8} roughness={0.3} /></mesh>
        <mesh position={[0, 2.35, 0.12]}><boxGeometry args={[13, 0.06, 0.06]} /><meshStandardMaterial color={tint} emissive={tint} emissiveIntensity={2.4} toneMapped={false} /></mesh>
        <mesh position={[0, 6.05, 0.12]}><boxGeometry args={[13, 0.06, 0.06]} /><meshStandardMaterial color={tint} emissive={tint} emissiveIntensity={2.4} toneMapped={false} /></mesh>
        <pointLight position={[0, 4.2, 2]} color={tint} intensity={10} distance={10} decay={1.6} />
      </group>
    </>
  )
}

// Alfombra luminosa con el número del piso, al frente (donde se para quien habla)
function FloorMark({ floor, color }: { floor: number; color: string }) {
  const ring = useRef<MeshStandardMaterial>(null)
  useFrame(({ clock }) => { if (ring.current) ring.current.emissiveIntensity = 1.6 + Math.sin(clock.elapsedTime * 2) * 0.6 })
  return (
    <group position={[0, 0.02, 10.4]}>
      <mesh rotation-x={-Math.PI / 2}><circleGeometry args={[1.6, 48]} /><meshStandardMaterial color="#0b1020" transparent opacity={0.75} /></mesh>
      <mesh rotation-x={-Math.PI / 2} position-y={0.01}>
        <ringGeometry args={[1.5, 1.62, 64]} />
        <meshStandardMaterial ref={ring} color={color} emissive={color} emissiveIntensity={2} toneMapped={false} />
      </mesh>
      {Array.from({ length: floor }, (_, k) => (
        <mesh key={k} rotation-x={-Math.PI / 2} position={[Math.cos((k / floor) * Math.PI * 2) * 1.2, 0.015, Math.sin((k / floor) * Math.PI * 2) * 1.2]}>
          <circleGeometry args={[0.1, 16]} />
          <meshStandardMaterial color={color} emissive={color} emissiveIntensity={2.5} toneMapped={false} />
        </mesh>
      ))}
    </group>
  )
}

// Lugares donde la cámara ve los muebles: al frente a lado y lado, en las esquinas y junto a las paredes
const A = [-7.5, 11.8] as const
const B = [7.5, 11.8] as const
const C = [-20, 14.5] as const
const D = [20, 14.5] as const
const E = [-20.6, 7.5] as const
const F = [20.6, 7.5] as const

export default function LevelDecor({ floor, identity }: { floor: number; identity: Identity | null }) {
  const f = FLOORS[floor] ?? FLOORS[1]!
  return (
    <group>
      <BrandSign identity={identity} color={f.color} />
      <FloorMark floor={floor} color={f.color} />
      <pointLight position={[0, 8, 0]} color={f.color} intensity={18} distance={40} decay={1.2} />
      {floor === 1 && (
        <>
          <Whiteboard x={-10} z={-17.5} /><Whiteboard x={10} z={-17.5} />
          <Whiteboard x={A[0]} z={A[1]} rot={0.25} /><Whiteboard x={B[0]} z={B[1]} rot={-0.25} />
          <Whiteboard x={E[0]} z={E[1]} rot={Math.PI / 2} /><Plant x={C[0]} z={C[1]} /><Plant x={D[0]} z={D[1]} />
        </>
      )}
      {floor === 2 && (
        <>
          <ValueCanvas x={-14.5} z={-17.6} />
          <Easel x={A[0]} z={A[1]} color="#f472b6" /><Easel x={A[0] - 1.6} z={A[1] - 0.6} color="#38bdf8" />
          <Easel x={B[0]} z={B[1]} color="#fbbf24" /><Easel x={B[0] + 1.6} z={B[1] - 0.6} color="#a3e635" />
          <Easel x={C[0]} z={C[1]} color="#fb923c" /><Easel x={D[0]} z={D[1]} color="#c084fc" />
        </>
      )}
      {floor === 3 && (
        <>
          <ChartScreen x={-10} z={-17.6} color="#4ade80" /><ChartScreen x={10} z={-17.6} color="#22d3ee" />
          <ChartScreen x={A[0]} z={A[1]} rot={0.25} color="#4ade80" /><NotaryDesk x={B[0]} z={B[1]} identity={identity} />
          <ChartScreen x={E[0]} z={E[1]} rot={Math.PI / 2} color="#fde68a" /><Plant x={C[0]} z={C[1]} /><Plant x={D[0]} z={D[1]} />
        </>
      )}
      {floor === 4 && (
        <>
          <CodeScreen x={-10} z={-17.6} /><CodeScreen x={10} z={-17.6} />
          <Printer x={A[0]} z={A[1]} /><Printer x={A[0] - 1.7} z={A[1]} /><Printer x={B[0]} z={B[1]} /><Printer x={B[0] + 1.7} z={B[1]} />
          <CodeScreen x={E[0]} z={E[1]} rot={Math.PI / 2} /><CodeScreen x={F[0]} z={F[1]} rot={-Math.PI / 2} />
        </>
      )}
      {floor === 5 && (
        <>
          <ChartScreen x={10} z={-17.6} color="#ef4444" />
          <Beakers x={A[0]} z={A[1]} /><Beakers x={B[0]} z={B[1]} /><Beakers x={C[0]} z={C[1]} />
          <ChartScreen x={E[0]} z={E[1]} rot={Math.PI / 2} color="#22d3ee" /><ChartScreen x={F[0]} z={F[1]} rot={-Math.PI / 2} color="#a3e635" />
        </>
      )}
      {floor === 6 && (
        <>
          <ChartScreen x={10} z={-17.6} color="#a78bfa" />
          <Rocket x={B[0] + 1} z={B[1]} /><Rocket x={C[0] + 1} z={C[1] - 1} />
          <ChartScreen x={A[0]} z={A[1]} rot={0.25} color="#f472b6" /><Plant x={D[0]} z={D[1]} />
        </>
      )}
      {floor === 7 && (
        <>
          <ChartScreen x={-10} z={-17.6} color="#fbbf24" /><ChartScreen x={10} z={-17.6} color="#34d399" />
          <Globe x={A[0]} z={A[1]} /><ChartScreen x={B[0]} z={B[1]} rot={-0.25} color="#fbbf24" />
          <Plant x={C[0]} z={C[1]} /><Plant x={D[0]} z={D[1]} /><Plant x={E[0]} z={E[1]} /><Plant x={F[0]} z={F[1]} />
        </>
      )}
    </group>
  )
}
