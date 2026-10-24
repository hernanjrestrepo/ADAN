// Universo ADÁN: el contenido del recorrido. Fuente: AD-FUNC-01 (7 Niveles), AD-FUNC-02 (Board Room),
// AD-FUNC-03/04 (emoción y ritmo de cada Nivel), AD-FUNC-07 (Scores) y AD-000 v2.0 (ecosistema).
// Todo lo que aparece de una empresa es un EJEMPLO ILUSTRATIVO: en ADÁN real sale de la evidencia del cliente.

export type ZoneId = 'board' | 'csi' | 'memoria' | 'genexis' | 'simulador' | 'gemelo' | 'eva' | 'mercado'
export type AgentId =
  | 'ceo' | 'cto' | 'cfo' | 'cmo' | 'legal' | 'producto' | 'operaciones'
  | 'csi' | 'genexis' | 'eva' | 'investigador' | 'analista'

export interface Zone {
  id: ZoneId
  name: string
  short: string
  description: string
  position: [number, number]
  color: string
}

export const ZONES: Record<ZoneId, Zone> = {
  board: { id: 'board', name: 'Sala de Juntas', short: 'Board Room', position: [0, -4], color: '#60a5fa',
    description: 'El CEO preside y seis especialistas votan. Toda decisión importante la aprueba el cliente.' },
  csi: { id: 'csi', name: 'Radar CSI', short: 'Inteligencia externa', position: [-14, -9], color: '#22d3ee',
    description: 'Mercado, competencia, regulación y tendencias: valida el dolor y la propuesta con fuentes externas.' },
  memoria: { id: 'memoria', name: 'Memoria Empresarial', short: 'EMS · 5 capas', position: [0, -13], color: '#a78bfa',
    description: 'Lo que ADÁN sabe de cada empresa, en cinco capas. Nunca vuelve a preguntar lo que ya sabe.' },
  genexis: { id: 'genexis', name: 'Laboratorio Genexis', short: 'Construcción', position: [14, -9], color: '#f472b6',
    description: 'El motor interno que construye el MVP: software, piloto físico o servicio, según la empresa.' },
  simulador: { id: 'simulador', name: 'Simulador de Mercado', short: 'Clientes simulados', position: [-14, 7], color: '#fbbf24',
    description: 'Clientes, competidores e inversionistas simulados prueban el modelo antes de arriesgar capital real.' },
  gemelo: { id: 'gemelo', name: 'Gemelo Digital', short: 'Tu empresa', position: [0, 6], color: '#34d399',
    description: 'La empresa con historia completa: cada decisión, versión y evento queda registrado para siempre.' },
  eva: { id: 'eva', name: 'Estudio EVA', short: 'Ventas y voz', position: [14, 7], color: '#fb923c',
    description: 'Ventas y marketing con IA: campañas, voz y agentes conversacionales cuando la empresa sale al mercado.' },
  mercado: { id: 'mercado', name: 'Marketplace y Comunidad', short: 'Agentes por tiempo', position: [0, 14], color: '#c084fc',
    description: 'Agentes por hora, día, semana o mes, y la red de empresas del ecosistema Paradixe.' },
}

export interface Agent {
  id: AgentId
  name: string
  role: string
  title: string
  color: string
  home: [number, number]
  seat?: number // puesto en la mesa del Board (0 = cabecera)
  focus: string
  board: boolean
  hello: string
}

export const AGENTS: Agent[] = [
  { id: 'ceo', name: 'Valeria', role: 'CEO', title: 'CEO Agent · preside el Board', color: '#60a5fa', home: [-3, 1.5], seat: 0,
    board: true, focus: 'Abre y cierra cada sesión, da la voz de ADÁN y nunca decide por ti.',
    hello: 'Soy Valeria. Presido el Board: abro con el objetivo, escucho a todos y te traigo una recomendación. Tú decides.' },
  { id: 'cto', name: 'Mateo', role: 'CTO', title: 'Viabilidad técnica', color: '#38bdf8', home: [-8, -6], seat: 1,
    board: true, focus: 'Factibilidad, arquitectura y riesgos tecnológicos.',
    hello: 'Soy Mateo. Miro si lo que quieres construir se puede construir, con qué y a qué riesgo.' },
  { id: 'cfo', name: 'Camila', role: 'CFO', title: 'Viabilidad financiera', color: '#4ade80', home: [-8, -2], seat: 2,
    board: true, focus: 'Costos, ingresos, caja y sostenibilidad, contrastados con benchmarks de CSI.',
    hello: 'Soy Camila. Mis números se contrastan con datos reales del sector: nada de soñar con cifras que no son.' },
  { id: 'cmo', name: 'Santiago', role: 'CMO', title: 'Mercado', color: '#f97316', home: [-8, 2], seat: 3,
    board: true, focus: 'Dolor real, demanda, diferenciación y canales.',
    hello: 'Soy Santiago. Me obsesiona una pregunta: ¿a quién le duele y cómo llegamos a esa persona?' },
  { id: 'legal', name: 'Lucía', role: 'Legal', title: 'Riesgos legales', color: '#e879f9', home: [8, -6], seat: 4,
    board: true, focus: 'Regulación, contratos, propiedad intelectual y datos personales.',
    hello: 'Soy Lucía. Te ayudo a ver los riesgos legales a tiempo. Ojo: soy una IA, no reemplazo a tu abogado.' },
  { id: 'producto', name: 'Andrés', role: 'Producto', title: 'Problema–solución', color: '#facc15', home: [8, -2], seat: 5,
    board: true, focus: 'Usuario, alcance del MVP y experiencia.',
    hello: 'Soy Andrés. Cuido que lo que se construya resuelva el dolor validado, y nada más de lo necesario.' },
  { id: 'operaciones', name: 'Sofía', role: 'Operaciones', title: 'Capacidad de ejecutar', color: '#2dd4bf', home: [8, 2], seat: 6,
    board: true, focus: 'Procesos, recursos, proveedores y capacidad real de operar.',
    hello: 'Soy Sofía. Pregunto lo incómodo: ¿quién hace qué, con qué recursos y cuándo?' },
  { id: 'csi', name: 'Orión', role: 'CSI', title: 'Inteligencia externa', color: '#22d3ee', home: [-14, -7], board: false,
    focus: 'Trae datos del mundo: estudios, cifras públicas, competencia y regulación.',
    hello: 'Soy Orión, del Radar CSI. Si algo se afirma sobre el mercado, busco la fuente.' },
  { id: 'genexis', name: 'Forja', role: 'Genexis', title: 'Constructor del MVP', color: '#f472b6', home: [14, -7], board: false,
    focus: 'Construye el MVP aprobado. Nunca empieza sin tu aprobación del blueprint.',
    hello: 'Soy Forja, de Genexis. Construyo lo que apruebas en el Nivel 4: ni una línea antes.' },
  { id: 'eva', name: 'Eva', role: 'EVA', title: 'Ventas y voz', color: '#fb923c', home: [14, 9], board: false,
    focus: 'Lleva el producto al mercado: campañas, voz y omnicanalidad.',
    hello: 'Soy Eva. Cuando tu empresa sale al mercado, yo la ayudo a vender en todos los canales.' },
  { id: 'investigador', name: 'Iris', role: 'Agente por hora', title: 'Investigadora de mercado', color: '#c084fc', home: [-3, 14], board: false,
    focus: 'Agente por tiempo: entrevistas, encuestas y análisis de competencia.',
    hello: 'Soy Iris, agente por hora del Marketplace. Me contratas para una tarea y entrego con evidencia.' },
  { id: 'analista', name: 'Teo', role: 'Agente por día', title: 'Analista financiero', color: '#a3e635', home: [3, 14], board: false,
    focus: 'Agente por tiempo: modelos financieros, flujo de caja y conciliaciones.',
    hello: 'Soy Teo, agente por día. Armo modelos financieros y tú apruebas la entrega antes de usarla.' },
]

export const AGENT_BY_ID = Object.fromEntries(AGENTS.map((a) => [a.id, a])) as Record<AgentId, Agent>

// ---------------------------------------------------------------- Empresas de ejemplo (cualquier sector)

export interface Archetype {
  id: string
  label: string
  sector: string
  icon: string
  example: string
  problema: string
  cliente: string
  alternativa: string
  costo: string
  propuesta: string
  diferenciador: string
  competidores: [string, string, string]
  modelo: string
  ticket: number
  clientesMes: number
  costoFijo: number
  capital: number
  legal: string
  roles: { humanos: string[]; agentes: string[] }
  mvp: string
  mvpIncluye: string[]
  mvpExcluye: string[]
  canal: string
  primerCliente: string
  cuelloBotella: string
  escala: string
}

export const ARCHETYPES: Archetype[] = [
  {
    id: 'panaderia', label: 'Panadería artesanal', sector: 'Alimentos y comercio', icon: '🥐', example: 'Masa Madre del Barrio',
    problema: 'Las familias del barrio no consiguen pan fresco de calidad antes de las 7 a. m. y terminan comprando pan industrial.',
    cliente: 'Familias y oficinas a menos de 2 km, que desayunan entre 6 y 8 a. m.',
    alternativa: 'Supermercado (pan del día anterior) o panaderías que abren a las 8 a. m.',
    costo: 'Desayunos de menor calidad y 20 minutos de desplazamiento diario.',
    propuesta: 'Pan de masa madre recién horneado en tu puerta a las 6:30 a. m., por suscripción semanal.',
    diferenciador: 'Entrega antes de las 7 a. m. y horneado en el barrio: nadie más lo hace en la zona.',
    competidores: ['Supermercado de cadena', 'Panadería tradicional', 'App de domicilios'],
    modelo: 'Suscripción semanal + venta en mostrador', ticket: 85000, clientesMes: 120, costoFijo: 6500000, capital: 38000000,
    legal: 'S.A.S. con registro sanitario INVIMA y concepto de uso de suelo',
    roles: { humanos: ['Maestro panadero', 'Ayudante de horno', 'Repartidor'], agentes: ['Pedidos por WhatsApp', 'Inventario de insumos', 'Facturación'] },
    mvp: 'Piloto de 4 semanas con 3 panes, 40 suscriptores y una sola ruta de entrega',
    mvpIncluye: ['Menú de 3 panes', 'Pedidos por WhatsApp', 'Una ruta de reparto', 'Pago por transferencia'],
    mvpExcluye: ['Local propio', 'Repostería', 'App móvil'],
    canal: 'Grupos de WhatsApp del conjunto y degustaciones en portería', primerCliente: 'Conjunto residencial Los Almendros (32 familias)',
    cuelloBotella: 'Un solo horno y un solo maestro panadero: la producción no pasa de 300 panes al día.',
    escala: 'Segunda cocina central y tres rutas nuevas, o franquicia del modelo de suscripción.',
  },
  {
    id: 'veterinaria', label: 'Clínica veterinaria', sector: 'Salud animal y servicios', icon: '🐾', example: 'Huellitas 24/7',
    problema: 'Los dueños de mascotas no tienen atención veterinaria confiable de noche ni seguimiento después de la consulta.',
    cliente: 'Hogares con perros o gatos en la ciudad, de 25 a 50 años, que tratan a su mascota como familia.',
    alternativa: 'Urgencias lejanas y costosas, o consultar en grupos de Facebook.',
    costo: 'Hasta COP 600.000 por una urgencia nocturna y riesgo real para la mascota.',
    propuesta: 'Consulta 24/7 con triaje por chat y plan de salud mensual con recordatorios.',
    diferenciador: 'Triaje inmediato a cualquier hora y historia clínica compartida con el dueño.',
    competidores: ['Clínica de cadena', 'Veterinario de barrio', 'Urgencias 24 h'],
    modelo: 'Consultas + plan de salud mensual', ticket: 95000, clientesMes: 180, costoFijo: 18000000, capital: 120000000,
    legal: 'S.A.S. con registro ante la Secretaría de Salud y médico veterinario con tarjeta profesional',
    roles: { humanos: ['Médico veterinario', 'Auxiliar', 'Recepción'], agentes: ['Triaje por chat', 'Recordatorios de vacunas', 'Agenda'] },
    mvp: 'Plan de salud piloto con 60 mascotas y triaje nocturno por chat',
    mvpIncluye: ['Triaje por chat de 8 p. m. a 6 a. m.', 'Plan mensual básico', 'Historia clínica compartida'],
    mvpExcluye: ['Cirugía', 'Hospitalización', 'Tienda de productos'],
    canal: 'Parques para perros, tiendas de mascotas aliadas e Instagram local', primerCliente: 'Familia con un labrador de 9 años y un gato',
    cuelloBotella: 'El turno nocturno depende de dos veterinarios: más demanda nocturna no se puede atender.',
    escala: 'Red de clínicas aliadas que usan el mismo triaje y planes de salud por suscripción.',
  },
  {
    id: 'muebles', label: 'Fábrica de muebles', sector: 'Manufactura', icon: '🪑', example: 'Roble & Co.',
    problema: 'Quienes compran apartamento pequeño no encuentran muebles a medida a precio razonable y en menos de un mes.',
    cliente: 'Parejas que estrenan apartamento de 40 a 70 m² en ciudades principales.',
    alternativa: 'Muebles de gran superficie que no caben, o carpinteros sin diseño ni garantía.',
    costo: 'Espacios desaprovechados y esperas de 6 a 10 semanas por un mueble a medida.',
    propuesta: 'Muebles modulares a medida, diseñados en una videollamada e instalados en 15 días.',
    diferenciador: 'Diseño en 3D en la llamada y fabricación con módulos estándar: rápido y a medida.',
    competidores: ['Gran superficie', 'Carpintero independiente', 'Tienda de diseño'],
    modelo: 'Venta por proyecto con anticipo del 50 %', ticket: 4200000, clientesMes: 14, costoFijo: 22000000, capital: 180000000,
    legal: 'S.A.S. con certificado de origen legal de la madera y garantía según el Estatuto del Consumidor',
    roles: { humanos: ['Diseñador', 'Ebanistas', 'Instalador'], agentes: ['Cotizador 3D', 'Compras de madera', 'Seguimiento de pedidos'] },
    mvp: 'Línea piloto de 2 muebles modulares (cama con almacenamiento y estudio) para 10 clientes',
    mvpIncluye: ['Configurador de 2 muebles', 'Diseño por videollamada', 'Instalación en 15 días'],
    mvpExcluye: ['Showroom', 'Cocinas integrales', 'Venta en otras ciudades'],
    canal: 'Constructoras de vivienda nueva y anuncios a compradores recientes', primerCliente: 'Pareja que estrena apartamento de 52 m²',
    cuelloBotella: 'El diseño lo hace una sola persona y cada proyecto tarda 6 horas de diseño.',
    escala: 'Biblioteca de módulos estándar y alianzas con constructoras para cada proyecto nuevo.',
  },
  {
    id: 'contable', label: 'Firma contable', sector: 'Servicios profesionales', icon: '📊', example: 'Cuentas Claras',
    problema: 'Los dueños de pymes se enteran tarde de sus impuestos y de su caja: reciben la información cuando ya no sirve para decidir.',
    cliente: 'Pymes de 5 a 50 empleados sin área financiera propia.',
    alternativa: 'Contador por horas que entrega reportes un mes tarde.',
    costo: 'Sanciones de la DIAN, intereses de mora y decisiones tomadas a ciegas.',
    propuesta: 'Contabilidad al día con un tablero semanal de caja y alertas de impuestos.',
    diferenciador: 'Información semanal, no mensual, y un asesor que explica en lenguaje simple.',
    competidores: ['Contador independiente', 'Firma tradicional', 'Software contable solo'],
    modelo: 'Iguala mensual por tamaño de empresa', ticket: 1800000, clientesMes: 25, costoFijo: 28000000, capital: 60000000,
    legal: 'S.A.S. con contador público titulado y registro ante la Junta Central de Contadores',
    roles: { humanos: ['Contador titulado', 'Asesor tributario'], agentes: ['Conciliación bancaria', 'Alertas de calendario DIAN', 'Tablero de caja'] },
    mvp: 'Servicio piloto con 8 pymes y tablero semanal de caja',
    mvpIncluye: ['Conciliación semanal', 'Tablero de caja', 'Calendario tributario con alertas'],
    mvpExcluye: ['Nómina', 'Auditoría', 'Revisoría fiscal'],
    canal: 'Cámara de comercio, gremios y referidos de clientes', primerCliente: 'Distribuidora de 18 empleados',
    cuelloBotella: 'Cada contador atiende máximo 12 empresas; crecer exige contratar y formar.',
    escala: 'Automatizar la conciliación con agentes y abrir una línea para pymes de otras ciudades.',
  },
  {
    id: 'logistica', label: 'App de domicilios', sector: 'Tecnología', icon: '🛵', example: 'Ruta Tienda',
    problema: 'Las tiendas de barrio pierden ventas porque no pueden ofrecer domicilios sin pagar comisiones del 25 %.',
    cliente: 'Tiendas de barrio y minimercados con ventas de COP 30 a 150 millones al mes.',
    alternativa: 'Apps de domicilio con comisiones altas o un mensajero propio subutilizado.',
    costo: 'Hasta 25 % de comisión por pedido o ventas perdidas por no tener domicilio.',
    propuesta: 'Domicilios compartidos entre tiendas vecinas por una tarifa fija mensual.',
    diferenciador: 'Mensajeros compartidos por zona: el costo baja con cada tienda que se une.',
    competidores: ['App de domicilios grande', 'Mensajero propio', 'Mensajería por WhatsApp'],
    modelo: 'Suscripción mensual por tienda + tarifa por pedido', ticket: 450000, clientesMes: 60, costoFijo: 35000000, capital: 250000000,
    legal: 'S.A.S. con contratos de mensajeros según la normativa laboral vigente y política de datos (Ley 1581)',
    roles: { humanos: ['Coordinador de zona', 'Mensajeros'], agentes: ['Asignación de rutas', 'Soporte a tiendas', 'Cobro y facturación'] },
    mvp: 'App piloto en un barrio con 12 tiendas y 3 mensajeros compartidos',
    mvpIncluye: ['Pedido desde WhatsApp', 'Asignación de mensajero', 'Seguimiento del domicilio'],
    mvpExcluye: ['App para el consumidor final', 'Pagos en la app', 'Otras ciudades'],
    canal: 'Visitas puerta a puerta y alianzas con distribuidores de consumo masivo', primerCliente: 'Minimercado Don Pedro',
    cuelloBotella: 'La asignación de rutas se vuelve lenta con más de 40 tiendas por zona.',
    escala: 'Nuevas zonas con el mismo modelo y API para distribuidores mayoristas.',
  },
  {
    id: 'turismo', label: 'Agencia de experiencias', sector: 'Turismo', icon: '🏝️', example: 'Rutas del Caribe',
    problema: 'Los viajeros que llegan a la región no encuentran experiencias locales auténticas y seguras fuera de los planes masivos.',
    cliente: 'Viajeros nacionales y extranjeros de 28 a 55 años que buscan experiencias locales.',
    alternativa: 'Tours masivos de hotel o recomendaciones sueltas en redes sociales.',
    costo: 'Experiencias genéricas y riesgo al contratar operadores informales.',
    propuesta: 'Experiencias locales verificadas, con guías certificados y reserva en minutos.',
    diferenciador: 'Operadores con RNT verificado y experiencias diseñadas con la comunidad local.',
    competidores: ['Tour del hotel', 'Plataforma global de experiencias', 'Guía informal'],
    modelo: 'Comisión por experiencia vendida', ticket: 320000, clientesMes: 150, costoFijo: 12000000, capital: 70000000,
    legal: 'S.A.S. con Registro Nacional de Turismo (RNT) y póliza de responsabilidad',
    roles: { humanos: ['Coordinador de operadores', 'Guías aliados'], agentes: ['Reservas y pagos', 'Atención 24/7', 'Reseñas'] },
    mvp: 'Catálogo piloto de 6 experiencias con 4 operadores verificados',
    mvpIncluye: ['6 experiencias', 'Reserva y pago en línea', 'Atención por WhatsApp'],
    mvpExcluye: ['Vuelos y hoteles', 'Paquetes', 'Otras ciudades'],
    canal: 'Hoteles boutique aliados y contenido en redes', primerCliente: 'Pareja de viajeros de Medellín, tour gastronómico',
    cuelloBotella: 'Verificar a cada operador toma una semana y frena el catálogo.',
    escala: 'Verificación de operadores con agentes y apertura de tres destinos nuevos.',
  },
]

// ---------------------------------------------------------------- Los 7 Niveles

export interface GateTask {
  id: string
  label: string
  agent: AgentId
  zone: ZoneId
  xp: number
  done: string // cómo se registra cuando el agente entrega
}

export interface Level {
  number: number
  name: string
  tagline: string
  ritmo: string
  emocion: string
  descubre: string
  aprende: string
  gemelo: string
  entregable: string
  score: string
  zones: ZoneId[]
  tasks: GateTask[]
  avance: string
  badge: { name: string; icon: string; meaning: string }
  focus: Partial<Record<AgentId, string>>
}

export const LEVELS: Level[] = [
  {
    number: 1, name: 'El Dolor', tagline: '¿El problema es real y le duele a alguien más que a ti?',
    ritmo: 'Inmediato', emocion: 'Comprendido',
    descubre: 'Si el problema es real, urgente y afecta a más personas que al fundador, validado con evidencia externa.',
    aprende: 'Si vale la pena perseguir la idea o conviene pivotar antes de invertir: el primer go/no-go honesto.',
    gemelo: 'Nace el Gemelo Digital: narrativa fundacional, Usuario Principal, primera Decisión y Problem Score.',
    entregable: 'Diagnóstico del Dolor', score: 'Problem Score', zones: ['csi', 'board', 'memoria'],
    avance: 'Evidencia externa + testimonios de clientes + tu aprobación del diagnóstico.',
    badge: { name: 'Nace el Gemelo', icon: '🧬', meaning: 'Tu empresa existe en ADÁN, con su primera decisión registrada.' },
    tasks: [
      { id: 'l1-guion', label: 'Conversar los 7 temas del dolor', agent: 'ceo', zone: 'memoria', xp: 40, done: 'Guion del dolor completo (7 de 7)' },
      { id: 'l1-csi', label: 'Buscar evidencia externa', agent: 'csi', zone: 'csi', xp: 60, done: '3 fuentes externas verificadas' },
      { id: 'l1-entrevistas', label: 'Entrevistar clientes del segmento', agent: 'investigador', zone: 'mercado', xp: 80, done: '5 testimonios de clientes registrados' },
    ],
    focus: { ceo: 'Te escucho: problema, a quién le duele, cuánto cuesta.', csi: 'Busco estudios y cifras que confirmen o desmientan el dolor.',
      cmo: 'Quiero saber si le duele a un segmento concreto, no a "todo el mundo".', investigador: 'Preparo el guion de entrevistas.' },
  },
  {
    number: 2, name: 'Propuesta de Valor', tagline: '¿Por qué te elegirían a ti y no a la alternativa?',
    ritmo: 'Exploratorio', emocion: 'Inspirado por la claridad',
    descubre: 'Cómo se diferencia la propuesta frente a las alternativas y qué tan defendible es esa diferencia.',
    aprende: 'Si la solución original necesita ajustes: aquí la idea puede evolucionar.',
    gemelo: 'Se registran Mercado, Competidores y la primera versión del Producto o Servicio. Solution Score.',
    entregable: 'Propuesta de Valor y matriz comparativa', score: 'Solution Score', zones: ['csi', 'simulador', 'board'],
    avance: 'Al menos una validación real con clientes potenciales + tu aprobación.',
    badge: { name: 'Propuesta con filo', icon: '💎', meaning: 'Tu diferencia frente al mercado quedó validada con clientes.' },
    tasks: [
      { id: 'l2-competencia', label: 'Mapear competidores y alternativas', agent: 'csi', zone: 'csi', xp: 50, done: 'Matriz de 3 competidores' },
      { id: 'l2-propuesta', label: 'Redactar la propuesta en una frase', agent: 'cmo', zone: 'board', xp: 50, done: 'Propuesta de valor v1' },
      { id: 'l2-validacion', label: 'Validar la propuesta con clientes', agent: 'investigador', zone: 'mercado', xp: 80, done: 'Validación con 8 clientes potenciales' },
    ],
    focus: { cmo: 'Busco el diferenciador que el cliente sí nota.', csi: 'Comparo con lo que ya existe: precio, cercanía, calidad.',
      producto: 'Ajusto la solución a lo que dijeron los clientes.' },
  },
  {
    number: 3, name: 'Plan de Negocios', tagline: '¿Cuánto capital necesitas de verdad y cómo te organizas?',
    ritmo: 'Reflexivo', emocion: 'Seguro',
    descubre: 'La estructura legal y tributaria, proyecciones contrastadas con benchmarks y un marketing con costos reales.',
    aprende: 'Cuánto capital necesita, qué estructura le conviene y qué roles son humanos y cuáles agénticos.',
    gemelo: 'Se crean Departamentos, Cargos, Activos y Pasivos, Objetivos e Indicadores y la ruta legal. Business Score.',
    entregable: 'Plan de negocio y organigrama híbrido', score: 'Business Score', zones: ['board', 'memoria', 'mercado'],
    avance: 'Proyecciones validadas contra benchmarks externos + tu aprobación.',
    badge: { name: 'Números con suelo', icon: '🏛️', meaning: 'Tu plan financiero resiste la comparación con el sector.' },
    tasks: [
      { id: 'l3-legal', label: 'Definir la estructura legal', agent: 'legal', zone: 'board', xp: 50, done: 'Ruta legal y tributaria' },
      { id: 'l3-finanzas', label: 'Proyectar 12 meses contra benchmarks', agent: 'cfo', zone: 'csi', xp: 70, done: 'Proyección financiera auditada' },
      { id: 'l3-organigrama', label: 'Diseñar el organigrama híbrido', agent: 'operaciones', zone: 'memoria', xp: 50, done: 'Organigrama: humanos y agentes' },
      { id: 'l3-modelo', label: 'Construir el modelo de caja', agent: 'analista', zone: 'mercado', xp: 40, done: 'Modelo de caja mensual' },
    ],
    focus: { cfo: 'Contrasto cada cifra con datos del sector.', legal: 'Elijo la figura legal y los permisos que aplican.',
      operaciones: 'Defino qué hace una persona y qué hace un agente.', analista: 'Armo el flujo de caja mes a mes.' },
  },
  {
    number: 4, name: 'MVP', tagline: '¿Qué construir exactamente, y nada más?',
    ritmo: 'Constructivo', emocion: 'Emocionado con base real',
    descubre: 'Qué construir exactamente, en el lenguaje del cliente: app, piloto físico o servicio.',
    aprende: 'Si lo que se puede construir coincide con la propuesta validada, antes de comprometer recursos.',
    gemelo: 'El Producto pasa a versión de construcción y nace la Iniciativa de construcción. Product Score.',
    entregable: 'Blueprint del MVP y roadmap', score: 'Product Score', zones: ['genexis', 'board', 'gemelo'],
    avance: 'Blueprint aprobado por ti antes de construir: nunca se construye sin aprobación.',
    badge: { name: 'Blueprint aprobado', icon: '🛠️', meaning: 'Aprobaste qué se construye: Genexis tiene luz verde.' },
    tasks: [
      { id: 'l4-alcance', label: 'Definir el alcance del MVP', agent: 'producto', zone: 'genexis', xp: 50, done: 'Alcance: qué entra y qué no' },
      { id: 'l4-blueprint', label: 'Diseñar el blueprint técnico', agent: 'cto', zone: 'genexis', xp: 60, done: 'Blueprint y mockups' },
      { id: 'l4-construir', label: 'Construir con Genexis', agent: 'genexis', zone: 'genexis', xp: 90, done: 'MVP construido y listo para probar' },
    ],
    focus: { producto: 'Recorto el alcance a lo mínimo que prueba la propuesta.', cto: 'Diseño cómo se construye y con qué.',
      genexis: 'Espero tu aprobación del blueprint para construir.' },
  },
  {
    number: 5, name: 'Validación Simulada', tagline: '¿Dónde se rompe tu modelo antes de arriesgar capital real?',
    ritmo: 'Intenso', emocion: 'Desafiado, no amenazado',
    descubre: 'Cómo reaccionarían clientes, competidores e inversionistas simulados ante el MVP.',
    aprende: 'Los puntos débiles del modelo, en un entorno seguro de práctica.',
    gemelo: 'Se registran Riesgos y los ajustes como nuevas Decisiones. Market Score y Execution Score.',
    entregable: 'Informe de Validación Simulada', score: 'Market Score', zones: ['simulador', 'board', 'csi'],
    avance: 'Métricas simuladas dentro de parámetros aceptables + tu aprobación para lanzar.',
    badge: { name: 'Prueba de fuego', icon: '🔥', meaning: 'Tu modelo resistió clientes, competidores e inversionistas simulados.' },
    tasks: [
      { id: 'l5-clientes', label: 'Simular 200 clientes', agent: 'cmo', zone: 'simulador', xp: 60, done: 'Conversión simulada y objeciones' },
      { id: 'l5-competidor', label: 'Simular la reacción de la competencia', agent: 'csi', zone: 'simulador', xp: 50, done: 'Escenario de guerra de precios' },
      { id: 'l5-inversionista', label: 'Pitch a inversionistas simulados', agent: 'cfo', zone: 'simulador', xp: 60, done: 'Preguntas difíciles respondidas' },
    ],
    focus: { cmo: 'Pongo el MVP frente a 200 clientes simulados.', cfo: 'Defiendo los números frente a inversionistas simulados.',
      csi: 'Simulo cómo respondería la competencia.', operaciones: 'Busco dónde se rompe la operación.' },
  },
  {
    number: 6, name: 'Lanzamiento', tagline: '¿Funciona con clientes reales y dinero real?',
    ritmo: 'Estable', emocion: 'Acompañado',
    descubre: 'Cómo se comporta la empresa en el mundo real: primeros clientes, ingresos y gastos.',
    aprende: 'Si el negocio funciona con el mercado real, la prueba que ninguna simulación reemplaza.',
    gemelo: 'La empresa pasa de "validada" a "operando". Primer Suceso Empresarial real.',
    entregable: 'Primer ciclo de operación', score: 'Venture Score', zones: ['eva', 'gemelo', 'mercado'],
    avance: 'Al menos un ingreso o cliente real, registrado y verificado.',
    badge: { name: 'Primer cliente real', icon: '🚀', meaning: 'Alguien pagó de verdad: tu empresa opera.' },
    tasks: [
      { id: 'l6-lanzar', label: 'Lanzar campaña con EVA', agent: 'eva', zone: 'eva', xp: 60, done: 'Campaña de lanzamiento activa' },
      { id: 'l6-venta', label: 'Registrar la primera venta real', agent: 'operaciones', zone: 'gemelo', xp: 100, done: 'Primer ingreso real verificado' },
      { id: 'l6-ciclo', label: 'Documentar el primer ciclo', agent: 'ceo', zone: 'memoria', xp: 50, done: 'Ingresos, gastos y lecciones del mes' },
    ],
    focus: { eva: 'Llevo la oferta a los canales donde está el cliente.', operaciones: 'Cuido que cada entrega salga bien.',
      ceo: 'Hago check-ins regulares: sin urgencias, sin picos.' },
  },
  {
    number: 7, name: 'Escalamiento', tagline: '¿Qué te frena para crecer y cuándo reestructurar?',
    ritmo: 'Expansivo', emocion: 'Ambicioso',
    descubre: 'Patrones de crecimiento y los cuellos de botella estructurales antes de que se vuelvan crisis.',
    aprende: 'Cuándo reestructurar, cuándo levantar capital y qué tan rápido madura su organización.',
    gemelo: 'La Velocidad de Maduración Organizacional pasa a ser la métrica central. Nuevas iniciativas de expansión.',
    entregable: 'Diagnóstico de Escalamiento', score: 'Venture Score', zones: ['board', 'gemelo', 'mercado', 'csi'],
    avance: 'Es continuo: ADÁN te acompaña de forma permanente, y la empresa puede volver a reinventarse.',
    badge: { name: 'Modo continuo', icon: '♾️', meaning: 'ADÁN te acompaña de forma permanente en el crecimiento.' },
    tasks: [
      { id: 'l7-cuello', label: 'Detectar el cuello de botella', agent: 'operaciones', zone: 'gemelo', xp: 60, done: 'Cuello de botella identificado' },
      { id: 'l7-capital', label: 'Evaluar opciones de capital', agent: 'cfo', zone: 'mercado', xp: 60, done: 'Opciones de capital comparadas' },
      { id: 'l7-plan', label: 'Diseñar el plan de reestructuración', agent: 'ceo', zone: 'board', xp: 70, done: 'Plan de escalamiento aprobado' },
    ],
    focus: { ceo: 'Vuelve el comité completo, ahora para pensar en grande.', operaciones: 'Mido dónde se atasca el crecimiento.',
      cfo: 'Comparo crecer con caja propia, deuda o capital.' },
  },
]

export const TOTAL_XP = LEVELS.reduce((sum, l) => sum + l.tasks.reduce((s, t) => s + t.xp, 0), 0)

export const ECOSYSTEM = [
  { name: 'ADÁN', icon: '🧠', text: 'Crea o reinventa empresas con los 7 Niveles y suministra agentes por tiempo.' },
  { name: 'CSI', icon: '📡', text: 'Inteligencia externa: mercado, competencia, regulación y benchmarks.' },
  { name: 'Genexis', icon: '⚙️', text: 'Motor interno que construye el MVP del Nivel 4.' },
  { name: 'EVA', icon: '🎙️', text: 'Ventas y marketing con IA: campañas, voz y omnicanalidad.' },
  { name: 'Marketplace', icon: '🛒', text: 'Donde se contratan agentes por hora, día, semana o mes.' },
  { name: 'Comunidad', icon: '🤝', text: 'Red de emprendedores y empresas del ecosistema Paradixe.' },
  { name: 'Paradixe Capital', icon: '💠', text: 'Invierte con equity negociado caso por caso. ADÁN solo aporta la evidencia.' },
  { name: 'Enterprise Intelligence', icon: '🌐', text: 'Aprendizaje agregado, solo con datos consentidos y anonimizados.' },
]

export function cop(n: number): string {
  return 'COP ' + Math.round(n).toLocaleString('es-CO')
}
