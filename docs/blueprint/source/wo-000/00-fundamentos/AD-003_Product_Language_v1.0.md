---
Código: AD-003
Nombre: Product Language
Versión: v1.0 — APROBADA Y CONGELADA
Estado: Aprobado. No editar en el sitio. La autoauditoría entregada junto con este documento fue aceptada como parte permanente de la metodología de la WO-000
Confidence Level: 65%
Fecha de aprobación: 2026-07-14
Responsable (autor del borrador): CC (Claude Code)
Aprobador: Hernán / Junta Directiva
---

# AD-003 — Product Language

> Este documento no es un glosario. Un glosario define palabras; esto define un **lenguaje controlado**: cada término tiene una definición oficial, una definición explícitamente prohibida, sinónimos aceptados y prohibidos, contexto de uso, dependencias con otros términos, y un responsable identificable. Ningún documento posterior de la WO-000 puede redefinir un término aquí fijado — lo referencia, o propone una nueva versión de este documento si el término necesita cambiar.

**Nivel de contenido de este documento:** mixto por naturaleza. La *existencia* de un lenguaje controlado es Principio Permanente (hereda de AD-002, Regla de No Duplicación, v3.1 §1). El *conjunto específico de 21 términos* tratados aquí es Decisión de Diseño — crecerá con cada documento nuevo que introduzca vocabulario genuinamente nuevo, sujeto a la Regla de Economía Conceptual (AD-002 v2.0 §1.10).

**Aplicación de Economía Conceptual (AD-002 v2.0 §1.10):** este documento no trata con las diez dimensiones completas cada palabra usada en la WO-000 — solo los términos que (a) se usan repetidamente en múltiples documentos, y (b) tienen riesgo real de ambigüedad ya demostrado en las fuentes de origen. Se seleccionaron 21 términos bajo ese criterio, divididos en dos grupos: Vocabulario del Producto (16 términos que un usuario final de ADÁN encontraría) y Vocabulario del Proceso de Documentación (5 términos que solo existen dentro de la WO-000 misma). Ningún término de este documento es un concepto nuevo — los 21 ya existían, dispersos y a veces inconsistentes, en Chat 1.docx, Blueprint v1, o los documentos ya aprobados de esta WO-000; el trabajo de AD-003 es fijarlos, no inventarlos.

---

## 1. Vocabulario del Producto

### Ecosistema Paradixe

- **Definición oficial:** el conjunto de componentes de IA especializados —EVA, ARQAI, ATO, Genexis (y otros motores de construcción), CSI, Marketplace, Paradixe Capital, ADÁN y futuros componentes— que colaboran, mediante contratos explícitos, para cubrir cualquier etapa del ciclo de vida de una empresa.
- **Definición prohibida:** no es un conjunto de productos SaaS independientes que compiten por el mismo cliente. No es sinónimo de "Paradixe" como organización (Paradixe construye el ecosistema; el ecosistema es lo que Paradixe construye).
- **Sinónimos aceptados:** "el ecosistema" (minúscula, dentro de un documento que ya estableció el contexto).
- **Sinónimos prohibidos:** "la plataforma", "la suite de productos", "el stack Paradixe".
- **Contexto de uso:** al describir cómo ADÁN se relaciona con otros componentes; nunca al describir la interfaz de un solo producto.
- **Documentos donde aparece:** AD-000 (definición completa), AD-001, este documento.
- **Responsable del concepto:** AD-000.
- **Fecha de creación:** 2026-07-14.
- **Nivel de estabilidad:** Estable.
- **Dependencias:** ninguna — es el concepto raíz.

### ADÁN

- **Definición oficial:** la inteligencia orquestadora del Ecosistema Paradixe aplicada a una empresa específica (definición completa en AD-001 §1).
- **Definición prohibida:** no es un chatbot, no es un generador de documentos, no es un asistente de propósito general con conocimiento de negocios.
- **Sinónimos aceptados:** ninguno — nombre propio, no se abrevia ni se traduce.
- **Sinónimos prohibidos:** "la IA", "el asistente", "el bot", "la plataforma" (cuando se refiere específicamente a ADÁN, no al ecosistema completo).
- **Contexto de uso:** siempre "ADÁN", con tilde y mayúsculas, en comunicación oficial.
- **Documentos donde aparece:** todos.
- **Responsable del concepto:** AD-001.
- **Fecha de creación:** origen del proyecto, formalizado en AD-001.
- **Nivel de estabilidad:** Estable.
- **Dependencias:** Ecosistema Paradixe, Orquestador.

### Orquestador

- **Definición oficial:** el rol que cumple ADÁN dentro del ecosistema — decide qué capacidades activar, en qué orden y con qué Motor, según el punto de entrada de una empresa (AD-000 §5).
- **Definición prohibida:** no es una entidad de software separada de ADÁN, ni un componente adicional del ecosistema — es la función que ADÁN cumple.
- **Sinónimos aceptados:** "rol orquestador", en contexto donde ya se estableció que se habla de ADÁN.
- **Sinónimos prohibidos:** "controlador", "gestor", "director" — implican jerarquía sobre otros componentes, que AD-000 §4 principio 2 rechaza explícitamente.
- **Contexto de uso:** al describir la relación de ADÁN con el resto del ecosistema; nunca su relación con el cliente (ahí, "comité ejecutivo", AD-001 §1).
- **Documentos donde aparece:** AD-000, AD-001.
- **Responsable del concepto:** AD-000.
- **Fecha de creación:** 2026-07-14 (revisión de AD-000 que reemplazó el modelo de cadena por el de red).
- **Nivel de estabilidad:** Estable.
- **Dependencias:** ADÁN, Ecosistema Paradixe.

### Motor (de Capacidad)

- **Definición oficial:** cualquier proveedor —interno o externo— que ejecuta una capacidad específica que ADÁN orquesta pero no posee en exclusiva (ej. Genexis como motor de construcción). Ver AD-000 §4, principio 3.
- **Definición prohibida:** no es una dependencia fija — nombrar "el motor de X" no implica que sea el único proveedor posible de esa capacidad, ahora ni en el futuro.
- **Sinónimos aceptados:** "motor de construcción" (para la capacidad de desarrollo de software específicamente).
- **Sinónimos prohibidos:** "proveedor exclusivo", "dependencia" sin calificar que es reemplazable.
- **Contexto de uso:** siempre acompañado de la capacidad que ejecuta.
- **Documentos donde aparece:** AD-000.
- **Responsable del concepto:** AD-000.
- **Fecha de creación:** 2026-07-14.
- **Nivel de estabilidad:** Estable.
- **Dependencias:** Orquestador.

### Gemelo Digital

- **Definición oficial:** la entidad estructural que representa a una Empresa dentro de ADÁN — agrega y versiona sus decisiones, documentos, código, procesos, KPIs y evidencias a lo largo de toda su relación con el sistema. Especificación completa pendiente en AD-007.
- **Definición prohibida:** no es un perfil de usuario estático ni un expediente — es una entidad viva y versionada (su ciclo de vida se define en AD-CMP-06, Digital Twin Lifecycle).
- **Sinónimos aceptados:** "el Gemelo" (dentro de un documento que ya estableció el contexto).
- **Sinónimos prohibidos:** "perfil de empresa", "expediente", "ficha".
- **Contexto de uso:** siempre en referencia a una empresa específica — nunca en plural genérico sin especificar cuáles.
- **Documentos donde aparece:** AD-000, AD-001 (Visión a 25 Años, §8, §12), este documento; especificación completa pendiente en AD-007.
- **Responsable del concepto:** AD-007 *(pendiente — definición preliminar fijada por AD-000/AD-001; AD-007 debe heredarla sin contradecirla)*.
- **Fecha de creación:** nombrado en Blueprint v1; posición estructural fijada en la revisión de AD-000.
- **Nivel de estabilidad:** En evolución — el término está fijado, su especificación técnica no.
- **Dependencias:** Empresa, Evidencia, Decisión.

### Empresa

- **Definición oficial:** la organización real —naciente o madura— que un Gemelo Digital representa dentro de ADÁN. Modelo de dominio completo pendiente en AD-005 (Enterprise Domain Model).
- **Definición prohibida:** no es sinónimo de "Proyecto" — Empresa es el concepto de dominio de negocio; Proyecto es su contraparte de dominio de software dentro de ADÁN (ver más abajo).
- **Sinónimos aceptados:** ninguno formal.
- **Sinónimos prohibidos:** "startup" — una Empresa acompañada por ADÁN puede tener treinta años; no todas son startups (AD-001, Declaración de Misión).
- **Contexto de uso:** al hablar del cliente real de ADÁN y su organización. Para el contenedor de software correspondiente, usar "Proyecto".
- **Documentos donde aparece:** AD-000, AD-001; modelo completo pendiente en AD-005.
- **Responsable del concepto:** AD-005 *(pendiente)*.
- **Fecha de creación:** 2026-07-14 (distinción formal Empresa/Proyecto introducida al separar Enterprise Domain Model de Domain Model en la revisión de la WO-000).
- **Nivel de estabilidad:** En evolución.
- **Dependencias:** ninguna — concepto de dominio de negocio, no depende de conceptos de software.

### Proyecto

- **Definición oficial:** el contenedor de software dentro de ADÁN donde vive el acompañamiento a una Empresa — la unidad principal de organización de la interfaz, no el chat. Especificación completa pendiente en AD-006.
- **Definición prohibida:** no es sinónimo de "Empresa" — un Proyecto es la representación de software de una Empresa, no la empresa misma.
- **Sinónimos aceptados:** ninguno.
- **Sinónimos prohibidos:** "workspace de la empresa" — confunde Proyecto con Workspace, un concepto de interfaz distinto (ver más abajo).
- **Contexto de uso:** al hablar de estructura de software y navegación dentro de ADÁN.
- **Documentos donde aparece:** este documento; modelo completo pendiente en AD-006.
- **Responsable del concepto:** AD-006 *(pendiente)*.
- **Fecha de creación:** conversaciones fundacionales del producto; formalizado como entidad de dominio en esta WO-000.
- **Nivel de estabilidad:** En evolución.
- **Dependencias:** Empresa, Gemelo Digital.

### Nivel

- **Definición oficial:** cada una de las etapas secuenciales y obligatorias del acompañamiento de ADÁN dentro de un Proyecto. Especificación completa en AD-FUNC-01 *(pendiente)*.
- **Definición prohibida:** no es una funcionalidad opcional ni un módulo que se pueda saltar — el avance entre Niveles está gobernado por evidencia, no por elección libre (AD-CMP-01).
- **Sinónimos aceptados:** ninguno.
- **Sinónimos prohibidos:** "fase" — usado libremente en las conversaciones de origen, pero "Nivel" es el término oficial de esta WO-000; "fase" queda reservado exclusivamente para "Fase 1 / Fase 2" del proceso de construcción de la propia WO-000, un concepto no confundible.
- **Contexto de uso:** siempre con número o nombre específico ("Nivel 1"), nunca genérico sin calificar cuál.
- **Documentos donde aparece:** profusamente en Chat 1.docx; formalización pendiente en AD-FUNC-01.
- **Responsable del concepto:** AD-FUNC-01 *(pendiente)*.
- **Fecha de creación:** origen del proyecto.
- **Nivel de estabilidad:** Estable en el concepto; **En evolución** en el número exacto de niveles — ver Preguntas Abiertas de este documento.
- **Dependencias:** Proyecto, Comportamiento de Progresión (AD-CMP-01).

### Card

- **Definición oficial:** la unidad de trabajo dentro de un Nivel — cada proceso específico (ej. Branding, Finanzas, Canvas) con su propio chat, documentos, archivos y agentes asociados. Especificación completa pendiente en AD-UX-06.
- **Definición prohibida:** no es un chat independiente ni una pestaña decorativa — tiene su propia memoria y ciclo de vida (AD-008).
- **Sinónimos aceptados:** ninguno.
- **Sinónimos prohibidos:** "módulo", "widget" — términos de implementación, evitados por la Regla 2 de redacción (v3.2).
- **Contexto de uso:** siempre dentro del contexto de un Nivel específico.
- **Documentos donde aparece:** Chat 1.docx (Vista 4); formalización pendiente en AD-006/AD-UX-06.
- **Responsable del concepto:** AD-006 *(pendiente)*.
- **Fecha de creación:** origen del proyecto.
- **Nivel de estabilidad:** En evolución.
- **Dependencias:** Nivel, Workspace.

### Workspace

- **Definición oficial:** el espacio de trabajo contenedor de un Proyecto — la pantalla principal tras iniciar sesión, compuesta por Sidebar, zona central y panel contextual. Especificación completa pendiente en AD-UX-02.
- **Definición prohibida:** no es sinónimo de "Proyecto" — el Workspace es la representación de interfaz de un Proyecto, no el Proyecto mismo (paralelo exacto a la distinción Empresa/Proyecto).
- **Sinónimos aceptados:** "Workspace Principal" para la vista raíz específicamente.
- **Sinónimos prohibidos:** "dashboard" — Dashboard es una vista específica dentro del Workspace, no el Workspace completo.
- **Contexto de uso:** al describir estructura de interfaz, no estructura de datos (para eso, "Proyecto").
- **Documentos donde aparece:** Chat 1.docx (prompts de arquitectura de producto); formalización pendiente en AD-UX-02.
- **Responsable del concepto:** AD-UX-02 *(pendiente)*.
- **Fecha de creación:** origen del proyecto.
- **Nivel de estabilidad:** En evolución.
- **Dependencias:** Proyecto.

### Decisión

- **Definición oficial:** el objeto formal que registra una elección relevante dentro de un Proyecto — descripción, justificación, responsable, impacto, estado, alternativas descartadas (AD-CMP-03). Un ciudadano de primera clase del sistema, no una nota informal.
- **Definición prohibida:** no es cualquier mensaje del chat — solo las elecciones que cumplen el umbral de relevancia definido en AD-CMP-03 se convierten en objeto Decisión. *(Ver también Pregunta Abierta sobre colisión de nombre con "Decisión de Diseño", sección 2.)*
- **Sinónimos aceptados:** "DEC-XXXX" como identificador al referenciar una decisión específica.
- **Sinónimos prohibidos:** "elección", "resolución" en contexto formal de producto.
- **Contexto de uso:** al referirse al registro formal y trazable de una elección — no al acto conversacional de decidir.
- **Documentos donde aparece:** Chat 1.docx, AD-001 (§11, §12), AD-002 (regla 1.4); formalización de entidad pendiente en AD-006, de comportamiento en AD-CMP-03.
- **Responsable del concepto:** AD-006 (entidad) / AD-CMP-03 (comportamiento) — ambos pendientes.
- **Fecha de creación:** conversaciones fundacionales ("capa de decisiones").
- **Nivel de estabilidad:** Estable en el concepto; En evolución en la especificación técnica.
- **Dependencias:** Proyecto, Evidencia.

### Score

- **Definición oficial:** la cuantificación objetiva del estado de una dimensión evaluable de una Empresa (ej. Founder Score, Business Score), siempre acompañada de su nivel de confianza (AD-002 regla 1.9). Especificación de producto en AD-FUNC-07; de cálculo en AD-ARQ-10.
- **Definición prohibida:** no es una opinión estética del sistema — todo Score debe ser trazable a la evidencia que lo produjo (AD-002 reglas 1.1, 1.2).
- **Sinónimos aceptados:** el nombre calificado específico ("Founder Score") es preferible a "el score" genérico si hay ambigüedad.
- **Sinónimos prohibidos:** "calificación", "nota" — connotan evaluación escolar, no evidencia de negocio.
- **Contexto de uso:** siempre calificado por tipo cuando exista ambigüedad de cuál se discute.
- **Documentos donde aparece:** Chat 1.docx; formalización pendiente en AD-FUNC-07, AD-ARQ-10.
- **Responsable del concepto:** AD-FUNC-07 *(pendiente)*.
- **Fecha de creación:** origen del proyecto.
- **Nivel de estabilidad:** En evolución.
- **Dependencias:** Evidencia, Confidence Level.

### Evidencia

- **Definición oficial:** dato, fuente o razonamiento verificable que respalda una afirmación, recomendación o Score del sistema (AD-002 regla 1.1). La unidad mínima de justificación de todo el sistema.
- **Definición prohibida:** la inspección de una conversación por sí sola no constituye evidencia suficiente (principio heredado de la metodología original del proyecto, formalizado en AD-CMP-05).
- **Sinónimos aceptados:** ninguno.
- **Sinónimos prohibidos:** "dato" sin calificar — toda evidencia es un dato, pero no todo dato es evidencia suficiente sin contexto de fuente y verificabilidad.
- **Contexto de uso:** siempre que se justifique una Decisión, un Score o el avance de un Nivel.
- **Documentos donde aparece:** AD-001, AD-002 (regla 1.1), este documento; comportamiento formal pendiente en AD-CMP-05.
- **Responsable del concepto:** AD-CMP-05 *(pendiente)*.
- **Fecha de creación:** metodología original del proyecto ("la inspección de código no constituye evidencia suficiente").
- **Nivel de estabilidad:** Estable.
- **Dependencias:** ninguna — concepto raíz de la Regla 1.1.

### Entregable

- **Definición oficial:** documento o artefacto formal que ADÁN produce al cierre de una Card o un Nivel, sintetizando decisiones, evidencia y resultados (ej. Diagnóstico_Dolor.pdf).
- **Definición prohibida:** no es cualquier archivo generado durante una conversación — un Entregable tiene un propósito de síntesis y cierre, definido por el Nivel o Card que lo produce.
- **Sinónimos aceptados:** el nombre específico del documento (ej. "Business Model Canvas") cuando aplica.
- **Sinónimos prohibidos:** "output", "resultado" — términos genéricos que no distinguen un Entregable formal de una respuesta conversacional.
- **Contexto de uso:** al describir qué produce formalmente un Nivel o una Card al completarse.
- **Documentos donde aparece:** Chat 1.docx (por Nivel); formalización pendiente en AD-UX-09 y AD-006.
- **Responsable del concepto:** AD-006 *(pendiente)*.
- **Fecha de creación:** origen del proyecto.
- **Nivel de estabilidad:** En evolución.
- **Dependencias:** Nivel, Card, Gemelo Digital.

### Agente

- **Definición oficial:** la unidad interna de especialización de ADÁN (ej. rol de CEO, CTO, CFO) que participa en el análisis y la generación de una respuesta, invisible y no administrable por el usuario salvo que este decida inspeccionarla (AD-UX-11).
- **Definición prohibida:** no es un chatbot independiente con el que el usuario conversa directamente — el usuario conversa con ADÁN; los Agentes son internos (AD-001 §1).
- **Sinónimos aceptados:** "agente especializado" para énfasis.
- **Sinónimos prohibidos:** "bot", "asistente" — implican una entidad independiente de cara al usuario, lo cual contradice AD-001 §1.
- **Contexto de uso:** al describir la arquitectura interna multiagente, nunca la experiencia del usuario (ahí, siempre "ADÁN").
- **Documentos donde aparece:** Chat 1.docx; comportamiento en AD-CMP-02; arquitectura pendiente en AD-ARQ-03.
- **Responsable del concepto:** AD-ARQ-03 *(pendiente)*.
- **Fecha de creación:** origen del proyecto.
- **Nivel de estabilidad:** Estable en el concepto; En evolución en la especificación técnica.
- **Dependencias:** ADÁN, Orquestador.

### Board Room

- **Definición oficial:** la Funcionalidad de comité ejecutivo donde múltiples Agentes debaten, documentan desacuerdos y llegan a una recomendación única, con posibilidad de cliente y terceros invitados (AD-FUNC-02, apoyada en AD-CMP-02 y AD-CMP-03).
- **Definición prohibida:** no es una categoría de documento de primer nivel de la WO-000 — se corrigió explícitamente en la revisión de la WO-000 (es una Funcionalidad, AD-FUNC-02) — ni una vista donde el usuario administra Agentes directamente.
- **Sinónimos aceptados:** ninguno.
- **Sinónimos prohibidos:** "comité de IA", "panel de agentes".
- **Contexto de uso:** al describir la mecánica de deliberación multiagente visible al usuario.
- **Documentos donde aparece:** Blueprint v1; formalización pendiente en AD-FUNC-02.
- **Responsable del concepto:** AD-FUNC-02 *(pendiente)*.
- **Fecha de creación:** Blueprint v1.
- **Nivel de estabilidad:** En evolución.
- **Dependencias:** Agente, Decisión.

---

## 2. Vocabulario del Proceso de Documentación (WO-000)

Estos cinco términos no los encontrará un usuario final de ADÁN — existen para gobernar cómo se escribe la especificación misma. Se incluyen aquí, en vez de en un documento aparte, en cumplimiento directo de la Regla de Economía Conceptual: cinco términos no justifican un nuevo documento cuando ya existe uno diseñado exactamente para fijar vocabulario.

### Comportamiento

- **Definición oficial:** en el contexto de la WO-000, una regla de dominio que especifica qué debe pasar y por qué, sin lenguaje de implementación (categoría de documentos AD-CMP).
- **Definición prohibida:** no es una Funcionalidad (capacidad concreta del producto) ni un documento de Arquitectura (cómo se implementa técnicamente).
- **Sinónimos aceptados:** ninguno.
- **Sinónimos prohibidos:** ninguno específico — es un término de metodología documental, no de producto.
- **Contexto de uso:** exclusivamente al referirse a la categoría de documentos AD-CMP.
- **Documentos donde aparece:** WO-000_INDICE_MAESTRO (todas las versiones desde v3).
- **Responsable del concepto:** WO-000_INDICE_MAESTRO_v3.
- **Fecha de creación:** 2026-07-14.
- **Nivel de estabilidad:** Estable.
- **Dependencias:** ninguna.

### Funcionalidad

- **Definición oficial:** en el contexto de la WO-000, una capacidad concreta del producto (categoría AD-FUNC), consecuencia de aplicar los Comportamientos sobre el Domain Model.
- **Definición prohibida:** no es un Comportamiento (regla de dominio) ni un documento de UX (cómo se ve) — es la capa intermedia entre ambos.
- **Sinónimos aceptados:** ninguno.
- **Sinónimos prohibidos:** ninguno específico.
- **Contexto de uso:** exclusivamente al referirse a la categoría de documentos AD-FUNC.
- **Documentos donde aparece:** WO-000_INDICE_MAESTRO (todas las versiones desde v3).
- **Responsable del concepto:** WO-000_INDICE_MAESTRO_v3.
- **Fecha de creación:** 2026-07-14.
- **Nivel de estabilidad:** Estable.
- **Dependencias:** Comportamiento.

### Principio Permanente

- **Definición oficial:** en el contexto de la WO-000, una declaración que debería seguir siendo cierta dentro de veinte años, y que ningún documento posterior puede contradecir sin crear una nueva versión del documento que lo declara (AD-001, nota metodológica).
- **Definición prohibida:** no es sinónimo de "regla" en sentido genérico — designa específicamente contenido de máxima estabilidad, distinto de una Decisión de Diseño.
- **Sinónimos aceptados:** ninguno.
- **Sinónimos prohibidos:** "regla de negocio" — más genérico, no implica el mismo nivel de permanencia.
- **Contexto de uso:** en la etiqueta explícita "Nivel de contenido" de cualquier documento de la WO-000.
- **Documentos donde aparece:** AD-001, AD-002, WO-000_INDICE_MAESTRO v3.2 en adelante.
- **Responsable del concepto:** AD-001.
- **Fecha de creación:** 2026-07-14.
- **Nivel de estabilidad:** Estable.
- **Dependencias:** ninguna.

### Decisión de Diseño

- **Definición oficial:** en el contexto de la WO-000, una elección concreta (una lista, un ejemplo, un mecanismo específico) que ilustra un Principio Permanente en el estado actual del producto, pero que puede evolucionar sin comprometer el principio que ilustra (AD-001, nota metodológica).
- **Definición prohibida:** no es lo mismo que el objeto "Decisión" del vocabulario de producto (sección 1) — "Decisión" es una entidad de ADÁN; "Decisión de Diseño" es una categoría de contenido de la documentación de la WO-000. *Esta coincidencia de nombre es una fuente de confusión real — ver Preguntas Abiertas.*
- **Sinónimos aceptados:** ninguno.
- **Sinónimos prohibidos:** "decisión de producto" — para evitar la confusión con el objeto Decisión, se usa siempre "Decisión de Diseño" completo, nunca abreviado a "Decisión".
- **Contexto de uso:** en la etiqueta explícita "Nivel de contenido" de cualquier documento de la WO-000.
- **Documentos donde aparece:** AD-001, WO-000_INDICE_MAESTRO v3.2 en adelante.
- **Responsable del concepto:** AD-001.
- **Fecha de creación:** 2026-07-14.
- **Nivel de estabilidad:** Estable — *pendiente de decisión del Board sobre posible renombre, ver Preguntas Abiertas*.
- **Dependencias:** Principio Permanente.

### Confidence Level

- **Definición oficial:** indicador de 0 a 100% que declara cuánto de un contenido —de un documento de la WO-000 o, más adelante, de una salida de ADÁN— está respaldado por evidencia frente a cuánto es hipótesis (v3.1 §1; AD-002 regla 1.9).
- **Definición prohibida:** no es una nota de calidad de redacción — es una nota de certeza de la información.
- **Sinónimos aceptados:** "nivel de confianza" en prosa; el término técnico se mantiene en inglés por convención ya establecida desde v3.1.
- **Sinónimos prohibidos:** "score de calidad".
- **Contexto de uso:** encabezado de todo documento de la WO-000; más adelante, en toda salida relevante del producto (regla 1.9).
- **Documentos donde aparece:** todos desde v3.1.
- **Responsable del concepto:** WO-000_INDICE_MAESTRO_v3.1.
- **Fecha de creación:** 2026-07-14.
- **Nivel de estabilidad:** Estable.
- **Dependencias:** Evidencia.

---

## Dependencias

- AD-000 Paradixe Ecosystem Vision
- AD-001 Product DNA
- AD-002 Principios del Sistema (v2.0)

## Documentos relacionados

- Todo documento futuro de la WO-000 — este es el vocabulario que todos deben usar sin redefinir.
- AD-005 Enterprise Domain Model, AD-006 Domain Model, AD-007 Gemelo Digital — deben heredar las definiciones preliminares de "Empresa", "Proyecto", "Gemelo Digital", "Decisión" fijadas aquí, no reinventarlas.
- AD-FUNC-01 — debe resolver la inconsistencia de número de Niveles señalada en Preguntas Abiertas antes de considerarse completo.

## Impacto sobre otros módulos

1. Todo documento de dominio (AD-005, AD-006, AD-007, AD-008) hereda las definiciones preliminares de este documento como punto de partida obligatorio, no como sugerencia.
2. La distinción Empresa/Proyecto fijada aquí es una restricción de diseño para toda la categoría UX — ningún documento AD-UX puede usar "Proyecto" y "Workspace" como sinónimos, ni "Empresa" y "Proyecto".
3. La colisión de nombre entre "Decisión" (producto) y "Decisión de Diseño" (documentación) — ver Preguntas Abiertas — debe resolverse antes de que AD-CMP-03 (Comportamiento de Decisiones) se redacte, para evitar que el propio documento que especifica el objeto Decisión tenga que lidiar con la ambigüedad de nombre en su propio texto.

## Riesgos

- **Riesgo de definiciones preliminares que no resistan la especificación técnica real.** Diez de los 21 términos tienen su "Responsable del concepto" marcado como *(pendiente)* — este documento fija el término y su frontera conceptual, pero la especificación completa vive en un documento que todavía no existe. Si ese documento futuro encuentra que la definición preliminar no funciona, debe generar una nueva versión de AD-003, no simplemente ignorarla.
- **Riesgo de que el "Nivel de estabilidad En evolución" se use como excusa para inconsistencia.** El campo existe para ser honesto sobre incertidumbre real (coherente con AD-002 regla 1.9), no para evitar comprometerse con una definición cuando sí es posible hacerlo.

## Preguntas abiertas

1. **Colisión de nombre: "Decisión" (producto) vs. "Decisión de Diseño" (documentación).** Ambos términos son legítimos y necesarios, pero comparten la palabra "Decisión", lo cual genera un riesgo real de confusión en documentos que hablan de ambos a la vez (por ejemplo, AD-CMP-03, que especifica el objeto Decisión del producto, podría necesitar explicar decisiones de diseño sobre sí mismo). Recomendación de este documento, no aplicada automáticamente: renombrar "Decisión de Diseño" a "Elección de Diseño" o "Decisión Documental" para eliminar la ambigüedad. Queda como decisión del Board — ver Decisiones pendientes.
2. **Número real de Niveles: ¿seis o siete?** Chat 1.docx y las comunicaciones de lanzamiento citan "seis niveles estratégicos" en un lugar y describen contenido hasta "Nivel 7" (Escalamiento) en otro. Este documento no resuelve la inconsistencia — la señala para que AD-FUNC-01 la resuelva de forma definitiva, con evidencia de cuál es la intención real, no por conveniencia editorial.

## Decisiones pendientes

- Confirmar o rechazar el renombre de "Decisión de Diseño" (Pregunta Abierta 1) antes de redactar AD-CMP-03.
- Confirmar el número definitivo de Niveles (Pregunta Abierta 2) antes de redactar AD-FUNC-01.

## Historial de cambios

| Versión | Fecha | Cambio | Motivo |
|---|---|---|---|
| v1.0 | 2026-07-14 | Creación inicial: lenguaje controlado de 21 términos (16 de producto, 5 de proceso documental), cada uno con los 10 campos solicitados por el Board | Cuarto documento de la WO-000, primero auditado bajo el nuevo flujo de autoauditoría obligatoria (AD-002 v2.0) — ver autoauditoría entregada junto con este documento en la conversación de aprobación |
| v1.0 — Aprobada | 2026-07-14 | Aprobación formal del Board, sin cambios de contenido. Se congela. La autoauditoría de 10 preguntas queda ratificada como parte permanente del flujo de la WO-000 (no solo de este documento) | Cierre del ciclo de revisión de AD-003 |
