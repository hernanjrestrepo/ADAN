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
  await page.getByLabel('Mensaje para ADÁN').fill('Las panaderías pierden pan cada día')
  await page.getByRole('button', { name: 'Enviar' }).click()
  await expect(page.getByText('¿Cuánto pan se pierde al día?')).toBeVisible()
  expect(api.callsTo('POST', '/nivel1/c1/chat')[0]?.body).toMatchObject({ message: 'Las panaderías pierden pan cada día' })
})

test('el avance del guion se ve en una línea y la evidencia se registra sola', async ({ page }) => {
  await openNivel1(page)
  await page.setViewportSize({ width: 1400, height: 900 })
  await expect(page.getByText('0/7')).toBeVisible()
  await page.getByLabel('Mensaje para ADÁN').fill('Las panaderías botan pan cada día')
  await page.getByLabel('Mensaje para ADÁN').press('Enter')
  await expect(page.getByText('¿Cuánto pan se pierde al día?')).toBeVisible()
  await expect(page.getByText('2/7')).toBeVisible()
  // Sin paneles ni botones de confirmar evidencia
  await expect(page.getByRole('button', { name: 'Registrar como evidencia' })).toHaveCount(0)
})

test('si responde el modelo de respaldo, ADÁN lo dice y el guion no avanza', async ({ page }) => {
  const api = await openNivel1(page)
  api.chatDegraded = 'Claude no disponible (AuthenticationError)'
  await page.getByLabel('Mensaje para ADÁN').fill('Hola')
  await page.getByRole('button', { name: 'Enviar' }).click()
  await expect(page.getByTestId('degraded-note')).toContainText('AuthenticationError')
})

test('el Board Room pasa dentro de la misma conversación y se le responde ahí, a todos o a uno', async ({ page }) => {
  const api = await openNivel1(page)
  await page.getByRole('button', { name: /Board Room/ }).click()
  await expect.poll(() => api.callsTo('POST', '/nivel1/c1/board-room').length).toBe(1)
  await expect(page.getByText('🏛️ Board Room').first()).toBeVisible()
  await page.getByLabel('Mensaje para ADÁN').fill('Ya tengo 20 preventas pagadas')
  await page.getByRole('button', { name: 'Enviar' }).click()
  await expect.poll(() => api.callsTo('POST', '/nivel1/c1/board-room/dialogo')[0]?.body)
    .toEqual({ message: 'Ya tengo 20 preventas pagadas', agent: null })
  await page.getByLabel('Mensaje para ADÁN').fill('Camila, ¿qué cifra te falta?')
  await page.getByRole('button', { name: 'Enviar' }).click()
  await expect.poll(() => api.callsTo('POST', '/nivel1/c1/board-room/dialogo')[1]?.body)
    .toEqual({ message: 'Camila, ¿qué cifra te falta?', agent: 'CFO' })
  await page.getByRole('button', { name: /Volver a la oficina/ }).click()
  await expect(page.getByText('🏢 Oficina')).toBeVisible()
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
  api.overrides.set('POST /nivel1/c1/board-room', [429, { detail: 'Demasiadas solicitudes al modelo; espera un momento' }])
  page.on('dialog', () => { throw new Error('No debe abrirse un diálogo del navegador') })
  await page.getByRole('button', { name: /Board Room/ }).click()
  await expect(page.getByRole('alert')).toContainText('Demasiadas solicitudes al modelo')
})

test('el cliente carga su documentación y ADÁN cuenta lo que aprendió', async ({ page }) => {
  const api = await openNivel1(page)
  await expect(page.getByTestId('upload-invite')).toBeVisible()
  await page.getByTestId('upload-input').setInputFiles({ name: 'plan.pdf', mimeType: 'application/pdf', buffer: Buffer.from('%PDF-1.4 plan') })
  await expect(page.getByText('Lo más débil: no hay ventas reales.')).toBeVisible()
  expect(api.callsTo('POST', '/nivel1/c1/documents/upload')).toHaveLength(1)
  expect(api.callsTo('POST', '/nivel1/c1/documents/upload')[0]?.headers['x-requested-with']).toBe('adan')
})

test('La Arena pasa dentro de la conversación: los inversionistas preguntan y se les responde ahí', async ({ page }) => {
  const api = await openNivel1(page)
  await page.getByRole('button', { name: /La Arena/ }).click()
  await expect.poll(() => api.callsTo('POST', '/nivel1/c1/arena/start')[0]?.body).toEqual({ pitch: '' })
  await page.getByLabel('Mensaje para ADÁN').fill('Ya vendí 30 suscripciones')
  await page.getByRole('button', { name: 'Enviar' }).click()
  await expect.poll(() => (api.callsTo('POST', '/nivel1/c1/arena/a1/answer')[0]?.body as { answers: Record<string, string> } | undefined)?.answers.angel)
    .toBe('Ya vendí 30 suscripciones')
})
