---
Código: AD-FUNC-07
Nombre: Sistema de Scoring (Producto)
Versión: v1.0
Estado: Construido y autoauditado. Congelado bajo la metodología "se construye, se autoaudita, se congela, se continúa"
Confidence Level: 50%
Fecha: 2026-07-17
Responsable (autor): Célula D (Claude Code), WO-000 Sprint 2
Aprobador: Hernán / Junta Directiva (validación en el próximo Gate Review)
---

# AD-FUNC-07 — Sistema de Scoring (Producto)

> Especifica qué significa cada Score para el usuario — qué mide, cuándo se muestra, qué acción habilita. La fórmula de cálculo (pesos, umbrales, comparación contra mercado) es responsabilidad exclusiva de AD-ARQ-10 (Motor de Scoring), no de este documento — mandato original del índice v3.1, sin cambios. El proceso conceptual de cómo una Conversación se convierte en un Score ya está fijado en AD-CMP-05 (Comportamiento de Evidencia y Scoring); este documento no repite ese proceso, lo hereda.

**Nivel de contenido:** la existencia de Confidence Level obligatorio en todo Score (sección 6), la regla genérica de aplicación del mecanismo de Score a Objetivo y Estrategia (sección 5), y la distinción entre Scores de diagnóstico secuencial y Scores continuos (sección 2) son Principio Permanente. Los nombres, umbrales de acción y momento exacto de cada uno de los 8 Scores (secciones 3-4) son Decisión de Diseño, sujetas a AD-004 §1.

---

## 0. Verificación de nombre y reconciliación de dos fuentes

Este documento reconcilia dos descripciones distintas de la misma Funcionalidad, detectadas en la auditoría de WO-000 Sprint 1 (`AUDIT.md`, hallazgo H-1):

- **Índice original (v3.1):** 8 scores nombrados — Founder, Problem, Solution, Business, Product, Market, Execution, Venture Score.
- **Plan Maestro de Ejecución (WO-000 Sprint 2):** "score empresarial, por proyecto, por usuario, por objetivo, por estrategia, de confianza y evolutivo".

**No son dos modelos distintos — son dos niveles de descripción del mismo modelo.** La reconciliación, aplicada en el resto de este documento:

| Término del Plan Maestro | Se resuelve como |
|---|---|
| Score empresarial | Venture Score (sección 4) — el agregado de toda la Empresa |
| Score por proyecto | Venture Score — el Proyecto (AD-006 §4) es el contenedor 1:1 de una Empresa, mismo score |
| Score por usuario | **Score del Responsable** (sección 3) — ver corrección de nombre abajo |
| Score por objetivo | Regla genérica de la sección 5 — no un score fijo adicional |
| Score por estrategia | Regla genérica de la sección 5 — no un score fijo adicional |
| De confianza | **No es un score separado** — es el Confidence Level que AD-002 §1.9 ya exige en todo Score (sección 6) |
| Evolutivo | Venture Score — es, por diseño, el único de los 8 que se actualiza de forma continua, no ligado a un Nivel específico |

**Corrección de nombre, heredada del mismo patrón ya aplicado en AD-FUNC-06:** "Founder Score" (nombre del índice original v3.1, repetido como ejemplo en AD-003 v1.1 y AD-006 v1.1) colisiona exactamente con la razón por la que AD-006 ya había renombrado "Fundador" a "Usuario Principal" — la Declaración de Misión de AD-001 cubre empresas de cualquier edad, no solo founders en fundación. Se renombra a **Score del Responsable**, consistente con "Responsable de Empresa" ya fijado en AD-FUNC-06 §3.1. Esto exige una versión menor de AD-003 (v1.2) y de AD-006 (v1.2) — ambas se emiten junto con este documento (sección de Impacto).

---

## 1. Qué es esta Funcionalidad

Especifica, para cada uno de los 8 Scores del producto: qué mide, en qué momento del acompañamiento se muestra, y qué acción del sistema o del cliente habilita. No especifica cómo se calcula (AD-ARQ-10) ni cómo una conversación se convierte en evidencia clasificada (AD-CMP-05, ya congelado). Es la capa de significado entre el proceso conceptual (AD-CMP-05) y la implementación técnica (AD-ARQ-10).

---

## 2. Los 8 Scores — dos familias

**Familia 1 — Scores de diagnóstico secuencial** (6 scores): ya anclados por AD-FUNC-01 a cada uno de los Niveles 1-5, aprobados y congelados — este documento no los reabre, solo les da el significado de producto que faltaba.

| Score | Nivel (AD-FUNC-01) | Qué mide | Qué acción habilita |
|---|---|---|---|
| **Problem Score** | 1 — El Dolor | Qué tan real y validado está el problema que el cliente dice tener | Habilita, junto con evidencia de Nivel 1, el avance a Nivel 2 (Patrón B, AD-CMP-01) |
| **Solution Score** | 2 — Propuesta de Valor | Qué tan diferenciada es la solución propuesta frente al Mercado y Competidores reales | Habilita avance a Nivel 3 |
| **Business Score** | 3 — Plan de Negocios | Qué tan sólido es el capital, la estructura y el plan real necesarios | Habilita avance a Nivel 4 |
| **Product Score** | 4 — MVP | Qué tan cerca está el producto construido de la propuesta original | Habilita avance a Nivel 5 |
| **Market Score** | 5 — Validación Simulada | Qué tan bien resiste la propuesta los escenarios simulados de mercado | Habilita, junto con Execution Score, avance a Nivel 6 |
| **Execution Score** | 5 — Validación Simulada | Qué tan bien ejecuta el equipo bajo presión simulada | Habilita, junto con Market Score, avance a Nivel 6 |

**Familia 2 — Scores continuos** (2 scores): no ligados a un Nivel específico, activos desde su primer cálculo y actualizados de forma permanente mientras dure la relación con ADÁN.

| Score | Cuándo nace | Qué mide | Qué acción habilita |
|---|---|---|---|
| **Score del Responsable** | Onboarding, en cuanto existe evidencia real (AD-FUNC-06 §3.1, hito "Líder Activo") | Track record de ejecución y buenas decisiones de la persona responsable — distinto del progreso de la Empresa | Alimenta la estimación de "Probabilidad de éxito" de una Estrategia (AD-FUNC-05 §6) — un Responsable con buen track record sube la probabilidad estimada de que una Estrategia ambiciosa funcione |
| **Venture Score** | Nivel 6 en adelante (cuando el acompañamiento se vuelve continuo, no secuencial — AD-FUNC-01 §Nivel 7) | Salud agregada de la Empresa como conjunto — sucesor natural de los 6 Scores de diagnóstico una vez que ya no hay "siguiente Nivel" que desbloquear | Resumen ejecutivo del Dashboard (AD-UX-03, índice original); insumo directo para decidir qué tipo de Estrategia recomendar (AD-FUNC-05) |

---

## 3. Score del Responsable — detalle

Es-N:1 con **Usuario Principal / Responsable de Empresa** (AD-006 §4), no con Empresa — distinción que obliga un ajuste menor en la definición de la entidad Score (sección 7, y AD-006 v1.2). Se calcula sobre el mismo proceso de AD-CMP-05 (evidencia clasificada por jerarquía de validez), aplicado a Decisiones de Negocio y Sucesos Empresariales donde el Responsable fue el actor — nunca sobre impresión subjetiva de un Agente sin evidencia.

## 4. Venture Score — detalle

Es N:1 con Empresa (igual que los 6 de diagnóstico). Su cálculo consume, como insumo, el historial completo de los 6 Scores de diagnóstico ya producidos — no los reemplaza, los agrega. Se actualiza con cada nuevo Suceso Empresarial real (Nivel 6+) o nueva Decisión de Negocio, versionado (Patrón C, AD-008), igual que cualquier otro Score.

---

## 5. Regla genérica: Score por Objetivo y Score por Estrategia

Ninguno de los dos es un Score fijo con nombre propio en la lista de 8 — son la aplicación del **mismo mecanismo** (AD-006 §4 entidad Score + proceso de AD-CMP-05) a dos entidades que ya existen y ya lo necesitan:

- **Cualquier Objetivo** (AD-005 §2.5) puede y debe tener un Score que mida su avance real hacia la Meta asociada — usando el mismo Indicador que AD-005 ya define, no uno nuevo.
- **Cualquier Estrategia** (AD-FUNC-05 §5) que se ejecute puede y debe tener un Score que trackee su desempeño real en el tiempo — es, en la práctica, el mecanismo concreto detrás de la comparación "ROI esperado vs. ROI real" que AD-FUNC-05 §10 ya exige para alimentar el Learning Engine (AD-FUNC-09).

Crear dos Scores fijos adicionales ("Score de Objetivo", "Score de Estrategia") además de los 8 ya nombrados habría violado el Principio de Emergencia — el mecanismo genérico ya cubre ambos casos sin nombrarlos aparte.

---

## 6. Confidence Level — nunca un score separado

Todo Score de este documento —los 6 de diagnóstico, los 2 continuos, y cualquier aplicación genérica de la sección 5— declara su Confidence Level como atributo obligatorio (AD-002 §1.9, ya heredado del Contrato Base de AD-006). "Score de confianza", tal como aparecía en la descripción del Plan Maestro, no se construye como un noveno score independiente: sería una entidad redundante con algo que el Contrato Base ya garantiza para cualquier Score sin excepción.

---

## 7. Verificación contra la Regla de Entidades y el Principio de Emergencia

Ninguna entidad nueva. **Score** ya existe en AD-006 §4 ("evaluación que ADÁN hace de una Empresa... N:1 con Empresa; declara Confidence Level"). Este documento necesita un ajuste menor a esa definición: el Score del Responsable requiere que la cardinalidad de Score se amplíe de "N:1 con Empresa" a "N:1 con Empresa **o** Usuario Principal" — no es una entidad nueva, es una generalización de una relación ya existente, y se resuelve en AD-006 v1.2 (Impacto sobre otros módulos). Los 8 nombres de Score son Decisión de Diseño (etiquetas de significado), no entidades — la entidad de datos sigue siendo una sola.

## 8. Verificación contra el Criterio de Existencia (AD-004 v1.1 §3.1)

| Condición | ¿Se cumple? | Cómo |
|---|---|---|
| ¿Modifica el Gemelo Digital? | Sí | Cada cálculo de Score es un registro nuevo (Patrón C, AD-008), acumulado en el Gemelo Digital |
| ¿Mejora el conocimiento del cliente? | Sí | El cliente ve, en lenguaje de producto, qué tan bien está progresando en cada dimensión, no solo un número |
| ¿Produce evidencia útil para la siguiente decisión? | Sí | Habilita directamente el avance de Nivel (Patrón B) y la estimación de Probabilidad de éxito de Estrategias (AD-FUNC-05) |

---

## 9. Autoauditoría obligatoria (10 preguntas)

1. **¿Contradice AD-000, AD-001 o AD-002?** No — implementa directamente la regla 1.9 de AD-002 (todo tiene nivel de confianza declarado).
2. **¿Todo concepto nuevo está justificado?** Ninguno de los 8 nombres es una entidad nueva (sección 7); la regla genérica de la sección 5 evita crear 2 scores adicionales sin necesidad.
3. **¿Hay duplicación con un documento existente?** No — hereda el proceso de AD-CMP-05 sin repetirlo, y corrige (no duplica) la colisión de "Founder Score" ya resuelta en espíritu por AD-FUNC-06.
4. **¿Qué impacto tiene sobre documentos futuros?** AD-ARQ-10 implementa la fórmula real de los 8 Scores. AD-UX-03 (Dashboard) muestra Venture Score como resumen ejecutivo. AD-FUNC-09 (Learning Engine) consume Score por Estrategia como su evidencia primaria de aprendizaje.
5. **¿Introduce un riesgo arquitectónico nuevo?** Uno: el ajuste de cardinalidad de Score (N:1 Empresa → Empresa o Usuario Principal) toca una entidad ya congelada — se gestiona como versión menor (v1.2), no como ruptura.
6. **¿El Confidence Level es honesto?** 50% — el modelo de reconciliación es sólido y evidenciado contra AD-FUNC-01 ya aprobado, pero ningún Score tiene todavía un caso real calculado (eso es AD-ARQ-10 + WO-006 de este mismo plan).
7. **Prueba "si este documento desapareciera":** ADÁN tendría 8 nombres de score sin significado de producto — números sin qué acción habilitan ni cuándo se muestran.
8. **Prueba "válido en 10 años":** la distinción diagnóstico-secuencial vs. continuo, y la regla genérica de aplicación a Objetivo/Estrategia, no dependen de qué modelo de IA calcule los números — es una decisión de significado, no de cómputo.
9. **¿Se verificó contra colisiones de nombre?** Sí — "Founder Score" contra el mismo hallazgo ya resuelto en AD-FUNC-06 (sección 0).
10. **¿La autoauditoría se entrega junto con el documento?** Sí, esta sección.

---

## Dependencias

- AD-FUNC-01 Los 7 Niveles (ancla los 6 Scores de diagnóstico — no se reabre)
- AD-CMP-05 Evidencia y Scoring (proceso conceptual heredado, no repetido)
- AD-006 §4 (entidad Score — requiere v1.2, ver Impacto)
- AD-005 §2.5 (Objetivo/Meta/Indicador — base de Score por Objetivo)
- AD-FUNC-05 §6, §10 (Probabilidad de éxito consume Score del Responsable; ROI esperado/real es Score por Estrategia)
- AD-FUNC-06 §3.1 (precedente de la corrección "Founder"→"Responsable")
- AD-002 §1.9 (Confidence Level obligatorio)
- AD-004 v1.1 §3.1 (Criterio de Existencia)

## Documentos relacionados

- AD-ARQ-10 Motor de Scoring (Cálculo) — fórmula, pesos, umbrales (Fase 2, no resuelto aquí)
- AD-UX-03 Dashboard General — consume Venture Score como resumen ejecutivo
- AD-FUNC-09 Learning Engine (Sprint 4 de esta misma WO) — consume Score por Estrategia como evidencia primaria

## Impacto sobre otros módulos

1. **AD-003 pasa a v1.2** — la entrada "Score" reemplaza el ejemplo "Founder Score, Business Score" por "Score del Responsable, Business Score", y su "Responsable del concepto" pasa de "(pendiente)" a "AD-FUNC-07".
2. **AD-006 pasa a v1.2** — la fila "Score" de la tabla de entidades operativas (§4) actualiza su relación principal de "N:1 con Empresa" a "N:1 con Empresa o Usuario Principal" y su ejemplo de "Founder Score" a "Score del Responsable".
3. AD-ARQ-10, cuando se escriba, hereda los 8 nombres y sus 2 familias como contrato de significado que no puede alterar sin nueva versión de este documento.

## Riesgos

- **Riesgo de que los umbrales de acción (ej. "Score suficiente para avanzar de Nivel") resulten mal calibrados sin datos reales** — se resolverá con el primer ciclo real de dogfooding sobre Paradixe (WO-009 de este plan), no antes.
- **Riesgo de que Score del Responsable se perciba como una evaluación punitiva de la persona** — debe comunicarse siempre junto con su Confidence Level y nunca de forma aislada de contexto, coherente con AD-001 §14 (confianza calmada).

## Preguntas abiertas

Ninguna nueva.

## Decisiones pendientes

- Umbrales exactos de "Score suficiente" por Nivel — Decisión de Diseño de AD-ARQ-10, no de este documento.

## Historial de cambios

| Versión | Fecha | Cambio | Motivo |
|---|---|---|---|
| v1.0 | 2026-07-17 | Creación inicial: reconciliación de las dos taxonomías de score (índice original de 8 nombres vs. Plan Maestro de 7 categorías); corrección "Founder Score"→"Score del Responsable"; distinción diagnóstico-secuencial (6, ya anclados por AD-FUNC-01) vs. continuo (2: Responsable, Venture); regla genérica de aplicación a Objetivo/Estrategia sin crear scores fijos adicionales; Confidence Level explícitamente no tratado como score separado | WO-000 Sprint 2 del Plan Maestro de Ejecución ADÁN v1.0 |
