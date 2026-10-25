// Los pisos del edificio (uno por Nivel) y la identidad de la empresa que se muestra en ellos
export interface Identity {
  nombre: string
  slogan: string
  logo: string | null
  color: string | null
  acento: string | null
  expediente?: { hechos: number; total: number }
}

export const FLOORS: Record<number, { name: string; color: string }> = {
  1: { name: 'Laboratorio de descubrimiento', color: '#38bdf8' },
  2: { name: 'Estudio de diseño', color: '#f472b6' },
  3: { name: 'Finanzas y notaría', color: '#4ade80' },
  4: { name: 'Taller del MVP', color: '#f59e0b' },
  5: { name: 'Laboratorio de pruebas', color: '#ef4444' },
  6: { name: 'Escenario de lanzamiento', color: '#a78bfa' },
  7: { name: 'Piso ejecutivo', color: '#fbbf24' },
}
