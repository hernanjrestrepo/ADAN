# WO-000 — Índice Maestro de Especificación de Producto ADÁN (v3.0)

**Tipo de documento:** Árbol documental para revisión. No contiene especificación de producto.
**Estado de la WO-000:** En diseño — pendiente de aprobación final antes de redactar AD-000.
**Supersede a:** `WO-000_INDICE_MAESTRO_v2.md` (retirado, no eliminado — cadena de evidencia: v1 → v2 → v3).
**Regla de bloqueo:** prohibido desarrollo de código o contenido de los documentos listados hasta que este índice sea aprobado.

---

## 0. Qué cambió respecto a v2 (resumen ejecutivo)

Cinco cambios estructurales, todos por la misma razón de fondo: v2 diseñaba un software; este árbol diseña un ecosistema y las empresas que ese ecosistema produce.

1. **Se agregó un nivel por encima del producto:** `AD-000 Paradixe Ecosystem Vision`, antes de `Product DNA`. ADÁN nace sabiendo que convive con EVA, ARQAI, Genexis, CSI, Marketplace, Paradixe Ventures y Applecoin — no se diseña aislado.
2. **Se agregó una capa de dominio empresarial antes del dominio de software:** `AD-005 Business Domain` (Empresa, Departamento, Proceso, Cliente, Proveedor, Activo, Pasivo, Producto, Servicio, Mercado, Competencia) precede a `AD-006 Domain Model`, porque ADÁN modela empresas, no solo pantallas y objetos de una app.
3. **El Gemelo Digital dejó de ser Funcionalidad y subió a Fundamentos.** `AD-007` (estructura) vive junto al Domain Model; su ciclo de vida es ahora `AD-CMP-06 Digital Twin Lifecycle`.
4. **Experience Engine se dividió en dos:** `AD-FUNC-03 Experience Engine` (capa de orquestación de la experiencia — tono, ritmo, cuándo se activa cada cosa) y `AD-FUNC-04 Gamification Engine` (el motor de mecánicas: oficinas, avatares, XP, ranking, Índice ADÁN, Shark Tank, mentorías).
5. **Se agregaron tres documentos nuevos:** `AD-004 Product Evolution` (reglas de evolución a 10 años, no roadmap), `AD-FUNC-09 Learning Engine` (cómo aprende/olvida/detecta sesgos el sistema — explícitamente no "Enterprise Intelligence", eso viene después) y la categoría `AD-PLAT Platform Services` (servicios compartidos: auth, notificaciones, storage, search, feature flags, calendario, correo, archivos).

**Cambio de filosofía (no agrega documentos, cambia el criterio de aceptación de todos):** cada documento debe superar una sola prueba — *si mañana desaparece todo el código, ¿este documento basta para reconstruir el sistema correctamente?* Si la respuesta es no, el documento está incompleto. Ver sección 1.

**Total en WO-000:** 58 documentos (antes 51). El crecimiento es 100% atribuible a los 8 puntos de esta retroalimentación, no a adición discrecional — el detalle de cada suma está en el resumen de cambios de cada categoría.

---

## 1. Cómo leer este índice

Mismas convenciones que v2: **Código** · **Objetivo** · **Alcance** · **Dependencias** · **Prioridad** (`P0` bloqueante · `P1` crítico · `P2` iterable · `P3` visión) · **Estado de insumos** · **Responsable** (`CC` = Claude Code, aprobación final siempre de Hernán/Junta) · **Págs./Complejidad**.

**Criterio de completitud — Prueba de Reconstrucción.** Todo documento de esta WO-000 debe redactarse pensando en una sola pregunta: *si el código de ADÁN desaparece esta noche, ¿un equipo de ingeniería distinto podría reconstruir el sistema completo leyendo solo estos documentos, sin tener que reinterpretar ni inventar nada?* No se trata de escribir documentación descriptiva — se trata de diseñar cada módulo con la precisión de una especificación de ingeniería. Esta prueba aplica a los 58 documentos por igual; no se repite fila por fila en las tablas, pero es la vara con la que se aprueba o se devuelve cada uno cuando llegue el momento de redactarlos.

**Regla de entidades (sin cambios desde v2):** ningún documento fuera de AD-005/AD-006/AD-007 puede introducir una entidad nueva. Si aparece la necesidad, ese documento se detiene y primero se modifica el documento de dominio correspondiente.

---

## 2. FUNDAMENTOS DEL ECOSISTEMA Y DEL PRODUCTO (AD-000 a AD-008) — 9 documentos

Categoría ampliada respecto a v2 (antes 5 documentos, "Fundamentos del Producto"). Ahora empieza un nivel más arriba y separa explícitamente dominio de negocio de dominio de software.

| Código | Nombre | Objetivo | Alcance | Dependencias | Prioridad | Estado insumos | Resp. | Págs. | Complejidad |
|---|---|---|---|---|---|---|---|---|---|
| AD-000 | Paradixe Ecosystem Vision | Fijar que ADÁN es un componente de un ecosistema mayor, no un producto aislado, antes de definir su propia identidad | Relación de ADÁN con EVA (financiero), ARQAI (voz/agente), Genexis (construcción), CSI (inteligencia de mercado), Marketplace, Paradixe Ventures y Applecoin; qué aporta ADÁN al ecosistema y qué recibe de él | — | **P0 — raíz de todo el árbol** | Definido en Blueprint v1 (integraciones nombradas, sin visión unificada) | CC | 6-8 | Alta |
| AD-001 | Product DNA | Fijar la identidad irrevocable de ADÁN dentro de ese ecosistema | Qué es, qué problema resuelve, para quién, por qué existe, qué jamás hará, ventaja competitiva, promesa, personalidad, filosofía | AD-000 | **P0** | Insumos en Chat 1.docx | CC | 6-8 | Media |
| AD-002 | Principios del Sistema | Declarar las reglas universales que el sistema debe cumplir siempre | Todo genera evidencia · todo es trazable · todo es reversible · toda decisión tiene responsable · nada se pierde · toda IA debe justificar · todo tiene versión · todo genera memoria. Incluye el checklist de justificación de diseño (UX/Ingeniería/Escalabilidad/Multiagentes/Performance/Seguridad/Costo) | AD-001 | **P0** | No iniciado | CC | 5-7 | Media |
| AD-003 | Product Language | Fijar el vocabulario oficial, una sola definición por término | Workspace, Proyecto, Nivel, Card, Gemelo Digital, Board Room, Prompt, Entregable, Contexto, Score, Artefacto, Decisión, etc. Ningún otro documento redefine un término aquí fijado | AD-001, AD-002 | **P0** | No iniciado | CC | 5-6 | Media |
| AD-004 | Product Evolution | Definir las reglas mediante las cuales ADÁN evoluciona sin perder coherencia — no un roadmap, un conjunto de reglas | Qué significa agregar una funcionalidad; cuándo nace un nuevo Nivel; cuándo una funcionalidad se convierte en un producto propio; mecanismos explícitos para evitar que ADÁN se convierta en un sistema inmanejable con el tiempo | AD-001, AD-003 | **P0** | No iniciado | CC | 5-7 | Alta |
| AD-005 | Business Domain | Modelar las empresas que ADÁN crea, no el software que las crea | Empresa, Departamento, Proceso, Cliente, Proveedor, Activo, Pasivo, Producto, Servicio, Mercado, Competencia — el vocabulario y las relaciones del mundo empresarial real que ADÁN necesita entender para asesorar. Este dominio se traduce después al Domain Model de software en AD-006 | AD-000, AD-001, AD-003 | **P0** | No iniciado | CC | 8-10 | Alta |
| AD-006 | Domain Model (Software) | Definir exhaustivamente las entidades del software y sus relaciones, traduciendo el Business Domain a estructuras operables por el sistema | Proyecto, Usuario, Fundador, Nivel, Card, Documento, Decisión, Agente, Workspace, Conversación, Artefacto, Entregable, Score, Objetivo, Tarea, Evento. Diagrama entidad-relación completo. Único lugar (junto con AD-005 y AD-007) donde se crean entidades nuevas | AD-005, AD-003, AD-002 | **P0 — el documento más referenciado del árbol** | Insumos en Chat 1.docx (entidades mencionadas de forma dispersa) | CC | 12-16 | Muy Alta |
| AD-007 | Gemelo Digital — Especificación Estructural | Especificar el elemento estructural del que depende todo lo demás — ya no es una funcionalidad, es el corazón del dominio | Qué representa (empresa, producto, fundador, mercado), qué agrega y versiona (decisiones, documentos, código, procesos, KPIs, evidencias), por qué el resto del sistema gira alrededor de él y no al revés. El comportamiento dinámico (cómo nace, crece, cambia) vive aparte, en AD-CMP-06 | AD-005, AD-006 | **P0 — vive al lado del Domain Model, no dentro de él** | Definido en Blueprint v1 (nombrado como pilar, sin especificar) | CC | 6-8 | Muy Alta |
| AD-008 | Objetos del Sistema | Profundizar cada entidad de AD-006/AD-007 en su ciclo de vida operativo completo | Para cada entidad: atributos, estados, ciclo de vida, acciones permitidas, permisos, relaciones, eventos que dispara, versionado | AD-006, AD-007, AD-002 | **P0** | No iniciado | CC | 18-24 | Muy Alta |

---

## 3. COMPORTAMIENTOS (AD-CMP) — 6 documentos

Sin cambios de enfoque respecto a v2 (reglas de dominio, sin vocabulario de implementación); se agrega el comportamiento del Gemelo Digital, ahora que es estructural.

| Código | Nombre | Objetivo | Alcance | Dependencias | Prioridad | Estado insumos | Resp. | Págs. | Complejidad |
|---|---|---|---|---|---|---|---|---|---|
| AD-CMP-01 | Comportamiento de Progresión entre Niveles | Especificar la regla de avance condicionado | Un Nivel no se aprueba por pago sino por evidencia; qué constituye evidencia suficiente; qué pasa si cliente y sistema no coinciden en que un nivel maduró | AD-006, AD-002 | P0 | Insumos en Chat 1.docx | CC | 5-6 | Alta |
| AD-CMP-02 | Comportamiento de Consenso Multiagente | Especificar cómo múltiples agentes producen una sola respuesta | Regla de "nunca cinco respuestas"; resolución de discrepancias internas sin exponerlas salvo que sea relevante | AD-006, AD-002 | P0 | Insumos en Chat 1.docx | CC | 5-6 | Alta |
| AD-CMP-03 | Comportamiento de Decisiones | Especificar el ciclo de vida del objeto Decisión | Quién propone, quién aprueba, cómo se documenta un desacuerdo del Board, consulta previa para evitar contradicciones | AD-006 (entidad Decisión), AD-002 | P0 | Insumos en Chat 1.docx | CC | 5-7 | Alta |
| AD-CMP-04 | Comportamiento de Memoria y Contexto | Especificar qué se recuerda, resume y descarta, sin el motor técnico | Jerarquía conceptual de contexto; regla de "nunca preguntar algo que el sistema ya sabe"; cuándo se genera un resumen | AD-006, AD-002 | P0 | Insumos en Chat 1.docx | CC | 6-8 | Alta |
| AD-CMP-05 | Comportamiento de Evidencia y Scoring | Especificar cómo una conversación se convierte en un score objetivo | Qué evidencia es válida vs. inválida; la inspección de conversación por sí sola no basta | AD-006, AD-002 | P0 | Insumos en Chat 1.docx | CC | 5-6 | Alta |
| AD-CMP-06 | Digital Twin Lifecycle | Especificar cómo cambia el Gemelo Digital en el tiempo | Cómo nace, cómo crece, cómo cambia, cómo se divide (ej. un proyecto se convierte en dos empresas), cómo se fusiona, cómo se archiva | AD-007, AD-002 | **P0** | No iniciado | CC | 5-6 | Alta |

---

## 4. FUNCIONALIDADES (AD-FUNC) — 9 documentos

`Gemelo Digital` se retira de esta categoría (elevado a AD-007). `Experience Engine` se divide en dos. Se agrega `Learning Engine`.

| Código | Nombre | Objetivo | Alcance | Dependencias | Prioridad | Estado insumos | Resp. | Págs. | Complejidad |
|---|---|---|---|---|---|---|---|---|---|
| AD-FUNC-01 | Los 7 Niveles (PRD Maestro) | Consolidar el flujo completo de creación de empresa | Objetivo, preguntas clave, documentación solicitada, metodologías, entregables y criterio de avance de cada nivel | AD-CMP-01, AD-CMP-05, AD-005 | P0 | Insumos en Chat 1.docx (niveles 1-6 detallados; nivel 7 falta) | CC | 16-20 | Alta |
| AD-FUNC-02 | Board Room | Especificar la funcionalidad de comité ejecutivo | CEO/CTO/CFO/CMO/Legal/Producto/Operaciones debatiendo con cliente y terceros invitados; votaciones y actas | AD-CMP-02, AD-CMP-03, AD-006 | P1 | Definido en Blueprint v1 | CC | 6-8 | Alta |
| AD-FUNC-03 | Experience Engine | Especificar la capa de orquestación de la experiencia — el "cómo se siente", no las mecánicas | Tono, ritmo narrativo, cuándo se activa cada elemento de la experiencia a lo largo del recorrido; punto de integración conceptual con voz (detalle técnico en AD-INT-02) | AD-001, AD-CMP-01 | P2 | Definido en Blueprint v1 | CC | 4-5 | Media |
| AD-FUNC-04 | Gamification Engine | Especificar el motor de mecánicas de juego como subsistema propio — deliberadamente el documento de Funcionalidades más extenso, porque el alcance lo justifica | Oficinas virtuales, personajes/avatares, recompensas, badges, XP, ranking, Índice ADÁN, celebraciones, Shark Tank simulado, mentorías, coaching. Puede simplificarse o diferirse en los primeros pilotos reales sin bloquear AD-FUNC-01 | AD-FUNC-03, AD-007, AD-CMP-01 | P2 | Definido en Blueprint v1 | CC | 10-14 | Muy Alta |
| AD-FUNC-05 | Marketplace | Especificar publicación de SaaS/agentes/servicios/APIs | Qué puede publicarse, cómo se descubre, cómo se cura calidad. Términos comerciales (revenue share) quedan en WO-100 | AD-006, AD-000 | P3 | Definido en Blueprint v1 | CC | 5-6 | Media |
| AD-FUNC-06 | Onboarding | Especificar la primera sesión de un usuario nuevo | Flujo desde registro hasta primera pregunta de ADÁN en Nivel 1 | AD-FUNC-01, AD-CMP-01 | P0 | Insumos en Chat 1.docx | CC | 4-5 | Media |
| AD-FUNC-07 | Sistema de Scoring (Producto) | Especificar qué significa cada score para el usuario | Founder, Problem, Solution, Business, Product, Market, Execution y Venture Score: qué mide, cuándo se muestra, qué acción habilita. La fórmula de cálculo va en AD-ARQ-10 | AD-CMP-05, AD-006 | P0 | Insumos en Chat 1.docx | CC | 8-10 | Alta |
| AD-FUNC-08 | User Journey Map | Mapear el recorrido completo de los perfiles ya identificados | Journey desde descubrimiento hasta suscripción activa, técnico vs. no técnico, individual vs. institucional | AD-FUNC-01, AD-FUNC-06 | P1 | Insumos en Chat 1.docx | CC | 6-8 | Media |
| AD-FUNC-09 | Learning Engine | Especificar cómo aprende ADÁN del conocimiento colectivo — explícitamente no es "Enterprise Intelligence" (eso es una capa posterior) | Cómo aprende de fracasos y de éxitos, cómo olvida información obsoleta, cómo detecta información incorrecta antes de incorporarla, cómo evita sesgos sistemáticos. Es el mecanismo concreto detrás del moat de "más startups → más inteligente" | AD-CMP-05, AD-007, AD-005, AD-002 | **P1 — sostiene el moat de largo plazo del ecosistema** | No iniciado | CC | 7-9 | Alta |

---

## 5. UX/UI (AD-UX) — 12 documentos

Sin cambios de alcance respecto a v2; se actualizan referencias de dependencia a los nuevos códigos de dominio (AD-006/AD-007/AD-008 en vez de los antiguos AD-003/AD-004).

| Código | Nombre | Objetivo | Alcance | Dependencias | Prioridad | Estado insumos | Resp. | Págs. | Complejidad |
|---|---|---|---|---|---|---|---|---|---|
| AD-UX-01 | Design System | Fijar el lenguaje visual y de componentes reutilizable | Tokens, tipografía, color, componentes base, estados, accesibilidad | AD-001, AD-002 | P1 | No iniciado | CC | 8-10 | Alta |
| AD-UX-02 | Workspace Principal | Especificar la pantalla contenedora tras login | Sidebar / zona central / panel derecho; cómo cambian al cambiar de Nivel | AD-UX-01, AD-006, AD-FUNC-01 | P1 | Insumos en Chat 1.docx | CC | 8-10 | Alta |
| AD-UX-03 | Dashboard General | Especificar la vista que responde "¿qué está pasando?" | Resumen ejecutivo, score (AD-FUNC-07), estado del Gemelo Digital (AD-007), próximos pasos, riesgos | AD-UX-02, AD-007, AD-FUNC-07 | P1 | Insumos en Chat 1.docx | CC | 8-10 | Alta |
| AD-UX-04 | Sidebar y Navegación | Especificar la navegación persistente | Iconos, jerarquías, estados de Nivel, badges, breadcrumbs | AD-UX-02, AD-008 | P1 | Insumos en Chat 1.docx | CC | 5-7 | Media |
| AD-UX-05 | Vista de Nivel | Especificar cómo cada uno de los 7 niveles se siente distinto | Layout por zona, paneles, Cards y widgets específicos de cada nivel | AD-UX-02, AD-FUNC-01, AD-CMP-01 | P1 | Insumos en Chat 1.docx | CC | 12-16 | Muy Alta |
| AD-UX-06 | Sistema de Cards | Especificar la unidad de trabajo dentro de un nivel | Qué muestra, qué contiene, expansión/colapso, interacción entre Cards | AD-UX-05, AD-008 | P1 | Insumos en Chat 1.docx | CC | 7-9 | Alta |
| AD-UX-07 | Chat / Conversación | Especificar la conversación como herramienta profesional | Contexto visible, documentos relacionados, agentes participantes, sesiones con resumen automático | AD-UX-06, AD-CMP-04 | P1 | Insumos en Chat 1.docx | CC | 8-10 | Alta |
| AD-UX-08 | Timeline | Especificar el registro cronológico de eventos | Navegación, filtrado, búsqueda, agrupación — entidad Evento de AD-006 | AD-006 | P2 | Insumos en Chat 1.docx | CC | 5-6 | Media |
| AD-UX-09 | Documentos (Gestor Documental) | Especificar la base documental generada por el sistema | Clasificación, generación, edición, versionado, búsqueda, enlace con chats y decisiones | AD-006, AD-008 | P2 | Insumos en Chat 1.docx | CC | 6-8 | Media |
| AD-UX-10 | Decisiones (Vista DEC) | Especificar la vista del objeto Decisión | Descripción, justificación, responsable, impacto, estado, alternativas descartadas | AD-CMP-03 | P2 | Insumos en Chat 1.docx | CC | 5-6 | Media |
| AD-UX-11 | Agentes (Consola) | Especificar la vista que expone agentes solo si el usuario decide inspeccionarlos | Estado, rol, skills, memoria, costo, tokens, rendimiento — cuándo permanece oculta | AD-CMP-02, AD-006 | P2 | Insumos en Chat 1.docx | CC | 6-7 | Media |
| AD-UX-12 | Memoria y RAG (Consolas de Contexto) | Especificar las vistas de introspección de contexto | Memoria por capas y estado del índice de recuperación documental | AD-CMP-04 | P2 | Insumos en Chat 1.docx | CC | 6-8 | Alta |

---

## 6. ARQUITECTURA (AD-ARQ) — 10 documentos

Fase 2 sin cambios de fondo; se actualizan dependencias hacia AD-006/AD-007/AD-CMP-06 y se añade el vínculo con Platform Services.

| Código | Nombre | Objetivo | Alcance | Dependencias | Prioridad | Estado insumos | Resp. | Págs. | Complejidad |
|---|---|---|---|---|---|---|---|---|---|
| AD-ARQ-01 | Arquitectura General | Vista técnica completa que traduce el dominio a implementación | Diagrama de componentes end-to-end derivado de AD-006/AD-007/AD-CMP | AD-006, AD-007, AD-008, todos los AD-CMP | P1 (Fase 2) | Insumos en Chat 1.docx | CC | 8-10 | Muy Alta |
| AD-ARQ-02 | Orquestador | Implementación técnica del comportamiento de consenso | Selección de agentes por fase, enrutamiento de contexto, selección de herramientas | AD-ARQ-01, AD-CMP-02 | P1 (Fase 2) | Insumos en Chat 1.docx | CC | 6-8 | Alta |
| AD-ARQ-03 | Multiagentes | Implementación técnica de roles y skills por agente | Roles, skills exclusivas, protocolo técnico de "respuesta única" | AD-ARQ-02 | P1 (Fase 2) | Insumos en Chat 1.docx | CC | 8-10 | Muy Alta |
| AD-ARQ-04 | Memoria (Motor Técnico) | Implementación técnica del comportamiento de memoria y del versionado del Gemelo Digital | Modelo de datos de las 7 capas de memoria, TTL, invalidación | AD-CMP-04, AD-007 | P1 (Fase 2) | Insumos en Chat 1.docx | CC | 8-10 | Muy Alta |
| AD-ARQ-05 | Context Engineering | Implementación técnica de la generación de resúmenes | Algoritmo de resumen MD, qué se pasa entre niveles, reducción de tokens | AD-ARQ-04, AD-CMP-04 | **P0 dentro de Fase 2** | Insumos en Chat 1.docx | CC | 7-9 | Alta |
| AD-ARQ-06 | RAG | Implementación técnica de indexación y recuperación documental | Chunking, embeddings, estrategia de relevancia | AD-ARQ-04, AD-UX-09 | P2 (Fase 2) | No iniciado | CC | 6-8 | Alta |
| AD-ARQ-07 | Eventos | Implementación técnica del registro append-only | Esquema de evento, event sourcing vs. log simple, retención | AD-006, AD-UX-08 | P2 (Fase 2) | No iniciado | CC | 5-6 | Media |
| AD-ARQ-08 | APIs | Contratos internos y de integración | Convenciones, versionado, contrato común consumido por integraciones y por Platform Services | AD-ARQ-01, AD-PLAT-01 | P1 (Fase 2) | No iniciado | CC | 6-8 | Alta |
| AD-ARQ-09 | Seguridad | Aislamiento de datos y control de acceso | Autenticación, aislamiento por proyecto/tenant, cifrado, gestión de secretos | AD-ARQ-01 | P1 (Fase 2) | No iniciado | CC | 8-10 | Alta |
| AD-ARQ-10 | Motor de Scoring (Cálculo) | Implementación técnica de AD-FUNC-07 | Fórmula, pesos, umbrales, comparación contra mercado | AD-FUNC-07, AD-CMP-05 | P1 (Fase 2) | Insumos en Chat 1.docx | CC | 6-8 | Alta |

---

## 7. INTELIGENCIA ARTIFICIAL (AD-IA) — 4 documentos

Sin cambios respecto a v2.

| Código | Nombre | Objetivo | Alcance | Dependencias | Prioridad | Estado insumos | Resp. | Págs. | Complejidad |
|---|---|---|---|---|---|---|---|---|---|
| AD-IA-01 | Modelos y Routing | Fijar qué modelo se usa para qué tarea | Haiku/Sonnet/Opus por tipo de tarea; STT/TTS propios; CPU vs. GPU | AD-ARQ-02 | P1 (Fase 2) | Definido en Blueprint v1 | CC | 5-6 | Media |
| AD-IA-02 | Prompt Engineering y Evaluación de Calidad | Especificar diseño y validación de prompts por agente y nivel | Plantillas por rol, criterios de evaluación ("proceso Outlier") | AD-IA-01, AD-ARQ-03 | P2 (Fase 2) | Insumos en Chat 1.docx | CC | 6-8 | Alta |
| AD-IA-03 | Costos de Inferencia | Medir el costo real de tokens por proyecto y nivel | Costo por modelo, por nivel, proyección a escala. Se queda en WO-000 porque mide consumo del sistema; la decisión de precio es de WO-100 | AD-IA-01, AD-ARQ-05 | **P0 dentro de Fase 2** | No iniciado | CC | 5-7 | Alta |
| AD-IA-04 | Optimización | Caching, batching, reducción de latencia | Estrategias de reducción de costo/tiempo sin degradar calidad | AD-IA-03 | P3 (Fase 2) | No iniciado | CC | 4-5 | Media |

---

## 8. OPERACIÓN (AD-OPS) — 3 documentos

Sin cambios de alcance; se vincula Auditoría al nuevo servicio compartido de Platform Services.

| Código | Nombre | Objetivo | Alcance | Dependencias | Prioridad | Estado insumos | Resp. | Págs. | Complejidad |
|---|---|---|---|---|---|---|---|---|---|
| AD-OPS-01 | Observabilidad y Logging | Especificar monitoreo y registro en producción | Métricas de sistema, logs estructurados, alertas | AD-ARQ-01 | P2 (Fase 2) | No iniciado | CC | 5-6 | Media |
| AD-OPS-02 | Auditoría | Especificar el rastro inmutable exigido por AD-002 | Qué se audita, retención, quién consulta el log; se apoya en el servicio técnico de AD-PLAT-01 | AD-002, AD-ARQ-07, AD-PLAT-01 | P1 (Fase 2) | No iniciado | CC | 4-5 | Media |
| AD-OPS-03 | Billing (Técnico) | Especificar cobro, facturación y manejo de impagos a nivel de integración | Pasarela de pago, ciclo de suscripción, dunning — sin definir precios (eso es WO-100) | AD-ARQ-08 | P2 (Fase 2) | No iniciado | CC | 5-6 | Media |

---

## 9. PLATFORM SERVICES (AD-PLAT) — 1 documento

Categoría nueva. Se consolida en un solo documento deliberadamente — nueve servicios compartidos no justifican nueve documentos separados en esta fase; fragmentarlos sería exactamente el tipo de sobre-especificación que el propio cierre de tu retroalimentación advierte evitar.

| Código | Nombre | Objetivo | Alcance | Dependencias | Prioridad | Estado insumos | Resp. | Págs. | Complejidad |
|---|---|---|---|---|---|---|---|---|---|
| AD-PLAT-01 | Platform Services | Especificar los servicios transversales que no pertenecen a ningún módulo de producto | Autenticación, Notificaciones, Storage, Search, Audit (técnico), Feature Flags, Calendario, Correo, Archivos — contrato de cada uno, quién lo consume, no la implementación interna del proveedor elegido | AD-ARQ-01, AD-ARQ-09 | P1 (Fase 2) | No iniciado | CC | 6-8 | Media |

---

## 10. INTEGRACIONES (AD-INT) — 4 documentos

Sin cambios respecto a v2.

| Código | Nombre | Objetivo | Alcance | Dependencias | Prioridad | Estado insumos | Resp. | Págs. | Complejidad |
|---|---|---|---|---|---|---|---|---|---|
| AD-INT-01 | Integración EVA | Contrato con el cerebro financiero/estratégico | Qué entrega ADÁN, qué recibe de vuelta | AD-ARQ-08 | P2 (Fase 2) | Definido en Blueprint v1 | CC | 4-5 | Media |
| AD-INT-02 | Integración ARQAI | Contrato con el motor de voz/agente conversacional | Uso de voz en Experience/Gamification Engine, reutilización del runtime existente | AD-ARQ-08 | P2 (Fase 2) | Insumos externos (repo Claro/ARQAI) | CC | 4-5 | Media |
| AD-INT-03 | Integración Genexis | Contrato con el motor de construcción de software | Qué especificación entrega ADÁN, qué entrega Genexis | AD-ARQ-08 | P2 (Fase 2) | Definido en Blueprint v1 | CC | 4-5 | Media |
| AD-INT-04 | Integración CSI | Contrato con el sistema de inteligencia de mercado | Qué investigación/competencia entrega CSI | AD-ARQ-08 | P2 (Fase 2) | Definido en Blueprint v1 | CC | 4-5 | Media |

---

## 11. Totales de la WO-000

| Categoría | Docs (v2) | Docs (v3) |
|---|---|---|
| Fundamentos (Ecosistema y Producto) | 5 | 9 |
| Comportamientos | 5 | 6 |
| Funcionalidades | 8 | 9 |
| UX/UI | 12 | 12 |
| Arquitectura | 10 | 10 |
| Inteligencia Artificial | 4 | 4 |
| Operación | 3 | 3 |
| Platform Services | 0 | 1 |
| Integraciones | 4 | 4 |
| **Total WO-000** | **51** | **58** |

**Páginas estimadas:** ~370-460. **Fase 1 (Fundamentos + Comportamientos + Funcionalidades, lo único redactable hasta nueva orden):** 24 documentos, ~190-230 páginas.

---

## 12. Secuenciación (backbone confirmada)

```
Paradixe Ecosystem Vision (AD-000)
  → Product DNA (AD-001)
    → Principios del Sistema (AD-002)
      → Product Language (AD-003)
        → Product Evolution (AD-004)
          → Business Domain (AD-005)
            → Domain Model (AD-006) + Gemelo Digital (AD-007)
              → Objetos del Sistema (AD-008)
                → Comportamientos (AD-CMP-01..06)
                  → Funcionalidades (AD-FUNC-01..09)
                    → UX/UI (AD-UX-01..12)
                      → Arquitectura (AD-ARQ-01..10) + Platform Services (AD-PLAT-01)
                        → Integraciones (AD-INT-01..04)
```

IA y Operación corren en paralelo a Arquitectura (Fase 2), no antes.

---

## 13. Reservado para WO-100 — Business Architecture (sin cambios respecto a v2)

Los 13 documentos comerciales listados en v2 (Modelo de Negocio SaaS, Pricing, Unit Economics, Modelo Financiero, Programa AAA/Ventures, Análisis Competitivo, GTM Institucional, Operación Continua, Marco Legal/Regulatorio, Playbook de Ventas, Convenios Institucionales, Billing-precio, Analytics de Negocio) siguen fuera de esta WO-000 y no se detallan aquí.

---

## 14. Nota de cierre — dos observaciones que no son parte del árbol

**Sobre "una iteración más y empezamos a construir":** de acuerdo. Este árbol ya cubre ecosistema, dominio de negocio, dominio de software, comportamiento y funcionalidad con la profundidad que pediste. Mantuve deliberadamente en 1 documento lo que pudo haber sido 9 (Platform Services) precisamente para no contradecir tu propia advertencia de parálisis por diseño en el mismo mensaje donde la hiciste.

**Sobre la secuencia real de trabajo, fuera del árbol:** el árbol es agnóstico a quién es dueño del código hoy. Pero antes de que la Fase 2 (Arquitectura) llegue a construirse de verdad, sigue sin resolverse lo que señalé en la primera conversación: el código actual de ADÁN corre en una infraestructura controlada por un socio en conflicto, y ese punto quedó reservado en WO-100 bajo Marco Legal. Ese tema no bloquea redactar AD-000 en adelante — es documentación de producto, no depende de quién posea el repositorio — pero sí debería resolverse en paralelo, no después, porque construir 58 documentos de especificación sobre una base de propiedad intelectual todavía en disputa es el tipo de riesgo que ninguna cantidad de rigor documental resuelve.

---

**Pendiente de tu aprobación final:** este árbol v3. Si lo apruebas, empiezo por AD-000 — Paradixe Ecosystem Vision.
