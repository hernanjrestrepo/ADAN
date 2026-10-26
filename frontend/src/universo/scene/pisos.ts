// Los pisos del edificio (uno por Nivel) y la identidad de la empresa que se muestra en ellos
export interface Identity {
  nombre: string
  slogan: string
  logo: string | null
  color: string | null
  acento: string | null
  expediente?: { hechos: number; total: number }
}

// Cada piso cambia de ambiente: piso, cuadrícula, neones de las paredes, cielo, niebla, luz y si hay estrellas
export interface FloorTheme {
  name: string
  color: string
  floor: string
  metal: number
  grid: [string, string]
  walls: [string, string, string]
  sky: string
  ambient: string
  stars: boolean
  // Partículas que flotan en el aire (polvo de taller, confeti, chispas)
  particles: string | null
}

export const FLOORS: Record<number, FloorTheme> = {
  1: { name: 'Laboratorio de descubrimiento', color: '#38bdf8', floor: '#e2e8f0', metal: 0.15, grid: ['#94a3b8', '#38bdf8'],
    walls: ['#38bdf8', '#22d3ee', '#a5f3fc'], sky: '#0b2236', ambient: '#e0f2fe', stars: false, particles: null },
  2: { name: 'Estudio de diseño', color: '#f472b6', floor: '#2a1626', metal: 0.3, grid: ['#4a1d3f', '#f472b6'],
    walls: ['#f472b6', '#fb923c', '#facc15'], sky: '#2b0f2a', ambient: '#fbcfe8', stars: false, particles: '#f9a8d4' },
  3: { name: 'Finanzas y notaría', color: '#4ade80', floor: '#3b2a1d', metal: 0.2, grid: ['#4b3621', '#4ade80'],
    walls: ['#4ade80', '#22c55e', '#fde68a'], sky: '#071a10', ambient: '#dcfce7', stars: false, particles: null },
  4: { name: 'Taller del MVP', color: '#f59e0b', floor: '#1f2937', metal: 0.85, grid: ['#374151', '#f59e0b'],
    walls: ['#f59e0b', '#ef4444', '#fbbf24'], sky: '#1a1206', ambient: '#fed7aa', stars: false, particles: '#fbbf24' },
  5: { name: 'Laboratorio de pruebas', color: '#ef4444', floor: '#f1f5f9', metal: 0.4, grid: ['#cbd5e1', '#ef4444'],
    walls: ['#ef4444', '#22d3ee', '#a3e635'], sky: '#1c0707', ambient: '#fecaca', stars: false, particles: '#a3e635' },
  6: { name: 'Escenario de lanzamiento', color: '#a78bfa', floor: '#0b0720', metal: 0.9, grid: ['#2e1065', '#a78bfa'],
    walls: ['#a78bfa', '#f472b6', '#38bdf8'], sky: '#05030f', ambient: '#c4b5fd', stars: true, particles: '#f0abfc' },
  7: { name: 'Piso ejecutivo', color: '#fbbf24', floor: '#111111', metal: 0.95, grid: ['#262626', '#fbbf24'],
    walls: ['#fbbf24', '#f5f5f4', '#d97706'], sky: '#120d02', ambient: '#fef3c7', stars: true, particles: null },
}

export function themeOf(floor: number): FloorTheme {
  return FLOORS[floor] ?? FLOORS[1]!
}
