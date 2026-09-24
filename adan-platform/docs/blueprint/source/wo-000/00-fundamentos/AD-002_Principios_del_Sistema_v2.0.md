---
Código: AD-002
Nombre: Principios del Sistema
Versión: v2.0 — APROBADA Y CONGELADA
Estado: Aprobado. No editar en el sitio
Confidence Level: 70%
Fecha de aprobación: 2026-07-14
Responsable (autor del borrador): CC (Claude Code)
Aprobador: Hernán / Junta Directiva
Supersede a: AD-002_Principios_del_Sistema_v1.0.md (aprobado y congelado el mismo día — ver su Historial de cambios)
---

# AD-002 — Principios del Sistema (v2.0)

> AD-001 declaró *quién es* ADÁN — su identidad, su filosofía, lo que jamás romperá. Este documento traduce esa identidad en **reglas de sistema**: lo que debe ser verdad, siempre, en cualquier instancia del producto, independientemente de qué funcionalidad, vista o motor técnico la implemente. AD-001 responde por qué algo importa; AD-002 responde qué debe garantizarse para que siga importando en la práctica. Ninguna de las diez reglas de este documento describe *cómo* se implementa (eso es Fase 2 — Arquitectura); todas describen *qué* debe cumplirse siempre, sin excepción, para que ADÁN siga siendo ADÁN.

**Nivel de contenido de este documento:** Principio Permanente en su totalidad.

**Nota de versión:** esta v2.0 sucede a v1.0 —aprobada y congelada el mismo día— para incorporar un décimo principio, Economía Conceptual, solicitado por el Board inmediatamente después de la aprobación. Es el primer caso real de la disciplina de versionado aplicada a un documento ya aprobado: v1.0 no se edita, se conserva como evidencia, y esta v2.0 es la versión vigente.

---

## 1. Las Diez Reglas

Cada regla incluye de dónde proviene, qué garantiza, y qué escenario constituiría una violación — para que la regla sea verificable, no solo aspiracional.

### 1.1 Todo genera evidencia

Ninguna afirmación relevante del sistema se sostiene sin datos, fuente o razonamiento verificable detrás.

- **Deriva de:** AD-001 §2, Filosofía #2 ("una decisión sin evidencia no es una decisión").
- **Garantiza:** que cada score, cada recomendación y cada documento generado por ADÁN pueda defenderse ante la pregunta "¿de dónde sale esto?".
- **Violación de ejemplo:** un agente afirma "tu mercado objetivo tiene alta demanda" sin citar la fuente de esa afirmación.

### 1.2 Todo es trazable

Toda decisión, documento, score o recomendación puede rastrearse hasta su origen: quién o qué la generó, con qué evidencia, y en qué momento.

- **Deriva de:** AD-001 §5, §11.
- **Garantiza:** que ningún resultado del sistema sea una caja negra, incluso años después de generado.
- **Violación de ejemplo:** un Score de Nivel 3 cambia entre dos consultas sin que exista un registro de qué evidencia nueva lo justificó.

### 1.3 Todo es reversible

Ninguna acción del sistema es irreversible sin que el cliente lo sepa y lo apruebe explícitamente.

- **Deriva de:** AD-001 §5, Filosofía #4.
- **Garantiza:** que un cliente pueda deshacer, cuestionar o revisar cualquier decisión previa sin perder lo construido antes de ella.
- **Violación de ejemplo:** un cambio de estrategia en Nivel 3 borra silenciosamente el Business Model Canvas del Nivel 2 en vez de versionarlo.

### 1.4 Toda decisión tiene responsable

Toda decisión registrada identifica quién la propuso y quién la aprobó — nunca "el sistema decidió" sin atribución.

- **Deriva de:** AD-001 §11 (regla 3), §12 (principio inviolable #2).
- **Garantiza:** que exista siempre una persona o un rol claramente identificado detrás de cada decisión, humano o agente.
- **Violación de ejemplo:** el sistema avanza de Nivel automáticamente sin que quede registrado qué agente lo recomendó y qué humano lo aprobó.

### 1.5 Nada se pierde

Ninguna información generada por el sistema se descarta silenciosamente; lo que deja de ser relevante se archiva, nunca se borra.

- **Deriva de:** AD-001, Visión a 25 Años; AD-001 §12 (principio inviolable #4).
- **Garantiza:** que una empresa acompañada por ADÁN nunca pierda su historial, incluso si pivota, se pausa o cambia de fundador.
- **Violación de ejemplo:** al reiniciar la estrategia de una empresa, se sobreescribe el historial de decisiones anteriores en vez de archivarlo y comenzar una nueva rama.

### 1.6 Toda IA debe justificar

Ninguna salida generada por un agente se presenta sin que su razonamiento esté disponible bajo solicitud del cliente.

- **Deriva de:** AD-001 §5, §11 (regla 2).
- **Garantiza:** que "porque lo dijo la IA" nunca sea una respuesta válida dentro del sistema.
- **Violación de ejemplo:** un agente presenta una recomendación final sin que exista, en ningún lugar del sistema, el razonamiento que la produjo.

### 1.7 Todo tiene versión

Ningún documento, entidad o configuración del sistema se sobreescribe silenciosamente; todo cambio relevante genera una versión nueva con su propio registro de qué cambió y por qué.

- **Deriva de:** AD-001 §12 (principio inviolable #4).
- **Garantiza:** trazabilidad histórica completa de cómo evolucionó cada elemento del sistema, no solo su estado actual.
- **Ya en práctica:** esta misma WO-000 es la instancia viva de esta regla — la existencia misma de este archivo (v2.0, sucediendo a un v1.0 aprobado el mismo día) es la demostración, no solo la declaración.
- **Violación de ejemplo:** un agente edita el Plan de Negocio de un cliente en el sitio, sin dejar rastro de la versión anterior.

### 1.8 Todo genera memoria

Ninguna interacción relevante desaparece al cerrar una sesión; se resume, se conecta al Gemelo Digital correspondiente, y queda disponible para el resto del sistema.

- **Deriva de:** AD-001 §1.
- **Garantiza:** que el cliente nunca tenga que repetir información ya provista, sin importar cuánto tiempo haya pasado entre sesiones.
- **Adelanto técnico:** la mecánica de resumen y jerarquía de contexto se especifica en AD-CMP-04; esta regla solo fija que debe existir, no cómo.
- **Violación de ejemplo:** el cliente vuelve después de un mes y ADÁN le pregunta de nuevo información que ya había dado en el Nivel 1.

### 1.9 Todo tiene un nivel de confianza declarado

Ninguna salida del sistema —recomendación, score, documento— se presenta sin declarar qué tan respaldada está por evidencia. Cuando el nivel de confianza es bajo, se dice explícitamente; nunca se disfraza de certeza.

- **Deriva de:** AD-001 §6.1 (Principio de Humildad Intelectual), §12 (principio inviolable #6).
- **Garantiza:** que un cliente nunca confunda una hipótesis bien redactada con un hecho verificado.
- **Coherencia deliberada:** esta regla es la razón por la que cada documento de esta misma WO-000 declara su propio Confidence Level desde v3.1 — la especificación del producto ya practica la regla que le exige al producto.
- **Violación de ejemplo:** un Score de mercado se presenta como "78/100" sin indicar si esa cifra se apoya en cinco entrevistas reales o en una estimación sin validar.

### 1.10 Economía Conceptual *(nuevo en v2.0)*

Cada concepto nuevo que se incorpora al sistema —una entidad, un término, un documento, una funcionalidad— aumenta la complejidad permanente del producto. Por eso ningún concepto nuevo se incorpora sin demostrar tres cosas a la vez: que resuelve un problema real, que no puede expresarse reutilizando un concepto ya existente, y que el valor que aporta supera la complejidad que agrega.

- **Deriva de:** instrucción directa del Board tras la aprobación de AD-002 v1.0, motivada por el riesgo real de que una especificación de 58 documentos y potencialmente más de 2.000 páginas acumule complejidad conceptual no examinada.
- **Garantiza:** que el vocabulario, el modelo de dominio y las funcionalidades de ADÁN no crezcan por inercia documental — cada pieza nueva tiene que justificar su propia existencia antes de incorporarse.
- **Relación con la Regla de No Duplicación (v3.1 §1):** son complementarias, no idénticas. No duplicación evita que un concepto ya definido se redefina con otras palabras en otro lugar. Economía Conceptual evita que se defina un concepto genuinamente nuevo cuando, en realidad, no hacía falta ninguno.
- **Violación de ejemplo:** proponer una entidad "Hito" distinta de "Evento" (AD-006) sin poder explicar qué problema resuelve "Hito" que "Evento" con un atributo adicional no resolvería igual.
- **Aplicación inmediata:** esta regla se aplicó, por primera vez, en la autoauditoría de AD-003, entregada junto con ese documento — ver ahí el razonamiento concreto de qué términos recibieron tratamiento completo y cuáles no, precisamente en cumplimiento de esta regla.

**Confidence Level de esta sección: 74%** — las reglas 1.1 a 1.8 derivan directamente de descripciones ya existentes en Chat 1.docx y del alcance original de AD-002 (v3.1); la regla 1.9 deriva del Principio de Humildad Intelectual, agregado por el Board a AD-001; la regla 1.10 es transcripción directa y casi textual de la instrucción del Board — la de mayor confianza de las diez, precisamente por no requerir interpretación.

---

## 2. Checklist de Justificación de Diseño

Sin cambios respecto a v1.0. Toda decisión de diseño no trivial que se tome en cualquier documento posterior de la WO-000 debe poder responder estas siete preguntas:

| Dimensión | Pregunta que obliga a responder |
|---|---|
| UX | ¿Esta decisión reduce o aumenta la carga cognitiva del usuario? |
| Ingeniería | ¿Esta decisión es sostenible de mantener, o genera deuda técnica oculta? |
| Escalabilidad | ¿Esta decisión sigue funcionando con diez o cien veces el volumen actual? |
| Multiagentes | ¿Esta decisión respeta el principio de consenso (AD-CMP-02) o introduce ambigüedad entre agentes? |
| Performance | ¿Esta decisión introduce latencia o costo computacional injustificado? |
| Seguridad | ¿Esta decisión expone información o una superficie de ataque nueva? |
| Costo | ¿Esta decisión es defendible frente a la economía unitaria del sistema (Unit Economics, reservado en WO-100)? |

A partir de esta versión, toda decisión de diseño no trivial también debe poder responder la Regla 1.10: ¿este concepto ya existe en otro documento? ¿el problema que resuelve justifica su propia existencia? Es, en efecto, una octava pregunta del checklist, aunque vive formalmente como principio de sistema (sección 1.10) y no como fila de esta tabla, para no duplicarla en dos lugares (Regla de No Duplicación, v3.1 §1).

---

## Dependencias

- AD-001 Product DNA (las diez reglas de este documento son la traducción operativa de sus principios de identidad)

## Documentos relacionados

- AD-CMP-01 a AD-CMP-06 (cada comportamiento debe poder señalar qué regla de este documento implementa)
- AD-ARQ-01 a AD-ARQ-10 (la implementación técnica de estas diez reglas vive ahí, en Fase 2)
- AD-007 Gemelo Digital (implementa directamente las reglas 1.3, 1.5 y 1.7)
- AD-FUNC-07 Sistema de Scoring (implementa directamente la regla 1.9)
- AD-OPS-02 Auditoría (implementa directamente las reglas 1.2 y 1.4)
- AD-003 Product Language (primer documento auditado bajo la Regla 1.10 — ver su autoauditoría)

## Impacto sobre otros módulos

Sin cambios respecto a v1.0, más uno nuevo:

1. AD-ARQ-04 y AD-ARQ-07 deben demostrar cómo se cumplen las reglas 1.5, 1.7 y 1.8 a nivel de almacenamiento real.
2. AD-FUNC-07 y AD-ARQ-10 deben definir el mecanismo concreto por el cual un score comunica su propio nivel de confianza (regla 1.9).
3. AD-OPS-02 hereda directamente las reglas 1.2 y 1.4.
4. **Nuevo:** todo documento de la WO-000 a partir de aquí debe incluir, en su autoauditoría previa a la entrega, una verificación explícita de la Regla 1.10 — qué conceptos nuevos introduce y por qué no podían evitarse.

## Riesgos

- **Riesgo de que las diez reglas queden como aspiración, no como restricción verificable.** Sin cambios respecto a v1.0 — mitigado solo cuando Fase 2 construya mecanismos técnicos concretos para cada una.
- **Riesgo de que Economía Conceptual se use para justificar no crear algo que sí hacía falta.** Es el riesgo simétrico al que la regla busca prevenir: un concepto necesario, rechazado por exceso de celo. Mitigación: la regla exige demostrar las tres condiciones a la vez, no solo una — un concepto que resuelve un problema real y no puede expresarse con lo existente sí debe incorporarse, aunque agregue complejidad.

## Preguntas abiertas

- Mecanismo concreto de la regla 1.9 (heredada de v1.0, sin resolver aún — ver AD-CMP-05 y AD-FUNC-07).

## Decisiones pendientes

Ninguna decisión de negocio pendiente en este documento.

## Historial de cambios

| Versión | Fecha | Cambio | Motivo |
|---|---|---|---|
| v1.0 | 2026-07-14 | Creación inicial: nueve reglas de sistema y checklist de justificación de diseño | Tercer documento de la WO-000 |
| v1.0 — Aprobada | 2026-07-14 | Aprobación formal del Board, sin cambios de contenido. Congelada | Cierre del ciclo de revisión de v1.0 |
| v2.0 | 2026-07-14 | Se agrega la Regla 1.10 (Economía Conceptual) como décimo principio permanente; se actualiza el checklist de la sección 2 con una nota de referencia cruzada; se actualiza Confidence Level y las secciones de cierre | Instrucción directa del Board inmediatamente después de aprobar v1.0 — primer caso real de la disciplina de versionado sobre un documento ya aprobado |
| v2.0 — Aprobada | 2026-07-14 | Aprobación formal del Board, sin cambios de contenido. Se congela | Cierre del ciclo de revisión de AD-002 v2.0 |
