import ReactMarkdown from 'react-markdown'
import Button from '../../components/ui/Button'
import Card from '../../components/ui/Card'
import { EmptyState, LoadingState } from '../../components/ui/States'
import type { DocumentRecord } from '../../types'

interface DiagnosisPanelProps {
  diagnosis: DocumentRecord | null
  running: boolean
  onGenerate: () => void
}

export default function DiagnosisPanel({ diagnosis, running, onGenerate }: DiagnosisPanelProps) {
  return (
    <div className="max-w-4xl mx-auto p-6 overflow-y-auto h-full">
      <h2 className="text-2xl font-bold mb-6">Diagnóstico del Dolor</h2>
      {running ? (
        <LoadingState label="Generando el diagnóstico..." />
      ) : !diagnosis ? (
        <EmptyState icon="📋" title="Sin diagnóstico" action={<Button onClick={onGenerate}>Generar Diagnóstico</Button>}>
          Genera el diagnóstico formal basado en la conversación y el Board Room.
        </EmptyState>
      ) : (
        <Card>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-bold">{diagnosis.title}</h3>
            <span className="text-xs text-adan-muted">v{diagnosis.version} · {diagnosis.origin}</span>
          </div>
          <div className="markdown">
            <ReactMarkdown>{diagnosis.content ?? ''}</ReactMarkdown>
          </div>
        </Card>
      )}
    </div>
  )
}
