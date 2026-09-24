import { expect, test } from "@playwright/test";

const API_BASE_URL = process.env.E2E_API_BASE_URL ?? "http://localhost:8020";

test("lanzar el agente de diagnostico y ver el resultado real", async ({ page }) => {
  const email = `e2e-agents-${Date.now()}@adan-demo.io`;
  const password = "e2e-password-123";

  await page.request.post(`${API_BASE_URL}/auth/register`, {
    data: { email, password, display_name: "E2E Agents User" },
  });

  await page.goto("/login");
  await page.getByLabel("Correo").fill(email);
  await page.getByLabel("Contraseña").fill(password);
  await page.getByRole("button", { name: /entrar/i }).click();
  await expect(page).toHaveURL(/\/dashboard/);

  await page.getByRole("link", { name: /agente de diagn/i }).click();
  await expect(page).toHaveURL(/\/agents/);

  await page.getByLabel(/cuéntale a adán/i).fill("No se si mis clientes pagarian por esto.");
  await page.getByRole("button", { name: /diagnosticar/i }).click();

  // Se escopea al panel de "ejecucion en curso" (no al historial, que puede tener
  // ejecuciones previas ya en estado completed de corridas anteriores).
  const currentPanel = page.getByTestId("current-execution");
  await expect(currentPanel.getByText(/^completed$/)).toBeVisible({ timeout: 30_000 });
  await expect(currentPanel.locator("pre")).not.toBeEmpty();
});
