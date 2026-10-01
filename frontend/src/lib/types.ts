// Contrato con el backend (app/schemas/schemas.py y app/api/v1/nivel1.py).

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
  version: number
  created_at: string
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
  created_at: string
}

export interface Message {
  id: string
  conversation_id: string
  role: 'user' | 'assistant' | 'system' | string
  agent_name: string | null
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

export interface Decision {
  id: string
  project_id: string
  title: string
  description: string | null
  proposed_by: string | null
  status: string
  reasoning: string | null
  confidence_level: number | null
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
}

export interface BoardVote {
  agent: string
  analysis: string
  justification: string
  vote: string
  confidence: number
  key_strengths: string[]
  key_concerns: string[]
  questions: string[]
  model: string
  duration_s: number
}

export interface BoardRoomResult {
  decision: string
  score: number
  confidence: number
  summary: string
  votes: BoardVote[]
  concerns_unanimous: string[]
  concerns_majority: string[]
  strengths_unanimous: string[]
  dissent: string
}

export interface GateReviewResult {
  approved: boolean
  scores: Score[]
  decisions: Decision[]
  level_status: string
  message: string
}
