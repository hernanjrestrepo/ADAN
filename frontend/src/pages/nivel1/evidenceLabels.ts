import type { Tone } from '../../components/ui/Badge'
import type { EvidenceKind } from '../../types'

// Jerarquía de validez de AD-CMP-05 §1, en lenguaje del cliente
export const KIND: Record<EvidenceKind, { label: string; short: string; tone: Tone; hint: string }> = {
  external: { label: 'Dato verificable', short: 'datos', tone: 'green',
    hint: 'Un estudio, una estadística, un registro público o un documento' },
  testimony: { label: 'Testimonio', short: 'testimonios', tone: 'blue',
    hint: 'Lo que tú o tus clientes declaran directamente' },
  inference: { label: 'Inferencia de un Agente', short: 'inferencias', tone: 'gray',
    hint: 'Lo que concluyó el Board; nunca basta por sí sola' },
}
