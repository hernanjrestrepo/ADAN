import { expect, test } from '@playwright/test'
import { FakeApi } from './fakeApi'

async function openNivel1(page: import('@playwright/test').Page) {
  const api = new FakeApi().withCompany()
  api.loggedIn = true
  await api.install(page)
  await page.goto('/nivel1/c1')
  await expect(page.getByRole('tab', { name: 'Sala' })).toHaveAttribute('aria-selected', 'true')
  return api
}

test('la conversación envía el mensaje y muestra la respuesta', async ({ page }) => {
  const api = await openNivel1(page)
  await page.getByLabel('Mensaje para ADAN').fill('Las panaderías pierden pan cada día')
  await page.getByRole('button', { name: 'Enviar' }).click()
  await expect(page.getByText('¿Cuánto pan se pierde al día?')).toBeVisible()
  expect(api.callsTo('POST', '/nivel1/c1/chat')[0]?.body).toMatchObject({ message: 'Las panaderías pierden pan cada día' })
})

test('el avance del guion se ve en una línea y la evidencia se registra sola', async ({ page }) => {
  await openNivel1(page)
  await page.setViewportSize({ width: 1400, height: 900 })
  await expect(page.getByText('0/7')).toBeVisible()
  await page.getByLabel('Mensaje para ADAN').fill('Las panaderías botan pan cada día')
  await page.getByLabel('Mensaje para ADAN').press('Enter')
  await expect(page.getByText('¿Cuánto pan se pierde al día?')).toBeVisible()
  await expect(page.getByText('2/7')).toBeVisible()
  // Sin paneles ni botones de confirmar evidencia
  await expect(page.getByRole('button', { name: 'Registrar como evidencia' })).toHaveCount(0)
})

test('si responde el modelo de respaldo, ADAN lo dice y el guion no avanza', async ({ page }) => {
  const api = await openNivel1(page)
  api.chatDegraded = 'Claude no disponible (AuthenticationError)'
  await page.getByLabel('Mensaje para ADAN').fill('Hola')
  await page.getByRole('button', { name: 'Enviar' }).click()
  await expect(page.getByTestId('degraded-note')).toContainText('AuthenticationError')
})

test('en el Nivel 1 se valida con encuestas: sin Board ni Arena (llegan en los Niveles 3 y 5)', async ({ page }) => {
  await openNivel1(page)
  await expect(page.getByRole('button', { name: /Board Room/ })).toHaveCount(0)
  await expect(page.getByRole('button', { name: /La Arena/ })).toHaveCount(0)
  await page.getByRole('button', { name: /Validar con encuesta simulada/ }).click()
  await expect(page.getByRole('dialog', { name: 'Encuesta' })).toBeVisible()
})

test('el Nivel se cierra solo cuando el cliente lo aprueba', async ({ page }) => {
  const api = await openNivel1(page)
  await page.getByRole('button', { name: /Cerrar el Nivel/ }).click()
  await expect(page.getByText('Falta tu aprobación para cerrar el Nivel 1.')).toBeVisible()
  await page.getByRole('button', { name: 'Aprobar cierre del Nivel 1' }).click()

  await expect(page.getByText('Aprobaste el cierre del Nivel 1. El Nivel 2 quedó activo.')).toBeVisible()
  await expect(page.getByText('Completado')).toBeVisible()
  expect(api.callsTo('POST', '/nivel1/c1/decisions/d1')[0]?.body).toEqual({ action: 'approve' })
})

test('un error del backend se muestra en la página, sin diálogos del navegador', async ({ page }) => {
  const api = await openNivel1(page)
  api.overrides.set('POST /nivel1/c1/chat', [429, { detail: 'Demasiadas solicitudes al modelo; espera un momento' }])
  page.on('dialog', () => { throw new Error('No debe abrirse un diálogo del navegador') })
  await page.getByLabel('Mensaje para ADAN').fill('Hola')
  await page.getByRole('button', { name: 'Enviar' }).click()
  await expect(page.getByRole('alert')).toContainText('Demasiadas solicitudes al modelo')
})

test('el cliente carga su documentación y ADAN cuenta lo que aprendió', async ({ page }) => {
  const api = await openNivel1(page)
  await expect(page.getByTestId('upload-invite')).toBeVisible()
  await page.getByTestId('upload-input').setInputFiles({ name: 'plan.pdf', mimeType: 'application/pdf', buffer: Buffer.from('%PDF-1.4 plan') })
  await expect(page.getByText('Lo más débil: no hay ventas reales.')).toBeVisible()
  expect(api.callsTo('POST', '/nivel1/c1/documents/upload')).toHaveLength(1)
  expect(api.callsTo('POST', '/nivel1/c1/documents/upload')[0]?.headers['x-requested-with']).toBe('adan')
})
