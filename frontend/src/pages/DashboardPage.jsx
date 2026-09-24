import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../lib/api'
import AiDisclaimer from '../components/AiDisclaimer'

export default function DashboardPage({ user }) {
  const [companies, setCompanies] = useState([])
  const [showCreate, setShowCreate] = useState(false)
  const [form, setForm] = useState({ name: '', description: '', industry: '', country: '' })
  const [loading, setLoading] = useState(true)
  const [creating, setCreating] = useState(false)
  const navigate = useNavigate()

  useEffect(() => {
    api.getCompanies()
      .then(setCompanies)
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [])

  const handleCreate = async (e) => {
    e.preventDefault()
    setCreating(true)
    try {
      const company = await api.createCompany(form.name, form.description, form.industry, form.country)
      navigate(`/nivel1/${company.id}`)
    } catch (err) {
      alert(err.message)
    } finally {
      setCreating(false)
    }
  }

  return (
    <div className="min-h-screen bg-adan-bg">
      {/* Header */}
      <header className="border-b border-adan-border px-6 py-4">
        <div className="flex items-center justify-between max-w-6xl mx-auto">
          <h1 className="text-2xl font-bold">ADÁN</h1>
          <div className="flex items-center gap-4">
            <span className="text-adan-muted">{user.name}</span>
            <button
              onClick={() => { api.logout(); window.location.href = '/login' }}
              className="text-sm text-adan-muted hover:text-adan-text"
            >
              Salir
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto p-6">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h2 className="text-3xl font-bold">Mis Empresas</h2>
            <p className="text-adan-muted mt-1">Gestiona tus proyectos empresariales</p>
          </div>
          <button
            onClick={() => setShowCreate(true)}
            className="px-6 py-3 bg-adan-accent text-white rounded-lg font-medium hover:bg-blue-600"
          >
            + Nueva Empresa
          </button>
        </div>

        {/* Create Company Modal */}
        {showCreate && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <div className="bg-adan-surface rounded-xl p-6 w-full max-w-md">
              <h3 className="text-xl font-bold mb-4">Crear Empresa</h3>
              <form onSubmit={handleCreate} className="space-y-4">
                <input
                  type="text"
                  placeholder="Nombre de la empresa"
                  value={form.name}
                  onChange={(e) => setForm({ ...form, name: e.target.value })}
                  className="w-full px-4 py-3 bg-adan-bg border border-adan-border rounded-lg text-adan-text focus:outline-none focus:border-adan-accent"
                  required
                />
                <textarea
                  placeholder="Descripción (opcional)"
                  value={form.description}
                  onChange={(e) => setForm({ ...form, description: e.target.value })}
                  className="w-full px-4 py-3 bg-adan-bg border border-adan-border rounded-lg text-adan-text focus:outline-none focus:border-adan-accent h-20 resize-none"
                />
                <div className="grid grid-cols-2 gap-4">
                  <input
                    type="text"
                    placeholder="Industria"
                    value={form.industry}
                    onChange={(e) => setForm({ ...form, industry: e.target.value })}
                    className="px-4 py-3 bg-adan-bg border border-adan-border rounded-lg text-adan-text focus:outline-none focus:border-adan-accent"
                  />
                  <input
                    type="text"
                    placeholder="País"
                    value={form.country}
                    onChange={(e) => setForm({ ...form, country: e.target.value })}
                    className="px-4 py-3 bg-adan-bg border border-adan-border rounded-lg text-adan-text focus:outline-none focus:border-adan-accent"
                  />
                </div>
                <div className="flex gap-3">
                  <button
                    type="button"
                    onClick={() => setShowCreate(false)}
                    className="flex-1 py-3 border border-adan-border rounded-lg text-adan-muted hover:text-adan-text"
                  >
                    Cancelar
                  </button>
                  <button
                    type="submit"
                    disabled={creating}
                    className="flex-1 py-3 bg-adan-accent text-white rounded-lg font-medium hover:bg-blue-600 disabled:opacity-50"
                  >
                    {creating ? 'Creando...' : 'Crear'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Companies List */}
        {loading ? (
          <div className="text-center text-adan-muted py-12">Cargando empresas...</div>
        ) : companies.length === 0 ? (
          <div className="text-center py-16">
            <div className="text-6xl mb-4">🏢</div>
            <h3 className="text-xl font-bold mb-2">No hay empresas todavía</h3>
            <p className="text-adan-muted mb-6">Crea tu primera empresa para comenzar con ADÁN</p>
            <button
              onClick={() => setShowCreate(true)}
              className="px-6 py-3 bg-adan-accent text-white rounded-lg font-medium hover:bg-blue-600"
            >
              Crear mi primera empresa
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {companies.map((company) => (
              <div
                key={company.id}
                onClick={() => navigate(`/nivel1/${company.id}`)}
                className="bg-adan-surface border border-adan-border rounded-xl p-6 cursor-pointer hover:border-adan-accent transition-colors"
              >
                <h3 className="text-lg font-bold mb-1">{company.name}</h3>
                {company.description && (
                  <p className="text-adan-muted text-sm mb-3 line-clamp-2">{company.description}</p>
                )}
                <div className="flex items-center gap-4 text-xs text-adan-muted">
                  {company.industry && <span>{company.industry}</span>}
                  {company.country && <span>{company.country}</span>}
                </div>
                <div className="mt-4 flex items-center justify-between">
                  <span className="text-xs text-adan-muted">
                    Madurez: {(company.maturity * 100).toFixed(0)}%
                  </span>
                  <span className="text-xs px-2 py-1 bg-adan-accent/20 text-adan-accent rounded">
                    Nivel 1
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
        <AiDisclaimer className="mt-12 text-center" />
      </main>
    </div>
  )
}
