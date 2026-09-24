import { useEffect, useState, type FormEvent } from 'react'
import { useNavigate } from 'react-router'
import AppShell from '../components/AppShell'
import Alert from '../components/ui/Alert'
import Badge from '../components/ui/Badge'
import Button from '../components/ui/Button'
import Card from '../components/ui/Card'
import { Field, TextAreaField } from '../components/ui/Field'
import { EmptyState, LoadingState } from '../components/ui/States'
import { api, errorMessage } from '../lib/api'
import type { Company, CompanyInput } from '../types'

const EMPTY_FORM: CompanyInput = { name: '', description: '', industry: '', country: '' }

function CreateCompanyDialog({ onClose }: { onClose: () => void }) {
  const navigate = useNavigate()
  const [form, setForm] = useState<CompanyInput>(EMPTY_FORM)
  const [creating, setCreating] = useState(false)
  const [error, setError] = useState<string | null>(null)

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
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" role="dialog"
      aria-modal="true" aria-labelledby="create-company-title">
      <div className="bg-adan-surface rounded-xl p-6 w-full max-w-md">
        <h3 id="create-company-title" className="text-xl font-bold mb-4">Crear Empresa</h3>
        <form onSubmit={handleCreate} className="space-y-4">
          <Field label="Nombre de la empresa" value={form.name} onChange={update('name')} maxLength={255} required />
          <TextAreaField label="Descripción (opcional)" value={form.description} onChange={update('description')}
            maxLength={5000} />
          <div className="grid grid-cols-2 gap-4">
            <Field label="Industria" value={form.industry} onChange={update('industry')} maxLength={255} />
            <Field label="País" value={form.country} onChange={update('country')} maxLength={100} />
          </div>
          <Alert message={error} />
          <div className="flex gap-3">
            <Button variant="secondary" className="flex-1" onClick={onClose}>Cancelar</Button>
            <Button type="submit" className="flex-1" disabled={creating}>{creating ? 'Creando...' : 'Crear'}</Button>
          </div>
        </form>
      </div>
    </div>
  )
}

function CompanyCard({ company }: { company: Company }) {
  const navigate = useNavigate()
  return (
    <button type="button" onClick={() => navigate(`/nivel1/${company.id}`)} className="text-left">
      <Card className="h-full hover:border-adan-accent transition-colors">
        <h3 className="text-lg font-bold mb-1">{company.name}</h3>
        {company.description && <p className="text-adan-muted text-sm mb-3 line-clamp-2">{company.description}</p>}
        <div className="flex items-center gap-4 text-xs text-adan-muted">
          {company.industry && <span>{company.industry}</span>}
          {company.country && <span>{company.country}</span>}
        </div>
        <div className="mt-4 flex items-center justify-between">
          <span className="text-xs text-adan-muted">Madurez: {(company.maturity * 100).toFixed(0)}%</span>
          <Badge tone="blue">Nivel 1</Badge>
        </div>
      </Card>
    </button>
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

  const createButton = <Button onClick={() => setShowCreate(true)}>+ Nueva Empresa</Button>

  return (
    <AppShell crumbs={[{ label: 'Mis Empresas' }]}>
      <main className="max-w-6xl mx-auto p-6">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h2 className="text-3xl font-bold">Mis Empresas</h2>
            <p className="text-adan-muted mt-1">Gestiona tus proyectos empresariales</p>
          </div>
          {createButton}
        </div>
        <Alert message={error} onClose={() => setError(null)} />
        {showCreate && <CreateCompanyDialog onClose={() => setShowCreate(false)} />}
        {loading ? (
          <LoadingState label="Cargando empresas..." />
        ) : companies.length === 0 ? (
          <EmptyState icon="🏢" title="No hay empresas todavía"
            action={<Button onClick={() => setShowCreate(true)}>Crear mi primera empresa</Button>}>
            Crea tu primera empresa para comenzar con ADÁN
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
