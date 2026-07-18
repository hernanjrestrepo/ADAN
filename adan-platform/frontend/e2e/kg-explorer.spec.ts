import { expect, test } from "@playwright/test";

const API_BASE_URL = process.env.E2E_API_BASE_URL ?? "http://localhost:8020";

test("explorar el knowledge graph con datos reales", async ({ page }) => {
  const email = `e2e-kg-${Date.now()}@adan-demo.io`;
  const password = "e2e-password-123";

  const registerResp = await page.request.post(`${API_BASE_URL}/auth/register`, {
    data: { email, password, display_name: "E2E KG User" },
  });
  expect(registerResp.ok()).toBeTruthy();
  const { access_token } = await registerResp.json();

  // Datos reales via API antes de explorar: dos nodos conectados
  const n1 = await page.request.post(`${API_BASE_URL}/kg/nodes`, {
    headers: { Authorization: `Bearer ${access_token}` },
    data: { tipo: "hecho", nombre: `E2E hecho origen ${Date.now()}` },
  });
  const n2 = await page.request.post(`${API_BASE_URL}/kg/nodes`, {
    headers: { Authorization: `Bearer ${access_token}` },
    data: { tipo: "hecho", nombre: `E2E hecho conectado ${Date.now()}` },
  });
  const n1Body = await n1.json();
  const n2Body = await n2.json();
  await page.request.post(`${API_BASE_URL}/kg/edges`, {
    headers: { Authorization: `Bearer ${access_token}` },
    data: { origen_id: n1Body.id, destino_id: n2Body.id, tipo_relacion: "relacionado_con" },
  });
  // Indexar el nodo origen para que sea encontrable por busqueda semantica (Sprint 5:
  // crear un nodo via /kg/nodes NO lo indexa automaticamente - son pasos separados).
  await page.request.post(`${API_BASE_URL}/kg/memory`, {
    headers: { Authorization: `Bearer ${access_token}` },
    data: { contenido: n1Body.nombre, origen: "hecho", nodo_id: n1Body.id },
  });

  await page.goto("/login");
  await page.getByLabel("Correo").fill(email);
  await page.getByLabel("Contraseña").fill(password);
  await page.getByRole("button", { name: /entrar/i }).click();
  await expect(page).toHaveURL(/\/dashboard/);

  await page.getByRole("link", { name: /explorar knowledge graph/i }).click();
  await expect(page).toHaveURL(/\/kg/);

  await page.getByPlaceholder(/buscar en el conocimiento/i).fill(n1Body.nombre);
  await page.getByRole("button", { name: /^buscar$/i }).click();

  await expect(page.getByText(n1Body.nombre)).toBeVisible({ timeout: 15_000 });

  await page.getByRole("button", { name: /ver conexiones/i }).first().click();
  await expect(page.getByText(/nodos,.*relaciones/)).toBeVisible();
});
