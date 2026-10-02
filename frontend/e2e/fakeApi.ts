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

// Gemelo Digital (WO-098)
export const TWIN_DECISION = {
  id: 'dec1', project_id: 'p1', title: 'Board Room: PROCEED', description: 'El Board recomienda avanzar',
  proposed_by: 'Board Room', status: 'proposed', reasoning: 'CTO, CMO y Producto ven demanda clara', confidence_level: 72,
  created_at: '2026-09-25T10:00:00', disagreement: 'CFO votó PIVOT: el margen es bajo',
  options: [
    { key: 'PROCEED', label: 'Avanzar', rationale: 'Demanda clara', evidence_level: 'alta', confidence: 78, votes: 5 },
    { key: 'PIVOT', label: 'Pivotar', rationale: 'CFO: margen bajo', evidence_level: 'baja', confidence: 60, votes: 1 },
    { key: 'STOP', label: 'Detener', rationale: '', evidence_level: 'baja', confidence: 0, votes: 0 },
  ],
  recommended_option: 'PROCEED', chosen_option: null, divergence: null,
  prior_decisions: [{ id: 'old', title: 'Cerrar Nivel 0', status: 'executed', chosen_option: 'CLOSE' }],
  presented_at: null, decided_at: null, executed_at: null, business_decision: null,
}

const TWIN_OVERVIEW = {
  company: { id: 'c1', name: 'Panadería Digital', status: 'active', version: 3, founded_on: null, jurisdiction: null,
    legal_structure: null, intangibles: {} },
  identity: { age_years: 0.1, maturity: 0.2, lifecycle_stage: 'nacimiento', maturation_velocity_per_year: null },
  counts: { brands: 1, competitors: 2 },
  lineage: [],
}

const TWIN_KINDS = [
  { key: 'brands', label: 'Marca', label_plural: 'Marcas', cluster: 'identidad', cluster_label: 'Identidad y Gobernanza', pattern: null },
  { key: 'competitors', label: 'Competidor', label_plural: 'Competidores', cluster: 'mercado', cluster_label: 'Mercado y Comercial', pattern: null },
]

interface TimelineItem {
  id: string
  event_type: string
  entity_type: string
  entity_id: string
  category: string
  data: Record<string, string>
  actor_type: string
  actor_id: string
  created_at: string
}

export interface Call {
  method: string
  path: string
  body: unknown
  headers: Record<string, string>
}

const LEVEL_NAMES = ['El Dolor', 'Propuesta de Valor', 'Plan de Negocios', 'MVP', 'Validación Simulada', 'Lanzamiento',
  'Escalamiento']
export const LEVELS = LEVEL_NAMES.map((name, i) => ({
  id: `l${i + 1}`, number: i + 1, name, status: i === 0 ? 'active' : 'blocked', completed_at: null,
  discovers: `Qué descubre el Nivel ${i + 1}`, deliverable: `Entregable ${i + 1}`, score_key: i === 0 ? 'problem' : null,
  score: i === 0 ? { value: 42, confidence: 55 } : null,
  cards: i === 0 ? [{ id: 'card1', title: 'Descubrimiento del Dolor', description: '¿Qué problema real resuelves?',
    card_type: 'pain_discovery', status: 'active' }] : [],
}))

export class FakeApi {
  loggedIn = false
  companies: typeof COMPANY[] = []
  messages: { id: string; role: string; content: string; created_at: string; agent_name?: string | null }[] = []
  levelStatus: 'active' | 'completed' = 'active'
  calls: Call[] = []
  twinDecisions: Record<string, unknown>[] = [structuredClone(TWIN_DECISION)]
  evidence: Record<string, unknown>[] = []
  gateApproved = true
  csiConnected = false
  aggregated = false
  timeline: TimelineItem[] = [
    { id: 'e2', event_type: 'entity_created', entity_type: 'brands', entity_id: 'b1', category: 'domain',
      data: { label: 'Pan de Ana' }, actor_type: 'user', actor_id: 'u1', created_at: '2026-09-25T09:00:00' },
    { id: 'e1', event_type: 'twin_born', entity_type: 'companies', entity_id: 'c1', category: 'domain',
      data: { label: 'Panadería Digital' }, actor_type: 'user', actor_id: 'u1', created_at: '2026-09-24T00:00:00' },
  ]
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

    if (route_ === 'GET /onboarding/me') {
      const has = this.companies.length > 0
      return this.json(route, 200, {
        identity: has
          ? { key: 'responsable', label: 'Responsable de Empresa', step: 2, of: 5,
            next: { key: 'lider_activo', label: 'Líder Activo', milestone: 'Recibiste tu primer Diagnóstico real del Nivel 1' } }
          : { key: 'usuario', label: 'Usuario', step: 1, of: 5,
            next: { key: 'responsable', label: 'Responsable de Empresa', milestone: 'Confirmaste que eres responsable de una Empresa' } },
        consents: this.consents(),
        next: has ? { step: 'first_answer', company_id: this.companies[0]!.id } : { step: 'company', company_id: null },
        policy_version: '2026-10',
      })
    }
    if (route_ === 'POST /onboarding/start') {
      const company = { ...COMPANY, id: 'c-new', name: body.company_name }
      this.companies.push(company)
      return this.json(route, 201, { company_id: 'c-new', first_question: 'Hola, Ana. ¿Qué problema quieres resolver?' })
    }
    if (route_ === 'POST /onboarding/consents') {
      this.aggregated = body.granted
      return this.json(route, 200, this.consents())
    }
    if (method === 'GET' && path.endsWith('/levels')) return this.json(route, 200, LEVELS)
    const companyMatch = path.match(/^\/companies\/([^/]+)$/)
    if (method === 'GET' && companyMatch) {
      const found = this.companies.find((c) => c.id === companyMatch[1])
      return found ? this.json(route, 200, found) : this.json(route, 404, { detail: 'Company not found' })
    }
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
    if (path.startsWith('/scoring/')) return this.handleScoring(route, method, path, body)
    if (method === 'POST' && path.endsWith('/advance-anyway')) {
      return this.json(route, 200, {
        approved: false, scores: [], level_status: 'active', missing: ['Al menos 1 dato verificable externamente'],
        message: 'Todavía no hay evidencia suficiente para cerrar el Nivel 1.',
        decisions: [{ id: 'd2', project_id: 'p1', title: 'Cerrar Nivel 1', description: null, proposed_by: 'Gate Review',
          status: 'proposed', reasoning: null, confidence_level: 20, recommended_option: 'CONTINUE',
          created_at: '2026-10-02T00:00:00' }],
        disclaimer: 'aviso',
      })
    }
    if (method === 'POST' && path.endsWith('/gate-review') && !this.gateApproved) {
      return this.json(route, 200, {
        approved: false, scores: [], level_status: 'active', decisions: [], disclaimer: 'aviso',
        message: 'Todavía no hay evidencia suficiente para cerrar el Nivel 1.',
        missing: ['Al menos 1 dato verificable externamente que respalde el problema'],
      })
    }
    if (method === 'POST' && path.endsWith('/gate-review')) {
      return this.json(route, 200, {
        approved: true, scores: [], level_status: 'active', message: 'Falta tu aprobación para cerrar el Nivel 1.',
        decisions: [{ id: 'd1', project_id: 'p1', title: 'Cerrar Nivel 1', description: null, proposed_by: 'Gate',
          status: 'proposed', reasoning: null, confidence_level: 92, created_at: '2026-09-24T00:00:00' }],
        disclaimer: 'aviso',
      })
    }
    if (path.startsWith('/twin/')) return this.handleTwin(route, method, path, body)
    if (method === 'POST' && path.includes('/decisions/')) {
      if (body.action === 'approve') this.levelStatus = 'completed'
      return this.json(route, 200, { id: 'd1', status: body.action === 'approve' ? 'executed' : 'rejected' })
    }
    return this.json(route, 404, { detail: `Sin simular: ${route_}` })
  }

  private consents() {
    return {
      data_processing: { purpose: 'data_processing', text: 'Tratamiento de mis datos para prestarme el servicio de ADÁN',
        granted: true, policy_version: '2026-10', since: '2026-10-02T00:00:00' },
      aggregated_intelligence: { purpose: 'aggregated_intelligence', text: 'Uso de mis datos anonimizados y agregados',
        granted: this.aggregated, policy_version: '2026-10', since: '2026-10-02T00:00:00' },
    }
  }

  private gatePreview() {
    const count = (kind: string) =>
      this.evidence.filter((e) => e.kind === kind && e.polarity === 'supports' && e.confirmed !== false).length
    const external = count('external')
    const strong = external + count('testimony')
    const missing = [
      ...(external < 1 ? ['Al menos 1 dato verificable externamente que respalde el problema'] : []),
      ...(strong < 2 ? [`Al menos 2 evidencias a favor entre datos externos y testimonios (tienes ${strong})`] : []),
    ]
    const value = Math.round((100 * (external + 0.6 * count('testimony'))) / (external + 0.6 * count('testimony') + 1.5))
    return {
      level_number: 1, sufficient: missing.length === 0, missing, score_type: 'problem', value,
      confidence: missing.length ? 30 : 80, reasoning: '',
      breakdown: {
        external: { supports: external, contradicts: 0 }, testimony: { supports: count('testimony'), contradicts: 0 },
        inference: { supports: 0, contradicts: 0 },
      },
    }
  }

  private handleScoring(route: Route, method: string, path: string, body: Record<string, unknown> | null) {
    if (method === 'GET' && path === '/scoring/c1/evidence') return this.json(route, 200, this.evidence)
    if (method === 'GET' && path === '/scoring/c1/csi') return this.json(route, 200, { connected: this.csiConnected })
    if (method === 'POST' && path === '/scoring/c1/csi/search') {
      const item = { id: `csi${this.evidence.length + 1}`, dimension: 'problem', status: 'active', level_number: 1,
        kind: 'external', kind_label: 'Dato verificable externamente', polarity: 'supports',
        claim: 'El 38 % de las panaderías reporta pérdidas diarias de pan', source: 'https://csi.example/estudio',
        created_by: 'agent:CSI', confidence_level: null, confirmed: false,
        verification: { status: 'verified', title: 'Estudio CSI', checked_at: '2026-10-02T00:00:00' },
        created_at: '2026-10-02T00:00:00' }
      this.evidence.unshift(item)
      return this.json(route, 200, [item])
    }
    const confirm = path.match(/^\/scoring\/c1\/evidence\/([^/]+)\/confirm$/)
    if (method === 'POST' && confirm) {
      const item = this.evidence.find((e) => e.id === confirm[1])
      if (item) item.confirmed = true
      return this.json(route, 200, item)
    }
    if (method === 'POST' && path === '/scoring/c1/evidence') {
      if (body?.kind === 'external' && !body.source) {
        return this.json(route, 422, { detail: 'Un dato verificable externamente necesita su fuente' })
      }
      const verification = typeof body?.source === 'string' && body.source.startsWith('http')
        ? { status: 'verified', title: 'Estudio de pérdidas de pan', checked_at: '2026-10-02T00:00:00' } : null
      const item = { id: `e${this.evidence.length + 1}`, dimension: 'problem', status: 'active', level_number: 1,
        kind_label: body?.kind, created_by: 'user:u1', confidence_level: null, created_at: '2026-10-02T00:00:00',
        source: null, confirmed: true, verification, ...body }
      this.evidence.unshift(item)
      return this.json(route, 201, item)
    }
    if (method === 'GET' && path === '/scoring/c1/gate/1') return this.json(route, 200, this.gatePreview())
    if (method === 'GET' && path === '/scoring/c1/scores') {
      const labels: [string, string, number | null][] = [['problem', 'Problem Score', 1], ['solution', 'Solution Score', 2],
        ['business', 'Business Score', 3], ['product', 'Product Score', 4], ['market', 'Market Score', 5],
        ['execution', 'Execution Score', 5], ['responsible', 'Score del Responsable', null], ['venture', 'Venture Score', 6]]
      const gate = this.gatePreview()
      return this.json(route, 200, labels.map(([key, label, level]) => {
        const available = key === 'problem' || key === 'responsible'
        return {
          key, label, measures: 'mide algo', level, family: key === 'responsible' || key === 'venture' ? 'continuous' : 'diagnostic',
          available, unavailable_reason: available ? null : key === 'venture' ? 'Nace en el Nivel 6' : `Se abre en el Nivel ${level}`,
          evidence_count: key === 'problem' ? this.evidence.length : 0,
          latest: key === 'problem' && this.evidence.length
            ? { id: 's1', value: gate.value, confidence: gate.confidence, reasoning: 'Problem Score: con evidencia.',
              breakdown: gate.breakdown, created_at: '2026-10-02T00:00:00' }
            : null,
        }
      }))
    }
    return this.json(route, 404, { detail: `Sin simular: ${method} ${path}` })
  }

  private handleTwin(route: Route, method: string, path: string, body: Record<string, unknown> | null) {
    if (method === 'GET' && path === '/twin/kinds') return this.json(route, 200, TWIN_KINDS)
    if (method === 'GET' && path === '/twin/c1') return this.json(route, 200, TWIN_OVERVIEW)
    if (method === 'GET' && path === '/twin/c1/decisions') return this.json(route, 200, this.twinDecisions)
    if (method === 'GET' && path === '/twin/c1/timeline') return this.json(route, 200, this.timeline)
    const match = path.match(/^\/twin\/c1\/decisions\/([^/]+)\/(present|decide|execute)$/)
    const decision = match && this.twinDecisions.find((d) => d.id === match[1])
    if (!match || !decision) return this.json(route, 404, { detail: `Sin simular: ${method} ${path}` })
    const action = match[2]
    const now = new Date().toISOString()
    if (action === 'present') {
      decision.status = 'presented'
      decision.presented_at = now
    } else if (action === 'decide') {
      if (body?.action === 'reject') {
        decision.status = 'rejected'
      } else {
        const chosen = (body?.chosen_option as string | undefined) ?? 'PROCEED'
        if (chosen !== decision.recommended_option) {
          // Mismas reglas del backend: decidir distinto exige riesgos y responsabilidad (§2.5)
          const risks = (body?.risks_assumed as string[] | undefined) ?? []
          if (!risks.length || !body?.responsibility_statement) {
            return this.json(route, 409, { detail: 'Al decidir distinto a lo recomendado hay que declarar los riesgos asumidos' })
          }
          decision.divergence = {
            chosen_option: { key: chosen, label: 'Pivotar' }, recommended_option: { key: 'PROCEED', label: 'Avanzar', rationale: 'Demanda clara' },
            evidence_level: { chosen: 'baja', recommended: 'alta' }, confidence: { chosen: 60, recommended: 78 },
            risks_assumed: risks, responsibility_assumed: body.responsibility_statement,
          }
        }
        decision.status = 'approved'
        decision.chosen_option = chosen
      }
      decision.decided_at = now
    } else {
      decision.status = 'executed'
      decision.executed_at = now
      if (body?.business_decision_title) {
        decision.business_decision = { id: 'bd1', title: body.business_decision_title, state: 'executed' }
      }
    }
    this.timeline.unshift({ id: `e${this.timeline.length + 1}`, event_type: 'state_changed', entity_type: 'decisions',
      entity_id: decision.id as string, category: 'domain', data: { label: decision.title as string, to: decision.status as string },
      actor_type: 'user', actor_id: 'u1', created_at: now })
    return this.json(route, 200, decision)
  }
}
