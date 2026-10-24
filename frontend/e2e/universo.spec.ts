import { expect, test } from '@playwright/test'
import { FakeApi } from './fakeApi'

test('el Universo se recorre sin cuenta: se elige la empresa, se encarga evidencia y se ve el entregable', async ({ page }) => {
  await new FakeApi().install(page)
  await page.goto('/universo')
  await expect(page.getByRole('heading', { name: /Tu equipo directivo de IA/ })).toBeVisible()
  await expect(page.getByAltText('Paradixe, AI Operating Company')).toBeVisible()

  await page.getByRole('button', { name: /Clínica veterinaria/ }).click()
  await page.getByPlaceholder('Huellitas 24/7').fill('Vet Caribe')
  await page.getByRole('button', { name: 'Entrar a la oficina →' }).click()

  const mission = page.getByRole('complementary', { name: 'Misión del Nivel 1' })
  await expect(mission.getByRole('heading', { name: 'El Dolor' })).toBeVisible()
  await expect(page.getByText('Vet Caribe').first()).toBeVisible()

  // Encargar una tarea del Gate: el agente sale a trabajar y queda en la bitácora
  await mission.getByRole('button', { name: 'Encargar' }).first().click()
  await expect(mission.getByText(/va en camino|está trabajando/)).toBeVisible()

  // El entregable muestra lo que falta: no se inventa evidencia
  await mission.getByRole('button', { name: /Diagnóstico del Dolor/ }).click()
  const report = page.getByRole('dialog', { name: 'Diagnóstico del Dolor' })
  await expect(report.getByText('Ejemplo ilustrativo')).toBeVisible()
  await expect(report.getByText(/Pendiente:/).first()).toBeVisible()
})

test('los 7 Niveles y el ecosistema se pueden consultar desde la barra', async ({ page }) => {
  await new FakeApi().install(page)
  await page.goto('/universo')
  await page.getByRole('button', { name: 'Entrar a la oficina →' }).click()
  await page.getByRole('button', { name: '🗺️ Ruta' }).click()
  await expect(page.getByRole('heading', { name: 'La ruta de 7 Niveles' })).toBeVisible()
  for (const name of ['El Dolor', 'Propuesta de Valor', 'Plan de Negocios', 'MVP', 'Validación Simulada', 'Lanzamiento', 'Escalamiento']) {
    await expect(page.getByRole('heading', { name: new RegExp(`^${name}`) })).toBeVisible()
  }
  await page.getByRole('button', { name: '🌐 Ecosistema' }).click()
  await expect(page.getByText('Motor interno que construye el MVP del Nivel 4.')).toBeVisible()
})
