import { expect, test } from '@playwright/test'
import { FakeApi, USER } from './fakeApi'

test('sin sesión, cualquier ruta lleva al login', async ({ page }) => {
  await new FakeApi().install(page)
  await page.goto('/nivel1/c1')
  await expect(page).toHaveURL(/\/login$/)
})

test('los errores de validación del backend se muestran en la página', async ({ page }) => {
  const api = new FakeApi()
  api.overrides.set('POST /auth/register', [422, { detail: [{ msg: 'La contraseña es demasiado repetitiva' }] }])
  await api.install(page)
  await page.goto('/register')
  await page.getByLabel('Nombre').fill('Ana')
  await page.getByLabel('Email').fill(USER.email)
  await page.getByLabel('Contraseña').fill('aaaaaaaaaaaa')
  await page.getByRole('button', { name: 'Crear cuenta' }).click()
  await expect(page.getByRole('alert')).toHaveText('La contraseña es demasiado repetitiva')
})

test('registro, sesión y cierre de sesión', async ({ page }) => {
  const api = new FakeApi()
  await api.install(page)
  await page.goto('/register')
  await page.getByLabel('Nombre').fill('Ana')
  await page.getByLabel('Email').fill(USER.email)
  await page.getByLabel('Contraseña').fill('clave-segura-2026')
  await page.getByRole('button', { name: 'Crear cuenta' }).click()

  await expect(page).toHaveURL(/\/dashboard$/)
  await expect(page.getByText(USER.name)).toBeVisible()
  await expect(page.getByText(/ADÁN es una inteligencia artificial/)).toBeVisible()
  // El token no se guarda en el navegador: la sesión es la cookie httpOnly del backend
  expect(await page.evaluate(() => localStorage.length)).toBe(0)

  await page.getByRole('button', { name: 'Salir' }).click()
  await expect(page).toHaveURL(/\/login$/)
  expect(api.callsTo('POST', '/auth/logout')).toHaveLength(1)
})

test('toda petición lleva la cabecera anti-CSRF', async ({ page }) => {
  const api = new FakeApi()
  await api.install(page)
  await page.goto('/login')
  await page.getByLabel('Email').fill(USER.email)
  await page.getByLabel('Contraseña').fill('clave-segura-2026')
  await page.getByRole('button', { name: 'Ingresar' }).click()
  await expect(page).toHaveURL(/\/dashboard$/)
  expect(api.calls.length).toBeGreaterThan(0)
  for (const call of api.calls) expect(call.headers['x-requested-with']).toBe('adan')
})
