# WO-092 — Frontend TypeScript y base de UX

**Fecha:** 2026-09-24 · **Ejecutor:** Claude Code · **Autoriza:** Hernán ("haz todo lo que tengas que hacer", 2026-09-24)
**Formato:** EPWO-050 · **Checklist:** EPWO-051
**Estado:** ✅ Cerrada al fusionar su PR en `main`.

---

## 1. Fase -1

| Verificación | Resultado |
|---|---|
| Canon | `AD-ROOT-0001 §3` fija TypeScript, y su nota de consistencia registraba que Build C estaba en JSX. `main` estaba en `c1053a0` (WO-097). |
| Reutilización | Del frontend de Build A (`WO-096_MAPA_REUTILIZACION.md`) se tomó la configuración: `tsconfig` estricto, ESLint con typescript-eslint y Playwright. Sus pantallas no se trajeron: son de otro dominio (el explorador del grafo y los agentes de WO-003). |
| Inventario | 940 líneas de JSX, 5 pantallas, sin pruebas, sin lint. `npm audit` tenía 4 vulnerabilidades, que WO-097 había dejado para esta WO. |
| Alcance | La ficha de WO-092 en `PLAN_WO_ADAN_100.md`. La categoría **AD-UX** del blueprint no está escrita (es la Fase 2 de WO-000; ver `BLUEPRINT_ADAN_v1.1.md` §9). Por eso esta WO construye la base técnica de UX (sistema de componentes, marco de navegación y workspace) y no inventa pantallas sin especificación. |

## 2. Versiones

| Paquete | Antes | Ahora | Por qué |
|---|---|---|---|
| react / react-dom | 18.3 | **19.3** | react-router 8 exige React 19.2.7 o superior |
| react-router(-dom) | 6.30 | **react-router 8.4** | Cierra las vulnerabilidades de react-router 6 (redirección abierta) |
| vite | 5.4 | **8.3** | Cierra la vulnerabilidad de esbuild en el servidor de desarrollo |
| @vitejs/plugin-react | 4.3 | 6.1 | Compatible con vite 8 |
| react-markdown | 9 | 10.1 | Soporta React 19 |
| typescript | — | **6.0.3** | Se usa 6.0 y no 7.0, el compilador nativo: typescript-eslint 8 solo soporta TypeScript por debajo de 6.1 |
| eslint | — | 10.11, con typescript-eslint 8.70 y react-hooks 7 | Lint en el proyecto |
| @playwright/test | — | 1.63 | Pruebas de la interfaz |
| tailwindcss | 3.4 | 3.4.19 | La versión 4 reescribe la configuración y no tiene vulnerabilidades pendientes; queda fuera del alcance |
| Node (Docker) | 20 | **22** | Lo exige react-router 8 |

## 3. Qué se hizo

- **TypeScript estricto** (`strict`, `noUncheckedIndexedAccess`, `verbatimModuleSyntax`) en todo `src/`. No queda ningún archivo `.jsx` ni `.js`.
- **Tipos del API** (`src/types.ts`), escritos contra los esquemas del backend. **Cliente tipado** (`src/lib/api.ts`), con `ApiError` que conserva el código HTTP; los errores de validación (422) se muestran legibles.
- **Sistema de componentes** (`src/components/ui/`): `Button` (4 variantes), `Card`, `Field`/`TextAreaField` (con `label` asociado), `Alert`, `Badge`, `Tabs` (con roles ARIA), `LoadingState` y `EmptyState`.
- **Marco de navegación y workspace:**
  - `AppShell`: marca, migas de pan (Mis Empresas / empresa / Nivel), estado del Nivel, usuario, Salir y aviso de IA fijo en el pie.
  - `AuthLayout` para login y registro.
  - `AuthProvider`/`useAuth` en lugar de pasar el usuario por props.
  - Rutas privadas y públicas.
- **Nivel 1 dividido en paneles:** `ChatPanel`, `BoardRoomPanel`, `DiagnosisPanel` y `ScoresPanel`. El contenedor maneja el estado y cancela la carga si el usuario cambia de empresa.
- **Los errores se muestran en la página.** Se quitaron todos los `alert()` del navegador.
- **Los mensajes de ADÁN se muestran como markdown.** Antes aparecían los `**` en crudo, como se ve en la evidencia.
- **Accesibilidad básica:** `label` en cada campo, `role="dialog"` en el diálogo de empresa, `role="alert"`, `aria-live` en el chat, `progressbar` en los scores y `aria-current` en las migas de pan.
- **ESLint** (`eslint.config.js`, config plana) y **Playwright** (`playwright.config.ts`) con un API simulado (`e2e/fakeApi.ts`): las pruebas de la interfaz no necesitan backend ni LLM, así que pueden correr en CI (WO-093).
- `Dockerfile` con Node 22 y `npm ci`; `.dockerignore`; `package-lock.json` regenerado.

## 4. Evidencia

| Evidencia | Resultado | Método |
|---|---|---|
| Tipos | Sin errores (código y configuración) | `npm run typecheck` |
| Lint | Sin errores ni avisos | `npm run lint` (`--max-warnings 0`) |
| Build | Correcto: 398 kB de JS (124 kB con gzip). Antes eran 306 kB; el aumento viene de React 19 y react-router 8. | `npm run build` |
| Vulnerabilidades | **0** (antes 4: 3 moderadas y 1 alta) | `npm audit` |
| Pruebas de interfaz | **10 passed**:<br>• redirección sin sesión<br>• errores 422 legibles<br>• registro, sesión y salida<br>• cabecera anti-CSRF en todas las peticiones<br>• crear la primera empresa<br>• lista de empresas<br>• chat<br>• Board Room con abstenciones y disenso<br>• cierre del Nivel con aprobación del cliente<br>• error 429 mostrado sin diálogos del navegador | `npm run test:e2e` (Chromium) |
| De punta a punta real | Registro → empresa → chat con respuesta del LLM (20 s) → Board Room (4 agentes, "Sin consenso") → salir. Total: 95 s. | Playwright contra el backend en `:8060` + Ollama (`qwen2.5:0.5b`). Capturas en `docs/wo/evidencia/WO-092/` |
| Backend | Sin cambios | — |

## 5. Hallazgo para WO-099

Las capturas del Board Room muestran por qué con `qwen2.5:0.5b` todos los agentes se abstienen. El modelo intenta responder en JSON, pero:
- el límite de 512 tokens lo corta;
- a veces escribe un objeto sin comillas;
- a veces anida el voto.

Se agregó a WO-099: salidas estructuradas (esquema JSON de Ollama y de Anthropic) y más tokens para los votos. La interfaz ya lo muestra con honestidad: abstenciones y "Sin consenso".

## 6. Deuda y riesgos

- **AD-UX-01/02/04 sin especificación:** cuando el blueprint las defina, se construyen sobre este sistema de componentes.
- **Tailwind 3:** migrar a la versión 4 es un cambio aparte, sin urgencia de seguridad.
- **Tamaño del bundle** (398 kB): dividir por rutas cuando haya más páginas (Niveles 2–7).
- **Pruebas con el API simulado:** validan la interfaz, no la integración. La prueba de punta a punta real se hizo a mano en esta WO; automatizarla con servicios en CI es WO-093.

## 7. Checklist EPWO-051

- [x] Evidencia objetiva ejecutada (§4).
- [x] Pruebas que pasan: 10 E2E, más tipos, lint y build.
- [x] Documentación (README, Canon §3, plan y auditoría) y deuda registradas.
- [x] `git status` limpio al hacer el commit.
- [x] Reporte en `docs/wo/`.
- [x] PR fusionado a `main`.
