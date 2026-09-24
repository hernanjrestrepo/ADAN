---
Identificador: WO-000-ANEXO-MPI (no es un código AD-XXX — este anexo no cuenta entre los 58 documentos del árbol, es un estándar transversal que rige cómo se construyen todos ellos)
Nombre: Meta-Principios de Ingeniería
Versión: v1.0 — APROBADA Y CONGELADA. Superseded el mismo día por v2.0 — ver WO-000_ANEXO_Meta-Principios-de-Ingenieria_v2.0.md
Estado: Aprobado y congelado. No editar en el sitio. El Board señaló que este anexo probablemente se reutilizará en otros productos de Paradixe, no solo en ADÁN — ver nota en Historial de cambios
Confidence Level: 60%
Fecha de aprobación: 2026-07-14
Responsable (autor del borrador): CC (Claude Code)
Aprobador: Hernán / Junta Directiva
---

# WO-000 — Anexo: Meta-Principios de Ingeniería

> AD-001 gobierna quién es ADÁN. AD-002 gobierna qué debe garantizar el sistema. Este anexo gobierna algo distinto de ambos: **cómo se toman las decisiones de construcción** —de documentación hoy, de arquitectura mañana— durante toda la vida del proyecto. No es un documento del Blueprint; es el criterio con el que se juzga cada documento del Blueprint, incluidos los que ya existen. Por eso vive como anexo transversal de la WO-000, no como un AD-XXX más.

**Nivel de contenido:** Principio Permanente en su totalidad — igual que AD-001 y AD-002, estos nueve principios deberían seguir siendo el criterio de decisión dentro de veinte años, independientemente de qué tecnología, equipo o modelo de negocio ejecute el proyecto en ese momento.

---

## 1. Los Nueve Meta-Principios

### 1. El dominio prevalece sobre la tecnología

Ninguna decisión de dominio (qué es una entidad, qué significa un término, qué regla de negocio aplica) se toma en función de qué es fácil o difícil de implementar con la tecnología disponible hoy.

- **Justificación:** si la tecnología dicta el dominio, cada cambio de proveedor, modelo o framework fuerza un cambio de significado del producto. Este principio es la razón de fondo detrás de la secuencia ya fijada en el backbone de la WO-000 (Domain Model antes que Arquitectura, v3.1 §12) — ese orden no es una preferencia estética, es la aplicación directa de este principio.
- **Violación de ejemplo:** cambiar la definición de "Nivel" (AD-003) porque el modelo de IA actual maneja mejor conversaciones cortas que largas.

### 2. La evidencia prevalece sobre la opinión

Toda decisión de diseño de la propia WO-000 —qué documento escribir, qué estructura usar, qué término fijar— se justifica con evidencia (uso real, riesgo demostrado, contradicción encontrada), no con preferencia estética.

- **Justificación:** este principio ya existe a nivel de *producto* (AD-001 Filosofía #2, AD-002 regla 1.1) — aquí se extiende explícitamente al *proceso de construir el producto*. No es un principio nuevo, es el mismo principio aplicado un nivel más arriba: si ADÁN debe evidencia a sus clientes, quienes construyen ADÁN se deben evidencia a sí mismos.
- **Violación de ejemplo:** agregar un documento nuevo "porque parece más completo", sin poder señalar qué riesgo concreto mitiga.

### 3. La simplicidad prevalece sobre la sofisticación innecesaria

Cada capa de sofisticación agregada sin necesidad demostrada es deuda —conceptual o técnica— que alguien más tendrá que pagar después.

- **Justificación:** distinto de Economía Conceptual (AD-002 §1.10), que gobierna cuándo se agrega un *concepto* nuevo. Este principio gobierna cuánta *complejidad interna* se permite dentro de un concepto ya aceptado (cuántos estados tiene una entidad, cuántas reglas se anidan en un comportamiento). Son complementarios, no duplicados: uno vigila la cantidad de piezas, el otro vigila la complejidad de cada pieza.
- **Violación de ejemplo:** un flujo de aprobación con cinco estados intermedios cuando dos bastan para capturar la misma información de negocio.

### 4. La experiencia del usuario prevalece sobre la comodidad de implementación

Cuando construir la experiencia correcta cuesta más que construir una versión más fácil de implementar, se elige la primera.

- **Justificación:** heredado directamente de AD-001 §14. Aquí se convierte en regla de decisión operativa: la complejidad que este principio y el principio 3 protegen es la complejidad *experimentada por el usuario*, nunca la complejidad de construirlo. Si hay que elegir dónde vive la complejidad, se absorbe internamente — nunca se traslada al usuario.
- **Violación de ejemplo:** mostrarle al usuario un mensaje de error técnico sin traducir porque es más rápido de implementar (viola además AD-001 §§15-16, personalidad y tono).

### 5. Toda decisión debe minimizar la complejidad futura

Entre dos soluciones igualmente simples hoy, se prefiere la que deja menos deuda para cuando el sistema crezca diez veces.

- **Justificación:** distinto del principio 3 (que mira la complejidad presente) — este mira hacia adelante. Es la razón por la que, por ejemplo, "Nivel" se define una sola vez en AD-003/AD-FUNC-01 y todo lo demás lo referencia, en vez de que cada documento redefina cuántos Niveles existen.
- **Violación de ejemplo:** fijar el número "7" en múltiples documentos en lugar de derivarlo de una sola fuente de verdad (viola además la Regla de No Duplicación, v3.1 §1).

### 6. Ninguna limitación temporal de una tecnología debe modificar el modelo conceptual del producto

El dominio se diseña para ser correcto; la tecnología se cambia cuando no alcanza al dominio, nunca al revés.

- **Justificación:** elaboración específica del principio 1, dirigida al caso de violación más común y más tentador: "el modelo actual no soporta X bien, así que redefinimos X para que sea más fácil de implementar hoy". Se declara aparte, con su propio ejemplo, porque la tentación de esta violación específica es mayor que la del principio general.
- **Violación de ejemplo:** eliminar el campo de nivel de confianza de un Score porque el modelo de IA actual no calcula bien la incertidumbre, en vez de mejorar el mecanismo de cálculo o esperar a que exista uno mejor.

### 7. La deuda conceptual es tan importante como la deuda técnica

Un término ambiguo, una entidad redundante o una regla contradictoria sin resolver es tan costosa como código mal escrito sin refactorizar — y se gestiona con la misma disciplina.

- **Justificación:** las organizaciones de ingeniería miden y gestionan deuda técnica rutinariamente; rara vez miden deuda conceptual, aunque suele ser más cara de pagar después porque afecta a todo lo que se construye encima. Este principio eleva la deuda conceptual al mismo estatus de seguimiento.
- **Violación de ejemplo:** dejar sin resolver la colisión de nombre "Decisión" / "Decisión de Diseño" —encontrada en la autoauditoría de AD-003— con el argumento de que "no rompe nada todavía".

### 8. Las decisiones irreversibles requieren mayor evidencia que las reversibles

El estándar de evidencia exigido sube en proporción directa a lo difícil que sea deshacer una decisión.

- **Justificación:** complementa la Regla 1.3 de AD-002 (todo es reversible) para el subconjunto de decisiones donde la reversibilidad genuinamente no es posible (eliminar datos de forma permanente, fijar un nombre de marca, comprometer una integración externa). Ahí no basta con el nivel de evidencia estándar — se exige más, precisamente porque no hay forma de corregir el error después.
- **Violación de ejemplo:** fijar el nombre definitivo de "Paradixe Capital" (decisión pendiente en AD-000) sin verificación de disponibilidad de marca, solo porque "ya se habló bastante del tema".

### 9. La arquitectura debe poder evolucionar sin romper el dominio *(propuesto por Claude Code — ver justificación de inclusión)*

Un cambio de arquitectura técnica nunca debe forzar un cambio en el modelo de dominio o en el comportamiento ya definido.

- **Por qué se propone además de los ocho anteriores:** apareció en los ejemplos iniciales de la instrucción del Board pero no en la lista final de ocho — se incluye aquí, con justificación explícita, en vez de omitirse silenciosamente o agregarse sin explicar por qué. Sostiene algo que la WO-000 ya decidió pero nunca declaró como principio: por qué el backbone ordena Domain Model antes que Arquitectura (v3.1 §12). Sin este principio explícito, un documento de Arquitectura futuro (Fase 2) podría proponer, sin darse cuenta, un cambio de dominio "porque la implementación lo pide" — que los principios 1 y 6 ya prohíben en general, pero este lo dice específicamente desde el ángulo donde ese riesgo es más probable de materializarse: la construcción técnica real.
- **Violación de ejemplo:** proponer que la entidad "Nivel" tenga una estructura distinta en la base de datos de la que tiene conceptualmente en AD-006, "porque es más eficiente de consultar así".

---

## 2. Principios considerados y descartados

En cumplimiento del principio 3 de este mismo anexo (simplicidad sobre sofisticación innecesaria) y de la Regla de Economía Conceptual (AD-002 §1.10), se evaluaron y se descartaron explícitamente tres candidatos adicionales, presentes en la fase de ejemplos de la instrucción original:

- *"Un concepto solo existe si genera más valor que complejidad"* — descartado por ser duplicado exacto de la Regla de Economía Conceptual (AD-002 §1.10). Se referencia, no se repite (Regla de No Duplicación, v3.1 §1).
- *"Toda ambigüedad se resuelve documentándola, no asumiéndola"* — descartado por estar ya cubierto por el mecanismo obligatorio de Preguntas Abiertas / Decisiones pendientes, vigente en todo documento desde v3.1.
- *"No se construye para el caso hipotético, se construye para el caso evidenciado"* — descartado por ser, en esencia, la Regla 1.1 de AD-002 (Todo genera evidencia) aplicada al proceso de construcción — ya cubierta por el principio 2 de este mismo anexo.

Esta sección existe deliberadamente para que el proceso de selección quede tan trazable como el resultado — un anexo sobre cómo se toman las decisiones de ingeniería debe, él mismo, mostrar su propio razonamiento de inclusión y exclusión.

---

## Dependencias

- AD-001 Product DNA (principios 4 hereda directamente de su sección 14; el resto son de un nivel de abstracción distinto pero no pueden contradecirlo)
- AD-002 Principios del Sistema v2.0 (principios 2, 3, 8 y 9 son elaboraciones o complementos directos de sus reglas 1.1, 1.10, 1.3 y del backbone que ya fija)

## Documentos relacionados

- Todo documento futuro de la WO-000 — este anexo es el criterio de juicio, no un documento a implementar.
- AD-004 Product Evolution (primer documento redactado bajo este anexo — se apoya directamente en los principios 1, 5, 6, 7 y 9 para definir qué puede y no puede cambiar en ADÁN)
- Toda la categoría Arquitectura (Fase 2) — el principio 9 aplica con mayor fuerza ahí que en cualquier otro lugar de la WO-000.

## Impacto sobre otros módulos

Este anexo se convierte en criterio de aceptación transversal, junto con la Prueba de Reconstrucción (v3.1) y el Checklist de Justificación de Diseño (AD-002 §2). A partir de ahora, la autoauditoría obligatoria (v3.4 §1) debe poder señalar, cuando sea relevante, qué Meta-Principio respalda una decisión de diseño no trivial.

## Riesgos

- **Riesgo de que nueve principios de alto nivel se usen para justificar cualquier decisión post-hoc.** Un principio como "minimizar complejidad futura" es fácil de invocar retroactivamente para defender casi cualquier elección. Mitigación: cada principio exige un ejemplo concreto de violación (ya incluido en cada uno) precisamente para que su aplicación sea verificable, no retórica.
- **Riesgo de tensión no resuelta entre principios 1/6 (dominio sobre tecnología) y decisiones reales de costo.** En la práctica, Fase 2 (Arquitectura) va a encontrar casos donde el dominio "correcto" es significativamente más caro de construir que una alternativa más simple. Este anexo no resuelve esa tensión — la declara como jerarquía (dominio gana), dejando a Fase 2 la responsabilidad de escalar el caso al Board cuando el costo sea materialmente alto, en vez de resolverlo unilateralmente.

## Preguntas abiertas

Ninguna al cierre de esta versión.

## Decisiones pendientes

Ninguna decisión de negocio pendiente en este anexo.

## Historial de cambios

| Versión | Fecha | Cambio | Motivo |
|---|---|---|---|
| v1.0 | 2026-07-14 | Creación inicial: ocho meta-principios instruidos por el Board, más un noveno propuesto y justificado por Claude Code, más una sección explícita de tres principios considerados y descartados | Anexo transversal de la WO-000, solicitado por el Board antes de iniciar AD-004 |
| v1.0 — Aprobada | 2026-07-14 | Aprobación formal del Board, sin cambios de contenido. Se congela. El Board señaló explícitamente que este anexo probablemente será reutilizado, sin modificación de fondo, como estándar de ingeniería para otros productos de Paradixe (EVA, ARQAI, Genexis, CSI) más allá de ADÁN — no se actúa sobre esa observación en esta versión, se deja registrada para cuando corresponda | Cierre del ciclo de revisión del Anexo |
| — | 2026-07-14 | **Superseded por v2.0** el mismo día: se agrega el Principio de Emergencia (décimo), motivado por dos rechazos reales de conceptos nuevos (Enterprise Genome, ciclo de vida de relaciones) que usaron ese razonamiento sin que todavía existiera como regla explícita. Este archivo v1.0 se conserva como evidencia histórica | Segundo caso de la disciplina de versionado sobre un documento ya aprobado (el primero fue AD-002 v1.0→v2.0) |
