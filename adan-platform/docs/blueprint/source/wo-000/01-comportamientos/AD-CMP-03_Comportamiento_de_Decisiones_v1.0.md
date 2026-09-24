---
Código: AD-CMP-03
Nombre: Comportamiento de Decisiones
Versión: v1.0
Estado: Construido y autoauditado. Congelado bajo la metodología "se construye, se autoaudita, se congela, se continúa"
Confidence Level: 63%
Fecha: 2026-07-14
Responsable (autor): CC (Claude Code)
Aprobador: Hernán / Junta Directiva (validación en el próximo Gate Review)
---

# AD-CMP-03 — Comportamiento de Decisiones

> Especifica el ciclo de vida del objeto Decisión (de ADÁN, AD-006) usando el Patrón A (Ciclo de Aprobación) ya fijado en AD-008: quién propone, quién aprueba, cómo se documenta un desacuerdo, y la consulta previa que evita contradicciones.

**Nivel de contenido:** Principio Permanente en su totalidad.

---

## 1. Ciclo de vida (aplicación del Patrón A)

`Propuesta` (por uno o más Agentes, con la evidencia que la respalda) → `Presentada al cliente` (con razonamiento visible bajo solicitud, Regla 1.6 de AD-002) → `Aprobada` o `Rechazada` (exclusivamente por el Usuario Principal, o por el Usuario con delegación explícita, sección 3 de AD-008) → `Ejecutada` (solo si fue Aprobada).

Ninguna Decisión pasa a `Ejecutada` sin haber pasado por `Aprobada` — es la traducción literal, a nivel de objeto, del principio inviolable de AD-001 §12.

## 2. Consulta previa obligatoria

Antes de proponer una Decisión nueva, el procedimiento exige consultar las Decisiones ya `Aprobadas` o `Ejecutadas` relevantes para la misma Empresa (accesibles vía el Gemelo Digital, AD-007) — esto evita que ADÁN proponga algo que contradice una decisión ya tomada, sin tener que confiar en que un Agente "recuerde" el historial. Es la aplicación operativa de la Regla 1.8 de AD-002 (todo genera memoria) al objeto Decisión específicamente.

## 3. Cómo se documenta un desacuerdo

Si la propuesta de una Decisión surgió de un proceso de Consenso Multiagente (AD-CMP-02) con discrepancia material sin resolver, esa discrepancia se adjunta a la Decisión como parte de su registro permanente — nunca se descarta al sintetizar la propuesta final. Cuando el contexto lo amerita (Board Room, AD-FUNC-02), este desacuerdo se hace visible al cliente antes de pedir su aprobación, no después.

## 4. Relación con Decisión de Negocio

Una Decisión (de ADÁN) `Ejecutada` puede *originar* una Decisión de Negocio (AD-005) cuando el cliente actúa en el mundo real siguiendo la recomendación — pero esa transición no es automática ni garantizada: el cliente puede aprobar una Decisión de ADÁN y aun así, en la práctica, tomar un curso de acción distinto. Ambos objetos se relacionan (Workshop de Relaciones), nunca se fusionan.

---

## Dependencias

- AD-008 Objetos del Sistema (Patrón A)
- AD-006 Domain Model v1.1 (entidad Decisión)
- AD-007 Gemelo Digital (fuente del historial consultado en la sección 2)
- AD-CMP-02 Comportamiento de Consenso Multiagente

## Documentos relacionados

- AD-UX-10 Decisiones (Vista DEC) — consume este ciclo de vida directamente
- AD-FUNC-02 Board Room

## Impacto sobre otros módulos

AD-UX-10 debe representar visualmente los cuatro estados del Patrón A aplicados aquí, incluyendo el desacuerdo adjunto cuando exista.

## Riesgos

Ninguno nuevo más allá de los ya heredados de AD-CMP-02.

## Preguntas abiertas

Ninguna nueva.

## Decisiones pendientes

Ninguna decisión de negocio pendiente en este documento.

## Historial de cambios

| Versión | Fecha | Cambio | Motivo |
|---|---|---|---|
| v1.0 | 2026-07-14 | Creación inicial | Duodécimo documento de la WO-000 |
