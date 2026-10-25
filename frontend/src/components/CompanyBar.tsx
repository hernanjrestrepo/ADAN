import { useEffect, useRef, useState } from 'react'
import { Link, useNavigate } from 'react-router'
import { api, errorMessage } from '../lib/api'
import type { AppleCompanyLevel, Company, LevelView } from '../types'

// La empresa en la que trabajas: su identidad (colores y logo) tiñe todo el entorno, se cambia de empresa con un
// clic y la checklist de los 7 Niveles muestra siempre qué falta y qué está pagado con @pples.

const MAX_LOGO_BYTES = 200_000

export function CompanyMark({ company, size = 32 }: { company: Pick<Company, 'name' | 'logo' | 'brand_color'>; size?: number }) {
  if (company.logo) {
    return <img src={company.logo} alt="" width={size} height={size} className="rounded-lg object-contain bg-white/5" style={{ width: size, height: size }} />
  }
  return (
    <span aria-hidden="true" className="grid place-items-center rounded-lg font-bold text-white"
      style={{ width: size, height: size, background: company.brand_color ?? 'var(--color-adan-accent)', fontSize: size * 0.45 }}>
      {company.name.slice(0, 1).toUpperCase()}
    </span>
  )
}

function BrandEditor({ company, onSaved, onClose }: { company: Company; onSaved: (c: Company) => void; onClose: () => void }) {
  const [color, setColor] = useState(company.brand_color ?? '#3b82f6')
  const [accent, setAccent] = useState(company.brand_accent ?? '#8b5cf6')
  const [logo, setLogo] = useState<string | null>(company.logo ?? null)
  const [error, setError] = useState<string | null>(null)
  const [saving, setSaving] = useState(false)
  const file = useRef<HTMLInputElement>(null)

  const pick = (f: File | undefined) => {
    if (!f) return
    if (f.size > MAX_LOGO_BYTES) {
      setError('El logo debe pesar menos de 200 KB.')
      return
    }
    const reader = new FileReader()
    reader.onload = () => setLogo(String(reader.result))
    reader.readAsDataURL(f)
  }

  const save = async () => {
    setSaving(true)
    setError(null)
    try {
      onSaved(await api.setCompanyBrand(company.id, { brand_color: color, brand_accent: accent, logo }))
      onClose()
    } catch (err) {
      setError(errorMessage(err))
    } finally {
      setSaving(false)
    }
  }

  return (
    <div role="dialog" aria-label="Identidad de la empresa"
      className="absolute left-0 top-full z-50 mt-2 w-80 rounded-2xl border border-adan-border bg-adan-surface p-4 shadow-xl">
      <p className="text-sm font-bold">Identidad de {company.name}</p>
      <p className="text-xs text-adan-muted mt-1">ADÁN usa estos colores y tu logo en todo el entorno de esta empresa.</p>
      <div className="mt-3 flex items-center gap-3">
        <CompanyMark company={{ name: company.name, logo, brand_color: color }} size={48} />
        <div className="flex-1 space-y-2 text-xs">
          <label className="flex items-center justify-between gap-2">Color principal
            <input type="color" value={color} onChange={(e) => setColor(e.target.value)} className="h-7 w-12 rounded bg-transparent" />
          </label>
          <label className="flex items-center justify-between gap-2">Color de acento
            <input type="color" value={accent} onChange={(e) => setAccent(e.target.value)} className="h-7 w-12 rounded bg-transparent" />
          </label>
        </div>
      </div>
      <input ref={file} type="file" accept="image/png,image/jpeg,image/webp,image/svg+xml" className="hidden" aria-label="Logo"
        onChange={(e) => { pick(e.target.files?.[0]); e.target.value = '' }} />
      <div className="mt-3 flex gap-2 text-xs">
        <button type="button" onClick={() => file.current?.click()} className="rounded-lg border border-adan-border px-3 py-1.5 hover:border-adan-accent">
          {logo ? 'Cambiar logo' : 'Subir logo'}
        </button>
        {logo && <button type="button" onClick={() => setLogo(null)} className="rounded-lg px-3 py-1.5 text-adan-muted hover:text-adan-text">Quitar</button>}
      </div>
      {error && <p role="alert" className="mt-2 text-xs text-adan-danger">{error}</p>}
      <div className="mt-4 flex justify-end gap-2 text-sm">
        <button type="button" onClick={onClose} className="rounded-lg px-3 py-1.5 text-adan-muted hover:text-adan-text">Cancelar</button>
        <button type="button" onClick={save} disabled={saving} className="rounded-lg bg-adan-accent px-4 py-1.5 font-semibold text-white disabled:opacity-50">
          {saving ? 'Guardando…' : 'Guardar'}
        </button>
      </div>
    </div>
  )
}

// Lo que se puede abrir de cada Nivel en ADÁN real
const LEVEL_LINK: Record<number, (id: string) => string> = {
  1: (id) => `/nivel1/${id}`,
  2: (id) => `/nivel/2/${id}`, 3: (id) => `/nivel/3/${id}`, 4: (id) => `/nivel/4/${id}`,
  5: (id) => `/nivel/5/${id}`, 6: (id) => `/nivel/6/${id}`, 7: (id) => `/nivel/7/${id}`,
}

function levelPath(n: number, companyId: string): string {
  return (LEVEL_LINK[n] ?? ((id: string) => `/ruta/${id}`))(companyId)
}

export default function CompanyBar({ companyId, company, onCompany }: {
  companyId: string
  company: Company | null
  onCompany: (c: Company) => void
}) {
  const navigate = useNavigate()
  const [companies, setCompanies] = useState<Company[]>([])
  const [levels, setLevels] = useState<LevelView[]>([])
  const [paid, setPaid] = useState<AppleCompanyLevel[]>([])
  const [required, setRequired] = useState(false)
  const [menu, setMenu] = useState<'switch' | 'brand' | null>(null)
  const [paying, setPaying] = useState<number | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    void Promise.all([api.getCompanies(), api.getLevels(companyId), api.getAppleLevels(companyId)])
      .then(([cs, lv, ap]) => {
        if (cancelled) return
        setCompanies(cs)
        setLevels(lv)
        setPaid(ap.levels)
        setRequired(ap.required)
      })
      .catch(() => undefined)
    return () => { cancelled = true }
  }, [companyId])

  const pay = async (level: number) => {
    setPaying(level)
    setError(null)
    try {
      await api.payLevel(companyId, level)
      setPaid((await api.getAppleLevels(companyId)).levels)
    } catch (err) {
      setError(errorMessage(err))
    } finally {
      setPaying(null)
    }
  }

  const done = levels.filter((l) => l.status === 'completed').length
  const current = levels.find((l) => l.status === 'active')

  return (
    <div className="border-b border-adan-border bg-adan-bg/60 px-4 sm:px-6">
      <div className="max-w-7xl mx-auto flex flex-wrap items-center gap-3 py-2">
        <div className="relative">
          <button type="button" onClick={() => setMenu(menu === 'switch' ? null : 'switch')} aria-expanded={menu === 'switch'}
            className="flex items-center gap-2 rounded-xl px-2 py-1 hover:bg-adan-surface" title="Cambiar de empresa">
            {company && <CompanyMark company={company} size={28} />}
            <span className="text-sm font-semibold max-w-[12rem] truncate">{company?.name ?? 'Empresa'}</span>
            <span className="text-adan-muted text-xs" aria-hidden="true">▾</span>
          </button>
          {menu === 'switch' && (
            <div className="absolute left-0 top-full z-50 mt-2 w-72 rounded-2xl border border-adan-border bg-adan-surface p-2 shadow-xl">
              <p className="px-2 py-1 text-[11px] font-semibold uppercase tracking-wider text-adan-muted">Tus empresas</p>
              {companies.map((c) => (
                <button key={c.id} type="button" onClick={() => { setMenu(null); navigate(`/ruta/${c.id}`) }}
                  className={`flex w-full items-center gap-2 rounded-lg px-2 py-1.5 text-left text-sm hover:bg-adan-bg ${c.id === companyId ? 'ring-1 ring-adan-accent' : ''}`}>
                  <CompanyMark company={c} size={24} /> <span className="truncate">{c.name}</span>
                </button>
              ))}
              <Link to="/bienvenida?nueva=1" className="mt-1 block rounded-lg px-2 py-1.5 text-sm text-adan-accent hover:bg-adan-bg">+ Nueva empresa o explorar</Link>
            </div>
          )}
          {menu === 'brand' && company && <BrandEditor company={company} onSaved={onCompany} onClose={() => setMenu(null)} />}
        </div>
        {company && (
          <button type="button" onClick={() => setMenu(menu === 'brand' ? null : 'brand')} className="text-xs text-adan-muted hover:text-adan-text">
            🎨 Identidad
          </button>
        )}
        <Link to={`/marca/${companyId}`} className="text-xs text-adan-muted hover:text-adan-text">🏷️ Marca</Link>
        <Link to={`/expediente/${companyId}`} className="text-xs text-adan-muted hover:text-adan-text">📁 Expediente</Link>
        <Link to={`/biblioteca/${companyId}`} className="text-xs text-adan-muted hover:text-adan-text">📚 Biblioteca</Link>

        {/* Checklist de los 7 Niveles, con flechas para ir al anterior o al siguiente */}
        <span className="ml-auto flex items-center gap-1">
          <button type="button" aria-label="Nivel anterior" title="Nivel anterior" disabled={!current || current.number <= 1}
            onClick={() => current && navigate(levelPath(current.number - 1, companyId))}
            className="grid h-7 w-7 place-items-center rounded-full border border-adan-border text-sm hover:border-adan-accent disabled:opacity-30">‹</button>
        <ol aria-label="Avance de los 7 Niveles" className="flex items-center gap-1 overflow-x-auto">
          {[1, 2, 3, 4, 5, 6, 7].map((n) => {
            const lv = levels.find((l) => l.number === n)
            const ap = paid.find((p) => p.level === n)
            const state = lv?.status ?? 'blocked'
            const link = LEVEL_LINK[n]
            const label = `Nivel ${n}${lv ? `: ${lv.name}` : ''} · ${state === 'completed' ? 'cerrado' : state === 'active' ? 'en curso' : 'bloqueado'}${ap ? ` · ${ap.paid ? 'pagado' : `${ap.apples} @pples`}` : ''}`
            const dot = (
              <span title={label} aria-label={label}
                className={`grid h-7 w-7 place-items-center rounded-full text-[11px] font-bold ${
                  state === 'completed' ? 'bg-adan-success text-white' : state === 'active' ? 'bg-adan-accent text-white ring-2 ring-adan-accent/40' : 'bg-adan-surface text-adan-muted'}`}>
                {state === 'completed' ? '✓' : n}
              </span>
            )
            return (
              <li key={n} className="flex items-center gap-1">
                {link && state !== 'blocked' ? <Link to={link(companyId)}>{dot}</Link> : dot}
                {n < 7 && <span className={`h-0.5 w-3 ${state === 'completed' ? 'bg-adan-success' : 'bg-adan-border'}`} aria-hidden="true" />}
              </li>
            )
          })}
        </ol>
          <button type="button" aria-label="Nivel siguiente" title="Nivel siguiente (cuando el actual esté cerrado)"
            disabled={!current || !levels.some((l) => l.number === current.number + 1 && l.status !== 'blocked')}
            onClick={() => current && navigate(levelPath(current.number + 1, companyId))}
            className="grid h-7 w-7 place-items-center rounded-full border border-adan-border text-sm hover:border-adan-accent disabled:opacity-30">›</button>
        </span>
        <span className="text-xs text-adan-muted whitespace-nowrap">{done} de 7{current ? ` · en curso: ${current.name}` : ''}</span>
        {current && paid.length > 0 && !paid.find((p) => p.level === current.number)?.paid && (
          <button type="button" onClick={() => pay(current.number)} disabled={paying !== null}
            className={`rounded-lg px-3 py-1 text-xs font-semibold ${required ? 'bg-adan-accent text-white' : 'border border-adan-border text-adan-muted hover:text-adan-text'}`}>
            {paying ? 'Pagando…' : `🍎 Activar Nivel ${current.number} · ${paid.find((p) => p.level === current.number)?.apples} @pples`}
          </button>
        )}
      </div>
      {error && (
        <p role="alert" className="max-w-7xl mx-auto pb-2 text-xs text-adan-danger">
          {error} <Link to="/apples" className="underline">Cargar @pples</Link>
        </p>
      )}
    </div>
  )
}
