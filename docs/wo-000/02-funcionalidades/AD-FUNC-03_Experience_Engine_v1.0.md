---
Código: AD-FUNC-03
Nombre: Experience Engine
Versión: v1.0
Estado: Construido y autoauditado. Congelado por Claude Code bajo la metodología "se construye, se autoaudita, se congela, se continúa"
Confidence Level: 52%
Fecha: 2026-07-14
Responsable (autor): CC (Claude Code)
Aprobador: Hernán / Junta Directiva (validación en el próximo Gate Review)
---

# AD-FUNC-03 — Experience Engine

> Especifica la capa de orquestación de la experiencia — el "cómo se siente", no las mecánicas. Por instrucción explícita del Board, este documento diseña primero la emoción y después, en otro documento, la interfaz. No hay animaciones, avatares, sonidos ni oficinas aquí — eso es AD-FUNC-04 (Gamification Engine) y AD-UX. Este documento responde una sola pregunta, Nivel por Nivel: **¿cómo debe sentirse un empresario mientras lo atraviesa?**

**Nivel de contenido:** la emoción objetivo de cada Nivel y sus principios de justificación son Decisión de Diseño, pero de la más permanente posible — cambiar la emoción objetivo de un Nivel sin evidencia de que la actual no funciona sería exactamente el tipo de cambio arbitrario que el Meta-Principio 2 (evidencia sobre opinión) prohíbe.

---

## 0. Principio rector: la emoción se diseña antes que la interfaz

Toda decisión de interfaz futura (AD-UX) y de mecánica de juego futura (AD-FUNC-04) debe poder responder: *¿a qué emoción objetivo de este documento sirve?* Si no puede responderlo, esa decisión no nace — es la misma disciplina que el Criterio de Existencia de AD-004 v1.1 §3.1 exige para toda Funcionalidad, aplicada aquí a nivel de interacción específica, no solo de Funcionalidad completa.

**Regla de honestidad emocional (AD-001 §14, §16):** ninguna emoción de esta especificación se fabrica — se refleja. Si un Nivel no ha producido avance real, la experiencia no simula entusiasmo o seguridad que el cliente no debería sentir todavía. La emoción objetivo es lo que el cliente *debería* sentir cuando lo que ADÁN le presenta es honesto y real — nunca lo que haría que se quedara más tiempo si no lo fuera.

---

## 1. Las Siete Emociones Objetivo

| Nivel | Emoción objetivo | Por qué (evidencia) | Qué debe evitarse explícitamente | Señal de que se logró |
|---|---|---|---|---|
| 1 — El Dolor | **Comprendido** | El diseño original de este Nivel (Chat 1.docx) ya lo pedía explícitamente: "muy conversacional... entender muy bien... como un diagnóstico inicial". Nadie describe su problema con precisión ante alguien que siente que no está escuchando | Sentirse **juzgado o interrogado** — una batería de preguntas sin calidez rompe exactamente lo que Nivel 1 necesita para producir evidencia honesta | El cliente extiende voluntariamente sus respuestas sin que se le pida — señal de que se siente escuchado, no evaluado |
| 2 — Propuesta de Valor y Diseño Estratégico | **Inspirado por la claridad** *(no hype genérico)* | Este Nivel puede pivotar la idea original del cliente (AD-FUNC-01 §2) — el riesgo es que sienta que "le quitaron" su idea. Debe sentir, en cambio, que la idea se volvió más nítida | **Desanimado** — que perciba la comparación con competidores como "tu idea no es especial", en vez de "ahora sabemos qué te hace diferente" | El cliente propone variaciones propias sobre la propuesta ajustada, en vez de solo aceptar pasivamente lo que ADÁN sugiere |
| 3 — Plan de Negocios y Estructura Empresarial | **Seguro** | Fuente directa (Chat 1.docx): "Es nuestro deber, desde ADÁN, ayudar a que estos números sean exactos... para que no los agarre por sorpresa" — la inseguridad financiera es, literalmente, la causa de fracaso que este Nivel existe para prevenir (AD-005 §5, Ley 6, Crisis) | **Abrumado** — la complejidad legal/financiera/organizacional de este Nivel es real; la experiencia no debe ocultarla, pero tampoco debe presentarla toda a la vez sin guía | El cliente toma decisiones financieras (presupuesto, estructura) sin pedir que alguien más las revise primero — señal de confianza real, no de resignación |
| 4 — Diseño y Construcción del MVP | **Emocionado, con base real** | La idea se vuelve tangible por primera vez — un blueprint aprobado, no una promesa | **Urgencia artificial** — expresamente prohibida por AD-001 §14 (confianza calmada, nunca urgencia fabricada); el entusiasmo debe originarse en el blueprint real, no en presión de avance | El cliente comparte el blueprint o el mockup con alguien fuera de la conversación con ADÁN — señal de orgullo genuino, no solo de aprobación funcional |
| 5 — Validación Simulada y Ajuste | **Desafiado, no amenazado** | Este Nivel expone debilidades a propósito (AD-005 §5, Ley de Adaptación) — el entorno es simulado precisamente para que el desafío sea seguro | **Amenazado o atacado** — la experiencia nunca debe sentirse como que "el sistema busca fallas para hundir la idea"; busca fallas para protegerla antes del riesgo real | El cliente pide más simulaciones o escenarios por iniciativa propia, en vez de intentar cerrar el Nivel lo más rápido posible |
| 6 — Lanzamiento y Operación Real | **Acompañado** | Es el momento de mayor riesgo real (primer dinero, primeros clientes reales) — y el momento donde más founders se sienten solos. La promesa de AD-001 (nunca abandona después de "vender el nivel") se prueba exactamente aquí | **Abandonado** — la experiencia nunca debe sentirse como que ADÁN "entregó el producto y se retiró"; el acompañamiento continúa aunque el negocio ya no dependa exclusivamente de ADÁN para cada paso | El cliente sigue iniciando conversaciones con ADÁN después del lanzamiento, no solo antes |
| 7 — Escalamiento | **Ambicioso** | Este Nivel es sobre crecimiento estructural (AD-005 §5, Ley 4) y horizontes nuevos (AD-000 §5, otros puntos de entrada) — el momento de pensar en grande, con datos que ya lo respaldan | **Estancado o satisfecho** — la experiencia nunca debe transmitir "ya llegaste", porque AD-005 §5 (Ley 10) establece que el ciclo continúa, nunca termina en una línea | El cliente formula preguntas sobre expansión, nuevos mercados o estructura futura sin que ADÁN se las plantee primero |

---

## 2. Principios narrativos transversales

- **Tono** (hereda AD-001 §16 sin modificarlo): profesional, claro, nunca alarmista, nunca artificialmente entusiasta. Las Siete Emociones Objetivo se producen dentro de ese tono, no violándolo — "inspirado" y "emocionado" no significan exclamaciones ni lenguaje de venta.
- **Ritmo narrativo:** cada Nivel abre reconociendo qué ya se sabe (Regla 1.8 de AD-002, AD-CMP-04) antes de pedir algo nuevo — nunca empieza en blanco. Cierra con una síntesis explícita de qué cambió (conectando directamente con las tres preguntas de AD-FUNC-01 §0).
- **Cuándo se activa cada elemento de experiencia:** ligado al Master Orchestration Flow de AD-FUNC-02 §3 — la experiencia no introduce momentos propios fuera de esa secuencia ya definida (ej. no se "celebra" en medio de una deliberación de Board sin resolver).
- **Punto de integración conceptual con voz:** cuando la interacción usa voz (AD-INT-02, ARQAI), el tono vocal debe reflejar la misma emoción objetivo del Nivel activo — este documento fija cuál es esa emoción; AD-INT-02 decide cómo se logra vocalmente.

---

## 3. Verificación contra el Criterio de Existencia (AD-004 v1.1 §3.1)

Aplicado a este documento mismo, no solo exigido a otros: ¿modifica el Gemelo Digital, mejora el conocimiento del cliente, o produce evidencia útil? Experience Engine no modifica el Gemelo Digital directamente ni produce evidencia por sí mismo — su contribución es la segunda condición: **mejora el conocimiento del cliente al hacer que la evidencia y las decisiones de cada Nivel (que sí modifican el Gemelo Digital y sí producen evidencia, per AD-FUNC-01) se comuniquen de una forma que el cliente realmente internaliza**, en vez de una forma que produce fatiga o desconexión. Pasa el criterio como amplificador de las otras Funcionalidades, no como generador independiente de valor — distinción que AD-FUNC-04 (Gamification Engine) deberá sostener también.

---

## Dependencias

- AD-001 Product DNA §14, §16 (cómo debe sentirse el usuario, tono)
- AD-FUNC-01 Los 7 Niveles (las tres preguntas de cada Nivel, fuente de las emociones objetivo)
- AD-FUNC-02 Board Room §3 (Master Orchestration Flow, secuencia sobre la que se activa la experiencia)
- AD-CMP-01 Comportamiento de Progresión entre Niveles

## Documentos relacionados

- AD-FUNC-04 Gamification Engine — implementa mecánicas concretas al servicio de estas emociones, no al revés
- AD-UX-01 a AD-UX-12 — toda decisión visual debe justificarse contra la tabla de la sección 1
- AD-INT-02 Integración ARQAI — tono vocal alineado a la emoción objetivo del Nivel activo

## Impacto sobre otros módulos

1. AD-FUNC-04 no puede diseñar una mecánica de gamificación que no esté justificada contra una de las Siete Emociones Objetivo.
2. Todo AD-UX que diseñe una vista de Nivel debe declarar explícitamente a qué fila de la tabla de la sección 1 sirve.
3. Las "señales de que se logró" (columna final de la sección 1) son candidatas directas a instrumentación real en AD-ARQ/AD-OPS — hoy son cualitativas, no medidas.

## Riesgos

- **Riesgo de que las emociones objetivo se conviertan en checklist superficial** ("agregar una animación de 'inspiración' en Nivel 2") en vez de gobernar decisiones de fondo — mitigado por la sección 0, que exige justificar cada decisión de interfaz contra la emoción, no decorar con ella.
- **Riesgo de que las señales de logro (sección 1) sean difíciles de medir en la práctica** hasta que exista telemetría real (Fase 2, Arquitectura) — son señales cualitativas de diseño, no KPIs todavía.

## Preguntas abiertas

Ninguna nueva.

## Decisiones pendientes

Ninguna decisión de negocio pendiente en este documento.

## Historial de cambios

| Versión | Fecha | Cambio | Motivo |
|---|---|---|---|
| v1.0 | 2026-07-14 | Creación inicial: Siete Emociones Objetivo (una por Nivel), cada una justificada contra evidencia existente, con su anti-emoción explícita y señal cualitativa de logro. Principios narrativos transversales. Verificación contra el Criterio de Existencia | Tercer documento de la categoría Funcionalidades |
