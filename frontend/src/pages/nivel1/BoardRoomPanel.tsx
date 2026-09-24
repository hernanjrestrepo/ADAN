import VoteBadge from '../../components/VoteBadge'
import Button from '../../components/ui/Button'
import Card from '../../components/ui/Card'
import { EmptyState, LoadingState } from '../../components/ui/States'
import type { BoardConsensus } from '../../types'

interface BoardRoomPanelProps {
  result: BoardConsensus | null
  running: boolean
  onRun: () => void
}

export default function BoardRoomPanel({ result, running, onRun }: BoardRoomPanelProps) {
  return (
    <div className="max-w-4xl mx-auto p-6 overflow-y-auto h-full">
      <h2 className="text-2xl font-bold mb-6">Board Room</h2>
      {running ? (
        <LoadingState label="El Board está deliberando..." />
      ) : !result ? (
        <EmptyState icon="🏛️" title="Board Room" action={<Button onClick={onRun}>Ejecutar Board Room</Button>}>
          Ejecuta el Board Room para que cada agente analice tu problema.
        </EmptyState>
      ) : (
        <div className="space-y-6">
          <Card>
            <div className="flex items-center justify-between">
              <h3 className="font-bold">Decisión del Board</h3>
              <VoteBadge vote={result.decision} />
            </div>
            <p className="text-sm text-adan-muted mt-2">
              Score {result.score.toFixed(0)}/100 · Confianza {result.confidence.toFixed(0)}%
            </p>
            {result.dissent && (
              <div className="mt-4 text-sm whitespace-pre-wrap">
                <span className="font-bold">Disenso:</span>{'\n'}{result.dissent}
              </div>
            )}
            <p className="text-xs text-adan-muted mt-4">Es una propuesta del Board: la decisión final es tuya.</p>
          </Card>
          {result.votes.map((vote) => (
            <Card key={vote.agent} data-testid="agent-vote">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-full bg-adan-accent/20 flex items-center justify-center text-adan-accent font-bold">
                  {vote.agent[0]}
                </div>
                <div className="flex-1">
                  <h3 className="font-bold">{vote.agent}</h3>
                  <p className="text-xs text-adan-muted">Agente del Board Room · confianza {vote.confidence.toFixed(0)}%</p>
                </div>
                <VoteBadge vote={vote.vote} />
              </div>
              <div className="text-sm whitespace-pre-wrap text-adan-text/90">{vote.analysis || vote.justification}</div>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
