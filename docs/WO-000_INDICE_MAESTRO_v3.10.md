# WO-000 — Índice Maestro de Especificación de Producto ADÁN (v3.10)

**Tipo de documento:** Árbol documental — **APROBADO Y CONGELADO** (sin cambios de estructura desde v3.1).
**Estado de la WO-000:** AD-000 a AD-006 completos. AD-007 (Gemelo Digital) es el siguiente y último documento de Fundamentos.
**Supersede a:** `WO-000_INDICE_MAESTRO_v3.9.md`.
**Naturaleza de este cambio:** avance de contenido bajo la nueva metodología de construcción.

---

## 0. Qué cambió respecto a v3.9

**AD-006 — Domain Model (Software), construido y congelado.** Segundo documento bajo "se construye, se autoaudita, se congela, se continúa". Contiene un hallazgo de alcance señalado explícitamente en su sección 0, no resuelto en silencio: la instrucción de que "AD-006 no crea entidades nuevas" aplica a la traducción del dominio de negocio (26 de AD-005, cero adicionales) — pero AD-006 también tenía, desde el índice v3.1 original, mandato propio de definir 12 entidades operativas de ADÁN (Proyecto, Usuario, Nivel, Card, Agente, Workspace, Conversación, Tarea, Decisión, Score, Evento, y un "Fundador" renombrado a "Usuario Principal" por quedar desalineado con la Declaración de Misión ampliada de AD-001). Esas 12 nunca fueron responsabilidad de AD-005, que se limitó por diseño a modelar la empresa del cliente, no a ADÁN mismo.

---

## 1. Estado de aprobación

| Código | Documento | Estado | Versión vigente |
|---|---|---|---|
| AD-000 a AD-004 | Núcleo filosófico | **Aprobados y congelados** | v1.0 / v2.0 |
| ANEXO-MPI | Meta-Principios de Ingeniería | **Aprobado y congelado** | v2.0 |
| **AD-005** | **Enterprise Domain Model** | **Construido y autoauditado — congelado** | v1.0 |
| **AD-006** | **Domain Model (Software)** | **Construido y autoauditado — congelado** | v1.0 |
| AD-007 | Gemelo Digital | No iniciado — siguiente paso | — |

**38 entidades totales fijadas hasta ahora:** 26 de negocio (AD-005) + 12 operativas de ADÁN (AD-006).

---

## 2. Nota de cierre

AD-006 cierra la traducción completa del mundo empresarial al software de ADÁN. AD-007 — Gemelo Digital es el último documento de Fase 1 (Fundamentos): especifica cómo una instancia de Empresa, junto con sus 25 entidades de negocio relacionadas y el historial de Proyecto/Nivel/Card/Decisión/Score que la acompaña, se versiona como una sola entidad viva a lo largo del tiempo — la pieza que, según ya lo señaló AD-005, "es el corazón del dominio".
