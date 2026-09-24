# AD-DEC-0001 — Historia Oficial de ADÁN

**Fecha de redacción:** 2026-07-31
**Estado:** ✅ DECIDIDO — 2026-07-31, por Hernán (CTO ADÁN). Ver sección 5.
**Ubicación deliberada:** raíz física de `repos-active/adan/`, fuera de los árboles de Build A, B o C, para no sesgar el documento hacia ninguna de las tres líneas antes de que exista una decisión.
**Origen:** reconstrucción forense de una serie de auditorías de solo lectura sobre el historial de git, archivos sin versionar y memoria de proyecto. Ningún archivo de código fue modificado para producir este documento.

---

## 1. Resumen ejecutivo

Existen **tres construcciones de código distintas** que responden al nombre "ADÁN", más una fuente documental compartida que las precede a todas. No hay, en ningún lugar del repositorio ni de la documentación revisada, una declaración explícita de cuál de las tres es "la oficial". Este documento no la inventa — la deja pendiente en la sección 5.

```
                 Fuente documental compartida
                    docs/wo-000/* (WO-000_INDICE_MAESTRO)
                    Blueprint cerrado 2026-07-14
                              │
              ┌───────────────┴───────────────┐
              │                               │
              ▼                               ▼
        BUILD A                          BUILD C
   adan-platform/ (repo indep.)      "Vertical Nivel 1"
   2026-07-17 → 2026-07-18            2026-07-23 → 2026-07-24
              │
              │ integración demostrada
              ▼
        BUILD B
   rama adan/platform-integration
   2026-07-18 → 2026-07-20
   WO-000 → WO-012 · tag v1.0.0
```

---

## 2. Las tres líneas, en una tabla

| | **Build A** | **Build B** | **Build C** |
|---|---|---|---|
| Ubicación | `adan-platform/` (repo git independiente, anidado) | rama `adan/platform-integration` del monorepo | archivos sueltos, sin versionar, en la raíz de `repos-active/adan/` |
| Rango de fechas | 2026-07-17 18:53 → 2026-07-18 10:54 | 2026-07-18 11:14 → 2026-07-20 05:53 | 2026-07-23 → 2026-07-24 12:46 |
| Alcance (WO) | WO-000 → WO-003 | WO-000 → WO-012 (cadena cerrada, tag `v1.0.0`) | WO-001 propia, más módulos etiquetados WO-011 a WO-020 (numeración propia, no continúa la de B) |
| Base de datos | PostgreSQL 16 + pgvector | PostgreSQL 16 + pgvector (heredado de A) | SQLite |
| Frontend | React + Vite + TypeScript | React + Vite + TypeScript (heredado de A, ampliado) | React + Vite + **JavaScript (JSX)** |
| Puertos | 5436 / 6382 / 8020 (según registro de la migración) | 8020 / 5173 | 8050 / 5174 |
| Historial git propio | Sí, 25 commits, **sin remote** (solo local) | Sí, 51 commits, sincronizado con `origin` | Ninguno — cero commits en cualquier rama |
| Autoevaluación de calidad | No documentada | 58/100 (metodología propia, `CHAIN_CLOSURE.md`) | No documentada |
| Documento que la ancla | — | `CHAIN_CLOSURE.md` | `ADAN_MASTER_ARCHITECTURE_v1.0.md` (se autodeclara *"Single Source of Truth"*) |

---

## 3. Lo demostrado vs. lo no demostrado

### Demostrado (con evidencia verificable)

- **A → B es una migración real, no una coincidencia.** Commit `b5acfabd7` ("*integra plataforma ADÁN... al monorepo compartido*"), corroborado por un registro de memoria de proyecto escrito en tiempo real durante la migración, y por hash MD5 idéntico de `WO-000_INDICE_MAESTRO_v3.21.md` entre ambos árboles.
- **Build C reutiliza la misma fuente documental compartida** (`docs/wo-000/*`) que usaron A y B — MD5 idéntico verificado.
- **Build C no tiene ningún commit en ninguna rama del monorepo**, y su código/documentación **no contiene ninguna referencia textual** a Build B, a la rama `adan/platform-integration`, a `CHAIN_CLOSURE.md` ni a `v1.0.0`.

### No demostrado (y no lo estará solo con evidencia de archivos)

- **Si el autor de Build C conocía o no la existencia de Build B.** La ausencia de referencias textuales o de commits demuestra que no hubo *reutilización de código o documentos* de B — no demuestra que no hubiera *conocimiento humano* de B. Un desarrollador puede reescribir todo mirando otro sistema sin copiar una sola línea; eso el historial de archivos nunca podría probarlo ni descartarlo.
- **Por qué existen tres esquemas de puertos y dos motores de base de datos distintos**, sin que ningún documento lo explique como decisión relativa a lo anterior.
- **Quién creó Build C, con qué instrucción y con qué contexto disponible en ese momento.**

### La contradicción central (sin resolver)

`ADR-001-Vertical-Nivel-1.md`, fechado **2026-07-23**, afirma textualmente: *"ADÁN tiene un blueprint conceptual completo... pero cero código."* Build B había cerrado su cadena completa (51 commits, tag `v1.0.0`) **tres días antes**, el 2026-07-20. No existe ningún documento que explique este salto.

---

## 4. Hipótesis planteadas (ninguna confirmada — se listan, no se eligen)

1. Decisión consciente de reiniciar el proyecto con otra arquitectura.
2. Continuación por un agente o sesión sin visibilidad del estado de Build B.
3. Experimento paralelo, corrido con conocimiento pleno de Build B pero sin intención de integrarse con él (todavía).

Este documento **no elige entre estas tres** — no hay evidencia suficiente para hacerlo desde el repositorio.

---

## 5. Preguntas de gobierno — RESUELTAS

Estas cuatro preguntas eran decisiones de producto/negocio que ningún análisis de archivos podía responder. Decididas por Hernán (CTO ADÁN) el 2026-07-31.

**5.1 — ¿Cuál línea representa oficialmente a ADÁN hoy?**
✅ **Build C.**
Justificación registrada: no por superioridad técnica, sino porque es el desarrollo más reciente, es sobre el que se ha trabajado activamente en las últimas semanas, e incorpora la visión de producto vigente (Cerebro, EMS, TEF, Board, OOS, DKA, Voice). Criterio explícito: *"la oficialidad la determina la estrategia del producto, no la antigüedad del código."*

**5.2 — ¿Cuál queda archivada (preservada, pero no se continúa)?**
✅ **Build A** (`adan-platform/`). Se preserva únicamente por valor histórico. No recibe más desarrollo.

**5.3 — ¿Cuál queda como experimental (se puede seguir explorando, sin comprometerse a ella)?**
✅ **Build B** (rama `adan/platform-integration`). Pasa de "certificado" a "repositorio de referencia técnica" — conserva valor real (PostgreSQL, pgvector, arquitectura enterprise, implementaciones ya probadas) pero no compite con Build C ni recibe más desarrollo bajo ese rol.

**5.4 — ¿Cuál será la base técnica de "ADÁN Enterprise"?**
✅ **Build C, con una condición explícita: migrar su motor de datos de SQLite a PostgreSQL + pgvector**, conservando el resto de su arquitectura funcional tal como está. No se adopta SQLite como estándar; se adopta la arquitectura de Build C sobre el motor de datos ya validado en Build A/B.

Los valores concretos que se derivan de esta decisión (repositorio, rama, numeración de WO, documentación canónica) están en `AD-ROOT-0001`, ya actualizado.

---

## 6. Recomendación de gobierno hacia adelante (no vinculante, no decide entre A/B/C)

El patrón que produjo las tres líneas es el mismo en los tres casos: el conocimiento del proyecto estuvo repartido entre documentos, memoria de conversación, ramas de git y repositorios físicamente distintos — y cada vez que alguno de esos cuatro no estuvo disponible para quien continuaba el trabajo, apareció una bifurcación nueva. Esto no es una crítica a ninguna sesión o decisión puntual — es una condición estructural que puede repetirse con cualquier equipo o herramienta mientras no exista:

- Un único repositorio de referencia.
- Una única rama principal declarada como tal (por ejemplo, en un `README.md` en la raíz del proyecto, no solo dentro de un documento de cierre).
- Un conjunto de documentos canónicos, con versión y autoridad explícitas.
- Un registro formal de decisiones arquitectónicas (ADR) consultado *antes* de iniciar trabajo nuevo, no solo escrito después.

Esta sección es una observación de proceso, no una instrucción — queda a discreción de Hernán adoptarla, junto con las respuestas de la sección 5.

---

## 6.1 Documentos relacionados

Este documento es el primero de un conjunto de tres pensado para que el mismo problema no se repita:

- **`AD-DEC-0001`** (este documento) — qué ocurrió, y las preguntas de gobierno pendientes.
- **`AD-ROOT-0001` — Canon del Proyecto** — bloqueado hasta que la sección 5 de este documento esté resuelta; declara repositorio, rama, arquitectura, numeración de WO y documentación oficiales una vez decidido.
- **`AD-GOV-0001` — Reglas de Desarrollo** — no bloqueado, ya redactado; reglas de proceso derivadas directamente de los incidentes encontrados en esta auditoría (colisión de numeración WO-012, arquitectura paralela sin ADR comparativo, ausencia de referencia a Build B en los documentos de Build C).

## 7. Evidencia de respaldo

Todo lo afirmado en este documento proviene de comandos de solo lectura ejecutados sobre el repositorio (`git log`, `git show`, `git ls-tree`, `md5sum`, `find`) y de un registro de memoria de proyecto (`adan_platform_execution.md`) escrito en tiempo real durante la migración A→B. El detalle completo de cada comando y su salida está disponible en la sesión de auditoría que originó este documento; no se reproduce aquí para mantenerlo legible.
