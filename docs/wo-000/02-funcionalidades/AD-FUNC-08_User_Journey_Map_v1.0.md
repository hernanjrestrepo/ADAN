---
Código: AD-FUNC-08
Nombre: User Journey Map
Versión: v1.0
Estado: Construido y autoauditado. Congelado bajo la metodología "se construye, se autoaudita, se congela, se continúa"
Confidence Level: 45%
Fecha: 2026-07-17
Responsable (autor): Célula D (Claude Code), WO-000 Sprint 3
Aprobador: Hernán / Junta Directiva (validación en el próximo Gate Review)
---

# AD-FUNC-08 — User Journey Map

> Mapea el recorrido completo del cliente — descubrimiento, onboarding, uso, adopción, expansión, renovación, embajador (mandato del Plan Maestro de Ejecución, WO-000 Sprint 3). No inventa una taxonomía nueva de etapas: se construye **sobre** la Identidad Progresiva ya fijada en AD-FUNC-06 §3.1, que es la misma progresión vista desde el ángulo de la relación (Anónimo→...→Embajador). Este documento la ve desde el ángulo del comportamiento y el producto: qué hace el cliente, qué siente, en qué touchpoint, y qué se mide, en cada etapa.

**Nivel de contenido:** el mapeo 1:1 entre etapas de journey e Identidad Progresiva (sección 1), y la herencia de emociones ya fijadas por AD-FUNC-03 sin inventar nuevas (sección 3), son Principio Permanente. Los touchpoints y métricas específicas por etapa (sección 4) son Decisión de Diseño, sujetas a AD-004 §1.

---

## 0. Por qué no hay una taxonomía de etapas nueva

Verificación contra el Principio de Emergencia, antes de escribir una sola etapa: AD-FUNC-06 §3.1 ya fijó una escalera de 7 estados de relación derivados (Anónimo → Visitante → Usuario → Responsable de Empresa → Líder Activo → Cliente Activo → Embajador), cada uno habilitado por un hito de evidencia real. El journey de 7 etapas que pide este Sprint (Descubrimiento → Onboarding → Uso → Adopción → Expansión → Renovación → Embajador) es la **misma progresión**, descrita desde el ángulo del comportamiento observable en vez del estado de relación. Construir dos escaleras paralelas habría duplicado exactamente lo que la Regla de Economía Conceptual prohíbe. Este documento las une:

| Etapa de Journey | Identidad Progresiva equivalente (AD-FUNC-06 §3.1) | Qué ocurre |
|---|---|---|
| **Descubrimiento** | Anónimo → Visitante | La persona conoce ADÁN, sin registro todavía |
| **Onboarding** | Visitante → Usuario | Cubierto en su totalidad por AD-FUNC-06 — este documento no repite su contenido, lo referencia |
| **Uso** | Usuario → Responsable de Empresa | Niveles 1-5 (AD-FUNC-01) — construcción del Diagnóstico, Plan, MVP, Validación |
| **Adopción** | Responsable de Empresa → Líder Activo | Primera Decisión de Negocio real, primer Entregable prometido y cumplido (AD-FUNC-06 §3.1) |
| **Expansión** | Líder Activo → Cliente Activo | Nivel 6-7 (Lanzamiento, Escalamiento) — Estrategias de crecimiento del Motor de Estrategias Empresariales (AD-FUNC-05) |
| **Renovación** | Cliente Activo (sostenido) | Continuidad de la relación — el mecanismo de suscripción/facturación concreto es materia de negocio, fuera de esta especificación de producto (ver Decisiones pendientes) |
| **Embajador** | Embajador | Igual que en AD-FUNC-06 — el mecanismo de referido queda fuera de esta especificación (WO-100) |

---

## 1. Perfiles del recorrido — variación, no bifurcación

El índice original (v3.1) pide distinguir el journey por "técnico vs. no técnico" e "individual vs. institucional". Estas variables **no crean journeys distintos** — modifican el touchpoint y el canal, nunca la secuencia de 7 etapas ni las emociones que le corresponden a cada una. Esto ya está resuelto por AD-FUNC-06 §3.2 (Onboarding independiente del canal: voz, texto, documento, audio, video, imagen) — un perfil técnico puede preferir documento/API; uno no técnico, voz o texto guiado; uno institucional puede llegar vía un Punto de Entrada distinto del Ecosistema (AD-000 §5) en vez de autoregistro directo. Ninguna de estas variaciones reabre AD-FUNC-01 ni AD-FUNC-06.

---

## 2. Las 7 etapas

### Descubrimiento
- **Qué hace el cliente:** conoce ADÁN por cualquier punto de entrada del Ecosistema Paradixe (AD-000 §5) — no necesariamente por búsqueda directa de ADÁN.
- **Emoción:** no gobernada por AD-FUNC-03 (esa especificación empieza en Nivel 1) — se rige por el principio general de AD-001 §14, confianza calmada, nunca urgencia artificial, incluso en un anuncio o landing.
- **Touchpoint:** variable, fuera del alcance de esta Funcionalidad (marketing/canales, WO-100).
- **Métrica:** fuera de alcance de producto — pertenece a instrumentación de marketing.

### Onboarding
- Cubierto en su totalidad por **AD-FUNC-06** — Prueba del Minuto Cero, captura mínima, recuperación de abandono, tiempo objetivo <30 segundos. Este documento no repite ese contenido.

### Uso (Niveles 1-5)
- **Qué hace el cliente:** recorre Los 7 Niveles desde El Dolor hasta Validación Simulada (AD-FUNC-01).
- **Emoción por Nivel:** heredada sin cambios de AD-FUNC-03 — Comprendido (N1), Inspirado por la claridad (N2), Seguro (N3), Emocionado con base real (N4), Desafiado no amenazado (N5).
- **Touchpoint:** Board Room (AD-FUNC-02) en cada punto de decisión relevante.
- **Métrica:** los 6 Scores de diagnóstico secuencial de AD-FUNC-07 (Problem, Solution, Business, Product, Market, Execution Score).

### Adopción
- **Qué hace el cliente:** toma su primera Decisión de Negocio real con evidencia detrás (AD-FUNC-02 §2.5); recibe su primer Entregable/Diagnóstico prometido y cumplido.
- **Emoción:** hereda de Nivel 3-4 según en qué Nivel ocurra el hito — no introduce una emoción nueva.
- **Touchpoint:** el hito de confianza "Líder Activo" de AD-FUNC-06 §3.1.
- **Métrica:** Score del Responsable (AD-FUNC-07 §3) empieza a acumular evidencia real.

### Expansión (Nivel 6-7)
- **Qué hace el cliente:** opera en el mundo real (Nivel 6) y escala (Nivel 7); consume Estrategias del Motor de Estrategias Empresariales (AD-FUNC-05) — contratar, automatizar, internacionalizar, cambiar modelo de negocio, según su Brecha real.
- **Emoción:** Acompañado (N6), Ambicioso (N7) — AD-FUNC-03, sin cambios.
- **Touchpoint:** Motor de Estrategias Empresariales (AD-FUNC-05), presentando Estrategias competidoras en el Board Room.
- **Métrica:** Venture Score (AD-FUNC-07 §4) se vuelve la métrica de seguimiento central, coherente con AD-FUNC-01 §Nivel 7.

### Renovación
- **Qué hace el cliente:** sostiene la relación en el tiempo — no hay un "Nivel 8" (AD-FUNC-01 congelado en 7), el acompañamiento es continuo desde Nivel 6/7 (AD-FUNC-01 §Nivel 7: "continuo, no secuencial").
- **Emoción:** la misma "confianza calmada" que gobierna toda la relación (AD-001 §14) sostenida en el tiempo, no una emoción nueva de "cliente que paga".
- **Touchpoint / métrica:** el mecanismo concreto de suscripción, facturación y condiciones de renovación es una decisión de negocio, no de producto — **queda explícitamente fuera de esta especificación**, es materia de WO-100 (Business Architecture), igual que el mecanismo de "Embajador" ya quedó fuera en AD-FUNC-06.

### Embajador
- Igual que AD-FUNC-06 §3.1 — el hito narrativo existe, el mecanismo concreto (si lo hay) queda fuera de esta especificación de producto, con el mismo riesgo ya señalado de evitar cualquier patrón de esquema multinivel.

---

## 3. Verificación contra la Regla de Entidades y el Principio de Emergencia

Ninguna entidad nueva, ninguna emoción nueva, ningún Score nuevo. Las 7 etapas son una **vista** sobre construcciones ya existentes (Identidad Progresiva de AD-FUNC-06, Niveles de AD-FUNC-01, Emociones de AD-FUNC-03, Scores de AD-FUNC-07, Estrategias de AD-FUNC-05) — no un objeto de datos ni un mecanismo propio.

## 4. Verificación contra el Criterio de Existencia (AD-004 v1.1 §3.1)

| Condición | ¿Se cumple? | Cómo |
|---|---|---|
| ¿Modifica el Gemelo Digital? | Indirectamente | El journey en sí no modifica nada — orquesta el orden de lectura de lo que ya modifican AD-FUNC-01/05/06/07 |
| ¿Mejora el conocimiento del cliente? | Sí | El cliente (y el equipo de producto) entiende en qué punto del recorrido está, sin ambigüedad, en cualquier momento |
| ¿Produce evidencia útil para la siguiente decisión? | Sí | Permite a AD-UX y AD-FUNC-09 saber exactamente qué touchpoint y qué métrica corresponde a cada etapa, sin inventar una nueva por Funcionalidad |

---

## 5. Autoauditoría obligatoria (10 preguntas)

1. **¿Contradice AD-000/AD-001/AD-002?** No.
2. **¿Todo concepto nuevo está justificado?** No se introduce ningún concepto nuevo — verificado explícitamente en sección 3.
3. **¿Hay duplicación?** Se verificó explícitamente contra AD-FUNC-06 §3.1 antes de escribir una sola etapa (sección 0) — es la razón de ser de este documento, evitar la duplicación, no cometerla.
4. **¿Impacto sobre documentos futuros?** AD-UX-completo debe usar esta tabla de 7 etapas como columna vertebral de navegación. AD-FUNC-09 consume las métricas por etapa como fuente de señales de aprendizaje.
5. **¿Riesgo arquitectónico nuevo?** Ninguno — es una capa de lectura, no de escritura.
6. **¿Confidence Level honesto?** 45% — el mapeo es sólido contra documentos ya aprobados, pero "Renovación" depende de una decisión de negocio (WO-100) que todavía no existe.
7. **Prueba "si desapareciera":** cada Funcionalidad seguiría funcionando por separado, pero nadie tendría el mapa de cómo se conectan en una sola narrativa de cliente.
8. **Prueba "10 años":** las 7 etapas describen un patrón universal de relación comercial (descubrir, incorporarse, usar, comprometerse, crecer, sostener, recomendar) — no depende de tecnología.
9. **¿Colisiones de nombre verificadas?** Sí — se verificó que ninguna de las 7 etapas reabre o duplica Los 7 Niveles (son ejes distintos: Niveles = madurez de la empresa dentro de "Uso"; Etapas = relación completa incluyendo antes y después de "Uso").
10. **¿Autoauditoría entregada junto al documento?** Sí.

---

## Dependencias

- AD-FUNC-06 §3.1 (Identidad Progresiva — base de las 7 etapas, no duplicada)
- AD-FUNC-01 (Los 7 Niveles — corresponden a la etapa "Uso")
- AD-FUNC-03 (Emociones — heredadas sin cambios)
- AD-FUNC-05 (Estrategias — corresponden a "Expansión")
- AD-FUNC-07 (Scores — métricas por etapa)
- AD-000 §5 (Puntos de entrada del Ecosistema — "Descubrimiento")
- AD-004 v1.1 §3.1 (Criterio de Existencia)

## Documentos relacionados

- AD-FUNC-09 Learning Engine (Sprint 4 de esta WO) — consume métricas por etapa
- AD-UX (Fase 2) — navegación completa del producto según estas 7 etapas
- WO-100 Business Architecture (futura) — mecanismo de Renovación (suscripción/facturación) y de Embajador (referidos)

## Impacto sobre otros módulos

1. Todo AD-UX debe usar esta tabla como referencia de navegación de alto nivel — nunca inventar una etapa adicional sin verificar primero contra este documento.

## Riesgos

- **Riesgo de que "Renovación" se trate como decisión de producto cuando es de negocio** — este documento lo señala explícitamente para prevenir esa confusión.
- Heredado de AD-FUNC-06: riesgo del mecanismo de "Embajador" (esquema multinivel).

## Preguntas abiertas

Ninguna nueva.

## Decisiones pendientes

- Mecanismo de Renovación (suscripción/facturación) — WO-100, no bloquea este documento.
- Mecanismo de Embajador (heredado de AD-FUNC-06) — WO-100.

## Historial de cambios

| Versión | Fecha | Cambio | Motivo |
|---|---|---|---|
| v1.0 | 2026-07-17 | Creación inicial: las 7 etapas del journey mapeadas 1:1 contra la Identidad Progresiva ya fijada en AD-FUNC-06 §3.1, sin crear una segunda taxonomía; touchpoints y métricas por etapa heredados de AD-FUNC-01/03/05/07 sin duplicación | WO-000 Sprint 3 del Plan Maestro de Ejecución ADÁN v1.0 |
