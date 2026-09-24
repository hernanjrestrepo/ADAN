# WO-000 Sprint 1 — Auditoría de Fuentes del Blueprint ADÁN

**Célula:** D · **Fecha:** 2026-07-17 · **Fuente auditada:** `/docs/blueprint/source/` (37 archivos, copiados desde el repo de documentación original)

---

## 1. Inventario de documentos por categoría

| Categoría | Documentos | Versión vigente | Estado |
|---|---|---|---|
| Fundamentos | AD-000 a AD-008 (9 docs) | Ver tabla §2 | Completos, aprobados |
| Comportamientos | AD-CMP-01 a 06 (6 docs) | v1.0 cada uno | Completos, aprobados |
| Funcionalidades | AD-FUNC-01 a 06 (6 docs) | Ver tabla §3 | AD-FUNC-01/02/03 aprobados; AD-FUNC-04 construido; **AD-FUNC-05 y AD-FUNC-06 APPROVED FOR GATE REVIEW** |
| Anexos | Meta-Principios de Ingeniería | v2.0 | Vigente |
| Workshops | Taxonomy, Relaciones, Comportamientos | Únicos (no versionados, son material de trabajo) | Vigentes como referencia, no como fuente de verdad |
| Índice Maestro | v3.21 (última) | v3.21 | Vigente — v3.1 conservada como referencia del árbol original de 58 documentos |
| Knowledge Graph | `kg.json` + README | Único | 86 nodos, 79 edges al momento de esta auditoría |

## 2. Versiones duplicadas detectadas — cuál es la vigente

Varios documentos tienen más de una versión en la fuente (v1.0 y v1.1, en un caso v1.0/v1.1/v1.2 pendiente). Regla aplicada: **la versión de número más alto es la vigente; las anteriores se conservan solo como evidencia histórica del Historial de cambios, nunca como fuente activa.**

| Documento | Versiones presentes | Vigente |
|---|---|---|
| AD-001 Product DNA | v1.0, v1.1 | **v1.1** |
| AD-002 Principios del Sistema | v1.0, v2.0 | **v2.0** |
| AD-003 Product Language | v1.0, v1.1 | **v1.1** (ver hallazgo H-3, requiere v1.2) |
| AD-004 Product Evolution | v1.0, v1.1 | **v1.1** |
| AD-006 Domain Model | v1.0, v1.1 | **v1.1** (ver hallazgo H-3, requiere v1.2) |
| AD-007 Gemelo Digital | v1.0, v1.1 | **v1.1** |
| Índice Maestro | v1 a v3.21 (28 versiones) | **v3.21** — el resto es historial de proceso, no contenido funcional vigente |

## 3. Estado de aprobación real de Funcionalidades (AD-FUNC)

| Doc | Nombre vigente | Estado | Nota |
|---|---|---|---|
| AD-FUNC-01 | Los 7 Niveles | Aprobado, congelado definitivamente | No se reabre bajo ninguna circunstancia (instrucción explícita del Board) |
| AD-FUNC-02 | Board Room | Aprobado | — |
| AD-FUNC-03 | Experience Engine | Aprobado | — |
| AD-FUNC-04 | Gamification Engine | Construido y autoauditado | Pendiente de Gate Review formal, sin bloquear la cadena |
| AD-FUNC-05 | Motor de Estrategias Empresariales | **APPROVED FOR GATE REVIEW** | Renombrado dos veces (Marketplace → Recomendación de Recursos → Motor de Estrategias Empresariales) antes de esta aprobación. No se reabre — instrucción explícita de este mismo plan |
| AD-FUNC-06 | Onboarding | **APPROVED FOR GATE REVIEW** | Revisión 2 + Prueba del Minuto Cero incorporada |
| AD-FUNC-07/08/09 | — | No existen | Se escriben en esta WO (Sprints 2-4) |

## 4. Contradicciones y huecos detectados

### H-1 (Alta) — Taxonomía de Scores: dos fuentes distintas, sin reconciliar

El índice original (v3.1) define AD-FUNC-07 alrededor de 8 scores nombrados: **Founder, Problem, Solution, Business, Product, Market, Execution, Venture Score**. Este Plan Maestro (§9, WO-000 Sprint 2) describe AD-FUNC-07 con una taxonomía distinta: **"score empresarial, por proyecto, por usuario, por objetivo, por estrategia, de confianza y evolutivo"**.

**Resolución adoptada** (aplicada en AD-FUNC-07, Sprint 2): las dos taxonomías no son incompatibles, son dos niveles de descripción del mismo modelo. Los 6 scores ya anclados a Niveles por AD-FUNC-01 (Problem/Solution/Business/Product/Market/Execution, aprobado y congelado, no se reabre) se mantienen como los "scores de diagnóstico secuencial". "Founder Score" se renombra a **Score del Responsable** (ver H-3) y cubre "score por usuario". **Venture Score** cubre "score empresarial"/"evolutivo"/"score por proyecto" (es el score continuo y agregado, activo desde Nivel 6). "Score de confianza" no se trata como un noveno score independiente — ya existe como el Confidence Level que AD-002 §1.9 exige en *todo* score (crear uno separado violaría el Principio de Emergencia). "Score por objetivo" y "score por estrategia" se resuelven como una **regla genérica de aplicación** del mismo mecanismo de Score (AD-006 + AD-CMP-05) a las entidades Objetivo (AD-005 §2.5) y Estrategia (AD-FUNC-05), no como dos scores fijos adicionales — evita inflar la lista de nombres sin necesidad real.

### H-2 (Media) — Gap de integración AD-INT ya señalado dos veces, nunca resuelto

El índice original solo define AD-INT-01 a 04 (EVA, ARQAI, Genexis, CSI). Dos gaps quedaron señalados en AD-FUNC-05 sin resolver: falta integración con ATO y con el Marketplace del Ecosistema. No se resuelve en este Sprint — es Fase 2 (fuera del alcance funcional de WO-000), se mantiene registrado como Decisión pendiente heredada.

### H-3 (Media) — "Founder Score" sobrevive como ejemplo en 2 documentos aprobados y congelados

AD-003 v1.1 y AD-006 v1.1 todavía usan "Founder Score" como ejemplo ilustrativo del concepto "Score", a pesar de que AD-006 mismo ya había renombrado "Fundador" a "Usuario Principal" (Hallazgo 1, por ser demasiado angosto para empresas de cualquier edad), y de que AD-FUNC-06 ya corrigió la misma colisión para su escalera de Identidad Progresiva ("Founder" → "Responsable de Empresa"). **Acción:** AD-003 pasa a v1.2 y AD-006 pasa a v1.2 (cambios menores, un ejemplo cada uno) al cerrar el Sprint 2, reemplazando el ejemplo por "Score del Responsable".

### H-4 (Baja) — "Capacidad Operativa" del Enterprise Taxonomy Workshop nunca resuelta explícitamente en AD-005 §6

Ya señalado en AD-FUNC-05. No bloquea nada, se mantiene como Decisión pendiente heredada, no se resuelve en esta WO.

### H-5 (Baja) — Comunidad como entidad propia

AD-005 §6 deja explícitamente abierta la posibilidad de que "Comunidad" se convierta en entidad si un caso real lo exige. Ninguna Funcionalidad construida hasta ahora lo ha necesitado. Se mantiene abierta.

## 5. Veredicto de la auditoría

Ninguna contradicción bloquea el inicio de WO-000 Sprint 2. H-1 y H-3 se resuelven dentro de este mismo Sprint (AD-FUNC-07 + versiones menores de AD-003/AD-006). H-2, H-4, H-5 quedan correctamente diferidas — no son bloqueos, son decisiones de diseño abiertas ya documentadas en su origen.

**Insumos humanos necesarios detectados en esta auditoría:** ninguno bloquea WO-000. Ver `SOLICITUD_DE_INSUMOS.md` para la lista completa de insumos previsibles de toda la cadena.
