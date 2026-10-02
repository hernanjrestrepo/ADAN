# WO-107 — Evidencia y Scoring

**Fecha:** 2026-10-02 · **Ejecutor:** Claude Code · **Autoriza:** Hernán ("sigue con WO-107, no pares"; permiso para revisar y fusionar los PR, 2026-10-02)
**Formato:** EPWO-050 · **Checklist:** EPWO-051
**Estado:** ✅ Cerrada al fusionar su PR. Cierra el hallazgo **B5** de la auditoría.

---

## 1. Fase -1

| Verificación | Resultado |
|---|---|
| Canon | WO-107 está en `docs/auditoria/PLAN_WO_ADAN_100.md` §4: jerarquía de evidencia (AD-CMP-05), los 8 scores de AD-FUNC-07 con su motor (AD-ARQ-10) y un Gate Review basado en evidencia que cierre B5. |
| Especificación | Se leyeron:<ul><li>**AD-CMP-05:** jerarquía de validez y paso de conversación a Score. "La inspección de una Conversación, por sí sola, nunca es evidencia suficiente".</li><li>**AD-FUNC-07:** los 8 Scores en dos familias, con Confidence Level obligatorio.</li><li>**AD-CMP-01:** avanzar exige evidencia y la aprobación del cliente. Si el cliente quiere avanzar sin evidencia, decide él y queda documentado.</li><li>**AD-FUNC-01 Nivel 1:** "requiere evidencia externa suficiente".</li></ul> |
| Estado previo | <ul><li>**B5:** el Gate contaba palabras clave ("problema", "mercado", "USD"…) en un diagnóstico escrito por el mismo LLM, al que se le pedía usar esas palabras. Un texto largo con esas palabras aprobaba el Nivel sin ninguna evidencia del cliente.</li><li>El Problem Score era una copia del puntaje del Board.</li><li>Solo existían 6 tipos de Score.</li></ul> |
| Faltante | **AD-ARQ-10 (Motor de Scoring) nunca se escribió.** Su primera versión se decidió por delegación (§4) y vive en `backend/app/scoring/engine.py`. |

## 2. Qué se hizo

| Pieza | Detalle |
|---|---|
| **Evidencia** (entidad del Gemelo) | Tabla `evidence` (migración `0006`) con Contrato Base: tiene versiones, se archiva y nunca se borra. Cada evidencia guarda:<ul><li>la afirmación;</li><li>su lugar en la jerarquía: dato verificable, testimonio o inferencia;</li><li>si respalda o contradice;</li><li>la fuente;</li><li>la dimensión (el Score al que alimenta).</li></ul>Reglas de registro:<ul><li>El cliente registra datos y testimonios.</li><li>Un dato verificable exige fuente.</li><li>Las inferencias solo las registran los Agentes, siempre marcadas como tales.</li><li>El voto del Board Room entra como inferencia sobre el problema, nunca como prueba.</li></ul> |
| **Motor de Scoring** (AD-ARQ-10 v0) | Funciones puras y deterministas, detalladas en §4. Cada cálculo es un **Score nuevo** (Patrón C) que cita la evidencia usada y su desglose por nivel. Sin evidencia, el Score se declara con 0 y confianza 0, y lo dice. |
| **Los 8 Scores** (AD-FUNC-07) | <ul><li>Los 6 de diagnóstico se abren con su Nivel.</li><li>**Score del Responsable:** se calcula sobre decisiones reales (tomadas, ejecutadas, Niveles cerrados) y se asigna a la persona (`subject = responsible`).</li><li>**Venture Score:** agrega los de diagnóstico ponderados por su confianza y nace en el Nivel 6.</li></ul> |
| **Gate del Nivel 1** (cierra B5) | Decide solo sobre la evidencia registrada. Pide al menos:<ul><li>1 dato verificable a favor;</li><li>2 evidencias fuertes a favor (datos o testimonios);</li><li>Problem Score de 60;</li><li>confianza de 50 %.</li></ul>Si no alcanza, ADÁN dice exactamente qué falta. Si alcanza, propone cerrar el Nivel y el cliente decide. |
| **Avanzar bajo tu responsabilidad** (AD-CMP-01 §3) | Sin evidencia suficiente, el cliente puede pedir avanzar. ADÁN propone la decisión recomendando seguir; elegir "Cerrar el Nivel" es decidir distinto y exige los riesgos y la responsabilidad asumidos (los 6 campos de WO-098). |
| **API** | `/api/v1/scoring/{empresa}/`:<ul><li>`evidence`: listar, registrar y archivar.</li><li>`scores`: los 8, con disponibilidad.</li><li>`scores/{tipo}/calculate`.</li><li>`gate/{nivel}`: vista previa sin guardar nada.</li></ul>En Nivel 1, `POST …/advance-anyway`. El `gate-review` ahora devuelve `missing`, `problem_score`, `confidence` y el desglose de la evidencia. |
| **Interfaz** | <ul><li>Pestaña **Evidencia** en el Nivel 1: muestra el progreso hacia el Gate con lo que falta, un formulario guiado con la fuente obligatoria para datos externos y la lista con su nivel de validez. Una evidencia se retira con un motivo.</li><li>**Scores:** los 8 con su confianza y desglose; el Gate muestra qué falta y ofrece "Avanzar bajo mi responsabilidad", que lleva a Decisiones del Gemelo.</li><li>**Timeline:** muestra las evidencias y los Scores calculados.</li></ul> |

## 3. Evidencia

| Evidencia | Resultado | Método |
|---|---|---|
| Suite con SQLite | **390 passed**, 8 omitidas: PostgreSQL y Redis, que corren en CI | `pytest`, local |
| Suite con PostgreSQL 16 | **395 passed**, 3 omitidas: Redis | `pytest` con `TEST_DATABASE_URL`, local |
| Pruebas nuevas | 27 en total:<ul><li>**10 del motor** (`tests/test_gate_review.py`): determinismo; Score declarado sin evidencia; conversación sola nunca basta (confianza ≤ 40 %); jerarquía; contradicciones; Gate y lo que falta; Responsable y Venture.</li><li>**17 de integración** (`tests/test_wo107.py`): registro y reglas de la evidencia; el Board solo como inferencia; archivo sin borrado; los 8 Scores; serie histórica; Gate con y sin evidencia; **un diagnóstico largo con todas las palabras clave ya no abre el Gate** (regresión de B5); avance bajo responsabilidad con los 6 campos; aislamiento entre empresas; Timeline.</li></ul>`tests/test_gate_review.py` probaba el Gate por palabras clave, que se eliminó; ahora prueba el motor que lo reemplaza. | `pytest` |
| Migración | `0006` sube en SQLite y PostgreSQL; `test_wo091` verifica el esquema contra los modelos (69 tablas). | `pytest` |
| Frontend | Tipos y lint limpios; **19 E2E**, 3 nuevas: evidencia y Gate, avance bajo responsabilidad y los 8 Scores. | Playwright |
| Verificación real | Con backend real y Chromium, Gate sin evidencia → 5 evidencias (3 datos, 2 testimonios) → Problem Score 74 con 88 % de confianza → Gate propone cerrar → el cliente aprueba → Nivel 1 completado. La captura `gate_sin_evidencia.png` se tomó antes de quitar del mensaje la lista repetida de lo que falta. | `docs/wo/evidencia/WO-107/` (5 capturas) |

## 4. Decisiones de diseño (por delegación): AD-ARQ-10 v0

1. **Pesos de la jerarquía:**

   | Nivel | Peso | Techo de confianza |
   |---|---|---|
   | Dato verificable | 1.0 | 95 % |
   | Testimonio | 0.6 | 75 % |
   | Inferencia | 0.3 | 40 % |

   Por el techo, **ninguna cantidad de conversación o de votos del Board lleva la confianza más allá de 40 %**.
2. **Valor** = respaldo / (respaldo + contradicción + 1.5). El 1.5 (PRIOR) hace que poca evidencia no aparente certeza: un solo dato a favor da 40, no 100.
3. **Confianza** = 1 − e^(−masa/2), limitada por el techo del mejor nivel presente.
4. **Umbral del Gate del Nivel 1:** los cuatro mínimos de §2 (1 dato verificable, 2 evidencias fuertes, Problem Score 60 y confianza 50 %). La regla está en una sola tabla (`GATE_RULES`) para calibrarla con el primer cliente real (AD-CMP-05, Riesgos).
5. **Score del Responsable:**
   - Cada decisión tomada cuenta como testimonio.
   - Cada decisión ejecutada y cada Nivel cerrado cuentan como dato verificable, porque son hechos del Gemelo.
   - Decidir distinto a lo recomendado no resta: queda documentado.
6. **Venture Score:** promedio de los Scores de diagnóstico ponderado por su confianza. Su confianza la limita el Score menos confiable y la proporción de Scores ya calculados.
7. **El Board Room cuenta como inferencia del Agente "Board Room":** PROCEED respalda el problema, STOP lo contradice y PIVOT no se registra.
8. **Retirar evidencia es archivarla.** Los Scores anteriores la siguen citando (serie histórica, AD-CMP-05 §4).

## 5. Deuda y riesgos

- **AD-ARQ-10 como documento del blueprint.** La v0 está en el código y en este reporte. Falta redactarla en `docs/wo-000/` y que Hernán la apruebe; los pesos y umbrales son los primeros candidatos a recalibrar.
- **Extracción automática de afirmaciones.** AD-CMP-05 §2 habla de extraer afirmaciones de la conversación. Hoy las registra el cliente y el Board aporta una inferencia. Extraerlas con el LLM, siempre como inferencias para que el cliente las confirme, queda para WO-108, junto con la evidencia externa vía CSI.
- **Gates de los Niveles 2 a 7:** cada Nivel agrega su regla en `GATE_RULES` cuando se implemente (WO-110 a WO-115).
- **Score por Objetivo y por Estrategia** (AD-FUNC-07 §5): el mecanismo es el mismo, pero se aplicará cuando existan los flujos de Objetivos y Estrategias.

## 6. Checklist EPWO-051

- [x] Evidencia objetiva ejecutada (§3).
- [x] Pruebas que pasan en local; CI en el PR.
- [x] Documentación y deuda registradas.
- [x] Reporte en `docs/wo/`.
- [ ] PR fusionado a `main` con el CI en verde.
