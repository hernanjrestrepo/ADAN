# WO-000 — Índice Maestro de Especificación de Producto ADÁN (v3.19)

**Tipo de documento:** Árbol documental — **APROBADO Y CONGELADO** (sin cambios de estructura desde v3.1; v3.19 registra la tercera revisión del mismo documento en el mismo día, no reestructura el árbol).
**Estado de la WO-000:** Fase 1 completa. Funcionalidades: AD-FUNC-01 a 03 aprobados; AD-FUNC-04 construido y autoauditado; AD-FUNC-05 en su tercera revisión (construido y autoauditado, aún no aprobado formalmente).

---

## 0. Qué cambió respecto a v3.18

1. **Nombre "Motor de Estrategias Empresariales" se mantiene — se evaluó y descartó un tercer nombre.** El Board propuso "Motor de Evolución Empresarial" (englobaría crear/transformar/operar/escalar/reinventar/recuperar/fusionar/internacionalizar). Se evaluó y no se adopta por dos razones: colisiona de nivel con AD-004 ("Product Evolution", que gobierna la evolución del producto ADÁN, no de la empresa cliente), y sobre-reclama frente a la Declaración de Misión de AD-001 (que ya usa "transformar y escalar" para *todo* ADÁN, no una sola Funcionalidad) y frente a AD-FUNC-01 (Los 7 Niveles, que ya es "evolución" en otro sentido). En vez del renombre, se incorporó la sustancia sin el riesgo: se agregó "Recuperación ante crisis" como sexto cluster de Estrategia — el único verbo de la lista del Board que de verdad faltaba.
2. **Estrategias Compuestas (híbridas).** Una combinación de Estrategias atómicas (ej. capacitar + automatizar + cambiar proceso + contratar) se evalúa como unidad —no como suma de partes, por sinergia o fricción— sin crear ninguna entidad nueva: al ejecutarse resuelve en las mismas entidades AD-005 que sus componentes.
3. **Estrategias Adaptativas — árboles de decisión condición→acción.** "Si ocurre A, haz B; si ocurre C, abandona." Verificado contra la Regla de Entidades: la condición ya es un Suceso Empresarial o Indicador (AD-005), la acción ya es otra Estrategia, y el abandono ya es una transición del Patrón A de AD-008. Lo único nuevo es la forma del contenido (un árbol pequeño en vez de un camino fijo) — no una entidad. El mecanismo técnico de vigilancia de condiciones en tiempo real queda diferido a un futuro AD-ARQ (Fase 2).
4. **Horizonte temporal obligatorio por Estrategia** (Inmediato 0-30 días, Corto plazo 3 meses, Mediano plazo 12 meses, Largo plazo 3 años, Transformacional 5-10 años) — insumo directo para un futuro Roadmap visual (AD-UX, no resuelto aquí). Se agregaron también Probabilidad de éxito, Esfuerzo esperado y Complejidad como campos distintos entre sí y de Confidence Level/Riesgo/Tiempo, siguiendo la misma disciplina de no fusionar métricas que miden preguntas distintas.
5. **Estrategias competidoras como conjunto, dentro del Board Room** — no se reduce a una sola recomendación antes de tiempo; el debate reutiliza AD-CMP-02 (Consenso Multiagente) ya congelado, sin mecanismo nuevo.
6. **Playbook Empresarial registrado como activo futuro, explícitamente no construido.** Conocimiento propietario agregado ("empresas de este perfil que ejecutaron esta combinación de Estrategias crecieron X veces más") — vive como output futuro de AD-FUNC-09 (Learning Engine), no como funcionalidad nueva; no se diseña sin evidencia real, por la misma disciplina de Economía Conceptual que gobierna todo el árbol.
7. **Confidence Level de AD-FUNC-05 bajó de 38% a 35%**, honestamente: más alcance (Compuestas, Adaptativas, Recuperación) sin un solo caso real ejecutado que lo respalde.

---

## 1. Estado de aprobación

| Categoría | Estado |
|---|---|
| Fundamentos (9) + Comportamientos (6) | Completa, aprobada |
| Funcionalidades (9) | AD-FUNC-01 ✅ · AD-FUNC-02 ✅ · AD-FUNC-03 ✅ · AD-FUNC-04 construido y autoauditado · AD-FUNC-05 construido y autoauditado (Revisión 3) · 4 pendientes |

---

## 2. Nota de cierre

20 documentos con contenido real. El próximo, según el árbol original, es AD-FUNC-06 — Onboarding.
