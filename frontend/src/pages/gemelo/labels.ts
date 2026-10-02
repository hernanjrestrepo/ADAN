import type { Tone } from '../../components/ui/Badge'
import type { DecisionStatus, TimelineEvent } from '../../types'

export const DECISION_STATUS: Record<DecisionStatus, { label: string; tone: Tone }> = {
  proposed: { label: 'Propuesta', tone: 'yellow' },
  presented: { label: 'Presentada', tone: 'blue' },
  approved: { label: 'Aprobada', tone: 'green' },
  rejected: { label: 'Rechazada', tone: 'red' },
  executed: { label: 'Ejecutada', tone: 'gray' },
}

export const EVIDENCE_TONE: Record<string, Tone> = { alta: 'green', media: 'yellow', baja: 'red' }

// Textos del Timeline (AD-UX-08)
const STATE_LABELS: Record<string, string> = {
  proposed: 'propuesta', presented: 'presentada', approved: 'aprobada', rejected: 'rechazada',
  executed: 'ejecutada', blocked: 'bloqueado', active: 'activo', completed: 'completado', paused: 'pausado',
  archived: 'archivado',
}

const ENTITY_LABELS: Record<string, string> = {
  decisions: 'Decisión', levels: 'Nivel', cards: 'Card', companies: 'Empresa', projects: 'Proyecto',
  initiatives: 'Iniciativa', business_decisions: 'Decisión de Negocio', business_contracts: 'Contrato',
  brands: 'Marca', shareholders: 'Accionista', departments: 'Departamento', positions: 'Cargo',
  functional_roles: 'Rol Funcional', employees: 'Empleado', end_customers: 'Cliente Final',
  offerings: 'Producto o Servicio', markets: 'Mercado', competitors: 'Competidor', suppliers: 'Proveedor',
  processes: 'Proceso', business_occurrences: 'Suceso Empresarial', objectives: 'Objetivo', goals: 'Meta',
  indicators: 'Indicador', assets: 'Activo', liabilities: 'Pasivo', revenues: 'Ingreso', expenses: 'Gasto',
  twin_risks: 'Riesgo', tasks: 'Tarea', workspaces: 'Workspace', document: 'Documento', documents: 'Documento',
  decision: 'Decisión', level: 'Nivel', evidence: 'Evidencia', scores: 'Score',
}

export const ACTOR_LABELS: Record<string, string> = { user: 'Tú', agent: 'Agente', system: 'ADÁN' }

export function describeEvent(e: TimelineEvent): string {
  const entity = ENTITY_LABELS[e.entity_type] ?? e.entity_type
  const label = e.data.label ? ` «${e.data.label}»` : ''
  switch (e.event_type) {
    case 'state_changed':
      return `${entity}${label}: ${STATE_LABELS[e.data.from ?? ''] ?? e.data.from} → ${STATE_LABELS[e.data.to ?? ''] ?? e.data.to}`
    case 'entity_created':
      return `Se registró ${entity}${label}`
    case 'entity_archived':
      return `Se archivó ${entity}${label}`
    case 'entity_restored':
      return `Se restauró ${entity}${label}`
    case 'twin_born':
      return `Nació el Gemelo Digital${label}`
    case 'twin_reinvented':
      return `Reinvención: cambió la Narrativa Fundacional`
    case 'twin_split':
      return `Una Iniciativa se separó como Empresa nueva`
    case 'twin_archived':
      return `Se archivó el Gemelo${label}`
    case 'twin_paused':
      return `Se pausó el Gemelo`
    case 'twin_resumed':
      return `Se reanudó el Gemelo`
    case 'board_room_completed':
      return 'Sesión del Board Room'
    case 'diagnosis_saved':
      return 'Se guardó el diagnóstico'
    case 'level_completed':
      return 'Se completó un Nivel'
    case 'level_completion_proposed':
      return 'El Gate Review propuso cerrar el Nivel'
    case 'score_calculated': {
      const value = typeof e.data.value === 'number' ? Math.round(e.data.value) : '—'
      const confidence = typeof e.data.confidence === 'number' ? Math.round(e.data.confidence) : '—'
      return `${e.data.label ?? 'Score'}: ${value}/100 con ${confidence} % de confianza`
    }
    default:
      return `${e.event_type.replaceAll('_', ' ')}${label}`
  }
}
