import { describe, expect, it, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router'
import App from './App'
import { api } from './lib/api'

describe('App', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
    api.setToken(null)
  })

  it('sin sesión redirige al login', async () => {
    render(
      <MemoryRouter initialEntries={['/dashboard']}>
        <App />
      </MemoryRouter>,
    )
    expect(await screen.findByRole('button', { name: 'Ingresar' })).toBeInTheDocument()
  })

  it('con token válido muestra el dashboard', async () => {
    localStorage.setItem('adan_token', 'tok')
    vi.spyOn(api, 'getMe').mockResolvedValue({ id: 'u1', email: 'h@adan.ai', name: 'Hernán', role: 'user' })
    vi.spyOn(api, 'getCompanies').mockResolvedValue([])
    render(
      <MemoryRouter initialEntries={['/login']}>
        <App />
      </MemoryRouter>,
    )
    expect(await screen.findByText('Mis Empresas')).toBeInTheDocument()
    expect(screen.getByText('Hernán')).toBeInTheDocument()
  })

  it('con token inválido cierra la sesión y vuelve al login', async () => {
    localStorage.setItem('adan_token', 'expirado')
    vi.spyOn(api, 'getMe').mockRejectedValue(new Error('Invalid token'))
    render(
      <MemoryRouter initialEntries={['/dashboard']}>
        <App />
      </MemoryRouter>,
    )
    expect(await screen.findByRole('button', { name: 'Ingresar' })).toBeInTheDocument()
    expect(localStorage.getItem('adan_token')).toBeNull()
  })
})
