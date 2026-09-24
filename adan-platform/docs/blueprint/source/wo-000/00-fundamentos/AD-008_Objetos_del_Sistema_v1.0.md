---
Código: AD-008
Nombre: Objetos del Sistema
Versión: v1.0
Estado: Construido y autoauditado. Congelado por Claude Code bajo la metodología "se construye, se autoaudita, se congela, se continúa"
Confidence Level: 60%
Fecha: 2026-07-14
Responsable (autor): CC (Claude Code)
Aprobador: Hernán / Junta Directiva (validación en el próximo Gate Review)
---

# AD-008 — Objetos del Sistema

> AD-006 definió qué entidades existen y el Contrato Base que todas heredan (identificador, versión, estado activo/archivado, responsable, evidencia, confianza, razonamiento). Este documento profundiza lo que el Contrato Base deja genérico: **qué estados específicos atraviesa cada entidad, qué acciones son posibles sobre ella, quién puede ejecutarlas, y qué eventos dispara.** Sigue siendo conceptual — ningún motor técnico, ninguna tabla de base de datos.

**Nivel de contenido:** los cuatro patrones (sección 2) y el modelo de permisos (sección 3) son Principio Permanente. La asignación de cada una de las 38 entidades a un patrón es Decisión de Diseño.

---

## 1. Por qué cuatro patrones y no 38 máquinas de estado

Antes de diseñar nada, se aplicó el Principio de Emergencia (Anexo v2.0 §2) y Economía Conceptual (AD-002 §1.10) a la pregunta obvia: ¿necesita cada una de las 38 entidades su propia máquina de estados custom? La respuesta, verificada entidad por entidad, es no — la inmensa mayoría cae en uno de cuatro patrones repetidos. Diseñar 38 máquinas de estado sería la definición exacta de sofisticación innecesaria (Meta-Principio 4 del Anexo). Diseñar cero sería dejar sin resolver exactamente lo que AD-006 dejó pendiente. Cuatro patrones es el punto donde el valor supera la complejidad.

## 2. Los Cuatro Patrones de Estado

### Patrón A — Ciclo de Aprobación
`Propuesto → Aprobado / Rechazado → Ejecutado`

Aplica a entidades donde una parte (frecuentemente un Agente) propone algo que otra parte (frecuentemente el Usuario Principal) debe aprobar antes de que tenga efecto — la traducción operativa directa del principio inviolable de AD-001 §12 ("ninguna decisión importante avanza sin aprobación explícita del cliente").

**Entidades:** Decisión (de ADÁN), Decisión de Negocio, Iniciativa, Contrato (de negocio).

### Patrón B — Progreso Secuencial
`Bloqueado → Activo → Completado`

Aplica a entidades cuyo avance está condicionado por evidencia previa, no por elección libre — la traducción operativa de AD-CMP-01 (Comportamiento de Progresión).

**Entidades:** Nivel, Card, Tarea.

### Patrón C — Registro Permanente
`Registrado` *(estado único — nunca cambia; una corrección genera un registro nuevo, nunca edita el anterior)*

Aplica a entidades que representan un hecho ya ocurrido — cambiarlas retroactivamente violaría la Regla 1.5 de AD-002 (nada se pierde) y la Regla 1.2 (todo es trazable).

**Entidades:** Suceso Empresarial, Evento (técnico), Score (cada cálculo nuevo es una versión nueva, nunca una edición del anterior — coherente con la Velocidad de Maduración de AD-005 §4, que depende de que el historial de Score/Madurez nunca se reescriba).

### Patrón D — Contenedor Continuo
`Activo → Pausado → Archivado`

Aplica a entidades de larga duración que envuelven trabajo continuo, no un hecho puntual ni una aprobación puntual.

**Entidades:** Proyecto, Workspace, Empresa *(su estado de alto nivel es, en realidad, la Etapa del Ciclo de Vida derivada de AD-005 §4 — Activo/Pausado/Archivado es la envoltura operativa mínima que usa AD-006, no un reemplazo de esa Etapa)*.

### Entidades que no requieren patrón propio

El resto de las 38 entidades (Empresa exceptuada arriba, Departamento, Cargo, Rol Funcional, Empleado, Cliente Final, Producto/Servicio, Mercado, Competidor, Proveedor, Proceso, Documento, Objetivo, Meta, Indicador, Activo, Pasivo, Ingreso, Gasto, Narrativa Fundacional, Marca, Accionista/Inversionista, Usuario, Usuario Principal, Conversación, Agente) usan exclusivamente el Contrato Base de AD-006 (activo/archivado) — no necesitan un ciclo de vida más rico porque nada en su naturaleza de negocio ni operativa lo exige. Esto no es una omisión: es la aplicación explícita de Economía Conceptual a cada una, verificada, no asumida.

## 3. Modelo de Permisos

Cuatro actores posibles sobre cualquier acción:

| Actor | Puede |
|---|---|
| **Agente** | Proponer (Patrón A), generar Registros (Patrón C), avanzar internamente dentro de un Nivel/Card ya activo |
| **Usuario Principal** | Aprobar o rechazar cualquier transición del Patrón A que AD-001 §12 marque como "decisión importante"; pausar o archivar un Proyecto |
| **Usuario** (no Principal) | Consultar; proponer dentro del alcance que el Usuario Principal le delegue — el mecanismo exacto de delegación es Decisión de Diseño para AD-FUNC, no se resuelve aquí |
| **ADÁN (sistema)** | Ejecutar automáticamente una transición del Patrón B cuando la evidencia requerida ya está completa (AD-CMP-01) — nunca ejecuta automáticamente una transición del Patrón A, eso violaría el principio inviolable de aprobación explícita |

**Regla general, sin excepciones:** ningún Agente puede, por sí mismo, mover una entidad del Patrón A a "Ejecutado". Solo puede proponerla. Es la misma regla que AD-001 §5 y §12 ya declararon a nivel de identidad — aquí se vuelve verificable a nivel de permisos por entidad.

## 4. Regla de Eventos Sistemáticos

**Toda transición de estado de cualquier entidad de los Patrones A, B o D genera automáticamente un Evento (AD-006).** No es una entidad nueva ni una excepción — es la aplicación directa de la Regla 1.2 de AD-002 (todo es trazable) al nivel de cada objeto del sistema, y la razón concreta por la que AD-UX-08 (Timeline) tendrá contenido real que mostrar. El Patrón C no dispara este mecanismo porque sus entidades ya SON el registro — no tienen una transición que registrar además de sí mismas.

---

## Dependencias

- AD-006 Domain Model v1.1 (Contrato Base, las 38 entidades)
- AD-007 Gemelo Digital (el Patrón C es coherente con su exigencia de permanencia)
- AD-002 Principios del Sistema v2.0 (reglas 1.2, 1.5 implementadas aquí a nivel de objeto)

## Documentos relacionados

- AD-CMP-01 (usa el Patrón B para Nivel), AD-CMP-03 (usa el Patrón A para Decisión)
- AD-UX-08 Timeline (consume los Eventos que la sección 4 genera sistemáticamente)
- AD-ARQ-07 Eventos (implementación técnica del mecanismo de la sección 4)

## Impacto sobre otros módulos

1. Todo AD-CMP posterior debe declarar explícitamente qué Patrón usa para la entidad que gobierna, en vez de inventar un ciclo de vida propio.
2. AD-FUNC debe resolver el mecanismo de delegación Usuario Principal → Usuario mencionado en la sección 3, hoy señalado como Decisión de Diseño sin resolver.

## Riesgos

- **Riesgo de que cuatro patrones resulten insuficientes en la práctica** cuando una entidad concreta necesite un estado intermedio que ningún patrón cubre — mitigado porque agregar un quinto patrón, si se justifica con un caso real, es una extensión de bajo costo (nueva versión menor de este documento), no una reescritura.
- **Riesgo del mecanismo de delegación sin resolver** (sección 3) — puede bloquear a AD-FUNC si se necesita antes de lo previsto.

## Preguntas abiertas

Ninguna nueva — persisten las heredadas de Fundamentos.

## Decisiones pendientes

- Mecanismo exacto de delegación Usuario Principal → Usuario (sección 3).

## Historial de cambios

| Versión | Fecha | Cambio | Motivo |
|---|---|---|---|
| v1.0 | 2026-07-14 | Creación inicial: 4 patrones de estado cubriendo las 38 entidades, modelo de permisos de 4 actores, regla de eventos sistemáticos | Noveno documento de la WO-000 — primero de los siete pendientes identificados en el Gate Review de Fase 1 |
