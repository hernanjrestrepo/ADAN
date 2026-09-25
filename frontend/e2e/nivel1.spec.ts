import { expect, test } from '@playwright/test'
import { BOARD_PROCEED, FakeApi } from './fakeApi'

async function openNivel1(page: import('@playwright/test').Page) {
  const api = new FakeApi().withCompany()
  api.loggedIn = true
  await api.install(page)
  await page.goto('/nivel1/c1')
  await expect(page.getByRole('tab', { name: 'Conversación' })).toHaveAttribute('aria-selected', 'true')
  return api
}

test('la conversación envía el mensaje y muestra la respuesta', async ({ page }) => {
  const api = await openNivel1(page)
  await page.getByLabel('Mensaje para ADÁN').fill('Las panaderías pierden pan cada día')
  await page.getByRole('button', { name: 'Enviar' }).click()
  await expect(page.getByText('¿Cuánto pan se pierde al día?')).toBeVisible()
  expect(api.callsTo('POST', '/nivel1/c1/chat')[0]?.body).toMatchObject({ message: 'Las panaderías pierden pan cada día' })
})

test('el Board Room muestra la propuesta, las abstenciones y el disenso', async ({ page }) => {
  await openNivel1(page)
  await page.getByRole('button', { name: /Ejecutar Board Room/ }).click()
  await expect(page.getByRole('tab', { name: 'Board Room' })).toHaveAttribute('aria-selected', 'true')
  await expect(page.getByText('Sin consenso')).toBeVisible()
  await expect(page.getByTestId('agent-vote')).toHaveCount(2)
  await expect(page.getByText('Abstención')).toBeVisible()
  await expect(page.getByText('CFO: STOP — El margen es bajo')).toBeVisible()
  await expect(page.getByText('la decisión final es tuya')).toBeVisible()
})

test('el Nivel se cierra solo cuando el cliente lo aprueba', async ({ page }) => {
  const api = await openNivel1(page)
  await page.getByRole('button', { name: /Gate Review/ }).click()
  await expect(page.getByText('Falta tu aprobación para cerrar el Nivel 1.')).toBeVisible()
  await page.getByRole('button', { name: 'Aprobar cierre del Nivel 1' }).click()

  await expect(page.getByText('Aprobaste el cierre del Nivel 1. El Nivel 2 quedó activo.')).toBeVisible()
  await expect(page.getByText('Completado')).toBeVisible()
  expect(api.callsTo('POST', '/nivel1/c1/decisions/d1')[0]?.body).toEqual({ action: 'approve' })
})

test('el cliente participa en el Board: pregunta, posición, síntesis y evidencia pedida', async ({ page }) => {
  const api = await openNivel1(page)
  api.overrides.set('POST /nivel1/c1/board-room', [200, BOARD_PROCEED])
  await page.getByRole('tab', { name: 'Board Room' }).click()
  await page.getByLabel('Tu pregunta para el Board').fill('¿Empiezo en Medellín?')
  await page.getByLabel('Tu posición').fill('Quiero lanzar ya')
  await page.getByRole('button', { name: 'Ejecutar Board Room' }).click()

  await expect(page.getByTestId('agent-vote')).toHaveCount(6)
  await expect(page.getByTestId('board-opening')).toContainText('Tu posición: Quiero lanzar ya')
  await expect(page.getByTestId('board-synthesis')).toContainText('El Board recomienda avanzar')
  await expect(page.getByText('Ventas de pan de los últimos 3 meses')).toBeVisible()
  expect(api.callsTo('POST', '/nivel1/c1/board-room')[0]?.body)
    .toEqual({ question: '¿Empiezo en Medellín?', position: 'Quiero lanzar ya' })
})

test('un error del backend se muestra en la página, sin diálogos del navegador', async ({ page }) => {
  const api = await openNivel1(page)
  api.overrides.set('POST /nivel1/c1/board-room', [429, { detail: 'Demasiadas solicitudes al modelo; espera un momento' }])
  page.on('dialog', () => { throw new Error('No debe abrirse un diálogo del navegador') })
  await page.getByRole('button', { name: /Ejecutar Board Room/ }).click()
  await expect(page.getByRole('alert')).toContainText('Demasiadas solicitudes al modelo')
})
