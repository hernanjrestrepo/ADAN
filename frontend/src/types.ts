// Tipos de las respuestas del backend (backend/app/schemas/schemas.py y api/v1/nivel1.py).

export interface User {
  id: string
  email: string
  name: string
  role: string
  is_superadmin?: boolean
  // Correo del superadministrador que está revisando esta cuenta (solo lectura)
  revisando_desde?: string | null
}

export interface TokenResponse {
  access_token: string
  token_type: string
  user: User
}

export interface Company {
  id: string
  name: string
  description: string | null
  industry: string | null
  country: string | null
  maturity: number
  status: string
  version: number
  created_at: string
  brand_color?: string | null
  brand_accent?: string | null
  logo?: string | null
  origin_stage?: string | null
}

export interface Project {
  id: string
  company_id: string
  name: string
  status: string
}

export type LevelStatus = 'blocked' | 'active' | 'completed'

export interface Level {
  id: string
  project_id: string
  number: number
  name: string
  status: LevelStatus
  completed_at: string | null
}

export interface Conversation {
  id: string
  card_id: string
  title: string | null
  status: string
  summary: string | null
}

export interface Message {
  id: string
  conversation_id?: string
  role: 'user' | 'assistant' | 'system' | 'agent' | string
  agent_name?: string | null
  content: string
  created_at: string
  // degraded: respondió el modelo local de respaldo porque Claude no estaba disponible
  metadata_json?: {
    degraded?: string | null
    reaccion?: { agente: string; emocion: string; frase: string } | null
    investigado?: { consulta: string; verificado: boolean } | null
    investigando?: { consulta: string } | null
    // ADÁN propone cerrar el Nivel (el fundador confirma con un clic o diciendo que sí)
    propone_cierre?: boolean
    // Respuestas rápidas que el fundador puede tocar en vez de escribir
    opciones?: string[]
    // Logo encontrado en la web de la empresa, para adoptarlo con un clic
    logo_sugerido?: { url: string } | null
    // Trabajo en segundo plano que llega como mensaje aparte
    trabajando?: { tipo: 'recorrido' | 'repositorio'; url: string; objetivo: string } | null
    recorrido?: boolean
    revision_codigo?: boolean
    agente?: string
    escena?: string
    voto?: string
  } | null
}

// Guion del Descubrimiento del Dolor: siete temas y lo que ADÁN ya entendió de cada uno
export type DiscoveryStatus = 'pendiente' | 'parcial' | 'respondido' | 'sin_dato'

export interface DiscoveryTopic {
  id: string
  label: string
  estado: DiscoveryStatus
  resumen: string
  base: 'dato' | 'supuesto' | 'desconocida'
}

export interface EvidenceSuggestion {
  afirmacion: string
  tipo: 'testimony' | 'external'
  fuente: string
}

export interface DiscoveryProgress {
  topics: DiscoveryTopic[]
  done: number
  total: number
  next: string | null
  complete: boolean
  evidence_suggestions: EvidenceSuggestion[]
}

export interface Score {
  id: string
  project_id: string
  score_type: string
  value: number
  confidence_level: number
  reasoning: string | null
  created_at: string
}

export interface DocumentRecord {
  id: string
  project_id: string
  title: string
  content: string | null
  doc_type: string
  origin: string
  version: number
  created_at: string
}

// Patrón A (AD-008) con el estado "Presentada" de AD-CMP-03 (WO-098)
export type DecisionStatus = 'proposed' | 'presented' | 'approved' | 'rejected' | 'executed'

export type EvidenceLevel = 'alta' | 'media' | 'baja'

export interface DecisionOption {
  key: string
  label: string
  rationale?: string
  evidence_level?: EvidenceLevel
  confidence?: number
  votes?: number
}

// Los 6 campos cuando el cliente decide distinto a lo recomendado (AD-FUNC-02 §2.5)
export interface Divergence {
  chosen_option: { key: string; label?: string }
  recommended_option: { key: string; label?: string; rationale?: string }
  evidence_level: { chosen?: EvidenceLevel; recommended?: EvidenceLevel }
  confidence: { chosen?: number; recommended?: number }
  risks_assumed: string[]
  responsibility_assumed: string
}

export interface PriorDecision {
  id: string
  title: string
  status: DecisionStatus
  chosen_option: string | null
}

export interface Decision {
  id: string
  project_id: string
  title: string
  description: string | null
  proposed_by: string | null
  status: DecisionStatus
  reasoning: string | null
  confidence_level: number | null
  created_at: string
  disagreement?: string | null
  options?: DecisionOption[] | null
  recommended_option?: string | null
  chosen_option?: string | null
  divergence?: Divergence | null
  prior_decisions?: PriorDecision[] | null
  presented_at?: string | null
  decided_at?: string | null
  executed_at?: string | null
  business_decision?: { id: string; title: string; state: string } | null
}

export interface DecideInput {
  action: 'approve' | 'reject'
  chosen_option?: string
  risks_assumed?: string[]
  responsibility_statement?: string
}

// Gemelo Digital (WO-098)
export interface TwinOverview {
  company: {
    id: string
    name: string
    status: 'active' | 'paused' | 'archived'
    version: number
    founded_on: string | null
    jurisdiction: string | null
    legal_structure: string | null
    intangibles: Record<string, string>
  }
  identity: {
    age_years: number
    maturity: number
    lifecycle_stage: string
    maturation_velocity_per_year: number | null
  }
  counts: Record<string, number>
  lineage: {
    company_id: string
    source_company_id: string
    relation: 'split_from' | 'merged_from'
    initiative_id: string | null
    note: string | null
    created_at: string
  }[]
}

export interface TwinKind {
  key: string
  label: string
  label_plural: string
  cluster: string
  cluster_label: string
  pattern: 'A' | 'B' | 'C' | 'D' | null
}

export interface TimelineEvent {
  id: string
  event_type: string
  entity_type: string
  entity_id: string
  category: 'domain' | 'cognitive'
  data: { label?: string; from?: string; to?: string; reason?: string; [key: string]: unknown }
  actor_type: 'user' | 'agent' | 'system' | null
  actor_id: string | null
  created_at: string
}

export interface Nivel1Status {
  company: Company
  project: Project
  level: Level | null
  card: { id: string } | null
  conversation: Conversation | null
  messages: Message[]
  scores: Score[]
  documents: DocumentRecord[]
  discovery?: DiscoveryProgress
}

export interface ChatResponse {
  message: Message
  conversation_id: string
  card_id: string | null
  disclaimer: string
}

export type Vote = 'PROCEED' | 'PIVOT' | 'STOP' | 'ABSTAIN' | 'NO_CONSENSUS'

export interface AgentVote {
  agent: string
  analysis: string
  justification: string
  vote: Vote
  confidence: number
  key_strengths: string[]
  key_concerns: string[]
  questions: string[]
  model: string
  duration_s: number
  // Board crítico: por qué cerraría la empresa desde su área y si su área está a prueba de balas
  failure_mode?: string
  bulletproof?: boolean
  devils_advocate?: boolean
}

export interface BoardConsensus {
  decision: Vote
  score: number
  confidence: number
  summary: string
  votes: AgentVote[]
  concerns_unanimous: string[]
  concerns_majority: string[]
  strengths_unanimous: string[]
  dissent: string  // vacío si nadie discrepa
  disclaimer: string
  // Flujo Maestro (AD-FUNC-02): el CEO abre y cierra; el cliente participa
  objective: string
  decision_at_stake: string
  synthesis: string
  evidence_requests: string[]
  next_steps: string[]
  client_question: string
  client_position: string
  minutes: string
  failure_modes?: string[]
  bulletproof_gaps?: string[]
}

export interface BoardRoomInput {
  question: string
  position: string
}

export interface GateReviewResult {
  approved: boolean
  scores: Score[]
  decisions: Decision[]
  level_status: string
  message: string
  // WO-107: el Gate decide sobre evidencia registrada y dice qué falta
  problem_score?: number | null
  confidence?: number | null
  missing?: string[]
  evidence_breakdown?: EvidenceBreakdown | null
  disclaimer: string
}

// --- Evidencia y Scoring (WO-107, AD-CMP-05 y AD-FUNC-07) ---

export type EvidenceKind = 'external' | 'testimony' | 'inference'
export type EvidencePolarity = 'supports' | 'contradicts'
export type EvidenceBreakdown = Record<EvidenceKind, Record<EvidencePolarity, number>>

export interface Evidence {
  id: string
  dimension: string
  claim: string
  kind: EvidenceKind
  kind_label: string
  polarity: EvidencePolarity
  source: string | null
  level_number: number | null
  status: string
  created_by: string | null
  confidence_level: number | null
  confirmed: boolean
  verification: EvidenceVerification | null
  created_at: string
}

export interface EvidenceVerification {
  status: 'verified' | 'unreachable' | 'blocked'
  http_status?: number
  title?: string | null
  detail?: string
  checked_at: string
}

export interface EvidenceInput {
  dimension?: string
  claim: string
  kind: 'external' | 'testimony'
  polarity: EvidencePolarity
  source?: string
}

export interface ScoreOverview {
  key: string
  label: string
  measures: string
  level: number | null
  family: 'diagnostic' | 'continuous'
  available: boolean
  unavailable_reason: string | null
  evidence_count: number
  latest: {
    id: string
    value: number
    confidence: number
    reasoning: string | null
    breakdown: EvidenceBreakdown | null
    created_at: string
  } | null
}

export interface GatePreview {
  level_number: number
  sufficient: boolean
  missing: string[]
  score_type: string
  value: number
  confidence: number
  reasoning: string
  breakdown: EvidenceBreakdown
}

export interface CompanyInput {
  name: string
  description: string
  industry: string
  country: string
}

// --- Onboarding (WO-108, AD-FUNC-06) ---

export interface Identity {
  key: string
  label: string
  step: number
  of: number
  next: { key: string; label: string; milestone: string } | null
}

export interface ConsentState {
  purpose: 'data_processing' | 'aggregated_intelligence'
  text: string
  granted: boolean
  policy_version: string | null
  since: string | null
}

export interface OnboardingState {
  identity: Identity
  consents: Record<'data_processing' | 'aggregated_intelligence', ConsentState>
  next: { step: 'company' | 'first_answer' | 'done'; company_id: string | null }
  policy_version: string
}

export interface LevelView {
  id: string
  number: number
  name: string
  status: LevelStatus
  completed_at: string | null
  discovers: string
  deliverable: string
  score_key: string | null
  score: { value: number; confidence: number } | null
  cards: { id: string; title: string; description: string | null; card_type: string; status: string }[]
}

// --- Agentes por tiempo (WO-109) ---

export type HirePeriod = 'hour' | 'day' | 'week' | 'month'

export interface AgentOffering {
  code: string
  name: string
  role: string
  description: string
  skills: string[]
  tools: string[]
  tier: string
  price_note: string
}

export interface AgentContract {
  id: string
  offering: AgentOffering
  period: HirePeriod
  units: number
  hours_capacity: number
  hours_used: number
  starts_at: string
  ends_at: string
  state: 'active' | 'expired' | 'exhausted' | 'cancelled'
  price_note: string
}

export interface AgentTask {
  id: string
  title: string
  description: string | null
  status: 'assigned' | 'in_progress' | 'review' | 'completed'
  result: string | null
  blocking_reason: string | null
  feedback: string[]
  created_at: string | null
  completed_at: string | null
}

export interface ContractReport {
  hours_capacity: number
  hours_used: number
  hours_left: number
  state: string
  runs: number
  delivered: number
  failed: number
  model_cost_usd: number
  tokens: number
  degraded_runs: number
  tools: string[]
  price_note: string
}

// Documentación del cliente: lo que se cargó y lo que ADÁN aprendió de ella
export interface UploadedDocument {
  id: string
  title: string
  kind: string
  pages: number
  chars: number
  truncated: boolean
}

export interface UploadResult {
  documents: UploadedDocument[]
  errors: string[]
  reply: string
  degraded?: string | null
  conversation_id: string
  learning: { resumen?: string; etapa?: string; vacios?: string[]; riesgos?: string[] }
  discovery: DiscoveryProgress
}

// La Arena: cuatro inversionistas simulados
export interface ArenaInvestor {
  id: string
  name: string
  role: string
  avatar: string
  first_impression: string
  questions: string[]
  red_flags: string[]
  unavailable?: boolean
  answer?: string
  decision?: 'INVIERTE' | 'CON_CONDICIONES' | 'NO_INVIERTE' | 'SIN_RESPUESTA'
  amount_usd?: number
  terms?: string
  reason?: string
  conditions?: string[]
  fatal_flaw?: string
}

export interface ArenaSession {
  id: string
  phase: 'questions' | 'decided'
  pitch: string
  investors: ArenaInvestor[]
  passed?: boolean
  backers?: number
  total_usd?: number
  verdict?: string
}

// Constitución de la empresa: nombre, dominios, ruta legal por país y estatutos
export interface DomainCheck {
  domain: string
  tld: string
  status: 'disponible' | 'probable_libre' | 'registrado' | 'sin_confirmar'
  usd_min: number
  usd_max: number
  nota: string
}

export interface NameCheck {
  name: string
  country: string
  searched: boolean
  veredicto: 'libre_probable' | 'conflicto' | 'incierto'
  explicacion: string
  coincidencias: { nombre: string; tipo: string; donde: string; fuente: string }[]
  registros_oficiales: { nombre: string; url: string; que_verificar: string }[]
  alternativas: string[]
  slug: string
  domains: DomainCheck[]
  registrars: { name: string; url: string; nota: string }[]
  prices_note: string
}

export interface LegalStep {
  titulo: string
  que_es: string
  donde: string
  url: string
  documentos: string[]
  costo: string
  tiempo: string
  errores_comunes: string[]
}

export interface LegalGuide {
  id: string
  pais: string
  resumen: string
  searched: boolean
  tipos_sociedad: { nombre: string; para_quien: string; ventajas: string[]; desventajas: string[]; socios: string; responsabilidad: string }[]
  recomendada: { nombre: string; por_que: string }
  regimenes: { nombre: string; quien_puede: string; como_funciona: string; conviene_si: string }[]
  regimen_recomendado: { nombre: string; por_que: string }
  pasos: LegalStep[]
  done: boolean[]
  obligaciones: string[]
  costo_total: string
  tiempo_total: string
  fuentes: { nombre: string; url: string }[]
  disclaimer: string
}

export interface Partner {
  nombre: string
  documento: string
  aporte: string
  porcentaje: number | null
}

export interface StatutesInput {
  pais: string
  tipo: string
  nombre: string
  domicilio: string
  objeto: string
  capital: string
  administracion: string
  socios: Partner[]
}

export interface Statutes {
  id: string
  title: string
  markdown: string
}

// Encuestas de validación
export type SurveyAnswer = string | number | string[]

export interface PublicSurvey {
  token: string
  company: string
  titulo: string
  intro: string
  open: boolean
  preguntas: { id: string; texto: string; tipo: 'opcion' | 'multiple' | 'escala' | 'numero' | 'texto'; opciones: string[] }[]
}

export interface SurveySummary {
  token: string
  titulo: string
  created_at: string
  open: boolean
  responses: number
}

export interface SurveyResults {
  token: string
  titulo: string
  open: boolean
  responses: number
  questions: {
    id: string
    texto: string
    tipo: string
    opciones: string[]
    por_que: string
    answered: number
    counts?: Record<string, number>
    average?: number | null
    texts?: string[]
  }[]
  simulation?: SurveySimulation | null
}

export interface SurveyInsights {
  resumen: string
  hallazgos: string[]
  alertas: string[]
  evidencia_sugerida: { afirmacion: string; tipo: 'testimony'; polaridad: EvidencePolarity; fuente: string }[]
}

// Finanzas y estrategia
export interface OrgRole {
  area: string
  cargo: string
  tipo: 'humano' | 'agente_adan' | 'servicio_paradixe'
  servicio: string
  responsabilidades: string[]
  desde_mes: number
  minutos_mes: number
  costo_mensual: number
  costo_humano_equivalente: number
  por_que: string
  precio: string
}

export interface OrgChart {
  moneda: string
  resumen: string
  roles: OrgRole[]
  costo_mensual_total: number
  costo_todo_humano: number
  ahorro_mensual: number
  ahorro_pct: number
  generated_at: string
}

export interface CashRow {
  mes: number
  unidades: number
  ingresos: number
  costo_variable: number
  margen_contribucion: number
  gastos_fijos: number
  marketing: number
  ebitda: number
  impuestos: number
  capex: number
  financiacion: number
  flujo_neto: number
  caja: number
}

export interface CashKpis {
  punto_equilibrio_mes: number | null
  caja_minima: number
  caja_minima_mes: number
  capital_necesario: number
  margen_contribucion_pct: number
  ingresos_ano_1: number
  ingresos_ano_2: number
  ebitda_ano_1: number
  ebitda_ano_2: number
  caja_final: number
  se_queda_sin_caja: boolean
  mes_sin_caja: number | null
  gasto_fijo_mensual_inicial: number
  ingresos_24_meses: number
}

export interface FinancialModel {
  assumptions: {
    moneda: string
    unidad: string
    precio_unitario: number
    mes_inicio_ventas: number
    unidades_mes_1: number
    crecimiento_mensual_pct: number
    unidades_max_mes: number
    costo_variable_pct: number
    comision_pagos_pct: number
    marketing_mensual: number
    impuesto_renta_pct: number
    capital_inicial: number
    gastos_fijos: { concepto: string; monto_mensual: number; desde_mes: number; tipo?: string | null; base?: string | null }[]
    capex: { concepto: string; monto: number; mes: number; base?: string | null }[]
    financiacion: { fuente: string; monto: number; mes: number }[]
    bases: Record<string, string>
  }
  base: { scenario: string; rows: CashRow[]; kpis: CashKpis }
  scenarios: Record<string, CashKpis>
  advertencias: string[]
  searched: boolean
  generated_at: string
  edited?: boolean
}

export interface ExecutiveReport {
  titulo: string
  company: string
  respuesta: string
  scqa: { situacion: string; complicacion: string; pregunta: string; respuesta: string }
  argumentos: { titulo: string; evidencia: string[] }[]
  lean_canvas: Record<'problema' | 'segmentos' | 'propuesta_unica' | 'solucion' | 'canales' | 'ingresos' | 'costos' | 'metricas_clave' | 'ventaja_injusta', string>
  benchmark: { competidor: string; fortalezas: string; debilidades: string; como_ganarle: string }[]
  riesgos: { riesgo: string; probabilidad: 'alta' | 'media' | 'baja'; impacto: 'alto' | 'medio' | 'bajo'; mitigacion: string }[]
  six_sigma: { ctq: string[]; definir: string; medir: string; analizar: string; mejorar: string; controlar: string }
  plan_90_dias: { semanas: string; accion: string; responsable: string; entregable: string }[]
  recomendacion: string
  generated_at: string
}

// Comunidad ADÁN
export interface CommunityProfile {
  id?: string
  display_name: string
  headline?: string
  bio?: string
  kind: string
  city?: string
  country?: string
  website?: string
  linkedin?: string
  public: boolean
  ticket_min_usd?: number | null
  ticket_max_usd?: number | null
  sectors?: string[]
  stages?: string[]
  is_curator?: boolean
}

export interface AdanSeal {
  levels_closed: number[]
  current_level?: number | null
  current_level_name?: string
  problem_score?: number | null
  testimonies?: number
  external_sources?: number
  board_decision?: string | null
  arena_passed?: boolean | null
  legal_steps?: [number, number] | null
  breakeven_month?: number | null
}

export interface CommunityListing {
  id: string
  company_id: string
  published: boolean
  name: string
  tagline: string
  description: string
  sector: string
  country: string
  city: string
  stage: string
  looking_for: string[]
  amount_sought_usd: number | null
  website: string
  seal: AdanSeal
  paradixe_selection: boolean
  selection_note: string
  mine: boolean
}

export interface CommunityConnection {
  id: string
  kind: string
  message: string
  status: string
  direction: 'sent' | 'received'
  other_name: string
  other_headline: string
  listing_name: string | null
  other_email: string | null
}

// @pples (US$ 1 = 1.000 @pples)
export interface AppleMovement {
  id: string
  kind: 'compra' | 'nivel' | 'referido' | 'bienvenida' | 'ajuste' | string
  amount: number
  detail: string
  level: number | null
  depth: number | null
  created_at: string
}

export interface AppleWallet {
  balance: number
  movements: AppleMovement[]
  provider: 'simulador' | 'wompi' | string
  required: boolean
}

export interface ApplePurchase {
  id: string
  apples: number
  amount_cop: number
  provider: string
  status: 'pendiente' | 'aprobada' | 'rechazada'
  checkout_url: string
  created_at: string
  balance?: number
}

export interface AppleLevelPrice {
  level: number
  name: string
  llm_usd: number
  infra_usd: number
  cost_usd: number
  price_usd: number
  apples: number
  profit_usd: number
  margin: number
  margin_gap: number
  gateway_usd: number
  referral_usd: number
  margin_after_fees: number
}

export interface ApplePrices {
  levels: AppleLevelPrice[]
  apples_per_usd: number
  target_margin: number
  total_usd: number
  total_apples: number
  total_cost_usd: number
  total_profit_usd: number
  margin: number
  margin_after_fees: number
  apart: string[]
  mvp_examples: Record<string, { cost_usd: number; price_usd: number; apples: number }>
  packs: number[]
  trm: number
  provider: string
}

export interface AppleCompanyLevel {
  level: number
  name: string
  apples: number
  paid: boolean
  paid_at: string | null
}

export interface AppleNetwork {
  code: string
  link: string
  sponsor: string | null
  levels: { depth: number; people: number; earned: number }[]
  rate_per_level: number
  depth: number
  total_earned: number
}

// Consola de Paradixe (superadministradores)
export interface AdminSummary {
  users: number
  users_30d: number
  companies: number
  referred_users: number
  purchases: number
  purchases_cop: number
  apples_sold: number
  apples_gifted: number
  apples_referral: number
  apples_in_wallets: number
  levels: { level: number; name: string; apples: number; price_usd: number; paid: number; revenue: number; revenue_usd: number; cost: number }[]
  levels_revenue: number
  levels_revenue_usd: number
  levels_cost: number
  levels_margin: number | null
  config: { provider: string; live: boolean; required: boolean; welcome_referral: number; trm: number; apples_per_usd: number }
}

export interface AdminUser {
  id: string
  name: string
  email: string
  created_at: string | null
  balance: number
  gift_balance: number
  companies: number
  levels_paid: number
  purchased_cop: number
  code: string | null
  sponsor: string | null
  invited: number
}

export interface AdminPurchase extends ApplePurchase {
  email: string
  external_id: string | null
  resolved_at: string | null
}

export interface AdminMovement {
  id: string
  email: string
  kind: string
  amount: number
  detail: string
  created_at: string
}

export interface AdminCompany {
  id: string
  name: string
  owner: string
  status: string
  stage: string | null
  created_at: string
  levels_paid: number[]
}

// Diálogo con el Board después de votar
export interface BoardDialogueReply {
  agent: string
  reply: string
  vote: Vote
  changed: boolean
  reason: string
}

export interface BoardDialogueTurn {
  message: string
  agent: string | null
  replies: BoardDialogueReply[]
  ceo: string
  consensus: string
  at: string
}

export interface BoardTally {
  votes: Record<string, Vote>
  proceed: number
  total: number
  recommendation: Vote
}

export interface BoardDialogue {
  thread: BoardDialogueTurn[]
  tally: BoardTally
}

// Encuesta simulada con el Simulador de Mercado (se contrasta con la real)
export interface SurveySimulation {
  size: number
  perfil: string
  supuestos: string[]
  questions: { id: string; texto: string; tipo: string; counts?: Record<string, number>; average?: number; texts?: string[] }[]
  created_at: string
}

// La Sala de un Nivel (2 a 7)
export interface LevelInfo {
  number: number
  name: string
  goal: string
  deliverables: string[]
  kpis: string[]
  team: string[]
  board: boolean
  arena: boolean
  topics: { id: string; label: string }[]
}

export interface LevelRoom {
  level: LevelInfo
  status: 'blocked' | 'active' | 'completed'
  conversation_id: string | null
  messages: Message[]
  discovery: DiscoveryProgress | null
}

// Construcción de la empresa: marca y Expediente de creación
export interface BrandName {
  nombre: string
  tipo: string
  por_que: string
  sonido: string
  fluidez: number
  memorabilidad: number
  distintividad: number
  puntaje: number
  dominios_libres: string[]
}

export interface BrandData {
  nombres?: BrandName[]
  nombre_elegido?: string
  logos?: import('./lib/logo').LogoConcept[]
  logo_elegido?: import('./lib/logo').LogoConcept
  slogans?: { texto: string; por_que: string }[]
  slogan?: string
  manual?: string
  identidad?: CompanyIdentity
}

export interface CompanyIdentity {
  nombre: string
  slogan: string
  logo: string | null
  color: string | null
  acento: string | null
  expediente?: { hechos: number; total: number }
}

export interface DossierItem {
  id: string
  grupo: 'identidad' | 'numeros' | 'legal' | 'operacion'
  titulo: string
  que_es: string
  modo: 'adan' | 'cliente_presencial' | 'cliente_en_linea'
  documento: string
  herramienta: string
  estado: 'pendiente' | 'en_curso' | 'preparado' | 'validado' | 'observado' | 'no_aplica'
  nota: string
  preparado_doc: string | null
  validacion: { valido: boolean; tipo_detectado: string; nombre_en_documento: string; numero_identificacion: string; fecha: string; observaciones: string[]; archivo: string } | null
}

export interface Dossier {
  pais: 'CO' | 'US' | 'OTRO'
  pais_nombre: string
  items: DossierItem[]
  hechos: number
  total: number
  identificacion: Record<string, string>
}

export interface LibraryDoc {
  id: string
  titulo: string
  tipo: string
  seccion: 'marca' | 'legal' | 'numeros' | 'estrategia' | 'board' | 'cliente'
  nivel: number | null
  origen: 'adan' | 'tuyo'
  creado: string | null
  actualizado: string | null
  legible: boolean
  herramienta: string | null
  descarga: string | null
  ext: string
  palabras: number | null
}

export interface Library {
  ficha?: Record<string, string>
  faltan?: { nivel: number; entregables: string[] }[]
  memoria?: { tipo: 'decidido' | 'descartado' | 'dato' | 'pendiente'; texto: string; nivel?: number; fecha?: string }[]
  marca: {
    nombre: string
    slogan: string
    logo: string | null
    logo_concepto: string
    tipografia: string
    paleta: { nombre: string; hex: string }[]
    manual: boolean
    nombres_considerados: string[]
    slogans_considerados: string[]
  }
  secciones: Record<LibraryDoc['seccion'], string>
  documentos: LibraryDoc[]
}

export interface AdminVisits {
  dias: number
  visitas: number
  visitantes: number
  ahora: number
  moviles: number
  con_cuenta: number
  paises: { pais: string; visitas: number; visitantes: number }[]
  por_dia: { dia: string; visitas: number; visitantes: number }[]
  paginas: { ruta: string; visitas: number }[]
  referentes: { origen: string; visitas: number }[]
  directas: number
}

export interface WorkshopSite {
  slug: string
  version: number
  estado: 'vacio' | 'construyendo' | 'listo' | 'error'
  error?: string
  ajustes?: number
  actualizado?: string
  ultimo_ajuste?: string
  url: string | null
}

export interface Workshop {
  empresa_existente: boolean
  especificacion: { id: string; markdown: string } | null
  plan_mejoras: { id: string; markdown: string } | null
  sitios: { landing: WorkshopSite | null; prototipo: WorkshopSite | null }
  interesados: number
  precio_prototipo: number
  precio_ajuste: number
  ajustes_gratis: number
}

export interface Lead {
  id: string
  nombre: string | null
  correo: string | null
  celular: string | null
  mensaje: string | null
  pagina: string
  fecha: string
}

export interface CheckIn {
  fecha: string
  valores: Record<string, number>
  nota: string
  lectura: string
}

export interface Graduation {
  nivel7_cerrado: boolean
  graduada: boolean
  estado: 'pendiente' | 'preparando' | 'lista' | 'error'
  fecha?: string
  certificado?: string
  frase?: string
  kpis?: { nombre: string; meta: number; unidad: string; frecuencia: string }[]
  board?: { decision: string; preparacion: number } | null
  libro: { id: string; markdown: string } | null
  seguimientos: CheckIn[]
  empresa?: string
  fundador?: string
  identidad?: CompanyIdentity
}
