import { expect, test } from '@playwright/test'
import { FakeApi } from './fakeApi'

test('se contrata un agente, se le encarga una tarea y el cliente aprueba la entrega', async ({ page }) => {
  const api = new FakeApi().withCompany()
  api.loggedIn = true
  await api.install(page)
  await page.goto('/dashboard')
  await page.getByRole('link', { name: 'Agentes' }).click()
  await expect(page).toHaveURL(/\/agentes\/c1$/)
  await expect(page.getByText('Todavía no has contratado agentes')).toBeVisible()

  const card = page.getByTestId('offering').first()
  await expect(card).toContainText('Precio por definir (WO-100)')
  await card.getByLabel('Período Redactor Comercial').selectOption('week')
  await card.getByLabel('Cantidad Redactor Comercial').fill('2')
  await expect(card).toContainText('80 h de trabajo efectivo')
  await card.getByRole('button', { name: 'Contratar' }).click()
  expect(api.callsTo('POST', '/hire/c1/contracts')[0]?.body).toEqual({ offering_code: 'redactor', period: 'week', units: 2 })

  const contract = page.getByTestId('contract')
  await expect(contract).toContainText('0.00 de 80 h')
  await contract.getByLabel('Nueva tarea').fill('Escribir la propuesta de valor de Xmart Travel')
  await contract.getByRole('button', { name: 'Encargar' }).click()
  await contract.getByRole('button', { name: 'Poner a trabajar' }).click()
  await expect(page.getByTestId('agent-task')).toContainText('viajes corporativos sin fricción')
  await page.getByRole('button', { name: 'Aprobar' }).click()
  await expect(page.getByTestId('agent-task')).toContainText('Aprobada')
})
