import { useEffect, useMemo, useRef, type RefObject } from 'react'
import { Color, type Group, type Mesh } from 'three'
import { type Look } from '../data'
import { type Rig } from './rig'

// El cuerpo humano de cada personaje: piel, pelo, ropa (traje, falda o vestido), barba, bigote, gafas y una cara
// que cambia con el ánimo. Lo comparten el equipo de ADÁN y los inversionistas de La Arena.

function tint(color: string, to: string, t: number): string {
  return '#' + new Color(color).lerp(new Color(to), t).getHexString()
}

function Hair({ look }: { look: Look }) {
  if (look.hair === 'calvo') return null
  const m = <meshStandardMaterial color={look.hairColor} roughness={0.75} />
  return (
    <group>
      {/* Gorro de pelo inclinado hacia atrás: deja ver la frente */}
      <mesh rotation-x={-0.3} castShadow>
        <sphereGeometry args={[0.215, 24, 16, 0, Math.PI * 2, 0, 1.3]} />
        {m}
      </mesh>
      {look.hair === 'largo' && (
        <mesh position={[0, -0.2, -0.09]} castShadow>
          <capsuleGeometry args={[0.17, 0.32, 4, 12]} />
          {m}
        </mesh>
      )}
      {look.hair === 'mono' && (
        <mesh position={[0, 0.16, -0.15]} castShadow>
          <sphereGeometry args={[0.095, 14, 14]} />
          {m}
        </mesh>
      )}
      {look.hair === 'rizado' && [0, 1, 2, 3, 4, 5, 6, 7].map((i) => {
        const a = (i / 8) * Math.PI * 2
        return (
          <mesh key={i} position={[Math.cos(a) * 0.17, 0.1 + (i % 2) * 0.05, Math.sin(a) * 0.15 - 0.03]}>
            <sphereGeometry args={[0.075, 10, 10]} />
            {m}
          </mesh>
        )
      })}
    </group>
  )
}

type FaceRefs = Record<'browL' | 'browR' | 'smile' | 'frown' | 'laugh', RefObject<Mesh | null>>

function Face({ look, color, faceRefs }: { look: Look; color: string; faceRefs: FaceRefs }) {
  const { browL, browR, smile, frown, laugh } = faceRefs
  const dark = '#1f1611'
  return (
    <group>
      {[-0.07, 0.07].map((x) => (
        <mesh key={x} position={[x, 0.035, 0.18]}>
          <sphereGeometry args={[0.024, 10, 10]} />
          <meshStandardMaterial color={dark} roughness={0.3} />
        </mesh>
      ))}
      <mesh ref={browL} position={[-0.07, 0.085, 0.188]}>
        <boxGeometry args={[0.065, 0.014, 0.012]} />
        <meshStandardMaterial color={look.hair === 'calvo' ? '#3b2a20' : look.hairColor} />
      </mesh>
      <mesh ref={browR} position={[0.07, 0.085, 0.188]}>
        <boxGeometry args={[0.065, 0.014, 0.012]} />
        <meshStandardMaterial color={look.hair === 'calvo' ? '#3b2a20' : look.hairColor} />
      </mesh>
      {/* Boca: sonrisa, preocupación o carcajada */}
      <mesh ref={smile} position={[0, -0.055, 0.196]} rotation-z={Math.PI}>
        <torusGeometry args={[0.05, 0.011, 6, 16, Math.PI]} />
        <meshStandardMaterial color="#7f1d1d" />
      </mesh>
      <mesh ref={frown} position={[0, -0.09, 0.19]} visible={false}>
        <torusGeometry args={[0.042, 0.011, 6, 16, Math.PI]} />
        <meshStandardMaterial color="#7f1d1d" />
      </mesh>
      <mesh ref={laugh} position={[0, -0.075, 0.185]} scale={[1, 0.7, 0.5]} visible={false}>
        <sphereGeometry args={[0.045, 12, 12]} />
        <meshStandardMaterial color="#450a0a" />
      </mesh>
      {look.beard && (
        <mesh position={[0, 0, 0.006]}>
          <sphereGeometry args={[0.212, 24, 12, 0.15, Math.PI - 0.3, Math.PI / 2 + 0.35, 1.0]} />
          <meshStandardMaterial color={look.hairColor} roughness={0.85} />
        </mesh>
      )}
      {look.mustache && (
        <mesh position={[0, -0.03, 0.205]}>
          <boxGeometry args={[0.11, 0.024, 0.02]} />
          <meshStandardMaterial color={look.hairColor} roughness={0.8} />
        </mesh>
      )}
      {look.glasses && (
        <group position={[0, 0.035, 0.2]}>
          {[-0.07, 0.07].map((x) => (
            <mesh key={x} position-x={x}>
              <torusGeometry args={[0.043, 0.008, 6, 20]} />
              <meshStandardMaterial color={color} emissive={color} emissiveIntensity={1.4} toneMapped={false} />
            </mesh>
          ))}
          <mesh>
            <boxGeometry args={[0.055, 0.008, 0.008]} />
            <meshStandardMaterial color={color} emissive={color} emissiveIntensity={1.4} toneMapped={false} />
          </mesh>
        </group>
      )}
    </group>
  )
}

// Pierna: pantalón del traje, o piel con zapato si lleva falda o vestido
function Leg({ legRef, x, cloth, look }: { legRef: RefObject<Group | null>; x: number; cloth: string; look: Look }) {
  const skirt = look.outfit !== 'traje'
  return (
    <group ref={legRef} position={[x, 0.78, 0]}>
      <mesh position-y={-0.38} castShadow>
        <capsuleGeometry args={[skirt ? 0.065 : 0.085, 0.55, 4, 10]} />
        <meshStandardMaterial color={skirt ? look.skin : cloth} roughness={skirt ? 0.6 : 0.5} metalness={skirt ? 0 : 0.3} />
      </mesh>
      <mesh position={[0, -0.72, 0.05]} castShadow>
        <boxGeometry args={[0.13, 0.08, 0.24]} />
        <meshStandardMaterial color="#0f172a" metalness={0.5} roughness={0.3} />
      </mesh>
    </group>
  )
}

function Arm({ armRef, x, sleeve, look }: { armRef: RefObject<Group | null>; x: number; sleeve: string; look: Look }) {
  return (
    <group ref={armRef} position={[x, 1.42, 0]}>
      <mesh position-y={-0.25} castShadow>
        <capsuleGeometry args={[0.062, 0.38, 4, 10]} />
        <meshStandardMaterial color={sleeve} roughness={0.5} metalness={0.2} />
      </mesh>
      <mesh position-y={-0.52}>
        <sphereGeometry args={[0.068, 12, 12]} />
        <meshStandardMaterial color={look.skin} roughness={0.6} />
      </mesh>
    </group>
  )
}

// `rigRef` recibe las piezas animables cuando el cuerpo se monta; la escena las mueve en cada cuadro
export function PersonBody({ rigRef, look, color }: { rigRef: RefObject<Rig | null>; look: Look; color: string }) {
  const body = useRef<Group>(null)
  const head = useRef<Group>(null)
  const legL = useRef<Group>(null)
  const legR = useRef<Group>(null)
  const armL = useRef<Group>(null)
  const armR = useRef<Group>(null)
  const browL = useRef<Mesh>(null)
  const browR = useRef<Mesh>(null)
  const smile = useRef<Mesh>(null)
  const frown = useRef<Mesh>(null)
  const laugh = useRef<Mesh>(null)
  useEffect(() => {
    rigRef.current = {
      body: body.current, head: head.current, legL: legL.current, legR: legR.current, armL: armL.current, armR: armR.current,
      browL: browL.current, browR: browR.current, smile: smile.current, frown: frown.current, laugh: laugh.current,
    }
    return () => { rigRef.current = null }
  }, [rigRef])
  // El color del rol tiñe la ropa: se distingue a cada quien desde lejos
  const suit = useMemo(() => tint(color, '#1e293b', 0.62), [color])
  const blouse = useMemo(() => tint(color, '#f8fafc', 0.55), [color])
  const dress = useMemo(() => tint(color, '#1e1b4b', 0.25), [color])
  const top = look.outfit === 'traje' ? suit : look.outfit === 'falda' ? blouse : dress
  return (
    <group ref={body}>
      <Leg legRef={legL} x={-0.11} cloth={suit} look={look} />
      <Leg legRef={legR} x={0.11} cloth={suit} look={look} />
      {/* Torso */}
      <mesh position-y={1.16} castShadow>
        <capsuleGeometry args={[0.23, 0.4, 6, 16]} />
        <meshStandardMaterial color={top} roughness={0.45} metalness={look.outfit === 'traje' ? 0.35 : 0.05} />
      </mesh>
      {look.outfit === 'traje' && (
        <>
          <mesh position={[0, 1.3, 0.205]} rotation-x={-0.12}>
            <boxGeometry args={[0.13, 0.26, 0.02]} />
            <meshStandardMaterial color="#e2e8f0" />
          </mesh>
          <mesh position={[0, 1.24, 0.222]} rotation-x={-0.12}>
            <boxGeometry args={[0.045, 0.24, 0.012]} />
            <meshStandardMaterial color={color} emissive={color} emissiveIntensity={1.6} toneMapped={false} />
          </mesh>
        </>
      )}
      {look.outfit === 'falda' && (
        <mesh position-y={0.82} castShadow>
          <cylinderGeometry args={[0.24, 0.34, 0.4, 24]} />
          <meshStandardMaterial color={suit} roughness={0.45} emissive={color} emissiveIntensity={0.08} />
        </mesh>
      )}
      {look.outfit === 'vestido' && (
        <mesh position-y={0.78} castShadow>
          <cylinderGeometry args={[0.24, 0.4, 0.52, 28]} />
          <meshStandardMaterial color={dress} roughness={0.4} emissive={color} emissiveIntensity={0.1} />
        </mesh>
      )}
      {/* Cinturón de neón: el toque futurista de la oficina */}
      <mesh position-y={0.97} rotation-x={Math.PI / 2}>
        <torusGeometry args={[0.24, 0.018, 8, 32]} />
        <meshStandardMaterial color={color} emissive={color} emissiveIntensity={2.2} toneMapped={false} />
      </mesh>
      <Arm armRef={armL} x={-0.31} sleeve={top} look={look} />
      <Arm armRef={armR} x={0.31} sleeve={top} look={look} />
      <mesh position-y={1.6}>
        <cylinderGeometry args={[0.07, 0.08, 0.12, 12]} />
        <meshStandardMaterial color={look.skin} roughness={0.6} />
      </mesh>
      <group ref={head} position-y={1.82}>
        <mesh castShadow>
          <sphereGeometry args={[0.2, 28, 28]} />
          <meshStandardMaterial color={look.skin} roughness={0.55} />
        </mesh>
        {[-0.2, 0.2].map((x) => (
          <mesh key={x} position={[x, 0, 0]}>
            <sphereGeometry args={[0.04, 10, 10]} />
            <meshStandardMaterial color={look.skin} roughness={0.6} />
          </mesh>
        ))}
        <Hair look={look} />
        <Face look={look} color={color} faceRefs={{ browL, browR, smile, frown, laugh }} />
      </group>
    </group>
  )
}
