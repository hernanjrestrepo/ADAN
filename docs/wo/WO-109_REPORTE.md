# WO-109 — Agentes por tiempo

**Fecha:** 2026-10-02 · **Ejecutor:** Claude Code · **Autoriza:** Hernán ("arranca en paralelo con el WO-109"; permiso para revisar y fusionar los PR, 2026-10-02)
**Formato:** EPWO-050 · **Checklist:** EPWO-051
**Estado:** ✅ Primera versión cerrada al fusionar su PR. Los precios están pendientes: se fijan en WO-100.

---

## 1. Fase -1

| Verificación | Resultado |
|---|---|
| Canon | `docs/auditoria/PLAN_WO_ADAN_100.md` §4 y `AD-DEC-0002` decisión 1: ADÁN suministra agentes por hora, día, semana o mes para tareas de cada empresa. Es su ingreso recurrente. |
| Reutilización | <ul><li>`agent_factory`: solo existía en memoria; ahora es un catálogo persistente.</li><li>Work Orders y Assignments del OOS.</li><li>TEF: ejecutor con permisos, timeouts y auditoría persistente (WO-097).</li><li>Motor de WO-099: el nivel de modelo según la complejidad y el costo por empresa (`llm_usage`).</li></ul> |
| Fuera de alcance | Los precios (WO-100). El sistema no los inventa: cada contrato dice "Precio por definir (WO-100)". |

## 2. Qué se hizo

| Pieza | Detalle |
|---|---|
| **Catálogo** | Cuatro agentes iniciales, cada uno con rol, habilidades, herramientas de TEF, nivel de modelo y su forma de trabajar:<ul><li>Investigador de Mercado;</li><li>Analista Financiero;</li><li>Redactor Comercial;</li><li>Asistente de Operaciones.</li></ul> |
| **Contratación por período** | La capacidad se mide en horas de trabajo efectivo:<ul><li>1 hora = 1 h, vigente 30 días;</li><li>1 día = 8 h;</li><li>1 semana = 40 h;</li><li>1 mes = 160 h.</li></ul>El contrato vence por calendario o cuando se acaban las horas, y se puede cancelar. |
| **Tareas = Work Orders del OOS** | Cada encargo es una Work Order de la organización OOS de la empresa (se crea si no existe), asignada al agente con su Assignment. Así el OOS ve todo el trabajo. |
| **Ejecución con TEF y WO-099** | Cada ejecución sigue cuatro pasos:<ol><li>El agente decide, con salida estructurada, si usa una de sus herramientas.</li><li>Si la usa, la ejecuta TEF, con permisos y auditoría.</li><li>Entrega su resultado con el modelo de su nivel.</li><li>Si el modelo falla, el intento queda registrado y la tarea sigue abierta, con el motivo.</li></ol> |
| **Revisión del cliente** | Cada entrega queda "para revisar". El cliente la aprueba o pide cambios, y sus correcciones llegan al agente en la siguiente ejecución. |
| **Medición y reporte** | `hire_work_logs` es un Registro Permanente, protegido por triggers. Por ejecución guarda:<ul><li>el tiempo real;</li><li>los tokens y el costo del modelo para ADÁN;</li><li>el modelo usado y si hubo degradación;</li><li>las herramientas usadas y el resultado.</li></ul>El reporte al cliente muestra horas contratadas, usadas y restantes, las entregas y las tareas por estado. |
| **Interfaz** | Página `/agentes/{empresa}` con:<ul><li>el catálogo, con período y cantidad, y las horas que incluye;</li><li>los contratos, con su barra de horas;</li><li>la opción de encargar una tarea y ponerla a trabajar;</li><li>la revisión de cada entrega, para aprobarla o pedir cambios.</li></ul>Se llega desde el tablero. |
| **Migración `0008`** | Tablas `hire_offerings`, `hire_contracts` y `hire_work_logs`, esta última con triggers append-only. |

## 3. Evidencia

| Evidencia | Resultado |
|---|---|
| Suite con SQLite | **417 passed**, 8 omitidas |
| Suite con PostgreSQL 16 | **422 passed**, 3 omitidas |
| Pruebas nuevas (`tests/test_wo109.py`, 10) | Cubren:<ul><li>catálogo sin precios inventados;</li><li>capacidad por período y validaciones;</li><li>tareas como Work Orders del OOS con su Assignment;</li><li>el agente usa la calculadora de TEF, que queda auditada en `tef_audit_log`, y el resultado le llega;</li><li>la revisión, con correcciones que llegan a la siguiente ejecución;</li><li>falla registrada;</li><li>capacidad agotada y cancelación;</li><li>registro inmutable;</li><li>reporte;</li><li>privacidad.</li></ul> |
| Migración | `0008` sube, baja, vuelve a subir y `alembic check` queda limpio, en SQLite y en PostgreSQL. |
| Frontend | Tipos y lint limpios. **25 E2E**; la nueva recorre contratar → encargar → poner a trabajar → aprobar. |

## 4. Decisiones (por delegación)

1. **La capacidad se mide en horas de trabajo efectivo,** el tiempo real que el agente trabaja, no en horas de calendario. 1 día equivale a 8 h, 1 semana a 40 h y 1 mes a 160 h, como en una jornada humana. Es lo que se reporta al cliente y lo que WO-100 podrá cobrar.
2. **Cada entrega la aprueba el cliente** (Patrón A). Un agente nunca da por terminada su propia tarea.
3. **Contratar no requiere una aprobación aparte:** el cliente es quien contrata. Si WO-100 agrega pago, la activación del contrato esperará el pago.
4. **Una herramienta por ejecución.** Es una versión inicial simple y auditable; los ciclos de varias herramientas llegan cuando haya casos reales.

## 5. Pendiente

- **Precios, facturación y cobro:** WO-100.
- **Probarlo con Claude:** la clave de Anthropic es válida, pero la cuenta no tiene saldo ("credit balance is too low"). Sin saldo, los agentes trabajan con Ollama en modo degradado.
- **Reconciliar el OOS con el Gemelo** (departamentos y objetivos paralelos): sigue abierto y conviene una WO propia.
- **Más agentes en el catálogo y agentes propios por empresa:** cuando haya demanda real.

## 6. Checklist EPWO-051

- [x] Evidencia objetiva (§3).
- [x] Pruebas en local; CI en el PR.
- [x] Documentación y deuda registradas.
- [ ] PR fusionado con el CI en verde.
