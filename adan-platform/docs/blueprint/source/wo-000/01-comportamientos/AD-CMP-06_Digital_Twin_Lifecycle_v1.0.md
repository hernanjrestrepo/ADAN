---
Código: AD-CMP-06
Nombre: Digital Twin Lifecycle
Versión: v1.0
Estado: Construido y autoauditado. Congelado bajo la metodología "se construye, se autoaudita, se congela, se continúa"
Confidence Level: 58%
Fecha: 2026-07-14
Responsable (autor): CC (Claude Code)
Aprobador: Hernán / Junta Directiva (validación en el próximo Gate Review)
---

# AD-CMP-06 — Digital Twin Lifecycle

> AD-007 definió qué es el Gemelo Digital (el límite de agregación entre Empresa y Proyecto) y dejó su comportamiento en el tiempo explícitamente fuera de su alcance, asignado aquí. Este documento resuelve, entre otras cosas, la pregunta abierta que AD-007 dejó pendiente: qué pasa cuando dos Empresas se fusionan o una se divide.

**Nivel de contenido:** Principio Permanente en su totalidad.

---

## 1. Nace

Un Gemelo Digital nace en el mismo momento en que nace su Proyecto correspondiente (AD-006) — que, por la relación 1:1:1 ya fijada en AD-007 §1, coincide con el momento en que la Ley de Origen (AD-005 §5, Ley 1) se satisface: Narrativa Fundacional + evidencia + compromiso de recursos irreversible. No existe un Gemelo Digital "vacío" a la espera de una Empresa — los tres nacen juntos.

## 2. Crece

Crecer, para un Gemelo Digital, es exactamente lo que la Regla 1.7 de AD-002 (todo tiene versión) ya garantiza: cada nueva entidad de negocio agregada, cada Decisión, cada Score, cada Documento, se suma a su historial sin sobreescribir nada anterior. No hay un mecanismo adicional que diseñar aquí — es la aplicación acumulativa, en el tiempo, de reglas ya vigentes desde AD-002.

## 3. Cambia

Un Gemelo Digital cambia de naturaleza cuando su Empresa atraviesa una Reinvención (AD-005 §5, Ley 9) — cambio de Narrativa Fundacional por aprendizaje de bucle doble. El Gemelo Digital no se reinicia: conserva su identidad e historial completo desde antes de la Reinvención, porque la identidad permanente es precisamente lo que AD-007 declaró que protege. Lo que cambia es el contenido de la Narrativa Fundacional, no el Gemelo Digital que la contiene.

## 4. Se divide

Ocurre cuando una Iniciativa (AD-005) se separa de su Empresa original para convertirse en una Empresa nueva — el caso que AD-004 §4 ya anticipó como "graduación", aplicado ahora a nivel de negocio del cliente, no de Funcionalidad de ADÁN. Procedimiento:

1. Se crea un Gemelo Digital nuevo, con su propio Proyecto nuevo (nace, sección 1).
2. El Gemelo Digital nuevo hereda, por referencia —no por copia— el historial relevante de la Iniciativa que le dio origen: qué Decisiones, Documentos y Evidencia la produjeron.
3. El Gemelo Digital original conserva su propio historial completo, incluida la Iniciativa ya derivada, marcada como "separada hacia" el nuevo Gemelo Digital — nunca se borra la referencia (Regla 1.5 de AD-002).

## 5. Se fusiona

Dos Gemelos Digitales se fusionan cuando sus Empresas correspondientes se fusionan en el mundo real. Procedimiento:

1. Se crea un Gemelo Digital nuevo para la Empresa resultante (nace, sección 1) — la fusión no elige a "ganador" entre los dos anteriores.
2. Ambos Gemelos Digitales originales se archivan (sección 6), no se borran — cada uno conserva su historial íntegro y queda referenciado desde el Gemelo Digital nuevo como "una de las Empresas que la originaron".
3. Ningún dato se copia dos veces: el Gemelo Digital nuevo referencia los historiales anteriores, no los duplica — aplicación directa de la Regla de No Duplicación (v3.1 §1) al propio dato del Gemelo Digital.

## 6. Se archiva

Ocurre tras la Ley de Muerte (AD-005 §5, Ley 8): la Empresa pierde la capacidad de generar nuevas Decisiones de Negocio respaldadas por evidencia. El Gemelo Digital nunca se elimina — pasa a estado `Archivado` (Patrón D, AD-008), sigue siendo consultable indefinidamente, en cumplimiento directo de la promesa de AD-001, Visión a 25 Años: *"el Gemelo Digital de las primeras empresas que usaron ADÁN debería seguir existiendo, seguir siendo consultable."*

---

## Dependencias

- AD-007 Gemelo Digital (estructura que este documento anima en el tiempo)
- AD-005 Enterprise Domain Model (Leyes 1, 8, 9)
- AD-004 Product Evolution §4 (graduación de Funcionalidades, patrón análogo aplicado aquí a Empresas)
- AD-008 Objetos del Sistema (Patrón D)
- AD-002 Principios del Sistema v2.0 (reglas 1.5, 1.7)

## Documentos relacionados

- AD-ARQ-04 Memoria (Motor Técnico) — implementación técnica de fusión/división, que este documento no diseña
- AD-FUNC-01 (el Nivel de una Empresa nueva tras una división hereda contexto según AD-CMP-04)

## Impacto sobre otros módulos

Resuelve formalmente la pregunta abierta que AD-007 había dejado pendiente (fusión/división) — AD-007 no requiere una nueva versión, su pregunta abierta se marca resuelta por referencia a este documento.

## Riesgos

- Riesgo de que "herencia por referencia, no por copia" (secciones 4 y 5) sea más compleja de implementar técnicamente de lo que este documento anticipa — señalado para que Fase 2 (AD-ARQ-04) lo evalúe con conocimiento de la intención, no en contra de ella, mismo patrón de riesgo ya usado en AD-007.

## Preguntas abiertas

Ninguna nueva.

## Decisiones pendientes

Ninguna decisión de negocio pendiente en este documento.

## Historial de cambios

| Versión | Fecha | Cambio | Motivo |
|---|---|---|---|
| v1.0 | 2026-07-14 | Creación inicial: ciclo de vida completo del Gemelo Digital (nace, crece, cambia, se divide, se fusiona, se archiva), resolviendo la pregunta abierta de AD-007 | Décimo quinto y último documento pendiente del Gate Review de Fase 1 |
