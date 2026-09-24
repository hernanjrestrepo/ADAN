# WO-000 — Índice Maestro de Especificación de Producto ADÁN (v3.21)

**Tipo de documento:** Árbol documental — **APROBADO Y CONGELADO** (sin cambios de estructura desde v3.1).
**Estado de la WO-000:** Fase 1 completa. Funcionalidades: AD-FUNC-01 a 03 aprobados; AD-FUNC-04 construido y autoauditado; **AD-FUNC-05 APPROVED FOR GATE REVIEW**; AD-FUNC-06 construido y autoauditado (Revisión 2).

---

## 0. Qué cambió respecto a v3.20

1. **AD-FUNC-05 — aprobado formalmente por el Board.** "Considero cerrado el documento, no veo valor en seguir iterándolo. El hecho de que la revisión de consistencia solo encontrara correcciones editoriales y no problemas de arquitectura es una muy buena señal." Estado actualizado a **APPROVED FOR GATE REVIEW** — queda disponible como dependencia estable para el resto del árbol, sin más rondas de revisión previstas.
2. **AD-FUNC-06 — Revisión 2.** Sin cambiar el modelo, se enriqueció con cuatro adiciones pedidas por el Board: (a) **Identidad Progresiva** — 7 etiquetas de relación derivadas (Anónimo→Visitante→Usuario→Responsable de Empresa→Líder Activo→Cliente Activo→Embajador), no entidades, unificadas con un modelo de confianza vía hitos de evidencia (reutiliza el Patrón B de AD-CMP-01, sin mecanismo de avance nuevo). Se detectaron y corrigieron dos colisiones de nombre antes de fijar la escalera: "Founder" (colisionaba con la razón exacta por la que AD-006 ya lo había renombrado a "Usuario Principal") y "CEO" (colisionaba con el CEO Agent ya definido en AD-FUNC-02) — reemplazados por "Responsable de Empresa" y "Líder Activo" respectivamente. (b) **Onboarding conversacional, independiente del canal** (voz, texto, documento, audio, video, imagen) — reutiliza Documento y Conversación ya existentes, y a ARQAI como Motor del Ecosistema si se necesita voz, sin construir nada nuevo. (c) **Recuperación de Onboarding** — retomar siempre desde el último paso real completado, nunca reiniciar, aplicación directa de AD-002 §1.5 y la Regla de no repetición de AD-CMP-04. (d) **Objetivo de tiempo máximo** (<30 segundos entre registro y primera pregunta real) como meta operativa medible de ADÁN, distinta del Indicador de negocio que AD-005 define para la Empresa cliente. Riesgo señalado explícitamente: el mecanismo concreto detrás de la etiqueta "Embajador" debe evitar el patrón de esquema multinivel ya identificado como riesgo de negocio para ADÁN, y queda fuera de esta especificación de producto (WO-100).

---

## 1. Estado de aprobación

| Categoría | Estado |
|---|---|
| Fundamentos (9) + Comportamientos (6) | Completa, aprobada |
| Funcionalidades (9) | AD-FUNC-01 ✅ · AD-FUNC-02 ✅ · AD-FUNC-03 ✅ · AD-FUNC-04 construido y autoauditado · **AD-FUNC-05 ✅ APPROVED FOR GATE REVIEW** · AD-FUNC-06 construido y autoauditado (Revisión 2) · 3 pendientes |

---

## 2. Nota de cierre

21 documentos con contenido real. El próximo, según el árbol original, es AD-FUNC-07 — Sistema de Scoring.
