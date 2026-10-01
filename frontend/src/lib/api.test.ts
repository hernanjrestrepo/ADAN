import { describe, expect, it, vi, beforeEach } from 'vitest'
import { ApiClient, ApiError } from './api'

function mockFetch(status: number, body: unknown) {
  const fn = vi.fn().mockResolvedValue({
    ok: status >= 200 && status < 300,
    status,
    json: () => Promise.resolve(body),
  })
  vi.stubGlobal('fetch', fn)
  return fn
}

describe('ApiClient', () => {
  beforeEach(() => {
    vi.unstubAllGlobals()
  })

  it('guarda el token al iniciar sesión y lo envía en las siguientes requests', async () => {
    const client = new ApiClient()
    mockFetch(200, { access_token: 'tok-123', token_type: 'bearer', user: { id: 'u1' } })
    await client.login('a@b.co', 'secret1')
    expect(localStorage.getItem('adan_token')).toBe('tok-123')

    const fetchMock = mockFetch(200, { id: 'u1', email: 'a@b.co', name: 'A', role: 'user' })
    await client.getMe()
    const [url, init] = fetchMock.mock.calls[0] as [string, RequestInit]
    expect(url).toBe('/api/v1/auth/me')
    expect(new Headers(init.headers).get('Authorization')).toBe('Bearer tok-123')
  })

  it('logout borra el token', () => {
    const client = new ApiClient()
    client.setToken('x')
    client.logout()
    expect(client.token).toBeNull()
    expect(localStorage.getItem('adan_token')).toBeNull()
  })

  it('propaga el detail de FastAPI como ApiError con status', async () => {
    const client = new ApiClient()
    mockFetch(401, { detail: 'Invalid credentials' })
    await expect(client.login('a@b.co', 'bad')).rejects.toMatchObject({
      name: 'ApiError',
      message: 'Invalid credentials',
      status: 401,
    })
  })

  it('aplana errores de validación (422) en un mensaje legible', async () => {
    const client = new ApiClient()
    mockFetch(422, { detail: [{ loc: ['body', 'password'], msg: 'String should have at least 6 characters' }] })
    const err = await client.register('a@b.co', 'A', '123').catch((e: unknown) => e)
    expect(err).toBeInstanceOf(ApiError)
    expect((err as ApiError).message).toBe('String should have at least 6 characters')
  })

  it('usa un mensaje por defecto si la respuesta de error no es JSON', async () => {
    const client = new ApiClient()
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
      ok: false, status: 502, json: () => Promise.reject(new Error('not json')),
    }))
    await expect(client.getCompanies()).rejects.toThrow('HTTP 502')
  })
})
