import { expect, test, type Page } from '@playwright/test'
import { FakeApi } from './fakeApi'

async function openGemelo(page: Page, tab?: 'Decisiones' | 'Timeline') {
  const api = new FakeApi().withCompany()
  api.loggedIn = true
  await api.install(page)
  await page.goto('/gemelo/c1')
  await expect(page.getByRole('heading', { name: 'Panadería Digital' })).toBeVisible()
  if (tab) await page.getByRole('tab', { name: tab }).click()
  return api
}

test('el resumen muestra la identidad del Gemelo y sus entidades', async ({ page }) => {
  await openGemelo(page)
  const identity = page.getByTestId('twin-identity')
  await expect(identity).toContainText('Nacimiento')
  await expect(identity).toContainText('20%')
  await expect(page.getByText('Identidad y Gobernanza')).toBeVisible()
  await expect(page.getByText('Competidores')).toBeVisible()
  await expect(page.getByText('1 por decidir')).toBeVisible()
})

test('una decisión se presenta, se aprueba la recomendación y se ejecuta', async ({ page }) => {
  const api = await openGemelo(page, 'Decisiones')
  const card = page.getByTestId('decision-card')
  await expect(card).toContainText('Propuesta')
  await expect(card).toContainText('Disenso del Board')
  await expect(page.getByTestId('prior-decisions')).toContainText('Cerrar Nivel 0')
  await expect(card.getByText('Recomendada')).toBeVisible()

  await page.getByRole('button', { name: 'Ver con razonamiento' }).click()
  await expect(card).toContainText('Presentada')
  await expect(card).toContainText('CTO, CMO y Producto ven demanda clara')

  await page.getByRole('button', { name: 'Aprobar la recomendación' }).click()
  await expect(card).toContainText('Aprobada')
  expect(api.callsTo('POST', '/twin/c1/decisions/dec1/decide')[0]?.body).toEqual({ action: 'approve', chosen_option: 'PROCEED' })

  await page.getByLabel('Decisión de Negocio que origina (opcional)').fill('Abrir punto en Medellín')
  await page.getByRole('button', { name: 'Marcar como ejecutada' }).click()
  await expect(card).toContainText('Ejecutada')
  await expect(card).toContainText('Originó la Decisión de Negocio «Abrir punto en Medellín»')
})

test('decidir distinto exige riesgos y responsabilidad, y queda registrado', async ({ page }) => {
  const api = await openGemelo(page, 'Decisiones')
  await page.getByRole('radio', { name: 'Pivotar' }).check()
  await expect(page.getByTestId('divergence-form')).toBeVisible()
  const approve = page.getByRole('button', { name: 'Aprobar mi opción' })
  await expect(approve).toBeDisabled()

  await page.getByLabel('Riesgos que asumes (uno por línea)').fill('Retrasar el lanzamiento\nPerder la temporada')
  await expect(approve).toBeDisabled()
  await page.getByLabel('Responsabilidad que asumes').fill('Elijo pivotar aunque el Board recomendó avanzar.')
  await approve.click()

  const divergence = page.getByTestId('divergence')
  await expect(divergence).toContainText('Decidiste distinto a lo recomendado')
  await expect(divergence).toContainText('Perder la temporada')
  await expect(divergence).toContainText('Elijo pivotar aunque el Board recomendó avanzar.')
  expect(api.callsTo('POST', '/twin/c1/decisions/dec1/decide')[0]?.body).toEqual({
    action: 'approve', chosen_option: 'PIVOT', risks_assumed: ['Retrasar el lanzamiento', 'Perder la temporada'],
    responsibility_statement: 'Elijo pivotar aunque el Board recomendó avanzar.',
  })
})

test('el Timeline muestra la historia del Gemelo y se actualiza con cada decisión', async ({ page }) => {
  await openGemelo(page, 'Timeline')
  const events = page.getByTestId('timeline-event')
  await expect(events).toHaveCount(2)
  await expect(events.first()).toContainText('Se registró Marca «Pan de Ana»')
  await expect(events.last()).toContainText('Nació el Gemelo Digital')

  await page.getByRole('tab', { name: 'Decisiones' }).click()
  await page.getByRole('button', { name: 'Rechazar' }).click()
  await expect(page.getByTestId('decision-card')).toContainText('Rechazada')
  await page.getByRole('tab', { name: 'Timeline' }).click()
  await expect(events.first()).toContainText('Decisión «Board Room: PROCEED»')
  await expect(events.first()).toContainText('rechazada')
})

test('desde el tablero se llega al Gemelo Digital', async ({ page }) => {
  const api = new FakeApi().withCompany()
  api.loggedIn = true
  await api.install(page)
  await page.goto('/dashboard')
  await page.getByRole('link', { name: 'Gemelo Digital →' }).click()
  await expect(page).toHaveURL(/\/gemelo\/c1$/)
})
