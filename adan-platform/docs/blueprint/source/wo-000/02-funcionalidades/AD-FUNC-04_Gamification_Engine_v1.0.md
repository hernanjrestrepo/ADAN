---
Código: AD-FUNC-04
Nombre: Gamification Engine
Versión: v1.0
Estado: Construido y autoauditado. Congelado por Claude Code bajo la metodología "se construye, se autoaudita, se congela, se continúa"
Confidence Level: 50%
Fecha: 2026-07-14
Responsable (autor): CC (Claude Code)
Aprobador: Hernán / Junta Directiva (validación en el próximo Gate Review)
---

# AD-FUNC-04 — Gamification Engine

> Por instrucción explícita del Board: este documento no diseña mecánicas de juego. Diseña el **ritmo psicológico** con el que el empresario vive los siete Niveles. XP, logros, oficinas, avatares, rankings, insignias y recompensas son herramientas — nunca el objetivo. El objetivo real es mantener al empresario comprometido durante un proceso que puede durar semanas o meses, sin manipularlo ni distraerlo de su propósito real: construir su empresa, no acumular puntos.

**Nivel de contenido:** los Siete Ritmos (sección 1) y la Regla Anti-Manipulación (sección 3) son Principio Permanente. Las mecánicas específicas (sección 2) son Decisión de Diseño, sujetas a AD-004 §1 — pueden cambiar de forma libremente sin tocar el ritmo o la emoción que sirven.

---

## 0. Principio rector: el ritmo se diseña antes que la mecánica

Mismo principio que AD-FUNC-03 §0, aplicado a una dimensión distinta. AD-FUNC-03 fijó *qué debe sentir* el empresario en cada Nivel. Este documento fija *a qué velocidad y con qué densidad* debe vivirlo. Ninguna mecánica de esta especificación nace sin responder dos preguntas a la vez: **¿qué emoción de AD-FUNC-03 fortalece?** y **¿qué ritmo de este documento sirve?** Una mecánica que no puede responder ambas no se admite — es la aplicación directa del Criterio de Existencia (AD-004 v1.1 §3.1) a nivel de mecánica individual, no solo de Funcionalidad completa.

---

## 1. Los Siete Ritmos

| Nivel | Ritmo | Por qué | Duración de sesión típica | Frecuencia de interacción | Agentes visibles |
|---|---|---|---|---|---|
| 1 — El Dolor | **Inmediato** | Sirve a "Comprendido" (AD-FUNC-03): una respuesta lenta en el primer contacto se lee como desinterés, exactamente lo opuesto a sentirse escuchado | Corta, ágil | Alta — intercambios rápidos y frecuentes | Uno — se siente como una sola persona atenta, no un comité desde el minuto uno |
| 2 — Propuesta de Valor | **Exploratorio** | Sirve a "Inspirado por la claridad": el ritmo debe permitir ida y vuelta sobre variaciones de la propuesta, sin apurar la iteración | Media, con pausas para comparar | Media | Uno a dos — puede aparecer un segundo Agente al comparar con el mercado |
| 3 — Plan de Negocios | **Reflexivo** | Sirve a "Seguro": la complejidad legal/financiera real de este Nivel exige pausas explícitas, nunca avanzar rápido sobre algo que compromete capital real | Larga, con pausas explícitas entre bloques (legal, financiero, organizacional) | Baja-media, pero sostenida | Varios — la complejidad ya amerita mostrar que distintas especialidades están involucradas |
| 4 — MVP | **Constructivo** | Sirve a "Emocionado con base real": ritmo colaborativo e iterativo sobre el blueprint, ni tan rápido que se sienta improvisado ni tan lento que apague el entusiasmo | Media-larga, con ciclos cortos de iteración visual | Media-alta | Uno a dos — foco en construcción, no en comité |
| 5 — Validación Simulada | **Intenso** | Sirve a "Desafiado, no amenazado": múltiples escenarios simulados en sucesión rápida, con la seguridad explícita de que es un entorno de práctica | Corta por escenario, varias en la misma sesión | Alta | Varios, simultáneos — hace tangible que se trata de una simulación con múltiples ángulos a la vez |
| 6 — Lanzamiento y Operación | **Estable** | Sirve a "Acompañado": nada de picos ni urgencia — presencia constante y predecible, coherente con el momento de mayor riesgo real | Corta, pero regular — check-ins predecibles, no maratones | Media, constante en el tiempo (no se apaga tras el lanzamiento) | Uno — vuelve a sentirse como una sola voz de confianza, ahora en operación, no en deliberación |
| 7 — Escalamiento | **Expansivo** | Sirve a "Ambicioso": sesiones más espaciosas, mirada de horizonte más amplio, menos urgencia de cierre inmediato | Larga, menos frecuente | Baja frecuencia, alta profundidad | Varios — vuelve el comité, ahora para pensar en grande, no para resolver una crisis |

**Densidad de información:** escala con la complejidad real del Nivel (Reflexivo e Intenso son los más densos), nunca de forma artificial para "parecer robusto".

**Pausas:** se insertan donde el Ritmo lo exige (explícitas en Reflexivo, ausentes por diseño en Inmediato) — nunca como recurso genérico de todos los Niveles por igual.

**Celebraciones:** proporcionales al logro real que las produce (Regla de la sección 3) — un cierre de Nivel 3 (Reflexivo, alto en riesgo real evitado) amerita un reconocimiento más sustancial que completar un formulario de Nivel 1.

**Momentos de reflexión:** el sistema invita explícitamente a pausar y pensar en Niveles 3, 5 y 7 (los de mayor densidad o mayor apuesta); en Niveles 1, 4 y 6 el sistema favorece continuidad sobre interrupción, coherente con sus ritmos Inmediato, Constructivo y Estable.

---

## 2. Mecánicas al servicio del ritmo y la emoción

Ninguna se describe con detalle visual (eso es AD-UX) — solo se justifica su existencia:

| Mecánica | Emoción que fortalece (AD-FUNC-03) | Ritmo que sirve | Condición de uso |
|---|---|---|---|
| **XP (experiencia acumulada)** | Emocionado, Ambicioso | Constructivo, Expansivo | Debe ser proporcional a evidencia real generada en el Gemelo Digital (Criterio de Existencia) — nunca a tiempo conectado, clics, o frecuencia de inicio de sesión |
| **Logros / insignias** | Seguro, Acompañado | Reflexivo, Estable | Corresponden 1:1 a un hito real del Gemelo Digital (ej. "primera Decisión de Negocio aprobada", "primer Cliente Final real") — nunca a hábitos de uso ("iniciaste sesión 5 días seguidos" queda explícitamente prohibido, sección 3) |
| **Oficinas virtuales / avatares** | Seguro, Desafiado | Reflexivo, Intenso | Hacen tangible la metáfora de comité ejecutivo (AD-001 §1) — nunca decoración sin función; su presencia debe coincidir con la cantidad de Agentes visibles de la tabla de la sección 1 |
| **Rankings** | *(ninguna emoción de AD-FUNC-03 lo requiere directamente — ver nota)* | — | Ver sección 2.1, tratamiento especial |
| **Recompensas genéricas** | Depende del Nivel | Depende del Nivel | Prohibidas si no están conectadas a un cambio real y verificable en el Gemelo Digital — nunca "premios sorpresa" sin causa |

### 2.1 Rankings — tratamiento especial

Ningún ranking comparativo entre empresarios distintos se admite por defecto. Comparar a un founder contra otros introduce ansiedad social no solicitada, exactamente lo que la "confianza calmada" de AD-001 §14 prohíbe. En su lugar, si se implementa algún índice de progreso, debe comparar **al empresario consigo mismo en el tiempo** — usando la Velocidad de Maduración Organizacional ya definida en AD-005 §4, que existe precisamente para esto. Un ranking social entre founders, si se justifica en el futuro con evidencia real de que ayuda (no de que "engancha"), requiere una nueva versión de este documento — no se admite por defecto en v1.0.

---

## 3. Regla Anti-Manipulación

Aplicación directa, a nivel de mecánica, del principio ya fijado en AD-001 §14.1 (Emoción Reflejada) y del Criterio de Existencia (AD-004 §3.1). Prohibido, sin excepción:

- **Notificaciones de urgencia artificial** ("tu racha se va a perder", "quedan 2 horas") — ya prohibidas por AD-001 §14.
- **Streaks que castigan la ausencia con culpa.** Un founder que se ausenta porque está atendiendo su negocio real —la razón misma por la que usa ADÁN— nunca debe sentir que "falló" al sistema.
- **Rankings sociales forzados o visibles por defecto** (sección 2.1).
- **Recompensas desconectadas de evidencia real** (Criterio de Existencia, sección 2).
- **Cualquier mecánica que aumente el tiempo en la plataforma sin aumentar evidencia real en el Gemelo Digital.** Esta es la prueba más general y la más importante: si una mecánica hace que el empresario pase más tiempo interactuando sin que eso produzca una sola entidad nueva o actualizada en su Gemelo Digital, esa mecánica compite con el objetivo real del empresario en vez de servirlo — y no se admite, sin importar cuánto "enganche" produzca.

---

## Dependencias

- AD-FUNC-03 Experience Engine (las Siete Emociones Objetivo que toda mecánica debe servir)
- AD-001 Product DNA v1.1 §14.1 (Principio de Emoción Reflejada)
- AD-004 v1.1 §3.1 (Criterio de Existencia)
- AD-005 Enterprise Domain Model §4 (Velocidad de Maduración Organizacional, base del tratamiento de rankings)

## Documentos relacionados

- AD-UX (implementación visual de oficinas, avatares, badges — Decisión de Diseño, no resuelta aquí)
- AD-FUNC-01 Los 7 Niveles (fuente de los hitos reales que las mecánicas reflejan)

## Impacto sobre otros módulos

1. Todo AD-UX que diseñe una mecánica visual debe declarar explícitamente a qué fila de la sección 1 (ritmo) y de la sección 2 (mecánica/emoción) sirve.
2. Ningún ranking social entre founders puede implementarse sin una nueva versión de este documento con evidencia real que lo justifique (sección 2.1).
3. AD-ARQ (Fase 2) debe garantizar técnicamente que XP, logros e insignias solo se generan a partir de cambios verificables en el Gemelo Digital — nunca de eventos de interfaz sin correspondencia real.

## Riesgos

- **Riesgo de que "ritmo psicológico" sea difícil de calibrar sin datos reales de uso** — los Siete Ritmos son una hipótesis de diseño razonada, no medida todavía.
- **Riesgo de presión comercial futura por introducir rankings sociales** ("aumentan el engagement") que contradiga la sección 2.1 — este documento fija la barrera alta a propósito.

## Preguntas abiertas

Ninguna nueva.

## Decisiones pendientes

Ninguna decisión de negocio pendiente en este documento.

## Historial de cambios

| Versión | Fecha | Cambio | Motivo |
|---|---|---|---|
| v1.0 | 2026-07-14 | Creación inicial: Siete Ritmos psicológicos (uno por Nivel), mecánicas tratadas exclusivamente como herramientas al servicio de emoción (AD-FUNC-03) y ritmo, tratamiento especial de rankings (comparación consigo mismo vía Velocidad de Maduración, no comparación social), Regla Anti-Manipulación con cinco prohibiciones explícitas | Cuarto documento de la categoría Funcionalidades |
