---
Código: AD-006
Nombre: Domain Model (Software)
Versión: v1.0 — APROBADA Y CONGELADA. Superseded el mismo día por v1.1 (aclaración menor) — ver AD-006_Domain_Model_v1.1.md
Estado: Aprobado y congelado. No editar en el sitio
Confidence Level: 66%
Fecha de aprobación: 2026-07-14
Responsable (autor): CC (Claude Code)
Aprobador: Hernán / Junta Directiva
---

# AD-006 — Domain Model (Software)

> AD-005 respondió qué es una empresa. Este documento responde cómo la representa el software de ADÁN — todavía no cómo se implementa (eso es Fase 2, Arquitectura): es un diagrama entidad-relación conceptual, sin tecnología, sin base de datos específica, sin API. Nombra entidades y sus atributos y relaciones, nada más.

**Nivel de contenido:** mixto. El Contrato Base (sección 2) y el principio de traducción sin pérdida (sección 1) son Principio Permanente. Los atributos específicos de cada entidad son, en su mayoría, Decisión de Diseño.

---

## 0. Aclaración de alcance — antes de la primera entidad

La instrucción del Board fue explícita: *"AD-006 no puede crear entidades nuevas... todo concepto que no exista en AD-005 queda prohibido salvo mediante una nueva versión formal de AD-005."* Aplicada literalmente, esa restricción impediría a AD-006 cumplir su propio mandato original (índice v3.1): definir Proyecto, Usuario, Fundador, Nivel, Card, Agente, Workspace, Conversación y Tarea — ninguno de estos aparece entre las 26 entidades de AD-005, porque **nunca fueron responsabilidad de AD-005**. AD-005 modela la empresa que ADÁN acompaña; nunca se propuso modelar a ADÁN mismo — su propia frase de apertura lo dice: *"no describe software... es la constitución conceptual del mundo empresarial"*.

No es una contradicción del Board — es una restricción que aplica correctamente a una parte de AD-006 (la traducción del negocio) y no a la otra (la estructura operativa propia de ADÁN, que este documento sí tiene mandato de crear desde su definición original en el índice v3.1). Se resuelve así, sin bloquear la entrega, y se deja señalado aquí con el mismo peso que cualquier otro hallazgo de esta WO-000:

- **Sección 3 (Traducción del Dominio de Negocio):** cero entidades nuevas. Las 26 de AD-005, sin excepción ni adición.
- **Sección 4 (Entidades Operativas de ADÁN):** las entidades que el propio índice v3.1 ya asignó a AD-006 desde el origen del árbol — no son "nuevas" en el sentido que la instrucción del Board buscaba prevenir (crecimiento no controlado del *dominio de negocio*), son el cumplimiento de un mandato que existía antes de esta conversación.

Si el Board considera que esta lectura es incorrecta, es exactamente el tipo de corrección que amerita reabrir el documento — el resto de AD-006 no depende de esta aclaración para ser válido.

---

## 1. Principio de Traducción sin Pérdida

Cada una de las 26 entidades de AD-005 se traduce a una entidad de software equivalente, sin fusionar, sin omitir y sin fragmentar ninguna, salvo que AD-005 ya haya indicado explícitamente lo contrario (como el caso de "Entregable", ya resuelto en AD-005 como un valor del atributo `Origen` de `Documento`, no como entidad propia — ver sección 3).

---

## 2. Contrato Base — atributos que hereda toda entidad

Definido una sola vez, en cumplimiento de la Regla de No Duplicación (v3.1 §1), en vez de repetirlo en cada una de las 38 entidades de este documento (26 traducidas + 12 operativas). Es la implementación directa, a nivel de software, de las diez reglas de AD-002:

| Atributo del Contrato Base | Regla de AD-002 que implementa |
|---|---|
| Identificador único | — (requisito técnico elemental) |
| Historial de versiones (qué cambió, cuándo, por qué) | Regla 1.7 — Todo tiene versión |
| Estado (activo / archivado — nunca "eliminado") | Regla 1.5 — Nada se pierde |
| Responsable del último cambio | Regla 1.4 — Toda decisión tiene responsable |
| Evidencia o fuente asociada, cuando aplica | Regla 1.1 — Todo genera evidencia |
| Nivel de confianza declarado, cuando el atributo proviene de una inferencia | Regla 1.9 — Todo tiene un nivel de confianza declarado |
| Razonamiento disponible bajo solicitud, cuando el valor lo generó un Agente | Regla 1.6 — Toda IA debe justificar |

Toda entidad de las secciones 3 y 4 hereda esto sin excepción — no se repite entidad por entidad.

---

## 3. Traducción del Dominio de Negocio (26 de 26, sin adición ni omisión)

No se redefine cada entidad — eso duplicaría AD-005. Se confirma la traducción y se señala solo donde el paso a software exige una precisión que el nivel conceptual no necesitaba.

| Entidad de AD-005 | Traducción de software | Precisión añadida (si alguna) |
|---|---|---|
| Empresa | Entidad raíz — todo lo demás de esta sección se relaciona con una Empresa, directa o transitivamente | Es la entidad que un Gemelo Digital (AD-007) versiona en su totalidad |
| Narrativa Fundacional | Entidad 1:1 con Empresa | — |
| Marca | Entidad 1:N con Empresa | — |
| Accionista / Inversionista | Entidad N:M con Empresa | — |
| Departamento | Entidad 1:N con Empresa, auto-relacionable (jerarquía) | — |
| Cargo | Entidad 1:N con Departamento | — |
| Rol Funcional | Entidad N:M con Cargo | — |
| Empleado | Entidad 1:N con Empresa | Historial de Cargos ocupados vía Contrato Base (versionado) |
| Cliente Final | Entidad 1:N con Empresa | — |
| Producto/Servicio | Entidad 1:N con Empresa | — |
| Mercado | Entidad N:M con Empresa | — |
| Competidor | Entidad ternaria con Empresa y Mercado (AD-005 §2.3) | — |
| Proveedor | Entidad N:1 con Empresa | Atributo de criticidad ya resuelto como parte de la relación (Workshop de Relaciones, Addendum Parte 1), no una entidad separada |
| Proceso | Entidad 1:N con Empresa | — |
| Iniciativa | Entidad 1:N con Empresa | Nombre definitivo — nunca "Proyecto" (reservado, sección 4) |
| Suceso Empresarial | Entidad 1:N con Empresa | Nombre definitivo — nunca "Evento" (reservado, sección 4) |
| Contrato (de negocio) | Entidad N:M con Empresa/Proveedor/Cliente Final | Distinto del "Contrato Base" técnico de la sección 2 — mismo término, dominios distintos, sin colisión real porque uno es de negocio y otro es un patrón de este documento, no una entidad |
| Documento | Entidad 1:N con Empresa | Atributo `Origen` (Cliente / Generado por ADÁN); el valor "Generado por ADÁN, cierre formal de Nivel o Card" es lo que en las conversaciones de origen se llamaba "Entregable" — no se crea una entidad aparte |
| Objetivo | Entidad 1:N con Empresa | — |
| Meta | Entidad 1:N con Objetivo | — |
| Indicador | Entidad 1:N con Meta | KPI es un valor de tipo, no una entidad distinta |
| Decisión de Negocio | Entidad 1:N con Empresa | Distinta de la "Decisión" operativa de ADÁN (sección 4) — puede *originarse en* o *producir* un registro de esa Decisión operativa, relación explícita, no fusión |
| Activo | Entidad 1:N con Empresa | — |
| Pasivo | Entidad 1:N con Empresa | — |
| Ingreso | Entidad 1:N con Empresa | — |
| Gasto | Entidad 1:N con Empresa | — |

**Propiedades transversales (Riesgo, Intangible) y dimensiones derivadas (Edad, Madurez, Velocidad de Maduración, Etapa):** se traducen como atributos y relaciones polimórficas sobre las entidades de esta tabla, exactamente como AD-005 las definió — no generan entidades nuevas aquí tampoco.

---

## 4. Entidades Operativas de ADÁN (mandato original del índice v3.1, no una adición de este documento)

Estas doce entidades representan cómo ADÁN se organiza a sí mismo para acompañar a una Empresa — no son parte del mundo empresarial que AD-005 modela, son parte del producto que AD-001 definió.

| Entidad | Definición | Relación principal |
|---|---|---|
| **Usuario** | Persona con acceso a ADÁN | N:M con Proyecto (puede tener acceso a más de uno) |
| **Usuario Principal** *(renombrado — ver Hallazgo 1 más abajo)* | El Usuario responsable de un Proyecto ante ADÁN | 1:N con Proyecto; N:1 con Empleado cuando el Usuario es parte formal de la Empresa |
| **Proyecto** | El contenedor de software donde ADÁN acompaña a una Empresa (AD-003) | 1:1 con Empresa |
| **Workspace** | La interfaz que envuelve un Proyecto (AD-003) | 1:1 con Proyecto |
| **Nivel** | Etapa del acompañamiento (AD-003; número exacto pendiente en AD-FUNC-01) | 1:N con Proyecto |
| **Card** | Unidad de trabajo dentro de un Nivel (AD-003) | 1:N con Nivel |
| **Conversación** | Una sesión de chat dentro de una Card | 1:N con Card |
| **Agente** | Rol interno especializado (AD-003) | N:M con Conversación (participa en) |
| **Tarea** | Unidad operativa de trabajo dentro de un Nivel — distinta de Iniciativa (que es del negocio del cliente, sección 3) | 1:N con Nivel o Card |
| **Decisión** *(de ADÁN)* | Registro de una recomendación aprobada por el cliente (AD-002 regla 1.4, AD-CMP-03) | Puede *originarse en* o *producir* una Decisión de Negocio (sección 3) — relación, no fusión |
| **Score** | Evaluación que ADÁN hace de una Empresa (Founder Score, Business Score...) — distinta de Indicador (métrica propia del negocio, sección 3) | N:1 con Empresa; declara Confidence Level (Contrato Base) |
| **Evento** | Registro técnico append-only (AD-006, timeline) — distinto de Suceso Empresarial (sección 3) | Puede *generarse a partir de* un Suceso Empresarial |

---

## 5. Hallazgos de esta versión

**Hallazgo 1 — "Fundador" ya no es el nombre correcto.** El índice original (v3.1) llamaba "Fundador" a lo que aquí se define como Usuario Principal. Ese nombre tenía sentido cuando ADÁN solo acompañaba startups. Desde que AD-001 amplió la Declaración de Misión a cualquier etapa del ciclo de vida empresarial —una empresa de treinta años también es cliente de ADÁN, y quien la representa no es su "fundador"—, mantener ese nombre habría sido una inconsistencia de vocabulario no forzada. Se renombra aquí a **Usuario Principal**. No requiere una nueva versión de AD-003, porque "Fundador" nunca llegó a fijarse formalmente ahí — era un término de las conversaciones de origen, no del lenguaje controlado ya aprobado.

**Hallazgo 2 — "Entregable" y "Artefacto" no se convierten en entidades.** "Entregable" ya quedó resuelto en AD-005 como un valor del atributo `Origen` de `Documento` (sección 3 de este documento). "Artefacto" —usado de forma difusa en las conversaciones de origen para "cualquier cosa producida", incluyendo posible código o mockups— no se resuelve en esta versión: si Genexis empieza a producir salidas que no son documentos en sentido natural (código fuente, por ejemplo), esa decisión le corresponde a AD-007 o a la categoría de Integraciones (Fase 2), no a este documento. Queda como Decisión de Diseño abierta, no como entidad admitida por precaución.

**Hallazgo 3 — Contrato (de negocio) y Contrato Base no colisionan.** Comparten palabra, no significado ni categoría: uno es una entidad del dominio de negocio (sección 3), el otro es un patrón de atributos común a todo este documento (sección 2), nunca una entidad por sí mismo. No se aplica aquí el mecanismo de renombre usado para otras colisiones (Proyecto/Iniciativa, Decisión/Decisión de Negocio) porque no hay ambigüedad real de uso — el contexto los distingue sin esfuerzo, a diferencia de los casos donde sí hizo falta intervenir.

---

## Dependencias

- AD-005 Enterprise Domain Model (traducción 1:1, sección 3)
- AD-003 Product Language (Proyecto, Nivel, Card, Workspace, Decisión, Agente ya tenían definición preliminar ahí; este documento es su "Responsable del concepto" formal, tal como AD-003 ya lo anticipaba)
- AD-002 Principios del Sistema v2.0 (Contrato Base, sección 2)

## Documentos relacionados

- AD-007 Gemelo Digital — versiona instancias de Empresa (y las 25 entidades de negocio relacionadas) más el historial de Proyecto, Nivel, Card, Decisión, Score asociados
- AD-CMP-01 a AD-CMP-06 — cada Comportamiento ya referenciaba varias de estas entidades como pendientes; quedan resueltas aquí
- Todo documento de AD-FUNC y AD-UX — consumen estas 38 entidades como su vocabulario de datos

## Impacto sobre otros módulos

1. AD-FUNC-01 (7 Niveles) puede ahora resolver su propia pregunta abierta (6 vs. 7 Niveles) contra una entidad `Nivel` ya formalizada.
2. AD-CMP-03 (Comportamiento de Decisiones) debe distinguir explícitamente Decisión (ADÁN) de Decisión de Negocio en su propio texto — ya no es ambiguo, pero el documento debe usarlo bien.
3. AD-FUNC-07 (Sistema de Scoring) debe construirse sobre la entidad Score aquí definida, distinguiéndola de Indicador.
4. AD-003 queda con una actualización pendiente, no bloqueante: reemplazar "Responsable del concepto: AD-006 (pendiente)" por "AD-006 (resuelto)" en los términos correspondientes — tarea editorial, no de contenido.

## Riesgos

- **Riesgo de la interpretación de la sección 0.** Es la decisión de mayor impacto de este documento y se tomó sin pausa para confirmación previa, bajo la nueva metodología. Si el Board no está de acuerdo, es el candidato más probable a forzar una nueva versión.
- **Riesgo de "Artefacto" sin resolver (Hallazgo 2).** Diferir la decisión es correcto por ahora, pero AD-007 no debería heredar la ambigüedad sin darse cuenta — se deja como Decisión pendiente explícita, no implícita.
- **Riesgo de 38 entidades totales (26 + 12) sin validar contra un caso de uso real.** Mismo riesgo que ya se señaló en AD-005, ahora extendido a la capa de software.

## Preguntas abiertas

Ninguna nueva — persisten las heredadas (número de Niveles, nombres pendientes de Paradixe Capital y Token del Ecosistema).

## Decisiones pendientes

- Resolver "Artefacto" cuando Genexis o AD-007 lo requieran con un caso concreto (Hallazgo 2).
- Actualizar las referencias "(pendiente)" de AD-003 a "(resuelto en AD-006)" — tarea editorial de bajo riesgo, puede hacerse en cualquier momento sin bloquear el avance.

## Historial de cambios

| Versión | Fecha | Cambio | Motivo |
|---|---|---|---|
| v1.0 | 2026-07-14 | Creación inicial: traducción sin pérdida de las 26 entidades de AD-005, Contrato Base (implementación de las 10 reglas de AD-002 a nivel de software), 12 entidades operativas de ADÁN ya mandatadas por el índice v3.1, y 3 hallazgos (renombre de "Fundador", resolución de "Entregable"/"Artefacto", no-colisión de "Contrato"). Construido, autoauditado y congelado en un solo ciclo | Séptimo documento de la WO-000, bajo la metodología "se construye, se autoaudita, se congela, se continúa" |
| v1.0 — Aprobada | 2026-07-14 | Aprobación formal del Board, sin cambios de contenido. Se congela | Cierre del ciclo de revisión de AD-006 |
| — | 2026-07-14 | **Superseded por v1.1** el mismo día: el Board refinó la instrucción original ("AD-006 no crea entidades nuevas") a su forma precisa ("no crea entidades nuevas del *dominio empresarial*"), y pidió dejar esa aclaración registrada para que la duda no vuelva a aparecer. Cambio menor — no afecta ninguna entidad, atributo ni relación ya definida | Aclaración metodológica solicitada explícitamente, sin reapertura de contenido |
