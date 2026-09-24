# Plan de Work Orders para llevar ADÁN al 100 %

**Fecha:** 2026-09-24
**Estado:** PROPUESTA. Requiere aprobación explícita de Hernán (EPWO-007). Ninguna WO de este plan se abre sin su Fase -1 (Regla 7 de `AD-GOV-0001`) ni sin pasar el Gate de Inicio (EPWO-052).
**Deriva de:** `docs/auditoria/AUDITORIA_ADAN_2026-09.md` (avance actual estimado: ~22 %).
**No es fuente de verdad** (Regla 6): la numeración vigente la fija `AD-ROOT-0001 §4`; este plan solo propone.

---

## 0. Qué significa "100 %"

**ADÁN Enterprise v1:** los 7 Niveles funcionando de punta a punta según AD-FUNC-01 a 09, con Board Room, Gemelo Digital, scoring por evidencia, experiencia y aprendizaje, integrado con el ecosistema Paradixe, sobre una plataforma certificada para producción (EPWO-054).

**Fuera de este plan**, porque tienen reserva propia y requieren aprobación separada:
- **WO-100 Business Architecture:** precio por Nivel, billing, revenue share del Marketplace, marco legal (incluidos "Ondas Expansivas" y la IP en disputa).
- **WO-101 → WO-106, cadena SaaS:** cuentas multiempresa, billing y administración (`CHAIN_CLOSURE.md`).

Sin ellas ADÁN puede estar técnicamente completo, pero no listo para venderse.

## 1. Numeración (verificada contra el Canon)

| Rango | Uso |
|---|---|
| WO-090 | Consolidación (abierta: falta el tag de baseline y la revisión humana) |
| WO-091, 092, 093 | Ya definidas en el Canon: PostgreSQL, TypeScript, Producción |
| **WO-094** | **Hotfix de seguridad: ejecutada (PR de esta auditoría)** |
| WO-095 → WO-099 | Nuevas (este plan) |
| WO-100 → WO-106 | Reservadas; no se tocan |
| WO-107 → WO-120 | Nuevas (este plan) |

Numeración interna antigua de Build C (WO-011 → 020): se conserva como historia; toda cita debe indicar la línea (`CATALOGO_WORK_ORDERS.md §1`).

## 2. Ruta crítica

```
WO-094 ✅ ─► WO-090 (cierre) ─► WO-095 ─► WO-096
                                   │
          ┌────────────────────────┴────────────────────────┐
          ▼                                                 ▼
   WO-091 PostgreSQL ─► WO-097 Seguridad por empresa    WO-092 TypeScript + UX base
          │                                                 │
          └──────────────► WO-093 Producción ◄──────────────┘
                                   │
                                   ▼
          WO-098 Gemelo Digital y Decisiones ─► WO-099 Motor cognitivo único
                                   │
                                   ▼
          WO-107 Evidencia y Scoring ─► WO-108 Onboarding + Nivel 1 completo
                                   │
                                   ▼
          WO-109 Nivel 2 ─► WO-110 Nivel 3 ─► WO-111 Nivel 4 ─► WO-112 Nivel 5 ─► WO-113 Nivel 6 ─► WO-114 Nivel 7
                                   │
               ┌───────────────────┼────────────────────┬──────────────────┐
               ▼                   ▼                    ▼                  ▼
   WO-115 Experiencia     WO-116 Estrategias    WO-117 Learning    WO-118 Ecosistema ─► WO-119 Marketplace
               └───────────────────┴────────────────────┴──────────────────┘
                                   ▼
                     WO-120 Certificación ADÁN Enterprise v1
```

Se pueden trabajar en paralelo: WO-092 junto con WO-091/097, y WO-115 → 118 entre sí una vez cerrado WO-114. Los Niveles son secuenciales porque cada uno consume lo que produce el anterior en el Gemelo Digital.

## 3. Hitos

| Hito | WOs | Resultado | Avance estimado |
|---|---|---|---:|
| H1 — Base segura | 094 ✅, 090, 095, 096 | Sin RCE ni fugas; bugs críticos corregidos; los 3 builds y el blueprint en un solo lugar | ~25 % |
| H2 — Plataforma enterprise | 091, 097, 092, 093 | PostgreSQL, aislamiento por empresa, frontend TS, CI/CD y despliegue reproducible | ~35 % |
| H3 — Núcleo y Nivel 1 real | 098, 099, 107, 108 | Nivel 1 cumple AD-FUNC-01 completo; primer piloto real con Paradixe (dogfooding) | ~55 % |
| H4 — Los 7 Niveles | 109 → 114 | Recorrido completo de creación de empresa | ~75 % |
| H5 — Experiencia, estrategia y aprendizaje | 115, 116, 117 | ADÁN se siente como lo diseña el blueprint y aprende de las decisiones | ~88 % |
| H6 — Ecosistema y certificación | 118, 119, 120 | Integrado con EVA, ARQAI, Genexis y CSI; Marketplace; Gate de Producción | 100 % |

---

## 4. Fichas de Work Order

Todas comparten el mismo criterio de cierre (EPWO-051): evidencia objetiva ejecutada, pruebas que pasan en CI (desde WO-093), documentación actualizada, deuda registrada, `git status` limpio, commits por Sprint y un PR revisado por Hernán. Cada ficha agrega solo lo específico.

### WO-094 — Hotfix de seguridad ✅ ejecutada
- **Hecho:** RCE en TEF cerrado (calculadora con AST; `python_sandbox`, `file_reader` y `sql_query` deshabilitadas); protección SSRF en `app/core/net.py`; aislamiento por empresa en Nivel 1, cognitivo, OOS, TEF y EMS; 5 pruebas de `test_board_room` corregidas; `tests/test_security.py`.
- **Pendiente para su cierre:** revisión y merge del PR.

### WO-095 — Estabilización funcional
- **Objetivo:** que lo que ya existe funcione como dice que funciona.
- **Alcance:** bugs B1–B18 de la auditoría. En particular:
  - Recomendaciones (500).
  - Persistencia de `/cognitive/think`.
  - Votos por defecto → abstención y no PROCEED.
  - Registrar todo el disenso.
  - Sin autoaprobación de decisiones y avance de Nivel solo con aprobación explícita del cliente (endpoint aprobar/rechazar, Patrón A).
  - Reutilizar el resultado del Board en recomendaciones y Gate Review.
  - SSE correcto.
  - Eliminar `services/memory.py` muerto.
  - Escala única de confianza.
  - Etiquetar como `mock` en la API toda respuesta de voz, omnicanal y conectores simulados.
  - `requirements-dev.txt` con las dependencias de pruebas.
- **Fuera de alcance:** funcionalidad nueva y cambio de base de datos.
- **Cierre específico:** prueba de regresión por cada bug; flujo Nivel 1 completo (chat → Board → diagnóstico → recomendaciones → aprobación del cliente → Gate) ejecutado contra Ollama real.
- **Estimación:** 3–5 días.

### WO-096 — Consolidación de builds y documentación
- **Objetivo:** un solo repositorio y un solo blueprint.
- **Alcance:**
  - Importar Build B (`git subtree split` de `repos-active/adan` en `adan/platform-integration`) a `adan-platform-integration/`, con su historial, previa revisión de secretos.
  - Llevar a `docs/wo-000/` las versiones más nuevas que hoy solo están en Build A (AD-003 v1.2, AD-006 v1.2, AD-FUNC-07/08/09) y marcar las superadas.
  - Mapa de reutilización A/B → C por módulo.
  - Actualizar `.claude/launch.json` y `ADAN_MASTER_ARCHITECTURE_v1.0.md` (quitar la autodeclaración de "Single Source of Truth").
  - Decidir qué documentos de negocio deben salir del repositorio público.
- **Estimación:** 2–3 días.

### WO-091 — Migración Enterprise: PostgreSQL + pgvector *(definida en el Canon)*
- **Alcance:**
  - PostgreSQL 16 + pgvector y Alembic.
  - Unificar `Base`, `EMSBase` y `OOSBase`.
  - Llevar el modelo a las 38 entidades de AD-006 v1.2, partiendo de la migración de 37 tablas de Build A.
  - Embeddings reales (`nomic-embed-text` vía Ollama) en pgvector, que reemplazan el hash de palabras y los índices en memoria.
  - Script de migración de datos desde SQLite.
- **Reutiliza:** `adan-platform/backend/migrations`, `adan-platform/infra`, `adan-platform/ai/memory`.
- **Cierre específico:** migración de ida y vuelta probada; suite completa contra PostgreSQL real.
- **Estimación:** 5–8 días.

### WO-097 — Seguridad y aislamiento por empresa
- **Objetivo:** cerrar los pendientes S12–S18 y hacer imposible, por diseño, una fuga entre empresas.
- **Alcance:**
  - Dependencia de autorización única (empresa, organización, conversación) usada por todos los routers, más pruebas que lo verifiquen para cada endpoint.
  - La app no arranca en producción con `JWT_SECRET` por defecto.
  - Límite de peticiones y de intentos de login; política de contraseñas.
  - Sesión en cookie `httpOnly` y revocación de tokens.
  - Conectores y credenciales por empresa, cifrados.
  - Permisos, confirmaciones y timeouts efectivos en TEF.
  - Auditoría persistente (AD-OPS-02).
  - Proxy de salida contra DNS rebinding.
  - Sandbox aislado (contenedor efímero sin red ni secretos) que permita reactivar `python_sandbox` y `file_reader` con almacenamiento por empresa.
- **Límite con WO-101 → 106:** esta WO aísla datos dentro de una instancia; cuentas SaaS, planes y billing siguen reservados.
- **Estimación:** 5–8 días.

### WO-092 — Frontend TypeScript y base de UX *(definida en el Canon)*
- **Alcance:**
  - Migrar a TypeScript tomando como base el frontend de Build A.
  - Design system (AD-UX-01), workspace (AD-UX-02), navegación (AD-UX-04) y cliente API tipado desde OpenAPI.
  - ESLint y Playwright; corregir las 5 vulnerabilidades npm.
  - Redactar antes AD-UX-01/02/04, siguiendo la regla del blueprint: especificación antes que interfaz.
- **Estimación:** 5–8 días.

### WO-093 — Producción Enterprise *(definida en el Canon)*
- **Alcance:**
  - GitHub Actions (pruebas backend, lint, build y E2E frontend).
  - Imágenes de producción: uvicorn sin `--reload` con workers, frontend compilado y servido estático, versiones fijadas.
  - Healthchecks.
  - Logs estructurados, métricas y trazas con `trace_id` (AD-OPS-01).
  - Backups y restauración probados.
  - Despliegue y rollback documentados.
- **Cierre específico:** Gate de Producción (EPWO-054), con despliegue limpio y rollback ensayado.
- **Estimación:** 5–8 días.

### WO-098 — Gemelo Digital y Decisiones
- **Alcance:**
  - Los 4 Patrones de estado de AD-008 (A aprobación, B progreso, C registro permanente, D contenedor) aplicados a las 38 entidades.
  - Versionado real: historial y no sobrescritura.
  - Event store append-only.
  - Ciclo de vida AD-CMP-06 (nacer, crecer, dividir, fusionar, archivar).
  - Decisión con los 6 campos de AD-FUNC-02 §2.5 cuando el cliente decide distinto del Board.
  - Vista de Decisiones (AD-UX-10) y Timeline (AD-UX-08).
- **Depende de:** WO-091.
- **Estimación:** 8–12 días.

### WO-099 — Motor cognitivo único (Board Room, memoria e IA)
- **Objetivo:** un solo orquestador y un solo Board Room donde hoy hay dos.
- **Alcance:**
  - Board Room con los 7 roles de AD-FUNC-02 (CEO, CTO, CFO, CMO, Legal, Producto, Operaciones) y el Master Orchestration Flow de 8 pasos.
  - Voto ponderado por evidencia y disenso visible.
  - Participación del cliente e invitados sin voto; actas.
  - Memoria de 5 capas de AD-CMP-04 con resúmenes y la regla de no repetición.
  - Enrutamiento de modelos AD-IA-01 (Claude Haiku/Sonnet/Opus y Ollama local) con fallback y degradación controlada.
  - Evaluación de prompts (AD-IA-02) y medición de costo por proyecto y Nivel (AD-IA-03).
  - Redactar antes AD-ARQ-02/03/04/05 y AD-IA-01.
- **Reutiliza:** `adan-platform/ai/orchestrator`, `adan-platform/ai/agents` y el Board de Build B.
- **Depende de:** WO-098.
- **Estimación:** 10–15 días.

### WO-107 — Evidencia y Scoring
- **Alcance:**
  - Jerarquía de validez de evidencia (AD-CMP-05).
  - Los 8 scores de AD-FUNC-07 (6 de diagnóstico y 2 continuos) con su motor de cálculo (AD-ARQ-10).
  - Gate Review que evalúe evidencia registrada, no palabras clave en texto generado.
  - Confidence Level declarado en cada score.
- **Depende de:** WO-098, WO-099.
- **Estimación:** 5–8 días.

### WO-108 — Onboarding y Nivel 1 completo
- **Alcance:**
  - AD-FUNC-06 completo: captura mínima, identidad progresiva derivada, recuperación y medición de <30 s hasta la primera pregunta.
  - Nivel 1 según AD-FUNC-01: evidencia externa vía CSI (AD-INT-04), perfil del Usuario Principal, entregable "Diagnóstico del Dolor" y aprobación explícita del cliente.
  - Vista de Nivel (AD-UX-05) y Cards (AD-UX-06).
- **Cierre específico:** piloto real con al menos una empresa de Paradixe.
- **Estimación:** 5–8 días.

### WO-109 → WO-114 — Niveles 2 a 7

Cada Nivel se construye con la misma plantilla: las 3 preguntas de AD-FUNC-01 §0 (qué descubre ADÁN, qué aprende el cliente, qué cambia en el Gemelo), su entregable, su score, su criterio de avance por evidencia, su emoción y ritmo (AD-FUNC-03/04) y su vista.

| WO | Nivel | Específico | Integración | Estimación |
|---|---|---|---|---|
| WO-109 | 2 — Propuesta de Valor | Mercado, Competidores, matriz comparativa; validación con clientes reales | CSI | 6–10 días |
| WO-110 | 3 — Plan de Negocios | Estructura legal y tributaria, proyecciones contra benchmarks, organigrama híbrido, Departamento/Cargo/Activo/Pasivo | EVA, CSI | 6–10 días |
| WO-111 | 4 — MVP | Blueprint técnico adaptado al perfil, mockups, Iniciativa de construcción; nunca construir sin aprobación | Genexis | 6–10 días |
| WO-112 | 5 — Validación Simulada | Clientes e inversionistas simulados, Riesgos, tablero de métricas simuladas | — | 6–10 días |
| WO-113 | 6 — Lanzamiento | Primeros Sucesos Empresariales reales verificados; paso a operación continua sobre OOS | EVA, OOS | 6–10 días |
| WO-114 | 7 — Escalamiento | Velocidad de Maduración Organizacional, crisis de crecimiento, seguimiento continuo | EVA | 6–10 días |

### WO-115 — Experience, Gamification y User Journey
- **Alcance:**
  - Las 7 emociones (AD-FUNC-03) y los 7 ritmos (AD-FUNC-04) aplicados a la interfaz.
  - XP, logros e insignias ligados solo a cambios verificables del Gemelo.
  - Regla anti-manipulación verificada con pruebas.
  - Journey de AD-FUNC-08.
  - Sin rankings sociales.
- **Estimación:** 8–12 días.

### WO-116 — Motor de Estrategias Empresariales
- **Alcance:** AD-FUNC-05 (flujo de 11 pasos, 16 tipos de estrategia, recursos internos primero, simulación de impacto y secuencia óptima) conectado al Board Room.
- **Estimación:** 6–10 días.

### WO-117 — Learning Engine
- **Alcance:** AD-FUNC-09 (3 ciclos de aprendizaje, Playbook y 6 salvaguardas contra sesgo e información incorrecta). Aprende de las decisiones, incluidas las que contradicen al Board. Reemplaza `learning/engine.py`.
- **Estimación:** 6–10 días.

### WO-118 — Integraciones del ecosistema y canales
- **Alcance:**
  - Contratos AD-INT-01 a 04: EVA, ARQAI (voz real en lugar del stub), Genexis y CSI.
  - Canales reales (WhatsApp, Telegram, correo) y conectores reales (Gmail, Calendar, Slack) con OAuth por empresa.
  - DKA con búsqueda real en lugar de URLs de demostración.
  - Redactar antes AD-INT-01 a 04 y AD-PLAT-01.
- **Estimación:** 12–20 días.

### WO-119 — Marketplace
- **Alcance:**
  - Publicación, descubrimiento y curaduría de SaaS, agentes y servicios Paradixe, sobre el `plugins/` actual llevado a persistencia y API.
  - El revenue share queda en WO-100.
- **Estimación:** 6–10 días.

### WO-120 — Certificación ADÁN Enterprise v1
- **Alcance:**
  - Recorrido E2E de los 7 Niveles con empresas reales.
  - Auditoría de seguridad externa.
  - Pruebas de carga para más de 100 empresas simultáneas (objetivo de `ADAN_MASTER_ARCHITECTURE §1.4`).
  - Revisión humana de producto (EPWO-053) y Gate de Producción (EPWO-054).
  - Tag `v1.0.0-enterprise`.
- **Estimación:** 5–8 días.

---

## 5. Esfuerzo total

| Bloque | WOs | Días de trabajo efectivo |
|---|---|---:|
| H1 Base segura | 095, 096 (+ cierre de 090) | 5–8 |
| H2 Plataforma | 091, 097, 092, 093 | 20–32 |
| H3 Núcleo y Nivel 1 | 098, 099, 107, 108 | 28–43 |
| H4 Niveles 2–7 | 109 → 114 | 36–60 |
| H5 Experiencia y aprendizaje | 115, 116, 117 | 20–32 |
| H6 Ecosistema y certificación | 118, 119, 120 | 23–38 |
| **Total** | **22 WOs** | **~130–215 días** |

Con un solo frente de trabajo son unos 6–10 meses; con dos frentes en paralelo (plataforma y producto a partir de H2), unos 4–7 meses. Las estimaciones incluyen las revisiones humanas que exige EPWO. El ritmo de Build B (12 WOs en 3 días) no es referencia, porque no pasó por esos gates.

## 6. Próximo paso

1. Revisar y fusionar el PR de WO-094.
2. Aprobar o ajustar este plan (numeración, orden y alcance).
3. Cerrar WO-090 y abrir WO-095 con su Fase -1.
