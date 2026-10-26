import { CameraControls, Sparkles, Stars } from '@react-three/drei'
import { Canvas } from '@react-three/fiber'
import { Bloom, EffectComposer, Vignette } from '@react-three/postprocessing'
import { useEffect, useRef } from 'react'
import { AGENTS, ZONES } from '../data'
import { useUniverso } from '../store'
import AgentFigure from './AgentFigure'
import LevelDecor from './Floors'
import { themeOf, type Identity } from './pisos'
import Holo from './Holo'
import { STAGE, livePositions } from './layout'
import Office from './Office'
import Zones from './Zones'

// El panel de misión ocupa la izquierda: la cámara mira un poco a la izquierda para centrar la oficina en lo visible
const OVERVIEW: [number, number, number, number, number, number] = [-3, 19, 23, -4, 0, 0]
// En el celular el chat ocupa la mitad de abajo: la cámara sube la oficina a la mitad de arriba
const MOBILE = typeof window !== 'undefined' && window.innerWidth < 768
const OVERVIEW_MOBILE: [number, number, number, number, number, number] = [0, 28, 25, 0, 0, 7]

// Cámara cinematográfica: vista general, o vuelo a la zona que se enfoca
function Director({ embedded = false }: { embedded?: boolean }) {
  const controls = useRef<CameraControls>(null)
  const focusZone = useUniverso((s) => s.focusZone)
  const selected = useUniverso((s) => s.selected)
  const started = useUniverso((s) => s.started) || embedded
  const cam = useUniverso((s) => s.cam)
  const onStage = useUniverso((s) => s.stage?.agent ?? null)

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

  // Botones de la cámara: acercar, alejar o volver a la vista general
  useEffect(() => {
    const c = controls.current
    if (!c || cam.n === 0) return
    if (cam.op === 'in') void c.dolly(4, true)
    else if (cam.op === 'out') void c.dolly(-4, true)
    else void c.setLookAt(...(MOBILE ? OVERVIEW_MOBILE : OVERVIEW), true)
  }, [cam])

  // Quien habla pasa al frente: la cámara lo encuadra de cerca, y al terminar vuelve a la vista general
  useEffect(() => {
    const c = controls.current
    if (!c || !started) return
    const [x, z] = STAGE
    if (onStage) void c.setLookAt(x + 1.2, MOBILE ? 5.5 : 4.2, z + (MOBILE ? 9 : 7.5), x, 1.5, z + (MOBILE ? 2 : 0), true)
    else if (!focusZone && !selected) void c.setLookAt(...(MOBILE ? OVERVIEW_MOBILE : OVERVIEW), true)
  }, [onStage, started, focusZone, selected])

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

export default function World({ embedded = false, floor, identity = null }: { embedded?: boolean; floor?: number; identity?: Identity | null }) {
  const select = useUniverso((s) => s.select)
  const level = useUniverso((s) => s.level)
  // En la Sala cada piso tiene su ambiente; el Universo conserva el suyo de siempre
  const theme = floor ? themeOf(floor) : undefined
  return (
    <Canvas shadows dpr={[1, 1.75]} camera={{ fov: 40, position: [30, 34, 46], near: 0.1, far: 300 }}
      onPointerMissed={() => select(null)} gl={{ antialias: true, powerPreference: 'high-performance' }}>
      <color attach="background" args={[theme ? theme.sky : '#0a0a0f']} />
      <fog attach="fog" args={[theme ? theme.sky : '#0a0a0f', 45, 120]} />
      <ambientLight intensity={theme ? 0.75 : 0.6} color={theme?.ambient ?? '#8ab4ff'} />
      <hemisphereLight args={[theme?.ambient ?? '#8aa4ff', '#0a0a1a', 0.8]} />
      <directionalLight position={[14, 26, 12]} intensity={1.3} castShadow shadow-mapSize={[2048, 2048]}
        shadow-camera-left={-26} shadow-camera-right={26} shadow-camera-top={22} shadow-camera-bottom={-22} />
      {Object.values(ZONES).map((z) => (
        <pointLight key={z.id} position={[z.position[0], 3.5, z.position[1]]} color={z.color} intensity={14} distance={11} decay={1.6} />
      ))}
      {(!theme || theme.stars) && <Stars radius={120} depth={40} count={2500} factor={4} saturation={0.4} fade speed={0.6} />}
      {theme?.particles && <Sparkles count={120} scale={[44, 8, 36]} position={[0, 4, 0]} size={4} speed={0.4} color={theme.particles} />}
      <Office theme={theme} />
      <LevelDecor floor={floor ?? level} identity={identity} />
      <Zones />
      <Holo />
      {AGENTS.map((a) => (
        <AgentFigure key={a.id} agent={a} />
      ))}
      <Director embedded={embedded} />
      <EffectComposer multisampling={0}>
        <Bloom mipmapBlur luminanceThreshold={0.9} luminanceSmoothing={0.2} intensity={1.15} />
        <Vignette eskil={false} offset={0.2} darkness={0.75} />
      </EffectComposer>
    </Canvas>
  )
}
