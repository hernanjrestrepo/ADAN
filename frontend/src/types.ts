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

export type DecisionStatus = 'proposed' | 'approved' | 'rejected' | 'executed'

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
  disclaimer: string
}

export interface CompanyInput {
  name: string
  description: string
  industry: string
  country: string
}
