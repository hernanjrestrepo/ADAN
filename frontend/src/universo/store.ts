import { create } from 'zustand'
import {
  AGENT_BY_ID, AGENTS, ARCHETYPES, LEVELS, type AgentId, type Archetype, type GateTask, type Level, type ZoneId,
} from './data'

// Estado del recorrido. Regla de AD-FUNC-04: el XP y las insignias solo salen de evidencia (tareas del Gate
// entregadas y Niveles cerrados con tu aprobación), nunca de tiempo conectado, clics o rachas.

export type JobPhase = 'going' | 'working' | 'returning'
export interface Job { taskId: string; zone: ZoneId; phase: JobPhase; until: number }
export interface Bubble { text: string; until: number; tone?: 'vote-yes' | 'vote-no' | 'info' }
export type Vote = 'PROCEED' | 'PIVOT'
export interface BoardVote { agent: AgentId; vote: Vote; line: string }
export interface BoardSession {
  level: number
  phase: 'gathering' | 'opening' | 'voting' | 'closing' | 'decided'
  step: number
  votes: BoardVote[]
  recommendation: Vote
  opening: string
  synthesis: string
  missing: string[]
}
export interface FeedItem { id: number; text: string; color: string; at: number }

interface State {
  started: boolean
  archetypeId: string
  companyName: string
  mode: 'crear' | 'reinventar'
  level: number
  doneTasks: string[]
  closedLevels: number[]
  jobs: Partial<Record<AgentId, Job>>
  bubbles: Partial<Record<AgentId, Bubble>>
  selected: AgentId | null
  focusZone: ZoneId | null
  board: BoardSession | null
  feed: FeedItem[]
  celebration: number | null
  report: number | null
  panel: 'mision' | 'ruta' | 'ecosistema' | 'insignias' | null
  start: (archetypeId: string, name: string, mode: 'crear' | 'reinventar') => void
  reset: () => void
  goToLevel: (n: number) => void
  assign: (taskId: string) => void
  setPhase: (agent: AgentId, phase: JobPhase | null, until?: number) => void
  completeTask: (agent: AgentId) => void
  say: (agent: AgentId, text: string, ms?: number, tone?: Bubble['tone']) => void
  select: (agent: AgentId | null) => void
  focus: (zone: ZoneId | null) => void
  convene: () => void
  advanceBoard: () => void
  approveLevel: () => void
  dismissBoard: () => void
  closeCelebration: () => void
  openReport: (level: number | null) => void
  setPanel: (panel: State['panel']) => void
  log: (text: string, color?: string) => void
}

const STORAGE_KEY = 'adan-universo-v1'
type Saved = Pick<State, 'started' | 'archetypeId' | 'companyName' | 'mode' | 'level' | 'doneTasks' | 'closedLevels'>

function load(): Partial<Saved> {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? (JSON.parse(raw) as Partial<Saved>) : {}
  } catch {
    return {}
  }
}

function save(s: Saved): void {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(s))
  } catch {
    // Sin almacenamiento (modo privado): el recorrido sigue, solo no se recuerda
  }
}

export function levelOf(n: number): Level {
  return LEVELS[Math.min(Math.max(n, 1), 7) - 1] as Level
}

export function taskById(id: string): GateTask | undefined {
  for (const l of LEVELS) {
    const t = l.tasks.find((x) => x.id === id)
    if (t) return t
  }
  return undefined
}

export function archetypeOf(id: string): Archetype {
  return ARCHETYPES.find((a) => a.id === id) ?? (ARCHETYPES[0] as Archetype)
}

export function xpOf(doneTasks: string[], closedLevels: number[]): number {
  const fromTasks = doneTasks.reduce((sum, id) => sum + (taskById(id)?.xp ?? 0), 0)
  return fromTasks + closedLevels.length * 100
}

let feedId = 0

// Qué dice cada especialista según la evidencia del Nivel (AD-FUNC-02: votos concretos, disenso visible)
const OK_LINES: Record<string, string> = {
  cto: 'Técnicamente es viable con lo que hay sobre la mesa.',
  cfo: 'Los números cuadran contra el sector; la caja aguanta.',
  cmo: 'El segmento está claro y la evidencia del mercado es suficiente.',
  legal: 'No veo riesgos legales que frenen este paso.',
  producto: 'La solución responde al dolor validado, sin sobrar nada.',
  operaciones: 'Podemos ejecutarlo con los recursos actuales.',
}

export function computeBoard(levelNumber: number, doneTasks: string[], archetype: Archetype): BoardSession {
  const level = levelOf(levelNumber)
  const missingTasks = level.tasks.filter((t) => !doneTasks.includes(t.id))
  const missing = missingTasks.map((t) => t.label)
  const specialists = AGENTS.filter((a) => a.board && a.id !== 'ceo')
  const votes: BoardVote[] = specialists.map((a, i) => {
    const own = level.tasks.filter((t) => t.agent === a.id)
    const ownMissing = own.filter((t) => !doneTasks.includes(t.id))
    // Sin tareas propias, el especialista vota según la evidencia completa del Nivel (con un disidente posible)
    const blocking = ownMissing[0] ?? (missingTasks.length > 0 ? missingTasks[i % missingTasks.length] : undefined)
    if (blocking) {
      return { agent: a.id, vote: 'PIVOT', line: `Cambiaría mi voto si tenemos: ${blocking.label.toLowerCase()}.` }
    }
    return { agent: a.id, vote: 'PROCEED', line: OK_LINES[a.id] ?? 'A favor.' }
  })
  const yes = votes.filter((v) => v.vote === 'PROCEED').length
  const recommendation: Vote = missingTasks.length === 0 && yes >= 4 ? 'PROCEED' : 'PIVOT'
  const name = archetype.example
  return {
    level: levelNumber, phase: 'gathering', step: 0, votes, recommendation, missing,
    opening: `Sesión del Nivel ${level.number}, ${level.name}. Lo que está en juego: ${level.tagline.toLowerCase()} Decidimos con la evidencia de ${name}.`,
    synthesis: recommendation === 'PROCEED'
      ? `El Board recomienda avanzar (${yes} de 6 a favor). El ${level.entregable} está listo. La decisión final es tuya.`
      : `El Board recomienda no cerrar todavía (${yes} de 6 a favor). Falta: ${missing.join('; ').toLowerCase() || 'más evidencia'}. Tú decides.`,
  }
}

const initial = load()

export const useUniverso = create<State>((set, get) => ({
  started: initial.started ?? false,
  archetypeId: initial.archetypeId ?? 'panaderia',
  companyName: initial.companyName ?? '',
  mode: initial.mode ?? 'crear',
  level: initial.level ?? 1,
  doneTasks: initial.doneTasks ?? [],
  closedLevels: initial.closedLevels ?? [],
  jobs: {},
  bubbles: {},
  selected: null,
  focusZone: null,
  board: null,
  feed: [],
  celebration: null,
  report: null,
  panel: 'mision',

  start: (archetypeId, name, mode) => {
    const a = archetypeOf(archetypeId)
    set({ started: true, archetypeId, companyName: name.trim() || a.example, mode, level: 1, doneTasks: [], closedLevels: [],
      jobs: {}, board: null, panel: 'mision' })
    get().log(`${mode === 'crear' ? 'Nace' : 'Se reinventa'} ${name.trim() || a.example}. Valeria abre el Nivel 1: El Dolor.`, '#34d399')
    get().say('ceo', AGENT_BY_ID.ceo.hello, 6000)
  },
  reset: () => set({ started: false, level: 1, doneTasks: [], closedLevels: [], jobs: {}, board: null, feed: [], selected: null }),
  goToLevel: (n) => {
    const { closedLevels } = get()
    const unlocked = n === 1 || closedLevels.includes(n - 1)
    if (unlocked) set({ level: n, panel: 'mision' })
  },
  assign: (taskId) => {
    const task = taskById(taskId)
    if (!task) return
    const { jobs, doneTasks } = get()
    if (doneTasks.includes(taskId) || jobs[task.agent]) return
    set({ jobs: { ...jobs, [task.agent]: { taskId, zone: task.zone, phase: 'going', until: 0 } } })
    const agent = AGENT_BY_ID[task.agent]
    get().say(task.agent, `Voy a ${task.label.toLowerCase()}.`, 2500, 'info')
    get().log(`${agent.name} (${agent.role}) va a ${task.label.toLowerCase()}.`, agent.color)
  },
  setPhase: (agent, phase, until = 0) => {
    const jobs = { ...get().jobs }
    const job = jobs[agent]
    if (!job) return
    if (phase === null) delete jobs[agent]
    else jobs[agent] = { ...job, phase, until }
    set({ jobs })
  },
  completeTask: (agent) => {
    const job = get().jobs[agent]
    if (!job) return
    const task = taskById(job.taskId)
    if (!task) return
    const doneTasks = get().doneTasks.includes(task.id) ? get().doneTasks : [...get().doneTasks, task.id]
    set({ doneTasks })
    const a = AGENT_BY_ID[agent]
    get().say(agent, `Listo: ${task.done}. +${task.xp} XP de evidencia.`, 3500, 'vote-yes')
    get().log(`${a.name} entregó: ${task.done} (+${task.xp} XP).`, a.color)
  },
  say: (agent, text, ms = 3000, tone) => {
    const bubble: Bubble = { text, until: Date.now() + ms, tone }
    set({ bubbles: { ...get().bubbles, [agent]: bubble } })
    // La burbuja se borra sola, salvo que el agente ya haya dicho otra cosa
    setTimeout(() => {
      if (get().bubbles[agent] !== bubble) return
      const bubbles = { ...get().bubbles }
      delete bubbles[agent]
      set({ bubbles })
    }, ms)
  },
  select: (agent) => set({ selected: agent }),
  focus: (zone) => set({ focusZone: zone }),
  convene: () => {
    const { level, doneTasks, archetypeId } = get()
    set({ board: computeBoard(level, doneTasks, archetypeOf(archetypeId)), focusZone: 'board', selected: null })
    get().log(`Valeria convoca al Board Room para el Nivel ${level}.`, '#60a5fa')
  },
  advanceBoard: () => {
    const b = get().board
    if (!b) return
    if (b.phase === 'gathering') {
      set({ board: { ...b, phase: 'opening' } })
      get().say('ceo', b.opening, 4200, 'info')
    } else if (b.phase === 'opening') {
      set({ board: { ...b, phase: 'voting', step: 0 } })
    } else if (b.phase === 'voting') {
      const v = b.votes[b.step]
      if (v) {
        get().say(v.agent, `${v.vote === 'PROCEED' ? 'A favor' : 'Pivotar'}: ${v.line}`, 3800, v.vote === 'PROCEED' ? 'vote-yes' : 'vote-no')
      }
      if (b.step + 1 >= b.votes.length) set({ board: { ...b, phase: 'closing', step: b.step + 1 } })
      else set({ board: { ...b, step: b.step + 1 } })
    } else if (b.phase === 'closing') {
      set({ board: { ...b, phase: 'decided' } })
      get().say('ceo', b.synthesis, 6500, b.recommendation === 'PROCEED' ? 'vote-yes' : 'vote-no')
    }
  },
  approveLevel: () => {
    const { level, closedLevels } = get()
    const lv = levelOf(level)
    const closed = closedLevels.includes(level) ? closedLevels : [...closedLevels, level]
    set({ closedLevels: closed, board: null, celebration: level, focusZone: 'gemelo',
      level: level < 7 ? level + 1 : 7 })
    get().log(`Aprobaste el cierre del Nivel ${level}. Insignia: ${lv.badge.name}. El Gemelo Digital crece.`, '#34d399')
  },
  dismissBoard: () => set({ board: null, focusZone: null }),
  closeCelebration: () => set({ celebration: null, focusZone: null }),
  openReport: (level) => set({ report: level }),
  setPanel: (panel) => set({ panel }),
  log: (text, color = '#94a3b8') => {
    feedId += 1
    set({ feed: [{ id: feedId, text, color, at: Date.now() }, ...get().feed].slice(0, 30) })
  },
}))

useUniverso.subscribe((s) => save({ started: s.started, archetypeId: s.archetypeId, companyName: s.companyName, mode: s.mode,
  level: s.level, doneTasks: s.doneTasks, closedLevels: s.closedLevels }))
