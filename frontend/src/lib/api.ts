import type {
  BoardRoomResult,
  ChatResponse,
  Company,
  DocumentRecord,
  GateReviewResult,
  Nivel1Status,
  Project,
  Score,
  TokenResponse,
  User,
} from './types'

const API_BASE = '/api/v1'
const TOKEN_KEY = 'adan_token'

export class ApiError extends Error {
  readonly status: number

  constructor(message: string, status: number) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

function detailMessage(detail: unknown, status: number): string {
  if (typeof detail === 'string') return detail
  // Errores de validación de FastAPI: [{loc, msg, type}, ...]
  if (Array.isArray(detail)) {
    const msgs = detail
      .map((d) => (d && typeof d === 'object' && 'msg' in d ? String(d.msg) : ''))
      .filter(Boolean)
    if (msgs.length) return msgs.join('; ')
  }
  return `HTTP ${status}`
}

export class ApiClient {
  token: string | null

  constructor() {
    this.token = localStorage.getItem(TOKEN_KEY)
  }

  setToken(token: string | null): void {
    this.token = token
    if (token) {
      localStorage.setItem(TOKEN_KEY, token)
    } else {
      localStorage.removeItem(TOKEN_KEY)
    }
  }

  async request<T>(path: string, options: RequestInit = {}): Promise<T> {
    const headers = new Headers(options.headers)
    headers.set('Content-Type', 'application/json')
    if (this.token) {
      headers.set('Authorization', `Bearer ${this.token}`)
    }

    const response = await fetch(`${API_BASE}${path}`, { ...options, headers })

    if (!response.ok) {
      const body: { detail?: unknown } = await response.json().catch(() => ({}))
      throw new ApiError(detailMessage(body.detail, response.status), response.status)
    }

    return (await response.json()) as T
  }

  // Auth
  async register(email: string, name: string, password: string): Promise<TokenResponse> {
    const data = await this.request<TokenResponse>('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, name, password }),
    })
    this.setToken(data.access_token)
    return data
  }

  async login(email: string, password: string): Promise<TokenResponse> {
    const data = await this.request<TokenResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    })
    this.setToken(data.access_token)
    return data
  }

  getMe(): Promise<User> {
    return this.request<User>('/auth/me')
  }

  // Companies
  createCompany(name: string, description: string, industry: string, country: string): Promise<Company> {
    return this.request<Company>('/companies/', {
      method: 'POST',
      body: JSON.stringify({ name, description, industry, country }),
    })
  }

  getCompanies(): Promise<Company[]> {
    return this.request<Company[]>('/companies/')
  }

  getCompany(id: string): Promise<Company> {
    return this.request<Company>(`/companies/${id}`)
  }

  getProject(companyId: string): Promise<Project> {
    return this.request<Project>(`/companies/${companyId}/project`)
  }

  // Nivel 1
  getNivel1Status(companyId: string): Promise<Nivel1Status> {
    return this.request<Nivel1Status>(`/nivel1/${companyId}/status`)
  }

  chat(companyId: string, message: string, conversationId?: string | null): Promise<ChatResponse> {
    return this.request<ChatResponse>(`/nivel1/${companyId}/chat`, {
      method: 'POST',
      body: JSON.stringify({ message, conversation_id: conversationId ?? null }),
    })
  }

  runBoardRoom(companyId: string): Promise<BoardRoomResult> {
    return this.request<BoardRoomResult>(`/nivel1/${companyId}/board-room`, { method: 'POST' })
  }

  generateDiagnosis(companyId: string): Promise<DocumentRecord> {
    return this.request<DocumentRecord>(`/nivel1/${companyId}/diagnosis`, { method: 'POST' })
  }

  gateReview(companyId: string): Promise<GateReviewResult> {
    return this.request<GateReviewResult>(`/nivel1/${companyId}/gate-review`, { method: 'POST' })
  }

  getScores(companyId: string): Promise<Score[]> {
    return this.request<Score[]>(`/nivel1/${companyId}/scores`)
  }

  getDocuments(companyId: string): Promise<DocumentRecord[]> {
    return this.request<DocumentRecord[]>(`/nivel1/${companyId}/documents`)
  }

  logout(): void {
    this.setToken(null)
  }
}

export function errorMessage(err: unknown): string {
  return err instanceof Error ? err.message : String(err)
}

export const api = new ApiClient()
