# WO-000 — Índice Maestro de Especificación de Producto ADÁN (v3.20)

**Tipo de documento:** Árbol documental — **APROBADO Y CONGELADO** (sin cambios de estructura desde v3.1).
**Estado de la WO-000:** Fase 1 completa. Funcionalidades: AD-FUNC-01 a 03 aprobados; AD-FUNC-04 construido y autoauditado; **AD-FUNC-05 Ready for Gate Review**; AD-FUNC-06 construido y autoauditado.

---

## 0. Qué cambió respecto a v3.19

1. **AD-FUNC-05 — Corrección Editorial Final, marcado Ready for Gate Review.** Se ejecutó una Architectural Consistency Review completa (checklist de 8 puntos: consistencia documental contra los 20 documentos ya congelados, dependencias, Principios Permanentes, Decisiones de Diseño, riesgos arquitectónicos, Economía Conceptual, test de los 10 años). Resultado: 0 hallazgos Críticos, 2 Altos, 2 Medios — todos corregidos editorialmente sin reabrir el modelo conceptual: (1) corregido un conteo interno ("15 tipos" → "16 tipos" de Estrategia); (2) restaurada la unidireccionalidad documental con AD-003 v1.1 (la referencia a AD-FUNC-05 se movió de "Dependencias" a "Documentos relacionados"); (3) Estrategias Compuestas, Horizonte Temporal y Playbook Empresarial quedaron clasificados explícitamente como Decisión de Diseño; (4) se separó el invariante permanente del flujo de razonamiento de su implementación actual de 11 pasos, dejando la taxonomía específica como evolucionable. AD-FUNC-05 queda cerrado y disponible como dependencia estable para el resto del árbol.
2. **AD-FUNC-06 — Onboarding, construido.** Cubre el tramo desde el registro hasta la primera pregunta real de ADÁN en Nivel 1 — no es un Nivel 0, Los 7 Niveles no se reabren. Principio rector: Onboarding no es un formulario, es la primera pregunta real llegando lo antes posible — un formulario de perfil completo antes de cualquier conversación produciría la anti-emoción "Juzgado" que AD-FUNC-03 ya prohibió para Nivel 1. Captura mínima antes de la primera pregunta (nombre, contacto, señal mínima de que existe o se busca crear una Empresa); todo lo demás (estructura organizacional, finanzas, razón social) se difiere. Creación progresiva de Usuario, Usuario Principal, Proyecto, Workspace y Empresa basada en evidencia real —ninguna entidad nueva, todas ya existentes en AD-005/AD-006. Emoción (Comprendido) y ritmo (Inmediato) heredados de AD-FUNC-03/04 sin duplicarse. Colisión de nombre menor con "Onboarding" de Empleado (Enterprise Taxonomy Workshop) documentada explícitamente, sin bloquear el documento.

---

## 1. Estado de aprobación

| Categoría | Estado |
|---|---|
| Fundamentos (9) + Comportamientos (6) | Completa, aprobada |
| Funcionalidades (9) | AD-FUNC-01 ✅ · AD-FUNC-02 ✅ · AD-FUNC-03 ✅ · AD-FUNC-04 construido y autoauditado · AD-FUNC-05 Ready for Gate Review · AD-FUNC-06 construido y autoauditado · 3 pendientes |

---

## 2. Nota de cierre

21 documentos con contenido real. El próximo, según el árbol original, es AD-FUNC-07 — Sistema de Scoring.
