---
Código: AD-CMP-05
Nombre: Comportamiento de Evidencia y Scoring
Versión: v1.0
Estado: Construido y autoauditado. Congelado bajo la metodología "se construye, se autoaudita, se congela, se continúa"
Confidence Level: 60%
Fecha: 2026-07-14
Responsable (autor): CC (Claude Code)
Aprobador: Hernán / Junta Directiva (validación en el próximo Gate Review)
---

# AD-CMP-05 — Comportamiento de Evidencia y Scoring

> Especifica cómo una conversación se convierte en un Score objetivo (AD-006) — el proceso conceptual, no la fórmula matemática (esa es AD-ARQ-10). Es, probablemente, el documento de Comportamientos con más consecuencias prácticas: de él depende directamente si AD-CMP-01 (Progresión) puede funcionar con integridad.

**Nivel de contenido:** Principio Permanente en su totalidad — los pesos y umbrales exactos de cada Score son Decisión de Diseño de AD-ARQ-10.

---

## 1. Qué cuenta como evidencia válida

Jerarquía de validez, de mayor a menor:

1. **Dato verificable externamente** (una fuente de mercado, un documento del cliente, un registro público) — la evidencia más fuerte.
2. **Testimonio directo del cliente**, cuando no hay dato externo disponible pero el cliente lo declara explícitamente.
3. **Inferencia razonada de un Agente**, siempre marcada como tal y siempre con Confidence Level más bajo que las dos anteriores (Regla 1.9 de AD-002).

**La inspección de una Conversación, por sí sola, nunca es evidencia suficiente** — heredado directamente de la metodología original del proyecto ("la inspección de código no constituye evidencia suficiente"), aplicado aquí a conversaciones: que un Agente haya "hablado del tema" no prueba nada sobre la empresa real.

## 2. El proceso: de conversación a Score

```
Conversación → se extraen afirmaciones verificables
             → cada afirmación se clasifica según la jerarquía de la sección 1
             → se agregan las afirmaciones válidas relevantes a la dimensión que se evalúa
             → se produce un Score con su Confidence Level declarado
```

Ninguna afirmación sin clasificar entra al cálculo. Si la evidencia disponible para una dimensión es insuficiente, el Score correspondiente se declara con Confidence Level bajo explícitamente — nunca se omite ni se rellena con un valor por defecto que aparente certeza (Principio de Humildad Intelectual, AD-001 §6.1).

## 3. Relación con Indicador (AD-005)

Un Score (evaluación que ADÁN hace de una Empresa) es distinto de un Indicador (una métrica que la propia Empresa usa para medir su Meta, AD-005) — pero puede consumir Indicadores como una fuente más de evidencia dentro de la jerarquía de la sección 1 (un Indicador reportado por la Empresa es, en la práctica, un dato verificable si tiene fuente, o un testimonio del cliente si no la tiene). No se fusionan los dos conceptos — se relacionan.

## 4. Actualización del Score en el tiempo

Cada nuevo cálculo de un Score es un registro nuevo (Patrón C, AD-008) — nunca sobreescribe al anterior. Esto es lo que permite calcular la Velocidad de Maduración Organizacional (AD-005 §4) sin ningún mecanismo adicional: la serie histórica de Scores y de Madurez ya existe por diseño, gratis, en cumplimiento de la Regla 1.7 de AD-002.

---

## Dependencias

- AD-006 Domain Model v1.1 (entidad Score)
- AD-005 Enterprise Domain Model (entidad Indicador, dimensiones de Madurez)
- AD-002 Principios del Sistema v2.0 (reglas 1.1, 1.9)
- AD-001 Product DNA §6.1 (Humildad Intelectual)

## Documentos relacionados

- AD-CMP-01 (consume este documento para definir "evidencia suficiente" de avance de Nivel)
- AD-FUNC-07 Sistema de Scoring (Producto) — define qué significa cada Score para el usuario
- AD-ARQ-10 Motor de Scoring (Cálculo) — fórmula, pesos, umbrales

## Impacto sobre otros módulos

AD-FUNC-07 y AD-ARQ-10 no pueden definir un Score sin pasar sus entradas por la jerarquía de validez de la sección 1 — evita que "más conversación" se confunda con "más evidencia".

## Riesgos

- Riesgo de que la clasificación de afirmaciones (sección 2) resulte ambigua en la práctica sin ejemplos reales que la calibren — se resolverá con el primer cliente real, no antes.

## Preguntas abiertas

Ninguna nueva.

## Decisiones pendientes

Ninguna decisión de negocio pendiente en este documento.

## Historial de cambios

| Versión | Fecha | Cambio | Motivo |
|---|---|---|---|
| v1.0 | 2026-07-14 | Creación inicial | Décimo cuarto documento de la WO-000 |
