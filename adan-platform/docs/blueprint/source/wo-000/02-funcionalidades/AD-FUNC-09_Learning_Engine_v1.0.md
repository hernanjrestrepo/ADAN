---
Código: AD-FUNC-09
Nombre: Learning Engine
Versión: v1.0
Estado: Construido y autoauditado. Congelado bajo la metodología "se construye, se autoaudita, se congela, se continúa"
Confidence Level: 38%
Fecha: 2026-07-17
Responsable (autor): Célula D (Claude Code), WO-000 Sprint 4
Aprobador: Hernán / Junta Directiva (validación en el próximo Gate Review)
---

# AD-FUNC-09 — Learning Engine

> Cierra el loop completo que el propio Plan Maestro de Ejecución declara como el corazón del producto (§1): *Empresa nueva → Onboarding → Diagnóstico → Board Room → Estrategia → Plan → Seguimiento → Aprendizaje → Actualización del Gemelo Digital.* Este documento no inventa el aprendizaje desde cero — recoge y unifica cuatro semillas ya sembradas, cada una en el documento que la originó, y especifica el mecanismo que faltaba: cómo se capturan las señales, qué ajustan, qué recuerda ADÁN, y qué límites tiene ese aprendizaje. Es, por mandato del propio Plan Maestro, el documento más grande de esta WO — dividido en 10 secciones numeradas para que ninguna se pierda en el volumen.

**Nivel de contenido:** el principio de que ADÁN aprende de las decisiones (no solo del éxito) y las Salvaguardas de la sección 6 son Principio Permanente — ninguna presión comercial o técnica futura puede levantarlas sin una nueva versión de este documento. El mecanismo concreto de agregación entre empresas (sección 5, Playbook) y los pesos/umbrales de recalibración son Decisión de Diseño, sujetos a AD-004 §1 y, sobre todo, a evidencia real todavía inexistente.

---

## 0. Las cuatro semillas que este documento hereda, no inventa

Verificación explícita antes de escribir una sola línea nueva — ninguna de las siguientes ideas nace aquí, todas ya estaban registradas:

1. **AD-FUNC-02 §2.5** — "ADÁN aprende de las decisiones, no solo del éxito." Cuando el cliente decide distinto a lo recomendado, se registran 6 campos (incluida "Responsabilidad asumida"), con 5 preguntas de ejemplo que el Learning Engine debería poder responder algún día: ¿en qué tipo de empresas el Board suele equivocarse? ¿qué perfiles de empresarios toman mejores decisiones contra la recomendación? ¿qué modelos LLM sobreestiman ciertos riesgos? ¿en qué industrias conviene ser más conservador? ¿cuándo un fundador debe ignorar la recomendación del sistema?
2. **AD-FUNC-05 §10** — el ciclo Brecha → Capacidad → Estrategia elegida → Implementación → Resultado → ROI real → Desviación frente al ROI esperado → Aprendizaje → Recalibración del Confidence Level.
3. **AD-FUNC-06 §10.1** — el Playbook Empresarial, registrado explícitamente como activo futuro, no construido por falta de evidencia real.
4. **AD-FUNC-07 §5** — Score por Estrategia, el mecanismo concreto que trackea el desempeño real de una Estrategia ejecutada en el tiempo.

Este documento es donde las cuatro convergen.

---

## 1. Qué es esta Funcionalidad

La capa que compara lo que ADÁN esperaba con lo que realmente ocurrió, en cualquier punto del ciclo completo (Onboarding, Diagnóstico, Board Room, Estrategia, Plan, Seguimiento), y ajusta tres cosas —nunca más de tres, por disciplina explícita— a partir de esa comparación: **Scores** (su Confidence Level), **priors del Motor de Estrategias** (qué tan probable es que un tipo de Estrategia funcione para un perfil de Empresa dado), y el **Gemelo Digital** (que registra el propio acto de aprendizaje como evidencia, Patrón C, AD-008).

Lo que NO es:

- No es una funcionalidad que decide por el cliente — ajusta cómo ADÁN estima y recomienda, nunca ejecuta nada por sí sola (hereda sin excepción AD-001 §5 y AD-FUNC-02 §2).
- No es el Playbook Empresarial ya construido — es donde el Playbook eventualmente vivirá, cuando exista evidencia real suficiente (sección 5).
- No es un mecanismo que optimiza tiempo en plataforma ni engagement — la Regla Anti-Manipulación de AD-FUNC-04 §3 aplica aquí con la misma fuerza (sección 6).

---

## 2. Señales capturadas

| Señal | De dónde viene | Qué revela |
|---|---|---|
| Desacuerdo cliente-Board | AD-FUNC-02 §2.5 | Cuándo la evidencia del Board no convenció, y qué pasó después |
| Desviación ROI esperado vs. ROI real | AD-FUNC-05 §10 | Qué tan calibradas están las estimaciones de una Estrategia |
| Evolución de Score por Estrategia | AD-FUNC-07 §5 | Desempeño real de una Estrategia ejecutada, en el tiempo, no solo al cierre |
| Simulación de Impacto vs. resultado real | AD-FUNC-05 §7 | Qué tan bien predice el modelo de simulación antes de comprometer recursos reales |
| Transiciones y abandonos del Journey | AD-FUNC-08 | En qué etapa el cliente se atasca o abandona, más allá de Onboarding (que ya tiene su propio mecanismo de recuperación, AD-FUNC-06 §3.3) |
| Recalibración de Score del Responsable | AD-FUNC-07 §3 | Si el track record de una persona predice mejor sus futuras decisiones |

Ninguna señal es nueva como concepto — todas ya estaban definidas en su documento de origen. Esta sección solo las reúne como el conjunto completo de entradas del Learning Engine.

---

## 3. Loops de aprendizaje — qué ajusta, y solo eso

Tres loops, ninguno más, por disciplina explícita (evitar que "aprendizaje" se convierta en una excusa para tocar cualquier cosa sin evidencia):

### 3.1 Recalibración de Confidence Level
Cuando la Desviación ROI esperado/real (o cualquier otra señal de la sección 2) muestra un patrón repetido, el Confidence Level de futuras estimaciones del mismo tipo se ajusta — nunca el Impacto Esperado en sí, que sigue siendo un juicio caso por caso (AD-FUNC-05 §6, nunca se fusionan). Mecanismo: mismo proceso de evidencia ya fijado en AD-CMP-05, aplicado ahora a un historial de predicciones en vez de a una conversación.

### 3.2 Priors del Motor de Estrategias
Cuando existe evidencia agregada suficiente (sección 5, umbral explícito, no arbitrario), la Probabilidad de éxito que AD-FUNC-05 §8 estima para una Estrategia candidata puede informarse con el patrón aprendido — nunca sustituye el análisis caso por caso, lo pondera. Sin evidencia agregada suficiente, este loop está inactivo por diseño, no hay valor por defecto que aparente aprendizaje donde no lo hay (mismo Principio de Humildad Intelectual de AD-001 §6.1).

### 3.3 Registro en el Gemelo Digital
Todo evento de aprendizaje (una recalibración, una desviación detectada) se registra como Patrón C (Registro Permanente, AD-008) — nunca sobreescribe el historial anterior, se acumula. Esto es lo que permite, sin mecanismo adicional, reconstruir *cuándo* ADÁN aprendió algo y *por qué* — coherente con AD-002 regla 1.6 (toda IA debe justificar).

---

## 4. Memoria de aprendizaje — dos escalas, nunca fusionadas

- **Por Empresa:** qué Estrategias se intentaron, cuáles funcionaron, cuáles no, y por qué —consultable por los Agentes del Board Room antes de recomendar de nuevo a la misma Empresa. No es una entidad nueva: es una consulta sobre el historial ya versionado de Decisión de Negocio, Score por Estrategia y Suceso Empresarial de esa Empresa (Patrón C, AD-008).
- **Entre Empresas (agregada y anonimizada):** el Playbook Empresarial — sección 5.

Nunca se fusionan: lo que funcionó para una Empresa específica no se convierte automáticamente en un patrón general sin pasar por el umbral de evidencia agregada de la sección 5.

---

## 5. El Playbook Empresarial — especificación del mecanismo (sin construirlo todavía)

Este es el punto exacto donde la semilla de AD-FUNC-06 §10.1 se especifica, no se construye. La diferencia importa: especificar el mecanismo permite que WO-008 (Learning Engine v1) y futuras WOs sepan qué construir cuando haya evidencia; construirlo ahora, sin datos reales, violaría la misma Economía Conceptual que ya se ha aplicado en todo este árbol.

**Condición de activación:** un patrón (ej. "combinación de Estrategias X para Empresas de perfil Y") solo se admite al Playbook cuando existe evidencia agregada de **al menos N Empresas reales** con resultado real medido — N es Decisión de Diseño de AD-ARQ-10, no de este documento, precisamente porque hoy no hay datos para fijarlo con evidencia.

**Qué mide un patrón, cuando exista:** perfil de Empresa (Etapa del Ciclo de Vida, Madurez, sector — AD-005 §4), combinación de Estrategias ejecutadas (AD-FUNC-05 §5.1), resultado agregado (Δ en Venture Score o en un Indicador específico), Confidence Level del patrón mismo (nunca un patrón "seguro" sin declarar cuántos casos lo sostienen).

**Verificación contra la Regla de Entidades:** si el Playbook, una vez que exista evidencia real, necesita una entidad propia (ej. "Patrón de Éxito"), esa entidad se crea en una futura versión de AD-005 o AD-006 —nunca aquí, y nunca antes de tener el primer caso real que la justifique (mismo criterio ya aplicado en AD-FUNC-06 §10.1).

---

## 6. Límites y salvaguardas (Principio Permanente, sin excepción)

1. **El Learning Engine nunca ejecuta.** Ajusta Confidence Level y priors internos de estimación — nunca una Decisión de Negocio, nunca una Estrategia. La autoridad de ejecución sigue siendo, sin excepción, del cliente (AD-001 §5, AD-FUNC-02 §2, AD-FUNC-05 §9).
2. **Nunca optimiza tiempo en plataforma ni engagement.** Aplica, sin relajarse, la prueba más general de AD-FUNC-04 §3: ninguna recalibración puede aumentar el uso de ADÁN sin aumentar evidencia real en el Gemelo Digital.
3. **Nunca trata a una Empresa como intercambiable con otra.** Un patrón del Playbook informa, no decide — la recomendación final siempre pasa por el análisis específico de AD-FUNC-05 sobre la Empresa real (AD-001 §5: "ADÁN nunca trata a dos empresas como intercambiables").
4. **Nunca aprende de una sola conversación como si fuera evidencia suficiente** — hereda sin excepción la jerarquía de validez de AD-CMP-05 §1.
5. **Ningún patrón se declara "seguro" sin su Confidence Level y el número de casos que lo sostienen, visible.** Nunca se oculta que un patrón está basado en pocos casos.
6. **El aprendizaje de desacuerdos (semilla 1, sección 0) nunca se usa para presionar al cliente a seguir la recomendación del Board la próxima vez** — se usa para mejorar la evidencia que el Board presenta, nunca para reducir la autoridad de ejecución del cliente.

---

## 7. Verificación contra la Regla de Entidades y el Principio de Emergencia

Ninguna entidad nueva se crea en esta versión. La Memoria de aprendizaje por Empresa es una consulta sobre entidades ya existentes (Decisión de Negocio, Score, Suceso Empresarial — Patrón C de AD-008). El Playbook Empresarial se especifica como mecanismo futuro, explícitamente sin construirse (sección 5) — su eventual entidad, si resulta necesaria, se decide en una futura versión de AD-005/006 contra evidencia real, nunca por adelantado.

## 8. Verificación contra el Criterio de Existencia (AD-004 v1.1 §3.1)

| Condición | ¿Se cumple? | Cómo |
|---|---|---|
| ¿Modifica el Gemelo Digital? | Sí | Todo evento de aprendizaje se registra como Patrón C, acumulativo |
| ¿Mejora el conocimiento del cliente? | Sí | Las recomendaciones futuras llegan mejor calibradas, con el historial real de la propia Empresa disponible para los Agentes |
| ¿Produce evidencia útil para la siguiente decisión? | Sí, por diseño — es la Funcionalidad completa dedicada exactamente a esto | — |

---

## 9. Autoauditoría obligatoria (10 preguntas)

1. **¿Contradice AD-000/AD-001/AD-002?** No — las Salvaguardas de la sección 6 son, en su mayoría, reafirmaciones más estrictas de principios ya fijados (AD-001 §5, AD-FUNC-04 §3), no reglas nuevas que puedan entrar en conflicto.
2. **¿Todo concepto nuevo está justificado?** El único mecanismo genuinamente nuevo es la condición de activación del Playbook (umbral de N Empresas) — justificado explícitamente por Economía Conceptual: sin ese umbral, cualquier caso aislado se trataría como patrón, violando el Principio de Humildad Intelectual.
3. **¿Hay duplicación?** No — las 3 secciones de loops (3.1-3.3) mapean 1:1 a las semillas ya sembradas (sección 0), sin agregar un cuarto mecanismo no solicitado.
4. **¿Impacto sobre documentos futuros?** AD-ARQ-10 debe fijar el umbral N del Playbook con datos reales. WO-008 (Learning Engine v1, este mismo plan) implementa los loops 3.1 y 3.3 primero — 3.2 (priors) queda inactivo hasta que exista evidencia agregada real.
5. **¿Riesgo arquitectónico nuevo?** Sí, el más importante de todo este documento: que la presión por demostrar "inteligencia adaptativa" empuje a activar el loop 3.2 (priors) sin el umbral de evidencia real cumplido — la sección 6 fija la barrera explícitamente por esto.
6. **¿Confidence Level honesto?** 38% — el mecanismo es coherente con todo lo ya construido, pero cero loops tienen todavía un caso real ejecutado (eso es, literalmente, el trabajo de WO-008 y WO-009 de este mismo plan).
7. **Prueba "si desapareciera":** las cuatro semillas de la sección 0 quedarían dispersas en cuatro documentos sin un mecanismo unificado que las conecte — ADÁN registraría evidencia sin nunca recalibrarse con ella.
8. **Prueba "10 años":** el principio (comparar lo esperado contra lo real, ajustar solo Confidence/priors/Gemelo, nunca ejecutar, nunca manipular) no depende de qué modelo de IA calcule las recalibraciones — es una disciplina epistémica, no una arquitectura técnica.
9. **¿Colisiones de nombre verificadas?** Sí — "Aprendizaje" no colisiona con ningún término ya fijado en AD-003; se verificó explícitamente que este documento no duplica el Playbook (lo hereda, sección 5) ni el ciclo de AD-FUNC-05 §10 (lo generaliza a las otras 3 señales, sección 2).
10. **¿Autoauditoría entregada junto al documento?** Sí.

---

## Dependencias

- AD-FUNC-02 §2.5 (semilla 1: aprendizaje de desacuerdos)
- AD-FUNC-05 §7, §10 (semilla 2: ciclo ROI esperado/real; Simulación de Impacto)
- AD-FUNC-06 §10.1 (semilla 3: Playbook Empresarial)
- AD-FUNC-07 §3, §5 (semilla 4: Score del Responsable, Score por Estrategia)
- AD-FUNC-08 (transiciones de journey como señal)
- AD-CMP-05 (jerarquía de evidencia, heredada sin duplicar)
- AD-008 (Patrón C, Registro Permanente)
- AD-FUNC-04 §3 (Regla Anti-Manipulación, reutilizada en Salvaguardas)
- AD-001 §5, §6.1 (autoridad de ejecución del cliente; Humildad Intelectual)
- AD-004 v1.1 §3.1 (Criterio de Existencia)

## Documentos relacionados

- AD-ARQ-10 (Fase 2) — umbral N del Playbook, pesos de recalibración
- AD-CMP-01 a 06 — consumen memoria de aprendizaje por Empresa donde aplique

## Impacto sobre otros módulos

1. WO-008 de este plan implementa los loops 3.1 y 3.3 en su v1; el loop 3.2 (priors) queda explícitamente fuera del alcance de v1 hasta cumplir el umbral de evidencia de la sección 5.
2. Ningún AD-ARQ puede activar el loop 3.2 sin declarar explícitamente el umbral N y el número real de casos que lo sostienen en ese momento.

## Riesgos

- **Riesgo de activar el Playbook prematuramente por presión de valorización** — mismo riesgo ya señalado en AD-FUNC-06 §10.1, reforzado aquí con una condición de activación explícita y verificable (sección 5).
- **Riesgo de que el loop 3.1 (recalibración de Confidence) se perciba como "la IA se equivocó" en vez de "la estimación se ajustó con más evidencia"** — cuestión de comunicación de producto, no de este documento, señalada para AD-UX.

## Preguntas abiertas

Ninguna nueva.

## Decisiones pendientes

- Umbral N de evidencia agregada para activar un patrón del Playbook — AD-ARQ-10, contra datos reales.
- Si el Playbook requiere entidad propia una vez alcanzado el umbral — futura versión de AD-005/006, no aquí.

## Historial de cambios

| Versión | Fecha | Cambio | Motivo |
|---|---|---|---|
| v1.0 | 2026-07-17 | Creación inicial: unifica las 4 semillas ya sembradas (AD-FUNC-02 §2.5, AD-FUNC-05 §10, AD-FUNC-06 §10.1, AD-FUNC-07 §5) en 3 loops de aprendizaje (recalibración de Confidence, priors de Estrategia, registro en Gemelo Digital), memoria por Empresa vs. agregada (Playbook, mecanismo especificado sin construirse), y 6 Salvaguardas permanentes que impiden ejecución autónoma, optimización de engagement, y activación prematura del Playbook | WO-000 Sprint 4 del Plan Maestro de Ejecución ADÁN v1.0 — documento más grande de la WO, dividido en 10 secciones por mandato explícito |
