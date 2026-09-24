---
Tipo: Documento de trabajo — NO es parte del Blueprint de la WO-000
Código: ninguno (deliberadamente, no es un AD-XXX)
Estado: no se congela como un AD-XXX, pero el Board lo aprobó explícitamente como base suficiente para iniciar AD-005 (2026-07-14) — ver Historial de cambios de este documento
Fecha: 2026-07-14
Propósito: materia prima conceptual para AD-005 — no comportamientos de entidades individuales, sino leyes dinámicas del sistema empresarial como un todo
Depende de: ENTERPRISE_TAXONOMY_WORKSHOP.md, WORKSHOP_DE_RELACIONES.md
---

# Workshop de Comportamientos — Dinámica del Sistema Empresarial

> Este documento cambia de registro respecto a los dos anteriores, por instrucción explícita del Board: no pregunta "¿qué hace la entidad Empresa?" sino "¿qué leyes gobiernan cómo cambia una empresa en el tiempo?". No se buscan reglas de negocio aisladas — se buscan las dinámicas que explicarían, si son correctas, por qué unas empresas nacen y otras no, por qué unas crecen y otras se estancan, por qué unas mueren y otras se reinventan. Ninguna de estas leyes se inventa desde cero: cada una se ancla en teoría de sistemas organizacionales ya establecida fuera de este proyecto, traducida al vocabulario ya fijado por los dos workshops anteriores (Empresa, Edad, Madurez Organizacional, Riesgo, Suceso Empresarial, Decisión de Negocio, Narrativa Fundacional, Intangible, Gemelo Digital). Esto no es adorno — es la aplicación del Meta-Principio 3 (evidencia sobre opinión, Anexo v2.0) al propio ejercicio de modelar dinámicas: una ley inventada por conveniencia narrativa vale menos que una anclada en algo que ya se probó en otro lugar.

**Aplicación explícita del Principio de Emergencia (Anexo v2.0 §2):** antes de cada ley, se verificó si el fenómeno descrito ya emerge de conceptos y reglas existentes (AD-002, los workshops anteriores) o si genuinamente requiere una idea nueva. Ninguna de las diez leyes de este documento propone una entidad nueva — todas son patrones temporales sobre conceptos ya definidos. Donde una ley sugiere que el modelo de AD-005 necesita un ajuste (no una entidad nueva, sino una relación o un atributo adicional), se señala explícitamente como hallazgo para AD-005, no se resuelve aquí.

---

## Las Diez Leyes Dinámicas

### Ley 1 — Ley de Origen

**Una empresa nace cuando una Narrativa Fundacional se combina con evidencia suficiente de que existe un problema real y con un compromiso de recursos irreversible.**

Sin compromiso de recursos, lo que existe es una intención, no un nacimiento — el mismo umbral que AD-CMP-01 ya exige para avanzar de Nivel dentro de ADÁN (avance por evidencia, no por conversación), aplicado aquí al nacimiento mismo de la organización que ADÁN acompaña. *Ancla teórica:* la etapa de "Courtship" del modelo de ciclo de vida corporativo de Ichak Adizes — el compromiso, no la idea, es lo que distingue una empresa de un proyecto de conversación.

### Ley 2 — Ley de Aprendizaje

**Una empresa aprende mediante ciclos de Decisión de Negocio → Suceso Empresarial → Evidencia del resultado → ajuste de la siguiente Decisión.** Existen dos modos, no uno: el aprendizaje que corrige la acción sin cuestionar la premisa detrás de ella (ajustar una campaña de marketing que no funcionó), y el aprendizaje que cuestiona y cambia la premisa misma (concluir que el Mercado elegido nunca fue el correcto). Solo el segundo modo puede producir una Reinvención (Ley 9); el primero, por sí solo, produce mejora operativa pero nunca cambio de identidad.

*Ancla teórica:* aprendizaje de bucle simple vs. bucle doble (Argyris & Schön). *Hallazgo para AD-005:* la Decisión de Negocio, tal como quedó modelada en el Workshop de Relaciones, necesitaría distinguir cuál de los dos modos de aprendizaje representa — no como entidad nueva, sino como un atributo de la relación Decisión de Negocio → Narrativa Fundacional (¿la decisión reafirma la narrativa existente, o la reemplaza?).

### Ley 3 — Ley de Adaptación

**La Madurez Organizacional crece más rápido cuando el ciclo Suceso Empresarial → Decisión de Negocio es corto, frecuente y de bajo costo por error, y se detiene cuando ese ciclo se alarga.** Una empresa que toma pocas decisiones grandes y espaciadas se adapta más lento que una que toma muchas decisiones pequeñas y frecuentes, incluso si el volumen total de cambio es el mismo.

*Ancla teórica:* teoría de sistemas adaptativos complejos — la velocidad de adaptación de un sistema depende de la velocidad y el costo de su retroalimentación, no de su tamaño.

### Ley 4 — Ley de Crecimiento y Cambio Estructural

**El crecimiento no es lineal: atraviesa fases de expansión estable, cada una impulsada por un mecanismo de coordinación distinto, seguidas de una crisis estructural predecible cuando ese mecanismo deja de escalar.** Una empresa que creció por la creatividad de su fundador entra en crisis cuando necesita liderazgo formal; una que creció por liderazgo fuerte entra en crisis cuando necesita delegar; una que creció por delegación entra en crisis cuando necesita coordinación entre las partes ya delegadas. Cada crisis se resuelve cambiando la Estructura Organizacional (Departamento, Cargo, Jerarquía) que la fase anterior no necesitaba — nunca añadiendo más de lo mismo.

*Ancla teórica:* modelo de Greiner (*"Evolution and Revolution as Organizations Grow"*) — crecimiento por fases, cada una terminada por una crisis específica y predecible según el mecanismo de coordinación vigente.

### Ley 5 — Ley de Estancamiento

**Una empresa se estanca cuando su Madurez Organizacional deja de crecer en relación a su Edad — no cuando su Ingreso deja de crecer.** Una empresa puede seguir facturando lo mismo mientras se estanca conceptualmente (el ciclo de la Ley 3 se detuvo), y puede estar en pleno estancamiento financiero mientras sigue aprendiendo y madurando activamente. Confundir ambas señales lleva a diagnósticos equivocados: ADÁN no debería alertar estancamiento solo por una meseta de ingresos, sino por una meseta en el ciclo de retroalimentación de la Ley 3.

*Ancla teórica:* consistencia directa con el hallazgo del Enterprise Taxonomy Workshop (Addendum, punto A4) de que Edad y Madurez son variables independientes — el estancamiento es, formalmente, la divergencia entre ambas curvas.

### Ley 6 — Ley de Crisis

**Una crisis ocurre cuando uno o más Riesgos se materializan simultáneamente y superan la capacidad de absorción de la empresa** — entendida como sus Activos disponibles, menos sus Pasivos comprometidos, menos el costo de reponer lo que se pierda. La crisis no es el Suceso Empresarial negativo en sí — es el momento en que la capacidad de absorción del sistema se agota frente a ese Suceso.

*Ancla teórica:* teoría de resiliencia de sistemas — la crisis se define por el agotamiento de la capacidad de absorción, no por la magnitud del evento que la provoca (el mismo evento puede ser absorbible para una empresa y catastrófico para otra, según su colchón previo).

### Ley 7 — Ley de Recuperación

**La velocidad de recuperación tras una crisis depende menos de los Activos financieros que de los Intangibles acumulados antes de la crisis** — Reputación, Confianza, Cultura, Capital Intelectual — porque son los que determinan si Clientes, Empleados, Proveedores e Inversionistas siguen dispuestos a sostener la relación mientras la empresa se reorganiza. Dos empresas con el mismo daño financiero se recuperan a velocidades distintas si una conservó la confianza de su red y la otra no.

*Ancla teórica:* consistente con el hallazgo de "Intangibles como propiedad transversal" del Enterprise Taxonomy Workshop — esta ley es la primera validación funcional de por qué esa decisión de modelado importaba: los intangibles dejan de ser un adorno conceptual y se vuelven la variable explicativa central de un fenómeno real (recuperación post-crisis).

### Ley 8 — Ley de Muerte

**Una empresa muere no cuando se le agotan los Activos, sino cuando pierde la capacidad de generar nuevas Decisiones de Negocio respaldadas por evidencia** — es decir, cuando el ciclo de aprendizaje de la Ley 2 se detiene por completo. El agotamiento financiero suele ser la consecuencia tardía y visible de que el aprendizaje ya se había detenido antes, no la causa.

*Nota directa para el Gemelo Digital, ya resuelta por reglas existentes (Principio de Emergencia en acción):* la "muerte" de una Empresa no borra su Gemelo Digital — por la Regla 1.5 de AD-002 (nada se pierde), el Gemelo Digital pasa a un estado archivado y consultable, gobernado por AD-CMP-06 (Digital Twin Lifecycle), exactamente el mismo mecanismo que ya se documentó para el archivado de relaciones en el Addendum del Workshop de Relaciones. No hace falta ninguna regla nueva para esto — ya existe.

### Ley 9 — Ley de Reinvención

**Una empresa se reinventa cuando ejecuta un cambio de Narrativa Fundacional respaldado por una Decisión de Negocio de aprendizaje de bucle doble (Ley 2)** — cambia no solo qué hace, sino por qué existe. Esto es distinto de un pivot de Producto/Servicio, que es Adaptación (Ley 3): cambiar de producto sin cambiar de narrativa es evolución dentro de la misma identidad; cambiar de narrativa es el nacimiento de una identidad distinta dentro del mismo Gemelo Digital.

*Ancla teórica:* fase de "reorganización" del ciclo adaptativo de Holling (crecimiento → conservación → liberación → reorganización → nuevo crecimiento) — la reorganización no vuelve al estado anterior, produce una configuración distinta.

### Ley 10 — Ley de Ciclo, no de Línea

**Nacimiento, crecimiento, estancamiento, crisis, recuperación y reinvención no son una secuencia de una sola pasada — son un ciclo que una empresa puede atravesar múltiples veces, en cualquier orden salvo el primero.** Una empresa madura puede volver a un estado de crisis; una empresa en crisis puede reinventarse hacia una madurez mayor que la que tenía antes de esa misma crisis. Muerte es el único estado del que no se regresa como la misma organización — aunque incluso ahí, per la Ley 8, el Gemelo Digital persiste.

*Ancla teórica:* el ciclo adaptativo de Holling se describe explícitamente como un bucle (*panarchy*), no una línea.

**Hallazgo para AD-005 (revisado tras retroalimentación del Board — versión final, reemplaza la formulación original de "trayectoria"):** "Etapa del Ciclo de Vida" (ya definida en el Addendum del Taxonomy Workshop como etiqueta derivada de Edad × Madurez) necesita una tercera señal, pero no dos por separado. La formulación original de este documento proponía una "trayectoria" (¿sube, baja, o hay crisis activa?) como un atributo distinto. El Board propuso, por separado, una **Velocidad de Maduración Organizacional** — la tasa de cambio de la Madurez en el tiempo (Δ Madurez / Δ Tiempo) — con el ejemplo de que dos empresas en la misma posición Edad × Madurez pueden ser radicalmente distintas si una llegó ahí en seis meses y la otra en ocho años.

Verificado con cuidado, **la Velocidad no complementa a la Trayectoria — la subsume.** Una velocidad con signo (positiva = madurando, negativa = retrocediendo, cercana a cero = estancada, Ley 5) ya codifica dirección y magnitud en un solo número — exactamente lo que la "trayectoria" buscaba capturar de forma más difusa. Mantener ambas como atributos separados habría sido una violación directa del Meta-Principio 3 (simplicidad) recién reordenado en el Anexo v2.0: dos fuentes de verdad donde una basta. Se retira la formulación de "trayectoria" de este documento; **Velocidad de Maduración Organizacional (Δ Madurez / Δ Tiempo) es el hallazgo final para AD-005.**

Una precisión que sí sobrevive de la idea original: la Velocidad, por sí sola, no señala una **Crisis activa** (Ley 6) — una crisis es la materialización de Riesgo superando la capacidad de absorción, un evento que puede ocurrir antes de que la Madurez tenga tiempo de reflejarlo en su tasa de cambio. Crisis activa se detecta por la presencia de un Suceso Empresarial de esa naturaleza, no por la Velocidad — son dos señales distintas, no una.

**Aplicación ejemplar del Principio de Emergencia (Anexo v2.0 §2), y por qué es incluso más fuerte de lo que parece a primera vista:** la Velocidad no es solo "un atributo derivado que no crea entidad nueva" — es literalmente gratis. Si la Madurez Organizacional es un atributo de la Empresa, y la Regla 1.7 de AD-002 ("todo tiene versión") ya obliga a que cada cambio de Madurez quede registrado con su historial, entonces Δ Madurez / Δ Tiempo se calcula directamente sobre ese historial ya existente, sin que AD-005 necesite modelar absolutamente nada adicional para que exista — ni una entidad, ni siquiera un atributo almacenado nuevo, solo una consulta sobre datos que el sistema ya está obligado a guardar.

---

## Síntesis — verificación contra el Principio de Emergencia

Cada una de las diez leyes se revisó contra la pregunta que el Anexo v2.0 exige antes de proponer algo nuevo: **¿esto ya emerge de conceptos existentes, o hace falta algo que no existe?**

| Ley | ¿Requirió concepto nuevo? | Qué usó en su lugar |
|---|---|---|
| 1. Origen | No | Narrativa Fundacional + Evidencia (ya existentes) |
| 2. Aprendizaje | No | Ciclo Decisión de Negocio–Suceso Empresarial ya modelado en el Workshop de Relaciones |
| 3. Adaptación | No | Madurez Organizacional + velocidad del ciclo de la Ley 2 |
| 4. Crecimiento y Cambio | No | Estructura Organizacional (ya en la taxonomía) |
| 5. Estancamiento | No | Edad y Madurez como variables independientes (ya resuelto en el Addendum) |
| 6. Crisis | No | Riesgo (ya transversal) + Activo/Pasivo |
| 7. Recuperación | No | Intangible (ya transversal) |
| 8. Muerte | No | AD-002 §1.5 + AD-CMP-06, exactamente como en el rechazo del ciclo de vida de relaciones |
| 9. Reinvención | No | Narrativa Fundacional + aprendizaje de bucle doble (Ley 2) |
| 10. Ciclo, no Línea | No | Velocidad de Maduración Organizacional (Δ Madurez / Δ Tiempo) — calculable directamente del historial de versiones que AD-002 §1.7 ya exige; reemplaza la formulación inicial de "trayectoria" por ser estrictamente más simple y capturarla por completo |

**Resultado: cero conceptos nuevos propuestos por este documento**, incluyendo el hallazgo final de la Ley 10, que empezó como una idea de "trayectoria" y terminó siendo una consulta sobre datos que el sistema ya está obligado a guardar — el ejemplo más limpio de todo este workshop de qué significa, en la práctica, que una capacidad "emerja" en vez de crearse. Diez leyes, todas expresadas combinando lo que los dos workshops anteriores y AD-002 ya establecieron. Es la prueba de que el Principio de Emergencia, recién formalizado, funciona incluso bajo la tentación más fuerte posible — modelar dinámicas de sistemas complejos es exactamente el tipo de ejercicio que invita a inventar entidades ("Crisis", "Estancamiento", "Reinvención" como objetos propios), y ninguna de las diez leyes necesitó hacerlo.

---

## Siguiente paso en el Ciclo Dominio

Con Taxonomía, Relaciones y Comportamientos completos, el Ciclo Dominio queda listo para AD-005 — Enterprise Domain Model. Este documento no decide la estructura final de AD-005; entrega diez leyes dinámicas, ancladas en teoría externa, expresadas en el vocabulario ya fijado, con un solo hallazgo final explícito para AD-005 (Velocidad de Maduración Organizacional, Δ Madurez / Δ Tiempo, calculable del historial de versiones que AD-002 §1.7 ya exige — ver Ley 10) para que AD-005 lo incorpore con el mapa completo por delante.

## Historial de cambios (documento de trabajo — se registra igual, por disciplina)

| Fecha | Cambio |
|---|---|
| 2026-07-14 | Creación inicial: diez leyes dinámicas del sistema empresarial, ancladas en teoría organizacional externa, con verificación explícita contra el Principio de Emergencia |
| 2026-07-14 | Revisión de la Ley 10: la formulación inicial de "trayectoria" (dirección de cambio de Madurez) se retira y se reemplaza por Velocidad de Maduración Organizacional (Δ Madurez / Δ Tiempo), propuesta por el Board — más simple, subsume la trayectoria, y es calculable sin modelar nada nuevo sobre el historial de versiones que AD-002 §1.7 ya exige |
| 2026-07-14 | Aprobado por el Board como base suficiente para iniciar AD-005 — Enterprise Domain Model |
