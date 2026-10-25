import ReactMarkdown, { type Components } from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { CHART_COLORS as COLORS, parseChart, type ChartSpec } from '../lib/chart'

// Respuesta de ADÁN con tablas, enlaces y gráficos: un bloque ```chart con JSON se dibuja como gráfico (barras,
// líneas o torta) en SVG, sin librerías pesadas.

function fmt(n: number) {
  return Math.abs(n) >= 1e9 ? `${(n / 1e9).toFixed(1)}B` : Math.abs(n) >= 1e6 ? `${(n / 1e6).toFixed(1)}M`
    : Math.abs(n) >= 1e3 ? `${(n / 1e3).toFixed(1)}k` : n.toLocaleString('es-CO', { maximumFractionDigits: 2 })
}

export function Chart({ spec, compact = false }: { spec: ChartSpec; compact?: boolean }) {
  const W = 360
  const H = compact ? 150 : 200
  const pad = { l: 36, r: 8, t: 8, b: 28 }
  if (spec.type === 'pie') {
    const data = spec.series[0]?.data ?? []
    const total = data.reduce((a, b) => a + Math.max(b, 0), 0) || 1
    const r = H / 2 - 8
    // Cada tajada empieza donde terminó la anterior
    const slices = data.reduce<{ from: number; to: number }[]>((acc, v) => {
      const from = acc.length ? (acc[acc.length - 1]?.to ?? 0) : -Math.PI / 2
      return [...acc, { from, to: from + (Math.max(v, 0) / total) * Math.PI * 2 }]
    }, [])
    return (
      <figure className="my-2">
        {spec.title && <figcaption className="text-xs font-semibold mb-1">{spec.title}</figcaption>}
        <div className="flex items-center gap-3">
          <svg viewBox={`0 0 ${H} ${H}`} width={H} height={H} role="img" aria-label={spec.title ?? 'Gráfico de torta'}>
            {slices.map(({ from, to }, i) => {
              const x1 = H / 2 + r * Math.cos(from)
              const y1 = H / 2 + r * Math.sin(from)
              const x2 = H / 2 + r * Math.cos(to)
              const y2 = H / 2 + r * Math.sin(to)
              return <path key={i} d={`M${H / 2},${H / 2} L${x1},${y1} A${r},${r} 0 ${to - from > Math.PI ? 1 : 0} 1 ${x2},${y2} Z`} fill={COLORS[i % COLORS.length]} />
            })}
          </svg>
          <ul className="text-xs space-y-1">
            {spec.labels.map((l, i) => (
              <li key={l + i}><span className="inline-block h-2 w-2 rounded-full mr-1" style={{ background: COLORS[i % COLORS.length] }} />{l}: <b>{fmt(data[i] ?? 0)}</b> ({Math.round(((data[i] ?? 0) / total) * 100)} %)</li>
            ))}
          </ul>
        </div>
      </figure>
    )
  }
  const all = spec.series.flatMap((s) => s.data)
  const max = Math.max(...all, 0) || 1
  const min = Math.min(...all, 0)
  const iw = W - pad.l - pad.r
  const ih = H - pad.t - pad.b
  const y = (v: number) => pad.t + ih - ((v - min) / (max - min || 1)) * ih
  const n = spec.labels.length || 1
  const groupW = iw / n
  const barW = Math.max(3, (groupW * 0.7) / spec.series.length)
  return (
    <figure className="my-2">
      {spec.title && <figcaption className="text-xs font-semibold mb-1">{spec.title}</figcaption>}
      <svg viewBox={`0 0 ${W} ${H}`} className="w-full max-w-md" role="img" aria-label={spec.title ?? 'Gráfico'}>
        {[0, 0.5, 1].map((t) => {
          const v = min + (max - min) * t
          return (
            <g key={t}>
              <line x1={pad.l} x2={W - pad.r} y1={y(v)} y2={y(v)} stroke="currentColor" strokeOpacity={0.12} />
              <text x={pad.l - 4} y={y(v) + 3} textAnchor="end" fontSize={9} fill="currentColor" opacity={0.6}>{fmt(v)}</text>
            </g>
          )
        })}
        {spec.labels.map((l, i) => (
          <text key={l + i} x={pad.l + groupW * i + groupW / 2} y={H - 10} textAnchor="middle" fontSize={9} fill="currentColor" opacity={0.7}>
            {l.length > 10 ? `${l.slice(0, 9)}…` : l}
          </text>
        ))}
        {spec.series.map((s, si) => spec.type === 'bar'
          ? s.data.map((v, i) => (
            <rect key={`${si}-${i}`} x={pad.l + groupW * i + groupW * 0.15 + si * barW} y={Math.min(y(v), y(0))} width={barW - 1}
              height={Math.abs(y(0) - y(v))} rx={2} fill={COLORS[si % COLORS.length]}><title>{`${s.name} · ${spec.labels[i]}: ${fmt(v)}`}</title></rect>
          ))
          : <polyline key={si} fill="none" stroke={COLORS[si % COLORS.length]} strokeWidth={2}
            points={s.data.map((v, i) => `${pad.l + groupW * i + groupW / 2},${y(v)}`).join(' ')} />)}
      </svg>
      {spec.series.length > 1 && (
        <p className="text-[11px] flex flex-wrap gap-3">{spec.series.map((s, i) => <span key={s.name + i}><span className="inline-block h-2 w-2 rounded-full mr-1" style={{ background: COLORS[i % COLORS.length] }} />{s.name}</span>)}</p>
      )}
    </figure>
  )
}

const components: Components = {
  code({ className, children }) {
    const raw = String(children ?? '')
    if (className?.includes('language-chart')) {
      const spec = parseChart(raw)
      if (spec) return <Chart spec={spec} />
    }
    return <code className={className}>{children}</code>
  },
  table({ children }) {
    return <div className="my-2 overflow-x-auto"><table className="text-xs border-collapse [&_td]:border [&_td]:border-white/10 [&_td]:px-2 [&_td]:py-1 [&_th]:border [&_th]:border-white/10 [&_th]:px-2 [&_th]:py-1 [&_th]:text-left">{children}</table></div>
  },
  a({ href, children }) {
    return <a href={href} target="_blank" rel="noreferrer noopener" className="underline break-all">{children}</a>
  },
}

export default function RichMessage({ text }: { text: string }) {
  return <ReactMarkdown remarkPlugins={[remarkGfm]} components={components}>{text}</ReactMarkdown>
}
