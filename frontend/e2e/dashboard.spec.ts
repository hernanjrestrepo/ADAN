import { expect, test } from '@playwright/test'
import { FakeApi } from './fakeApi'

test('sin empresas, el onboarding hace una sola pregunta y lleva a la primera pregunta de ADÁN', async ({ page }) => {
  const api = new FakeApi()
  api.loggedIn = true
  await api.install(page)
  await page.goto('/dashboard')
  await expect(page).toHaveURL(/\/bienvenida$/)
  await expect(page.getByRole('heading', { name: '¿Cómo se llama tu empresa o tu idea?' })).toBeVisible()

  await page.getByLabel('Nombre de la empresa o de la idea').fill('Nueva SAS')
  await page.getByRole('radio', { name: 'Ya existe' }).check()
  await page.getByRole('button', { name: 'Empezar con ADÁN' }).click()

  await expect(page).toHaveURL(/\/nivel1\/c-new$/)
  expect(api.callsTo('POST', '/onboarding/start')[0]?.body).toEqual({ company_name: 'Nueva SAS', stage: 'existing' })
})

test('quien ya empezó retoma desde su último paso', async ({ page }) => {
  const api = new FakeApi().withCompany()
  api.loggedIn = true
  await api.install(page)
  await page.goto('/bienvenida')
  await expect(page).toHaveURL(/\/nivel1\/c1$/)
})

test('desde el tablero se crea otra empresa', async ({ page }) => {
  const api = new FakeApi().withCompany()
  api.loggedIn = true
  await api.install(page)
  await page.goto('/dashboard')
  await expect(page.getByTestId('identity')).toContainText('Responsable de Empresa')
  await page.getByRole('button', { name: '+ Nueva Empresa' }).click()
  const dialog = page.getByRole('dialog', { name: 'Crear Empresa' })
  await dialog.getByLabel('Nombre de la empresa').fill('Otra SAS')
  await dialog.getByLabel('Industria').fill('Software')
  await dialog.getByRole('button', { name: 'Crear' }).click()
  await expect(page).toHaveURL(/\/nivel1\/c-new$/)
  expect(api.callsTo('POST', '/companies/')[0]?.body).toMatchObject({ name: 'Otra SAS', industry: 'Software' })
})

test('la ruta muestra los 7 Niveles con sus Cards', async ({ page }) => {
  const api = new FakeApi().withCompany()
  api.loggedIn = true
  await api.install(page)
  await page.goto('/dashboard')
  await page.getByRole('link', { name: 'Ruta' }).click()
  await expect(page).toHaveURL(/\/ruta\/c1$/)
  await expect(page.getByTestId('level-step')).toHaveCount(7)
  await expect(page.getByText('Descubrimiento del Dolor')).toBeVisible()
  await page.getByRole('link', { name: 'Continuar el Nivel 1 →' }).click()
  await expect(page).toHaveURL(/\/nivel1\/c1$/)
})

test('la lista de empresas lleva a cada Nivel 1', async ({ page }) => {
  const api = new FakeApi().withCompany()
  api.loggedIn = true
  await api.install(page)
  await page.goto('/dashboard')
  await page.getByRole('button', { name: /Panadería Digital/ }).click()
  await expect(page).toHaveURL(/\/nivel1\/c1$/)
  await expect(page.getByRole('navigation', { name: 'Ubicación' })).toContainText('Panadería Digital')
})
