---
Código: AD-CMP-01
Nombre: Comportamiento de Progresión entre Niveles
Versión: v1.0
Estado: Construido y autoauditado. Congelado bajo la metodología "se construye, se autoaudita, se congela, se continúa"
Confidence Level: 62%
Fecha: 2026-07-14
Responsable (autor): CC (Claude Code)
Aprobador: Hernán / Junta Directiva (validación en el próximo Gate Review)
---

# AD-CMP-01 — Comportamiento de Progresión entre Niveles

> Especifica la regla de avance condicionado entre los Nivel de AD-006: un Nivel no se aprueba por pago, se aprueba por evidencia. Este documento define esa regla a nivel de dominio — sin lenguaje de implementación — usando el Patrón B (Progreso Secuencial) ya fijado en AD-008.

**Nivel de contenido:** Principio Permanente en su totalidad — el umbral exacto de "evidencia suficiente" por Nivel es Decisión de Diseño y se fija en AD-FUNC-01, no aquí.

---

## 1. La regla de avance condicionado

Un Nivel transiciona de `Activo` a `Completado` (Patrón B, AD-008 §2) únicamente cuando se cumplen, a la vez:

1. **Evidencia suficiente registrada** — evaluada según AD-CMP-05 (Comportamiento de Evidencia y Scoring), no por juicio subjetivo de un Agente.
2. **Aprobación explícita del Usuario Principal** — Patrón A aplicado aquí de forma cruzada: el avance de Nivel no es solo un Patrón B interno, requiere además una aprobación tipo Patrón A antes de completarse. Ningún Nivel avanza solo porque ADÁN considere que la evidencia alcanza.

**Ningún pago, por sí solo, produce esta transición.** El pago (fuera del alcance de este documento, reservado en WO-100) puede ser una condición adicional de negocio, pero nunca sustituye a la evidencia ni a la aprobación — invertir ese orden sería la violación más directa posible del principio inviolable de AD-001 §12.

## 2. Qué constituye evidencia suficiente

No se define aquí la fórmula (eso es AD-CMP-05 y, técnicamente, AD-ARQ-10) — se define el criterio de aceptación: evidencia suficiente es aquella que un Usuario Principal, al revisarla, puede verificar de forma independiente sin tener que confiar ciegamente en la palabra de un Agente. Cumple, por diseño, la Regla 1.1 de AD-002 (todo genera evidencia) y el Principio de Humildad Intelectual de AD-001 §6.1: si la evidencia disponible es insuficiente, el Nivel no avanza y ADÁN lo dice explícitamente, en vez de aproximar una respuesta.

## 3. Qué pasa si el cliente y el sistema no coinciden

Dos casos, tratados de forma distinta:

- **El sistema considera que la evidencia es suficiente, el cliente no está de acuerdo en avanzar.** Prevalece el cliente — el Nivel permanece `Activo`. Es la aplicación literal del principio inviolable "ninguna decisión importante avanza sin aprobación explícita del cliente" (AD-001 §12); el sistema no tiene autoridad para forzar un avance que el cliente no acepta.
- **El cliente quiere avanzar, el sistema considera que la evidencia es insuficiente.** ADÁN no bloquea de forma silenciosa — comunica explícitamente qué evidencia falta y por qué (Regla 1.6 de AD-002, toda IA debe justificar), y ofrece al cliente la opción de avanzar de todas formas bajo su propia responsabilidad, registrada como una Decisión (de ADÁN, Patrón A) con nivel de confianza bajo declarado (Regla 1.9). El sistema informa; nunca decide en lugar del cliente — pero tampoco oculta su desacuerdo para complacerlo.

---

## Dependencias

- AD-008 Objetos del Sistema (Patrón B, Patrón A cruzado)
- AD-006 Domain Model v1.1 (entidad Nivel)
- AD-002 Principios del Sistema v2.0 (reglas 1.1, 1.6, 1.9)

## Documentos relacionados

- AD-CMP-05 Comportamiento de Evidencia y Scoring (define qué es evidencia válida, referenciado, no duplicado aquí)
- AD-FUNC-01 Los 7 Niveles (fija el umbral exacto de evidencia por Nivel específico)

## Impacto sobre otros módulos

AD-FUNC-01 hereda esta regla como marco obligatorio — no puede definir un Nivel que avance sin evidencia o sin aprobación, sin contradecir este documento.

## Riesgos

- Riesgo de que "evidencia suficiente" siga siendo un criterio cualitativo hasta que AD-CMP-05 y AD-ARQ-10 lo hagan medible — este documento fija el principio, no la métrica.

## Preguntas abiertas

Ninguna nueva.

## Decisiones pendientes

Ninguna decisión de negocio pendiente en este documento.

## Historial de cambios

| Versión | Fecha | Cambio | Motivo |
|---|---|---|---|
| v1.0 | 2026-07-14 | Creación inicial | Décimo documento de la WO-000, segundo de los siete pendientes del Gate Review |
