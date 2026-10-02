import { describe, expect, it, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, Route, Routes } from 'react-router'
import Nivel1Page from './Nivel1Page'
import { api } from '../lib/api'
import type { BoardRoomResult, Nivel1Status } from '../lib/types'

const status = {
  company: { id: 'c1', name: 'Café Andino' },
  project: { id: 'p1' },
  level: { id: 'l1', status: 'active' },
  card: null,
  conversation: null,
  messages: [],
  scores: [],
  documents: [],
} as unknown as Nivel1Status

const board: BoardRoomResult = {
  decision: 'PIVOT',
  score: 61.4,
  confidence: 72,
  summary: '**Decisión del Board Room: PIVOT**\n\nEl Board recomienda ajustar el segmento objetivo.',
  votes: [
    {
      agent: 'CFO', analysis: 'Márgenes bajos en retail.', justification: '', vote: 'PIVOT',
      confidence: 70, key_strengths: [], key_concerns: ['Capital de trabajo'], questions: [],
      model: 'test', duration_s: 1,
    },
  ],
  concerns_unanimous: [],
  concerns_majority: [],
  strengths_unanimous: [],
  dissent: '',
}

describe('Nivel1Page', () => {
  it('muestra el consenso y los votos del Board Room', async () => {
    vi.spyOn(api, 'getNivel1Status').mockResolvedValue(status)
    const runBoard = vi.spyOn(api, 'runBoardRoom').mockResolvedValue(board)

    render(
      <MemoryRouter initialEntries={['/nivel1/c1']}>
        <Routes>
          <Route path="/nivel1/:companyId" element={<Nivel1Page />} />
        </Routes>
      </MemoryRouter>,
    )
    expect(await screen.findByText('Café Andino')).toBeInTheDocument()

    await userEvent.setup().click(screen.getByRole('button', { name: /Ejecutar Board Room/ }))

    expect(runBoard).toHaveBeenCalledWith('c1')
    expect(await screen.findByText('Decisión: Pivotar')).toBeInTheDocument()
    expect(screen.getByText('Márgenes bajos en retail.')).toBeInTheDocument()
    expect(screen.getByText('Capital de trabajo')).toBeInTheDocument()
    // el resumen llega en Markdown: se renderiza, no se muestra con asteriscos
    expect(screen.getByText('Decisión del Board Room: PIVOT').tagName).toBe('STRONG')
    expect(screen.queryByText(/\*\*/)).not.toBeInTheDocument()
  })
})
