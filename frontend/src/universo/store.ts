import { create } from 'zustand'
import type { ChartSpec } from '../lib/chart'
import {
  AGENT_BY_ID, AGENTS, ARCHETYPES, INVESTORS, LEVELS, type AgentId, type Archetype, type GateTask, type Level, type ZoneId,
} from './data'

// Estado del recorrido. Regla de AD-FUNC-04: el XP y las insignias solo salen de evidencia (tareas del Gate
// entregadas y Niveles cerrados con tu aprobación), nunca de tiempo conectado, clics o rachas.
// Como en un videojuego, el Board es exigente: en la primera sesión de cada Nivel el abogado del diablo descubre
// un riesgo crítico que hay que blindar antes de pasar; y el Nivel 5 no se cierra sin pasar La Arena.

export type JobPhase = 'going' | 'working' | 'returning'
export interface Job { taskId: string; zone: ZoneId; phase: JobPhase; until: number }
export interface Bubble { text: string; until: number; tone?: 'vote-yes' | 'vote-no' | 'info' }
export type Mood = 'feliz' | 'riendo' | 'preocupado' | 'estresado' | 'celebrando' | 'pensando' | 'hablando'
export type Vote = 'PROCEED' | 'PIVOT'
export interface BoardVote { agent: AgentId; vote: Vote; line: string; devil?: boolean }
export interface BoardSession {
  level: number
  phase: 'gathering' | 'opening' | 'voting' | 'closing' | 'decided'
  step: number
  votes: BoardVote[]
  recommendation: Vote
  opening: string
  synthesis: string
  missing: string[]
  revealsRisk: boolean
}
export interface ArenaVerdict { investor: string; invests: boolean; line: string; fatal?: string }
export interface ArenaSession {
  phase: 'gathering' | 'pitch' | 'deciding' | 'decided'
  step: number
  verdicts: ArenaVerdict[]
  passed: boolean
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
  revealed: number[]
  arenaPassed: boolean
  jobs: Partial<Record<AgentId, Job>>
  bubbles: Partial<Record<string, Bubble>>
  moods: Partial<Record<string, Mood>>
  selected: AgentId | null
  focusZone: ZoneId | null
  board: BoardSession | null
  arena: ArenaSession | null
  feed: FeedItem[]
  celebration: number | null
  report: number | null
  panel: 'mision' | 'ruta' | 'ecosistema' | 'insignias' | null
  holo: ChartSpec | null
  // Órdenes a la cámara desde los botones: vista general, acercar, alejar
  cam: { n: number; op: 'reset' | 'in' | 'out' }
  // Subtítulo de quien habla, debajo de la oficina
  subtitle: { who: string; text: string; color: string } | null
  // Quien habla pasa al frente de la oficina hasta `until`
  stage: { agent: string; until: number } | null
  // Sustos (clic derecho): el personaje brinca y tiembla hasta ese momento
  jolts: Partial<Record<string, number>>
  // Piso que se está viendo en la Sala (null en el Universo, que usa `level`)
  floor: number | null
  // Bromas del equipo sobre el proyecto (las genera ADAN una vez al día)
  jokes: { agente: string; texto: string }[]
  start: (archetypeId: string, name: string, mode: 'crear' | 'reinventar') => void
  reset: () => void
  goToLevel: (n: number) => void
  assign: (taskId: string) => void
  setPhase: (agent: AgentId, phase: JobPhase | null, until?: number) => void
  completeTask: (agent: AgentId) => void
  say: (who: string, text: string, ms?: number, tone?: Bubble['tone']) => void
  feel: (who: string, mood: Mood, ms?: number) => void
  select: (agent: AgentId | null) => void
  focus: (zone: ZoneId | null) => void
  convene: () => void
  advanceBoard: () => void
  approveLevel: () => void
  dismissBoard: () => void
  enterArena: () => void
  advanceArena: () => void
  leaveArena: () => void
  closeCelebration: () => void
  openReport: (level: number | null) => void
  setPanel: (panel: State['panel']) => void
  log: (text: string, color?: string) => void
  showHolo: (chart: ChartSpec | null) => void
  camera: (op: 'reset' | 'in' | 'out') => void
  caption: (who: string, text: string, color: string, ms?: number) => void
  present: (agent: string, ms: number) => void
  jolt: (agent: string, ms: number) => void
  setFloor: (floor: number | null) => void
  setJokes: (jokes: { agente: string; texto: string }[]) => void
}

// Partes de un subtítulo: frases completas de hasta ~150 caracteres, sin cortar palabras
export function subtitleParts(text: string): string[] {
  const sentences = text.match(/[^.!?]+[.!?]+["»)]*|[^.!?]+$/g) ?? [text]
  const parts: string[] = []
  let cur = ''
  for (const raw of sentences) {
    const s = raw.trim()
    if (!s) continue
    if ((cur + ' ' + s).trim().length <= 150) {
      cur = (cur + ' ' + s).trim()
      continue
    }
    if (cur) parts.push(cur)
    if (s.length <= 150) {
      cur = s
      continue
    }
    // Frase muy larga: se parte por palabras
    cur = ''
    for (const w of s.split(' ')) {
      if ((cur + ' ' + w).trim().length > 150) {
        parts.push(cur)
        cur = w
      } else cur = (cur + ' ' + w).trim()
    }
  }
  if (cur) parts.push(cur)
  return parts.slice(0, 6)
}

const STORAGE_KEY = 'adan-universo-v2'
// El subtítulo vigente: uno nuevo reemplaza al anterior aunque no haya terminado
let captionToken: object = {}
type Saved = Pick<State, 'started' | 'archetypeId' | 'companyName' | 'mode' | 'level' | 'doneTasks' | 'closedLevels' | 'revealed' | 'arenaPassed'>

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
    const t = l.tasks.find((x) => x.id === id) ?? (l.riesgo.task.id === id ? l.riesgo.task : undefined)
    if (t) return t
  }
  return undefined
}

// Las tareas visibles de un Nivel: las del Gate y, si el Board ya lo descubrió, la de blindar el riesgo crítico
export function tasksOf(level: Level, revealed: number[]): GateTask[] {
  return revealed.includes(level.number) ? [...level.tasks, level.riesgo.task] : level.tasks
}

export function archetypeOf(id: string): Archetype {
  return ARCHETYPES.find((a) => a.id === id) ?? (ARCHETYPES[0] as Archetype)
}

export function xpOf(doneTasks: string[], closedLevels: number[]): number {
  const fromTasks = doneTasks.reduce((sum, id) => sum + (taskById(id)?.xp ?? 0), 0)
  return fromTasks + closedLevels.length * 100
}

let feedId = 0

const OK_LINES: Record<string, string> = {
  cto: 'Técnicamente es viable con lo que hay sobre la mesa.',
  cfo: 'Los números cuadran contra el sector; la caja aguanta.',
  cmo: 'El segmento está claro y la evidencia del mercado es suficiente.',
  legal: 'No veo riesgos legales que frenen este paso.',
  producto: 'La solución responde al dolor validado, sin sobrar nada.',
  operaciones: 'Podemos ejecutarlo con los recursos actuales.',
}
const SPECIALISTS = AGENTS.filter((a) => a.board && a.id !== 'ceo')

export function computeBoard(levelNumber: number, doneTasks: string[], archetype: Archetype, revealed: number[]): BoardSession {
  const level = levelOf(levelNumber)
  const missingTasks = level.tasks.filter((t) => !doneTasks.includes(t.id))
  const devil = SPECIALISTS[(levelNumber - 1) % SPECIALISTS.length] as (typeof SPECIALISTS)[number]
  const second = SPECIALISTS[levelNumber % SPECIALISTS.length] as (typeof SPECIALISTS)[number]
  const riskKnown = revealed.includes(levelNumber)
  const riskDone = doneTasks.includes(level.riesgo.task.id)
  let revealsRisk = false
  let missing = missingTasks.map((t) => t.label)
  const votes: BoardVote[] = SPECIALISTS.map((a, i) => {
    const isDevil = a.id === devil.id
    const ownMissing = level.tasks.filter((t) => t.agent === a.id && !doneTasks.includes(t.id))
    const blocking = ownMissing[0] ?? (missingTasks.length > 0 ? missingTasks[i % missingTasks.length] : undefined)
    if (blocking) return { agent: a.id, vote: 'PIVOT' as Vote, devil: isDevil, line: `Cambiaría mi voto si tenemos: ${blocking.label.toLowerCase()}.` }
    if (!riskKnown && (isDevil || a.id === second.id)) {
      revealsRisk = true
      return { agent: a.id, vote: 'PIVOT' as Vote, devil: isDevil,
        line: isDevil ? `Riesgo crítico: ${level.riesgo.texto}` : 'Coincido con el abogado del diablo: eso nos puede cerrar la empresa.' }
    }
    if (riskKnown && !riskDone && (isDevil || a.id === second.id)) {
      return { agent: a.id, vote: 'PIVOT' as Vote, devil: isDevil, line: `Falta blindar: ${level.riesgo.task.label.toLowerCase()}.` }
    }
    if (isDevil) return { agent: a.id, vote: 'PROCEED' as Vote, devil: true, line: 'Busqué fallas serias a fondo y esta vez no las encontré.' }
    return { agent: a.id, vote: 'PROCEED' as Vote, line: OK_LINES[a.id] ?? 'A favor.' }
  })
  if (revealsRisk) missing = [...missing, level.riesgo.task.label]
  else if (riskKnown && !riskDone) missing = [...missing, level.riesgo.task.label]
  const yes = votes.filter((v) => v.vote === 'PROCEED').length
  // Como en ADAN real: avanzar exige 5 de 6 a favor y nada pendiente
  const recommendation: Vote = missing.length === 0 && yes >= 5 ? 'PROCEED' : 'PIVOT'
  const synthesis = recommendation === 'PROCEED'
    ? `El Board recomienda avanzar (${yes} de 6 a favor). ${levelNumber === 5 ? 'Antes de cerrar, te toca convencer a los inversionistas en La Arena.' : `El ${level.entregable} está listo.`} La decisión es tuya.`
    : revealsRisk
      ? `No cerramos todavía (${yes} de 6 a favor). ${devil.name}, el abogado del diablo, encontró un riesgo crítico: ${level.riesgo.texto} Blíndalo y volvemos a sesionar.`
      : `No cerramos todavía (${yes} de 6 a favor). Falta: ${missing.join('; ').toLowerCase()}. Tú decides.`
  return {
    level: levelNumber, phase: 'gathering', step: 0, votes, recommendation, missing, revealsRisk, synthesis,
    opening: `Sesión del Nivel ${level.number}, ${level.name}. Lo que está en juego: ${level.tagline.toLowerCase()} Decidimos con la evidencia de ${archetype.example}. ${devil.name} es el abogado del diablo.`,
  }
}

function computeArena(doneTasks: string[]): ArenaSession {
  const level = levelOf(5)
  const ready = level.tasks.every((t) => doneTasks.includes(t.id)) && doneTasks.includes(level.riesgo.task.id)
  const verdicts: ArenaVerdict[] = ready ? [
    { investor: 'angel', invests: true, line: 'Me convenció la evidencia de clientes. Pongo USD 80.000.' },
    { investor: 'vc', invests: true, line: 'El CAC está medido y el mercado es grande. Entramos con condiciones.' },
    { investor: 'banca', invests: false, line: 'Sin historial de ventas no presto todavía. Vuelve en seis meses.' },
    { investor: 'estrategico', invests: true, line: 'Hay sinergia con mi negocio. Aliémonos.' },
  ] : [
    { investor: 'angel', invests: false, line: 'No veo clientes reales detrás de las cifras.', fatal: 'Sin evidencia de clientes' },
    { investor: 'vc', invests: false, line: 'El costo de adquisición es una suposición.', fatal: 'CAC sin probar' },
    { investor: 'banca', invests: false, line: 'No hay flujo que respalde un crédito.' },
    { investor: 'estrategico', invests: false, line: 'Cualquiera puede copiar esto mañana.', fatal: 'Diferenciador sin blindar' },
  ]
  return { phase: 'gathering', step: 0, verdicts, passed: verdicts.filter((v) => v.invests).length >= 2 && !verdicts.some((v) => v.fatal) }
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
  revealed: initial.revealed ?? [],
  arenaPassed: initial.arenaPassed ?? false,
  jobs: {},
  bubbles: {},
  moods: {},
  selected: null,
  focusZone: null,
  board: null,
  arena: null,
  feed: [],
  celebration: null,
  report: null,
  panel: 'mision',
  holo: null,
  cam: { n: 0, op: 'reset' },
  subtitle: null,
  stage: null,
  jolts: {},
  floor: null,
  jokes: [],

  start: (archetypeId, name, mode) => {
    const a = archetypeOf(archetypeId)
    set({ started: true, archetypeId, companyName: name.trim() || a.example, mode, level: 1, doneTasks: [], closedLevels: [],
      revealed: [], arenaPassed: false, jobs: {}, board: null, arena: null, panel: 'mision' })
    get().log(`${mode === 'crear' ? 'Nace' : 'Se reinventa'} ${name.trim() || a.example}. ADAN abre el Nivel 1: El Dolor.`, '#34d399')
    get().say('ceo', AGENT_BY_ID.ceo.hello, 6000)
    get().feel('ceo', 'feliz', 4000)
  },
  reset: () => set({ started: false, level: 1, doneTasks: [], closedLevels: [], revealed: [], arenaPassed: false, jobs: {},
    board: null, arena: null, feed: [], selected: null }),
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
    get().say(agent, `¡Listo! ${task.done}. +${task.xp} XP de evidencia.`, 3500, 'vote-yes')
    get().feel(agent, 'feliz', 3500)
    get().log(`${a.name} entregó: ${task.done} (+${task.xp} XP).`, a.color)
  },
  say: (who, text, ms = 3000, tone) => {
    const bubble: Bubble = { text, until: Date.now() + ms, tone }
    set({ bubbles: { ...get().bubbles, [who]: bubble } })
    // La burbuja se borra sola, salvo que ya haya dicho otra cosa
    setTimeout(() => {
      if (get().bubbles[who] !== bubble) return
      const bubbles = { ...get().bubbles }
      delete bubbles[who]
      set({ bubbles })
    }, ms)
  },
  feel: (who, mood, ms = 3500) => {
    set({ moods: { ...get().moods, [who]: mood } })
    setTimeout(() => {
      if (get().moods[who] !== mood) return
      const moods = { ...get().moods }
      delete moods[who]
      set({ moods })
    }, ms)
  },
  select: (agent) => set({ selected: agent }),
  focus: (zone) => set({ focusZone: zone }),
  convene: () => {
    const { level, doneTasks, archetypeId, revealed } = get()
    set({ board: computeBoard(level, doneTasks, archetypeOf(archetypeId), revealed), focusZone: 'board', selected: null })
    get().log(`ADAN convoca al Board Room para el Nivel ${level}.`, '#60a5fa')
  },
  advanceBoard: () => {
    const b = get().board
    if (!b) return
    if (b.phase === 'gathering') {
      set({ board: { ...b, phase: 'opening' } })
      get().say('ceo', b.opening, 4200, 'info')
      get().feel('ceo', 'hablando', 4200)
    } else if (b.phase === 'opening') {
      set({ board: { ...b, phase: 'voting', step: 0 } })
    } else if (b.phase === 'voting') {
      const v = b.votes[b.step]
      if (v) {
        get().say(v.agent, `${v.devil ? '😈 ' : ''}${v.vote === 'PROCEED' ? 'A favor' : 'Pivotar'}: ${v.line}`, 3800, v.vote === 'PROCEED' ? 'vote-yes' : 'vote-no')
        get().feel(v.agent, v.vote === 'PROCEED' ? 'feliz' : v.devil ? 'pensando' : 'preocupado', 3800)
      }
      if (b.step + 1 >= b.votes.length) set({ board: { ...b, phase: 'closing', step: b.step + 1 } })
      else set({ board: { ...b, step: b.step + 1 } })
    } else if (b.phase === 'closing') {
      set({ board: { ...b, phase: 'decided' } })
      get().say('ceo', b.synthesis, 7000, b.recommendation === 'PROCEED' ? 'vote-yes' : 'vote-no')
      if (b.revealsRisk) {
        // El riesgo crítico aparece como tarea nueva y el equipo se estresa un momento
        set({ revealed: [...new Set([...get().revealed, b.level])] })
        SPECIALISTS.forEach((a, i) => setTimeout(() => get().feel(a.id, 'estresado', 3500), i * 120))
        get().feel('ceo', 'preocupado', 5000)
        get().log(`Riesgo crítico en el Nivel ${b.level}: ${levelOf(b.level).riesgo.texto} Nueva tarea: ${levelOf(b.level).riesgo.task.label}.`, '#ef4444')
      } else {
        get().feel('ceo', b.recommendation === 'PROCEED' ? 'feliz' : 'preocupado', 5000)
      }
    }
  },
  approveLevel: () => {
    const { level, closedLevels, arenaPassed } = get()
    if (level === 5 && !arenaPassed) {
      get().enterArena()
      return
    }
    const lv = levelOf(level)
    const closed = closedLevels.includes(level) ? closedLevels : [...closedLevels, level]
    set({ closedLevels: closed, board: null, arena: null, celebration: level, focusZone: 'gemelo', level: level < 7 ? level + 1 : 7 })
    AGENTS.forEach((a, i) => setTimeout(() => get().feel(a.id, i % 3 === 0 ? 'riendo' : 'celebrando', 4500), i * 80))
    get().log(`Aprobaste el cierre del Nivel ${level}. Insignia: ${lv.badge.name}. El Gemelo Digital crece.`, '#34d399')
  },
  dismissBoard: () => set({ board: null, focusZone: null }),
  enterArena: () => {
    set({ board: null, arena: computeArena(get().doneTasks), focusZone: 'arena', selected: null })
    get().log('Entras a La Arena: cuatro inversionistas te esperan.', '#ef4444')
  },
  advanceArena: () => {
    const a = get().arena
    if (!a) return
    if (a.phase === 'gathering') {
      set({ arena: { ...a, phase: 'pitch' } })
      get().say('ceo', `Presentamos ${get().companyName}: el problema validado, la propuesta, los números y lo que pedimos.`, 4200, 'info')
      get().feel('ceo', 'hablando', 4200)
    } else if (a.phase === 'pitch') {
      set({ arena: { ...a, phase: 'deciding', step: 0 } })
    } else if (a.phase === 'deciding') {
      const v = a.verdicts[a.step]
      if (v) {
        get().say(`inv-${v.investor}`, `${v.invests ? '💰 Invierto' : '❌ No invierto'}: ${v.line}`, 3800, v.invests ? 'vote-yes' : 'vote-no')
        get().feel(`inv-${v.investor}`, v.invests ? 'feliz' : 'preocupado', 3800)
      }
      if (a.step + 1 >= a.verdicts.length) {
        set({ arena: { ...a, phase: 'decided', step: a.step + 1 }, arenaPassed: get().arenaPassed || a.passed })
        if (a.passed) {
          AGENTS.forEach((ag) => get().feel(ag.id, 'celebrando', 4000))
          get().log('¡Pasaste La Arena! Ya puedes cerrar el Nivel 5.', '#34d399')
        } else {
          AGENTS.filter((ag) => ag.board).forEach((ag) => get().feel(ag.id, 'estresado', 4000))
          get().log('No pasaste La Arena: blinda lo que te señalaron y vuelve a entrar.', '#ef4444')
        }
      } else set({ arena: { ...a, step: a.step + 1 } })
    }
  },
  leaveArena: () => set({ arena: null, focusZone: null }),
  closeCelebration: () => set({ celebration: null, focusZone: null }),
  openReport: (level) => set({ report: level }),
  setPanel: (panel) => set({ panel }),
  showHolo: (chart) => set({ holo: chart }),
  caption: (who, text, color) => {
    // Subtítulos completos: frase por frase, cada parte el tiempo que toma leerla
    const parts = subtitleParts(text)
    let at = 0
    const token = {}
    captionToken = token
    parts.forEach((part, i) => {
      const subtitle = { who, text: part, color }
      setTimeout(() => { if (captionToken === token) set({ subtitle }) }, at)
      at += Math.max(2600, part.length * 60)
      if (i === parts.length - 1) setTimeout(() => { if (captionToken === token && get().subtitle === subtitle) set({ subtitle: null }) }, at)
    })
  },
  present: (agent, ms) => {
    const stage = { agent, until: Date.now() + ms }
    set({ stage })
    setTimeout(() => { if (get().stage === stage) set({ stage: null }) }, ms + 50)
  },
  jolt: (agent, ms) => set({ jolts: { ...get().jolts, [agent]: Date.now() + ms } }),
  setFloor: (floor) => set({ floor }),
  setJokes: (jokes) => set({ jokes }),
  camera: (op) => set({ cam: { n: get().cam.n + 1, op }, ...(op === 'reset' ? { selected: null, focusZone: null } : {}) }),
  log: (text, color = '#94a3b8') => {
    feedId += 1
    set({ feed: [{ id: feedId, text, color, at: Date.now() }, ...get().feed].slice(0, 30) })
  },
}))

export const INVESTOR_BY_ID = Object.fromEntries(INVESTORS.map((i) => [i.id, i]))

useUniverso.subscribe((s) => save({ started: s.started, archetypeId: s.archetypeId, companyName: s.companyName, mode: s.mode,
  level: s.level, doneTasks: s.doneTasks, closedLevels: s.closedLevels, revealed: s.revealed, arenaPassed: s.arenaPassed }))
