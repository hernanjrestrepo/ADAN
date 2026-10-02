# WO-108 — Onboarding y Nivel 1 completo

**Fecha:** 2026-10-02 · **Ejecutor:** Claude Code · **Autoriza:** Hernán ("sigue con WO-108, no pares"; permiso para revisar y fusionar los PR, 2026-10-02)
**Formato:** EPWO-050 · **Checklist:** EPWO-051
**Estado:** 🟡 **Hecha la parte técnica**, fusionada con su PR. El plan define el cierre de esta WO como **un piloto real con una empresa de Paradixe**, y eso solo puede hacerlo Hernán (§5).

---

## 1. Fase -1

| Verificación | Resultado |
|---|---|
| Canon | WO-108 en `docs/auditoria/PLAN_WO_ADAN_100.md` §4. Alcance:<ul><li>AD-FUNC-06 completo, con consentimiento de datos (`AD-DEC-0002` decisión 8);</li><li>Nivel 1 con evidencia externa vía CSI y aprobación del cliente;</li><li>Vista de Nivel y Cards.</li></ul> |
| Especificación | **AD-FUNC-06** pide llegar a la primera pregunta real, no llenar un formulario:<ul><li>captura mínima (§2);</li><li>creación progresiva de entidades (§3);</li><li>Identidad Progresiva derivada, nunca guardada (§3.1);</li><li>recuperación desde el último paso real (§3.3);</li><li>menos de 30 s a la primera pregunta (§3.4).</li></ul>**AD-FUNC-01, Nivel 1:** el dolor se valida con CSI, no solo con la palabra del cliente. **AD-000 §3-4:** CSI es la inteligencia externa del ecosistema, siempre por contrato versionado y nunca con acceso directo. **AD-DEC-0002 d.8:** consentimiento explícito y anonimización (Ley 1581 de 2012). |
| Estado previo | <ul><li>El registro no pedía consentimiento.</li><li>Después de registrarse, la persona veía un tablero vacío y un formulario de 4 campos.</li><li>Al entrar al Nivel 1, el chat estaba vacío: ADÁN nunca preguntaba primero.</li><li>No existía una vista de los 7 Niveles.</li><li>La evidencia externa era solo un enlace sin comprobar.</li></ul> |
| CSI | No existe todavía una API de CSI a la que conectarse. Se construyó el lado de ADÁN del contrato (v0) y la verificación real de fuentes mientras tanto (§4). |

## 2. Qué se hizo

| Pieza | Detalle |
|---|---|
| **Consentimiento** (Ley 1581) | Sin aceptar la política de tratamiento de datos no hay cuenta: la API responde 422 y el botón no se habilita. La inteligencia agregada y anonimizada es una autorización aparte y opcional.<ul><li>Cada constancia guarda el propósito, la decisión, la versión de la política y la fecha, en la tabla `consents` (Registro Permanente, con triggers append-only).</li><li>Cambiar de opinión agrega una fila nueva; la anterior se conserva.</li><li>Retirar la autorización de tratamiento se tramita como solicitud de supresión.</li><li>Página pública `/privacidad` con la política y, si hay sesión, las autorizaciones de la persona.</li></ul> |
| **Onboarding** (AD-FUNC-06) | Al registrarse, **una sola pregunta**: "¿Cómo se llama tu empresa o tu idea?" (es una idea / ya existe).<ul><li>En cuanto nace la empresa, **ADÁN escribe su primera pregunta real** en la conversación del Nivel 1, sin esperar al cliente. También ocurre cuando la empresa se crea desde el tablero.</li><li>El tiempo desde el registro queda medido en el evento `onboarding_first_question` (meta: 30 s).</li><li>Recuperación: quien vuelve a medio camino retoma desde su último paso real.</li><li>La primera pregunta nunca se repite.</li></ul> |
| **Identidad Progresiva** (§3.1) | Se deriva de lo que ya hay en el Gemelo, con un hito para cada etapa:<ul><li>**Usuario:** registro mínimo.</li><li>**Responsable de Empresa:** tiene empresa.</li><li>**Líder Activo:** recibió su primer Diagnóstico.</li><li>**Cliente Activo:** registró su primera Decisión de Negocio.</li><li>**Embajador:** una recomendación aceptada se sostuvo 30 días.</li></ul>El tablero muestra la etapa actual y el hito siguiente. |
| **Evidencia externa** | **Verificación de fuentes:** si el cliente registra un dato con enlace, ADÁN abre la fuente (con la protección SSRF de WO-094) y deja constancia: verificada con su título, no se pudo abrir, o bloqueada por ser una dirección interna.<br>**CSI, contrato v0:** `POST {CSI_BASE_URL}/v0/signals` con token. Lo que devuelve CSI entra como dato externo **propuesto**: solo cuenta para el Score cuando el cliente lo confirma (AD-CMP-01). Las señales sin fuente se descartan y lo ya registrado no se repite. Sin CSI conectado, la interfaz lo dice claramente. |
| **Vista de Nivel y Cards** | Página `/ruta/{empresa}` con los 7 Niveles. Cada uno muestra su estado, lo que descubre (AD-FUNC-01), su entregable, sus Cards y su Score. Se llega desde el tablero. API: `GET /companies/{id}/levels`. |
| **Migración `0007`** | Tabla `consents` con triggers, y dos campos nuevos en `evidence`: `confirmed` y `verification`. |

## 3. Evidencia

| Evidencia | Resultado | Método |
|---|---|---|
| Suite con SQLite | **407 passed**, 8 omitidas: PostgreSQL y Redis, que corren en CI | `pytest`, local |
| Suite con PostgreSQL 16 | **412 passed**, 3 omitidas: Redis | `pytest`, local |
| Pruebas nuevas | 17 en `tests/test_wo108.py`:<ul><li>sin consentimiento no hay cuenta;</li><li>constancias con versión, append-only, y retiro equivalente a supresión;</li><li>primera pregunta real con el nombre y medición del tiempo;</li><li>no repetición y recuperación;</li><li>la escalera completa de identidad;</li><li>fuente verificada, inalcanzable y bloqueada (169.254.169.254);</li><li>CSI no conectado;</li><li>CSI simulado por HTTP con el contrato v0: propone, el cliente confirma, recién entonces cuenta y no se repite;</li><li>vista de Niveles y su privacidad.</li></ul>Las 20 llamadas de registro de las pruebas existentes ahora envían el consentimiento. | `pytest` |
| Migración | `0007` sube, baja a `0006`, vuelve a subir y `alembic check` no muestra diferencias, en SQLite y PostgreSQL. | Alembic, local |
| Frontend | Tipos y lint limpios; **24 E2E**:<ul><li>consentimiento obligatorio;</li><li>bienvenida de una pregunta;</li><li>recuperación;</li><li>ruta de 7 Niveles;</li><li>verificación y CSI;</li><li>CSI no conectado.</li></ul> | Playwright |
| Verificación real | Backend real y Chromium. Del registro a la primera pregunta de ADÁN: **3,4 s en escritorio y 2,1 s en celular** (meta < 30 s). Este entorno no tiene salida a internet, así que la fuente de ejemplo quedó como "no se pudo abrir", tal como debe informarse. | `docs/wo/evidencia/WO-108/` (10 capturas) |

## 4. Decisiones de diseño (por delegación)

1. **El consentimiento obligatorio está en la API, no solo en la pantalla.** Un registro sin `accept_data_policy` recibe 422.
2. **Dos propósitos separados:** el tratamiento para prestar el servicio (obligatorio) y la inteligencia agregada y anonimizada (opcional, desmarcada por defecto), como pide la decisión 8.
3. **Política versionada (`2026-10`).** Si cambia el texto, sube la versión y queda claro qué aceptó cada persona. El texto no nombra un correo de contacto que no está decidido; dice "el canal de atención de Paradixe".
4. **La empresa nace con la primera respuesta de onboarding,** no con la primera respuesta sobre el dolor como sugiere AD-FUNC-06 §3. Así ADÁN puede escribir su pregunta dentro del Nivel 1 y nada queda en el aire. Proyecto y Workspace nacen con ella (decisión de WO-098).
5. **La primera pregunta es un texto fijo, no generado por el LLM.** Llega al instante y no depende de que haya modelo.
6. **"Embajador":** una decisión ejecutada sin divergencia y sostenida 30 días. El mecanismo de referidos queda fuera, como dice AD-FUNC-06 (WO-100).
7. **CSI propone y el cliente confirma.** Un dato que no ha visto el cliente no mueve su Score.
8. **La verificación nunca bloquea el registro.** Una fuente que no abre queda marcada y el cliente lo ve, pero la evidencia se guarda.

## 5. Pendiente

- **Piloto real con una empresa de Paradixe (Hernán).** Es el criterio de cierre del plan. Necesita:
  - el stack desplegado (`scripts/deploy.sh`);
  - la clave de Anthropic, para que la conversación y el Board sean de calidad;
  - una empresa dispuesta a recorrer el Nivel 1.
- **CSI:** cuando exista su API, basta configurar `CSI_BASE_URL` y `CSI_API_KEY` y cumplir el contrato v0 (`backend/app/scoring/external.py`). Formalizarlo como AD-INT de CSI queda para cuando CSI se construya.
- **Onboarding multicanal** (voz, documentos, AD-FUNC-06 §3.2): la base existe (TEF y Voice simulados), pero la ingesta real llega con un AD-ARQ futuro.
- **Extracción automática de afirmaciones** desde la conversación (de WO-107): sigue pendiente.
- **Cuentas antiguas:** las creadas antes de WO-108 no tienen constancia de consentimiento, y en `/privacidad` aparecen "sin autorizar". Falta un aviso que les pida aceptar la política la próxima vez que entren.

## 6. Checklist EPWO-051

- [x] Evidencia objetiva ejecutada (§3).
- [x] Pruebas que pasan en local; CI en el PR.
- [x] Documentación y deuda registradas.
- [x] Reporte en `docs/wo/`.
- [ ] PR fusionado a `main` con el CI en verde.
- [ ] Piloto real (Hernán).
