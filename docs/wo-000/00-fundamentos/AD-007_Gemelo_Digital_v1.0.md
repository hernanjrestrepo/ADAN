---
Código: AD-007
Nombre: Gemelo Digital — Especificación Estructural
Versión: v1.0 — APROBADA Y CONGELADA. Superseded por v1.1 (pregunta abierta resuelta) — ver AD-007_Gemelo_Digital_v1.1.md
Estado: Aprobado y congelado. Validado por el Board en el Gate Review de Fase 1 (2026-07-14)
Confidence Level: 64%
Fecha de aprobación: 2026-07-14
Responsable (autor): CC (Claude Code)
Aprobador: Hernán / Junta Directiva
---

# AD-007 — Gemelo Digital — Especificación Estructural

> AD-005 modela qué existe en una empresa. AD-006 modela cómo ADÁN representa eso en software, más su propia estructura operativa. Este documento responde la pregunta que queda: **¿qué hace que ambos dominios —el de la empresa real y el de ADÁN— sean, en la práctica, una sola identidad persistente?** Esa identidad es el Gemelo Digital. Solo su estructura vive aquí — qué es, qué agrega, por qué existe. Su comportamiento en el tiempo (cómo nace, crece, se divide, se fusiona, se archiva) vive en AD-CMP-06, y este documento no lo duplica.

**Nivel de contenido:** mixto. La definición estructural (secciones 1-3) es Principio Permanente. El detalle de qué campos exactos versiona (sección 4) es Decisión de Diseño.

---

## 0. Verificación previa: ¿el Gemelo Digital pasa el Principio de Emergencia?

Antes de escribir una sola línea de definición, se aplicó la prueba que el Anexo v2.0 exige para todo concepto nuevo: **¿ya emerge de combinar lo que AD-005 y AD-006 definieron?**

Casi. Empresa (AD-005) más Proyecto (AD-006) más el Contrato Base (versionado, permanencia, responsable — AD-002 §§1.4, 1.5, 1.7) se acercan mucho a lo que el Gemelo Digital promete. Si se quedara ahí, el Gemelo Digital sería un nombre nuevo para algo que ya existe — exactamente el tipo de rechazo que ya se aplicó a Enterprise Genome.

**Pero hay un vacío real que ni Empresa ni Proyecto, por separado, cubren:** ninguno de los dos se declaró a sí mismo como el punto de referencia que el resto del Ecosistema Paradixe consulta. AD-000 §4 (Principio de Interoperabilidad 5) exige "una sola fuente de verdad por entidad" — pero Empresa vive enteramente dentro del vocabulario de AD-005 (el mundo del cliente) y Proyecto vive enteramente dentro del vocabulario de AD-006 (el mundo interno de ADÁN). Ninguno de los dos, por diseño, se declaró como el contrato que EVA, ATO, Genexis o CSI deberían consultar. Ese vacío es real, no inventado — y es exactamente lo que el Gemelo Digital resuelve.

**Veredicto: pasa la prueba, con una condición.** El Gemelo Digital se admite no como una tercera bolsa de datos nueva, sino como la **declaración formal de que Empresa (AD-005) y Proyecto (AD-006), junto con todo lo que ambos versionan, constituyen un límite de agregación único** — el objeto que el resto del ecosistema referencia. No agrega atributos nuevos; agrega una frontera.

---

## 1. Qué es el Gemelo Digital

**El Gemelo Digital es el límite de agregación que une, bajo una sola identidad persistente y consultable, todo lo que AD-005 y AD-006 saben sobre una Empresa específica.** No es una entidad de datos adicional — es la declaración de que una Empresa (AD-005) y su Proyecto correspondiente (AD-006), junto con las 36 entidades restantes que ambos versionan, se tratan como un solo objeto para efectos de: (a) referencia desde el resto del Ecosistema Paradixe, (b) permanencia a través del tiempo (AD-001, Visión a 25 Años), y (c) ciclo de vida propio (nacimiento, crecimiento, archivado — especificado en AD-CMP-06, no aquí).

Relación estructural exacta: **Gemelo Digital 1:1 Empresa, 1:1 Proyecto** — los tres términos refieren, en la práctica, a la misma instancia vista desde tres ángulos: Empresa es el sujeto real (AD-005); Proyecto es la sesión operativa de trabajo (AD-006); Gemelo Digital es la identidad permanente y públicamente referenciable que envuelve a ambos.

---

## 2. Qué agrega y versiona

Sin excepción, todo lo que AD-005 y AD-006 ya declararon versionado (Contrato Base, AD-006 §2) queda agregado bajo un solo Gemelo Digital por Empresa:

- Las 26 entidades de negocio de AD-005 y su historial completo (Empleados, Contratos, Decisiones de Negocio, Activos/Pasivos, Riesgos materializados, Intangibles...).
- Las entidades operativas de AD-006 asociadas a su Proyecto (Niveles completados, Cards, Conversaciones, Decisiones de ADÁN, Scores históricos, Eventos técnicos).
- Las dimensiones de identidad de AD-005 §4 (Edad, Madurez Organizacional y su Velocidad derivada, Etapa del Ciclo de Vida derivada).

No se enumeran de nuevo campo por campo — ya están definidos en AD-005 y AD-006; el Gemelo Digital no los redefine, los agrega bajo una identidad común, en cumplimiento directo de la Regla de No Duplicación.

---

## 3. Por qué el resto del sistema gira alrededor de él, y no al revés

Tres razones, cada una ya establecida en documentos previos, ahora conectadas:

1. **Es la única entidad diseñada explícitamente para ser referenciada fuera de ADÁN.** AD-000 §3 ya declaraba que EVA, ATO, Genexis y CSI consumen "las señales que ADÁN produce" — el Gemelo Digital es, formalmente, esa señal unificada. Ningún otro componente del ecosistema necesita saber que internamente existen una Empresa (AD-005) y un Proyecto (AD-006) separados.
2. **Es lo único que sobrevive cuando todo lo demás cambia.** Un Proyecto puede reiniciarse operativamente (nueva sesión de trabajo); una Empresa puede cambiar de Narrativa Fundacional (Ley 9, Reinvención); Niveles, Cards y Agentes pueden rediseñarse en Fase 2 sin tocar el dominio. El Gemelo Digital es la única identidad que ninguno de esos cambios puede romper — es, literalmente, la aplicación de la Regla 1.5 de AD-002 (nada se pierde) al nivel más alto posible de agregación.
3. **Es la unidad de la Visión a 25 Años (AD-001).** La promesa de que "el Gemelo Digital de las primeras empresas que usaron ADÁN debería seguir existiendo, seguir siendo consultable" solo tiene sentido si existe un objeto identificable de forma estable — ni "esta fila de la tabla Empresa" ni "este Proyecto activo" son identidades que sobrevivan veinticinco años de cambios de arquitectura; el Gemelo Digital, por definición, sí.

---

## 4. El puente entre los dos dominios de AD-006

Retomando el diagrama de AD-006 v1.1 §0:

```
DOMINIO EMPRESARIAL (AD-005)  ←──┐
                                  │
                          GEMELO DIGITAL
                        (identidad única,
                      referenciable, permanente)
                                  │
DOMINIO OPERATIVO DE ADÁN (AD-006) ──┘
```

El Gemelo Digital no vive "entre" ambos dominios en el sentido de contener información propia que ninguno de los dos tenga — vive **por encima** de ambos, como la frontera que los declara unificados. Esta distinción importa: evita que AD-007 termine siendo un tercer lugar donde se dupliquen datos que ya existen en AD-005 o AD-006 (lo cual habría violado tanto la Regla de No Duplicación como el propio Principio de Emergencia que este documento tuvo que pasar en la sección 0).

---

## 5. Qué explícitamente no vive aquí

- **El ciclo de vida dinámico** (nace, crece, se divide, se fusiona, se archiva) — es AD-CMP-06, ya nombrado como su dueño desde el índice v3.1. Este documento define la estructura que ese comportamiento opera, no el comportamiento mismo.
- **El cálculo de Scores o Indicadores** — vive en AD-FUNC-07 y AD-ARQ-10; el Gemelo Digital solo agrega su historial.
- **El mecanismo técnico de versionado** (cómo se almacena, qué motor lo implementa) — Fase 2, Arquitectura.

---

## 6. Nota de lenguaje — el "genoma" recuperado

En el Enterprise Taxonomy Workshop (Addendum A3), la hipótesis de un "Enterprise Genome" como concepto formal se evaluó y se rechazó por duplicar lo que el Gemelo Digital ya representa — pero se reservó explícitamente como lenguaje explicativo para cuando este documento se escribiera. Aplicándolo aquí, sin convertirlo en un concepto del vocabulario controlado (AD-003) ni en una entidad (AD-006): **el Gemelo Digital es, en el sentido más literal, el genoma de la empresa que representa** — no porque contenga algo que Empresa y Proyecto no tengan ya, sino porque, igual que un genoma biológico, es la identidad unificada y persistente a partir de la cual todo lo demás —crecimiento, adaptación, incluso reinvención— se expresa sin dejar de ser, en su núcleo, la misma entidad reconocible.

---

## Dependencias

- AD-005 Enterprise Domain Model (26 entidades de negocio agregadas)
- AD-006 Domain Model v1.1 (12 entidades operativas agregadas; el diagrama de los Dos Dominios que este documento conecta)
- AD-000 Paradixe Ecosystem Vision §3-4 (el rol de "señal unificada" que el resto del ecosistema consume)
- AD-001 Product DNA (Visión a 25 Años — el requisito de persistencia que motiva la existencia de este documento)

## Documentos relacionados

- AD-CMP-06 Digital Twin Lifecycle — especifica el comportamiento dinámico que este documento deja fuera a propósito (sección 5)
- AD-INT-01 a AD-INT-04 — cada integración con el resto del ecosistema debe referenciar el Gemelo Digital, no la Empresa ni el Proyecto por separado
- AD-FUNC-07, AD-ARQ-10 — consumen el historial agregado aquí para calcular Scores

## Impacto sobre otros módulos

1. Toda futura integración de ecosistema (AD-INT-01 a 04) debe diseñarse contra el Gemelo Digital como contrato — nunca exponer directamente las entidades internas de AD-005 o AD-006 a otro componente del ecosistema, en cumplimiento de AD-000 §4 (Contrato Explícito).
2. AD-CMP-06, cuando se redacte, hereda esta estructura como el objeto sobre el que opera su ciclo de vida — no puede redefinir qué agrega el Gemelo Digital, solo cómo cambia en el tiempo.
3. Cierra Fase 1 (Fundamentos) de la WO-000 — todo documento de Fase 2 (Comportamientos ya completos, Funcionalidades, UX, Arquitectura) puede ahora referenciar un vocabulario de dominio completo y estable.

## Riesgos

- **Riesgo de que "límite de agregación, no entidad nueva" sea una distinción demasiado sutil para sostenerse en Fase 2.** Cuando AD-ARQ diseñe la implementación técnica real, podría resultar más simple tratar al Gemelo Digital como una tabla/entidad propia con referencias a Empresa y Proyecto, en cuyo caso la distinción conceptual de este documento seguiría siendo válida pero su traducción técnica no sería literal — se señala para que Fase 2 lo resuelva con conocimiento de esta intención, no en contra de ella.
- **Riesgo de que la relación 1:1:1 (Gemelo Digital, Empresa, Proyecto) deje de sostenerse si AD-004 §5 (una empresa que se fusiona con otra) ocurre en la práctica.** AD-CMP-06 deberá resolver explícitamente qué pasa con dos Gemelos Digitales que se fusionan — este documento no lo anticipa más allá de nombrarlo como pregunta pendiente.

## Preguntas abiertas

- ¿Qué ocurre con el Gemelo Digital cuando dos Empresas se fusionan (AD-004 §4) o cuando una Iniciativa se separa en una Empresa nueva? Queda para AD-CMP-06.

## Decisiones pendientes

Ninguna decisión de negocio pendiente en este documento.

## Historial de cambios

| Versión | Fecha | Cambio | Motivo |
|---|---|---|---|
| v1.0 | 2026-07-14 | Creación inicial: verificación explícita contra el Principio de Emergencia, definición del Gemelo Digital como límite de agregación (no entidad nueva) entre Empresa (AD-005) y Proyecto (AD-006), recuperación del lenguaje de "genoma" reservado desde el Taxonomy Workshop. Construido, autoauditado y congelado en un solo ciclo | Octavo documento de la WO-000, bajo la metodología "se construye, se autoaudita, se congela, se continúa" |
| — | 2026-07-14 | Validación final del Board, sin cambios de contenido, confirmada en el Gate Review de Fase 1. Nota del Gate Review: este documento cierra "Fundamentos" (AD-000 a AD-007), no la totalidad de la "Fase 1" original del árbol (v3, línea 190: Fundamentos + Comportamientos + Funcionalidades) — ver hallazgo del Gate Review | Cierre formal de la aprobación pendiente |
