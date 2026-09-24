# WO-000 — Índice Maestro de Especificación de Producto ADÁN (v2.0)

**Tipo de documento:** Árbol documental para revisión. No contiene especificación de producto.
**Estado de la WO-000:** En diseño — pendiente de aprobación del árbol antes de redactar cualquier documento.
**Supersede a:** `WO-000_INDICE_MAESTRO_v1.md` (retirado, no eliminado — queda como evidencia del primer intento y de la corrección aplicada).
**Regla de bloqueo:** prohibido desarrollo de código o contenido de los documentos listados hasta que este índice sea aprobado.

---

## 0. Qué cambió respecto a v1 (resumen ejecutivo)

v1 respondía "¿qué documentos necesitamos?". Este árbol responde primero "¿qué producto estamos construyendo?" y solo después deriva documentos. Cuatro cambios estructurales:

1. **Se extrajo todo lo comercial.** 13 documentos (Pricing, Unit Economics, Modelo Financiero, GTM, Ventas, Convenios, Billing de negocio, Marco Legal societario, etc.) salen de la WO-000 y quedan reservados para una futura **WO-100 — Business Architecture** (sección 12). La WO-000 ahora describe el producto, no la empresa.
2. **Se insertó la columna vertebral pedida:** `Product DNA → Principios del Sistema → Product Language → Domain Model → Objetos del Sistema → Comportamientos → Funcionalidades → UX → Arquitectura → Integraciones`. Antes, UX y Arquitectura arrancaban sin que existiera un modelo de dominio; ahora dependen explícitamente de él.
3. **Board Room y Marketplace dejaron de ser documentos maestros de primer nivel.** Ahora son Funcionalidades (sección 6), como pediste.
4. **La categoría "Enterprise Intelligence" se disolvió.** Su parte de producto (qué significa cada score para el usuario) pasó a Funcionalidades; su parte de cálculo (fórmulas, pesos) pasó a Arquitectura, como documento técnico tardío — separando "qué mide" de "cómo se calcula", que antes estaban mezclados.

**Total en WO-000 (producto):** 51 documentos. **Total reservado en WO-100 (negocio, sin detallar todavía):** 13 documentos. El total combinado (64) es coherente con v1 (60); lo que cambió es la frontera, no el volumen de trabajo real.

---

## 1. Cómo leer este índice

Mismas convenciones que v1: **Código** (`AD-<CATEGORÍA>-<NN>`) · **Objetivo** · **Alcance** · **Dependencias** · **Prioridad** (`P0` bloqueante · `P1` crítico · `P2` iterable · `P3` visión) · **Estado de insumos** · **Responsable** (`CC` = Claude Code, aprobación final siempre de Hernán/Junta) · **Págs./Complejidad** estimadas.

**Regla nueva, explícita:** ningún documento de UX, Arquitectura, Funcionalidades o Comportamientos puede introducir una entidad que no exista en AD-003 Domain Model. Si durante la redacción de cualquier documento posterior aparece la necesidad de una entidad nueva, ese documento se detiene y primero se modifica AD-003.

---

## 2. FUNDAMENTOS DEL PRODUCTO (AD-000 a AD-004) — 5 documentos

Esta categoría reemplaza a la antigua "Gobierno" de v1. `AD-GOV-01 Constitución` y `AD-PRD-01 Product Vision` de v1 quedan retirados: su contenido lo absorbe AD-000. `AD-GOV-04 Glosario Maestro` queda retirado: lo absorbe AD-002. `AD-GOV-02 Filosofía y Principios de Diseño` (el checklist de justificación) queda absorbido como una sección dentro de AD-001, no como documento propio.

| Código | Nombre | Objetivo | Alcance | Dependencias | Prioridad | Estado insumos | Resp. | Págs. | Complejidad |
|---|---|---|---|---|---|---|---|---|---|
| AD-000 | Product DNA | Fijar la identidad irrevocable de ADÁN antes de que exista ningún otro documento | Qué es, qué problema resuelve, para quién existe, por qué existe, qué jamás hará, ventaja competitiva, promesa, personalidad, filosofía. Absorbe la antigua Constitución del Producto y Product Vision | — | **P0 — raíz de todo el árbol** | Insumos en Chat 1.docx (mucho ya discutido de forma dispersa) | CC | 6-8 | Media |
| AD-001 | Principios del Sistema | Declarar las reglas universales que el sistema debe cumplir siempre, antes de modelar nada | Todo genera evidencia · todo es trazable · todo es reversible · toda decisión tiene responsable · nada se pierde · toda IA debe justificar su respuesta · todo tiene versión · todo genera memoria. Incluye, como sección, el checklist de justificación de diseño (UX/Ingeniería/Escalabilidad/Multiagentes/Performance/Seguridad/Costo) que hereda de la antigua AD-GOV-02 | AD-000 | **P0** | No iniciado | CC | 5-7 | Media |
| AD-002 | Product Language | Fijar el vocabulario oficial: una sola definición por término, reutilizada por referencia en todo el resto | Workspace, Proyecto, Nivel, Card, Gemelo Digital, Board Room, Prompt, Entregable, Contexto, Objetivo, Score, Artefacto, Decisión, etc. Ningún otro documento puede redefinir un término aquí ya fijado | AD-000, AD-001 | **P0** | No iniciado | CC | 5-6 | Media |
| AD-003 | Domain Model | Definir exhaustivamente las entidades del dominio y sus relaciones — el documento más referenciado de todo el árbol | Proyecto, Empresa, Usuario, Fundador, Nivel, Card, Documento, Decisión, Agente, Workspace, Conversación, Artefacto, Entregable, Score, Objetivo, Tarea, Evento, y Gemelo Digital como entidad agregadora central. Diagrama entidad-relación completo. Único lugar donde se crean entidades nuevas | AD-002 | **P0 — el documento más importante del árbol** | Insumos en Chat 1.docx (entidades mencionadas de forma dispersa: Nivel, Card, Decisión, Gemelo Digital) | CC | 12-16 | Muy Alta |
| AD-004 | Objetos del Sistema | Profundizar cada entidad de AD-003 en su ciclo de vida operativo completo | Para cada entidad: atributos, estados, ciclo de vida, acciones permitidas, permisos, relaciones, eventos que dispara, versionado. Documento extenso por diseño — no se fragmenta porque la coherencia entre entidades es el punto | AD-003, AD-001 | **P0** | No iniciado | CC | 18-24 | Muy Alta |

---

## 3. COMPORTAMIENTOS (AD-CMP) — 5 documentos

Categoría nueva, no existía en v1. Define reglas de negocio a **nivel de dominio** (qué debe pasar y por qué) — deliberadamente sin lenguaje de implementación (nada de API, RAG, embeddings). La traducción técnica de estos comportamientos vive después, en Arquitectura.

| Código | Nombre | Objetivo | Alcance | Dependencias | Prioridad | Estado insumos | Resp. | Págs. | Complejidad |
|---|---|---|---|---|---|---|---|---|---|
| AD-CMP-01 | Comportamiento de Progresión entre Niveles | Especificar la regla de avance condicionado sin describir cómo se implementa | Un Nivel no se aprueba por pago sino por evidencia; qué constituye "evidencia suficiente" a nivel conceptual; qué pasa si el cliente y el sistema no están de acuerdo en que un nivel está maduro | AD-003, AD-001 | P0 | Insumos en Chat 1.docx ("no se avanza sin score", "cliente debe estar 100% de acuerdo") | CC | 5-6 | Alta |
| AD-CMP-02 | Comportamiento de Consenso Multiagente | Especificar cómo múltiples agentes producen una sola respuesta coherente | Regla de "nunca cinco respuestas"; qué pasa cuando dos agentes internos discrepan; cómo se resuelve sin exponer la discrepancia al usuario salvo que sea relevante | AD-003, AD-001 | P0 | Insumos en Chat 1.docx | CC | 5-6 | Alta |
| AD-CMP-03 | Comportamiento de Decisiones | Especificar el ciclo de vida del objeto Decisión definido en AD-003 | Quién propone, quién aprueba, cómo se documenta un desacuerdo del Board, cómo se consulta antes de responder para evitar contradicciones | AD-003 (entidad Decisión), AD-001 | P0 | Insumos en Chat 1.docx (mecanismo ya descrito en detalle) | CC | 5-7 | Alta |
| AD-CMP-04 | Comportamiento de Memoria y Contexto | Especificar qué se recuerda, qué se resume y qué se descarta, sin especificar el motor técnico que lo hace posible | Jerarquía conceptual de contexto (Global→Proyecto→Nivel→Card→Chat); regla de "nunca preguntar algo que el sistema ya sabe"; cuándo se genera un resumen y qué debe contener | AD-003, AD-001 | P0 | Insumos en Chat 1.docx (mecanismo de resúmenes MD ya descrito) | CC | 6-8 | Alta |
| AD-CMP-05 | Comportamiento de Evidencia y Scoring | Especificar cómo una conversación se convierte en un score objetivo, sin definir la fórmula exacta | Qué tipo de evidencia es válida (dato de mercado, testimonio, benchmark) vs. cuál no lo es; regla de que la inspección de código/conversación no es evidencia suficiente por sí sola | AD-003, AD-001 | P0 | Insumos en Chat 1.docx | CC | 5-6 | Alta |

---

## 4. FUNCIONALIDADES (AD-FUNC) — 8 documentos

Categoría nueva. Aquí viven las capacidades concretas del producto, incluyendo Board Room y Marketplace ya degradados de categoría a funcionalidad, como pediste.

| Código | Nombre | Objetivo | Alcance | Dependencias | Prioridad | Estado insumos | Resp. | Págs. | Complejidad |
|---|---|---|---|---|---|---|---|---|---|
| AD-FUNC-01 | Los 7 Niveles (PRD Maestro) | Consolidar el flujo completo de creación de empresa en un PRD único | Objetivo, preguntas clave, documentación solicitada, metodologías, entregables y criterio de avance de cada uno de los 7 niveles | AD-CMP-01, AD-CMP-05 | P0 | Insumos en Chat 1.docx (niveles 1-6 ya discutidos en detalle; nivel 7 falta) | CC | 16-20 | Alta |
| AD-FUNC-02 | Gemelo Digital — Funcionalidad de Producto | Especificar qué ve y qué puede hacer el usuario con su Gemelo Digital (la entidad ya está definida en AD-003) | Cómo se presenta al usuario, qué acciones dispara, por qué es la "fuente de verdad" que el usuario percibe | AD-003 (entidad Gemelo Digital), AD-CMP-04 | P0 | Definido en Blueprint v1 (nombrado, no especificado) | CC | 5-6 | Alta |
| AD-FUNC-03 | Board Room | Especificar la funcionalidad de comité ejecutivo — ya no es documento maestro independiente | CEO/CTO/CFO/CMO/Legal/Producto/Operaciones debatiendo con cliente y terceros invitados; votaciones y actas, apoyado en AD-CMP-02 y AD-CMP-03 | AD-CMP-02, AD-CMP-03, AD-003 | P1 | Definido en Blueprint v1 | CC | 6-8 | Alta |
| AD-FUNC-04 | Experience Engine | Especificar gamificación, avatares, voz, Shark Tank simulado, Índice ADÁN | Mecánicas de progreso visibles al usuario; integración conceptual con voz (detalle técnico de integración va en AD-INT-02) | AD-000, AD-CMP-01 | P2 | Definido en Blueprint v1 | CC | 7-9 | Alta |
| AD-FUNC-05 | Marketplace | Especificar la funcionalidad de publicación de SaaS/agentes/servicios/APIs — ya no es documento maestro independiente | Qué puede publicarse, cómo se descubre, cómo se cura calidad. Los términos comerciales (revenue share) quedan fuera, reservados a WO-100 | AD-003, AD-000 | P3 | Definido en Blueprint v1 | CC | 5-6 | Media |
| AD-FUNC-06 | Onboarding | Especificar la primera sesión de un usuario nuevo | Flujo desde registro hasta primera pregunta de ADÁN en Nivel 1 — reclasificado desde "Comercial" en v1, porque es un flujo de producto, no una decisión de negocio | AD-FUNC-01, AD-CMP-01 | P0 | Insumos en Chat 1.docx | CC | 4-5 | Media |
| AD-FUNC-07 | Sistema de Scoring (Producto) | Especificar qué significa cada score para el usuario y por qué le importa — sin la fórmula de cálculo, que va en AD-ARQ-10 | Founder, Problem, Solution, Business, Product, Market, Execution y Venture Score: qué mide cada uno, cuándo se muestra, qué acción habilita. Consolida lo que en v1 eran 4 documentos de "Enterprise Intelligence" | AD-CMP-05, AD-003 | P0 | Insumos en Chat 1.docx (metodología de pesos y ranking ya discutida en Nivel 2) | CC | 8-10 | Alta |
| AD-FUNC-08 | User Journey Map | Mapear el recorrido completo de los perfiles ya identificados como distintos (técnico vs. no técnico, individual vs. institucional) | Journey desde descubrimiento hasta suscripción activa, con puntos de fricción explícitos | AD-FUNC-01, AD-FUNC-06 | P1 | Insumos en Chat 1.docx (perfilamiento por lenguaje técnico ya discutido) | CC | 6-8 | Media |

---

## 5. UX/UI (AD-UX) — 12 documentos

Mismo alcance que v1, **pero ahora depende explícitamente del dominio, no lo antecede.** Antes de este bloque debe existir AD-003, AD-004 y todos los AD-CMP. Ninguna pantalla se diseña antes de saber qué objetos, estados y comportamientos va a mostrar.

| Código | Nombre | Objetivo | Alcance | Dependencias | Prioridad | Estado insumos | Resp. | Págs. | Complejidad |
|---|---|---|---|---|---|---|---|---|---|
| AD-UX-01 | Design System | Fijar el lenguaje visual y de componentes reutilizable | Tokens, tipografía, color, componentes base, estados, accesibilidad | AD-000, AD-001 | P1 | No iniciado | CC | 8-10 | Alta |
| AD-UX-02 | Workspace Principal | Especificar la pantalla contenedora tras login | Sidebar / zona central / panel derecho; cómo cambian al cambiar de Nivel (entidad definida en AD-003) | AD-UX-01, AD-003, AD-FUNC-01 | P1 | Insumos en Chat 1.docx | CC | 8-10 | Alta |
| AD-UX-03 | Dashboard General | Especificar la vista que responde "¿qué está pasando?" | Resumen ejecutivo, score (AD-FUNC-07), estado del Gemelo Digital (AD-FUNC-02), próximos pasos, riesgos | AD-UX-02, AD-FUNC-02, AD-FUNC-07 | P1 | Insumos en Chat 1.docx | CC | 8-10 | Alta |
| AD-UX-04 | Sidebar y Navegación | Especificar la navegación persistente | Iconos, jerarquías, estados de Nivel (bloqueado/desbloqueado, definidos en AD-004), badges, breadcrumbs | AD-UX-02, AD-004 | P1 | Insumos en Chat 1.docx | CC | 5-7 | Media |
| AD-UX-05 | Vista de Nivel | Especificar cómo cada uno de los 7 niveles se siente distinto | Layout por zona, paneles, Cards (entidad de AD-003) y widgets específicos de cada nivel | AD-UX-02, AD-FUNC-01, AD-CMP-01 | P1 | Insumos en Chat 1.docx (especificación por nivel 1-7 ya redactada) | CC | 12-16 | Muy Alta |
| AD-UX-06 | Sistema de Cards | Especificar la unidad de trabajo dentro de un nivel | Qué muestra, qué contiene, expansión/colapso, interacción entre Cards — usa la entidad Card de AD-003 y su ciclo de vida de AD-004 | AD-UX-05, AD-004 | P1 | Insumos en Chat 1.docx | CC | 7-9 | Alta |
| AD-UX-07 | Chat / Conversación | Especificar la conversación como herramienta profesional | Contexto visible, documentos relacionados, agentes participantes, sesiones con inicio/desarrollo/conclusión/resumen automático (comportamiento definido en AD-CMP-04) | AD-UX-06, AD-CMP-04 | P1 | Insumos en Chat 1.docx | CC | 8-10 | Alta |
| AD-UX-08 | Timeline | Especificar el registro cronológico de eventos | Cómo se navega, filtra, busca y agrupa — usa la entidad Evento de AD-003 | AD-003 | P2 | Insumos en Chat 1.docx | CC | 5-6 | Media |
| AD-UX-09 | Documentos (Gestor Documental) | Especificar la base documental generada por el sistema | Clasificación, generación, edición, versionado, búsqueda, enlace con chats y decisiones — usa la entidad Documento/Artefacto de AD-003 | AD-003, AD-004 | P2 | Insumos en Chat 1.docx | CC | 6-8 | Media |
| AD-UX-10 | Decisiones (Vista DEC) | Especificar la vista del objeto Decisión | Descripción, justificación, responsable, impacto, estado, alternativas descartadas — usa la entidad y comportamiento definidos en AD-003/AD-CMP-03 | AD-CMP-03 | P2 | Insumos en Chat 1.docx | CC | 5-6 | Media |
| AD-UX-11 | Agentes (Consola) | Especificar la vista que expone agentes solo cuando el usuario decide inspeccionarlos | Estado, rol, skills, memoria, costo, tokens, rendimiento — y cuándo permanece oculta por defecto | AD-CMP-02, AD-003 | P2 | Insumos en Chat 1.docx | CC | 6-7 | Media |
| AD-UX-12 | Memoria y RAG (Consolas de Contexto) | Especificar las vistas de introspección de contexto | Memoria por capas y estado del índice de recuperación documental — vista conceptual, la implementación técnica va en AD-ARQ-04/06 | AD-CMP-04 | P2 | Insumos en Chat 1.docx | CC | 6-8 | Alta |

---

## 6. ARQUITECTURA (AD-ARQ) — 10 documentos

**Se retrasa deliberadamente**, tal como pediste. Ningún documento de esta categoría se redacta hasta que Fundamentos + Comportamientos + Funcionalidades estén cerrados — su función es traducir a implementación lo que ya quedó definido en dominio, no inventar dominio sobre la marcha.

| Código | Nombre | Objetivo | Alcance | Dependencias | Prioridad | Estado insumos | Resp. | Págs. | Complejidad |
|---|---|---|---|---|---|---|---|---|---|
| AD-ARQ-01 | Arquitectura General | Vista técnica completa que traduce AD-003/AD-004 en sistema | Diagrama de componentes end-to-end, ahora derivado del Domain Model en vez de precederlo | AD-003, AD-004, todos los AD-CMP | P1 (Fase 2) | Insumos en Chat 1.docx | CC | 8-10 | Muy Alta |
| AD-ARQ-02 | Orquestador | Implementación técnica del comportamiento de consenso (AD-CMP-02) | Selección de agentes por fase, enrutamiento de contexto, selección de herramientas | AD-ARQ-01, AD-CMP-02 | P1 (Fase 2) | Insumos en Chat 1.docx | CC | 6-8 | Alta |
| AD-ARQ-03 | Multiagentes | Implementación técnica de roles y skills por agente | Roles (CEO/CTO/CFO/CMO/Legal/Ops), skills exclusivas, protocolo técnico de "respuesta única" | AD-ARQ-02 | P1 (Fase 2) | Insumos en Chat 1.docx | CC | 8-10 | Muy Alta |
| AD-ARQ-04 | Memoria (Motor Técnico) | Implementación técnica del comportamiento de memoria (AD-CMP-04) | Modelo de datos de las 7 capas de memoria, TTL, invalidación | AD-CMP-04 | P1 (Fase 2) | Insumos en Chat 1.docx | CC | 8-10 | Muy Alta |
| AD-ARQ-05 | Context Engineering | Implementación técnica de la generación de resúmenes | Algoritmo de resumen MD, qué se pasa entre niveles, reducción de tokens | AD-ARQ-04, AD-CMP-04 | **P0 dentro de Fase 2 — condiciona costo unitario** | Insumos en Chat 1.docx (mecanismo ya descrito) | CC | 7-9 | Alta |
| AD-ARQ-06 | RAG | Implementación técnica de indexación y recuperación documental | Chunking, embeddings, estrategia de relevancia | AD-ARQ-04, AD-UX-09 | P2 (Fase 2) | No iniciado | CC | 6-8 | Alta |
| AD-ARQ-07 | Eventos | Implementación técnica del registro append-only | Esquema de evento, event sourcing vs. log simple, retención | AD-003 (entidad Evento), AD-UX-08 | P2 (Fase 2) | No iniciado | CC | 5-6 | Media |
| AD-ARQ-08 | APIs | Contratos internos y de integración | Convenciones, versionado, contrato común consumido por integraciones externas | AD-ARQ-01 | P1 (Fase 2) | No iniciado | CC | 6-8 | Alta |
| AD-ARQ-09 | Seguridad | Aislamiento de datos y control de acceso | Autenticación, aislamiento por proyecto/tenant, cifrado, gestión de secretos | AD-ARQ-01 | P1 (Fase 2) | No iniciado | CC | 8-10 | Alta |
| AD-ARQ-10 | Motor de Scoring (Cálculo) | Implementación técnica de AD-FUNC-07: fórmula, pesos, umbrales | Cómo se calcula cada score numéricamente, de dónde saca sus datos, cómo se compara contra mercado | AD-FUNC-07, AD-CMP-05 | P1 (Fase 2) | Insumos en Chat 1.docx (metodología de pesos ya discutida) | CC | 6-8 | Alta |

---

## 7. INTELIGENCIA ARTIFICIAL (AD-IA) — 4 documentos

También Fase 2 — depende de que Orquestador y Multiagentes (arquitectura) estén definidos primero.

| Código | Nombre | Objetivo | Alcance | Dependencias | Prioridad | Estado insumos | Resp. | Págs. | Complejidad |
|---|---|---|---|---|---|---|---|---|---|
| AD-IA-01 | Modelos y Routing | Fijar qué modelo se usa para qué tarea | Haiku/Sonnet/Opus por tipo de tarea; STT/TTS propios; CPU vs. GPU | AD-ARQ-02 | P1 (Fase 2) | Definido en Blueprint v1 | CC | 5-6 | Media |
| AD-IA-02 | Prompt Engineering y Evaluación de Calidad | Especificar diseño y validación de prompts por agente y nivel | Plantillas por rol, criterios de evaluación ("proceso Outlier" mencionado en conversaciones) | AD-IA-01, AD-ARQ-03 | P2 (Fase 2) | Insumos en Chat 1.docx | CC | 6-8 | Alta |
| AD-IA-03 | Costos de Inferencia | Medir el costo real de tokens por proyecto y nivel — dato técnico, no decisión de precio | Costo por modelo, por nivel, proyección a escala. Este documento **se queda en WO-000** porque mide consumo del sistema; la decisión de qué cobrar por ese consumo es de WO-100 | AD-IA-01, AD-ARQ-05 | **P0 dentro de Fase 2 — insumo directo de la futura WO-100** | No iniciado | CC | 5-7 | Alta |
| AD-IA-04 | Optimización | Caching, batching, reducción de latencia | Estrategias de reducción de costo/tiempo sin degradar calidad | AD-IA-03 | P3 (Fase 2) | No iniciado | CC | 4-5 | Media |

---

## 8. OPERACIÓN (AD-OPS) — 3 documentos

Se retira `Analytics` de v1 (era una métrica de negocio: CAC/LTV/conversión — pasa a WO-100). `Billing` se queda porque su alcance aquí es técnico (integración con pasarela, ciclo de facturación), no la decisión de cuánto cobrar.

| Código | Nombre | Objetivo | Alcance | Dependencias | Prioridad | Estado insumos | Resp. | Págs. | Complejidad |
|---|---|---|---|---|---|---|---|---|---|
| AD-OPS-01 | Observabilidad y Logging | Especificar monitoreo y registro en producción | Métricas de sistema, logs estructurados, alertas | AD-ARQ-01 | P2 (Fase 2) | No iniciado | CC | 5-6 | Media |
| AD-OPS-02 | Auditoría | Especificar el rastro inmutable exigido por AD-001 | Qué se audita, retención, quién consulta el log | AD-001, AD-ARQ-07 | P1 (Fase 2) | No iniciado | CC | 4-5 | Media |
| AD-OPS-03 | Billing (Técnico) | Especificar cobro, facturación y manejo de impagos a nivel de integración | Pasarela de pago, ciclo de suscripción, dunning — sin definir precios (eso es WO-100) | AD-ARQ-08 | P2 (Fase 2) | No iniciado | CC | 5-6 | Media |

---

## 9. INTEGRACIONES (AD-INT) — 4 documentos

Última categoría, sin cambios de contenido respecto a v1, pero ahora explícitamente al final de la secuencia.

| Código | Nombre | Objetivo | Alcance | Dependencias | Prioridad | Estado insumos | Resp. | Págs. | Complejidad |
|---|---|---|---|---|---|---|---|---|---|
| AD-INT-01 | Integración EVA | Contrato con el cerebro financiero/estratégico | Qué entrega ADÁN, qué recibe de vuelta | AD-ARQ-08 | P2 (Fase 2) | Definido en Blueprint v1 | CC | 4-5 | Media |
| AD-INT-02 | Integración ARQAI | Contrato con el motor de voz/agente conversacional | Uso de voz en Experience Engine (AD-FUNC-04), reutilización del runtime existente | AD-ARQ-08 | P2 (Fase 2) | Insumos externos (repo Claro/ARQAI) | CC | 4-5 | Media |
| AD-INT-03 | Integración Genexis | Contrato con el motor de construcción de software | Qué especificación entrega ADÁN, qué entrega Genexis | AD-ARQ-08 | P2 (Fase 2) | Definido en Blueprint v1 | CC | 4-5 | Media |
| AD-INT-04 | Integración CSI | Contrato con el sistema de inteligencia de mercado | Qué investigación/competencia entrega CSI | AD-ARQ-08 | P2 (Fase 2) | Definido en Blueprint v1 | CC | 4-5 | Media |

---

## 10. Totales de la WO-000

| Categoría | Docs |
|---|---|
| Fundamentos del Producto | 5 |
| Comportamientos | 5 |
| Funcionalidades | 8 |
| UX/UI | 12 |
| Arquitectura | 10 |
| Inteligencia Artificial | 4 |
| Operación | 3 |
| Integraciones | 4 |
| **Total WO-000** | **51** |

**Páginas estimadas:** ~330-410. **Documentos P0 (bloqueantes de Fase 1 — Fundamentos/Comportamientos/Funcionalidades):** 18.

---

## 11. Secuenciación (backbone confirmada)

```
Product DNA (AD-000)
  → Principios del Sistema (AD-001)
    → Product Language (AD-002)
      → Domain Model (AD-003)
        → Objetos del Sistema (AD-004)
          → Comportamientos (AD-CMP-01..05)
            → Funcionalidades (AD-FUNC-01..08)
              → UX/UI (AD-UX-01..12)
                → Arquitectura (AD-ARQ-01..10)
                  → Integraciones (AD-INT-01..04)
```

IA y Operación corren en paralelo a Arquitectura (Fase 2), no antes.

**Fase 1 — Dominio funcional completo** (esto es lo único que se redacta hasta nueva orden): AD-000, AD-001, AD-002, AD-003, AD-004, los 5 AD-CMP, los 8 AD-FUNC. 18 documentos, ~140-170 páginas.

**Fase 2 — Solo después de que Fase 1 esté aprobada por ti:** UX, Arquitectura, IA, Operación, Integraciones.

---

## 12. Reservado para WO-100 — Business Architecture (futura, no se detalla aquí)

Se extraen de la WO-000 porque describen la empresa y el negocio, no el producto. Se listan para que no se pierdan — ninguno se descarta, solo se relocaliza:

1. Modelo de Negocio SaaS
2. Monetización y Pricing
3. Unit Economics *(consume como insumo AD-IA-03, que sí queda en WO-000)*
4. Modelo Financiero y Proyecciones
5. Programa AAA y Paradixe Ventures
6. Análisis Competitivo
7. Estrategia Go-to-Market e Institucional
8. Operación Continua y Suscripción (negocio recurrente post-Nivel 7)
9. Marco Legal, Regulatorio y Cumplimiento — incluye la legalidad de "Ondas Expansivas", el régimen del programa de equity, y la titularidad de IP en disputa con el socio/dev. *Nota: el límite de responsabilidad del producto (qué asesoría automatizada puede/no puede dar sin disclaimer) ya quedó cubierto como restricción de producto dentro de AD-000 y AD-001, para que el riesgo no desaparezca de la WO-000 mientras se resuelve el resto en WO-100.*
10. Playbook de Ventas
11. Convenios Institucionales (términos comerciales — el soporte de producto a cohortes institucionales, si lo hay, se especificaría como Funcionalidad en WO-000; los términos del contrato no)
12. Billing — términos y precios (la integración técnica queda en AD-OPS-03)
13. Analytics de Negocio (CAC, LTV, conversión)

---

**Pendiente de tu aprobación:** este árbol v2, antes de redactar el contenido de cualquier documento — empezando, si apruebas, por AD-000.
