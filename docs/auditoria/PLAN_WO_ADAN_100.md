# Plan de Work Orders para llevar ADÁN al 100 %

**Fecha:** 2026-09-24 (v2: incorpora `AD-DEC-0002`, decisiones de modelo de negocio y ecosistema)
**Estado:** aprobado por Hernán para ejecución ("sí a todas", 2026-09-24). Cada WO igual pasa su Fase -1 (Regla 7 de `AD-GOV-0001`) y el Gate de Inicio (EPWO-052) al abrirse.
**Deriva de:** `docs/auditoria/AUDITORIA_ADAN_2026-09.md` (avance estimado: ~22 %) y `AD-DEC-0002`.
**No es fuente de verdad** (Regla 6): la numeración vigente la fija `AD-ROOT-0001 §4`.

---

## 0. Qué significa "100 %"

**ADÁN Enterprise v1:**
- Los 7 Niveles funcionando de punta a punta según AD-FUNC-01 a 09.
- Agentes por tiempo para las empresas, Marketplace y Comunidad.
- Integración con el ecosistema: EVA para ventas y marketing, CSI e internamente Genexis.
- Todo sobre una plataforma certificada para producción (EPWO-054).

**Fuera de este plan:**
- **WO-100 Business Architecture.** Precios, billing, términos del Marketplace, cumplimiento de la red multinivel (Ley 1700 de 2013) y régimen del Programa AAA. Puede abrirse ya, con `AD-DEC-0002` como insumo.
- **WO-101 → WO-106, cadena SaaS.** Cuentas multiempresa, planes y administración.

## 1. Numeración (verificada contra el Canon)

| Rango | Uso |
|---|---|
| WO-090 | Consolidación (abierta: falta el tag de baseline y la revisión humana) |
| WO-091, 092, 093 | Ya definidas en el Canon: PostgreSQL, TypeScript, Producción |
| **WO-094** | **Hotfix de seguridad: ejecutada y fusionada (hernanjrestrepo/ADAN#1)** |
| WO-095 → WO-099 | Nuevas |
| WO-100 → WO-106 | Reservadas; no se tocan |
| WO-107 → WO-122 | Nuevas |

## 2. Ruta crítica

```
WO-094 ✅ ─► WO-095 ─► WO-096
                 │
     ┌───────────┴──────────────────────┐
     ▼                                  ▼
  WO-091 PostgreSQL ─► WO-097 Seguridad   WO-092 TypeScript + UX base
     └──────────────► WO-093 Producción ◄──────┘
                          │
                          ▼
  WO-098 Gemelo y Decisiones ─► WO-099 Motor cognitivo + IA (Ollama/Anthropic)
                          │
                          ▼
  WO-107 Evidencia y Scoring ─► WO-108 Onboarding + Nivel 1 ──► WO-109 Agentes por tiempo (en paralelo)
                          │
                          ▼
  WO-110 N2 ─► WO-111 N3 ─► WO-112 N4 (MVP con Anthropic) ─► WO-113 N5 ─► WO-114 N6 ─► WO-115 N7
                          │
       ┌──────────────────┼─────────────────┬───────────────────┬─────────────────┐
       ▼                  ▼                 ▼                   ▼                 ▼
  WO-116 Experiencia  WO-117 Estrategias  WO-118 Learning  WO-119 EVA/CSI/canales  WO-120 Marketplace ─► WO-121 Comunidad
       └──────────────────┴─────────────────┴───────────────────┴─────────────────┘
                                         ▼
                           WO-122 Certificación ADÁN Enterprise v1
```

## 3. Hitos

| Hito | WOs | Resultado | Avance estimado |
|---|---|---|---:|
| H1 — Base segura | 094 ✅, 090, 095, 096 | Sin RCE ni fugas; bugs críticos corregidos; avisos de IA; builds y blueprint en un solo lugar | ~25 % |
| H2 — Plataforma enterprise | 091, 097, 092, 093 | PostgreSQL, aislamiento por empresa, frontend TS, CI/CD | ~35 % |
| H3 — Núcleo, Nivel 1 real e ingreso recurrente | 098, 099, 107, 108, 109 | Nivel 1 completo con piloto real; primeros agentes por tiempo | ~55 % |
| H4 — Los 7 Niveles | 110 → 115 | Recorrido completo de creación o reinvención de empresa | ~75 % |
| H5 — Experiencia, estrategia y aprendizaje | 116, 117, 118 | ADÁN se siente como lo diseña el blueprint y aprende de las decisiones | ~85 % |
| H6 — Ecosistema, comunidad y certificación | 119, 120, 121, 122 | EVA, CSI, Marketplace, Comunidad y red de comisiones; Gate de Producción | 100 % |

---

## 4. Fichas de Work Order

Criterio de cierre común (EPWO-051), además de lo específico de cada ficha:
- Evidencia objetiva ejecutada.
- Pruebas que pasan (en CI desde WO-093).
- Documentación y deuda registradas.
- `git status` limpio y commits por Sprint.
- Reporte en `docs/wo/` y PR fusionado a `main`.

### WO-094 — Hotfix de seguridad ✅
- RCE en TEF cerrado.
- Protección SSRF.
- Aislamiento por empresa en Nivel 1, cognitivo, OOS, TEF y EMS.
- 5 pruebas de board room corregidas y `tests/test_security.py`.
- Fusionada en `main`.

### WO-095 — Estabilización funcional
- **Alcance:** bugs B1–B4 y B6–B18 de la auditoría. B5, el Gate por palabras clave, es de diseño y va en WO-107. Además:
  - Aprobación explícita del cliente para las decisiones y para cerrar un Nivel (Patrón A), en backend y en la interfaz.
  - **Avisos de IA** en la interfaz, en los documentos y en la API (`AD-DEC-0002` decisión 6).
  - Etiqueta `mock` en toda respuesta simulada (voz, omnicanal, conectores).
  - `requirements-dev.txt`.
- **Cierre específico:** prueba de regresión por cada bug.
- **Estimación:** 3–5 días.

### WO-096 — Consolidación de builds y documentación
- **Alcance:**
  - Importar Build B con su historial.
  - Llevar a `docs/wo-000/` las versiones más nuevas del blueprint que hoy están en Build A.
  - Nueva versión de AD-000 según `AD-DEC-0002` (EVA = ventas y marketing, agentes por tiempo, Genexis interno, Comunidad).
  - Mapa de reutilización A/B → C.
  - Actualizar `.claude/launch.json` y `ADAN_MASTER_ARCHITECTURE_v1.0.md`.
- **Estimación:** 2–3 días.

### WO-091 — PostgreSQL + pgvector *(Canon)*
- **Alcance:**
  - PostgreSQL 16, pgvector y Alembic.
  - Una sola base declarativa.
  - Las 38 entidades de AD-006 v1.2, partiendo de la migración de Build A.
  - Embeddings reales (`nomic-embed-text`) en pgvector.
  - Migración de datos desde SQLite.
- **Estimación:** 5–8 días.

### WO-097 — Seguridad y aislamiento por empresa
- **Alcance:**
  - Autorización centralizada.
  - La app no arranca con `JWT_SECRET` por defecto.
  - Límite de peticiones y de intentos; política de contraseñas.
  - Sesión en cookie `httpOnly`.
  - Credenciales de conectores por empresa y cifradas.
  - Permisos, confirmaciones y timeouts en TEF.
  - Auditoría persistente.
  - Proxy de salida.
  - Sandbox aislado que permita reactivar `python_sandbox` y `file_reader`.
- **Estimación:** 5–8 días.

### WO-092 — Frontend TypeScript y base de UX *(Canon)*
- **Alcance:**
  - TypeScript, tomando como base el frontend de Build A.
  - Design system, workspace y navegación (AD-UX-01/02/04).
  - Cliente API tipado.
  - ESLint y Playwright.
  - Corregir las vulnerabilidades npm.
- **Estimación:** 5–8 días.

### WO-093 — Producción Enterprise *(Canon)*
- **Alcance:**
  - GitHub Actions.
  - Imágenes de producción.
  - Healthchecks.
  - Logs, métricas y trazas.
  - Backups y restauración probados.
  - Despliegue y rollback.
- **Cierre:** Gate de Producción (EPWO-054).
- **Estimación:** 5–8 días.

### WO-098 — Gemelo Digital y Decisiones
- **Alcance:**
  - Los 4 Patrones de AD-008.
  - Versionado real.
  - Event store append-only.
  - Ciclo de vida AD-CMP-06.
  - Decisión con los 6 campos de AD-FUNC-02 §2.5.
  - Vistas de Decisiones y Timeline.
- **Estimación:** 8–12 días.

### WO-099 — Motor cognitivo único e IA
- **Alcance:**
  - Un solo Board Room con los 7 roles de AD-FUNC-02 y el Master Orchestration Flow.
  - Participación del cliente, disenso visible y actas.
  - Memoria de 5 capas (AD-CMP-04).
  - **Enrutamiento de modelos (`AD-DEC-0002` decisión 3):**
    - Ollama avanzado (un modelo local de 7B–14B en lugar del 0,5B actual) para tareas simples.
    - Claude Haiku, Sonnet u Opus de Anthropic según la complejidad.
    - Fallback, degradación controlada y medición de costo por proyecto y Nivel (AD-IA-03).
- **Estimación:** 10–15 días.

### WO-107 — Evidencia y Scoring
- **Alcance:**
  - Jerarquía de evidencia (AD-CMP-05).
  - Los 8 scores de AD-FUNC-07 con su motor (AD-ARQ-10).
  - Gate Review basado en evidencia registrada. Cierra B5.
- **Estimación:** 5–8 días.

### WO-108 — Onboarding y Nivel 1 completo
- **Alcance:**
  - AD-FUNC-06 completo, con **consentimiento de datos** (`AD-DEC-0002` decisión 8).
  - Nivel 1 con evidencia externa vía CSI y aprobación del cliente.
  - Vista de Nivel y Cards.
- **Cierre:** piloto real con una empresa de Paradixe.
- **Estimación:** 5–8 días.

### WO-109 — Agentes por tiempo
- **Objetivo:** que ADÁN suministre agentes por hora, día, semana o mes para tareas específicas de cada empresa (`AD-DEC-0002` decisión 1). Es el ingreso recurrente de ADÁN.
- **Alcance:**
  - Catálogo de agentes: rol, habilidades, herramientas y modelo, construido sobre la `agent_factory` actual llevada a persistencia.
  - Contratación por período y asignación de tareas mediante las Work Orders del OOS.
  - Ejecución con TEF y el motor de WO-099.
  - Medición del tiempo y del trabajo real, y reporte al cliente.
  - Los precios se fijan en WO-100.
- **Depende de:** WO-097, WO-099.
- **Estimación:** 8–12 días.

### WO-110 → WO-115 — Niveles 2 a 7

Cada Nivel se construye con la misma plantilla:
- Las 3 preguntas de AD-FUNC-01 §0.
- Entregable, score y criterio de avance por evidencia.
- Emoción y ritmo (AD-FUNC-03/04).
- Vista propia y aviso de IA en todos los documentos.

| WO | Nivel | Específico | Apoyo | Estimación |
|---|---|---|---|---|
| WO-110 | 2 — Propuesta de Valor | Mercado, competidores, matriz comparativa; validación con clientes reales | CSI | 6–10 días |
| WO-111 | 3 — Plan de Negocios | Estructura legal y tributaria, proyecciones contra benchmarks (agente CFO + CSI), organigrama híbrido | CSI | 6–10 días |
| WO-112 | 4 — MVP | Blueprint técnico, mockups y **MVP construido con Anthropic** a través de Genexis como motor interno; nunca construir sin aprobación | Genexis, Anthropic | 8–12 días |
| WO-113 | 5 — Validación Simulada | Clientes e inversionistas simulados, riesgos, tablero de métricas | — | 6–10 días |
| WO-114 | 6 — Lanzamiento | Primeros sucesos reales verificados; campañas de lanzamiento con EVA | EVA | 6–10 días |
| WO-115 | 7 — Escalamiento | Velocidad de maduración, crisis de crecimiento, acompañamiento continuo con agentes por tiempo | EVA, WO-109 | 6–10 días |

### WO-116 — Experience, Gamification y User Journey
- **Alcance:**
  - 7 emociones y 7 ritmos.
  - XP y logros ligados solo a cambios del Gemelo.
  - Regla anti-manipulación.
  - Índice ADÁN.
  - Journey de AD-FUNC-08.
- **Estimación:** 8–12 días.

### WO-117 — Motor de Estrategias Empresariales
- **Alcance:** AD-FUNC-05 (11 pasos, 16 tipos de estrategia, recursos internos primero) conectado al Board Room.
- **Estimación:** 6–10 días.

### WO-118 — Learning Engine
- **Alcance:** AD-FUNC-09 (3 ciclos de aprendizaje, Playbook, 6 salvaguardas), solo con datos consentidos y anonimizados.
- **Estimación:** 6–10 días.

### WO-119 — Integración con EVA, CSI y canales
- **Alcance:**
  - **EVA** (antes ARQAI): campañas inbound y outbound, voz real en lugar del stub, agentes conversacionales y omnicanalidad.
  - **CSI:** inteligencia externa.
  - Conectores reales (Gmail, Calendar, Slack) con OAuth por empresa.
  - DKA con búsqueda real.
  - Contratos AD-INT actualizados según `AD-DEC-0002`.
- **Estimación:** 12–20 días.

### WO-120 — Marketplace
- **Alcance:**
  - Publicación, descubrimiento y curaduría de agentes, servicios y APIs del ecosistema y de terceros.
  - Integración con el catálogo de agentes de WO-109.
  - Comisiones según WO-100.
- **Estimación:** 6–10 días.

### WO-121 — Comunidad y red de comisiones
- **Alcance:**
  - Comunidad de emprendedores y empresas: perfiles, conexiones y espacios.
  - Red de comisiones multinivel ("Ondas Expansivas"): referidos, árbol de hasta 7 niveles, cálculo y liquidación de comisiones **solo sobre ventas reales**, plan de compensación publicado y contratos (Ley 1700 de 2013, según `AD-DEC-0002` §3.3).
- **Depende de:** WO-100 (términos) y WO-120.
- **Estimación:** 10–15 días.

### WO-122 — Certificación ADÁN Enterprise v1
- **Alcance:**
  - E2E de los 7 Niveles con empresas reales.
  - Auditoría de seguridad externa.
  - Carga para más de 100 empresas.
  - Revisión humana (EPWO-053) y Gate de Producción (EPWO-054).
  - Tag `v1.0.0-enterprise`.
- **Estimación:** 5–8 días.

---

## 5. Esfuerzo total

| Bloque | WOs | Días de trabajo efectivo |
|---|---|---:|
| H1 | 095, 096 (+ cierre de 090) | 5–8 |
| H2 | 091, 097, 092, 093 | 20–32 |
| H3 | 098, 099, 107, 108, 109 | 36–55 |
| H4 | 110 → 115 | 38–62 |
| H5 | 116, 117, 118 | 20–32 |
| H6 | 119, 120, 121, 122 | 33–53 |
| **Total** | **24 WOs** | **~150–240 días** |

Con un solo frente de trabajo son unos 7–11 meses; con dos frentes en paralelo desde H2, unos 5–8 meses. Incluye las revisiones humanas que exige EPWO.

## 6. Orden de ejecución

1. WO-095, en curso.
2. WO-096, en lo que no dependa de la laptop.
3. H2 en el orden de la ruta crítica.
