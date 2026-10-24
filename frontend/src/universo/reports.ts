import { cop, type Archetype } from './data'

// Los entregables de cada Nivel (AD-FUNC-01), armados con la empresa de ejemplo. Cada sección depende de una
// tarea del Gate: mientras el agente no la entregue, la sección sale como pendiente (no se inventa evidencia).

export interface ReportSection {
  title: string
  task?: string // id de la tarea del Gate que la respalda; sin tarea = contexto que ya existe
  paragraphs?: string[]
  bullets?: string[]
  table?: { head: string[]; rows: string[][] }
}

export interface Report {
  title: string
  subtitle: string
  sections: ReportSection[]
}

function months(a: Archetype): string[][] {
  const rows: string[][] = []
  let cash = a.capital
  for (const m of [1, 3, 6, 9, 12]) {
    const clients = Math.round(a.clientesMes * Math.min(1, 0.25 + m * 0.07))
    const revenue = clients * a.ticket
    const costs = a.costoFijo + revenue * 0.38
    cash += (revenue - costs) * (m === 1 ? 1 : m <= 3 ? 2 : 3)
    rows.push([`Mes ${m}`, String(clients), cop(revenue), cop(costs), cop(cash)])
  }
  return rows
}

export function buildReport(level: number, a: Archetype, company: string): Report {
  const name = company || a.example
  switch (level) {
    case 1:
      return {
        title: 'Diagnóstico del Dolor', subtitle: `${name} · ${a.sector}`,
        sections: [
          { title: 'El problema', task: 'l1-guion', paragraphs: [a.problema] },
          { title: 'A quién le duele y cuánto le cuesta', task: 'l1-guion', bullets: [`Segmento: ${a.cliente}`,
            `Hoy lo resuelven con: ${a.alternativa}`, `Lo que pierden: ${a.costo}`] },
          { title: 'Evidencia externa (CSI)', task: 'l1-csi', bullets: ['Estudio sectorial con cifras del mercado local',
            'Registro público de empresas del sector en la ciudad', 'Tendencia de búsquedas y conversación en redes'] },
          { title: 'Testimonios de clientes', task: 'l1-entrevistas', bullets: ['5 entrevistas con personas del segmento',
            '4 de 5 confirman el problema con un ejemplo concreto', '1 de 5 no lo siente: se registra como evidencia en contra'] },
          { title: 'Veredicto', task: 'l1-entrevistas', paragraphs: ['GO con confianza media: el dolor existe y se repite. ' +
            'Riesgo principal: confirmar que pagarían por resolverlo (se valida en el Nivel 2).'] },
        ],
      }
    case 2:
      return {
        title: 'Propuesta de Valor', subtitle: `${name} · matriz comparativa`,
        sections: [
          { title: 'La propuesta en una frase', task: 'l2-propuesta', paragraphs: [a.propuesta] },
          { title: 'Diferenciador defendible', task: 'l2-propuesta', paragraphs: [a.diferenciador] },
          { title: 'Matriz comparativa', task: 'l2-competencia', table: { head: ['', name, ...a.competidores],
            rows: [['Resuelve el dolor principal', 'Sí', 'Parcial', 'Parcial', 'No'], ['Precio para el cliente', 'Medio', 'Bajo', 'Medio', 'Alto'],
              ['Cercanía y confianza', 'Alta', 'Baja', 'Alta', 'Media'], ['Disponibilidad', 'Alta', 'Media', 'Baja', 'Alta']] } },
          { title: 'Validación con clientes potenciales', task: 'l2-validacion', bullets: ['8 conversaciones con el segmento',
            '6 de 8 eligen la propuesta frente a su alternativa actual', 'Ajuste: se simplifica la oferta inicial a lo que más valoraron'] },
        ],
      }
    case 3:
      return {
        title: 'Plan de Negocios', subtitle: `${name} · estructura, finanzas y organización`,
        sections: [
          { title: 'Estructura legal y tributaria', task: 'l3-legal', paragraphs: [a.legal],
            bullets: ['Régimen tributario recomendado según los ingresos proyectados', 'Permisos y registros antes de operar'] },
          { title: 'Modelo de ingresos', paragraphs: [`${a.modelo}. Ticket promedio: ${cop(a.ticket)}.`] },
          { title: 'Proyección a 12 meses (contrastada con el sector)', task: 'l3-finanzas', table: {
            head: ['Periodo', 'Clientes', 'Ingresos', 'Costos', 'Caja acumulada'], rows: months(a) } },
          { title: 'Capital necesario', task: 'l3-modelo', paragraphs: [`${cop(a.capital)} para operar 12 meses con un margen de seguridad del 25 %.`] },
          { title: 'Organigrama híbrido', task: 'l3-organigrama', bullets: [...a.roles.humanos.map((r) => `Persona: ${r}`),
            ...a.roles.agentes.map((r) => `Agente de IA: ${r}`)] },
        ],
      }
    case 4:
      return {
        title: 'Blueprint del MVP', subtitle: `${name} · qué se construye y qué no`,
        sections: [
          { title: 'El MVP', task: 'l4-alcance', paragraphs: [a.mvp] },
          { title: 'Entra en el MVP', task: 'l4-alcance', bullets: a.mvpIncluye },
          { title: 'Queda por fuera (a propósito)', task: 'l4-alcance', bullets: a.mvpExcluye },
          { title: 'Blueprint y flujo del cliente', task: 'l4-blueprint', bullets: ['El cliente descubre la oferta', 'Pide o reserva en menos de 2 minutos',
            'Recibe el servicio y confirma', 'Deja su opinión: se registra como evidencia'] },
          { title: 'Roadmap de construcción', task: 'l4-construir', table: { head: ['Semana', 'Entrega'],
            rows: [['1', 'Montaje y pruebas internas'], ['2', 'Primeros 5 clientes de prueba'], ['3', 'Ajustes por lo aprendido'], ['4', 'MVP listo para la simulación']] } },
        ],
      }
    case 5:
      return {
        title: 'Informe de Validación Simulada', subtitle: `${name} · clientes, competencia e inversionistas simulados`,
        sections: [
          { title: 'Clientes simulados', task: 'l5-clientes', table: { head: ['Métrica', 'Resultado', 'Umbral'],
            rows: [['Conversión de visita a compra', '6,8 %', '≥ 5 %'], ['Recompra a 30 días', '41 %', '≥ 30 %'], ['Objeción principal', 'Precio de entrada', '—']] } },
          { title: 'Reacción de la competencia', task: 'l5-competidor', paragraphs: [`Escenario: ${a.competidores[0]} baja precios un 15 %. ` +
            'El diferenciador resiste en el segmento objetivo, con caída de conversión de 6,8 % a 5,4 %.'] },
          { title: 'Inversionistas simulados', task: 'l5-inversionista', bullets: ['¿Cuál es el costo de adquirir un cliente? Respondido con datos del MVP',
            '¿Qué pasa si se duplica la demanda? Ver cuello de botella del Nivel 7', '¿Por qué ustedes? Diferenciador validado en el Nivel 2'] },
          { title: 'Plan de ajuste', task: 'l5-clientes', bullets: ['Oferta de entrada más barata para bajar la objeción de precio',
            'Mensaje centrado en el diferenciador', 'Riesgos registrados en el Gemelo Digital'] },
        ],
      }
    case 6:
      return {
        title: 'Primer ciclo de operación', subtitle: `${name} · el mundo real`,
        sections: [
          { title: 'Lanzamiento', task: 'l6-lanzar', paragraphs: [`Canal principal: ${a.canal}. Campaña operada con EVA.`] },
          { title: 'Primer cliente real', task: 'l6-venta', paragraphs: [`${a.primerCliente}: primera venta verificada por ${cop(a.ticket)}.`] },
          { title: 'Ingresos y gastos del primer mes', task: 'l6-ciclo', table: { head: ['Concepto', 'Valor'],
            rows: [['Ingresos', cop(a.ticket * Math.round(a.clientesMes * 0.3))], ['Costos fijos', cop(a.costoFijo)], ['Clientes', String(Math.round(a.clientesMes * 0.3))]] } },
          { title: 'Lecciones del ciclo', task: 'l6-ciclo', bullets: ['Lo que el cliente valoró más de lo esperado', 'El paso del proceso que más se demoró',
            'La empresa pasa de "validada" a "operando" en el Gemelo Digital'] },
        ],
      }
    default:
      return {
        title: 'Diagnóstico de Escalamiento', subtitle: `${name} · crecer sin romperse`,
        sections: [
          { title: 'Cuello de botella', task: 'l7-cuello', paragraphs: [a.cuelloBotella] },
          { title: 'Velocidad de maduración', paragraphs: ['Se compara la empresa consigo misma en el tiempo, nunca con otras empresas: ' +
            'meses entre Niveles, decisiones ejecutadas y procesos formalizados.'] },
          { title: 'Opciones de capital', task: 'l7-capital', table: { head: ['Opción', 'Ventaja', 'Costo'],
            rows: [['Caja propia', 'Control total', 'Crecimiento más lento'], ['Crédito', 'Rápido, sin ceder empresa', 'Intereses y garantías'],
              ['Socio o inversionista', 'Capital y red', 'Ceder participación']] } },
          { title: 'Plan de escalamiento', task: 'l7-plan', paragraphs: [a.escala],
            bullets: ['Nuevos cargos y agentes para el cuello de botella', 'Indicadores de seguimiento continuo', 'Revisión con el Board cada trimestre'] },
        ],
      }
  }
}
