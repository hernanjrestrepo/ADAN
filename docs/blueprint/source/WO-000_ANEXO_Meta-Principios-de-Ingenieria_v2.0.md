---
Identificador: WO-000-ANEXO-MPI (no es un código AD-XXX — este anexo no cuenta entre los 58 documentos del árbol, es un estándar transversal que rige cómo se construyen todos ellos)
Nombre: Meta-Principios de Ingeniería
Versión: v2.0 — APROBADA Y CONGELADA
Estado: Aprobado. No editar en el sitio
Confidence Level: 68%
Fecha de aprobación: 2026-07-14
Responsable (autor del borrador): CC (Claude Code)
Aprobador: Hernán / Junta Directiva
Supersede a: WO-000_ANEXO_Meta-Principios-de-Ingenieria_v1.0.md (aprobado y congelado el mismo día — ver su Historial de cambios)
---

# WO-000 — Anexo: Meta-Principios de Ingeniería (v2.0)

> AD-001 gobierna quién es ADÁN. AD-002 gobierna qué debe garantizar el sistema. Este anexo gobierna cómo se toman las decisiones de construcción durante toda la vida del proyecto. No es un documento del Blueprint; es el criterio con el que se juzga cada documento del Blueprint, incluidos los que ya existen.

**Nivel de contenido:** Principio Permanente en su totalidad.

**Nota de versión:** esta v2.0 sucede a v1.0 —aprobada y congelada el mismo día— para incorporar el Principio de Emergencia. Tuvo dos revisiones antes de la aprobación final: primero se agregó como principio 10; el Board pidió reubicarlo como principio 2, porque el orden lógico correcto es evaluar primero si algo ya emerge de reglas existentes, y solo si no emerge, evaluar si vale la pena crear un concepto nuevo (Economía Conceptual, AD-002 §1.10). Emergencia no complementa a Economía Conceptual — la precede.

---

## 1. Los Diez Meta-Principios

### 1. El dominio prevalece sobre la tecnología
Ninguna decisión de dominio se toma en función de qué es fácil o difícil de implementar con la tecnología disponible hoy. Razón de fondo del backbone Domain Model → Arquitectura (v3.1 §12). *Violación de ejemplo:* cambiar la definición de "Nivel" porque el modelo de IA actual maneja mejor conversaciones cortas.

### 2. Principio de Emergencia

**Siempre que una capacidad pueda emerger de la combinación de principios ya existentes, queda prohibido convertirla en un nuevo concepto, entidad o documento. Primero debe demostrarse que las reglas actuales son insuficientes — solo entonces puede proponerse una nueva abstracción.**

- **Por qué ocupa el segundo lugar, no el décimo:** el flujo lógico correcto ante cualquier propuesta de concepto nuevo es (1) ¿ya emerge de combinar reglas existentes? — si sí, se descarta aquí mismo, sin seguir. (2) Si no emerge, ¿vale la pena crear el concepto de todas formas, dado lo que cuesta en complejidad? — esa es la pregunta de Economía Conceptual (AD-002 §1.10). Colocar Emergencia al final del anexo invertía el orden real de las preguntas; colocarlo en segundo lugar, inmediatamente después del principio más general (dominio sobre tecnología), refleja que es la primera pregunta de filtro ante cualquier idea nueva — antes incluso de discutir si es simple o compleja.
- **Por qué se formalizó:** ya se había aplicado dos veces sin existir como regla explícita. Enterprise Genome se rechazó porque toda su descripción ("identidad, cultura, conocimiento, estrategia...") ya emergía de lo que AD-000/AD-001 declaran que el Gemelo Digital representa. El "ciclo de vida de las relaciones" se rechazó porque nacer/fortalecerse/debilitarse/desaparecer ya emerge, de forma literal y citable, de AD-002 §§1.5 y 1.7 aplicadas a una relación tratada como objeto.
- **Cómo se aplica en la práctica:** antes de proponer un concepto nuevo, se responde primero: ¿qué reglas, principios o comportamientos ya aprobados, combinados, producirían este mismo resultado? Si existe esa combinación, se documenta y se descarta el concepto nuevo. Si no existe, recién ahí se evalúa contra Economía Conceptual (principio complementario, no un paso posterior de este mismo anexo — vive en AD-002 §1.10).
- **Violación de ejemplo:** proponer una entidad "Historial de Cambios de Precio" separada, cuando ya emerge de aplicar la Regla 1.7 (todo tiene versión) al atributo Precio de la entidad Producto.

### 3. La evidencia prevalece sobre la opinión
Extiende AD-001 Filosofía #2 y AD-002 regla 1.1 del producto al *proceso de construirlo*. *Violación de ejemplo:* agregar un documento nuevo "porque parece más completo", sin poder señalar qué riesgo mitiga.

### 4. La simplicidad prevalece sobre la sofisticación innecesaria
Distinto del principio 2 (Emergencia) y de Economía Conceptual (AD-002 §1.10), que preceden a esta pregunta: aquellos deciden si un concepto nuevo debe existir; este gobierna cuánta complejidad interna se permite dentro de un concepto ya aceptado. La simplicidad que protege es la del usuario y de quien mantiene el sistema — nunca a costa de eso se simplifica la implementación. *Violación de ejemplo:* un flujo de aprobación con cinco estados cuando dos bastan.

### 5. La experiencia del usuario prevalece sobre la comodidad de implementación
Heredado de AD-001 §14. Si hay que elegir dónde vive la complejidad, se absorbe internamente, nunca se traslada al usuario. *Violación de ejemplo:* mostrar un error técnico sin traducir porque es más rápido de implementar.

### 6. Toda decisión debe minimizar la complejidad futura
Mira hacia adelante, distinto del principio 4 (que mira el presente). *Violación de ejemplo:* fijar "7" en múltiples documentos en vez de derivarlo de una sola fuente de verdad.

### 7. Ninguna limitación temporal de una tecnología debe modificar el modelo conceptual del producto
Elaboración específica del principio 1, dirigida al caso de violación más tentador. *Violación de ejemplo:* eliminar el campo de confianza de un Score porque el modelo actual no calcula bien la incertidumbre.

### 8. La deuda conceptual es tan importante como la deuda técnica
Un término ambiguo o una entidad redundante sin resolver es tan costosa como código sin refactorizar. *Violación de ejemplo:* dejar sin resolver una colisión de nombre encontrada en autoauditoría "porque no rompe nada todavía".

### 9. Las decisiones irreversibles requieren mayor evidencia que las reversibles
Complementa la regla de reversibilidad de AD-002 (§1.3) para el subconjunto donde la reversibilidad no es posible. *Violación de ejemplo:* fijar un nombre de marca sin verificación de disponibilidad.

### 10. La arquitectura debe poder evolucionar sin romper el dominio
Sostiene por qué el backbone ordena Domain Model antes que Arquitectura. *Violación de ejemplo:* proponer que "Nivel" tenga una estructura de datos distinta de su definición conceptual "porque es más eficiente de consultar así".

**Confidence Level de esta sección: 68%** — el principio 2 (Emergencia) tiene la confianza más alta de los diez, porque no es una inferencia: es la formalización directa de un razonamiento ya ejecutado y verificado dos veces, y su reubicación a esta posición fue una corrección explícita del Board sobre el orden lógico de aplicación, no una hipótesis pendiente de validar.

---

## 2. Principios considerados y descartados

Sin cambios de fondo respecto a v1.0 — se mantienen los tres descartes originales (duplicado de Economía Conceptual, duplicado del mecanismo de Preguntas Abiertas, duplicado de la Regla 1.1). El Principio de Emergencia no reabre esa evaluación; la refuerza y, en retrospectiva, es la regla que debería haberse aplicado para llegar más rápido a esos tres descartes.

---

## Dependencias

- AD-001 Product DNA
- AD-002 Principios del Sistema v2.0

## Documentos relacionados

- Todo documento futuro de la WO-000.
- AD-004 Product Evolution (principios 1, 6, 7, 8 y 10 ya aplicados ahí)
- Enterprise Taxonomy Workshop y Workshop de Relaciones (primeras dos aplicaciones documentadas del Principio de Emergencia, antes de que existiera con ese nombre)
- Workshop de Comportamientos (tercera aplicación documentada — aplicado explícitamente a las diez leyes dinámicas, resultado: cero conceptos nuevos)

## Impacto sobre otros módulos

La autoauditoría obligatoria (v3.4 §1) queda ampliada en la práctica: la pregunta 4 ("¿qué conceptos nuevos aparecen, y realmente deben existir?") ahora tiene un procedimiento explícito, en el orden correcto — primero Emergencia (principio 2), después Economía Conceptual (AD-002 §1.10) solo si Emergencia no resuelve la pregunta.

## Riesgos

- **Riesgo de que "Emergencia" se use para negar avances legítimos.** Es invocable de forma retroactiva para rechazar cualquier propuesta. Mitigación: el principio exige demostrar la combinación específica de reglas que produce el resultado equivalente — una afirmación vaga de "esto ya emerge de algo" sin señalar qué regla exacta no es una aplicación válida del principio.
- **Riesgo de sobre-rigidez en ejercicios de modelado de dinámicas complejas.** Mitigado en la práctica — el Workshop de Comportamientos ya se sometió a esta prueba con las diez leyes dinámicas más tentadoras de convertir en entidades, y ninguna lo requirió.

## Preguntas abiertas

Ninguna al cierre de esta versión.

## Decisiones pendientes

Ninguna decisión de negocio pendiente en este anexo.

## Historial de cambios

| Versión | Fecha | Cambio | Motivo |
|---|---|---|---|
| v1.0 | 2026-07-14 | Creación inicial: ocho meta-principios instruidos por el Board, más un noveno propuesto por Claude Code | Anexo transversal de la WO-000 |
| v1.0 — Aprobada | 2026-07-14 | Aprobación formal, congelada | Cierre del ciclo de revisión |
| v2.0 (Revisión 1) | 2026-07-14 | Se agrega el Principio de Emergencia como principio 10 | Instrucción directa del Board tras observar el rechazo de Enterprise Genome y del ciclo de vida de relaciones |
| v2.0 (Revisión 2 — pre-aprobación) | 2026-07-14 | Se reubica el Principio de Emergencia de la posición 10 a la posición 2, inmediatamente después de "el dominio prevalece sobre la tecnología" — refleja el orden lógico real: Emergencia se evalúa antes que Economía Conceptual, no después. Se renumeran los principios 2-9 originales a 3-10 | El Board identificó que el orden de aplicación real era el inverso al orden de aparición en el documento |
| v2.0 — Aprobada | 2026-07-14 | Aprobación formal del Board, sin más cambios de contenido. Se congela | Cierre del ciclo de revisión del Anexo v2.0 |
