import { expect, test } from '@playwright/test'
import { FakeApi } from './fakeApi'

test('sin empresas se ofrece crear la primera y se entra a su Nivel 1', async ({ page }) => {
  const api = new FakeApi()
  api.loggedIn = true
  await api.install(page)
  await page.goto('/dashboard')
  await expect(page.getByText('No hay empresas todavía')).toBeVisible()

  await page.getByRole('button', { name: 'Crear mi primera empresa' }).click()
  const dialog = page.getByRole('dialog', { name: 'Crear Empresa' })
  await dialog.getByLabel('Nombre de la empresa').fill('Nueva SAS')
  await dialog.getByLabel('Industria').fill('Software')
  await dialog.getByRole('button', { name: 'Crear' }).click()

  await expect(page).toHaveURL(/\/nivel1\/c-new$/)
  expect(api.callsTo('POST', '/companies/')[0]?.body).toMatchObject({ name: 'Nueva SAS', industry: 'Software' })
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
