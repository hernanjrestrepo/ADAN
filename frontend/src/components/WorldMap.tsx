import { useMemo, useState } from 'react'
import { feature } from 'topojson-client'
import world from 'world-atlas/countries-110m.json'
import { countryName } from '../lib/paises'

// El mapa de las visitas (como en la consola de Xmart Travel): cada país pintado según cuántas visitas trajo.
// Fronteras de Natural Earth 1:110 millones (world-atlas, dominio público), proyección equirectangular sin la Antártida.
// El país de cada visita lo pone Cloudflare como código ISO; aquí se cruza con el nombre en inglés del mapa.

const ISO_TO_MAP: Record<string, string> = {
  AR: 'Argentina', AU: 'Australia', AT: 'Austria', BE: 'Belgium', BO: 'Bolivia', BR: 'Brazil', CA: 'Canada', CL: 'Chile',
  CN: 'China', CO: 'Colombia', CR: 'Costa Rica', CU: 'Cuba', CZ: 'Czechia', DK: 'Denmark', DO: 'Dominican Rep.',
  EC: 'Ecuador', EG: 'Egypt', SV: 'El Salvador', FI: 'Finland', FR: 'France', DE: 'Germany', GR: 'Greece', GT: 'Guatemala',
  HN: 'Honduras', HU: 'Hungary', IN: 'India', ID: 'Indonesia', IE: 'Ireland', IL: 'Israel', IT: 'Italy', JM: 'Jamaica',
  JP: 'Japan', KE: 'Kenya', KR: 'South Korea', MX: 'Mexico', MA: 'Morocco', NL: 'Netherlands', NZ: 'New Zealand',
  NI: 'Nicaragua', NG: 'Nigeria', NO: 'Norway', PA: 'Panama', PY: 'Paraguay', PE: 'Peru', PH: 'Philippines', PL: 'Poland',
  PT: 'Portugal', PR: 'Puerto Rico', RO: 'Romania', RU: 'Russia', SA: 'Saudi Arabia', ZA: 'South Africa', ES: 'Spain',
  SE: 'Sweden', CH: 'Switzerland', TW: 'Taiwan', TH: 'Thailand', TR: 'Turkey', UA: 'Ukraine', AE: 'United Arab Emirates',
  GB: 'United Kingdom', US: 'United States of America', UY: 'Uruguay', VE: 'Venezuela', VN: 'Vietnam', TT: 'Trinidad and Tobago',
  HT: 'Haiti', BZ: 'Belize', GY: 'Guyana', SR: 'Suriname', PK: 'Pakistan', BD: 'Bangladesh', MY: 'Malaysia', SG: 'Singapore',
}
const W = 1000
const NORTH = 84
const SOUTH = -57
const H = Math.round((W * (NORTH - SOUTH)) / 360)

type Geo = { type: string; coordinates: number[][][] | number[][][][] }

function path(geo: Geo): string {
  const x = (lon: number) => ((lon + 180) / 360) * W
  const y = (lat: number) => ((NORTH - Math.max(SOUTH, Math.min(NORTH, lat))) / (NORTH - SOUTH)) * H
  // Rusia y Fiyi cruzan la línea de cambio de fecha: ahí se corta el trazo para que no atraviese el mapa
  const ring = (r: number[][]) => r.map(([lon = 0, lat = 0], i) => {
    const jump = i > 0 && Math.abs(lon - (r[i - 1]?.[0] ?? lon)) > 180
    return `${i === 0 || jump ? 'M' : 'L'}${x(lon).toFixed(1)},${y(lat).toFixed(1)}`
  }).join('') + 'Z'
  const polys = (geo.type === 'Polygon' ? [geo.coordinates] : geo.coordinates) as number[][][][]
  return polys.map((p) => p.map(ring).join('')).join('')
}


export default function WorldMap({ countries }: { countries: { pais: string; visitas: number; visitantes: number }[] }) {
  const shapes = useMemo(() => {
    const topo = world as unknown as { objects: { countries: unknown } }
    const fc = feature(topo as never, topo.objects.countries as never) as unknown as { features: { properties: { name: string }; geometry: Geo | null }[] }
    return fc.features.filter((f) => f.properties.name !== 'Antarctica' && f.geometry)
      .map((f) => ({ name: f.properties.name, d: path(f.geometry as Geo) }))
  }, [])
  const [focus, setFocus] = useState<string | null>(null)
  const byName = new Map(countries.filter((c) => ISO_TO_MAP[c.pais]).map((c) => [ISO_TO_MAP[c.pais], c]))
  const max = Math.max(...countries.map((c) => c.visitas), 1)
  const hit = focus ? byName.get(focus) : undefined
  return (
    <div className="space-y-2">
      <p className="min-h-5 text-sm font-semibold">
        {hit ? `${countryName(hit.pais)}: ${hit.visitas.toLocaleString('es-CO')} visitas · ${hit.visitantes.toLocaleString('es-CO')} visitantes`
          : focus ? `${focus}: sin visitas en el periodo` : 'Pasa el mouse o toca un país'}
      </p>
      <svg viewBox={`0 0 ${W} ${H}`} className="w-full rounded-xl bg-adan-bg" role="img" aria-label="Mapa de visitas por país">
        {shapes.map((s) => {
          const c = byName.get(s.name)
          const t = c ? 0.25 + 0.75 * Math.sqrt(c.visitas / max) : 0
          return (
            <path key={s.name} d={s.d} onMouseEnter={() => setFocus(s.name)} onMouseLeave={() => setFocus(null)} onClick={() => setFocus(s.name)}
              fill={c ? `rgba(59, 130, 246, ${t.toFixed(2)})` : 'var(--color-adan-surface-2, #1e293b)'}
              stroke="var(--color-adan-border, #334155)" strokeWidth={0.6} className="cursor-pointer transition-opacity hover:opacity-80" />
          )
        })}
      </svg>
    </div>
  )
}
