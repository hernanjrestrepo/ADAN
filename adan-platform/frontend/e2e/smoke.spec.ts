import { expect, test } from "@playwright/test";

const API_BASE_URL = process.env.E2E_API_BASE_URL ?? "http://localhost:8020";

test("registro real via API, login via UI, dashboard visible", async ({ page }) => {
  const email = `e2e-${Date.now()}@adan-demo.io`;
  const password = "e2e-password-123";

  // Registro real contra la API (evidencia objetiva, no mock)
  const registerResp = await page.request.post(`${API_BASE_URL}/auth/register`, {
    data: { email, password, display_name: "E2E Smoke User" },
  });
  expect(registerResp.ok()).toBeTruthy();

  // Login via la UI real
  await page.goto("/login");
  await page.getByLabel("Correo").fill(email);
  await page.getByLabel("Contraseña").fill(password);
  await page.getByRole("button", { name: /entrar/i }).click();

  await expect(page).toHaveURL(/\/dashboard/);
  await expect(page.getByText("ADÁN — Workspace")).toBeVisible();
  await expect(page.getByText(/^ok ·/)).toBeVisible({ timeout: 10_000 });
});

test("ruta privada redirige a login sin token", async ({ page }) => {
  await page.goto("/dashboard");
  await expect(page).toHaveURL(/\/login/);
});
