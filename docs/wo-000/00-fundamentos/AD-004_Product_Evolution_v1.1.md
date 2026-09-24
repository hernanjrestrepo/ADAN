---
Código: AD-004
Nombre: Product Evolution
Versión: v1.1 — APROBADA Y CONGELADA
Estado: Aprobado y congelado
Confidence Level: 68%
Fecha de aprobación: 2026-07-14
Responsable (autor del borrador): CC (Claude Code)
Aprobador: Hernán / Junta Directiva
Supersede a: AD-004_Product_Evolution_v1.0.md
---

# AD-004 — Product Evolution — v1.1

> Este documento no es un roadmap. Responde una sola pregunta: **¿cómo puede evolucionar ADÁN durante los próximos veinticinco años sin perder la identidad que AD-001 y AD-002 ya fijaron como inviolable?** Todo lo que sigue son reglas de cambio, no un plan de cambios.

**Nivel de contenido:** mixto. Las reglas son Principio Permanente. Los umbrales numéricos de ejemplo son Decisión de Diseño.

---

## Respuesta directa a la pregunta central

ADÁN evoluciona **añadiendo alcance dentro de los límites que ya son inviolables, nunca renegociando esos límites**. Todo lo declarado en AD-001 §12, en AD-001 §1.1, en las diez reglas de AD-002, y en los diez Meta-Principios de Ingeniería, permanece fijo durante los veinticinco años de esta visión.

---

## 1. Qué puede cambiar

- El modelo de negocio, precios y monetización (reservado en WO-100).
- El número exacto y el orden de los Niveles, siempre que AD-CMP-01 se mantenga.
- Los motores de construcción, modelos de IA y proveedores técnicos.
- Las mecánicas específicas de Experience Engine y Gamification Engine.
- Las métricas específicas instrumentadas para medir éxito.
- La interfaz de usuario en su totalidad.
- Los componentes del Ecosistema Paradixe listados en AD-000 §3.

## 2. Qué nunca podrá cambiar

- Los seis principios inviolables de AD-001 §12.
- Las ocho categorías que ADÁN jamás intentará convertirse, AD-001 §1.1.
- Las diez reglas de sistema de AD-002 v2.0.
- Los diez Meta-Principios de Ingeniería del Anexo v2.0.
- La Declaración de Misión de AD-001 — puede *ampliarse*, nunca *reducirse*.

## 3. Cómo nace una Funcionalidad

Ninguna Funcionalidad se incorpora al producto sin pasar por esta secuencia, en orden:

1. **Evidencia del problema.** Debe existir un problema real, demostrado con casos de uso concretos o solicitudes documentadas de clientes reales.
2. **Prueba de no-redundancia.** El problema no puede resolverse combinando Funcionalidades y Comportamientos ya existentes (Economía Conceptual, AD-002 §1.10) — y, antes de eso, debe verificarse si ya *emerge* de reglas existentes (Principio de Emergencia, Anexo v2.0 §2).
3. **Verificación contra AD-001 §1.1.** Debe explicitarse contra cuál de las ocho categorías excluidas podría estar rozando la propuesta.
4. **Criterio de existencia** *(nuevo en v1.1)* — ver sección 3.1, obligatorio y sin excepción.
5. **Checklist de Justificación de Diseño** (AD-002 §2).
6. **Registro como Decisión** — con Justificación, Alternativas evaluadas y Motivo de descarte.

Una Funcionalidad que no puede superar el paso 1 no nace. Una que no puede superar el paso 2 no es nueva — es una extensión de una existente. Una que no puede superar el paso 4 no nace tampoco, sin importar cuánta evidencia tenga de que "sería útil".

### 3.1 Criterio de existencia (nuevo)

**Ninguna Funcionalidad puede existir si no cumple, al menos, una de estas tres condiciones:**

- **Modifica el Gemelo Digital** — agrega, cambia o versiona algo en el historial permanente de una Empresa (AD-007).
- **Mejora el conocimiento del cliente** — el cliente sale de usarla sabiendo algo verificable que no sabía antes, no solo habiendo interactuado con una interfaz.
- **Produce evidencia útil para la siguiente decisión** — genera el insumo que AD-CMP-01 o AD-CMP-05 necesitan para permitir un avance de Nivel o respaldar una Decisión.

**Por qué se agrega:** las cinco condiciones anteriores (evidencia del problema, no-redundancia, límites de categoría, checklist, registro) verifican que una Funcionalidad esté *justificada*. Ninguna verifica que, una vez construida, *haga algo que importe* — una Funcionalidad podría pasar las cinco y aun así ser decorativa (bonita, popular, pero sin efecto real en el Gemelo Digital, el conocimiento del cliente, o la evidencia del sistema). Este criterio cierra ese hueco. Es, en efecto, la aplicación de AD-001 §9 (qué métricas realmente importan: calidad de decisión, no actividad) al nivel de si una Funcionalidad individual merece existir, no solo al nivel de qué medir después de que ya existe.

**Violación de ejemplo:** una animación de celebración que no registra ningún Evento, no cambia ningún Score, y no queda reflejada en el historial del Gemelo Digital — sería experiencia sin sustancia, exactamente lo que este criterio prohíbe. (Nota: esto no descalifica la gamificación en general — Gamification Engine, AD-FUNC-04, sí cumple el criterio en la medida en que sus mecánicas de progreso reflejan avance real ya registrado, AD-001 §14. Descalifica específicamente la gamificación que no refleja nada real.)

## 4. Cuándo una Funcionalidad se convierte en un producto independiente

Cuando se cumplen, a la vez: (a) su valor es útil fuera del contexto de ADÁN, (b) tiene un ciclo de vida de usuario propio, (c) extraerla reduce la complejidad interna sin reducir el valor ofrecido. Requiere, por el Meta-Principio 8 (ahora reordenado), un nivel de evidencia superior al de una Decisión ordinaria.

## 5. Cuándo un producto pasa a formar parte del ecosistema

No le corresponde a AD-004 — le corresponde a la futura Constitución de Paradixe (AD-000 §7). AD-004 solo fija las condiciones que ADÁN exige de cualquier nuevo par: No Duplicación de Capacidad y Contrato Explícito (AD-000 §4).

## 6. Cómo se controla el crecimiento del dominio

La Regla de Entidades (v3.1 §1) — solo AD-005, AD-006, AD-007, AD-008 pueden introducir una entidad nueva. Economía Conceptual y Principio de Emergencia, aplicados antes de eso. Autoauditoría obligatoria declarando qué conceptos introduce cada documento nuevo.

## 7. Cómo se evita el feature creep

AD-001 §1.1 + la secuencia de nacimiento de la sección 3, ahora con el Criterio de Existencia de la sección 3.1 como filtro adicional. Toda propuesta que no complete la secuencia en un plazo razonable se rechaza formalmente, registrada como Decisión descartada.

## 8. Cómo se preserva la coherencia del ecosistema a largo plazo

Product Language + Knowledge Graph evitan fragmentación de vocabulario. Los Comportamientos (AD-CMP) fijan reglas de dominio independientes de la implementación. Revisión Periódica de Coherencia cada diez documentos nuevos aprobados.

---

## Dependencias

- AD-001 Product DNA
- AD-003 Product Language
- AD-002 Principios del Sistema v2.0
- WO-000-ANEXO-MPI Meta-Principios de Ingeniería v2.0
- AD-007 Gemelo Digital v1.1 *(dependencia nueva en v1.1 — el Criterio de Existencia de §3.1 referencia directamente lo que el Gemelo Digital agrega)*

## Documentos relacionados

- Toda la categoría Funcionalidades (AD-FUNC) — el Criterio de Existencia de §3.1 aplica, sin excepción, a los 9 documentos AD-FUNC-01 a 09, empezando por AD-FUNC-01
- AD-000 §7, El Knowledge Graph de la WO-000

## Impacto sobre otros módulos

1. Toda propuesta futura de Funcionalidad queda sujeta al Criterio de Existencia de §3.1 — no es opcional.
2. AD-FUNC-01, primer documento evaluado bajo este criterio, debe poder mostrar explícitamente qué modifica en el Gemelo Digital en cada uno de sus Niveles.

## Riesgos

- Riesgo de que "veinticinco años sin perder identidad" bloquee evolución legítima — mitigado porque la sección 1 es deliberadamente amplia.
- Riesgo de que la Revisión Periódica de Coherencia (sección 8) nunca tenga responsable operativo asignado.
- Riesgo de sub-especificación de la sección 5, hasta que exista la Constitución de Paradixe.

## Preguntas abiertas

Ninguna nueva.

## Decisiones pendientes

- Asignar responsable operativo de la Revisión Periódica de Coherencia (sección 8).

## Historial de cambios

| Versión | Fecha | Cambio | Motivo |
|---|---|---|---|
| v1.0 | 2026-07-14 | Creación inicial (ver historial completo en AD-004_Product_Evolution_v1.0.md) | Quinto documento de la WO-000 |
| v1.0 — Aprobada | 2026-07-14 | Aprobación formal, congelada | Cierre del ciclo de revisión |
| v1.1 | 2026-07-14 | Se agrega el Criterio de Existencia (§3.1) como sexto paso de la secuencia de nacimiento de Funcionalidades: ninguna existe si no modifica el Gemelo Digital, mejora el conocimiento del cliente, o produce evidencia útil | Instrucción directa del Board al iniciar AD-FUNC, para evitar funcionalidades decorativas o aisladas |
