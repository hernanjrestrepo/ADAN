# WO-099 — Motor cognitivo único e IA

**Fecha:** 2026-09-25 · **Ejecutor:** Claude Code · **Autoriza:** Hernán ("sigue con lo que propones", 2026-09-25: adelantar WO-099 a WO-098)
**Formato:** EPWO-050 · **Checklist:** EPWO-051
**Estado:** ✅ Cerrada al fusionar su PR. **Falta una verificación:** correr la IA con la clave real de Anthropic. Esta sesión no tiene clave; la verificación es `scripts/check_claude.py` (§5).

---

## 1. Fase -1

| Verificación | Resultado |
|---|---|
| Canon | WO-099 está definida en el plan (`docs/auditoria/PLAN_WO_ADAN_100.md` §4). La decisión 3 de `AD-DEC-0002` fija qué modelo hace qué: Ollama para lo simple y Anthropic según la complejidad. |
| Especificación | AD-FUNC-02: los 7 roles, el Flujo Maestro (§3), la jerarquía de autoridad (§2) y el disenso visible. AD-CMP-04: las cinco capas de memoria, los resúmenes que ascienden y la regla de no repetición. AD-CMP-05: la evidencia que se le pide al cliente. |
| Estado previo | Había dos Board distintos:<br>• Nivel 1: 4 agentes en paralelo.<br>• `/board`: 7 agentes en secuencia, con COO, CLO y CHRO, que no son los roles de la especificación.<br>Solo existía Ollama con `qwen2.5:0.5b` y 512 tokens: el JSON llegaba cortado y el Board se abstenía. El contexto era el historial crudo de la conversación. No se medía el costo. |
| Reutilización | La capa de adaptadores (`LLMAdapter`), la normalización de votos, `InstrumentedLLM` (WO-093) y el consenso con quórum (WO-095). |

## 2. Qué se hizo

| Sprint | Pieza | Detalle |
|---|---|---|
| 1 | **Adaptador de Anthropic** | Usa el SDK oficial (`anthropic` 1.8). Detalle:<ul><li>Pensamiento adaptativo, con el esfuerzo que corresponde a cada nivel.</li><li>No envía parámetros de muestreo, porque los modelos actuales los rechazan.</li><li>Salidas estructuradas con `output_config.format`.</li><li>`fallbacks: "default"`: si Claude declina por política, la API reintenta con el modelo que Anthropic recomienda para ese caso.</li><li>Calcula el costo de cada llamada con la tarifa pública.</li></ul> |
| 1 | **Enrutador por complejidad** | Cada nivel va a un modelo:<ul><li>`simple` → Ollama.</li><li>`fast` → Haiku.</li><li>`standard` → Sonnet: conversación, diagnóstico y apertura y cierre del Board.</li><li>`complex` → Opus: los votos del Board.</li></ul>Sin clave, o si Claude falla por red, por la API o por un rechazo, la llamada cae a Ollama y queda marcada como **degradada**. El servicio no se cae. |
| 1 | **Salidas estructuradas** | El voto tiene un esquema JSON y el modelo queda restringido a él: Claude con `output_config.format`, Ollama con `format`. Se acaba el JSON cortado o mal formado, que era la causa de que el Board se abstuviera siempre. |
| 1 | **Costo por empresa y Nivel** (AD-IA-03) | Tabla `llm_usage` (migración `0003`) con una fila por llamada: modelo, nivel, tokens y costo. Métricas Prometheus `adan_llm_tokens_total`, `adan_llm_cost_usd_total` y `adan_llm_degraded_total`. Resumen por empresa en `GET /api/v1/companies/{id}/llm-usage`: total, por Nivel y por modelo. |
| 2 | **Board Room de 7 roles** (AD-FUNC-02) | Sigue el Flujo Maestro:<ol><li>El CEO abre con el objetivo y la decisión en juego.</li><li>Votan en paralelo **CTO, CFO, CMO, Legal, Producto y Operaciones**.</li><li>Consenso con quórum y disenso visible.</li><li>El CEO cierra con la síntesis, la **evidencia que falta pedirle al cliente** y los próximos pasos.</li></ol>El CEO preside y no vota (§2.3). |
| 2 | **Participación del cliente y acta** | El cliente puede plantear su pregunta y su posición, y las dos llegan a cada especialista. Cada sesión deja un **Acta del Board Room** como documento del Gemelo Digital. La interfaz muestra el formulario, la apertura, la síntesis, la evidencia pedida y los 6 votos. |
| 3 | **Un solo Board Room** | El Board ejecutivo de la operación continua (`/board`, OOS) usa ahora el mismo motor y los mismos 7 roles. Conserva lo suyo: memoria y decisiones pasadas como contexto, el Decision Record y su persistencia. `agents/board.py` pasa de ~740 a ~300 líneas. |
| 4 | **Memoria en cinco capas** (AD-CMP-04) | **Global → Proyecto → Nivel → Card → Conversación** en el contexto del chat:<ul><li>perfil de la empresa;</li><li>decisiones aprobadas;</li><li>scores;</li><li>resúmenes de los Niveles cerrados;</li><li>resultado y evidencia pedida del último Board;</li><li>la Card y sus conversaciones anteriores.</li></ul>**Regla de no repetición:** si algo ya se sabe, ADÁN no lo pregunta y dice qué está asumiendo. Al cerrar un Nivel, sus Cards se completan, las conversaciones quedan resumidas y el **resumen del Nivel asciende al Proyecto**. |
| — | **Modelo local de producción** | `.env.prod.example` pasa a `qwen2.5:7b` para las tareas simples. El 0,5B queda solo para desarrollo. |

## 3. Evidencia

| Evidencia | Resultado | Método |
|---|---|---|
| Suite con SQLite | **328 passed**, 7 omitidas: las de PostgreSQL y Redis, que corren en CI | `pytest`, local |
| Pruebas de WO-099 | 17 pruebas (`tests/test_wo099.py`), que cubren:<ul><li>el enrutamiento por nivel;</li><li>la degradación sin clave y ante fallas;</li><li>la forma exacta de la petición a Claude: sin `temperature`, con esquema, `fallbacks`, costo y rechazo;</li><li>el Board con salida estructurada;</li><li>el costo por empresa, persistido incluso si la petición falla, y aislado entre empresas;</li><li>la sesión con participación del cliente y el acta;</li><li>las cinco capas y el resumen de Nivel que asciende.</li></ul> | `pytest` |
| Migraciones | `0003`: subir, `alembic check` sin diferencias, bajar y subir | Alembic contra SQLite, local; PostgreSQL en CI |
| Frontend | Tipos, lint y build. **11 E2E**, incluida la participación del cliente en el Board | Playwright con Chromium |
| `pip-audit` | Sin vulnerabilidades, con `anthropic` 1.8.0 | local |
| CI | El sprint 1 pasó los 3 jobs, incluido el stack de producción. El resto queda en la corrida del PR. | GitHub Actions |

## 4. Deuda y riesgos

- **Sin verificación real con Claude.** Esta sesión no tiene `ANTHROPIC_API_KEY`: el adaptador está probado con un cliente simulado que valida la forma exacta de la petición. Con la clave, correr `python scripts/check_claude.py`, que hace una conversación y un voto del Board con JSON y muestra el modelo, los tokens y el costo.
- **Costo:** con clave, una sesión de Board son 8 llamadas (6 votos en Opus, más apertura y cierre en Sonnet). El costo real queda medido en `llm-usage`. Si pesa, se pueden bajar los votos a Sonnet con `LLM_MODEL_COMPLEX=claude-sonnet-5`.
- **El debate secuencial** del Board ejecutivo (cada agente respondía al anterior) se reemplazó por votos independientes con apertura y cierre del CEO, que es lo que pide AD-FUNC-02. Si se quiere una segunda ronda de réplica (AD-CMP-02), es una extensión del motor único.
- **La capa Global** es conocimiento fijo de ADÁN. El aprendizaje entre empresas es WO-118.
- **Los resúmenes** que ascienden son extractivos y deterministas: no llaman al modelo. Los resúmenes con IA quedan para cuando haya medición de calidad.
- **La participación del cliente durante la sesión** (réplicas en vivo, invitados sin voto) llega con la vista de Board de AD-UX. Hoy participa al inicio, con su pregunta y su posición, y al final, cuando aprueba (Patrón A).

## 5. Cómo activarla

```bash
# .env o .env.prod
ANTHROPIC_API_KEY=sk-ant-...
python scripts/check_claude.py          # verifica conversación y voto del Board
```

Sin clave, ADÁN sigue funcionando con Ollama, y `llm-usage` muestra las llamadas degradadas.

## 6. Checklist EPWO-051

- [x] Evidencia objetiva ejecutada (§3).
- [x] Pruebas que pasan en local y en CI.
- [x] Documentación y deuda registradas (README, Canon, plan, estado y este reporte).
- [x] `git status` limpio y un commit por sprint.
- [x] Reporte en `docs/wo/`.
- [x] PR fusionado a `main`, con el CI en verde.
