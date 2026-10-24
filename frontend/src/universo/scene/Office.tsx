import { Grid } from '@react-three/drei'
import { useFrame } from '@react-three/fiber'
import { useMemo, useRef } from 'react'
import { Object3D, type InstancedMesh, type MeshStandardMaterial } from 'three'
import { AGENTS } from '../data'

const W = 46
const D = 38

// Planta, paredes de neón, escritorios del Board y la ciudad al fondo
export default function Office() {
  return (
    <>
      <mesh rotation-x={-Math.PI / 2} receiveShadow>
        <planeGeometry args={[W, D]} />
        <meshStandardMaterial color="#060a14" metalness={0.75} roughness={0.32} />
      </mesh>
      <Grid position-y={0.005} args={[W, D]} cellSize={1} cellThickness={0.6} cellColor="#13284a" sectionSize={4}
        sectionThickness={1.1} sectionColor="#1d4ed8" fadeDistance={60} fadeStrength={1.2} infiniteGrid={false} />
      <Walls />
      {AGENTS.filter((a) => a.board).map((a) => <Desk key={a.id} x={a.home[0]} z={a.home[1]} color={a.color} />)}
      <Skyline />
    </>
  )
}

function Walls() {
  const strips = useRef<(MeshStandardMaterial | null)[]>([])
  useFrame(({ clock }) => {
    strips.current.forEach((m, i) => {
      if (m) m.emissiveIntensity = 1.6 + Math.sin(clock.elapsedTime * 0.8 + i) * 0.4
    })
  })
  const walls: { pos: [number, number, number]; size: [number, number, number]; color: string }[] = [
    { pos: [0, 0.6, -D / 2], size: [W, 1.2, 0.2], color: '#7c3aed' },
    { pos: [-W / 2, 0.6, 0], size: [0.2, 1.2, D], color: '#2563eb' },
    { pos: [W / 2, 0.6, 0], size: [0.2, 1.2, D], color: '#db2777' },
  ]
  return (
    <>
      {walls.map((w, i) => (
        <group key={i}>
          <mesh position={w.pos} receiveShadow>
            <boxGeometry args={w.size} />
            <meshStandardMaterial color="#0b1222" metalness={0.8} roughness={0.3} />
          </mesh>
          <mesh position={[w.pos[0], 1.22, w.pos[2]]}>
            <boxGeometry args={[Math.max(w.size[0], 0.06), 0.05, Math.max(w.size[2], 0.06)]} />
            <meshStandardMaterial ref={(m) => { strips.current[i] = m }} color={w.color} emissive={w.color}
              emissiveIntensity={1.8} toneMapped={false} />
          </mesh>
        </group>
      ))}
      {/* Columnas de luz en las esquinas */}
      {[[-W / 2, -D / 2], [W / 2, -D / 2], [-W / 2, D / 2], [W / 2, D / 2]].map(([x, z]) => (
        <mesh key={`${x}${z}`} position={[x as number, 3, z as number]}>
          <cylinderGeometry args={[0.12, 0.12, 6, 12]} />
          <meshStandardMaterial color="#38bdf8" emissive="#38bdf8" emissiveIntensity={2.5} toneMapped={false} />
        </mesh>
      ))}
    </>
  )
}

function Desk({ x, z, color }: { x: number; z: number; color: string }) {
  const facing = Math.atan2(-x, 2 - z)
  return (
    <group position={[x, 0, z]} rotation-y={facing}>
      <group position={[0, 0, 0.75]}>
        <mesh position-y={0.74} castShadow receiveShadow>
          <boxGeometry args={[1.5, 0.05, 0.7]} />
          <meshStandardMaterial color="#0f1b33" metalness={0.8} roughness={0.2} transparent opacity={0.9} />
        </mesh>
        <mesh position={[0, 0.76, 0.35]}>
          <boxGeometry args={[1.5, 0.02, 0.02]} />
          <meshStandardMaterial color={color} emissive={color} emissiveIntensity={2.2} toneMapped={false} />
        </mesh>
        <mesh position={[0, 1.15, -0.2]}>
          <planeGeometry args={[0.9, 0.5]} />
          <meshStandardMaterial color="#0b1222" emissive={color} emissiveIntensity={0.5} side={2} transparent opacity={0.85} />
        </mesh>
        {[-0.65, 0.65].map((dx) => (
          <mesh key={dx} position={[dx, 0.37, 0]}>
            <boxGeometry args={[0.05, 0.74, 0.6]} />
            <meshStandardMaterial color="#1e293b" metalness={0.7} roughness={0.3} />
          </mesh>
        ))}
      </group>
    </group>
  )
}

// Torres lejanas con ventanas encendidas: la oficina flota sobre una ciudad
function Skyline() {
  const mesh = useRef<InstancedMesh>(null)
  const towers = useMemo(() => {
    const out: { x: number; z: number; h: number; w: number }[] = []
    for (let i = 0; i < 70; i++) {
      const side = i % 3
      const t = i / 70
      const x = side === 0 ? -60 + t * 120 : side === 1 ? -36 - (i % 7) * 4 : 36 + (i % 7) * 4
      const z = side === 0 ? -36 - (i % 5) * 5 : -30 + ((i * 13) % 60)
      out.push({ x, z, h: 6 + ((i * 29) % 24), w: 2.5 + ((i * 7) % 3) })
    }
    return out
  }, [])
  const dummy = useMemo(() => new Object3D(), [])
  useFrame(() => {
    const m = mesh.current
    if (!m || m.userData.done) return
    towers.forEach((t, i) => {
      dummy.position.set(t.x, t.h / 2 - 4, t.z)
      dummy.scale.set(t.w, t.h, t.w)
      dummy.updateMatrix()
      m.setMatrixAt(i, dummy.matrix)
    })
    m.instanceMatrix.needsUpdate = true
    m.userData.done = true
  })
  return (
    <instancedMesh ref={mesh} args={[undefined, undefined, towers.length]}>
      <boxGeometry args={[1, 1, 1]} />
      <meshStandardMaterial color="#0a1024" emissive="#312e81" emissiveIntensity={0.35} metalness={0.6} roughness={0.5} />
    </instancedMesh>
  )
}
