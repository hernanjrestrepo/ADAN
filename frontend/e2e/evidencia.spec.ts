import { expect, test } from '@playwright/test'
import { FakeApi } from './fakeApi'

async function openEvidence(page: import('@playwright/test').Page, api: FakeApi) {
  api.loggedIn = true
  await api.install(page)
  await page.goto('/nivel1/c1')
  await page.getByRole('tab', { name: 'Evidencia' }).click()
}

test('la evidencia se registra por tipo y el Gate dice qué falta hasta que alcanza', async ({ page }) => {
  const api = new FakeApi().withCompany()
  await openEvidence(page, api)
  const progress = page.getByTestId('gate-progress')
  await expect(progress).toContainText('Todavía falta evidencia')
  await expect(progress).toContainText('dato verificable externamente')

  // Un dato externo sin fuente no se acepta: el formulario exige la fuente
  await page.getByLabel('¿Qué afirmas?').fill('El 40 % de las panaderías bota pan cada día')
  await expect(page.getByLabel('Fuente (obligatoria)')).toHaveAttribute('required', '')
  await page.getByLabel('Fuente (obligatoria)').fill('https://example.org/estudio')
  await page.getByRole('button', { name: 'Registrar evidencia' }).click()
  await expect(page.getByTestId('evidence-item')).toHaveCount(1)
  expect(api.callsTo('POST', '/scoring/c1/evidence')[0]?.body).toMatchObject({ kind: 'external', polarity: 'supports' })

  await page.getByRole('radio', { name: /Testimonio/ }).check()
  await expect(page.getByLabel('Fuente (opcional)')).toBeVisible()
  await page.getByLabel('¿Qué afirmas?').fill('Tres panaderos me confirmaron que botan pan a diario')
  await page.getByRole('button', { name: 'Registrar evidencia' }).click()
  await expect(page.getByTestId('evidence-item')).toHaveCount(2)
  await expect(progress).toContainText('La evidencia ya alcanza')
})

test('sin evidencia suficiente, avanzar es decisión del cliente y se documenta', async ({ page }) => {
  const api = new FakeApi().withCompany()
  api.gateApproved = false
  api.loggedIn = true
  await api.install(page)
  await page.goto('/nivel1/c1')
  await page.getByRole('button', { name: /Gate Review/ }).click()
  const result = page.getByTestId('gate-result')
  await expect(result).toContainText('Todavía falta evidencia')
  await expect(result).toContainText('dato verificable externamente')
  await expect(page.getByRole('button', { name: 'Aprobar cierre del Nivel 1' })).toHaveCount(0)

  await page.getByRole('button', { name: 'Avanzar bajo mi responsabilidad' }).click()
  await expect(result).toContainText('ADÁN recomienda seguir trabajando el Nivel')
  await expect(page.getByRole('link', { name: 'Ir a Decisiones →' })).toHaveAttribute('href', '/gemelo/c1?tab=decisions')
})

test('los 8 Scores se muestran con su disponibilidad', async ({ page }) => {
  const api = new FakeApi().withCompany()
  api.loggedIn = true
  await api.install(page)
  await page.goto('/nivel1/c1')
  await page.getByRole('tab', { name: 'Scores' }).click()
  await expect(page.getByTestId('score-card')).toHaveCount(8)
  await expect(page.getByText('Nace en el Nivel 6')).toBeVisible()
  await expect(page.getByText('Se abre en el Nivel 2')).toBeVisible()
})

test('cada fuente se verifica y CSI propone datos que el cliente confirma', async ({ page }) => {
  const api = new FakeApi().withCompany()
  api.csiConnected = true
  await openEvidence(page, api)
  await page.getByLabel('¿Qué afirmas?').fill('El 40 % de las panaderías bota pan cada día')
  await page.getByLabel('Fuente (obligatoria)').fill('https://example.org/estudio')
  await page.getByRole('button', { name: 'Registrar evidencia' }).click()
  await expect(page.getByTestId('verification').first()).toContainText('Fuente verificada')

  await page.getByRole('button', { name: 'Buscar evidencia en CSI' }).click()
  await expect(page.getByText('Propuesta por CSI: todavía no cuenta para tu Score.')).toBeVisible()
  await expect(page.getByTestId('gate-progress')).toContainText('Dato verificable: 1 a favor')
  await page.getByRole('button', { name: 'Confirmar' }).click()
  await expect(page.getByTestId('gate-progress')).toContainText('Dato verificable: 2 a favor')
})

test('sin CSI conectado se dice claramente', async ({ page }) => {
  await openEvidence(page, new FakeApi().withCompany())
  await expect(page.getByTestId('csi')).toContainText('CSI todavía no está conectado')
  await expect(page.getByRole('button', { name: 'Buscar evidencia en CSI' })).toBeDisabled()
})
