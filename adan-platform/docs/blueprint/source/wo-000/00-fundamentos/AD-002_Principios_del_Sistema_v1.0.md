---
Código: AD-002
Nombre: Principios del Sistema
Versión: v1.0 — APROBADA Y CONGELADA. Superseded por v2.0 el mismo día — ver AD-002_Principios_del_Sistema_v2.0.md
Estado: Aprobado y congelado. No editar en el sitio
Confidence Level: 68%
Fecha de aprobación: 2026-07-14
Responsable (autor del borrador): CC (Claude Code)
Aprobador: Hernán / Junta Directiva
---

# AD-002 — Principios del Sistema

> AD-001 declaró *quién es* ADÁN — su identidad, su filosofía, lo que jamás romperá. Este documento traduce esa identidad en **reglas de sistema**: lo que debe ser verdad, siempre, en cualquier instancia del producto, independientemente de qué funcionalidad, vista o motor técnico la implemente. AD-001 responde por qué algo importa; AD-002 responde qué debe garantizarse para que siga importando en la práctica. Ninguna de las nueve reglas de este documento describe *cómo* se implementa (eso es Fase 2 — Arquitectura); todas describen *qué* debe cumplirse siempre, sin excepción, para que ADÁN siga siendo ADÁN.

**Nivel de contenido de este documento:** Principio Permanente en su totalidad. Las nueve reglas de la sección 1 no deberían necesitar una nueva versión en veinte años; su implementación técnica sí evolucionará constantemente, pero eso ocurre en otros documentos (AD-CMP, AD-ARQ), nunca aquí.

---

## 1. Las Nueve Reglas

Cada regla incluye de dónde proviene en AD-001, qué garantiza, y qué escenario constituiría una violación — para que la regla sea verificable, no solo aspiracional.

### 1.1 Todo genera evidencia

Ninguna afirmación relevante del sistema se sostiene sin datos, fuente o razonamiento verificable detrás.

- **Deriva de:** AD-001 §2 (el problema que resuelve ADÁN), Filosofía #2 ("una decisión sin evidencia no es una decisión").
- **Garantiza:** que cada score, cada recomendación y cada documento generado por ADÁN pueda defenderse ante la pregunta "¿de dónde sale esto?".
- **Violación de ejemplo:** un agente afirma "tu mercado objetivo tiene alta demanda" sin citar la fuente de esa afirmación (un dato de CSI, una entrevista, un benchmark). Si no puede citarse, no puede afirmarse.

### 1.2 Todo es trazable

Toda decisión, documento, score o recomendación puede rastrearse hasta su origen: quién o qué la generó, con qué evidencia, y en qué momento.

- **Deriva de:** AD-001 §5 ("nunca oculta el razonamiento"), AD-001 §11 (cómo toma decisiones).
- **Garantiza:** que ningún resultado del sistema sea una caja negra, incluso años después de generado.
- **Violación de ejemplo:** un Score de Nivel 3 cambia entre dos consultas sin que exista un registro de qué evidencia nueva lo justificó.

### 1.3 Todo es reversible

Ninguna acción del sistema es irreversible sin que el cliente lo sepa y lo apruebe explícitamente.

- **Deriva de:** AD-001 §5 ("nunca avanza sin el acuerdo explícito del cliente"), Filosofía #4 (toda empresa merece el mismo rigor, incluyendo el derecho a corregir el rumbo).
- **Garantiza:** que un cliente pueda deshacer, cuestionar o revisar cualquier decisión previa sin perder lo construido antes de ella.
- **Violación de ejemplo:** un cambio de estrategia en Nivel 3 borra silenciosamente el Business Model Canvas del Nivel 2 en vez de versionarlo.

### 1.4 Toda decisión tiene responsable

Toda decisión registrada identifica quién la propuso y quién la aprobó — nunca "el sistema decidió" sin atribución.

- **Deriva de:** AD-001 §11 (regla 3: la decisión final siempre pertenece al cliente), AD-001 §12 (principio inviolable #2).
- **Garantiza:** que exista siempre una persona o un rol claramente identificado detrás de cada decisión, humano o agente.
- **Violación de ejemplo:** el sistema avanza de Nivel automáticamente sin que quede registrado qué agente lo recomendó y qué humano lo aprobó.

### 1.5 Nada se pierde

Ninguna información generada por el sistema se descarta silenciosamente; lo que deja de ser relevante se archiva, nunca se borra.

- **Deriva de:** AD-001, Visión a 25 Años ("el Gemelo Digital de las primeras empresas... debería seguir existiendo, seguir siendo consultable"), AD-001 §12 (principio inviolable #4).
- **Garantiza:** que una empresa acompañada por ADÁN nunca pierda su historial, incluso si pivota, se pausa o cambia de fundador.
- **Violación de ejemplo:** al reiniciar la estrategia de una empresa, se sobreescribe el historial de decisiones anteriores en vez de archivarlo y comenzar una nueva rama.

### 1.6 Toda IA debe justificar

Ninguna salida generada por un agente se presenta sin que su razonamiento esté disponible bajo solicitud del cliente.

- **Deriva de:** AD-001 §5 ("nunca oculta el razonamiento"), AD-001 §11 (regla 2: todo desacuerdo interno relevante se comunica).
- **Garantiza:** que "porque lo dijo la IA" nunca sea una respuesta válida dentro del sistema.
- **Violación de ejemplo:** un agente presenta una recomendación final sin que exista, en ningún lugar del sistema, el razonamiento que la produjo.

### 1.7 Todo tiene versión

Ningún documento, entidad o configuración del sistema se sobreescribe silenciosamente; todo cambio relevante genera una versión nueva con su propio registro de qué cambió y por qué.

- **Deriva de:** AD-001 §12 (principio inviolable #4, memoria permanente).
- **Garantiza:** trazabilidad histórica completa de cómo evolucionó cada elemento del sistema, no solo su estado actual.
- **Ya en práctica:** esta misma WO-000 es la primera instancia viva de esta regla — AD-000 y AD-001 se congelaron como v1.0 exactamente por esto, y este documento seguirá el mismo patrón en adelante.
- **Violación de ejemplo:** un agente edita el Plan de Negocio de un cliente en el sitio, sin dejar rastro de la versión anterior.

### 1.8 Todo genera memoria

Ninguna interacción relevante desaparece al cerrar una sesión; se resume, se conecta al Gemelo Digital correspondiente, y queda disponible para el resto del sistema.

- **Deriva de:** AD-001 §1 ("nunca pierde contexto, nunca olvida una decisión anterior").
- **Garantiza:** que el cliente nunca tenga que repetir información ya provista, sin importar cuánto tiempo haya pasado entre sesiones.
- **Adelanto técnico:** la mecánica de resumen y jerarquía de contexto se especifica en AD-CMP-04; esta regla solo fija que debe existir, no cómo.
- **Violación de ejemplo:** el cliente vuelve después de un mes y ADÁN le pregunta de nuevo información que ya había dado en el Nivel 1.

### 1.9 Todo tiene un nivel de confianza declarado

Ninguna salida del sistema —recomendación, score, documento— se presenta sin declarar qué tan respaldada está por evidencia. Cuando el nivel de confianza es bajo, se dice explícitamente; nunca se disfraza de certeza.

- **Deriva de:** AD-001 §6.1, el Principio de Humildad Intelectual, y AD-001 §12 (principio inviolable #6, agregado en la revisión final de AD-001).
- **Garantiza:** que un cliente nunca confunda una hipótesis bien redactada con un hecho verificado.
- **Coherencia deliberada:** esta regla es la razón por la que cada documento de esta misma WO-000 declara su propio Confidence Level desde v3.1 — la especificación del producto ya practica la regla que le exige al producto.
- **Violación de ejemplo:** un Score de mercado se presenta como "78/100" sin indicar si esa cifra se apoya en cinco entrevistas reales o en una estimación sin validar.

**Confidence Level de esta sección: 72%** — ocho de las nueve reglas derivan directamente de descripciones ya existentes en Chat 1.docx y del alcance original fijado para AD-002 en el índice maestro (v3.1); la regla 9 es una adición de esta versión, consistente con el Principio de Humildad Intelectual que el Board agregó a AD-001 en su revisión final, pero sin confirmación textual propia todavía.

---

## 2. Checklist de Justificación de Diseño

Toda decisión de diseño no trivial —de producto, de arquitectura, de UX— que se tome en cualquier documento posterior de la WO-000 debe poder responder estas siete preguntas. No es necesario responderlas explícitamente en cada documento, pero cualquier decisión que no pueda responderlas si se le pregunta, no está lista para aprobarse.

| Dimensión | Pregunta que obliga a responder |
|---|---|
| UX | ¿Esta decisión reduce o aumenta la carga cognitiva del usuario? |
| Ingeniería | ¿Esta decisión es sostenible de mantener, o genera deuda técnica oculta? |
| Escalabilidad | ¿Esta decisión sigue funcionando con diez o cien veces el volumen actual? |
| Multiagentes | ¿Esta decisión respeta el principio de consenso (AD-CMP-02) o introduce ambigüedad entre agentes? |
| Performance | ¿Esta decisión introduce latencia o costo computacional injustificado? |
| Seguridad | ¿Esta decisión expone información o una superficie de ataque nueva? |
| Costo | ¿Esta decisión es defendible frente a la economía unitaria del sistema (Unit Economics, reservado en WO-100)? |

Este checklist es la forma operativa de la Regla 4 de redacción fijada en el índice maestro (v3.2): *"toda decisión importante se justifica."* No sustituye el registro formal de Justificación/Alternativas/Motivo de descarte que exige esa misma regla — lo complementa, dando siete ángulos concretos desde los cuales construir esa justificación.

---

## Dependencias

- AD-001 Product DNA (las nueve reglas de este documento son la traducción operativa de sus principios de identidad)

## Documentos relacionados

- AD-CMP-01 a AD-CMP-06 (cada comportamiento debe poder señalar qué regla de este documento implementa)
- AD-ARQ-01 a AD-ARQ-10 (la implementación técnica de estas nueve reglas — auditoría, versionado, memoria — vive ahí, en Fase 2)
- AD-007 Gemelo Digital (implementa directamente las reglas 1.3, 1.5 y 1.7)
- AD-FUNC-07 Sistema de Scoring (implementa directamente la regla 1.9)
- AD-OPS-02 Auditoría (implementa directamente las reglas 1.2 y 1.4)

## Impacto sobre otros módulos

Estas nueve reglas son la vara de aceptación técnica de toda la Fase 2. Ningún documento de Arquitectura, IA u Operación puede darse por completo si no puede señalar, explícitamente, cómo garantiza cada una de las nueve reglas que le aplican. En particular:

1. AD-ARQ-04 (Memoria) y AD-ARQ-07 (Eventos) deben demostrar cómo se cumplen las reglas 1.5, 1.7 y 1.8 a nivel de almacenamiento real, no solo de intención.
2. AD-FUNC-07 y AD-ARQ-10 (Scoring) deben definir el mecanismo concreto por el cual un score comunica su propio nivel de confianza (regla 1.9) — hoy es un principio declarado, no un mecanismo especificado.
3. AD-OPS-02 (Auditoría) hereda directamente las reglas 1.2 y 1.4 como su razón de existir.

## Riesgos

- **Riesgo de que las nueve reglas queden como aspiración, no como restricción verificable.** Cada regla incluye un "violación de ejemplo" precisamente para mitigar esto — pero la verificación real solo existe cuando Fase 2 (Arquitectura) construye mecanismos técnicos concretos para cada una. Hasta entonces, estas reglas son un compromiso de diseño, no una garantía operativa.
- **Riesgo de sobrecarga del checklist de la sección 2.** Si se aplica de forma mecánica y ritual a cada micro-decisión, pierde valor. Está pensado para decisiones no triviales, no para cada elección de redacción.

## Preguntas abiertas

- **Mecanismo concreto de la regla 1.9.** ¿Cómo se representa exactamente un "nivel de confianza bajo" ante el cliente dentro del producto — un número, una etiqueta cualitativa, una explicación en lenguaje natural? Esta pregunta queda abierta para AD-CMP-05 y AD-FUNC-07, no se resuelve aquí porque sería describir implementación, lo cual esta categoría de documento evita por diseño (Regla 2 de redacción, v3.2).

## Decisiones pendientes

Ninguna decisión de negocio pendiente en este documento.

## Historial de cambios

| Versión | Fecha | Cambio | Motivo |
|---|---|---|---|
| v1.0 | 2026-07-14 | Creación inicial del documento: nueve reglas de sistema (ocho del alcance original de v3.1 más la regla 1.9, derivada del Principio de Humildad Intelectual agregado a AD-001 en su revisión final) y checklist de justificación de diseño | Tercer documento de la WO-000, redactado bajo los 6 Estándares Permanentes de Redacción y la distinción Principio Permanente / Decisión de Diseño |
| v1.0 — Aprobada | 2026-07-14 | Aprobación formal del Board, sin cambios de contenido. Se congela | Cierre del ciclo de revisión de AD-002 |
| — | 2026-07-14 | **Superseded por v2.0** el mismo día de aprobación: el Board solicitó agregar un décimo principio permanente (Economía Conceptual) inmediatamente después de aprobar v1.0. Este archivo v1.0 se conserva como evidencia histórica; la versión vigente es v2.0 | Primer caso real de la disciplina de versionado aplicada a un documento ya aprobado |
