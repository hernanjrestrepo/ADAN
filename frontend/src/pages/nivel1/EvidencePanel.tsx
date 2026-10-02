import { useCallback, useEffect, useState, type FormEvent } from 'react'
import Alert from '../../components/ui/Alert'
import Badge from '../../components/ui/Badge'
import Button from '../../components/ui/Button'
import Card from '../../components/ui/Card'
import { Field, TextAreaField } from '../../components/ui/Field'
import { EmptyState, LoadingState } from '../../components/ui/States'
import { api, errorMessage } from '../../lib/api'
import type { Evidence, EvidenceKind, EvidencePolarity, EvidenceVerification, GatePreview } from '../../types'
import { KIND } from './evidenceLabels'

// Evidencia del Nivel 1 (AD-CMP-05): lo único que mueve el Problem Score y abre el Gate
function VerificationNote({ v }: { v: EvidenceVerification }) {
  const text = {
    verified: `Fuente verificada${v.title ? `: «${v.title}»` : ''}`,
    unreachable: 'No se pudo abrir la fuente: revisa el enlace',
    blocked: 'Enlace no permitido (dirección interna o no pública)',
  }[v.status]
  return (
    <p className={`text-xs mt-1 ${v.status === 'verified' ? 'text-adan-success' : 'text-adan-warning'}`}
      data-testid="verification">
      {v.status === 'verified' ? '✓ ' : '⚠ '}{text}
    </p>
  )
}

interface EvidencePanelProps {
  companyId: string
  onChanged: () => void
}

function GateProgress({ gate }: { gate: GatePreview }) {
  const b = gate.breakdown
  return (
    <Card className={gate.sufficient ? '!border-adan-success/50' : '!border-adan-warning/40'} data-testid="gate-progress">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="text-sm text-adan-muted">Para cerrar el Nivel 1</p>
          <h3 className="text-lg font-bold">
            {gate.sufficient ? 'La evidencia ya alcanza ✓' : 'Todavía falta evidencia'}
          </h3>
        </div>
        <div className="text-right">
          <p className="text-2xl font-bold text-adan-accent">{gate.value.toFixed(0)}</p>
          <p className="text-xs text-adan-muted">Problem Score · confianza {gate.confidence.toFixed(0)} %</p>
        </div>
      </div>
      <div className="flex flex-wrap gap-2 mt-4 text-xs">
        {(['external', 'testimony', 'inference'] as EvidenceKind[]).map((k) => (
          <Badge key={k} tone={KIND[k].tone}>{KIND[k].label}: {b[k].supports} a favor · {b[k].contradicts} en contra</Badge>
        ))}
      </div>
      {!gate.sufficient && (
        <ul className="mt-4 space-y-1 text-sm list-disc pl-5" aria-label="Lo que falta">
          {gate.missing.map((m) => <li key={m}>{m}</li>)}
        </ul>
      )}
    </Card>
  )
}

export default function EvidencePanel({ companyId, onChanged }: EvidencePanelProps) {
  const [items, setItems] = useState<Evidence[]>([])
  const [gate, setGate] = useState<GatePreview | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [claim, setClaim] = useState('')
  const [kind, setKind] = useState<'external' | 'testimony'>('external')
  const [polarity, setPolarity] = useState<EvidencePolarity>('supports')
  const [source, setSource] = useState('')
  const [saving, setSaving] = useState(false)
  const [retiring, setRetiring] = useState<string | null>(null)
  const [reason, setReason] = useState('')
  const [csiConnected, setCsiConnected] = useState(false)
  const [searching, setSearching] = useState(false)
  const [csiNote, setCsiNote] = useState<string | null>(null)

  const fetchAll = useCallback(
    () => Promise.all([api.listEvidence(companyId), api.getGatePreview(companyId)]),
    [companyId],
  )

  useEffect(() => {
    let cancelled = false
    api.getCsiStatus(companyId).then((s) => { if (!cancelled) setCsiConnected(s.connected) }).catch(() => undefined)
    fetchAll()
      .then(([list, preview]) => { if (!cancelled) { setItems(list); setGate(preview) } })
      .catch((err: unknown) => { if (!cancelled) setError(errorMessage(err)) })
      .finally(() => { if (!cancelled) setLoading(false) })
    return () => { cancelled = true }
  }, [companyId, fetchAll])

  const reload = async () => {
    const [list, preview] = await fetchAll()
    setItems(list)
    setGate(preview)
    onChanged()
  }

  const submit = async (e: FormEvent) => {
    e.preventDefault()
    setSaving(true)
    setError(null)
    try {
      await api.addEvidence(companyId, { claim: claim.trim(), kind, polarity, source: source.trim() || undefined })
      setClaim('')
      setSource('')
      await reload()
    } catch (err) {
      setError(errorMessage(err))
    } finally {
      setSaving(false)
    }
  }

  // CSI propone evidencia externa; cuenta solo cuando el cliente la confirma (WO-108)
  const searchCsi = async () => {
    setSearching(true)
    setError(null)
    try {
      const found = await api.searchCsi(companyId)
      setCsiNote(found.length ? `CSI propuso ${found.length} ${found.length === 1 ? 'dato' : 'datos'}: revísalos abajo.`
        : 'CSI no encontró datos nuevos para este problema.')
      await reload()
    } catch (err) {
      setError(errorMessage(err))
    } finally {
      setSearching(false)
    }
  }

  const confirm = async (id: string) => {
    setError(null)
    try {
      await api.confirmEvidence(companyId, id)
      await reload()
    } catch (err) {
      setError(errorMessage(err))
    }
  }

  const retire = async (id: string) => {
    setError(null)
    try {
      await api.archiveEvidence(companyId, id, reason.trim())
      setRetiring(null)
      setReason('')
      await reload()
    } catch (err) {
      setError(errorMessage(err))
    }
  }

  if (loading) return <LoadingState label="Cargando evidencia..." />

  return (
    <div className="max-w-4xl mx-auto p-4 sm:p-6 overflow-y-auto h-full space-y-6">
      <div>
        <h2 className="text-2xl font-bold">Evidencia</h2>
        <p className="text-sm text-adan-muted mt-1">
          Conversar no prueba nada por sí solo: el Problem Score y el cierre del Nivel salen de lo que puedas
          mostrar. Un dato verificable pesa más que un testimonio, y un testimonio más que una inferencia.
        </p>
      </div>
      {error && <Alert message={error} onClose={() => setError(null)} />}
      {gate && <GateProgress gate={gate} />}

      <Card>
        <h3 className="font-bold mb-4">Registrar evidencia</h3>
        <form onSubmit={submit} className="space-y-4">
          <TextAreaField label="¿Qué afirmas?" value={claim} onChange={(e) => setClaim(e.target.value)}
            placeholder="Ej.: El 40 % de las tiendas de café pierde producto cada semana" required minLength={10} />
          <fieldset>
            <legend className="block text-sm text-adan-muted mb-2">¿Qué tipo de evidencia es?</legend>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {(['external', 'testimony'] as const).map((k) => (
                <label key={k} className={`flex gap-3 p-3 rounded-lg border cursor-pointer ${
                  kind === k ? 'border-adan-accent bg-adan-accent/5' : 'border-adan-border'}`}>
                  <input type="radio" name="evidence-kind" className="mt-1" checked={kind === k}
                    onChange={() => setKind(k)} />
                  <span>
                    <span className="block text-sm font-medium">{KIND[k].label}</span>
                    <span className="block text-xs text-adan-muted">{KIND[k].hint}</span>
                  </span>
                </label>
              ))}
            </div>
          </fieldset>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Field label={kind === 'external' ? 'Fuente (obligatoria)' : 'Fuente (opcional)'} value={source}
              onChange={(e) => setSource(e.target.value)} required={kind === 'external'}
              placeholder="Enlace, documento o referencia" />
            <div>
              <label htmlFor="evidence-polarity" className="block text-sm text-adan-muted mb-1">¿Qué hace con el problema?</label>
              <select id="evidence-polarity" value={polarity}
                onChange={(e) => setPolarity(e.target.value as EvidencePolarity)}
                className="w-full px-4 py-3 bg-adan-bg border border-adan-border rounded-lg text-adan-text focus:outline-none focus:border-adan-accent">
                <option value="supports">Lo respalda</option>
                <option value="contradicts">Lo contradice</option>
              </select>
            </div>
          </div>
          <Button type="submit" loading={saving}>Registrar evidencia</Button>
        </form>
      </Card>

      <Card className="!p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4" data-testid="csi">
        <div>
          <h3 className="font-bold">Inteligencia externa (CSI)</h3>
          <p className="text-sm text-adan-muted">
            {csiConnected
              ? 'ADÁN puede pedirle a CSI estudios y datos sobre tu problema. Tú decides cuáles cuentan.'
              : 'CSI todavía no está conectado. Mientras tanto, ADÁN verifica cada fuente que registras.'}
          </p>
          {csiNote && <p className="text-sm mt-2">{csiNote}</p>}
        </div>
        <Button variant="secondary" loading={searching} disabled={!csiConnected} onClick={searchCsi}>
          Buscar evidencia en CSI
        </Button>
      </Card>

      {items.length === 0 ? (
        <EmptyState icon="🔎" title="Sin evidencia todavía">
          Empieza por un dato que cualquiera pueda verificar: es lo que más pesa para cerrar el Nivel 1.
        </EmptyState>
      ) : (
        <ul className="space-y-3" aria-label="Evidencia registrada">
          {items.map((e) => (
            <li key={e.id}>
              <Card className="!p-4" data-testid="evidence-item">
                <div className="flex flex-wrap items-center gap-2 mb-2">
                  <Badge tone={KIND[e.kind].tone}>{KIND[e.kind].label}</Badge>
                  <Badge tone={e.polarity === 'supports' ? 'green' : 'red'}>
                    {e.polarity === 'supports' ? 'Respalda' : 'Contradice'}
                  </Badge>
                  <span className="text-xs text-adan-muted ml-auto">
                    {new Date(e.created_at).toLocaleDateString('es-CO')}
                  </span>
                </div>
                {!e.confirmed && (
                  <p className="text-xs text-adan-warning mb-2">Propuesta por CSI: todavía no cuenta para tu Score.</p>
                )}
                <p className="text-sm">{e.claim}</p>
                {e.verification && <VerificationNote v={e.verification} />}
                {e.source && (
                  <p className="text-xs text-adan-muted mt-1 break-all">
                    Fuente: {/^https?:\/\//.test(e.source)
                      ? <a href={e.source} target="_blank" rel="noreferrer" className="text-adan-accent hover:underline">{e.source}</a>
                      : e.source}
                  </p>
                )}
                {!e.confirmed && retiring !== e.id && (
                  <div className="flex gap-2 mt-3">
                    <Button size="sm" variant="success" onClick={() => confirm(e.id)}>Confirmar</Button>
                    <Button size="sm" variant="ghost" onClick={() => setRetiring(e.id)}>Descartar</Button>
                  </div>
                )}
                {e.kind !== 'inference' && (e.confirmed || retiring === e.id) && (retiring === e.id ? (
                  <div className="flex flex-wrap items-end gap-2 mt-3">
                    <Field className="flex-1 min-w-48" label="¿Por qué la retiras?" value={reason}
                      onChange={(ev) => setReason(ev.target.value)} />
                    <Button size="sm" variant="danger" disabled={reason.trim().length < 5}
                      onClick={() => retire(e.id)}>Retirar</Button>
                    <Button size="sm" variant="ghost" onClick={() => setRetiring(null)}>Cancelar</Button>
                  </div>
                ) : (
                  <Button size="sm" variant="ghost" className="mt-2 -ml-3" onClick={() => setRetiring(e.id)}>
                    Retirar
                  </Button>
                ))}
              </Card>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
