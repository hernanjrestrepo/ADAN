// Tipos de las respuestas del backend (backend/app/schemas/schemas.py y api/v1/nivel1.py).

export interface User {
  id: string
  email: string
  name: string
  role: string
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
