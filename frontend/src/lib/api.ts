import type {
  BoardConsensus, BoardRoomInput, ChatResponse, Company, CompanyInput, DecideInput, Decision, DocumentRecord,
  Evidence, EvidenceInput, GatePreview, GateReviewResult, LevelView, Nivel1Status, OnboardingState, Score,
  ScoreOverview, TimelineEvent, TokenResponse, TwinKind, TwinOverview, User,
} from '../types'

const API_BASE = '/api/v1'

export class ApiError extends Error {
  readonly status: number

  constructor(message: string, status: number) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

interface ErrorBody {
  detail?: string | { msg: string }[]
}

// La sesión vive en la cookie httpOnly `adan_session` que pone el backend (WO-097):
// el token nunca pasa por JavaScript, así que un XSS no puede robarlo.
// `X-Requested-With` es la marca anti-CSRF que el backend exige a toda petición con cookie.
async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'X-Requested-With': 'adan',
      ...options.headers,
    },
    credentials: 'same-origin',
  })

  if (!response.ok) {
    const body: ErrorBody = await response.json().catch(() => ({ detail: 'Request failed' }))
    // Los errores de validación (422) llegan como lista
    const detail = Array.isArray(body.detail) ? body.detail.map((d) => d.msg).join('. ') : body.detail
    throw new ApiError(detail || `HTTP ${response.status}`, response.status)
  }

  if (response.status === 204) return undefined as T
  return response.json() as Promise<T>
}

const post = <T>(path: string, body?: unknown) =>
  request<T>(path, { method: 'POST', body: body === undefined ? undefined : JSON.stringify(body) })

export const api = {
  // Auth
  register: (email: string, name: string, password: string, consent: { acceptDataPolicy: boolean; shareAggregated: boolean }) =>
    post<TokenResponse>('/auth/register', {
      email, name, password, accept_data_policy: consent.acceptDataPolicy, share_aggregated: consent.shareAggregated,
    }),
  // Onboarding y consentimiento (WO-108)
  getOnboarding: () => request<OnboardingState>('/onboarding/me'),
  startOnboarding: (companyName: string, stage: 'idea' | 'existing') =>
    post<{ company_id: string; first_question: string | null }>('/onboarding/start', { company_name: companyName, stage }),
  setConsent: (purpose: 'data_processing' | 'aggregated_intelligence', granted: boolean) =>
    post<OnboardingState['consents']>('/onboarding/consents', { purpose, granted }),
  getLevels: (companyId: string) => request<LevelView[]>(`/companies/${companyId}/levels`),
  getCsiStatus: (companyId: string) => request<{ connected: boolean }>(`/scoring/${companyId}/csi`),
  searchCsi: (companyId: string, query?: string) => post<Evidence[]>(`/scoring/${companyId}/csi/search`, { query }),
  confirmEvidence: (companyId: string, evidenceId: string) =>
    post<Evidence>(`/scoring/${companyId}/evidence/${evidenceId}/confirm`),
  login: (email: string, password: string) => post<TokenResponse>('/auth/login', { email, password }),
  getMe: () => request<User>('/auth/me'),
  // Cierra la sesión en todos los dispositivos
  logout: () => post<void>('/auth/logout').catch(() => undefined),

  // Companies
  createCompany: (input: CompanyInput) => post<Company>('/companies/', input),
  getCompanies: () => request<Company[]>('/companies/'),
  getCompany: (id: string) => request<Company>(`/companies/${id}`),

  // Nivel 1
  getNivel1Status: (companyId: string) => request<Nivel1Status>(`/nivel1/${companyId}/status`),
  chat: (companyId: string, message: string, conversationId?: string) =>
    post<ChatResponse>(`/nivel1/${companyId}/chat`, { message, conversation_id: conversationId }),
  runBoardRoom: (companyId: string, input?: BoardRoomInput) =>
    post<BoardConsensus>(`/nivel1/${companyId}/board-room`, input ?? {}),
  generateDiagnosis: (companyId: string) => post<DocumentRecord>(`/nivel1/${companyId}/diagnosis`),
  gateReview: (companyId: string) => post<GateReviewResult>(`/nivel1/${companyId}/gate-review`),
  getScores: (companyId: string) => request<Score[]>(`/nivel1/${companyId}/scores`),
  advanceAnyway: (companyId: string) => post<GateReviewResult>(`/nivel1/${companyId}/advance-anyway`),
  // Evidencia y Scoring (WO-107)
  listEvidence: (companyId: string) => request<Evidence[]>(`/scoring/${companyId}/evidence`),
  addEvidence: (companyId: string, input: EvidenceInput) => post<Evidence>(`/scoring/${companyId}/evidence`, input),
  archiveEvidence: (companyId: string, evidenceId: string, reason: string) =>
    post<Evidence>(`/scoring/${companyId}/evidence/${evidenceId}/archive`, { reason }),
  getScoresOverview: (companyId: string) => request<ScoreOverview[]>(`/scoring/${companyId}/scores`),
  calculateScore: (companyId: string, scoreType: string) =>
    post<ScoreOverview>(`/scoring/${companyId}/scores/${scoreType}/calculate`),
  getGatePreview: (companyId: string, level = 1) => request<GatePreview>(`/scoring/${companyId}/gate/${level}`),
  getDocuments: (companyId: string) => request<DocumentRecord[]>(`/nivel1/${companyId}/documents`),
  getDecisions: (companyId: string) => request<Decision[]>(`/nivel1/${companyId}/decisions`),
  decide: (companyId: string, decisionId: string, action: 'approve' | 'reject') =>
    post<Decision>(`/nivel1/${companyId}/decisions/${decisionId}`, { action }),

  // Gemelo Digital (WO-098)
  getTwin: (companyId: string) => request<TwinOverview>(`/twin/${companyId}`),
  getTwinKinds: () => request<TwinKind[]>('/twin/kinds'),
  // Cursor (fecha, id) del último evento recibido: no se pierden eventos con la misma marca de tiempo
  getTimeline: (companyId: string, before?: Pick<TimelineEvent, 'created_at' | 'id'>) =>
    request<TimelineEvent[]>(`/twin/${companyId}/timeline?limit=50${before
      ? `&before=${encodeURIComponent(before.created_at)}&before_id=${encodeURIComponent(before.id)}` : ''}`),
  getTwinDecisions: (companyId: string) => request<Decision[]>(`/twin/${companyId}/decisions`),
  presentDecision: (companyId: string, decisionId: string) =>
    post<Decision>(`/twin/${companyId}/decisions/${decisionId}/present`),
  decideDecision: (companyId: string, decisionId: string, input: DecideInput) =>
    post<Decision>(`/twin/${companyId}/decisions/${decisionId}/decide`, input),
  executeDecision: (companyId: string, decisionId: string, businessDecisionTitle?: string) =>
    post<Decision>(`/twin/${companyId}/decisions/${decisionId}/execute`,
      businessDecisionTitle ? { business_decision_title: businessDecisionTitle } : {}),
}

export function errorMessage(err: unknown): string {
  return err instanceof Error ? err.message : String(err)
}
