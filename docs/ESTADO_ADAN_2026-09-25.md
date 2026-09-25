# Estado de ADÁN — 2026-09-25

**Para:** Hernán · **Preparado por:** Claude Code, al pausar el trabajo antes de WO-098
**En una línea:** ADÁN pasó de **~22 % a ~35 %** del camino a ADÁN Enterprise v1. Quedaron cerradas la **base segura (H1)** y la **plataforma enterprise (H2)**. Lo que sigue es el producto: Gemelo Digital, la IA de calidad y los Niveles 2 a 7.

---

## 1. Qué se hizo

| Paso | Resultado | Detalle |
|---|---|---|
| Unificación | Todo ADÁN vive ahora en un solo repositorio público, `hernanjrestrepo/ADAN`, con `main` como rama oficial. Build A quedó en `adan-platform/` y el prototipo de 2024 en `autonomous/`, los dos con su historial completo. Del monorepo de la laptop solo se subió la carpeta de ADÁN: los datos de clientes nunca salieron de la laptop. | `README.md`, `AD-ROOT-0001` (Canon), `AD-DEC-0001` |
| Decisiones de negocio | Se registró qué es ADÁN en Paradixe: crea o reinventa empresas, alquila agentes por tiempo, usa Ollama y Anthropic según la complejidad, tiene comisiones multinivel y participación por negociación, lleva avisos de IA siempre y recorre 7 Niveles. | `AD-DEC-0002` |
| Auditoría al 100 % del código | Avance medido en ~22 %, con la lista de bugs y brechas frente al blueprint. De ahí salió un plan de 24 Work Orders para llegar al 100 %. | `docs/auditoria/AUDITORIA_ADAN_2026-09.md`, `docs/auditoria/PLAN_WO_ADAN_100.md` |
| **WO-094** Hotfix de seguridad ✅ | Se cerraron la ejecución remota de código en TEF y el SSRF. | Plan §4 |
| **WO-095** Estabilización ✅ | Bugs críticos de Nivel 1 corregidos. El Board Room ahora tiene quórum y disenso visible, y las respuestas de IA llevan su aviso. | `docs/wo/WO-095_REPORTE.md` |
| **WO-096** Consolidación 🟡 | Blueprint ordenado, mapa de qué reutilizar de Build A y documentación de arquitectura. Falta importar Build B desde la laptop (§5). | `docs/wo/WO-096_REPORTE.md` |
| **WO-091** PostgreSQL + pgvector ✅ | Base de datos de producción con migraciones versionadas (Alembic). Los embeddings pasaron a ser semánticos de verdad, y una base vieja se adopta sin perder datos. | `docs/wo/WO-091_REPORTE.md` |
| **WO-097** Seguridad por empresa ✅ | Una empresa no puede ver datos de otra. Sesión en cookie segura, anti-CSRF, bloqueo de login y límites de uso. Credenciales cifradas y auditoría persistente de herramientas. | `docs/wo/WO-097_REPORTE.md` |
| **WO-092** Frontend ✅ | Interfaz en TypeScript con sistema de diseño base, dependencias al día y pruebas de navegador (Playwright). | `docs/wo/WO-092_REPORTE.md` |
| **WO-093** Producción ✅ | CI en GitHub en cada cambio, con el stack completo en Docker. Imágenes de producción sin root. Logs con `request_id`, métricas Prometheus y readiness. Límites en Redis, sandbox aislado, backups y restauración probados, despliegue y rollback con un comando. `pip-audit` pasó de 35 vulnerabilidades a 0. | `docs/wo/WO-093_REPORTE.md`, `docs/operacion/RUNBOOK.md` |

Todo está verificado en CI:
- Backend: 313 pruebas con SQLite y 317 con PostgreSQL.
- Frontend: E2E en el navegador.
- Producción: prueba de humo de 18 verificaciones, más backup, rollback y restauración.

## 2. Avance

| Hito | Contenido | Estado | Avance acumulado |
|---|---|---|---:|
| Punto de partida (auditoría) | Build C "Vertical Nivel 1" | — | ~22 % |
| H1 — Base segura | 094, 095, 096 | ✅ (solo falta Build B) | ~25 % |
| H2 — Plataforma enterprise | 091, 097, 092, 093 | ✅ | **~35 %** |
| H3 — Núcleo, Nivel 1 real e ingreso recurrente | 098, 099, 107, 108, 109 | ⏳ siguiente | ~55 % |
| H4 — Los 7 Niveles | 110 → 115 | — | ~75 % |
| H5 — Experiencia, estrategia y aprendizaje | 116, 117, 118 | — | ~85 % |
| H6 — Ecosistema y certificación | 119 → 122 | — | 100 % |

**Cómo leer el +13 %:** casi todo el salto está en la **plataforma**: seguridad, datos, CI, producción y estabilidad de Nivel 1. El **producto** sigue concentrado en el Nivel 1. Los Niveles 2 a 7, el scoring por evidencia y la IA de calidad son H3 y H4. Es una estimación razonada con el método de la auditoría, no una medición.

## 3. Qué se puede ver hoy y cuándo

**Qué funciona hoy:**
- Registro e ingreso.
- Crear una empresa.
- En el Nivel 1:
  - conversación con ADÁN sobre el dolor;
  - Board Room de 4 agentes, con votos, quórum y disenso;
  - diagnóstico y scores;
  - Gate Review, donde el cliente aprueba o rechaza cerrar el Nivel.

**Limitación importante:** el modelo local por defecto (`qwen2.5:0.5b`) es muy pequeño. Las respuestas son pobres y el Board suele abstenerse porque el modelo no devuelve JSON válido. Esto se resuelve en WO-099 con Ollama avanzado y Anthropic.

| Para ver… | Qué hace falta | Cuándo |
|---|---|---|
| **La plataforma en un computador** | Docker. Correr `docker compose up --build` y abrir http://localhost:5174 (ver `README.md`, "Arranque rápido"). | **Hoy mismo** |
| **La plataforma en internet** | Elegir servidor, dominio con TLS, backups externos y monitoreo (criterios 16 a 19 del Gate). El despliegue ya es un comando: `scripts/deploy.sh`. | Pocos días después de elegir la infraestructura |
| **Una demo con calidad para mostrar** | Respuestas buenas del Board y del chat: WO-099, con una API key de Anthropic. | ~2–3 semanas si se adelanta WO-099 |
| **Piloto real con una empresa de Paradixe** | Cerrar H3 (WO-098, 099, 107, 108) | ~36–55 días de trabajo (2–3 meses) |
| **ADÁN completo, 7 Niveles (100 %)** | H3 a H6 | ~130–200 días de trabajo: 6–10 meses con un frente, 4–7 meses con dos |

**Recomendación:** si lo primero es **ver y mostrar** ADÁN, conviene adelantar **WO-099** (IA de calidad) antes de WO-098. Es lo que más cambia la experiencia visible.

## 4. Siguiente paso técnico: WO-098 (Gemelo Digital y Decisiones)

La Fase -1 quedó hecha: se leyeron AD-005, AD-006 v1.2, AD-007, AD-008, AD-CMP-03, AD-CMP-05, AD-CMP-06, AD-FUNC-02 y los modelos de Build A. Todavía no hay código escrito. Diseño propuesto:

- **Entidades:** hoy existen 11 de las 38. Faltan las 23 de negocio de AD-005 (Marca, Accionista, Departamento, Cargo, Rol Funcional, Empleado, Cliente Final, Producto/Servicio, Mercado, Competidor, Proveedor, Proceso, Iniciativa, Suceso Empresarial, Contrato, Objetivo, Meta, Indicador, Decisión de Negocio, Activo, Pasivo, Ingreso y Gasto) y 3 operativas (Workspace, Agente y Tarea). Se parte de `adan-platform/backend/app/models/`, con todo filtrado por empresa. Score pasa a ser polimórfico (Empresa o Usuario Principal) y Riesgo se guarda como propiedad transversal.
- **4 Patrones (AD-008):** se validan en un solo punto (hook de SQLAlchemy) con el actor de cada cambio (Usuario Principal, agente o sistema). Toda transición genera un Evento automáticamente. Un agente nunca aprueba ni ejecuta una decisión.
- **Versionado real y event store append-only:** una tabla de versiones con el cambio, el autor y el motivo. `events`, las versiones y los Scores no se pueden modificar: lo impiden el ORM y triggers en PostgreSQL y SQLite. Los eventos se separan en "dominio" (para el Timeline) y "cognitivo".
- **Decisión (AD-CMP-03, AD-FUNC-02 §2.5):** agrega el estado *Presentada*, las opciones con su evidencia y su confianza, y la consulta previa de decisiones anteriores. Si el cliente elige distinto a lo recomendado, se registran los 6 campos: opción elegida, opción recomendada, evidencia y confianza de cada una, riesgos asumidos y responsabilidad del cliente.
- **Ciclo de vida (AD-CMP-06):** nacer, crecer, reinventarse, dividirse, fusionarse y archivarse, con API `/api/v1/twin/...`.
- **Vistas:** Decisiones y Timeline en el frontend.
- **Deuda a decidir:** el OOS tiene su propio modelo de Departamentos, Objetivos y KPIs, paralelo a AD-005. La fuente oficial pasa a ser el Gemelo, y el OOS se reconcilia en WO-109.

## 5. Pendiente de Hernán (solo él puede hacerlo)

1. En GitHub: dejar `main` como rama por defecto y borrar las ramas `laptop` y `laptop-platform`.
2. Archivar los repositorios `adan_autonomous` y `ADAN-BACK`.
3. Importar Build B desde la laptop con los pasos de `docs/wo/WO-096_REPORTE.md` §4. **Nunca** se sube el monorepo completo: tiene datos de clientes.
4. Elegir la infraestructura de producción (servidor, dominio, backups externos y monitoreo), proteger `main` y firmar el Gate (`docs/operacion/GATE_PRODUCCION_H2.md`).
5. Para WO-099: una API key de Anthropic (se configura como secreto; nunca va en el repositorio).
