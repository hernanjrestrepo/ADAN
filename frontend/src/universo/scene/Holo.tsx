import { Html } from '@react-three/drei'
import { Chart } from '../../components/RichMessage'
import { ZONES } from '../data'
import { useUniverso } from '../store'

// Lo que ADAN muestra en la conversación (gráficos, proyecciones) aparece también en una pantalla de la oficina
export default function Holo() {
  const holo = useUniverso((s) => s.holo)
  const close = useUniverso((s) => s.showHolo)
  if (!holo) return null
  const [x, z] = ZONES.gemelo.position
  return (
    <Html position={[x, 4.6, z - 1]} center distanceFactor={13} zIndexRange={[15, 0]}>
      <div className="u-holo-screen">
        <button type="button" onClick={() => close(null)} aria-label="Cerrar la pantalla" className="u-holo-close">×</button>
        <Chart spec={holo} compact />
      </div>
    </Html>
  )
}
