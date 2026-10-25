import { CameraControls, Stars } from '@react-three/drei'
import { Canvas } from '@react-three/fiber'
import { Bloom, EffectComposer, Vignette } from '@react-three/postprocessing'
import { useEffect, useRef } from 'react'
import { AGENTS, ZONES } from '../data'
import { useUniverso } from '../store'
import AgentFigure from './AgentFigure'
import Holo from './Holo'
import { livePositions } from './layout'
import Office from './Office'
import Zones from './Zones'

// El panel de misión ocupa la izquierda: la cámara mira un poco a la izquierda para centrar la oficina en lo visible
const OVERVIEW: [number, number, number, number, number, number] = [-3, 19, 23, -4, 0, 0]
// En el celular el chat ocupa la mitad de abajo: la cámara sube la oficina a la mitad de arriba
const MOBILE = typeof window !== 'undefined' && window.innerWidth < 768
const OVERVIEW_MOBILE: [number, number, number, number, number, number] = [0, 28, 25, 0, 0, 7]

// Cámara cinematográfica: vista general, o vuelo a la zona que se enfoca
function Director() {
  const controls = useRef<CameraControls>(null)
  const focusZone = useUniverso((s) => s.focusZone)
  const selected = useUniverso((s) => s.selected)
  const started = useUniverso((s) => s.started)

  useEffect(() => {
    const c = controls.current
    if (!c) return
    if (!started) {
      void c.setLookAt(30, 34, 46, 0, 0, 0, false)
      return
    }
    if (focusZone) {
      const [x, z] = ZONES[focusZone].position
      // En el Board, el panel de votos ocupa la parte baja: se mira un poco por delante de la mesa para subirla
      const board = focusZone === 'board'
      const close = board ? 12.5 : 11
      void c.setLookAt(x, close * (board ? 0.95 : 0.85) * (MOBILE ? 1.3 : 1), z + close, x, 0.8, z + (board ? 3.2 : 0) + (MOBILE ? 4 : 0), true)
    } else if (!selected) {
      void c.setLookAt(...(MOBILE ? OVERVIEW_MOBILE : OVERVIEW), true)
    }
  }, [focusZone, selected, started])

  useEffect(() => {
    const c = controls.current
    if (!c || !selected) return
    const agent = AGENTS.find((a) => a.id === selected)
    if (!agent) return
    // Acercarse al agente donde está ahora
    const [x, z] = livePositions.get(selected) ?? agent.home
    void c.setLookAt(x + 3, MOBILE ? 6 : 4.2, z + (MOBILE ? 8 : 6.5), x, 1.3, z + (MOBILE ? 2.5 : 0), true)
  }, [selected])

  return (
    <CameraControls ref={controls} makeDefault minDistance={4} maxDistance={70} maxPolarAngle={Math.PI / 2.15}
      smoothTime={0.6} />
  )
}

export default function World() {
  const select = useUniverso((s) => s.select)
  return (
    <Canvas shadows dpr={[1, 1.75]} camera={{ fov: 40, position: [30, 34, 46], near: 0.1, far: 300 }}
      onPointerMissed={() => select(null)} gl={{ antialias: true, powerPreference: 'high-performance' }}>
      <color attach="background" args={['#0a0a0f']} />
      <fog attach="fog" args={['#0a0a0f', 45, 120]} />
      <ambientLight intensity={0.6} color="#8ab4ff" />
      <hemisphereLight args={['#8aa4ff', '#0a0a1a', 0.8]} />
      <directionalLight position={[14, 26, 12]} intensity={1.3} castShadow shadow-mapSize={[2048, 2048]}
        shadow-camera-left={-26} shadow-camera-right={26} shadow-camera-top={22} shadow-camera-bottom={-22} />
      {Object.values(ZONES).map((z) => (
        <pointLight key={z.id} position={[z.position[0], 3.5, z.position[1]]} color={z.color} intensity={14} distance={11} decay={1.6} />
      ))}
      <Stars radius={120} depth={40} count={2500} factor={4} saturation={0.4} fade speed={0.6} />
      <Office />
      <Zones />
      <Holo />
      {AGENTS.map((a) => (
        <AgentFigure key={a.id} agent={a} />
      ))}
      <Director />
      <EffectComposer multisampling={0}>
        <Bloom mipmapBlur luminanceThreshold={0.9} luminanceSmoothing={0.2} intensity={1.15} />
        <Vignette eskil={false} offset={0.2} darkness={0.75} />
      </EffectComposer>
    </Canvas>
  )
}
