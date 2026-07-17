# Solicitud de Insumos Humanos — Cadena WO-000 → WO-012

**Emitido por:** Célula D, WO-000 Sprint 1 · **Fecha:** 2026-07-17

Insumos previsibles de toda la cadena, para resolución anticipada por el humano. Ninguno bloquea el arranque de la cadena — cada uno se activa como parada dura únicamente cuando la WO correspondiente llegue a necesitarlo, si no se resolvió antes.

| ID | Insumo necesario | WO que lo necesita | Naturaleza (parada dura) | Estado |
|---|---|---|---|---|
| INS-01 | Datos reales de la empresa Paradixe (estructura, finanzas básicas, mercado, equipo) para poblar el Gemelo Digital de dogfooding | WO-009 (Beta) | #3 — información externa inexistente | Pendiente |
| INS-02 | Credenciales de integraciones externas si se activan conectores reales (más allá de import/export de archivos) | WO-011 | #2 — credenciales | Pendiente, no bloquea WO-011 (los conectores sin credenciales se construyen igual) |
| INS-03 | Decisión sobre proveedor de hosting/infraestructura de producción, si excede lo ya disponible localmente | WO-012 | #1 — dinero real | Pendiente, no bloquea el resto de la cadena |
| INS-04 | Código fuente de los proyectos de reutilización autorizada (EVA, JobXeeker, NOURA, TradeHub, MigPAL, VDC) si no está accesible en el entorno de ejecución | WO-002 a WO-006 (según ADR-R de cada célula) | #3 — información externa inexistente | Por verificar en cada WO; mientras tanto se reimplementa el mínimo del camino crítico |
| INS-05 | Confirmación de nombre de dominio/URL de producción, si aplica antes de WO-012 | WO-012 | #3 | Pendiente, no bloquea |

**Nota de la Célula D:** ninguno de estos insumos bloquea el arranque de WO-000 ni de WO-001. Se registran aquí por anticipado, tal como exige la Precondición PRE-0 del Plan Maestro §6, para que el humano pueda resolverlos con antelación si lo desea, depositando la respuesta en `/docs/blocks/RESPUESTAS/`. La cadena continúa sin esperar respuesta.
