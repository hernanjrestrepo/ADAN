# WO-098 — Gemelo Digital y Decisiones

**Fecha:** 2026-10-02 · **Ejecutor:** Claude Code · **Autoriza:** Hernán. El plan está aprobado ("sí a todas", 2026-09-24) y Hernán delegó las decisiones de esta sesión ("hazlo todo, lo que tengas que tomar decisiones tómalas tú", 2026-10-01).
**Formato:** EPWO-050 · **Checklist:** EPWO-051
**Estado:** ✅ Cerrada al fusionar su PR. Las decisiones tomadas por delegación están en §4; Hernán puede revisarlas y revertir cualquiera.

---

## 1. Fase -1

| Verificación | Resultado |
|---|---|
| Canon | WO-098 está definida en `docs/auditoria/PLAN_WO_ADAN_100.md` §4. La rama oficial es `main` (AD-ROOT-0001 §2). |
| Especificación | Se leyeron:<ul><li>AD-005: las 26 entidades de negocio y la identidad del Gemelo.</li><li>AD-006 v1.2: Contrato Base y 12 entidades operativas.</li><li>AD-007: el Gemelo como límite de agregación.</li><li>AD-008: los 4 Patrones, los permisos por actor y "toda transición genera un Evento".</li><li>AD-CMP-03: Decisión.</li><li>AD-CMP-05: Evidencia.</li><li>AD-CMP-06: ciclo de vida.</li><li>AD-FUNC-02 §2.5: los 6 campos de la decisión divergente.</li></ul> |
| Estado previo | Existían 11 de las 38 entidades. Los Eventos y Scores se podían modificar y borrar. No había versiones. La Decisión no tenía el estado *Presentada*, ni opciones ni evidencia. Toda la actividad se atribuía al sistema: el Board Room "aprobaba" escribiendo directo en la base. |
| Reutilización | Los modelos de Build A (`adan-platform/backend/app/models/`) sirvieron de referencia para los campos de AD-005. El flujo de Nivel 1 (Board Room, Gate Review y `GemeloDigitalService`) se conservó y ahora pasa por las reglas nuevas. Build B sigue sin importar (WO-096). |
| Hallazgos que bloqueaban verificar | Tres pruebas de DKA pasaban en silencio sin red (`if > 0`). `test_stress.py` nunca corría en CI. El avatar del Board mostraba "C" para todos los roles. Se corrigieron en el sprint 0, antes de tocar el Gemelo. |
| Sesión paralela | El 2026-10-01 una sesión trabajó sobre la rama `laptop` sin ver `main` y rehízo WO-090 a WO-093. Sus commits quedan en el historial como registro (Regla 5 de AD-GOV-0001), con un merge `-s ours`: no entra nada de su contenido. Se recomienda fusionar el PR con *squash*. |

## 2. Qué se hizo

| Sprint | Pieza | Detalle |
|---|---|---|
| 0 | **Pruebas herméticas** | <ul><li>Servidor HTTP local para DKA e integraciones, con aserciones reales. La protección SSRF de producción no se toca.</li><li>`test_stress.py` corre en CI contra un uvicorn levantado por la propia suite.</li><li>`dka/tools.py` pasa de 0 % a 100 % de cobertura.</li><li>Avatar del Board con 3 letras.</li></ul> |
| 1 | **Las 38 entidades** (AD-005, AD-006 v1.2) | <ul><li>Las 23 entidades de negocio que faltaban: Marca, Accionista, Departamento, Cargo, Rol Funcional, Empleado, Cliente Final, Producto/Servicio, Mercado, Competidor, Proveedor, Proceso, Iniciativa, Suceso Empresarial, Contrato, Objetivo, Meta, Indicador, Decisión de Negocio, Activo, Pasivo, Ingreso y Gasto.</li><li>Las 3 operativas que faltaban: Workspace, Agente y Tarea.</li><li>Riesgo como propiedad transversal y polimórfica (Proceso, Iniciativa, Contrato o Decisión). Score polimórfico (Empresa o Usuario Principal).</li><li>Contrato Base en todas: versión, estado, responsables, fuente de evidencia, confianza y razonamiento.</li><li>Catálogo de Agentes: ADÁN más los 7 roles del Board.</li><li>Migración `0004`.</li></ul> |
| 2 | **4 Patrones, versiones y eventos** (AD-008) | Un solo hook de SQLAlchemy (`app/twin/hooks.py`) aplica las reglas en cada `flush`:<ul><li>**Nada se borra.** Patrón C (Score, Evento, Suceso Empresarial, versiones y linaje) es inmutable. Lo impiden el ORM y los triggers de PostgreSQL y SQLite.</li><li>**A, B y D** validan cada transición contra su máquina de estados y contra el actor. Un Agente propone, pero nunca aprueba, rechaza ni ejecuta. ADÁN tampoco aprueba.</li><li>**Versión completa** de cada alta o cambio en `entity_versions`, con actor y motivo.</li><li>**Evento de dominio** por cada transición, alta o archivo. Los eventos del motor cognitivo quedan en la categoría `cognitive`, fuera del Timeline.</li><li>El actor viaja en un `ContextVar` (`acting_as`). El cliente decide a su nombre; el Board Room y el Gate Review proponen como Agentes.</li></ul>API `/api/v1/twin`: catálogo, identidad (Edad, Madurez, Etapa, Velocidad de Maduración), alta, edición, archivo y restauración de las 24 clases (las 23 entidades más Riesgo), historial, Timeline y roles N:M. Cada empresa solo ve sus datos (WO-097). |
| 3 | **Decisión completa** (AD-CMP-03, AD-FUNC-02 §2.5) | <ul><li>Flujo Propuesta → **Presentada** → Aprobada o Rechazada → Ejecutada.</li><li>Opciones con fundamento, nivel de evidencia y confianza, más la opción recomendada. Board Room: Avanzar, Pivotar o Detener. Gate Review: cerrar el Nivel o seguir trabajándolo.</li><li>**Consulta previa:** cada propuesta guarda las decisiones ya aprobadas.</li><li>El **disenso** del Board queda adjunto.</li><li>**Decidir distinto** exige los 6 campos; los riesgos asumidos quedan además como Riesgos del Gemelo.</li><li>Ejecutar puede originar una **Decisión de Negocio** enlazada.</li><li>Migración `0005`.</li></ul> |
| 3 | **Ciclo de vida** (AD-CMP-06) | <ul><li>**Nace** con Empresa, Narrativa, Proyecto, Workspace y 7 Niveles (evento `twin_born`).</li><li>**Crece** con cada versión.</li><li>**Cambia** por Reinvención (Ley 9): nueva Narrativa, mismo Gemelo e historial.</li><li>**Se divide** desde una Iniciativa aprobada y **se fusiona**. En ambos casos hay herencia por referencia (`twin_lineage`).</li><li>Se **pausa**, se **reanuda** y se **archiva**. Un Gemelo archivado sigue consultable y queda de solo lectura.</li></ul> |
| 4 | **Vistas** (AD-UX-08, AD-UX-10) | Página `/gemelo/:id` con tres pestañas:<ul><li>**Resumen:** estado, Edad, Madurez, Etapa, linaje y entidades por clúster.</li><li>**Decisiones:** presentar con razonamiento, aprobar la recomendación o elegir otra opción (con el formulario de riesgos y responsabilidad), rechazar y marcar como ejecutada.</li><li>**Timeline:** eventos con actor y motivo, con paginación por cursor `(fecha, id)` que no pierde eventos con la misma marca de tiempo.</li></ul>Se llega desde el tablero y desde la miga de pan del Nivel 1. |

## 3. Evidencia

| Evidencia | Resultado | Método |
|---|---|---|
| Suite con SQLite | **370 passed**, 8 omitidas: las de PostgreSQL y Redis, que corren en CI | `pytest`, local |
| Suite con PostgreSQL 16 | **375 passed**, 3 omitidas: las de Redis | `pytest` con `TEST_DATABASE_URL`, local |
| Pruebas de WO-098 | 37 pruebas en `tests/test_wo098.py`. Cubren:<ul><li>el catálogo y las 38 entidades;</li><li>alta, edición, archivo y restauración con historia completa;</li><li>que nada se borra;</li><li>validación y referencias que no salen del Gemelo;</li><li>roles N:M y riesgos;</li><li>los 4 Patrones y la atribución del actor;</li><li>identidad y Timeline, incluida la paginación con marcas de tiempo repetidas;</li><li>los triggers en bases migradas, SQLite y PostgreSQL;</li><li>el ciclo completo de la Decisión y los 6 campos;</li><li>nacer, reinventar, dividir, fusionar, pausar y archivar.</li></ul> | `pytest` |
| Migraciones | `0004` y `0005`: subir, bajar a `0003`, volver a subir y `alembic check` sin diferencias, en SQLite y PostgreSQL. Los triggers append-only quedan instalados en los dos. | Alembic, local |
| Frontend | Tipos y lint limpios. **16 E2E**, 5 de ellos del Gemelo: resumen, ciclo de la decisión, decisión divergente, Timeline y navegación. | Playwright con Chromium y API simulada |
| Verificación real | Contra el backend real, con una base nueva y Chromium:<ol><li>registro;</li><li>empresa y 4 entidades;</li><li>propuesta con dos opciones;</li><li>presentar;</li><li>elegir la opción no recomendada, con riesgos y responsabilidad;</li><li>ejecutar con una Decisión de Negocio.</li></ol>Resultado: 11 eventos en el Timeline, 2 Riesgos creados y la Decisión de Negocio ejecutada y enlazada. | `docs/wo/evidencia/WO-098/` (4 capturas) |
| CI | Sprints 0 a 3 en verde en GitHub Actions. El resto queda en la corrida del PR. | GitHub Actions |

## 4. Decisiones de diseño (tomadas por delegación)

1. **Nombres en inglés, etiquetas en español.** Las tablas y clases siguen el estilo del código existente. Lo que ve el usuario sale de `app/twin/registry.py`.
2. **Renombres por choque con el OOS.** El OOS ya tenía clases `Department`, `Objective`, `Initiative`, `Task` y `Risk`. Las del Gemelo se llaman `CompanyDepartment`, `CompanyObjective`, `CompanyInitiative`, `LevelTask` y `TwinRisk`.
3. **`company_id` en todas las entidades de negocio.** Es el límite de agregación de AD-007 y la base del aislamiento de WO-097. Accionista y Mercado también son por empresa: compartirlos entre Gemelos se decidirá con el aprendizaje entre empresas (WO-118) o el Marketplace (WO-120).
4. **Usuario Principal es un rol, no una tabla.** Es `companies.primary_user_id` sobre Usuario. Así, las 12 operativas son 11 tablas más ese rol.
5. **Dos "decisiones".** La Decisión de ADÁN (tabla `decisions`, Patrón A, lo que propone el Board) es distinta de la Decisión de Negocio de AD-005 (lo que la empresa decidió en su operación). Ejecutar la primera puede crear la segunda, y quedan enlazadas.
6. **Heurísticas provisionales**, hasta WO-107 (Evidencia y Scoring):
   - Nivel de evidencia de una opción del Board por la proporción de votos: alta si es más de la mitad, media desde un tercio, baja por debajo.
   - Etapa del ciclo de vida por Edad y Madurez. "Estancamiento" es Edad sin Madurez.
7. **El Workspace nace con la empresa y no emite `entity_created`.** Es un contenedor técnico, no un hecho de negocio para el Timeline.
8. **Cerrar un Nivel con "seguir trabajándolo"** deja la decisión ejecutada sin completar el Nivel. Queda documentado que el cliente eligió continuar.
9. **El cliente también puede registrar una propuesta** con opciones (`POST /twin/{id}/decisions`). Los Agentes proponen solo por sus flujos (Board Room y Gate Review).
10. **El catálogo de Agentes es global**, sin `company_id`. Se siembra en la migración, y la copia SQLite→PostgreSQL lo fusiona por código.

## 5. Deuda y riesgos

- **El OOS tiene su propio modelo paralelo** de Departamentos, Objetivos y KPIs. La fuente oficial pasa a ser el Gemelo; la reconciliación queda para WO-109.
- **La delegación de AD-008 no está modelada.** Hoy aprueba cualquier actor de tipo usuario que sea dueño de la empresa. Varios usuarios por empresa con permisos delegados entran con la cadena SaaS (WO-101 a WO-106).
- **Triggers en SQLite y migraciones futuras.** Una operación `batch_alter_table` de Alembic sobre `events`, `scores`, `business_occurrences`, `entity_versions` o `twin_lineage` recrea la tabla y, en SQLite, borra sus triggers. Esa migración debe volver a llamar a `_create_append_only_triggers()` (ver `0004`). PostgreSQL no se ve afectado.
- **Fechas sin zona horaria (UTC "naive")**, igual que el resto del código. Si se cambia, que sea para todo el sistema a la vez.
- **Sin pantallas de edición** para las 23 entidades nuevas ni para dividir, fusionar o reinventar. Hoy hay API y conteos en el Resumen. El alcance pedía las vistas de Decisiones y Timeline; las demás llegan con los Niveles que llenan esas entidades (WO-108 en adelante).
- **El botón "Ver eventos anteriores"** no tiene prueba E2E. El cursor está probado en el backend.
- **Build B sigue sin importar** (WO-096). Si trae algo útil para el Gemelo, se integra al importarlo.

## 6. Checklist EPWO-051

- [x] Evidencia objetiva ejecutada (§3).
- [x] Pruebas que pasan en local y en CI.
- [x] Documentación y deuda registradas: README, Canon, plan, estado y este reporte.
- [x] `git status` limpio y un commit por sprint.
- [x] Reporte en `docs/wo/`.
- [ ] PR fusionado a `main`, con el CI en verde.
