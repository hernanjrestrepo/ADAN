---
Código: AD-FUNC-01
Nombre: Los 7 Niveles (PRD Maestro)
Versión: v1.0 — APROBADA Y CONGELADA
Estado: Aprobado y congelado. Los 7 Niveles (sección 1) quedan cerrados de forma definitiva — el Board indicó explícitamente que no se volverá a discutir 6 vs. 7
Confidence Level: 58%
Fecha: 2026-07-14
Responsable (autor): CC (Claude Code)
Aprobador: Hernán / Junta Directiva (validación en el próximo Gate Review)
---

# AD-FUNC-01 — Los 7 Niveles

> Primer documento de la categoría Funcionalidades — y el primero evaluado bajo el Criterio de Existencia de AD-004 v1.1 §3.1. No describe siete pantallas ni siete formularios. Describe un proceso de transformación empresarial: en cada Nivel, algo cambia de verdad — lo que ADÁN sabe de la Empresa, lo que el cliente entiende de su propio negocio, y lo que queda escrito de forma permanente en el Gemelo Digital. Un Nivel que no produce las tres cosas no es un Nivel válido bajo esta especificación.

**Nivel de contenido:** mixto. La estructura de tres preguntas y el requisito de avance por evidencia (sección 0) son Principio Permanente. El contenido específico de cada Nivel es Decisión de Diseño, sujeto a AD-004 §1 (el número y orden de Niveles puede evolucionar sin romper AD-CMP-01).

---

## 0. El principio de diseño: tres preguntas por Nivel

Cada uno de los siete Niveles se especifica respondiendo, sin excepción:

1. **¿Qué descubre ADÁN sobre la Empresa en este Nivel?** — la evidencia nueva que entra al sistema.
2. **¿Qué aprende el cliente en este Nivel?** — el conocimiento verificable que el cliente no tenía antes de empezar.
3. **¿Qué cambia en el Gemelo Digital cuando el Nivel termina?** — qué entidades de AD-005/AD-006 se crean, actualizan o versionan.

Esta estructura es la aplicación directa del Criterio de Existencia (AD-004 v1.1 §3.1) al documento que más lo necesitaba: si un Nivel no puede responder las tres preguntas con contenido real, ese Nivel es una pantalla decorativa, no una etapa de transformación — y esta especificación no lo admite como tal.

---

## 1. Resolución de la pregunta abierta: ¿seis o siete Niveles?

Abierta desde AD-003 §Preguntas Abiertas. Se resuelve aquí con la evidencia disponible, no por conveniencia editorial, como esa misma pregunta exigía:

- La comunicación de lanzamiento a Caribe Tech (Chat 1.docx) dice "6 niveles estratégicos" y termina en "Lanzamiento y operación real del proyecto" — es una publicación de marketing, optimizada para brevedad, la misma clase de comunicación que en otras partes de Chat 1.docx afirmó cifras sin evidencia verificable (ej. "500 usuarios" sin campañas activas).
- La conversación de arquitectura del Workspace Principal (Chat 1.docx, posterior y más deliberada) diseña explícitamente un **Nivel 7 — Escalamiento**, con contenido de interfaz propio y distinto de Lanzamiento: *"Debe mostrar: KPIs, crecimiento, nuevas oportunidades, expansión, optimización."*
- La Declaración de Misión de AD-001 incluye **"escalar"** como uno de sus seis verbos, distinto de **"operar"** — si Lanzamiento (Nivel 6) ya cubriera "operar", hace falta un Nivel propio para "escalar", que es exactamente lo que la fuente de arquitectura describe.

**Resolución: siete Niveles.** Lanzamiento (operar) y Escalamiento (escalar) son fases distintas con objetivos distintos — la primera valida que el negocio funciona con clientes reales; la segunda gestiona su crecimiento estructural (AD-005 §5, Ley 4: crisis de crecimiento de Greiner). Se prioriza la fuente más detallada y deliberada sobre la más breve y promocional.

---

## 2. Los Siete Niveles

### Nivel 1 — El Dolor (Validación del Problema)

- **¿Qué descubre ADÁN?** Si el problema declarado es real, urgente y afecta a más personas que al propio fundador — validado contra CSI (tendencias, foros, estudios de mercado), no solo contra la palabra del cliente. El perfil del Usuario Principal (motivación, experiencia previa, recursos disponibles).
- **¿Qué aprende el cliente?** Si su idea resuelve un problema real y digno de perseguir, o si necesita pivotar antes de invertir más tiempo o capital — la primera decisión "go/no-go" honesta de todo el proceso.
- **¿Qué cambia en el Gemelo Digital?** Nace el Gemelo Digital (AD-CMP-06, Ley de Origen). Se registra la Narrativa Fundacional inicial, el Usuario Principal, la primera Decisión de Negocio (validar o pivotar), y el primer Score (Problem Score) con su Confidence Level.
- **Entregable:** Diagnóstico del Dolor — problema, evidencia externa, perfil del emprendedor.
- **Avance (AD-CMP-01):** requiere evidencia externa suficiente + aprobación explícita del Usuario Principal de que el diagnóstico refleja su realidad.

### Nivel 2 — Propuesta de Valor y Diseño Estratégico

- **¿Qué descubre ADÁN?** Cómo se diferencia la propuesta frente a alternativas existentes (Competidor, Mercado ya registrados) y qué tan defendible es esa diferenciación.
- **¿Qué aprende el cliente?** Si su solución original necesita ajustarse — la propuesta puede evolucionar aquí, no es un trámite (Chat 1.docx: "este nivel no es un mero trámite... la idea inicial puede evolucionar").
- **¿Qué cambia en el Gemelo Digital?** Se registran Mercado, Competidor(es), y una primera versión de Producto/Servicio. Solution Score.
- **Entregable:** Propuesta de Valor formal, matriz comparativa contra el mercado.
- **Avance:** evidencia de al menos una validación real con clientes potenciales (no solo análisis interno) + aprobación del Usuario Principal.

### Nivel 3 — Plan de Negocios y Estructura Empresarial

- **¿Qué descubre ADÁN?** La estructura legal y tributaria óptima según el mercado objetivo (vía CSI), proyecciones financieras verificadas contra benchmarks reales (vía EVA, evitando que el cliente "sueñe con cifras que no son"), y una estrategia de marketing con costos de adquisición realistas.
- **¿Qué aprende el cliente?** Cuánto capital realmente necesita, qué estructura legal le conviene, y cuál es su estructura organizacional (incluyendo qué roles pueden ser agénticos vs. humanos).
- **¿Qué cambia en el Gemelo Digital?** Se crean Departamento y Cargo, Activo/Pasivo iniciales, Objetivo/Meta/Indicador, Documento (acta de constitución y ruta legal), Accionista/Inversionista si aplica. Business Score.
- **Entregable:** Plan de negocio, acta de constitución, organigrama híbrido, proyecciones financieras auditadas.
- **Avance:** proyecciones validadas contra benchmarks externos (no solo supuestos del cliente) + aprobación del Usuario Principal.

### Nivel 4 — Diseño y Construcción del MVP

- **¿Qué descubre ADÁN?** Qué construir exactamente (blueprint técnico), adaptado al nivel de lenguaje técnico del Usuario Principal (ya perfilado en Nivel 1).
- **¿Qué aprende el cliente?** Si el producto real que puede construirse coincide con la propuesta de valor validada, o si hace falta ajustar diseño, marca o alcance antes de comprometer recursos de construcción.
- **¿Qué cambia en el Gemelo Digital?** Producto/Servicio se actualiza a su versión de construcción; nace una Iniciativa de construcción (orquestada hacia Genexis, AD-000 §5); primer Documento de tipo blueprint técnico. Product Score.
- **Entregable:** Blueprint del MVP, mockups validados por el cliente, roadmap de desarrollo.
- **Avance:** blueprint aprobado explícitamente por el Usuario Principal antes de iniciar construcción real — nunca se construye sin aprobación (Patrón A, AD-008).

### Nivel 5 — Validación Simulada y Ajuste

- **¿Qué descubre ADÁN?** Cómo reaccionarían clientes e inversionistas simulados ante el MVP — fricciones que no eran evidentes en el diseño (AD-005 §5, conecta con Ley de Adaptación).
- **¿Qué aprende el cliente?** Dónde están los puntos débiles de su modelo antes de arriesgar capital o reputación real con clientes reales.
- **¿Qué cambia en el Gemelo Digital?** Se registran Riesgos identificados (propiedad transversal, AD-005 §3), ajustes documentados como nuevas Decisiones de Negocio. Market Score y Execution Score.
- **Entregable:** Informe de simulación, tablero de métricas simuladas, plan de ajuste.
- **Avance:** métricas simuladas dentro de parámetros aceptables + aprobación del Usuario Principal para proceder a lanzamiento real.

### Nivel 6 — Lanzamiento y Operación Real

- **¿Qué descubre ADÁN?** Cómo se comporta la Empresa en el mundo real — los primeros Sucesos Empresariales genuinos, primeros Ingresos y Gastos reales, primeros Clientes Finales reales (no simulados).
- **¿Qué aprende el cliente?** Si su negocio funciona con el mercado real, la prueba que ninguna simulación puede reemplazar.
- **¿Qué cambia en el Gemelo Digital?** La Etapa del Ciclo de Vida de la Empresa (AD-005 §4) transiciona de "validada" a "operando". El Proyecto (AD-006) pasa a modo de operación continua — el límite exacto donde EVA, no ADÁN, asume la optimización financiera recurrente (AD-000 §6, AD-001 §1.1).
- **Entregable:** MVP desplegado en producción, primer ciclo de operación documentado.
- **Avance:** al menos un Suceso Empresarial real de ingreso o adquisición de cliente, registrado y verificado — no simulado.

### Nivel 7 — Escalamiento

- **¿Qué descubre ADÁN?** Patrones de crecimiento y los cuellos de botella estructurales que predice AD-005 §5 (Ley 4, crisis de coordinación de Greiner) — cuándo el mecanismo que trajo a la Empresa hasta aquí deja de escalar.
- **¿Qué aprende el cliente?** Cuándo y cómo reestructurar (nuevos Departamento/Cargo), cuándo levantar capital, y qué tan rápido está madurando realmente su organización — no solo cuánto está facturando.
- **¿Qué cambia en el Gemelo Digital?** La Velocidad de Maduración Organizacional (AD-005 §4) se vuelve la métrica central de seguimiento continuo. Pueden registrarse nuevas Iniciativas de expansión o internacionalización (AD-000 §5, otros puntos de entrada del ecosistema).
- **Entregable:** Diagnóstico de escalamiento, plan de reestructuración si aplica.
- **Avance:** no aplica en el mismo sentido que los Niveles anteriores — Nivel 7 es el punto donde el acompañamiento de ADÁN se vuelve continuo, no secuencial (conecta con AD-005 §5, Ley 10: ciclo, no línea — una Empresa puede volver a un estado de Crisis o Reinvención desde aquí, no solo avanzar).

---

## 3. Verificación contra el Criterio de Existencia (AD-004 v1.1 §3.1)

| Nivel | ¿Modifica el Gemelo Digital? | ¿Mejora el conocimiento del cliente? | ¿Produce evidencia útil? |
|---|---|---|---|
| 1 | Sí — nace el Gemelo Digital | Sí — go/no-go del problema | Sí — Problem Score |
| 2 | Sí — Mercado, Competidor | Sí — diferenciación real | Sí — Solution Score |
| 3 | Sí — Departamento, Cargo, Activo/Pasivo | Sí — capital real necesario | Sí — Business Score |
| 4 | Sí — Iniciativa de construcción | Sí — producto real vs. propuesta | Sí — Product Score |
| 5 | Sí — Riesgos registrados | Sí — puntos débiles antes del riesgo real | Sí — Market/Execution Score |
| 6 | Sí — Etapa transiciona a "operando" | Sí — prueba de mercado real | Sí — primer Suceso Empresarial real |
| 7 | Sí — Velocidad de Maduración como seguimiento continuo | Sí — diagnóstico de crecimiento | Sí — señal de crisis estructural temprana |

Los siete Niveles pasan el Criterio de Existencia sin excepción.

---

## Dependencias

- AD-CMP-01 Comportamiento de Progresión entre Niveles (regla de avance por evidencia)
- AD-CMP-05 Comportamiento de Evidencia y Scoring (qué cuenta como evidencia válida en cada Nivel)
- AD-005 Enterprise Domain Model (entidades que cada Nivel modifica)
- AD-004 v1.1 §3.1 (Criterio de Existencia)
- AD-007 Gemelo Digital, AD-008 Objetos del Sistema (Patrón A aplicado a las aprobaciones de cada Nivel)

## Documentos relacionados

- AD-FUNC-06 Onboarding (primera sesión, entra al Nivel 1)
- AD-FUNC-07 Sistema de Scoring (los Scores nombrados por Nivel se especifican ahí)
- AD-UX-05 Vista de Nivel (consume esta especificación directamente)
- WO-100 (precio por Nivel — explícitamente fuera de alcance aquí, AD-004 §1)

## Impacto sobre otros módulos

1. AD-UX-05 no puede diseñar una vista de Nivel que no refleje las tres preguntas de la sección 0.
2. AD-FUNC-07 debe definir Problem/Solution/Business/Product/Market/Execution Score consistentemente con lo que cada Nivel aquí declara que produce.
3. El precio por Nivel (WO-100, fuera de esta WO-000) debe fijarse conociendo qué evidencia y qué cambio en el Gemelo Digital compra cada pago — no un número arbitrario.

## Riesgos

- **Riesgo de la resolución de "siete Niveles" (sección 1).** Se decidió con la evidencia disponible, priorizando la fuente más deliberada sobre la más breve — pero es una interpretación, no un hecho verificado con el Board de forma directa en este documento. Es el candidato más probable a requerir una nueva versión si el Board tiene información adicional.
- **Riesgo de que el Nivel 7 (Escalamiento) no tenga un criterio de avance claro (sección 2, Nivel 7)** — es intencional, porque ese Nivel es continuo, no secuencial, pero merece revisarse cuando exista un caso de uso real.

## Preguntas abiertas

Ninguna nueva — la pregunta de 6 vs. 7 Niveles queda resuelta en este documento, no abierta.

## Decisiones pendientes

- Validar la resolución de "siete Niveles" (sección 1) explícitamente con el Board, dado que invierte parcialmente una comunicación pública previa (el anuncio de 6 niveles a Caribe Tech).
- Definir el criterio de avance/seguimiento continuo del Nivel 7 con más detalle cuando exista un caso real.

## Historial de cambios

| Versión | Fecha | Cambio | Motivo |
|---|---|---|---|
| v1.0 | 2026-07-14 | Creación inicial: 7 Niveles especificados como transformación empresarial (3 preguntas cada uno), resolución de la pregunta abierta de 6 vs. 7 Niveles con evidencia, verificación contra el Criterio de Existencia de AD-004 v1.1 | Primer documento de la categoría Funcionalidades — dieciseisavo documento de la WO-000 |
