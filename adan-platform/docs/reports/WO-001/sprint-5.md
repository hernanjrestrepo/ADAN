# WO-001 Sprint 5 — Shell frontend

**Célula:** B · **Fecha:** 2026-07-17

## Resumen ejecutivo

React 18 + Vite + Tailwind con design tokens propios (paleta `adan-*`, coherente con AD-001 §14 "confianza calmada"). Flujo de login real contra la API (`/auth/login`, form-urlencoded, JWT persistido en `localStorage`), routing con ruta privada (`PrivateRoute`), Dashboard que consulta `/health` en vivo. Cliente API tipado manual (`src/api/client.ts`) — se documenta como reemplazable por generación automática desde OpenAPI cuando el contrato de agentes (WO-002) estabilice.

## Archivos creados

`index.html`, `vite.config.ts`, `tsconfig.json`, `tailwind.config.js`, `postcss.config.js`, `.eslintrc.cjs`, `playwright.config.ts`, `src/index.css`, `src/main.tsx`, `src/App.tsx`, `src/vite-env.d.ts`, `src/api/client.ts`, `src/pages/Login.tsx`, `src/pages/Dashboard.tsx`.

## Archivos modificados

Ninguno (todo nuevo en este Sprint).

## Bugs encontrados

Ninguno bloqueante — `npm install` reportó 2 vulnerabilidades de dependencias transitivas de ESLint 8.x (deprecado mayor), registradas como deuda técnica, no bloquean el Sprint.

## Bugs corregidos

N/A.

## Evidencias objetivas

- `npm install`: 258 paquetes reales instalados.
- `npm run lint`: **sin errores** (0 warnings, `--max-warnings 0`).
- `npm run build`: **build real exitoso** — `tsc -b && vite build`, 37 módulos transformados, `dist/` generado (165KB JS, 6.9KB CSS).

## Tiempo real (Wall Clock)

~25 minutos.

## Estado del Sprint

COMPLETO — el smoke E2E completo (login real contra el backend, vía Docker Compose) se ejecuta en el Sprint 6 (baseline reproducible), una vez que `docker compose up` levanta ambos servicios juntos.
