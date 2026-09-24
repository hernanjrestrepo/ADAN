const API_BASE = '/api/v1'

// La sesión vive en la cookie httpOnly `adan_session` que pone el backend (WO-097):
// el token nunca pasa por JavaScript, así que un XSS no puede robarlo.
// `X-Requested-With` es la marca anti-CSRF que el backend exige a toda petición con cookie.
class ApiClient {
  async request(path, options = {}) {
    const headers = {
      'Content-Type': 'application/json',
      'X-Requested-With': 'adan',
      ...options.headers,
    }

    const response = await fetch(`${API_BASE}${path}`, {
      ...options,
      headers,
      credentials: 'same-origin',
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Request failed' }))
      // Los errores de validación (422) llegan como lista
      const detail = Array.isArray(error.detail)
        ? error.detail.map((d) => d.msg).join('. ')
        : error.detail
      throw new Error(detail || `HTTP ${response.status}`)
    }

    if (response.status === 204) return null
    return response.json()
  }

  // Auth
  async register(email, name, password) {
    return this.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, name, password }),
    })
  }

  async login(email, password) {
    return this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    })
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

  // Cierra la sesión en todos los dispositivos
  async logout() {
    await this.request('/auth/logout', { method: 'POST' }).catch(() => {})
  }
}

export const api = new ApiClient()
