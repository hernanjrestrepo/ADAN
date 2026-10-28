"""Precio de cada Nivel: se fija en dólares y se cobra en @pples (US$ 1 = 1.000 @pples).

Costo: lo que cuesta prestar el Nivel, redondeado hacia arriba a un decimal. El costo por llamada sale de lo medido
con Kimi en el piloto de Xmart Travel (tabla `llm_usage`, oct-2026): una llamada estructurada ~USD 0,0061, una con
búsqueda en internet ~USD 0,034 y un documento largo ~USD 0,05, con holgura por reintentos y segundas vueltas.

Precio: lo fija Hernán. El 2026-10-24 eran 95 @pples de US$ 1; el 2026-10-29 pasó a US$ 45 los 7 Niveles, repartidos
en la misma proporción y con US$ 1 = 1.000 @pples. El desarrollo del MVP, el dominio, el servidor y demás servicios
se cotizan aparte (costo ÷ 0,10, es decir, un margen del 90 %).
"""
from __future__ import annotations

import math
from dataclasses import asdict, dataclass

from app.core.config import settings

# Costo promedio medido por tipo de llamada (USD)
CALL_COST_USD = {"llamada": 0.0061, "busqueda": 0.034, "documento": 0.05}

# Llamadas que hace ADÁN en cada Nivel (por empresa)
LEVEL_CALLS: dict[int, dict[str, int]] = {
    1: {"llamada": 54, "busqueda": 5, "documento": 1},   # guion de 7 temas, documentos, Board x2, encuesta, Gate
    2: {"llamada": 43, "busqueda": 6, "documento": 1},   # propuesta de valor y prueba de humo
    3: {"llamada": 42, "busqueda": 8, "documento": 4},   # nombre y dominio, ruta legal, estatutos, flujo de caja
    4: {"llamada": 46, "busqueda": 3, "documento": 3},   # MVP o landing
    5: {"llamada": 59, "busqueda": 6, "documento": 2},   # validación simulada y La Arena (dos rondas)
    6: {"llamada": 41, "busqueda": 6, "documento": 2},   # lanzamiento
    7: {"llamada": 41, "busqueda": 6, "documento": 2},   # escalamiento
}
LEVEL_NAMES = {1: "El Dolor", 2: "Propuesta de Valor", 3: "Plan de Negocios", 4: "MVP", 5: "Validación Simulada",
               6: "Lanzamiento", 7: "Escalamiento"}

SAFETY_FACTOR = 1.5          # reintentos, segundas sesiones del Board, preguntas de más
INFRA_USD_PER_LEVEL = 0.60   # servidor, base de datos, memoria vectorial y almacenamiento de documentos
TARGET_COST_SHARE = 0.10     # el costo es el 10 % del precio en lo que se cotiza aparte (MVP construido)
APPLES_PER_USD = settings.APPLES_PER_USD
TARGET_MARGIN = 0.90          # la meta de utilidad sobre el costo de prestar el Nivel
# Precio de cada Nivel en dólares: 45 en total, en la proporción 5:10:20:15:15:15:15 de la tabla anterior
LEVEL_USD = {1: 2.50, 2: 5.00, 3: 9.50, 4: 7.00, 5: 7.00, 6: 7.00, 7: 7.00}
LEVEL_APPLES = {n: round(usd * APPLES_PER_USD) for n, usd in LEVEL_USD.items()}
REFERRAL_RATE = 0.005        # por nivel de la red
REFERRAL_DEPTH = 7           # el nivel 1 es quien invitó directamente


def gateway_rate() -> float:
    """Comisión porcentual de Wompi con IVA."""
    return settings.WOMPI_FEE_RATE * (1 + settings.IVA_RATE)


def gateway_fixed_usd() -> float:
    return settings.WOMPI_FEE_FIXED_COP * (1 + settings.IVA_RATE) / settings.APPLE_TRM


@dataclass
class LevelPrice:
    level: int
    name: str
    llm_usd: float
    infra_usd: float
    cost_usd: float          # redondeado hacia arriba a un decimal
    price_usd: float
    apples: int
    profit_usd: float
    margin: float            # sobre el costo de prestar el Nivel
    margin_gap: float        # cuánto falta (en puntos) para la meta del 90 %; 0 si ya se cumple
    gateway_usd: float       # comisión de Wompi si el Nivel se pagara en una compra aparte
    referral_usd: float      # 3,5 % de la red
    margin_after_fees: float


def level_cost(level: int) -> tuple[float, float]:
    calls = LEVEL_CALLS[level]
    llm = sum(CALL_COST_USD[k] * n for k, n in calls.items()) * SAFETY_FACTOR
    return llm, math.ceil(round((llm + INFRA_USD_PER_LEVEL) * 10, 6)) / 10


def level_price(level: int) -> LevelPrice:
    llm, cost = level_cost(level)
    usd = LEVEL_USD[level]
    gateway = usd * gateway_rate() + gateway_fixed_usd()
    referral = usd * REFERRAL_RATE * REFERRAL_DEPTH
    margin = 1 - cost / usd
    return LevelPrice(level=level, name=LEVEL_NAMES[level], llm_usd=round(llm, 3), infra_usd=INFRA_USD_PER_LEVEL,
                      cost_usd=cost, price_usd=usd, apples=LEVEL_APPLES[level], profit_usd=round(usd - cost, 2),
                      margin=round(margin, 4), margin_gap=round(max(0.0, TARGET_MARGIN - margin), 4),
                      gateway_usd=round(gateway, 3), referral_usd=round(referral, 3),
                      margin_after_fees=round(1 - (cost + gateway + referral) / usd, 4))


def mvp_quote(input_tokens: int, output_tokens: int) -> dict:
    """Cotización del MVP construido (aparte del Nivel 4): costo de tokens con holgura, dividido entre 0,10."""
    from app.core.config import settings as s
    cost = (input_tokens * s.KIMI_PRICE_INPUT + output_tokens * s.KIMI_PRICE_OUTPUT) / 1_000_000 * SAFETY_FACTOR
    price_usd = cost / TARGET_COST_SHARE
    return {"cost_usd": round(cost, 2), "price_usd": round(price_usd, 2),
            "apples": int(math.ceil(price_usd * APPLES_PER_USD))}


def price_table() -> dict:
    levels = [level_price(n) for n in range(1, 8)]
    revenue = round(sum(p.price_usd for p in levels), 2)
    cost = round(sum(p.cost_usd for p in levels), 2)
    fees = sum(p.gateway_usd + p.referral_usd for p in levels)
    return {
        "levels": [asdict(p) for p in levels],
        "apples_per_usd": APPLES_PER_USD,
        "target_margin": TARGET_MARGIN,
        "total_usd": revenue,
        "total_apples": sum(p.apples for p in levels),
        "total_cost_usd": cost,
        "total_profit_usd": round(revenue - cost, 2),
        "margin": round(1 - cost / revenue, 4),
        "margin_after_fees": round(1 - (cost + fees) / revenue, 4),
        "apart": ["Desarrollo del MVP listo (según tokens, costo ÷ 0,10)", "Dominio", "Servidor", "Otros servicios de Paradixe"],
        "mvp_examples": {"landing": mvp_quote(2_000_000, 300_000), "app": mvp_quote(10_000_000, 1_500_000)},
        "assumptions": {
            "call_cost_usd": CALL_COST_USD, "safety_factor": SAFETY_FACTOR, "infra_usd_per_level": INFRA_USD_PER_LEVEL,
            "gateway_rate": round(gateway_rate(), 4), "gateway_fixed_usd": round(gateway_fixed_usd(), 3),
            "referral_rate": REFERRAL_RATE, "referral_depth": REFERRAL_DEPTH, "trm": settings.APPLE_TRM,
        },
    }


def apples_for(level: int) -> int:
    return LEVEL_APPLES[level]


def usd_to_apples(usd: float) -> int:
    return round(usd * APPLES_PER_USD)


def apples_to_usd(apples: float) -> float:
    return apples / APPLES_PER_USD
