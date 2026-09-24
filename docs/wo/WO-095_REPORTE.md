# WO-095 — Estabilización funcional

**Fecha:** 2026-09-24 · **Ejecutor:** Claude Code · **Autoriza:** Hernán ("haz todo lo que tengas que hacer", misma fecha)
**Formato:** EPWO-050 · **Checklist:** EPWO-051
**Estado:** ✅ Cerrada al fusionar su PR en `main`.

---

## 1. Fase -1 (AD-GOV-0001, Regla 7)

| Verificación | Resultado |
|---|---|
| Canon leído | `AD-ROOT-0001`, `AD-GOV-0001`, `AD-DEC-0001` y `AD-DEC-0002`. Repositorio `hernanjrestrepo/ADAN`, rama base `main` en `ca4b648` (WO-094 fusionada), rama de trabajo `claude/nifty-ptolemy-30dwoo`. |
| Reutilización (EPWO-022) | Se reutilizaron `ai/normalize.py`, `GemeloDigitalService` y el modelo `Decision` que ya existía, con sus estados `PROPOSED`, `APPROVED`, `REJECTED` y `EXECUTED`. No se creó ningún módulo paralelo. Los únicos archivos nuevos son `core/disclaimer.py`, `ems/store.py`, `AiDisclaimer.jsx`, `requirements-dev.txt` y las pruebas. |
| Alcance congelado (EPWO-008) | La ficha de `docs/auditoria/PLAN_WO_ADAN_100.md` §4: B1–B4 y B6–B18, aprobación del cliente (Patrón A), avisos de IA, etiqueta `mock` y `requirements-dev.txt`. B5 queda fuera y pasa a WO-107. |
| Numeración (Regla 2) | WO-095 figura en el rango nuevo WO-095 → 099 del Canon. No choca con ninguna reserva. |
| Camino crítico | B4, la aprobación del cliente, es la pieza más larga: toca el backend, la API y la interfaz. Lo demás son arreglos locales. |
| Aprobación | Hernán aprobó el plan y pidió ejecutarlo sin más preguntas (2026-09-24). |

Sin hallazgos bloqueantes.

## 2. Qué se corrigió

Cada bug tiene su prueba de regresión en `backend/tests/test_wo095.py`.

| Bug | Corrección | Prueba |
|---|---|---|
| B1 | `save_recommendation` pasaba los argumentos corridos a `_record_event`. Ahora registra el evento `recommendation_saved`. | `test_b1_*` |
| B2 | `/cognitive/think` hace `commit` al terminar. `_persist_conversation` crea la tarjeta `cognitive` en el Nivel activo cuando falta y solo hace `flush`. | `test_b2_*` |
| B3 | Un voto inválido, un error del LLM o una respuesta que no es JSON cuenta como **abstención** con confianza 0, en `normalize_vote`, en el Board Room de Nivel 1 y en el Board ejecutivo de 7. Las abstenciones no suman. **Regla de quórum:** si menos de la mitad de los agentes emite un voto válido, el resultado es "Sin consenso". | `test_b3_*` (5) |
| B4 | El Board solo **propone**: la decisión queda en `PROPOSED` y guarda el consenso en su evento. El Gate Review ya no cierra el Nivel, sino que propone el cierre. Se agregaron `GET /nivel1/{id}/decisions` y `POST /nivel1/{id}/decisions/{decision_id}`: el cliente aprueba o rechaza, y si aprueba el cierre, el Nivel se completa y la decisión pasa a `EXECUTED`. Una decisión que ya se decidió responde 409. | `test_b4_*` (5) |
| B6 | `recommendations` y `gate-review` reutilizan el último Board Room guardado, sin volver a correrlo. Si no hay uno, responden 400. Un segundo Gate no crea otra decisión: reutiliza la pendiente. | `test_b6_*` (2) |
| B7 | El disenso reúne a todos los agentes que discrepan, no solo al último. | `test_b7_*` |
| B8 | El chat envía los últimos 12 mensajes. Los anteriores se condensan en un resumen extractivo de 2.000 caracteres como máximo. | `test_b8_*` |
| B9 | El SSE envía eventos JSON (`{"token": …}` y un evento final `{"done": true, "disclaimer": …}`). La respuesta se guarda en `finally`, aunque el cliente se desconecte. | `test_b9_*` |
| B10 | Se eliminó `services/memory.py`, que estaba roto y nadie usaba. | `test_b10_*` |
| B11 | `ems/store.py` es el índice vectorial único para `/agents`, `/board`, `/ems` y `/dka`. Se reconstruye desde la BD en el primer uso. | `test_b11_*` |
| B12 | El CEO ya no hace llamadas de relleno (`COUNT(*)` global, `httpbin.org`, calculadora con "0"). El paso queda marcado como omitido. | `test_b12_*` |
| B13 | DKA sin URLs devuelve un mensaje claro y no ingiere páginas de demostración. | `test_b13_*` |
| B14 | La confianza va de 0 a 100 en todo el sistema (`_to_percent`), y en la memoria se guarda como fracción. | `test_b14_*` (parametrizada) |
| B15 | Completar el Nivel 7 no crea un Nivel 8 (`LAST_LEVEL = 7`). | `test_b15_*` |
| B16 | `record_correction` guarda el ajuste de confianza en un solo `commit`. `delete_document` archiva en vez de borrar, y los listados y búsquedas excluyen los documentos archivados. | `test_b16_*` (2) |
| B17 | Si el LLM devuelve una lista JSON, el voto cuenta como abstención y no produce un 500. | `test_b17_*` |
| B18 | `ensure_sqlite_dir` solo crea carpetas cuando la URL es SQLite. | `test_b18_*` |
| B19 *(nuevo)* | La pestaña Board Room leía `data.board_results`, un campo que no existe, así que nunca mostraba los votos. Ahora se muestran los votos con su etiqueta, la decisión y el disenso. | Verificación con Playwright (§3) |

Además:
- **Avisos de IA** (`AD-DEC-0002`, decisión 6):
  - En la API, como campo `disclaimer` en chat, Gate, cognitivo, CEO y Board.
  - En los documentos guardados: el Gate lo quita antes de evaluar.
  - En la interfaz: registro, dashboard y pie de página de Nivel 1.
- **Etiqueta `mock`** en voz, omnicanal y conectores simulados. Omnicanal responde `delivered: false`. El único conector real es `rest_api`.
- **`backend/requirements-dev.txt`** con las versiones instaladas y probadas.

**B5** (el Gate que cuenta palabras clave) queda para **WO-107**, como fija el plan.

## 3. Evidencia (EPWO-017/018)

| Evidencia | Resultado | Método |
|---|---|---|
| Suite del backend | **261 passed**, 2 deseleccionadas (stress) | `pytest`, 35,7 s |
| Stress | 2 passed | `tests/test_stress.py` contra un servidor real en `:8050` |
| Lint de los archivos tocados | 54 → 44 avisos de pyflakes, **0 nuevos** | Comparación antes y después |
| Build del frontend | Sin errores, 306 kB de JS | `vite build` |
| E2E real con Ollama | Chat (SSE) funcional. Board: los 4 agentes se abstienen → "Sin consenso" (antes contaba como PROCEED). Diagnóstico en 95,6 s, con aviso. Recomendaciones en 68 s con **1** llamada al LLM (antes eran 5 y fallaban con 500). Gate en 0,0 s (sin repetir el Board): 73/100, no aprobado. Las decisiones quedan `proposed`. | Backend en `:8060` con Ollama 0.34.4 y `qwen2.5:0.5b` |
| Interfaz | El Board Room muestra votos, etiquetas y "Sin consenso". El Gate aprobado muestra los botones "Aprobar cierre del Nivel 1" y "Todavía no". Al aprobar, el Nivel 1 pasa a "Completado" y el Nivel 2 queda activo. El aviso de IA es visible. | Playwright + Chromium contra `vite` en `:5199`. Capturas en `docs/wo/evidencia/WO-095/` |

Capturas:
- `ui_board_room.png`: Board Room con el código final. 4 de 4 agentes se abstienen, así que el resultado es "Sin consenso".
- `ui_board_room_antes_quorum.png`: la misma pantalla **antes** de la regla de quórum. Tres agentes se abstenían y el voto del CMO decidía "Detener" por todo el Board. Por este hallazgo se agregó el quórum.
- `ui_gate_pending.png` y `ui_gate_approved.png`: el cierre del Nivel pendiente de aprobación y luego aprobado por el cliente.

## 4. Hallazgos de la ejecución

1. **`qwen2.5:0.5b` no alcanza.** En el E2E real se niega a responder ("no puedo ayudar con eso") y casi nunca devuelve el JSON que se le pide, así que el Board casi siempre se abstiene. Ahora el sistema lo muestra con honestidad en vez de aprobar por defecto, pero el producto necesita un modelo más capaz. Se resuelve en **WO-099**: enrutamiento Ollama avanzado / Anthropic según complejidad (`AD-DEC-0002`, decisión 3).
2. **Quórum.** No estaba en la auditoría y apareció en el E2E: un solo voto válido decidía por siete agentes. Quedó corregido en esta WO, con prueba.
3. **B19**, descrito en §2.

## 5. Deuda técnica y riesgos

- Los 44 avisos de pyflakes que ya existían en los archivos tocados (imports sin usar, sobre todo). Se atienden en WO-093, cuando haya lint en CI.
- El índice vectorial sigue en memoria (reconstruible). Lo reemplaza pgvector en WO-091.
- El resumen de conversaciones largas es extractivo, no generado por el LLM. Alcanza para no desbordar el contexto; la memoria por capas (AD-CMP-04) llega en WO-098.
- Las pruebas de interfaz son manuales con Playwright. La suite E2E automatizada se arma en WO-093.

## 6. Checklist EPWO-051

- [x] Evidencia objetiva ejecutada (§3).
- [x] Pruebas que pasan: 261 + 2 de stress.
- [x] Una prueba de regresión por cada bug del alcance.
- [x] Documentación y deuda registradas (este reporte, §5).
- [x] `git status` limpio al hacer el commit.
- [x] Reporte en `docs/wo/`.
- [x] PR fusionado a `main`.
