import { describe, expect, it, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router'
import LoginPage from './LoginPage'
import { api } from '../lib/api'

const user = { id: 'u1', email: 'h@adan.ai', name: 'Hernán', role: 'user' }

function renderLogin(onLogin = vi.fn()) {
  render(
    <MemoryRouter>
      <LoginPage onLogin={onLogin} />
    </MemoryRouter>,
  )
  return onLogin
}

describe('LoginPage', () => {
  it('envía credenciales y notifica el usuario autenticado', async () => {
    const login = vi.spyOn(api, 'login').mockResolvedValue({ access_token: 't', token_type: 'bearer', user })
    const onLogin = renderLogin()
    const ue = userEvent.setup()

    await ue.type(screen.getByLabelText('Email'), 'h@adan.ai')
    await ue.type(screen.getByLabelText('Contraseña'), 'secret1')
    await ue.click(screen.getByRole('button', { name: 'Ingresar' }))

    expect(login).toHaveBeenCalledWith('h@adan.ai', 'secret1')
    expect(onLogin).toHaveBeenCalledWith(user)
  })

  it('muestra el error del backend', async () => {
    vi.spyOn(api, 'login').mockRejectedValue(new Error('Invalid credentials'))
    const onLogin = renderLogin()
    const ue = userEvent.setup()

    await ue.type(screen.getByLabelText('Email'), 'h@adan.ai')
    await ue.type(screen.getByLabelText('Contraseña'), 'mala')
    await ue.click(screen.getByRole('button', { name: 'Ingresar' }))

    expect(await screen.findByText('Invalid credentials')).toBeInTheDocument()
    expect(onLogin).not.toHaveBeenCalled()
  })
})
