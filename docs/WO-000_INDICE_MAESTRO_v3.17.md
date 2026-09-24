# WO-000 — Índice Maestro de Especificación de Producto ADÁN (v3.17)

**Tipo de documento:** Árbol documental — **APROBADO Y CONGELADO** (sin cambios de estructura desde v3.1; v3.17 renombra un documento del árbol, no reestructura el árbol).
**Estado de la WO-000:** Fase 1 completa. Funcionalidades: AD-FUNC-01 a 03 aprobados; AD-FUNC-04 y AD-FUNC-05 construidos y autoauditados.

---

## 0. Qué cambió respecto a v3.16

1. **AD-FUNC-05 cambia de nombre: "Marketplace" → "Recomendación de Recursos".** Por instrucción explícita del Board, se reevaluó el nombre antes de construir el documento: "Marketplace" nombra una implementación (un lugar donde se navega y se compra), no la función real que el Board pidió (recomendar recursos con evidencia, de forma proactiva, nunca como catálogo). Se descartó también "Business Ecosystem"/"Ecosistema Empresarial" por colisión directa con "Ecosistema Paradixe" (AD-000 §3, término ya fijo). El nombre "Marketplace" no desaparece — sigue vigente en AD-000 §3 como componente compartido del Ecosistema Paradixe; AD-FUNC-05 ahora es la Funcionalidad de ADÁN que *consume* datos de ese Marketplace (entre otras fuentes), no la que lleva su nombre. Ver AD-FUNC-05 §0 para el análisis completo y la tabla de alternativas descartadas.
2. **AD-FUNC-05 — Recomendación de Recursos, construido.** Amplía el alcance original de v3.1 ("SaaS/agentes/servicios/APIs") a seis clusters: Tecnología, Servicios Paradixe, Personas y relaciones (partners, inversionistas, mentores, empresas aliadas), Conocimiento (cursos, plantillas, casos de éxito), Comunidad, Evidencia agregada. Cada recurso recomendado debe responder ocho preguntas de evidencia (para quién sirve, en qué etapa, empresas similares, resultados, costo, riesgo, recomendación de ADÁN, Confidence Level). Modelo de recomendación proactivo por defecto, no navegable. Fija como Principio Permanente la secuencia **Recomendar → Explicar → Ofrecer** ("ADÁN primero es asesor. Después proveedor."), aplicada por igual a recursos de terceros y a productos propios de Paradixe — ningún privilegio de secuencia por pertenecer al mismo ecosistema.
3. **Verificación explícita contra la Regla de Entidades:** "Recurso" no se crea como entidad nueva en AD-FUNC-05 (solo AD-005/006/007/008 pueden crear entidades). Se modela como dato externo, propiedad del Marketplace del Ecosistema y de otras fuentes, consumido vía un futuro contrato de integración. Lo que sí ocurre al adoptar un recurso —Proveedor, Contrato, Iniciativa, Decisión de Negocio— ya tenía dónde vivir en AD-005, sin necesidad de nada nuevo.
4. **Gap identificado:** la categoría AD-INT (originalmente 4 documentos: EVA, ARQAI, Genexis, CSI) necesita, en Fase 2, una integración adicional con el Marketplace del Ecosistema para que AD-FUNC-05 tenga datos reales — se suma al gap ya señalado para ATO. Registrado como semilla en el Knowledge Graph (`SEED-AD-INT-MARKETPLACE`), no bloquea el diseño de este documento, sí su implementación futura.

---

## 1. Estado de aprobación

| Categoría | Estado |
|---|---|
| Fundamentos (9) + Comportamientos (6) | Completa, aprobada |
| Funcionalidades (9) | AD-FUNC-01 ✅ · AD-FUNC-02 ✅ · AD-FUNC-03 ✅ · AD-FUNC-04 construido y autoauditado · AD-FUNC-05 construido y autoauditado (renombrado) · 4 pendientes |

---

## 2. Nota de cierre

20 documentos con contenido real. El próximo, según el árbol original, es AD-FUNC-06 — Onboarding.
