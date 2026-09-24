---
Código: AD-004
Nombre: Product Evolution
Versión: v1.0 — APROBADA Y CONGELADA. Superseded por v1.1 (nuevo criterio de existencia de Funcionalidad) — ver AD-004_Product_Evolution_v1.1.md
Estado: Aprobado y congelado. No editar en el sitio
Confidence Level: 68%
Fecha de aprobación: 2026-07-14
Responsable (autor del borrador): CC (Claude Code)
Aprobador: Hernán / Junta Directiva
---

# AD-004 — Product Evolution

> Este documento no es un roadmap. No enumera versiones, fechas ni funcionalidades futuras — eso pertenece a la ejecución, no a la especificación. Responde una sola pregunta: **¿cómo puede evolucionar ADÁN durante los próximos veinticinco años sin perder la identidad que AD-001 y AD-002 ya fijaron como inviolable?** Todo lo que sigue son reglas de cambio, no un plan de cambios.

**Nivel de contenido:** mixto. Las reglas de esta sección son Principio Permanente — deberían regir la evolución de ADÁN sin importar qué versión, qué equipo o qué tecnología esté vigente. Los umbrales numéricos específicos usados como ejemplo (cuántos casos de uso, cuántos documentos) son Decisión de Diseño — se calibran con la experiencia real del producto, sin que eso comprometa la regla que ilustran.

---

## Respuesta directa a la pregunta central

ADÁN evoluciona **añadiendo alcance dentro de los límites que ya son inviolables, nunca renegociando esos límites**. Todo lo declarado en AD-001 §12 (los seis principios inviolables), en AD-001 §1.1 (qué jamás intentará convertirse), en las diez reglas de AD-002, y en los nueve Meta-Principios de Ingeniería, permanece fijo durante los veinticinco años de esta visión. Lo que cambia —funcionalidades, niveles de detalle, motores técnicos, mecánicas de experiencia— cambia *dentro* de ese marco. El día en que un cambio propuesto solo pueda justificarse rompiendo uno de esos límites, ese cambio no es evolución: es una ruptura de identidad, y este documento no la autoriza — solo el Board, mediante una nueva versión de AD-001, podría hacerlo.

---

## 1. Qué puede cambiar

Categorías explícitas de Decisión de Diseño, sujetas a evolución sin necesidad de tocar ningún Principio Permanente:

- El modelo de negocio, precios y monetización (reservado en WO-100 — nunca vive aquí).
- El número exacto y el orden de los Niveles dentro del flujo de acompañamiento, siempre que seis reglas del principio inviolable de progresión (AD-CMP-01) se mantengan.
- Los motores de construcción, modelos de IA y proveedores técnicos usados en cada momento (Meta-Principio 1: el dominio no depende de ellos).
- Las mecánicas específicas de Experience Engine y Gamification Engine (AD-FUNC-03/04).
- Las métricas específicas instrumentadas para medir éxito (AD-001 §18 fija la filosofía — medir calidad de decisión, no actividad —, no la lista exacta de métricas).
- La interfaz de usuario en su totalidad — ningún elemento visual de AD-UX es permanente.
- Los componentes del Ecosistema Paradixe listados en AD-000 §3 — la lista está explícitamente declarada como no cerrada.

## 2. Qué nunca podrá cambiar

Esta sección no redefine nada — únicamente consolida, por referencia, todo lo que ya es inviolable en otros documentos, para que quien lea AD-004 tenga en un solo lugar la lista completa de lo que la evolución de ADÁN no puede tocar:

- Los seis principios inviolables de AD-001 §12 (evidencia obligatoria, aprobación explícita del cliente, razonamiento disponible, Gemelo Digital permanente, límites de ecosistema y categoría, Humildad Intelectual).
- Las ocho categorías que ADÁN jamás intentará convertirse, AD-001 §1.1 (ERP, CRM, sistema contable, IDE, herramienta de diseño primaria, motor de búsqueda, red social, plataforma de pagos genérica).
- Las diez reglas de sistema de AD-002 v2.0.
- Los nueve Meta-Principios de Ingeniería de este anexo.
- La Declaración de Misión de AD-001 (diseñar, validar, construir, operar, transformar, escalar) — puede *ampliarse* en cómo se ejecuta, nunca *reducirse* de vuelta a solo "crear empresas".

## 3. Cómo nace una Funcionalidad

Ninguna Funcionalidad (categoría AD-FUNC, AD-003 §2) se incorpora al producto sin pasar por esta secuencia, en orden:

1. **Evidencia del problema.** Debe existir un problema real, demostrado con casos de uso concretos o solicitudes documentadas de clientes reales — no una intuición del equipo de producto (Meta-Principio 2).
2. **Prueba de no-redundancia.** Debe demostrarse que el problema no puede resolverse combinando Funcionalidades y Comportamientos ya existentes (Economía Conceptual, AD-002 §1.10).
3. **Verificación contra AD-001 §1.1.** Debe explicitarse contra cuál de las ocho categorías excluidas podría estar rozando la propuesta, y justificar por qué no cruza la línea. Si cruza, no se construye dentro de ADÁN — se orquesta hacia el componente del ecosistema correspondiente (AD-000 §4).
4. **Checklist de Justificación de Diseño** (AD-002 §2) — las siete dimensiones, respondidas.
5. **Registro como Decisión** — con Justificación, Alternativas evaluadas y Motivo de descarte de cada alternativa (v3.1 §1), antes de que exista una sola línea del documento AD-FUNC correspondiente.

Una Funcionalidad que no puede superar el paso 1 no nace. Una que no puede superar el paso 2 no es una Funcionalidad nueva — es una extensión de una existente.

## 4. Cuándo una Funcionalidad se convierte en un producto independiente

Una Funcionalidad se gradúa fuera de ADÁN, hacia el Ecosistema Paradixe como componente propio, cuando se cumplen las tres condiciones a la vez:

- Su valor es útil **fuera** del contexto de acompañar a una empresa a través de los Niveles de ADÁN — alguien pagaría por ella de forma independiente.
- Tiene un ciclo de vida de usuario propio, distinto del recorrido de los Niveles.
- Extraerla **reduce** la complejidad interna de ADÁN sin reducir el valor que ofrece (Meta-Principio 3 y 5 aplicados en sentido inverso: a veces la respuesta correcta a demasiada complejidad no es dejar de construir algo, sino separarlo).

**Ejemplo ilustrativo, no un compromiso de roadmap:** si Gamification Engine (AD-FUNC-04) creciera hasta el punto de que EVA o ATO también quisieran usarlo para sus propios usuarios, esa demanda cruzada es la señal de que debería graduarse a componente compartido del ecosistema, en vez de seguir viviendo exclusivamente dentro de ADÁN.

La graduación de una Funcionalidad a producto independiente es, en sí misma, una Decisión irreversible o de muy alto costo de reversión — requiere, por el Meta-Principio 8, un nivel de evidencia superior al de una Decisión ordinaria, y pasa necesariamente por el mismo comité que aprueba decisiones estructurales de ecosistema, no solo por el flujo normal de un AD-FUNC.

## 5. Cuándo un producto pasa a formar parte del ecosistema

En sentido inverso: un componente externo (adquirido, incubado, o construido por Paradixe fuera de ADÁN) se incorpora al Ecosistema Paradixe solo si cumple los Principios de Interoperabilidad ya fijados en AD-000 §4 — en particular, No Duplicación de Capacidad (no puede reconstruir algo que ya resuelve otro componente existente) y Contrato Explícito (debe integrarse mediante API versionada, nunca acceso directo a datos de otro componente).

Esta decisión, a diferencia de las anteriores, **no le corresponde a AD-004 ni a ningún documento de la especificación de ADÁN** — le corresponde a la autoridad de todo el ecosistema, hoy sin documento propio (la futura Constitución de Paradixe, AD-000 §7). AD-004 solo fija las condiciones que ADÁN, como componente ya existente del ecosistema, exige de cualquier nuevo par antes de aceptar interoperar con él.

## 6. Cómo se controla el crecimiento del dominio

El control no es discrecional — son tres mecanismos ya existentes, aplicados de forma consistente:

1. **La Regla de Entidades** (v3.1 §1): solo AD-005 (Enterprise Domain Model), AD-006 (Domain Model) y AD-007 (Gemelo Digital) pueden introducir una entidad nueva. Ningún otro documento —presente o futuro— tiene esa autoridad.
2. **Economía Conceptual** (AD-002 §1.10): toda entidad nueva debe demostrar que resuelve un problema real, que no puede expresarse con entidades existentes, y que su valor supera su complejidad — antes de incorporarse a AD-006/AD-007.
3. **La autoauditoría obligatoria** (v3.4 §1, pregunta 4): todo documento nuevo declara explícitamente qué conceptos introduce y por qué son necesarios, como parte de su entrega — no como revisión posterior.

## 7. Cómo se evita el feature creep

La defensa principal ya existe y no es nueva en este documento — es la combinación de AD-001 §1.1 (qué NO es ADÁN) con la secuencia de nacimiento de la sección 3. El feature creep ocurre cuando una funcionalidad se construye porque "sería útil" sin pasar por ese filtro. AD-004 agrega una sola regla operativa nueva: **toda propuesta de Funcionalidad que no pueda completar los cinco pasos de la sección 3 en un plazo razonable no se pospone indefinidamente en un estado ambiguo — se rechaza formalmente y se registra como Decisión descartada**, para que no reaparezca sin evidencia nueva seis meses después bajo otro nombre.

## 8. Cómo se preserva la coherencia del ecosistema a largo plazo

Tres mecanismos, dos ya existentes y uno nuevo:

- **Product Language** (AD-003) y el **Knowledge Graph** de la WO-000 evitan que el vocabulario se fragmente a medida que la especificación crece más allá de los 58 documentos actuales.
- Los **Comportamientos** (categoría AD-CMP) fijan reglas de dominio independientes de la implementación (Meta-Principio 1 y 6), de modo que el dominio no se corrompe aunque la arquitectura cambie varias veces en veinticinco años.
- **Nuevo — Revisión Periódica de Coherencia:** cada vez que se aprueban diez documentos nuevos de la WO-000, se audita el Knowledge Graph completo buscando contradicciones acumuladas entre documentos que fueron aprobados en momentos distintos y pudieron divergir sin que ningún documento individual lo detectara — porque cada autoauditoría (v3.4 §1) solo compara un documento nuevo contra los ya aprobados, nunca contra todo el conjunto acumulado a la vez. *Nivel de contenido de este mecanismo: Decisión de Diseño — el umbral de "diez documentos" es ajustable con la experiencia; la necesidad de una revisión periódica agregada, no.*

---

## Dependencias

- AD-001 Product DNA
- AD-003 Product Language
- AD-002 Principios del Sistema v2.0 *(dependencia agregada respecto al alcance original fijado en el índice v3.1, que solo listaba AD-001 y AD-003 — ver autoauditoría, pregunta 6)*
- WO-000-ANEXO-MPI Meta-Principios de Ingeniería *(dependencia nueva, por la misma razón — este documento se apoya directamente en los Meta-Principios 1, 5, 6, 7 y 9)*

## Documentos relacionados

- Toda la categoría Funcionalidades (AD-FUNC) — cualquier Funcionalidad nueva debe demostrar que pasó por la secuencia de la sección 3.
- AD-000 §7 (Constitución de Paradixe, futura) — autoridad final de la sección 5 de este documento.
- El Knowledge Graph de la WO-000 — implementa mecánicamente la Revisión Periódica de Coherencia de la sección 8.

## Impacto sobre otros módulos

1. Toda propuesta futura de Funcionalidad (AD-FUNC) queda formalmente sujeta a la secuencia de cinco pasos de la sección 3 — no es opcional, es la puerta de entrada.
2. El Knowledge Graph adquiere una responsabilidad operativa nueva: sostener la Revisión Periódica de Coherencia de la sección 8, no solo registrar relaciones pasivamente.
3. Cualquier decisión futura de graduar una Funcionalidad a producto independiente (sección 4) o de incorporar un componente externo al ecosistema (sección 5) queda marcada como Decisión de alto costo de reversión, heredando el estándar de evidencia elevado del Meta-Principio 8.

## Riesgos

- **Riesgo de que "veinticinco años sin perder identidad" se use para bloquear evolución legítima.** Las reglas de esta sección definen qué NO puede cambiar, pero la sección 1 (qué sí puede cambiar) es deliberadamente amplia — el riesgo simétrico de que este documento se invoque para rechazar cambios que en realidad son evolución válida dentro del marco, no ruptura de él.
- **Riesgo de que la Revisión Periódica de Coherencia (sección 8) nunca se ejecute en la práctica**, al no tener un responsable operativo asignado más allá de "se audita" — este documento fija la regla, no designa quién la ejecuta cada diez documentos; eso queda como decisión de proceso del Board, no de esta especificación.
- **Riesgo de sub-especificación de la sección 5.** Deliberadamente se dejó la incorporación de componentes externos al ecosistema fuera de la autoridad de este documento, pero eso significa que hoy no existe ningún documento que regule ese proceso con detalle — es un vacío real, no solo una decisión de alcance, hasta que exista la Constitución de Paradixe.

## Preguntas abiertas

Ninguna nueva al cierre de esta versión — las de AD-000 (relaciones entre pares de componentes) y AD-003 (colisión de nombre, número de Niveles) siguen abiertas ahí, no se duplican aquí.

## Decisiones pendientes

- Asignar responsable operativo de la Revisión Periódica de Coherencia (sección 8) — pendiente de decisión de proceso del Board, no de contenido de esta especificación.

## Historial de cambios

| Versión | Fecha | Cambio | Motivo |
|---|---|---|---|
| v1.0 | 2026-07-14 | Creación inicial: reglas de evolución de ADÁN a 25 años — qué puede/no puede cambiar, nacimiento y graduación de Funcionalidades, incorporación de componentes al ecosistema, control de crecimiento del dominio, prevención de feature creep, y mecanismo nuevo de Revisión Periódica de Coherencia | Quinto documento de la WO-000, primero redactado bajo el Anexo de Meta-Principios de Ingeniería recién aprobado |
| v1.0 — Aprobada | 2026-07-14 | Aprobación formal del Board, sin cambios de contenido. Se congela. Cierra el núcleo filosófico de la WO-000 (AD-001, AD-002, AD-004) — a partir de aquí la especificación pasa a modelar el dominio real, comenzando con un Enterprise Taxonomy Workshop previo a AD-005 | Cierre del ciclo de revisión de AD-004 |
| — | 2026-07-14 | **Superseded por v1.1** el mismo día: se agrega un sexto criterio de existencia a la secuencia de nacimiento de Funcionalidades (sección 3) — ninguna existe si no modifica el Gemelo Digital, mejora el conocimiento del cliente, o produce evidencia útil para la siguiente decisión | Instrucción directa del Board al iniciar la categoría AD-FUNC, para evitar funcionalidades decorativas o aisladas |
