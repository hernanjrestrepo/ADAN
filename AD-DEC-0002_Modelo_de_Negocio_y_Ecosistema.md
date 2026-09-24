# AD-DEC-0002 — Modelo de negocio y lugar de ADÁN en el ecosistema

**Fecha:** 2026-09-24
**Estado:** ✅ DECIDIDO — 2026-09-24, por Hernán (CTO ADÁN), en la revisión conceptual posterior a la auditoría (`docs/auditoria/AUDITORIA_ADAN_2026-09.md`). La decisión 7 la delegó Hernán explícitamente y la tomó Claude Code; queda registrada con su justificación.
**Qué reemplaza:** los textos citados en la sección 4. Los documentos del blueprint no se reescriben aquí; se actualizan en WO-096 tomando este documento como referencia (Regla 4 de `AD-GOV-0001`).

---

## 1. Decisiones

| # | Tema | Decisión |
|---|---|---|
| 0 | Campañas | **EVA hace campañas inbound y outbound.** |
| 1 | ADÁN, EVA y el ecosistema | **ARQAI y EVA son el mismo producto; ARQAI pasa a llamarse EVA.** EVA es el motor de ventas y marketing con IA: campañas, voz, agentes conversacionales y omnicanalidad. **ADÁN crea o reinventa empresas** y además **suministra agentes por hora, día, semana o mes** que hacen tareas específicas para cada empresa. El **Marketplace** y la **Comunidad** son piezas importantes del universo Paradixe. |
| 2 | Genexis | Genexis construye el software, pero **es un motor interno**: no se vende como paquete de desarrollo al cliente. |
| 3 | Modelos de IA | **Ollama avanzado para tareas simples** y **agentes de Anthropic según la complejidad** (Haiku, Sonnet, Opus). Los **MVPs del Nivel 4 se construyen con Anthropic**. |
| 4 | Red de comisiones ("Ondas Expansivas") | Se mantiene. Es un **sistema de comisiones multinivel tipo Amway**: nadie paga por entrar. |
| 5 | Programa AAA | **El % de equity se negocia caso por caso.** Se descarta el 50 % como referencia. |
| 6 | Responsabilidad | ADÁN no tiene límites temáticos, pero **en todo momento muestra un aviso**: es una IA, no reemplaza la asesoría profesional y Paradixe no se hace responsable por los resultados. |
| 7 | Motor comercial | Decidido por Claude Code, por delegación. Ver sección 2. |
| 8 | Datos | Se vende inteligencia agregada, nunca datos crudos: con **consentimiento explícito y anonimización** (Ley 1581 de 2012). |
| 9 | Número de Niveles | **7 Niveles.** Queda cerrada la diferencia con el anuncio público de 6. |
| 10 | Propiedad intelectual | **No hay nada en disputa.** Se retira ese riesgo de todos los documentos. |

## 2. Decisión 7: motor comercial

**Motor principal: venta directa y autoservicio a fundadores y pymes.** El canal institucional (universidades, cámaras de comercio, SENA, gobiernos) queda como **canal secundario de volumen**, a partir del momento en que haya casos reales que mostrar.

Por qué:
1. **El producto ya está diseñado para autoservicio:** onboarding en menos de 30 segundos, Nivel 1 gratis, pago por Nivel solo al aprobarlo y agentes por tiempo. Todo apunta a una persona que decide y paga sola.
2. **Los canales que ya existen empujan en esa dirección:** EVA hace campañas inbound y outbound, y la red de comisiones distribuye de persona a persona. Ninguno de los dos está hecho para una venta institucional larga.
3. **El canal institucional necesita evidencia que hoy no existe.** Una cámara de comercio o una universidad compra con casos de éxito, métricas de cohortes y contratos. Eso se construye primero con clientes directos: el piloto de WO-108 y los Niveles completos (H4).
4. **El canal institucional no se pierde:** entra como licencias por cohorte sobre el mismo producto, sin una versión aparte.

Esta decisión se revisa con datos reales de adquisición cuando se cierre el hito H3 (primer piloto real).

## 3. Consecuencias

### 3.1 Mapa del ecosistema (reemplaza AD-000 §3 en lo que contradice)

| Componente | Rol |
|---|---|
| **ADÁN** | Crea o reinventa empresas (7 Niveles y demás puntos de entrada) y suministra agentes por tiempo para tareas específicas de cada empresa |
| **EVA** (antes ARQAI) | Ventas y marketing con IA: campañas inbound y outbound, voz, agentes conversacionales, omnicanalidad |
| **Genexis** | Motor interno de construcción de software; lo usa ADÁN, no lo compra el cliente |
| **CSI** | Inteligencia externa: mercado, competencia, regulación |
| **Marketplace** | Publicación y venta de agentes, servicios y APIs del ecosistema y de terceros |
| **Comunidad** | Red de emprendedores y empresas del ecosistema; es también el soporte de la red de comisiones |
| **Paradixe Capital** | Programa AAA: invierte con equity negociado caso por caso; decide un comité independiente |

**Finanzas del Nivel 3:** como el nuevo EVA es ventas y marketing, las proyecciones financieras las hace el agente CFO de ADÁN contrastadas con benchmarks de CSI. Ya no dependen de EVA.

**ATO:** esta decisión no lo menciona y su rol queda como está. Si EVA absorbe también el motor comercial, se registra en un AD-DEC posterior.

### 3.2 Fuentes de ingreso (insumo para WO-100)

| Línea | Cómo cobra | Estado |
|---|---|---|
| **Niveles** | Nivel 1 gratis; pago único al aprobar cada Nivel siguiente | Se mantiene |
| **Agentes por tiempo** | Por hora, día, semana o mes, según las tareas que el agente hace para la empresa | **Nueva**: es el ingreso recurrente de ADÁN y reemplaza la "membresía operativa" de planes fijos |
| **Marketplace** | Comisiones por venta, contratación, servicios y APIs | Se mantiene |
| **Programa AAA** | Equity negociado caso por caso | Se mantiene, sin 50 % de referencia |
| **ADÁN Academy** | Cursos, certificaciones y licencias institucionales | Se mantiene |
| **Inteligencia agregada** | Informes y licencias con datos anonimizados y consentidos | Se mantiene |
| ~~Desarrollo de SaaS~~ | ~~Paquetes USD 1.500–20.000~~ | **Eliminada**: Genexis es interno |

La **red de comisiones** es un canal de distribución: es un costo de adquisición, no una línea de ingreso.

### 3.3 Cumplimiento que WO-100 debe incluir

- **Red multinivel:** la comercialización en red es legal en Colombia bajo la **Ley 1700 de 2013**, que exige ciertas condiciones:
  - Que las comisiones salgan de ventas reales de productos o servicios, no del simple reclutamiento.
  - Un plan de compensación publicado y contratos escritos con los participantes.
  - La vigilancia de la Superintendencia de Sociedades.

  El diseño de "Ondas Expansivas" (7 niveles, 1 % de la red) debe cumplir esas condiciones desde el primer día. No se cuestiona la decisión, se registra lo que exige para cumplirla.
- **Avisos de IA (decisión 6):** texto único en `backend/app/core/disclaimer.py`, visible en la interfaz, en cada documento generado y en las respuestas de la API. Se implementa en WO-095.
- **Datos (decisión 8):** consentimiento explícito en el registro y anonimización verificable antes de cualquier informe agregado.

### 3.4 Impacto en el plan de Work Orders

- **WO-095:** agrega los avisos de IA.
- **WO-099:** enrutamiento Ollama avanzado + Anthropic (Haiku, Sonnet, Opus) según complejidad.
- **WO-111 (Nivel 3):** finanzas con el CFO de ADÁN + CSI, sin EVA.
- **WO-112 (Nivel 4):** MVP construido con Anthropic, a través de Genexis como motor interno.
- **WO-119:** la integración de voz y canales pasa a ser **EVA** (antes ARQAI), con campañas inbound y outbound.
- **Nuevas:** **WO-109 Agentes por tiempo** y **WO-121 Comunidad y red de comisiones**. Ver `docs/auditoria/PLAN_WO_ADAN_100.md` v2.

## 4. Textos que este documento reemplaza

| Documento | Texto | Queda |
|---|---|---|
| `AD-000` §3 | EVA = operación continua y finanzas; ARQAI = voz e interacción | EVA (antes ARQAI) = ventas, marketing, voz y canales |
| `AD-000` §6 | "ADÁN nunca se convierte en el sistema de operación continua" | ADÁN suministra agentes por tiempo para tareas específicas; las ventas y el marketing continuos siguen siendo de EVA |
| `Chat 1.docx`, monetización | Líneas 2 (SaaS) y 3 (membresía USD 99/299/999); AAA al 50 % | Ver 3.2 |
| `WO-000_INDICE_MAESTRO_v1/v2/v3`, `AD-ROOT-0001 §4` (WO-100) | "IP en disputa con el socio" | No hay disputa (decisión 10) |
| `AD-FUNC-01` §1 | Pregunta abierta sobre anunciar 6 o 7 Niveles | 7, cerrado (decisión 9) |
