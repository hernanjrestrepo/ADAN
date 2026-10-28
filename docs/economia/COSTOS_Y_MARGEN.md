# Costos, margen y modo inteligente

**Fecha:** 2026-10-29 · **Meta:** 90 % de margen · **Precio de los 7 Niveles:** US$ 45 (US$ 1 = 1.000 @pples)
Las cuentas salen de `backend/app/apples/economia.py` y se reproducen con las pruebas de `backend/tests/test_economia.py`.

## 1. Qué hay medido y qué es supuesto

| Dato | Origen | Confiabilidad |
|---|---|---|
| Costo por llamada con Kimi: US$ 0,0061 normal, 0,034 con búsqueda, 0,05 documento largo | Tabla `llm_usage` del piloto de Xmart Travel (oct-2026), ya en `pricing.py` | Medido |
| Llamadas por Nivel (54, 43, 42, 46, 59, 41, 41 + búsquedas y documentos) | `pricing.LEVEL_CALLS`, del mismo piloto | Medido, con holgura de 1,5× |
| Infraestructura: US$ 0,60 por Nivel | `pricing.INFRA_USD_PER_LEVEL` | **Supuesto sin medir** |
| Precios por modelo | `catalog.json`: OpenRouter, Anthropic y Moonshot, tarifa de lista | Dato público con fecha |
| Calidad de cada modelo (1 a 5) | Asignada por Paradixe según el uso | **Supuesto: hay que validarlo con evaluaciones** |
| Tokens de un MVP construido | `economia.MVP_SIZES` (landing y app son supuestos de `pricing`; plataforma, estimación) | **Sin medir** |

## 2. Los 7 Niveles a US$ 45

| Escenario | IA | Infra | Costo | Margen | Tras comisiones* |
|---|---:|---:|---:|---:|---:|
| Hoy: Kimi, infra 0,60/Nivel | 6,15 | 4,20 | 10,35 | 77,0 % | 69,9 % |
| Kimi, infra 0,15/Nivel | 6,15 | 1,05 | 7,20 | 84,0 % | 76,9 % |
| Haiku 5.5 (OpenRouter), infra 0,60/Nivel | 0,72 | 4,20 | 4,92 | 89,1 % | 82,0 % |
| **Haiku 5.5, infra 0,15/Nivel** | 0,72 | 1,05 | 1,77 | **96,1 %** | 88,9 % |
| DeepSeek v4 flash, infra 0,15/Nivel | 0,40 | 1,05 | 1,45 | 96,8 % | 89,6 % |
| Sonnet 5.5, infra 0,15/Nivel | 14,36 | 1,05 | 15,41 | 65,8 % | 58,6 % |

\* Después de la comisión de Wompi (3,15 % + IVA, más un fijo por compra) y del 3,5 % de la red de referidos.

**Conclusiones**
1. **Con Kimi y US$ 45 no se llega al 90 %, ni siquiera con infraestructura gratis** (la IA sola ya es el 13,7 % del precio).
2. **El margen del 90 % antes de comisiones es alcanzable con un modelo barato (Haiku 5.5 o DeepSeek v4 flash) y una infraestructura por Nivel menor de ~US$ 0,54.** Hoy el supuesto es 0,60.
3. **Después de comisiones el techo es ~89–90 %:** Wompi y la red se llevan ~US$ 4,4 de los 45. Si la meta del 90 % es neta de comisiones, hace falta subir el precio o cobrar los 7 Niveles en una sola compra (el fijo de Wompi se paga una vez).
4. **El modelo caro destruye el margen:** Sonnet 5.5 en todas las llamadas deja 66 %. Por eso el modo inteligente reserva lo caro para lo que decide plata del cliente.

## 3. MVP construido (se cotiza aparte: costo ÷ 0,10)

Tokens supuestos: landing 2 M entrada / 0,3 M salida; app 10 M / 1,5 M; plataforma 30 M / 5 M. Incluye la holgura de 1,5×.

| Tamaño | Modelo (calidad ≥ 3) | Costo | **Precio 90 %** | Modelo (calidad ≥ 4, para código) | Costo | **Precio 90 %** |
|---|---|---:|---:|---|---:|---:|
| Landing | Haiku 5.5 | 0,52 | **US$ 5,25** | Sonnet 5 | 10,50 | **US$ 105** |
| App sencilla | Haiku 5.5 | 2,62 | **US$ 26,25** | Sonnet 5 | 52,50 | **US$ 525** |
| Plataforma | Haiku 5.5 | 8,25 | **US$ 82,50** | Sonnet 5 | 165 | **US$ 1.650** |
| *Referencia: Kimi k2.6 directo (cómo se cotiza hoy)* | | 4,65 / 23,25 / 72,75 | US$ 46,50 / 232,50 / 727,50 | | | |

**La decisión que no puedo tomar yo:** ¿el código de un MVP puede hacerse con un modelo de calidad 3? Es 20 veces más barato, pero no está probado. El catálogo exige calidad 4 para `codigo_mvp`. Para bajarla hay que construir el mismo MVP con Haiku 5.5, Kimi y Sonnet, y comparar con una rúbrica (¿corre?, ¿cumple lo pedido?, ¿cuántas correcciones?). Mientras no se haga, la cotización honesta con calidad 4 es la de la derecha.

## 4. Modo inteligente

`LLM_SMART_ROUTING=true` (apagado por defecto). El enrutador elige, entre los proveedores con clave, **el modelo más barato que cumple la tarea**:

| Tarea | Calidad mínima | Capacidad | Hoy elegiría (con todas las claves) |
|---|---:|---|---|
| clasificar, resumir, respuesta rápida | 2 | JSON | DeepSeek v4 flash |
| conversación, documento, visión | 3 | visión para visión | Haiku 5.5 |
| decisión (votos del Board, Gate) | 4 | JSON | Sonnet 5 |
| código del MVP | 4 | herramientas | Sonnet 5 |
| imagen borrador / imagen final | 2 / 4 | — | gpt-5-image-mini (~US$ 0,01) / Gemini 3.1 flash image (~US$ 0,08) |
| video | 3 | — | **ninguno**: OpenRouter no lista modelos de video |

Reglas: no baja la calidad en silencio (si nada cumple, falla y se usa la configuración fija), no usa proveedores sin clave y Ollama solo sirve para lo simple. El costo real de cada llamada queda en `llm_usage`, así que el ahorro se mide, no se supone.

**Cómo encenderlo con seguridad:** (1) poner `OPENROUTER_API_KEY`; (2) correr `scripts/refresh_catalog.py` para precios al día; (3) evaluar Haiku 5.5 contra Kimi en conversación y Board con 10 casos reales; (4) `LLM_SMART_ROUTING=true`; (5) vigilar `llm-usage` una semana.

**Pendiente:** generación de imagen y video no tiene adaptador (el catálogo ya los cotiza); el costo de infraestructura por Nivel hay que medirlo en producción.
