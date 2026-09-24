# WO-000 — Índice Maestro de Especificación de Producto ADÁN (v1.0)

**Tipo de documento:** Árbol documental para revisión. No contiene especificación de producto.
**Estado de la WO-000:** En diseño — pendiente de aprobación del árbol antes de redactar cualquier documento.
**Regla de bloqueo:** prohibido desarrollo de código o contenido de los documentos listados hasta que este índice sea aprobado.

---

## 0. Cómo leer este índice

Cada fila define un documento maestro con:

- **Código** — identificador único, formato `AD-<CATEGORÍA>-<NN>`.
- **Objetivo** — qué decisión o ambigüedad elimina el documento.
- **Alcance** — qué cubre y, cuando es relevante, qué NO cubre (para evitar solapamiento con otro documento).
- **Dependencias** — códigos de documentos que deben aprobarse antes, porque este hereda definiciones de ellos.
- **Prioridad** — `P0` bloqueante (nada se construye sin esto) · `P1` crítico para el producto final · `P2` necesario pero puede iterar · `P3` fase posterior / visión.
- **Estado de insumos** — `Insumos en Chat 1.docx` (ya se discutió en las conversaciones ADÁN y solo falta formalizar) · `Definido en Blueprint v1` (el PDF ya lo nombra conceptualmente) · `No iniciado` (no existe insumo previo, se redacta desde cero).
- **Responsable** — quién redacta el borrador. `CC` = Claude Code (redacción asistida). `LEGAL` = requiere abogado externo antes de que el borrador pueda aprobarse. La aprobación final de **todo** documento es siempre de Hernán / Junta — eso no varía fila a fila y no se repite en la tabla.
- **Págs. / Complejidad** — estimado, para dimensionar la WO-000 en su totalidad.

Total de documentos: **60**. El pedido original fijaba un mínimo de referencia de ~50; el delta (+10) está justificado uno por uno en la sección 11, no añadido por relleno.

---

## 1. GOBIERNO (AD-GOV) — 5 documentos

| Código | Nombre | Objetivo | Alcance | Dependencias | Prioridad | Estado insumos | Resp. | Págs. | Complejidad |
|---|---|---|---|---|---|---|---|---|---|
| AD-GOV-01 | Constitución del Producto | Fijar qué es y qué NO es ADÁN, de forma que ninguna decisión futura pueda contradecirla | Definición irrevocable: unidad principal = Proyecto (no chat), agentes invisibles, evidencia > afirmación, cliente decide. Incluye cómo se aprueban y versionan los demás documentos (gobernanza documental) | — | P0 | Insumos en Chat 1.docx | CC | 6-8 | Media |
| AD-GOV-02 | Filosofía y Principios de Diseño | Traducir "pensar como Apple" en criterios verificables, no en gusto estético | Checklist de justificación obligatoria (UX / Ingeniería / Escalabilidad / Multiagentes / Performance / Seguridad / Costo) que todo documento posterior debe satisfacer | AD-GOV-01 | P0 | No iniciado | CC | 4-6 | Media |
| AD-GOV-03 | Arquitectura de Decisiones (Decision Log) | Especificar el objeto `DEC-XXXX` como ciudadano de primera clase del sistema, no solo como vista de UI | Esquema del objeto decisión, ciclo de vida (propuesta→debate→aprobada/rechazada), trazabilidad hacia Cards/Niveles/Documentos afectados | AD-GOV-01 | P0 | Insumos en Chat 1.docx | CC | 5-7 | Alta |
| AD-GOV-04 | Glosario Maestro y Taxonomía | Una sola definición autorizada por término (Proyecto, Nivel, Card, Score, Gemelo Digital, Board Room, etc.) | Diccionario canónico referenciado por todos los demás documentos; sin esto, cada documento reinterpretará los términos a su manera | AD-GOV-01 | P0 | No iniciado | CC | 4-5 | Baja |
| AD-GOV-05 | Marco Legal, Regulatorio y Cumplimiento | Determinar qué partes del producto actual son legalmente inviables tal como están planteadas | Cubre obligatoriamente: (a) legalidad del esquema de referidos "Ondas Expansivas" en Colombia — riesgo de pirámide bajo Ley 1700/2013; (b) responsabilidad por asesoría legal/tributaria/financiera automatizada; (c) régimen aplicable al programa de equity vía créditos (Programa AAA); (d) titularidad de IP del código actual en disputa con el socio/dev | AD-GOV-01 | **P0 — bloqueante de negocio, no solo de documentación** | No iniciado | **LEGAL** (borrador inicial CC, aprobación obligatoria de abogado externo) | 8-12 | Alta |

---

## 2. NEGOCIO (AD-BIZ) — 8 documentos

| Código | Nombre | Objetivo | Alcance | Dependencias | Prioridad | Estado insumos | Resp. | Págs. | Complejidad |
|---|---|---|---|---|---|---|---|---|---|
| AD-BIZ-01 | Modelo de Negocio SaaS | Definir los flujos de ingreso de forma consolidada (no dispersos entre niveles) | Pago por nivel, construcción de MVP, suscripción Paradixe XA, futuro Ventures — como un solo modelo, no fragmentos sueltos | AD-GOV-04 | P0 | Insumos en Chat 1.docx | CC | 6-8 | Media |
| AD-BIZ-02 | Monetización y Pricing | Fijar precios finales y su justificación, incluyendo empaquetamiento por canal (retail vs. institucional) | Precios por nivel, por MVP, por suscripción; grilla de descuento por volumen para convenios institucionales | AD-BIZ-01, AD-BIZ-03 | P0 | Insumos en Chat 1.docx (precios provisionales $5-10) | CC | 5-7 | Media |
| AD-BIZ-03 | Unit Economics | Determinar si el negocio es rentable por unidad antes de escalarlo | Costo real de inferencia (tokens/LLM) + operación por proyecto vs. precio cobrado, por nivel y en agregado. Gate obligatorio antes de cualquier campaña de adquisición | AD-IA-03 | **P0 — bloqueante** | No iniciado | CC | 6-9 | Alta |
| AD-BIZ-04 | Modelo Financiero y Proyecciones | Convertir los escenarios pesimista/base/optimista del Chat 1.docx en un modelo trazable, no en cifras sueltas | P&L proyectado, runway, supuestos explícitos y auditables (no proyecciones "de fe") | AD-BIZ-01, AD-BIZ-03 | P1 | Insumos en Chat 1.docx (escenarios 12 meses ya esbozados) | CC | 8-10 | Alta |
| AD-BIZ-05 | Programa AAA y Paradixe Ventures | Especificar el mecanismo de inversión en créditos/equity nombrado en el Blueprint v1 | Founder/Venture Score → oferta de créditos → conversión a equity; rol del Comité de Inversión independiente | AD-EI-03, AD-EI-04, AD-GOV-05 | P2 | Definido en Blueprint v1 | CC | 6-8 | Alta |
| AD-BIZ-06 | Análisis Competitivo | Corregir la afirmación actual ("competidores directos: prácticamente ninguno"), que no resiste escrutinio de junta | Mapeo real frente a Lovable, Bolt, v0, ChatGPT/Claude directo, incubadoras/aceleradoras, venture studios con IA; define el diferenciador defendible | AD-GOV-04 | P1 | No iniciado | CC | 5-7 | Media |
| AD-BIZ-07 | Estrategia Go-to-Market e Institucional | Resolver la tensión no resuelta entre cliente retail ($5) y cliente institucional (licencia de cohorte) | Segmentación de clientes, secuencia de entrada al mercado, rol del Nivel 1 gratuito como gancho | AD-BIZ-02, AD-COM-03 | P0 | Insumos en Chat 1.docx (mencionado, no desarrollado) | CC | 6-8 | Alta |
| AD-BIZ-08 | Operación Continua y Suscripción | Especificar qué ocurre después del Nivel 7 — el negocio recurrente real, según el Blueprint v1 ("los 7 niveles son creación; después la operación continua es la suscripción") | Alcance de Paradixe XA como capa operativa: hosting, agentes, soporte, evolución continua; cómo se factura y qué SLA aplica | AD-BIZ-01, AD-INT-01..04 | P1 | Definido en Blueprint v1 | CC | 6-8 | Alta |

---

## 3. PRODUCTO (AD-PRD) — 7 documentos

| Código | Nombre | Objetivo | Alcance | Dependencias | Prioridad | Estado insumos | Resp. | Págs. | Complejidad |
|---|---|---|---|---|---|---|---|---|---|
| AD-PRD-01 | Product Vision & Experience Vision | Fijar el norte de producto y de experiencia en un solo documento rector | Qué se siente usar ADÁN, comparables explícitos (Notion/Linear/Cursor, no ChatGPT), qué NUNCA debe sentirse (chatbot genérico) | AD-GOV-01, AD-GOV-02 | P0 | Insumos en Chat 1.docx | CC | 5-7 | Media |
| AD-PRD-02 | Gemelo Digital — Especificación Funcional | Especificar el objeto central del sistema: qué representa, qué versiona, quién lo lee/escribe | Empresa, producto, fundador, mercado; versionado de decisiones/documentos/código/KPIs/evidencias. Es la base de datos conceptual de la que dependen casi todos los demás documentos | AD-GOV-01, AD-GOV-04 | **P0 — el más referenciado de toda la WO-000** | Definido en Blueprint v1 (nombrado, no especificado) | CC | 8-10 | Muy Alta |
| AD-PRD-03 | Product Requirements Document (7 Niveles) | Consolidar los 7 niveles ya discutidos en un PRD único con criterios de entrada/salida por nivel | Objetivo, preguntas clave, documentación solicitada, metodologías, entregables, criterio de avance y precio por cada uno de los 7 niveles | AD-PRD-02, AD-GOV-03 | P0 | Insumos en Chat 1.docx (niveles 1-6 ya discutidos en detalle; nivel 7 falta) | CC | 14-18 | Alta |
| AD-PRD-04 | User Journey Map | Mapear el recorrido completo para los perfiles que ya se identificaron como distintos en las conversaciones (técnico vs. no técnico, individual vs. institucional) | Journey desde descubrimiento hasta suscripción activa, con puntos de fricción y abandono explícitos | AD-PRD-03 | P1 | Insumos en Chat 1.docx (perfilamiento por lenguaje técnico ya discutido) | CC | 6-8 | Media |
| AD-PRD-05 | Experience Engine | Especificar el subsistema nombrado en el Blueprint v1: gamificación, avatares, voz, Shark Tank simulado, Índice ADÁN | Mecánicas de progreso, integración con voz (ARQAI/Claro), simulación tipo Shark Tank para Nivel 5-6 | AD-PRD-01, AD-INT-02 | P2 | Definido en Blueprint v1 | CC | 7-9 | Alta |
| AD-PRD-06 | Marketplace de Agentes y SaaS | Especificar el marketplace nombrado en el Blueprint v1 (publicación de SaaS, agentes, servicios Paradixe, APIs, partners) | Reglas de publicación, curaduría, revenue share — fase posterior al núcleo de 7 niveles | AD-PRD-02, AD-BIZ-01 | P3 | Definido en Blueprint v1 | CC | 6-8 | Media |
| AD-PRD-07 | Board Room — Producto y Mecánica de Comité Ejecutivo | Especificar el subsistema nombrado en el Blueprint v1: CEO/CTO/CFO/CMO/Legal/Producto/Operaciones debatiendo, con cliente y terceros invitados, votaciones y actas | Reglas de debate, cómo se documentan desacuerdos entre agentes, quién tiene voto, cómo se genera el acta; se apoya en AD-ARQ-03 para el mecanismo técnico subyacente | AD-GOV-03, AD-ARQ-03 | P1 | Definido en Blueprint v1 | CC | 7-9 | Alta |

---

## 4. UX/UI (AD-UX) — 12 documentos

Esta es la categoría con más peso deliberadamente: coincide con el nivel de detalle que ya se exigió en las conversaciones ("cada vista al nivel de componentes, comportamiento, estados, relaciones y flujo de navegación").

| Código | Nombre | Objetivo | Alcance | Dependencias | Prioridad | Estado insumos | Resp. | Págs. | Complejidad |
|---|---|---|---|---|---|---|---|---|---|
| AD-UX-01 | Design System | Fijar el lenguaje visual y de componentes reutilizable | Tokens, tipografía, color, componentes base, estados (hover/loading/error/disabled), accesibilidad | AD-PRD-01 | P0 | No iniciado | CC | 8-10 | Alta |
| AD-UX-02 | Workspace Principal | Especificar la pantalla contenedora tras login: distribución de zonas | Sidebar / zona central / panel derecho; cómo cambian juntas al cambiar de nivel | AD-UX-01, AD-PRD-03 | P0 | Insumos en Chat 1.docx (prompt "Workspace Principal" ya redactado) | CC | 8-10 | Alta |
| AD-UX-03 | Dashboard General | Especificar la vista que responde "¿qué está pasando?" | Resumen ejecutivo, score global, próximos pasos, riesgos, KPIs, actividad reciente — distribución, tamaños, prioridad visual | AD-UX-02, AD-PRD-02 | P0 | Insumos en Chat 1.docx (Vista 1 ya redactada) | CC | 8-10 | Alta |
| AD-UX-04 | Sidebar y Navegación | Especificar la navegación persistente | Iconos, jerarquías, estados de nivel (bloqueado/desbloqueado/progreso), badges, breadcrumbs | AD-UX-02 | P0 | Insumos en Chat 1.docx (Vista 2 ya redactada) | CC | 5-7 | Media |
| AD-UX-05 | Vista de Nivel (Workspace por Nivel) | Especificar cómo cada uno de los 7 niveles se siente distinto, no como 7 chats idénticos | Layout por zona (arriba/izquierda/derecha/abajo), paneles, cards, widgets específicos de cada nivel | AD-UX-02, AD-PRD-03 | P0 | Insumos en Chat 1.docx (Vista 3 + especificación por nivel 1-7 ya redactadas) | CC | 12-16 | Muy Alta |
| AD-UX-06 | Sistema de Cards | Especificar la unidad de trabajo dentro de un nivel (Branding, Canvas, Finanzas, etc.) | Qué muestra, qué contiene, cómo se expande/colapsa, cómo interactúa con otras Cards | AD-UX-05 | P0 | Insumos en Chat 1.docx (Vista 4 ya redactada) | CC | 7-9 | Alta |
| AD-UX-07 | Chat / Conversación | Especificar la conversación como herramienta profesional, no como chat genérico | Contexto visible, documentos relacionados, agentes participantes, versionado, sesiones con inicio/desarrollo/conclusión/resumen automático | AD-UX-06, AD-ARQ-05 | P0 | Insumos en Chat 1.docx (Vista 5 + prompt "Workspace/Chat" ya redactados) | CC | 8-10 | Alta |
| AD-UX-08 | Timeline | Especificar el registro cronológico de todo evento relevante | Cómo se navega, filtra, busca y agrupa; qué eventos se registran | AD-ARQ-07 | P1 | Insumos en Chat 1.docx (Vista 8 ya redactada) | CC | 5-6 | Media |
| AD-UX-09 | Documentos (Gestor Documental) | Especificar la base documental generada por el sistema | Clasificación, generación, edición, versionado, búsqueda, enlace con chats y decisiones | AD-ARQ-06 | P1 | Insumos en Chat 1.docx (Vista 6 ya redactada) | CC | 6-8 | Media |
| AD-UX-10 | Decisiones (Vista DEC) | Especificar la vista del objeto decisión definido en AD-GOV-03 | Descripción, justificación, responsable, impacto, estado, alternativas descartadas | AD-GOV-03 | P1 | Insumos en Chat 1.docx (Vista 9 ya redactada) | CC | 5-6 | Media |
| AD-UX-11 | Agentes (Consola) | Especificar la vista que expone agentes solo cuando el usuario decide inspeccionarlos | Estado, rol, skills, herramientas, memoria, costo, tokens, rendimiento — y cuándo permanece oculta por defecto | AD-ARQ-03 | P1 | Insumos en Chat 1.docx (Vista 7 ya redactada) | CC | 6-7 | Media |
| AD-UX-12 | Memoria y RAG (Consolas de Contexto) | Especificar las dos vistas de introspección de contexto: memoria por capas y estado del índice RAG | Memoria (global/proyecto/nivel/card/agente); RAG (documentos indexados, chunks, embeddings, relevancia, último uso) — sin ocultar esta información al usuario avanzado | AD-ARQ-04, AD-ARQ-06 | P2 | Insumos en Chat 1.docx (Vistas 10 y 11 ya redactadas) | CC | 6-8 | Alta |

---

## 5. ARQUITECTURA (AD-ARQ) — 9 documentos

| Código | Nombre | Objetivo | Alcance | Dependencias | Prioridad | Estado insumos | Resp. | Págs. | Complejidad |
|---|---|---|---|---|---|---|---|---|---|
| AD-ARQ-01 | Arquitectura General | Vista técnica de sistema completa, de la que se desprenden los demás documentos de arquitectura | Diagrama de componentes end-to-end: Usuario→Workspace→Proyecto→Nivel→Cards→Chats→Orquestador→Agentes→Herramientas→RAG→Memoria→Documentos | AD-PRD-02 | P0 | Insumos en Chat 1.docx (diagrama de 17 capas ya esbozado) | CC | 8-10 | Muy Alta |
| AD-ARQ-02 | Orquestador | Especificar el "director invisible": quién decide qué agente actúa | Selección de agentes por fase, enrutamiento de contexto, selección de herramientas — nunca decidido por el usuario | AD-ARQ-01 | P0 | Insumos en Chat 1.docx | CC | 6-8 | Alta |
| AD-ARQ-03 | Multiagentes | Especificar el protocolo de consenso entre agentes | Roles (CEO/CTO/CFO/CMO/Legal/Ops), skills exclusivas por rol, mecanismo de "respuesta única, nunca cinco respuestas" | AD-ARQ-02 | P0 | Insumos en Chat 1.docx | CC | 8-10 | Muy Alta |
| AD-ARQ-04 | Memoria (Motor Técnico) | Especificar el almacenamiento y recuperación de las 7 capas de memoria nombradas | Global / Proyecto / Nivel / Card / Chat / Usuario / Empresa / Agente — modelo de datos, TTL, invalidación | AD-PRD-02 | P0 | Insumos en Chat 1.docx | CC | 8-10 | Muy Alta |
| AD-ARQ-05 | Context Engineering | Especificar cómo se evita el explode de contexto | Generación de resúmenes MD por Card→Nivel→Proyecto; qué se pasa al siguiente nivel y qué se descarta | AD-ARQ-04 | **P0 — condiciona el costo unitario (ver AD-BIZ-03)** | Insumos en Chat 1.docx (mecanismo ya descrito en detalle) | CC | 7-9 | Alta |
| AD-ARQ-06 | RAG | Especificar indexación y recuperación documental | Chunking, embeddings, estrategia de relevancia, actualización de índice | AD-ARQ-04 | P1 | No iniciado | CC | 6-8 | Alta |
| AD-ARQ-07 | Eventos | Especificar el registro append-only que alimenta el Timeline | Esquema de evento, event sourcing vs. simple log, retención | AD-ARQ-01 | P1 | No iniciado | CC | 5-6 | Media |
| AD-ARQ-08 | APIs | Especificar contratos internos y de integración | Convenciones REST/eventos, versionado, y el contrato común que consumen las integraciones externas (EVA/ARQAI/Genexis/CSI) | AD-ARQ-01 | P0 | No iniciado | CC | 6-8 | Alta |
| AD-ARQ-09 | Seguridad | Especificar aislamiento de datos y control de acceso | Autenticación, aislamiento por proyecto/tenant, cifrado en reposo/tránsito, gestión de secretos | AD-ARQ-01, AD-GOV-05 | P0 | No iniciado | CC | 8-10 | Alta |

---

## 6. INTELIGENCIA ARTIFICIAL (AD-IA) — 4 documentos

| Código | Nombre | Objetivo | Alcance | Dependencias | Prioridad | Estado insumos | Resp. | Págs. | Complejidad |
|---|---|---|---|---|---|---|---|---|---|
| AD-IA-01 | Modelos y Routing | Fijar qué modelo se usa para qué tarea, y por qué | Haiku (tareas ligeras), Sonnet (razonamiento/desarrollo), Opus (arquitectura crítica/revisión final); STT/TTS propios; CPU vs. GPU | AD-ARQ-02 | P0 | Definido en Blueprint v1 | CC | 5-6 | Media |
| AD-IA-02 | Prompt Engineering y Evaluación de Calidad | Especificar cómo se diseñan y validan los prompts por agente y por nivel, incluyendo el "proceso Outlier" de precisión mencionado en las conversaciones | Plantillas por rol de agente, criterios de evaluación de respuesta, proceso de validación antes de poner un agente en producción | AD-IA-01, AD-ARQ-03 | P1 | Insumos en Chat 1.docx (mención de "proceso Outlier") | CC | 6-8 | Alta |
| AD-IA-03 | Costos de Inferencia | Modelar el costo real de tokens por proyecto y por nivel — insumo directo de AD-BIZ-03 | Costo por modelo, por nivel, proyección de costo a escala (500 / 2.000 / 10.000 usuarios) | AD-IA-01, AD-ARQ-05 | **P0 — bloqueante de negocio** | No iniciado | CC | 5-7 | Alta |
| AD-IA-04 | Optimización | Especificar caching, batching y reducción de latencia | Estrategias de reducción de costo y tiempo de respuesta sin degradar calidad | AD-IA-03 | P2 | No iniciado | CC | 4-5 | Media |

---

## 7. ENTERPRISE INTELLIGENCE (AD-EI) — 4 documentos

| Código | Nombre | Objetivo | Alcance | Dependencias | Prioridad | Estado insumos | Resp. | Págs. | Complejidad |
|---|---|---|---|---|---|---|---|---|---|
| AD-EI-01 | Enterprise Intelligence Engine | Especificar el motor nombrado en el Blueprint v1 como pilar de arquitectura | Cómo se agregan las señales de todos los niveles en inteligencia accionable para el Board Room y para Paradixe Ventures | AD-PRD-02, AD-ARQ-04 | P1 | Definido en Blueprint v1 | CC | 6-8 | Alta |
| AD-EI-02 | Motor de Scoring (Framework General) | Fijar la metodología común de puntuación antes de definir cada score específico | Parámetros, pesos, umbrales de avance, metodología de comparación contra el mercado (ya usada en Nivel 2) | AD-EI-01 | P0 | Insumos en Chat 1.docx (metodología de pesos y ranking ya discutida en Nivel 2) | CC | 6-8 | Alta |
| AD-EI-03 | Venture Score | Especificar el score usado para decisiones de inversión (Programa AAA) | Composición del score, relación con la calculadora de equity ya esbozada (Score 95+/85/75 → % equity) | AD-EI-02, AD-GOV-05 | P2 | Insumos en Chat 1.docx (calculadora de equity ya esbozada) | CC | 5-6 | Alta |
| AD-EI-04 | Founder / Problem / Solution / Business / Product / Market / Execution Scores | Especificar los scores por nivel en un solo documento consolidado (evita 6 documentos casi idénticos) | Un score por nivel 1-6, su fórmula, su fuente de datos y su criterio de aprobación | AD-EI-02, AD-PRD-03 | P0 | Insumos en Chat 1.docx (Score de oportunidad Nivel 1, ranking Nivel 2 ya discutidos) | CC | 8-10 | Alta |

---

## 8. OPERACIÓN (AD-OPS) — 4 documentos

| Código | Nombre | Objetivo | Alcance | Dependencias | Prioridad | Estado insumos | Resp. | Págs. | Complejidad |
|---|---|---|---|---|---|---|---|---|---|
| AD-OPS-01 | Observabilidad y Logging | Especificar qué se monitorea y qué se registra en producción | Métricas de sistema, logs estructurados, alertas — consolidado en un documento porque logging es subconjunto de observabilidad | AD-ARQ-01 | P1 | No iniciado | CC | 5-6 | Media |
| AD-OPS-02 | Auditoría | Especificar el rastro inmutable exigido por AD-GOV-03 (trazabilidad de toda decisión) | Qué se audita, retención, quién puede consultar el log de auditoría | AD-GOV-03, AD-ARQ-07 | P1 | No iniciado | CC | 4-5 | Media |
| AD-OPS-03 | Analytics | Especificar métricas de producto y negocio (no técnicas) | Retención, conversión entre niveles, CAC, LTV — alimenta AD-BIZ-03 y AD-BIZ-04 | AD-BIZ-03 | P2 | No iniciado | CC | 5-6 | Media |
| AD-OPS-04 | Billing | Especificar cobro, facturación y manejo de impagos | Integración con pasarela de pago, ciclo de suscripción, dunning | AD-BIZ-01, AD-BIZ-02 | P1 | No iniciado | CC | 5-6 | Media |

---

## 9. INTEGRACIONES (AD-INT) — 4 documentos

| Código | Nombre | Objetivo | Alcance | Dependencias | Prioridad | Estado insumos | Resp. | Págs. | Complejidad |
|---|---|---|---|---|---|---|---|---|---|
| AD-INT-01 | Integración EVA | Especificar el contrato con el cerebro financiero/estratégico | Qué datos entrega ADÁN a EVA, qué recibe de vuelta (análisis financiero, KPIs, riesgos, proyecciones) | AD-ARQ-08 | P1 | Definido en Blueprint v1 (relación conceptual "ADÁN diseña, EVA evalúa") | CC | 4-5 | Media |
| AD-INT-02 | Integración ARQAI | Especificar el contrato con el motor de voz/agente conversacional | Uso de voz en Experience Engine (AD-PRD-05), reutilización del runtime GPU existente | AD-ARQ-08 | P1 | Insumos externos (repo Claro/ARQAI ya existente) | CC | 4-5 | Media |
| AD-INT-03 | Integración Genexis | Especificar el contrato con el motor de construcción de software | Qué especificación entrega ADÁN (Nivel 4/6), qué entrega Genexis (MVP construido) | AD-ARQ-08 | P1 | Definido en Blueprint v1 (relación conceptual "ADÁN diseña, Genexis construye") | CC | 4-5 | Media |
| AD-INT-04 | Integración CSI | Especificar el contrato con el sistema de inteligencia de mercado | Qué investigación/competencia/tendencias entrega CSI para validación en Niveles 1-2 | AD-ARQ-08 | P1 | Definido en Blueprint v1 (relación conceptual "ADÁN decide, CSI suministra información") | CC | 4-5 | Media |

*(El contrato técnico común a las cuatro integraciones — autenticación, formato de payload, versionado — se especifica una sola vez en AD-ARQ-08 y no se repite en cada documento de integración, para evitar redundancia de cuatro especificaciones de API casi idénticas.)*

---

## 10. COMERCIAL (AD-COM) — 3 documentos

| Código | Nombre | Objetivo | Alcance | Dependencias | Prioridad | Estado insumos | Resp. | Págs. | Complejidad |
|---|---|---|---|---|---|---|---|---|---|
| AD-COM-01 | Onboarding | Especificar la primera sesión de un usuario nuevo, retail o institucional | Flujo desde registro hasta primera pregunta de ADÁN en Nivel 1 | AD-UX-02, AD-PRD-03 | P0 | Insumos en Chat 1.docx (flujo "login→dashboard→ADÁN inicia conversación" ya descrito) | CC | 4-5 | Media |
| AD-COM-02 | Playbook de Ventas | Especificar cómo se vende a canal institucional | Guion de venta, objeciones frecuentes, materiales de apoyo (deriva de AD-BIZ-06, sin repetirlo) | AD-BIZ-07 | P2 | No iniciado | CC | 4-5 | Baja |
| AD-COM-03 | Convenios Institucionales | Especificar el modelo de convenio con SENA, Cámaras de Comercio y universidades | Estructura de licencia por cohorte, reportería a la institución, condiciones de exclusividad — este documento es prerequisito de AD-BIZ-07, no al revés | AD-GOV-05, AD-BIZ-02 | P0 | Insumos en Chat 1.docx (mencionado para Uninorte, SENA, Cámara de Comercio) | CC | 5-7 | Media |

---

## 11. Documentos añadidos más allá del listado mínimo — justificación técnica

El pedido original listaba un piso de referencia. Estos 10 documentos se añadieron porque su ausencia deja huecos que ya se manifestaron como riesgo real en las conversaciones previas del proyecto, no por completitud cosmética:

1. **AD-GOV-05 Marco Legal y Cumplimiento** — el esquema "Ondas Expansivas" (7 niveles de referidos, 1% de la red) es estructuralmente indistinguible de un multinivel bajo la ley colombiana, y el proyecto busca convenios con SENA/Cámaras/gobierno que no se firman con ese riesgo activo. Sin este documento, cualquier otro documento comercial se construye sobre una base que puede tener que revertirse.
2. **AD-BIZ-03 Unit Economics** — el documento base solo tiene precios de venta ($5-10 por nivel); no hay costo de inferencia calculado. Sin esto, todo el modelo de pricing es una suposición, exactamente lo que la metodología de Work Orders prohíbe afirmar sin evidencia.
3. **AD-BIZ-06 Análisis Competitivo** — la afirmación existente ("competidores directos: prácticamente ninguno") no sobrevive dos minutos frente a Lovable, Bolt o v0. Presentarla así ante una junta o un gobierno resta credibilidad al resto del pitch.
4. **AD-BIZ-07 Estrategia GTM Institucional** — el documento base menciona SENA/Cámara/Uninorte como ocurrencia, no como estrategia. El modelo retail ($5) y el modelo institucional (licencia por cohorte) no pueden coexistir sin definir cuál es el motor principal.
5. **AD-BIZ-08 Operación Continua** — el Blueprint v1 nombra la suscripción post-Nivel-7 como el negocio recurrente real, pero no hay ningún documento que la especifique; es el ingreso de mayor valor a largo plazo y hoy es la pieza menos definida.
6. **AD-PRD-02 Gemelo Digital** — nombrado en el Blueprint v1 como pilar de arquitectura pero nunca especificado; es la estructura de datos de la que dependen Dashboard, Timeline, Decisiones, Scoring y Memoria. Sin este documento, esos cinco documentos se escribirían sin un modelo de datos común y se contradirían entre sí.
7. **AD-PRD-07 Board Room** — nombrado explícitamente en el Blueprint v1 ("CEO ADÁN, CTO, CFO... debate visible... votaciones y actas") pero ausente del listado original; es el mecanismo que hace creíble la promesa de "comité ejecutivo permanente".
8. **AD-ARQ-05 Context Engineering** — ya estaba en el listado original bajo Arquitectura, se mantiene aquí solo para señalar su dependencia directa con AD-BIZ-03: es la palanca principal de reducción de costo de tokens, así que su diseño condiciona si el negocio es rentable.
9. **AD-EI-02 Motor de Scoring (framework general)** — el listado original salta directo a los scores individuales (Founder, Venture, Business); sin un framework común de pesos y umbrales antes, cada score se inventaría su propia metodología.
10. **AD-COM-03 Convenios Institucionales** — consecuencia directa de #4: si la estrategia GTM es institucional, el contrato de convenio es un entregable comercial de primer orden, no un anexo.

---

## 12. Totales y secuenciación recomendada

**Total de documentos:** 60 · **Páginas estimadas:** ~390-480 · **Documentos P0 (bloqueantes):** 20

La secuenciación no es una sugerencia de desarrollo (eso está prohibido hasta aprobar este índice) sino un orden de **redacción** basado en dependencias reales:

1. **Batch 1 — Cimientos** (sin estos, ningún otro documento tiene terreno firme): AD-GOV-01, AD-GOV-04, AD-GOV-05, AD-PRD-02.
2. **Batch 2 — Viabilidad de negocio** (determina si el modelo actual es sostenible antes de especificar UI): AD-IA-03, AD-BIZ-03, AD-BIZ-02, AD-BIZ-06, AD-BIZ-07.
3. **Batch 3 — Producto y arquitectura núcleo**: AD-PRD-03, AD-ARQ-01, AD-ARQ-02, AD-ARQ-03, AD-ARQ-04, AD-ARQ-05, AD-EI-02, AD-EI-04.
4. **Batch 4 — Experiencia**: AD-UX-01 a AD-UX-12.
5. **Batch 5 — Operación, integraciones, comercial**: el resto.

**Nota sobre AD-GOV-05:** este documento no es solo un entregable de la WO-000. Su hallazgo puede forzar un cambio de decisión arquitectónica ya aprobada (el esquema de referidos), lo cual, según la propia metodología de Work Orders, es uno de los únicos motivos válidos para detener el trabajo y pedir tu decisión explícita. Recomiendo redactarlo primero, no al final.

---

**Pendiente de tu aprobación:** el árbol completo, antes de redactar el contenido de cualquier documento individual.
