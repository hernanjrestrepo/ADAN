import type { Page, Request, Route } from '@playwright/test'

// Backend simulado para las pruebas de interfaz: mismas rutas y formas que backend/app.
// Registra cada petición para poder verificar lo que la interfaz envía.

export const USER = { id: 'u1', email: 'ana@example.com', name: 'Ana', role: 'primary_user' }

const COMPANY = {
  id: 'c1', name: 'Panadería Digital', description: 'Pan del día', industry: 'Alimentos', country: 'Colombia',
  maturity: 0.2, status: 'active', version: 1, created_at: '2026-09-24T00:00:00',
}

export const BOARD_NO_CONSENSUS = {
  decision: 'NO_CONSENSUS', score: 0, confidence: 0, summary: 'Sin quórum',
  votes: [
    { agent: 'CEO', analysis: 'No hay datos suficientes', justification: 'x', vote: 'ABSTAIN', confidence: 0,
      key_strengths: [], key_concerns: [], questions: [], model: 'qwen', duration_s: 1 },
    { agent: 'CFO', analysis: 'El margen es bajo', justification: 'x', vote: 'STOP', confidence: 70,
      key_strengths: [], key_concerns: [], questions: [], model: 'qwen', duration_s: 1 },
  ],
  concerns_unanimous: [], concerns_majority: [], strengths_unanimous: [],
  dissent: 'CFO: STOP — El margen es bajo', disclaimer: 'aviso',
  objective: 'Evaluar el dolor de las panaderías', decision_at_stake: '¿Avanzar, ajustar o detenerse?',
  synthesis: '', evidence_requests: [], next_steps: [], client_question: '', client_position: '', minutes: '# Acta',
}

export const BOARD_PROCEED = {
  ...BOARD_NO_CONSENSUS,
  decision: 'PROCEED', score: 72, confidence: 78, summary: 'Avanzar',
  votes: ['CTO', 'CFO', 'CMO', 'Legal', 'Producto', 'Operaciones'].map((agent) => ({
    agent, analysis: `Análisis de ${agent}`, justification: 'x', vote: agent === 'CFO' ? 'PIVOT' : 'PROCEED',
    confidence: 78, key_strengths: [], key_concerns: [], questions: [], model: 'claude-opus-5', duration_s: 3,
  })),
  dissent: 'CFO votó PIVOT: el margen es bajo',
  synthesis: 'El Board recomienda avanzar, con el disenso del CFO sobre el margen.',
  evidence_requests: ['Ventas de pan de los últimos 3 meses'], next_steps: ['Entrevistar 5 panaderías'],
  client_question: '¿Empiezo en Medellín?', client_position: 'Quiero lanzar ya',
}

export interface Call {
  method: string
  path: string
  body: unknown
  headers: Record<string, string>
}

export class FakeApi {
  loggedIn = false
  companies: typeof COMPANY[] = []
  messages: { id: string; role: string; content: string; created_at: string; agent_name?: string | null }[] = []
  levelStatus: 'active' | 'completed' = 'active'
  calls: Call[] = []
  // Respuestas forzadas por ruta ("POST /nivel1/c1/board-room" -> [status, body])
  overrides = new Map<string, [number, unknown]>()

  withCompany() {
    this.companies = [COMPANY]
    return this
  }

  async install(page: Page) {
    await page.route('**/api/v1/**', (route) => this.handle(route, route.request()))
  }

  callsTo(method: string, path: string) {
    return this.calls.filter((c) => c.method === method && c.path === path)
  }

  private json(route: Route, status: number, body: unknown) {
    return route.fulfill({ status, contentType: 'application/json', body: JSON.stringify(body) })
  }

  private handle(route: Route, request: Request) {
    const url = new URL(request.url())
    const path = url.pathname.replace('/api/v1', '')
    const method = request.method()
    const body = request.postData() ? JSON.parse(request.postData() as string) : null
    this.calls.push({ method, path, body, headers: request.headers() })

    const forced = this.overrides.get(`${method} ${path}`)
    if (forced) return this.json(route, forced[0], forced[1])

    const route_ = `${method} ${path}`
    if (route_ === 'GET /auth/me') {
      return this.loggedIn ? this.json(route, 200, USER) : this.json(route, 401, { detail: 'Not authenticated' })
    }
    if (route_ === 'POST /auth/login' || route_ === 'POST /auth/register') {
      this.loggedIn = true
      return this.json(route, route_.endsWith('register') ? 201 : 200, { access_token: 't', token_type: 'bearer', user: USER })
    }
    if (route_ === 'POST /auth/logout') {
      this.loggedIn = false
      return route.fulfill({ status: 204 })
    }
    if (!this.loggedIn) return this.json(route, 401, { detail: 'Not authenticated' })

    if (route_ === 'GET /companies/') return this.json(route, 200, this.companies)
    if (route_ === 'POST /companies/') {
      const company = { ...COMPANY, id: 'c-new', name: body.name }
      this.companies.push(company)
      return this.json(route, 201, company)
    }
    const companyId = path.split('/')[2]
    const company = this.companies.find((c) => c.id === companyId) ?? COMPANY
    if (method === 'GET' && path.endsWith('/status')) {
      return this.json(route, 200, {
        company, project: { id: 'p1', company_id: company.id, name: 'P', status: 'active' },
        level: { id: 'l1', project_id: 'p1', number: 1, name: 'El Dolor', status: this.levelStatus, completed_at: null },
        card: null, conversation: this.messages.length ? { id: 'conv1' } : null,
        messages: this.messages, scores: [], documents: [],
      })
    }
    if (method === 'POST' && path.endsWith('/chat')) {
      const now = new Date().toISOString()
      this.messages.push({ id: `m${this.messages.length}`, role: 'user', content: body.message, created_at: now })
      const reply = { id: `m${this.messages.length}`, role: 'assistant', content: '¿Cuánto pan se pierde al día?', created_at: now, agent_name: null }
      this.messages.push(reply)
      return this.json(route, 200, { message: reply, conversation_id: 'conv1', card_id: null, disclaimer: 'aviso' })
    }
    if (method === 'POST' && path.endsWith('/board-room')) return this.json(route, 200, BOARD_NO_CONSENSUS)
    if (method === 'POST' && path.endsWith('/gate-review')) {
      return this.json(route, 200, {
        approved: true, scores: [], level_status: 'active', message: 'Falta tu aprobación para cerrar el Nivel 1.',
        decisions: [{ id: 'd1', project_id: 'p1', title: 'Cerrar Nivel 1', description: null, proposed_by: 'Gate',
          status: 'proposed', reasoning: null, confidence_level: 92, created_at: '2026-09-24T00:00:00' }],
        disclaimer: 'aviso',
      })
    }
    if (method === 'POST' && path.includes('/decisions/')) {
      if (body.action === 'approve') this.levelStatus = 'completed'
      return this.json(route, 200, { id: 'd1', status: body.action === 'approve' ? 'executed' : 'rejected' })
    }
    return this.json(route, 404, { detail: `Sin simular: ${route_}` })
  }
}
