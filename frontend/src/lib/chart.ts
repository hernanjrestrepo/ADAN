// Gráficos que ADÁN puede pedir en sus respuestas: un bloque ```chart con este JSON

export interface ChartSpec {
  type: 'bar' | 'line' | 'pie'
  title?: string
  labels: string[]
  series: { name: string; data: number[] }[]
}

export const CHART_COLORS = ['#60a5fa', '#34d399', '#f59e0b', '#f472b6', '#a78bfa', '#22d3ee', '#fb923c']

export function parseChart(raw: string): ChartSpec | null {
  try {
    const c = JSON.parse(raw) as ChartSpec
    if (!['bar', 'line', 'pie'].includes(c.type) || !Array.isArray(c.labels) || !Array.isArray(c.series)) return null
    const series = c.series.filter((s) => Array.isArray(s.data)).map((s) => ({ name: String(s.name ?? ''), data: s.data.map((v) => Number(v) || 0) }))
    return series.length ? { ...c, series } : null
  } catch {
    return null
  }
}

// El último gráfico de un texto, para mostrarlo también en la pantalla holográfica del Universo
export function lastChart(text: string): ChartSpec | null {
  const blocks = [...text.matchAll(/```chart\s*([\s\S]*?)```/g)]
  for (let i = blocks.length - 1; i >= 0; i--) {
    const spec = parseChart(blocks[i]?.[1] ?? '')
    if (spec) return spec
  }
  return null
}
