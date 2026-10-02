import { useEffect, useState, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router'
import AppShell from '../components/AppShell'
import Alert from '../components/ui/Alert'
import Badge from '../components/ui/Badge'
import Button from '../components/ui/Button'
import Card from '../components/ui/Card'
import { Field, TextAreaField } from '../components/ui/Field'
import { EmptyState, LoadingState } from '../components/ui/States'
import { useAuth } from '../auth/context'
import { api, errorMessage } from '../lib/api'
import type { Company, CompanyInput } from '../types'

function greeting() {
  const h = new Date().getHours()
  return h < 12 ? 'Buenos días' : h < 19 ? 'Buenas tardes' : 'Buenas noches'
}

const EMPTY_FORM: CompanyInput = { name: '', description: '', industry: '', country: '' }

function CreateCompanyDialog({ onClose }: { onClose: () => void }) {
  const navigate = useNavigate()
  const [form, setForm] = useState<CompanyInput>(EMPTY_FORM)
  const [creating, setCreating] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Escape cierra el diálogo (mientras no se esté creando)
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => { if (e.key === 'Escape' && !creating) onClose() }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [onClose, creating])

  const update = (field: keyof CompanyInput) => (e: { target: { value: string } }) =>
    setForm({ ...form, [field]: e.target.value })

  const handleCreate = async (e: FormEvent) => {
    e.preventDefault()
    setCreating(true)
    setError(null)
    try {
      const company = await api.createCompany(form)
      navigate(`/nivel1/${company.id}`)
    } catch (err) {
      setError(errorMessage(err))
      setCreating(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-end sm:items-center justify-center z-50 p-0 sm:p-4"
      onMouseDown={(e) => { if (e.target === e.currentTarget && !creating) onClose() }}>
      <div className="bg-adan-surface border border-adan-border rounded-t-2xl sm:rounded-2xl p-6 w-full max-w-lg shadow-2xl"
        role="dialog" aria-modal="true" aria-labelledby="create-company-title">
        <h3 id="create-company-title" className="text-xl font-bold">Crear Empresa</h3>
        <p className="text-sm text-adan-muted mt-1 mb-5">
          Nace su Gemelo Digital y empiezas por el Nivel 1: entender el dolor que resuelve.
        </p>
        <form onSubmit={handleCreate} className="space-y-4">
          <Field label="Nombre de la empresa" value={form.name} onChange={update('name')} maxLength={255} required
            autoFocus placeholder="Ej.: Café Andino" />
          <TextAreaField label="Descripción (opcional)" value={form.description} onChange={update('description')}
            maxLength={5000} placeholder="¿Qué hace o qué quieres que haga?" />
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Field label="Industria" value={form.industry} onChange={update('industry')} maxLength={255}
              placeholder="Alimentos" />
            <Field label="País" value={form.country} onChange={update('country')} maxLength={100}
              placeholder="Colombia" />
          </div>
          <Alert message={error} />
          <div className="flex gap-3 pt-2">
            <Button variant="secondary" className="flex-1" onClick={onClose} disabled={creating}>Cancelar</Button>
            <Button type="submit" className="flex-1" loading={creating}>Crear</Button>
          </div>
        </form>
      </div>
    </div>
  )
}

function MaturityBar({ value }: { value: number }) {
  const pct = Math.round(Math.max(0, Math.min(1, value)) * 100)
  return (
    <div>
      <div className="flex justify-between text-xs text-adan-muted mb-1">
        <span>Madurez</span><span className="font-medium text-adan-text">{pct}%</span>
      </div>
      <div className="h-1.5 rounded-full bg-adan-bg overflow-hidden" role="progressbar" aria-valuenow={pct}
        aria-valuemin={0} aria-valuemax={100} aria-label="Madurez">
        <div className="h-full rounded-full bg-gradient-to-r from-adan-accent to-indigo-400" style={{ width: `${pct}%` }} />
      </div>
    </div>
  )
}

function CompanyCard({ company }: { company: Company }) {
  const navigate = useNavigate()
  const meta = [company.industry, company.country].filter(Boolean).join(' · ')
  return (
    <Card className="flex flex-col gap-4 hover:border-adan-accent/60 transition-colors">
      <button type="button" onClick={() => navigate(`/nivel1/${company.id}`)} className="text-left flex-1 group">
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-center gap-3 min-w-0">
            <span aria-hidden="true"
              className="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-adan-surface-2 font-bold text-adan-accent">
              {company.name.slice(0, 1).toUpperCase()}
            </span>
            <div className="min-w-0">
              <h3 className="text-lg font-bold truncate group-hover:text-adan-accent">{company.name}</h3>
              {meta && <p className="text-xs text-adan-muted truncate">{meta}</p>}
            </div>
          </div>
          <Badge tone="blue">Nivel 1</Badge>
        </div>
        {company.description && <p className="text-adan-muted text-sm mt-3 line-clamp-2">{company.description}</p>}
      </button>
      <MaturityBar value={company.maturity} />
      <div className="flex items-center justify-between gap-3 pt-3 border-t border-adan-border">
        <Link to={`/nivel1/${company.id}`} className="text-sm font-medium text-adan-text hover:text-adan-accent">
          Continuar Nivel 1
        </Link>
        {/* Enlace aparte: un enlace no puede ir dentro de un botón */}
        <Link to={`/gemelo/${company.id}`} className="text-sm text-adan-accent hover:underline">
          Gemelo Digital →
        </Link>
      </div>
    </Card>
  )
}

export default function DashboardPage() {
  const [companies, setCompanies] = useState<Company[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showCreate, setShowCreate] = useState(false)

  useEffect(() => {
    api.getCompanies()
      .then(setCompanies)
      .catch((err: unknown) => setError(errorMessage(err)))
      .finally(() => setLoading(false))
  }, [])

  const { user } = useAuth()
  const createButton = <Button onClick={() => setShowCreate(true)}>+ Nueva Empresa</Button>

  return (
    <AppShell crumbs={[{ label: 'Mis Empresas' }]}>
      <main className="max-w-6xl mx-auto p-4 sm:p-6 h-full overflow-y-auto">
        <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4 mb-8">
          <div>
            <p className="text-sm text-adan-muted">{greeting()}{user ? `, ${user.name.split(' ')[0]}` : ''}</p>
            <h2 className="text-3xl font-bold mt-1">Mis Empresas</h2>
            <p className="text-adan-muted mt-1">
              {companies.length > 0
                ? `${companies.length} ${companies.length === 1 ? 'empresa' : 'empresas'} en camino`
                : 'Crea o reinventa una empresa con tu equipo directivo de IA'}
            </p>
          </div>
          {createButton}
        </div>
        <div className="mb-4"><Alert message={error} onClose={() => setError(null)} /></div>
        {showCreate && <CreateCompanyDialog onClose={() => setShowCreate(false)} />}
        {loading ? (
          <LoadingState label="Cargando empresas..." />
        ) : companies.length === 0 ? (
          <EmptyState icon="🏢" title="No hay empresas todavía"
            action={<Button onClick={() => setShowCreate(true)}>Crear mi primera empresa</Button>}>
            Crea tu primera empresa: nace su Gemelo Digital y empiezas por el Nivel 1, entender el dolor que
            resuelve. ADÁN y su Board te acompañan; tú decides.
          </EmptyState>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {companies.map((company) => <CompanyCard key={company.id} company={company} />)}
          </div>
        )}
      </main>
    </AppShell>
  )
}
