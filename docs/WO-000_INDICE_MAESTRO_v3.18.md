# WO-000 — Índice Maestro de Especificación de Producto ADÁN (v3.18)

**Tipo de documento:** Árbol documental — **APROBADO Y CONGELADO** (sin cambios de estructura desde v3.1; v3.18 registra el segundo renombre del mismo documento en el mismo día, no reestructura el árbol).
**Estado de la WO-000:** Fase 1 completa. Funcionalidades: AD-FUNC-01 a 03 aprobados; AD-FUNC-04 construido y autoauditado; AD-FUNC-05 en su segunda revisión (construido y autoauditado, aún no aprobado formalmente).

---

## 0. Qué cambió respecto a v3.17

1. **AD-FUNC-05 — segundo renombre del mismo día: "Recomendación de Recursos" → "Motor de Estrategias Empresariales".** El Board cuestionó el objeto de razonamiento del documento por segunda vez: un empresario no compra recursos, compra capacidades — y una recomendación de recurso es, en el mejor de los casos, la consecuencia final de un análisis estratégico, nunca su punto de partida. AD-FUNC-05 deja de ser un recomendador y pasa a ser el sistema que diagnostica brechas empresariales reales, identifica qué capacidad falta, evalúa toda forma razonable de cerrarla —empezando siempre por lo que la Empresa ya tiene— y entrega una secuencia de estrategias con impacto estimado. El flujo obligatorio: Problema detectado → Diagnóstico → Brechas → Capacidades requeridas → Estrategias posibles → Simulación de Impacto → ROI esperado → Secuencia óptima → Recomendación → Ejecución (decisión del cliente) → Aprendizaje.
2. **Alcance de Estrategia ampliado a 15 tipos en 5 clusters** (Personas: capacitar/contratar/despedir; Operación: automatizar/cambiar procesos; Tecnología: comprar/desarrollar software; Estructura: cambiar estructura organizacional; Alianzas y Capital: tercerizar/buscar socios/levantar inversión/adquirir empresas/fusionarse; Expansión y Modelo: internacionalizarse/cambiar el modelo de negocio) — ya no se limita a software. Cada tipo se mapeó a una entidad de AD-005 ya existente, o a AD-CMP-06 (fusión/adquisición de Gemelos Digitales) o a la Ley 9 del Workshop de Comportamientos (Reinvención, para cambio de modelo de negocio) — **ninguna entidad nueva, AD-005 no se tocó.**
3. **"Recursos internos primero" se eleva a Principio Permanente y paso obligatorio del flujo** (Empleado, Activo, Proceso, Proveedor ya vinculado, Documento interno) — ninguna alternativa externa se evalúa antes de descartar que la Empresa ya tiene lo necesario.
4. **AD-003 → v1.1** (cambio menor, un solo término): la entrada "Motor (de Capacidad)" se amplió para declarar que "Capacidad" es el concepto general —aplicable tanto a lo que el Ecosistema provee a ADÁN como a lo que una Empresa cliente necesita— sin crear el término nuevo "Capacidad Empresarial" que se había considerado y descartado explícitamente.
5. **Separación explícita Confidence Level / Impacto Esperado** — nunca se fusionan en una sola cifra; se agregó ROI esperado, Tiempo, Costo, Dependencias y Orden recomendado como campos propios de cada Estrategia.
6. **Ciclo de aprendizaje ampliado, registrado como dependencia explícita de AD-FUNC-09:** Brecha → Capacidad → Estrategia elegida → Implementación → Resultado → ROI real → Desviación frente al ROI esperado → Aprendizaje → Recalibración del Confidence Level — compara proyección contra resultado real, no solo si una recomendación se aceptó o se rechazó.
7. **Confidence Level de AD-FUNC-05 bajó de 42% a 38%**, honestamente: el modelo es arquitectónicamente más sólido que la Revisión 1, pero cubre un alcance mucho mayor (13 de 15 tipos de estrategia sin un solo caso real ejecutado todavía).

---

## 1. Estado de aprobación

| Categoría | Estado |
|---|---|
| Fundamentos (9) + Comportamientos (6) | Completa, aprobada |
| Funcionalidades (9) | AD-FUNC-01 ✅ · AD-FUNC-02 ✅ · AD-FUNC-03 ✅ · AD-FUNC-04 construido y autoauditado · AD-FUNC-05 construido y autoauditado (Revisión 2, renombrado dos veces) · 4 pendientes |

---

## 2. Nota de cierre

20 documentos con contenido real (AD-003 cuenta como v1.1, no como documento adicional). El próximo, según el árbol original, es AD-FUNC-06 — Onboarding.
