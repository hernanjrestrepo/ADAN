---
Tipo: Documento interno de consolidación — NO es un AD-XXX, NO es una nueva Work Order
Propósito: dar a cualquier desarrollador, arquitecto o inversionista que entra al proyecto una lectura única que reemplace cientos de páginas
Fecha: 2026-07-14
Cubre: Fase 1 (Fundamentos) de la WO-000, completa — AD-000 a AD-007, Anexo de Meta-Principios, y los tres workshops del Ciclo Dominio
---

# WO-000 — Executive Architecture Summary

## Cómo leer este documento

Este documento **resume; no reemplaza.** En caso de cualquier conflicto entre lo que dice aquí y lo que dice un documento AD-XXX congelado, **el AD-XXX prevalece siempre.** Este resumen no es una fuente de verdad — es un mapa de lectura rápida hacia las fuentes de verdad, que son los ocho documentos AD-000 a AD-007, el Anexo de Meta-Principios de Ingeniería, y los tres workshops del Ciclo Dominio. Por eso no está sujeto a la Regla de No Duplicación de la misma forma que el resto de la WO-000: su función explícita es duplicar en forma resumida lo que ya existe en forma completa, para que nadie tenga que leer 8 documentos y un anexo para entender la arquitectura.

---

## 1. Qué es ADÁN, en un párrafo

ADÁN es la inteligencia orquestadora del Ecosistema Paradixe aplicada a una empresa específica: acompaña a esa empresa desde una idea sin validar hasta una organización madura, tomando y documentando cada decisión sobre evidencia, nunca sobre supuestos. No es un chatbot ni un generador de MVPs — es un Sistema Operativo Empresarial para cualquier etapa del ciclo de vida de una organización. Su misión formal: **"Diseñar, validar, construir, operar, transformar y escalar empresas extraordinarias, mediante inteligencia artificial y conocimiento colectivo."** Su propósito último: aumentar la probabilidad de que las buenas ideas se conviertan en grandes empresas, independientemente del capital, la experiencia previa o la red de contactos de sus fundadores.

---

## 2. Qué se construyó en Fase 1 — quince documentos, un anexo, tres workshops

**Nota de esta revisión:** una versión anterior de este resumen llamaba "Fase 1" solo a los primeros ocho documentos (Fundamentos). El Gate Review de Fase 1 (`WO-000_GATE_REVIEW_FASE1.md`) encontró que la definición original del árbol (v3, línea 190) incluye también Comportamientos — 15 documentos, no 8. Esta sección queda corregida.

| # | Documento | Responde | Estado |
|---|---|---|---|
| 1 | AD-000 — Paradixe Ecosystem Vision | ¿Qué ecosistema rodea a ADÁN y qué lugar ocupa en él? | Aprobado y congelado, v1.0 |
| 2 | AD-001 — Product DNA | ¿Quién es ADÁN, permanentemente? | Aprobado y congelado, v1.0 |
| 3 | AD-002 — Principios del Sistema | ¿Qué debe garantizar el sistema, siempre? | Aprobado y congelado, v2.0 |
| 4 | AD-003 — Product Language | ¿Qué significa cada término oficial? | Aprobado y congelado, v1.0 |
| 5 | AD-004 — Product Evolution | ¿Cómo puede cambiar ADÁN sin perder su identidad? | Aprobado y congelado, v1.0 |
| — | Anexo — Meta-Principios de Ingeniería | ¿Cómo se toman las decisiones de construcción? | Aprobado y congelado, v2.0 |
| — | Ciclo Dominio (3 workshops) | ¿Qué es una empresa, cómo se relacionan sus partes, cómo evoluciona? | Aprobado como base, no congelados formalmente |
| 6 | AD-005 — Enterprise Domain Model | ¿Cómo está constituida una organización? | Aprobado y congelado, v1.0 |
| 7 | AD-006 — Domain Model (Software) | ¿Cómo representa ADÁN esa organización en software? | Aprobado y congelado, v1.1 |
| 8 | AD-007 — Gemelo Digital | ¿Qué unifica el mundo de la empresa con el mundo de ADÁN? | Aprobado y congelado, v1.1 |
| 9 | AD-008 — Objetos del Sistema | ¿Qué estados, acciones y permisos tiene cada entidad? | Aprobado y congelado, v1.0 |
| 10 | AD-CMP-01 — Progresión entre Niveles | ¿Cómo avanza un Nivel? | Aprobado y congelado, v1.0 |
| 11 | AD-CMP-02 — Consenso Multiagente | ¿Cómo producen los Agentes una sola respuesta? | Aprobado y congelado, v1.0 |
| 12 | AD-CMP-03 — Comportamiento de Decisiones | ¿Cómo se aprueba una Decisión? | Aprobado y congelado, v1.0 |
| 13 | AD-CMP-04 — Memoria y Contexto | ¿Qué recuerda ADÁN y qué olvida? | Aprobado y congelado, v1.0 |
| 14 | AD-CMP-05 — Evidencia y Scoring | ¿Cómo se convierte una conversación en un Score? | Aprobado y congelado, v1.0 |
| 15 | AD-CMP-06 — Digital Twin Lifecycle | ¿Cómo nace, crece, se fusiona y se archiva un Gemelo Digital? | Aprobado y congelado, v1.0 |
| 8 | AD-007 — Gemelo Digital | ¿Qué unifica el mundo de la empresa con el mundo de ADÁN? | Construido y autoauditado, v1.0 |

**15 de 58 documentos del árbol oficial (25,9%). Fase 1 (Fundamentos + Comportamientos) completa, verificada por Gate Review. AD-FUNC (Funcionalidades) es la siguiente categoría.**

---

## 3. Los principios que gobiernan todo el sistema

### 3.1 Los seis principios inviolables de ADÁN (AD-001 §12)

1. Ninguna decisión avanza sin evidencia.
2. Ninguna decisión importante avanza sin aprobación explícita del cliente.
3. Ninguna recomendación se presenta sin su razonamiento disponible si se solicita.
4. Ninguna empresa pierde su historial — el Gemelo Digital es permanente.
5. ADÁN nunca actúa fuera de los límites de ecosistema (AD-000) ni de categoría (AD-001 §1.1).
6. ADÁN reconoce los límites de su conocimiento — Principio de Humildad Intelectual.

### 3.2 Las ocho cosas que ADÁN nunca intentará ser (AD-001 §1.1)

ERP · CRM de propósito general · sistema contable · IDE o reemplazo de desarrolladores · herramienta primaria de diseño gráfico · motor de búsqueda de propósito general · red social · plataforma de pagos genérica. Cada una tiene dueño en el ecosistema — no en ADÁN.

### 3.3 Las diez reglas de sistema (AD-002 v2.0)

Todo genera evidencia · todo es trazable · todo es reversible · toda decisión tiene responsable · nada se pierde · toda IA debe justificar · todo tiene versión · todo genera memoria · todo tiene un nivel de confianza declarado · **Economía Conceptual** (ningún concepto nuevo se incorpora sin demostrar que resuelve un problema real, que no puede expresarse con lo existente, y que su valor supera su complejidad).

### 3.4 Los diez Meta-Principios de Ingeniería (Anexo v2.0)

1. El dominio prevalece sobre la tecnología.
2. **Principio de Emergencia** — ninguna capacidad que ya emerja de combinar reglas existentes se convierte en concepto, entidad o documento nuevo. *(Precede a Economía Conceptual, no la sigue — es la pregunta que se hace primero.)*
3. La evidencia prevalece sobre la opinión.
4. La simplicidad prevalece sobre la sofisticación innecesaria.
5. La experiencia del usuario prevalece sobre la comodidad de implementación.
6. Toda decisión debe minimizar la complejidad futura.
7. Ninguna limitación temporal de una tecnología debe modificar el modelo conceptual del producto.
8. La deuda conceptual es tan importante como la deuda técnica.
9. Las decisiones irreversibles requieren mayor evidencia que las reversibles.
10. La arquitectura debe poder evolucionar sin romper el dominio.

### 3.5 Disciplina editorial (vigente en toda la WO-000 desde v3.1-v3.4)

Regla de No Duplicación · Estructura de cierre obligatoria (Dependencias, Documentos relacionados, Impacto, Riesgos, Preguntas abiertas, Decisiones pendientes, Historial de cambios) · Confidence Level 0-100% con justificación, nunca un número arbitrario · Prueba de Reconstrucción (¿un equipo distinto podría reconstruir el sistema leyendo solo estos documentos?) · distinción Principio Permanente / Decisión de Diseño · disciplina de versionado (un documento aprobado se congela; toda mejora crea v1.1 o v2.0, nunca se edita en el sitio) · autoauditoría obligatoria de 10 preguntas antes de entregar cualquier documento nuevo · metodología de cierre de Fase 1: **construye → autoaudita → congela → continúa.**

---

## 4. El vocabulario oficial (AD-003) — los términos que nunca deben reinterpretarse

| Término | Significado fijado |
|---|---|
| Ecosistema Paradixe | Red de componentes de IA (EVA, ARQAI, ATO, Genexis, CSI, Marketplace, Paradixe Capital, Token del Ecosistema, Enterprise Intelligence) que cubren cualquier etapa del ciclo de vida de una empresa |
| ADÁN | Nombre propio, la inteligencia orquestadora — nunca "la IA", "el bot" o "el asistente" |
| Orquestador | El rol de ADÁN dentro del ecosistema: decide qué activar, en qué orden, con qué motor |
| Gemelo Digital | El límite de agregación permanente que une a una Empresa con su Proyecto — no una entidad de datos por separado |
| Empresa / Proyecto | Empresa = el sujeto real de negocio (AD-005). Proyecto = el contenedor de software de ADÁN (AD-006). Nunca sinónimos |
| Decisión / Decisión de Negocio / Elección de Diseño | Tres conceptos distintos que comparten raíz: el objeto interno de ADÁN, la decisión real de la empresa cliente, y la categoría de contenido de esta misma WO-000 |
| Confidence Level | Indicador 0-100% de cuánto de un contenido está respaldado por evidencia — aplica tanto a los documentos de la WO-000 como, más adelante, a las salidas del propio producto |
| Principio Permanente / Decisión de Diseño | Distinción entre lo que debe seguir siendo cierto en veinte años y lo que puede evolucionar sin romper ese principio |

*(21 términos totales en AD-003, 16 de producto y 5 de proceso documental — ver el documento original para el tratamiento completo de cada uno, con sus 10 campos de definición.)*

---

## 5. El dominio empresarial — qué existe en una empresa (AD-005)

**De 172 conceptos candidatos (enumerados en el Enterprise Taxonomy Workshop), 26 se convirtieron en entidades núcleo.** La reducción es la decisión más importante de todo el Ciclo Dominio.

### 5.1 Las 26 entidades, por cluster

- **Identidad y Gobernanza (4):** Empresa (raíz), Narrativa Fundacional, Marca, Accionista/Inversionista.
- **Estructura y Personas (4):** Departamento, Cargo, Rol Funcional, Empleado.
- **Mercado y Comercial (5):** Cliente Final, Producto/Servicio, Mercado, Competidor, Proveedor.
- **Operación (5):** Proceso, Iniciativa, Suceso Empresarial, Contrato, Documento.
- **Dirección y Evidencia (4):** Objetivo, Meta, Indicador, Decisión de Negocio.
- **Finanzas (4):** Activo, Pasivo, Ingreso, Gasto.

### 5.2 Lo que deliberadamente NO es entidad

- **Riesgo** e **Intangible** (reputación, confianza, marca, cultura, capital intelectual...) — propiedades transversales, se predican de varias entidades, nunca son entidades por sí mismas.
- **Edad, Madurez Organizacional, Velocidad de Maduración (derivada), Etapa del Ciclo de Vida (derivada)** — dimensiones de identidad de la Empresa, no entidades separadas. La Velocidad (Δ Madurez / Δ Tiempo) es, en particular, calculable gratis sobre el historial de versiones que AD-002 ya exige — no requiere modelar nada adicional.
- Extensiones específicas de industria (SKU, Patente, Cap Table, Ronda de Inversión...) — quedan fuera del núcleo por no ser universales; candidatas a un futuro mecanismo de extensión.

### 5.3 Las diez Leyes Dinámicas (Workshop de Comportamientos)

Origen · Aprendizaje (bucle simple vs. doble) · Adaptación · Crecimiento y Cambio Estructural (crisis predecibles de Greiner) · Estancamiento (divergencia Edad-Madurez) · Crisis (Riesgo supera capacidad de absorción) · Recuperación (explicada por Intangibles, no por Activos) · Muerte (se detiene el aprendizaje, nunca se borra el Gemelo Digital) · Reinvención (cambio de Narrativa Fundacional por aprendizaje de bucle doble) · Ciclo, no Línea (las nueve anteriores no son secuenciales). Ancladas en Adizes, Greiner, Argyris & Schön, Holling y teoría de sistemas adaptativos complejos — ninguna requirió inventar un concepto nuevo.

---

## 6. El dominio operativo — cómo se representa ADÁN a sí mismo (AD-006)

**12 entidades adicionales**, que nunca fueron responsabilidad de AD-005 porque pertenecen al mundo de ADÁN, no al mundo de la empresa modelada: Usuario, Usuario Principal (renombrado de "Fundador" — ya no aplicaba desde que la misión se amplió más allá de startups), Proyecto, Workspace, Nivel, Card, Conversación, Agente, Tarea, Decisión (de ADÁN), Score, Evento (técnico).

**Contrato Base** — siete atributos que heredan las 38 entidades (26 + 12) sin repetirse: identificador único, historial de versiones, estado (activo/archivado, nunca eliminado), responsable del último cambio, evidencia asociada, nivel de confianza declarado, razonamiento disponible bajo solicitud. Es la primera implementación a nivel de software de las diez reglas de AD-002.

**AD-005 y AD-006 modelan dos universos distintos, no el mismo universo con dos nombres:**

```
DOMINIO EMPRESARIAL (AD-005, 26)      DOMINIO OPERATIVO DE ADÁN (AD-006, 12)
Empresa, Cliente Final, Mercado,       Usuario, Proyecto, Workspace, Nivel,
Proceso, Riesgo, Decisión de           Card, Conversación, Agente, Tarea,
Negocio...                             Decisión, Score, Evento...
              └───────────┬───────────┘
                 AD-007 — Gemelo Digital
```

---

## 7. El Gemelo Digital — el puente (AD-007)

No es una tercera entidad de datos. Es el **límite de agregación 1:1:1** que declara que una Empresa (AD-005) y su Proyecto correspondiente (AD-006) son, para efectos de referencia externa y persistencia, una sola identidad. Pasó explícitamente la prueba del Principio de Emergencia antes de admitirse: el vacío real que resuelve no es de datos —esos ya existían en AD-005 y AD-006— sino de **frontera**: es la única entidad diseñada para que el resto del Ecosistema Paradixe (EVA, ATO, Genexis, CSI) la consulte, sin necesidad de conocer la distinción interna entre Empresa y Proyecto. Su comportamiento en el tiempo (nace, crece, se fusiona, se archiva) no vive aquí — vive en AD-CMP-06, todavía no escrito.

---

## 8. Mapa de dependencias entre documentos

```
AD-000 (raíz)
  └─ AD-001
       └─ AD-002 ── Anexo MPI
            └─ AD-003
                 └─ AD-004
                      └─ [Ciclo Dominio: Taxonomía → Relaciones → Comportamientos]
                           └─ AD-005
                                └─ AD-006 (+ AD-003 para las 5 entidades ya forward-referenciadas)
                                     └─ AD-007 (agrega AD-005 + AD-006 + AD-000 + AD-001)
```

Cada flecha es una dependencia real, registrada en el Knowledge Graph (`docs/wo-000/knowledge-graph/kg.json`) junto con cada concepto, cada uno de los 26 principios/reglas, y cada relación entre entidades — la fuente consultable mecánicamente, no solo narrativa, de todo este mapa.

---

## 9. Registro consolidado de decisiones congeladas

| # | Decisión | Documento |
|---|---|---|
| 1 | Modelo de red/orquestación del ecosistema, no cadena lineal | AD-000 |
| 2 | Misión ampliada a las 6 etapas del ciclo de vida empresarial, no solo "crear" | AD-001 |
| 3 | 6 principios inviolables + 8 categorías excluidas + Humildad Intelectual | AD-001 |
| 4 | 10 reglas de sistema, incluida Economía Conceptual | AD-002 |
| 5 | 21 términos de lenguaje controlado; 5 colisiones de nombre resueltas caso por caso | AD-003 |
| 6 | Reglas de nacimiento/graduación de Funcionalidades; control de crecimiento del dominio | AD-004 |
| 7 | 10 Meta-Principios, Emergencia en posición 2 | Anexo v2.0 |
| 8 | 172 → 26 entidades de negocio; Riesgo e Intangible transversales; Edad/Madurez/Velocidad/Etapa derivadas; 10 Leyes Dinámicas | AD-005 |
| 9 | 12 entidades operativas de ADÁN; Contrato Base; "Fundador" → "Usuario Principal" | AD-006 |
| 10 | Gemelo Digital como límite de agregación, no entidad nueva | AD-007 |

### Decisiones deliberadamente NO congeladas — pendientes, con dueño claro

- Nombre definitivo de **Paradixe Capital** (vs. "Ventures") — pendiente del Board, incluye validación de marca.
- Nombre definitivo del **Token del Ecosistema** (nunca "Applecoin", riesgo legal) — pendiente del Board.
- Número real de **Niveles**: 6 vs. 7 — pendiente de AD-FUNC-01, ahora resoluble contra la entidad `Nivel` ya formalizada.
- Resolución de **ARQAI vs. ATO** como productos distintos — ya resuelta por el Board en AD-000, pendiente de reflejarse en un futuro AD-INT-05.
- **"Artefacto"** (posible salida no-documental de Genexis) — diferido a AD-007/Integraciones hasta que exista un caso real.

---

## 10. Qué sigue — AD-FUNC (Funcionalidades)

Fase 1 (Fundamentos + Comportamientos, 15 documentos) está completa y verificada por Gate Review — ver `WO-000_GATE_REVIEW_FASE1.md`. Empieza ahora la categoría Funcionalidades (AD-FUNC-01 a 09), que traduce el modelo ya congelado en capacidades concretas del producto — sin poder introducir una sola entidad de dominio que no exista ya en AD-005, AD-006, AD-007 u AD-008 (Regla de Entidades, v3.1 §1, sin cambios desde el origen del árbol). El primer documento es **AD-FUNC-01 — Los 7 Niveles**, que ahora sí puede escribirse cumpliendo, y no violando, sus dependencias declaradas contra AD-CMP-01 (Progresión) y AD-CMP-05 (Evidencia y Scoring), ambos ya congelados.
