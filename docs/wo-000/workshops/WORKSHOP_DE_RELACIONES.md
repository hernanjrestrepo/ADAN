---
Tipo: Documento de trabajo — NO es parte del Blueprint de la WO-000
Código: ninguno (deliberadamente, no es un AD-XXX)
Estado: no se aprueba, no se congela, no tiene Confidence Level formal
Fecha: 2026-07-14
Propósito: materia prima conceptual para AD-005 y AD-006 — cómo se relacionan los conceptos ya enumerados en el Enterprise Taxonomy Workshop
Depende de: ENTERPRISE_TAXONOMY_WORKSHOP.md (incluido su Addendum)
---

# Workshop de Relaciones

> Este documento tampoco modela software — sigue siendo conceptual, como pidió el Board. No hay claves foráneas, tablas ni cardinalidad de base de datos aquí; hay cardinalidad de **negocio** ("¿cuántos Departamentos puede tener una Empresa?", no "¿cómo se implementa esa relación en SQL?"). El objetivo es responder qué le faltaba a la sección 5 del workshop de taxonomía: no solo qué conceptos se relacionan, sino **cuántos con cuántos y en qué dirección**.

**Alcance deliberadamente reducido:** de los 172 conceptos del workshop de taxonomía (tras el addendum), este documento relaciona solo los ~27 conceptos marcados como universales o elevados a primera clase por el propio Board — modelar cardinalidad y dirección de los 172 sería sobre-especificación antes de que exista evidencia de que todos merecen ser entidades reales en AD-005 (Meta-Principio 3, simplicidad sobre sofisticación innecesaria). Los conceptos específicos de industria quedan fuera de este ejercicio hasta que se demuestre que se necesitan.

---

## 1. Relaciones estructurales

| Origen | Cardinalidad | Relación | Destino |
|---|---|---|---|
| Empresa | 1:N | se organiza en | Departamento |
| Departamento | 1:N | contiene | Cargo |
| Cargo | 1:N (en el tiempo) / 0:1 (en un momento dado) | es ocupado por | Empleado |
| Cargo | N:M | cumple | Rol Funcional |
| Cargo | N:1 (auto-relación) | reporta a | Cargo |
| Empresa | 1:N | emplea | Empleado |

*Nota:* la relación Cargo→Empleado cambia de cardinalidad según si se mira en un instante (0 o 1 empleado activo) o a lo largo del tiempo (muchos empleados históricos pueden haber ocupado el mismo Cargo) — esta distinción temporal es exactamente el tipo de matiz que AD-CMP-06 (Digital Twin Lifecycle) ya anticipa para el Gemelo Digital, y probablemente aplica igual de bien a la estructura organizacional interna de la empresa modelada.

## 2. Relaciones de mercado

| Origen | Cardinalidad | Relación | Destino |
|---|---|---|---|
| Empresa | 1:N | ofrece | Producto/Servicio |
| Producto/Servicio | N:M | se posiciona en | Mercado |
| Empresa | N:M | opera en | Mercado |
| Empresa | N:M | compite con | Competidor |
| Empresa | 1:N | atiende a | Cliente Final |
| Cliente Final | N:M | compra/consume | Producto/Servicio |

*Nota:* "Empresa compite con Competidor" es en realidad una relación de tres puntas — dos empresas compiten *dentro de* un Mercado compartido, no en abstracto. Modelarla como relación binaria simple pierde esa condición; queda señalado para que AD-005 decida si vale la pena una relación ternaria o si "compite en el mismo Mercado que" basta como regla derivada.

## 3. Relaciones operativas

| Origen | Cardinalidad | Relación | Destino |
|---|---|---|---|
| Empresa | 1:N | ejecuta | Proceso |
| Proceso | 1:N | puede originar | Iniciativa |
| Iniciativa | N:1 | puede mejorar | Proceso |
| Iniciativa | N:M | involucra | Empleado |
| Proceso | 1:N | genera | Suceso Empresarial |
| Suceso Empresarial | 0:N | puede generar | Documento |

*Nota — relación bidireccional de causalidad:* Proceso→Iniciativa ("un proceso ineficiente motiva una iniciativa de mejora") e Iniciativa→Proceso ("una iniciativa modifica el proceso") son direcciones distintas de la misma pareja de conceptos, no una relación única. Este patrón —causalidad en ambas direcciones según el momento— reaparece en la sección 5 con Decisión de Negocio y Suceso Empresarial, y es probablemente el hallazgo estructural más importante de todo este workshop: **el dominio empresarial no es un árbol, es un grafo con ciclos de causalidad reales**, y AD-006 deberá decidir cómo representar esa direccionalidad sin perderla (ver Síntesis).

## 4. Relaciones financieras

| Origen | Cardinalidad | Relación | Destino |
|---|---|---|---|
| Empresa | 1:N | posee | Activo |
| Empresa | 1:N | tiene | Pasivo |
| Empresa | 1:N | genera | Ingreso |
| Empresa | 1:N | incurre en | Gasto |
| Empresa | 1:N | contrata a | Proveedor |
| Proveedor | 1:N | sostiene relación mediante | Contrato |
| Empresa | 1:N | celebra | Contrato |
| Contrato | 1:N | se formaliza mediante | Documento |

## 5. Relaciones de dirección y evidencia

| Origen | Cardinalidad | Relación | Destino |
|---|---|---|---|
| Empresa | 1:N | declara | Objetivo |
| Objetivo | 1:N | se concreta mediante | Meta |
| Meta | 1:N | se mide mediante | Indicador (KPI es subtipo) |
| Empresa | 1:N | está expuesta a | Riesgo |
| Riesgo | N:1 (polimórfica) | afecta a | Empresa \| Proceso \| Iniciativa \| Contrato |
| Empresa | 1:N | toma | Decisión de Negocio |
| Decisión de Negocio | N:1 | puede originarse en | Suceso Empresarial |
| Suceso Empresarial | N:1 | puede ser producido por | Decisión de Negocio |
| Decisión de Negocio | N:M | se respalda en | Documento |
| Decisión de Negocio | N:1 | es tomada por | Empleado (en su Cargo) |

*Nota — relación polimórfica:* "Riesgo afecta a" no apunta a un solo tipo de concepto — un Riesgo puede estar asociado a la Empresa en general, a un Proceso específico, a una Iniciativa o a un Contrato. Esto no es una debilidad del modelo, es una propiedad real del concepto (ya señalada como "transversal" en la sección 3.2 del workshop de taxonomía) — AD-006 necesitará un mecanismo conceptual explícito para representar "esto se relaciona con distintos tipos de origen", no una relación fija a una sola entidad.

## 6. Relaciones de identidad (dimensión "organismo")

| Origen | Cardinalidad | Relación | Destino |
|---|---|---|---|
| Empresa | 1:1 | tiene | Edad |
| Empresa | 1:1 | tiene | Madurez Organizacional |
| (Edad, Madurez Organizacional) | derivada, no almacenada | determinan | Etapa del Ciclo de Vida |
| Empresa | 1:1 | tiene | Narrativa Fundacional |
| Empresa | 1:N | posee | Marca |
| Marca / Empresa | 1:1 (ambigüedad abierta) | genera | Reputación |

*Nota:* la relación Marca/Empresa→Reputación queda con ambigüedad abierta deliberadamente — no está claro todavía si la Reputación se predica de la Empresa como un todo o de cada Marca por separado (una empresa con mala reputación corporativa puede tener una submarca con buena reputación propia). Se señala como pregunta para AD-005, no se resuelve aquí.

---

## Síntesis — hallazgos para AD-005 y AD-006

1. **32 relaciones documentadas** entre 27 conceptos núcleo, agrupadas en 6 clusters.
2. **El hallazgo estructural principal: el dominio es un grafo con ciclos de causalidad, no un árbol.** Dos pares de conceptos (Proceso↔Iniciativa, Decisión de Negocio↔Suceso Empresarial) tienen relaciones causales en ambas direcciones según el contexto temporal. Un modelo que solo permita relaciones de padre-a-hijo en una dirección perderá información real del negocio.
3. **Dos relaciones polimórficas confirmadas** (Riesgo, y en menor medida Documento como respaldo de Decisión de Negocio) — conceptos que se asocian con más de un tipo de origen. AD-006 necesita una forma explícita de modelar esto, no una relación fija por par de entidades.
4. **Una relación ternaria disfrazada de binaria** (Empresa compite con Competidor, realmente "dentro de un Mercado") — señalada para que AD-005 decida si se modela explícitamente o se deriva.
5. **Una ambigüedad genuina sin resolver** (Reputación: ¿de la Empresa o de la Marca?) — se deja abierta a propósito en vez de decidirse por conveniencia.
6. Los tres términos ya renombrados en el Addendum del workshop de taxonomía (Iniciativa, Suceso Empresarial, Decisión de Negocio) se usaron consistentemente en todo este documento, sin una sola aparición residual de "Proyecto", "Evento" o "Decisión" sin calificar en el sentido de negocio — verificación de que la resolución de colisiones sí es operable en la práctica, no solo en la tabla que la propuso.

---

## Addendum — Evaluación crítica: "Relaciones Vivas" (hipótesis del Board, post-aprobación)

El Board aprobó este workshop sin cambios de contenido y planteó una hipótesis para que se evalúe con el mismo rigor aplicado a Enterprise Genome, antes de tocar el Workshop de Comportamientos: **las relaciones entre conceptos empresariales tienen ciclo de vida propio** (nacen, se fortalecen, se debilitan, cambian de naturaleza, desaparecen) **y atributos propios** (intensidad, criticidad, confianza, dependencia, frecuencia, dirección de influencia). Se evalúan las dos partes por separado, porque tienen naturaleza distinta y el resultado no es el mismo para ambas.

### Parte 1 — ¿Las relaciones tienen atributos propios?

**Prueba de tres partes (AD-002 §1.10):**

1. **¿Resuelve un problema real?** Sí, sin ambigüedad. Los ejemplos del Board son exactos: en la sección 2 de este documento, "Empresa atiende a Cliente Final" trata igual a un comprador ocasional que a una cuenta que representa el 60% de los ingresos. Ese es un vacío real, y de hecho es un vacío que este mismo workshop se auto-impuso al alcance ("cardinalidad y dirección", explícitamente sin intensidad) — no es un descuido, es un límite que ya tocó su borde.
2. **¿No puede expresarse con conceptos existentes?** Parcialmente falla. "Score" ya existe como mecanismo de cuantificación con nivel de confianza (AD-FUNC-07) — pero hoy está pensado para calificar *entidades* (Founder Score, Business Score), no *relaciones entre entidades*. Extenderlo a relaciones es posible sin crear un concepto nuevo, solo ampliando dónde se aplica un concepto que ya existe.
3. **¿El valor supera la complejidad?** Depende completamente de si se aplica de forma universal o selectiva. Aplicar seis atributos a las 32 relaciones del workshop (192 valores a mantener) sería sofisticación innecesaria (Meta-Principio 3) — la mayoría no lo necesita (¿"intensidad" de "Cargo reporta a Cargo"? No aporta nada). Aplicado solo donde el negocio realmente hace la pregunta —Cliente, Proveedor, Riesgo, probablemente Competidor— el valor es alto y la complejidad es baja.

**Veredicto Parte 1: válido, pero no como concepto nuevo del dominio conceptual — como patrón de modelado para AD-006.** En terminología de modelado de dominios, esto ya tiene nombre: una "relación de primera clase" o "entidad asociativa" (el mismo patrón detrás de, por ejemplo, una matrícula que conecta Estudiante y Curso pero también tiene su propia nota). No es una idea nueva de Paradixe — es una técnica estándar que AD-006 debe adoptar selectivamente, no un concepto que este workshop deba agregar a la taxonomía. Se documenta aquí como instrucción para AD-006, no como entrada nueva del vocabulario.

### Parte 2 — ¿Las relaciones tienen ciclo de vida propio?

Aplicada la misma prueba, con un resultado más contundente:

1. **¿Resuelve un problema real?** Sí en la superficie — una relación que se debilita o se transforma es un fenómeno de negocio real (un cliente que se aleja, una alianza que cambia de naturaleza).
2. **¿No puede expresarse con conceptos existentes?** Aquí falla de forma directa, exactamente como falló Enterprise Genome. Si la Parte 1 se acepta —una relación es un objeto con atributos, como "intensidad"— entonces **el "ciclo de vida" de una relación ya está garantizado por dos reglas que el Board ya aprobó**: la Regla 1.7 de AD-002 ("todo tiene versión") ya obliga a que cada cambio de "intensidad" quede versionado con su historial; la Regla 1.5 ("nada se pierde") ya obliga a que una relación que desaparece se archive, no se borre. "Nacer" es la primera versión. "Fortalecerse/debilitarse" es un cambio de valor entre versiones. "Cambiar de naturaleza" es un cambio de tipo, con el mismo mecanismo. Y el patrón completo —nace, crece, cambia, se archiva— es literalmente el mismo que AD-CMP-06 (Digital Twin Lifecycle) ya define para el Gemelo Digital, aplicado un nivel más abajo, a una relación en vez de a la entidad completa.
3. **¿El valor supera la complejidad?** No aplica — si el punto 2 ya está cubierto por reglas existentes, cualquier mecanismo nuevo sería, por definición, duplicación.

**Veredicto Parte 2: se rechaza como concepto nuevo, por el mismo motivo estructural que Enterprise Genome.** No es una idea equivocada — es una idea correcta que ya fue aprobada, dos veces, en otro documento (AD-002 §§1.5 y 1.7) y adaptada una vez más en AD-CMP-06. Formalizarla de nuevo aquí no agregaría capacidad al sistema, solo un nombre adicional para algo que ya funciona. Se recupera únicamente como una **nota de referencia cruzada** que AD-006 debería incluir explícitamente, para que nadie más adelante reinvente un "mecanismo de ciclo de vida de relaciones" sin darse cuenta de que ya existe: *"toda relación de primera clase hereda versionado y permanencia de AD-002 §§1.5/1.7; su evolución se observa en su historial de versiones, sin mecanismo adicional."*

### Por qué este resultado es más limpio que el de Enterprise Genome

En Enterprise Genome, la duplicación había que inferirla comparando descripciones en lenguaje natural entre documentos. Aquí la duplicación es señalable por número de regla exacto (AD-002 §1.5, §1.7) — es la primera vez que la Regla de Economía Conceptual se aplica contra una violación que se puede citar literalmente, no solo argumentar. Eso es, en sí mismo, una señal de que el sistema de principios está madurando de guía interpretativa a herramienta de verificación.

---
