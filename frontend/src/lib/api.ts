import type {
  BoardConsensus, ChatResponse, Company, CompanyInput, Decision, DocumentRecord, GateReviewResult,
  Nivel1Status, Score, TokenResponse, User,
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
  register: (email: string, name: string, password: string) =>
    post<TokenResponse>('/auth/register', { email, name, password }),
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
  runBoardRoom: (companyId: string) => post<BoardConsensus>(`/nivel1/${companyId}/board-room`),
  generateDiagnosis: (companyId: string) => post<DocumentRecord>(`/nivel1/${companyId}/diagnosis`),
  gateReview: (companyId: string) => post<GateReviewResult>(`/nivel1/${companyId}/gate-review`),
  getScores: (companyId: string) => request<Score[]>(`/nivel1/${companyId}/scores`),
  getDocuments: (companyId: string) => request<DocumentRecord[]>(`/nivel1/${companyId}/documents`),
  getDecisions: (companyId: string) => request<Decision[]>(`/nivel1/${companyId}/decisions`),
  decide: (companyId: string, decisionId: string, action: 'approve' | 'reject') =>
    post<Decision>(`/nivel1/${companyId}/decisions/${decisionId}`, { action }),
}

export function errorMessage(err: unknown): string {
  return err instanceof Error ? err.message : String(err)
}
