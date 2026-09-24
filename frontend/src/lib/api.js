const API_BASE = '/api/v1'

class ApiClient {
  constructor() {
    this.token = localStorage.getItem('adan_token')
  }

  setToken(token) {
    this.token = token
    if (token) {
      localStorage.setItem('adan_token', token)
    } else {
      localStorage.removeItem('adan_token')
    }
  }

  async request(path, options = {}) {
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers,
    }
    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`
    }

    const response = await fetch(`${API_BASE}${path}`, {
      ...options,
      headers,
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Request failed' }))
      throw new Error(error.detail || `HTTP ${response.status}`)
    }

    return response.json()
  }

  // Auth
  async register(email, name, password) {
    const data = await this.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, name, password }),
    })
    this.setToken(data.access_token)
    return data
  }

  async login(email, password) {
    const data = await this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    })
    this.setToken(data.access_token)
    return data
  }

  async getMe() {
    return this.request('/auth/me')
  }

  // Companies
  async createCompany(name, description, industry, country) {
    return this.request('/companies/', {
      method: 'POST',
      body: JSON.stringify({ name, description, industry, country }),
    })
  }

  async getCompanies() {
    return this.request('/companies/')
  }

  async getCompany(id) {
    return this.request(`/companies/${id}`)
  }

  async getProject(companyId) {
    return this.request(`/companies/${companyId}/project`)
  }

  // Nivel 1
  async getNivel1Status(companyId) {
    return this.request(`/nivel1/${companyId}/status`)
  }

  async chat(companyId, message, conversationId) {
    return this.request(`/nivel1/${companyId}/chat`, {
      method: 'POST',
      body: JSON.stringify({ message, conversation_id: conversationId }),
    })
  }

  async runBoardRoom(companyId) {
    return this.request(`/nivel1/${companyId}/board-room`, {
      method: 'POST',
    })
  }

  async generateDiagnosis(companyId) {
    return this.request(`/nivel1/${companyId}/diagnosis`, {
      method: 'POST',
    })
  }

  async gateReview(companyId) {
    return this.request(`/nivel1/${companyId}/gate-review`, {
      method: 'POST',
    })
  }

  async getScores(companyId) {
    return this.request(`/nivel1/${companyId}/scores`)
  }

  async getDocuments(companyId) {
    return this.request(`/nivel1/${companyId}/documents`)
  }

  async getDecisions(companyId) {
    return this.request(`/nivel1/${companyId}/decisions`)
  }

  // action: 'approve' | 'reject'
  async decide(companyId, decisionId, action) {
    return this.request(`/nivel1/${companyId}/decisions/${decisionId}`, {
      method: 'POST',
      body: JSON.stringify({ action }),
    })
  }

  logout() {
    this.setToken(null)
  }
}

export const api = new ApiClient()
