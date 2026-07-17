---
Código: AD-005
Nombre: Enterprise Domain Model
Versión: v1.0
Estado: Aprobado y congelado. Validado por el Board en el Gate Review de Fase 1 (2026-07-14)
Confidence Level: 70%
Fecha de aprobación: 2026-07-14
Responsable (autor): CC (Claude Code)
Aprobador: Hernán / Junta Directiva
---

# AD-005 — Enterprise Domain Model

> Este documento responde una sola pregunta: **¿cómo está constituida una organización, independientemente de su tamaño, industria, país o momento de vida?** No describe software. No hay tablas, clases ni bases de datos aquí — eso es AD-006. Este documento es la constitución conceptual del mundo empresarial que ADÁN entenderá durante los próximos veinte años. Todo lo construido en el Ciclo Dominio —172 conceptos enumerados, 32 relaciones catalogadas, 10 leyes dinámicas ancladas en teoría— converge aquí, y converge **reducido**, no ampliado: de 172 conceptos candidatos, este documento selecciona 26 entidades núcleo. La reducción no es una pérdida — es la aplicación más grande, hasta ahora, de la Regla de Economía Conceptual (AD-002 §1.10) y el Principio de Emergencia (Anexo v2.0 §2) en toda la WO-000.

**Nivel de contenido:** mixto, señalado explícitamente en cada sección. Los criterios de admisión (sección 1) y las leyes dinámicas (sección 5) son Principio Permanente. La lista específica de 26 entidades (sección 2) es, en su mayoría, Principio Permanente por representar estructura universal — salvo donde se indica lo contrario, son Decisión de Diseño sujeta a evolución sin romper el criterio de admisión que las produjo.

---

## 1. Criterio de Admisión — qué convierte un concepto en entidad núcleo

De los 172 conceptos del Ciclo Dominio, solo entra a este documento un concepto que cumple **las cuatro condiciones a la vez**:

1. **Es universal** — no depende de industria, país, tamaño ni etapa de vida (criterio ya establecido en el Enterprise Taxonomy Workshop §6).
2. **No es una propiedad transversal disfrazada de entidad** — si el concepto describe una cualidad que se predica de otras entidades (como Riesgo o Intangible), no es una entidad, es un atributo o una relación (Enterprise Taxonomy Workshop §3.2, Addendum A5).
3. **No emerge de combinar entidades ya admitidas** — Principio de Emergencia (Anexo v2.0 §2): si el concepto puede expresarse componiendo entidades y reglas ya incluidas en este documento, no se admite por separado.
4. **Pasa la prueba de Economía Conceptual** (AD-002 §1.10) sobre lo que queda después de los tres filtros anteriores: resuelve un problema real, no puede expresarse con lo ya admitido, y su valor supera su complejidad.

**Resultado de aplicar este criterio a los 172 conceptos: 26 entidades núcleo.** El resto se clasifica en tres categorías, todas fuera del núcleo por diseño, no por descuido — ver sección 6.

---

## 2. Las 26 Entidades Núcleo

Organizadas en seis clusters. Cada entidad indica su definición conceptual y sus atributos conceptuales clave — nunca un esquema técnico. Los nombres ya reflejan las resoluciones de colisión decididas en el Addendum del Enterprise Taxonomy Workshop (Iniciativa, Suceso Empresarial, Decisión de Negocio, Documento con atributo Origen) — este documento es la primera vez que esas resoluciones se aplican de forma sistemática y definitiva, no vuelve a discutirlas.

### 2.1 Identidad y Gobernanza

| Entidad | Definición conceptual | Atributos conceptuales clave |
|---|---|---|
| **Empresa** | La organización misma — la raíz de todo el modelo. Existe con una Edad, una Madurez Organizacional, y una identidad que persiste incluso cuando todo lo demás cambia | Razón Social, Jurisdicción, Tipo Societario, Edad, Madurez Organizacional, Narrativa Fundacional (relación 1:1), Marca(s) (relación 1:N) |
| **Narrativa Fundacional** | La historia de origen de la Empresa — por qué existe, más allá de qué hace. No es marketing, es la referencia contra la que se mide una Reinvención (Ley 9) | Relato de origen, motivación fundadora, momento de compromiso irreversible (Ley 1) |
| **Marca** | Una identidad comercial que la Empresa proyecta al mercado. Una Empresa puede tener varias | Nombre, posicionamiento, atributo `es_intangible: true` en su dimensión de Reputación asociada |
| **Accionista / Inversionista** | Quien tiene una participación de propiedad o financiamiento sobre la Empresa | Tipo de participación, desde cuándo — mecánica de rondas/valuación queda fuera del núcleo (sección 6) |

### 2.2 Estructura Organizacional y Personas

| Entidad | Definición conceptual | Atributos conceptuales clave |
|---|---|---|
| **Departamento** | Unidad formal de organización interna de la Empresa | Nombre, función, jerarquía respecto a otros Departamentos |
| **Cargo** | Posición formal dentro de un Departamento | Nivel jerárquico, a qué Cargo reporta |
| **Rol Funcional** | Función que se cumple, no necesariamente igual a un Cargo — relación N:M con Cargo | Descripción funcional, habilidades asociadas |
| **Empleado** | Persona con relación laboral formal con la Empresa, ocupando uno o más Cargos en el tiempo | Fecha de ingreso, historial de Cargos (versionado, AD-002 §1.7) |

### 2.3 Mercado y Comercial

| Entidad | Definición conceptual | Atributos conceptuales clave |
|---|---|---|
| **Cliente Final** | Quien compra o consume lo que la Empresa ofrece | Segmento, historial de relación (no solo transacciones — también Confianza como atributo intangible) |
| **Producto/Servicio** | Lo que la Empresa ofrece al Mercado | Categoría, propuesta de valor, Mercado(s) donde se posiciona |
| **Mercado** | El espacio de intercambio donde la Empresa y sus Competidores operan | Definición del segmento, tamaño, tendencias |
| **Competidor** | Otra organización que compite con la Empresa dentro de un Mercado compartido | Relación ternaria con Empresa y Mercado (Workshop de Relaciones §2) |
| **Proveedor** | Quien suministra recursos, bienes o servicios a la Empresa | Criticidad de la relación (atributo, no entidad separada — Workshop de Relaciones, Addendum Parte 1) |

### 2.4 Operación

| Entidad | Definición conceptual | Atributos conceptuales clave |
|---|---|---|
| **Proceso** | Una secuencia repetible de actividad que la Empresa ejecuta para producir un resultado | Objetivo del proceso, frecuencia, puede originar Iniciativas (Workshop de Relaciones §3) |
| **Iniciativa** | Un esfuerzo interno, delimitado en el tiempo, para lograr un cambio específico — nombre definitivo, distinto de "Proyecto" (reservado para ADÁN, AD-003) | Objetivo, Empleados involucrados, Presupuesto asociado |
| **Suceso Empresarial** | Algo que ocurrió en el mundo real de la Empresa — nombre definitivo, distinto de "Evento" (reservado para el registro técnico de ADÁN, AD-006) | Naturaleza (rutinario, crítico, fundacional), fecha, puede originar o ser originado por una Decisión de Negocio |
| **Contrato** | Un acuerdo formal entre la Empresa y otra parte (Proveedor, Cliente, Empleado, Socio) | Partes, vigencia, se formaliza mediante uno o más Documentos |
| **Documento** | Cualquier archivo con contenido y metadatos relevante para la Empresa | Atributo `Origen` (generado internamente / recibido de un tercero) — resuelve la colisión con el "Documento" de ADÁN sin crear dos entidades (Addendum A1) |

### 2.5 Dirección y Evidencia

| Entidad | Definición conceptual | Atributos conceptuales clave |
|---|---|---|
| **Objetivo** | Una declaración cualitativa de dirección estratégica | Horizonte de tiempo, se concreta mediante una o más Metas |
| **Meta** | La cuantificación de un Objetivo (equivalente a un Key Result) | Valor objetivo, fecha límite |
| **Indicador** | Lo que se mide para verificar el avance hacia una Meta (KPI es el subtipo más común, no una entidad separada) | Fórmula conceptual, frecuencia de medición |
| **Decisión de Negocio** | Una elección real tomada por la Empresa — nombre definitivo, distinto de "Decisión" (objeto de ADÁN, AD-006) y de "Elección de Diseño" (documentación de la WO-000) | Quién la tomó (Empleado en su Cargo), Documentos que la respaldan, modo de aprendizaje que representa (bucle simple o doble, Ley 2) |

### 2.6 Finanzas

| Entidad | Definición conceptual | Atributos conceptuales clave |
|---|---|---|
| **Activo** | Algo de valor que la Empresa posee | Tipo, valor, liquidez (relevante para la Ley 6, capacidad de absorción) |
| **Pasivo** | Una obligación que la Empresa tiene | Tipo, monto, plazo |
| **Ingreso** | Valor que entra a la Empresa | Fuente, periodicidad |
| **Gasto** | Valor que sale de la Empresa | Categoría, periodicidad |

**Confidence Level de esta sección: 62%** — la reducción de 172 a 26 sigue un criterio explícito y verificable, pero la composición exacta de "atributos conceptuales clave" por entidad es una primera propuesta, no validada contra un caso real todavía; se espera que AD-006 ajuste detalles sin tocar la lista de 26 entidades en sí.

---

## 3. Propiedades Transversales

No son entidades — son cualidades que se predican de varias entidades del núcleo a la vez. Tratarlas como entidades habría violado el Principio de Emergencia (cada una ya emerge de aplicarse como atributo a lo que ya existe).

- **Riesgo** — se predica de Empresa, Proceso, Iniciativa y Contrato (relación polimórfica, Workshop de Relaciones §5). Atributos: tipo (legal, financiero, operativo, reputacional...), severidad, probabilidad.
- **Intangible** (`es_intangible: true`) — se predica de Marca (vía Reputación), de la Empresa en general (vía Cultura, Confianza, Credibilidad, Capital Intelectual, Propósito) y de la relación con Cliente Final y Comunidad. No introduce entidades nuevas — estos conceptos viven como atributos cualitativos de Empresa o de Marca, con la propiedad transversal marcándolos como de naturaleza distinta a los Activos financieros tradicionales (Ley 7: los Intangibles, no los Activos financieros, explican la velocidad de Recuperación).

---

## 4. Dimensiones de Identidad y Ciclo de Vida

Todas viven como atributos (algunos derivados) de la entidad Empresa — ninguna es una entidad separada:

- **Edad** — tiempo transcurrido desde el nacimiento de la Empresa (Ley 1).
- **Madurez Organizacional** — variable independiente de la Edad (Enterprise Taxonomy Workshop, Addendum A4). Se actualiza por versión, según AD-002 §1.7.
- **Velocidad de Maduración Organizacional** (derivada, no almacenada) — Δ Madurez / Δ Tiempo, calculada directamente sobre el historial de versiones de Madurez que AD-002 §1.7 ya exige. Reemplaza la formulación inicial de "trayectoria" (Workshop de Comportamientos, Ley 10) por ser más simple y subsumirla completamente.
- **Etapa del Ciclo de Vida** (derivada, no almacenada) — una etiqueta legible calculada de la posición Edad × Madurez.

---

## 5. Leyes Dinámicas del Dominio

Las diez leyes del Workshop de Comportamientos se incorporan aquí como reglas formales del dominio — no como comportamiento de ADÁN (eso es AD-CMP), sino como verdades sobre cómo se comportan las organizaciones que ADÁN modela. Se listan por nombre, con referencia a su desarrollo completo en el workshop de origen, en cumplimiento de la Regla de No Duplicación:

1. **Ley de Origen** — nacimiento por Narrativa Fundacional + evidencia + compromiso irreversible de recursos.
2. **Ley de Aprendizaje** — ciclo Decisión de Negocio → Suceso Empresarial → Evidencia → ajuste; bucle simple vs. bucle doble.
3. **Ley de Adaptación** — Madurez crece con la velocidad y el bajo costo del ciclo de retroalimentación.
4. **Ley de Crecimiento y Cambio Estructural** — crisis predecibles de coordinación (Greiner) que exigen cambio de Estructura Organizacional.
5. **Ley de Estancamiento** — divergencia entre Edad y Madurez, no meseta de Ingreso.
6. **Ley de Crisis** — Riesgo materializado que supera la capacidad de absorción (Activo menos Pasivo menos costo de reposición).
7. **Ley de Recuperación** — explicada por Intangibles acumulados antes de la crisis, no por Activos financieros.
8. **Ley de Muerte** — pérdida de la capacidad de generar Decisiones de Negocio respaldadas por evidencia; el Gemelo Digital nunca se borra (AD-002 §1.5 + AD-CMP-06).
9. **Ley de Reinvención** — cambio de Narrativa Fundacional por aprendizaje de bucle doble.
10. **Ley de Ciclo, no de Línea** — las nueve leyes anteriores no son secuenciales; Velocidad de Maduración (sección 4) es la señal cuantitativa que las conecta a todas.

*Ver `WORKSHOP_DE_COMPORTAMIENTOS.md` para el desarrollo completo de cada ley, su ancla teórica y su verificación contra el Principio de Emergencia — no se reproduce aquí.*

---

## 6. Qué queda fuera del núcleo, y por qué

Tres categorías, ninguna por descuido:

1. **Extensiones específicas de industria** (SKU, Inventario, Patente, Licencia Regulatoria, Territorio Comercial, Ronda de Inversión, Cap Table, Valuación...) — no pasan el criterio de universalidad (sección 1, condición 1). Quedan documentadas en el Enterprise Taxonomy Workshop como candidatas a un futuro **mecanismo de extensión por industria**, fuera del alcance de esta versión de AD-005.
2. **Propiedades transversales ya resueltas como atributos** (Riesgo, Intangible) — no son entidades, son cualidades (sección 3).
3. **Conceptos que emergen de combinar entidades del núcleo** — Etapa del Ciclo de Vida y Velocidad de Maduración son los ejemplos centrales (sección 4); ninguno necesitó convertirse en entidad.

**Ambigüedades señaladas por los workshops de origen que este documento decide explícitamente no resolver por conveniencia:**

- **Reputación: ¿de la Empresa o de la Marca?** (Workshop de Relaciones §6). Se resuelve aquí: de ambas — Reputación es un atributo intangible tanto de Empresa como de cada Marca que posee, sin relación de subordinación entre ambas mediciones. Esto no es indecisión — es la respuesta correcta al hallazgo, formalizada.
- **Comunidad como posible entidad propia** (Enterprise Taxonomy Workshop, categoría S) — no se admite en el núcleo de esta versión porque no demuestra necesidad universal comprobada (condición 1 y 4 del criterio de admisión); queda como Decisión de Diseño abierta para cuando AD-006 encuentre un caso real que lo exija.

---

## Dependencias

- AD-000 Paradixe Ecosystem Vision
- AD-001 Product DNA
- AD-002 Principios del Sistema v2.0
- AD-003 Product Language
- Anexo de Meta-Principios de Ingeniería v2.0
- Enterprise Taxonomy Workshop (+ Addendum), Workshop de Relaciones (+ Addendum), Workshop de Comportamientos — las tres fuentes de este documento

## Documentos relacionados

- AD-006 Domain Model (software) — traduce estas 26 entidades a estructuras operables; no puede introducir una entidad de negocio que no esté aquí sin antes crear una nueva versión de AD-005 (Regla de Entidades, v3.1 §1)
- AD-007 Gemelo Digital — representa una instancia de Empresa (y sus 25 entidades relacionadas) en el tiempo; la metáfora de "genoma" descartada en el Taxonomy Workshop se recupera aquí como lenguaje explicativo cuando AD-007 se redacte
- AD-CMP-06 Digital Twin Lifecycle — implementa el archivado permanente exigido por la Ley 8 (Muerte)
- AD-FUNC-01 (7 Niveles) — el acompañamiento de ADÁN opera sobre estas 26 entidades desde el primer Nivel

## Impacto sobre otros módulos

1. **AD-006 queda estructuralmente acotado**: no puede modelar más de 26 entidades de negocio sin abrir una nueva versión de este documento, ni menos sin justificar la eliminación.
2. **AD-FUNC-01 y el Sistema de Scoring (AD-FUNC-07)** deben calcular sus scores sobre estas entidades — en particular, cualquier score de "salud" o "riesgo" de una Empresa debería poder explicarse en términos de las diez Leyes Dinámicas de la sección 5, no como una fórmula aislada.
3. **AD-007 hereda directamente** la Empresa y su red de 25 entidades relacionadas como el contenido real que un Gemelo Digital versiona.
4. **El mecanismo de extensión por industria** (sección 6, punto 1) queda como trabajo futuro explícito — ningún documento de Fase 2 debe asumir que ya existe.

## Riesgos

- **Riesgo de que 26 entidades resulten insuficientes en la práctica.** Es una hipótesis fuerte, no probada contra datos reales todavía — el primer uso real de ADÁN con un cliente es la prueba definitiva. Mitigación: la Regla de Entidades exige que cualquier entidad faltante se agregue mediante una nueva versión de este documento, nunca silenciosamente en AD-006.
- **Riesgo de que la resolución de Reputación (Empresa y Marca a la vez, sección 6) genere ambigüedad de cálculo en AD-FUNC-07.** Se documenta la decisión conceptual aquí; su mecanismo de cálculo dual queda para el documento de Arquitectura correspondiente.
- **Riesgo de la nueva metodología misma:** este documento se congela sin una ronda de revisión previa del Board, por instrucción explícita. El riesgo se mitiga con la autoauditoría completa (ver conversación de entrega) y con la posibilidad, ya ejercida varias veces en esta WO-000, de abrir una nueva versión ante cualquier contradicción objetiva que aparezca.

## Preguntas abiertas

Ninguna nueva — las heredadas de los tres workshops (número de Niveles 6 vs. 7, nombre definitivo de Paradixe Capital y del Token del Ecosistema) siguen abiertas en sus documentos de origen, no se duplican aquí.

## Decisiones pendientes

- Validar las 26 entidades núcleo contra un caso de negocio real (el primer cliente acompañado por ADÁN) antes de considerar esta lista definitivamente probada, no solo lógicamente derivada.
- Diseñar el mecanismo de extensión por industria (sección 6) cuando exista evidencia de qué industrias lo requieren primero.

## Historial de cambios

| Versión | Fecha | Cambio | Motivo |
|---|---|---|---|
| v1.0 | 2026-07-14 | Creación inicial: 26 entidades núcleo seleccionadas de 172 conceptos candidatos, 2 propiedades transversales, 4 dimensiones de identidad, 10 leyes dinámicas incorporadas por referencia. Construido, autoauditado y congelado en un solo ciclo, bajo la nueva metodología "se construye, se autoaudita, se congela, se continúa" | Documento fundacional del modelo empresarial de ADÁN — instrucción directa del Board de avanzar sin más iteraciones de workshop |
| — | 2026-07-14 | Validación final del Board, sin cambios de contenido, confirmada en el Gate Review de Fase 1 | Cierre formal de la aprobación pendiente |
