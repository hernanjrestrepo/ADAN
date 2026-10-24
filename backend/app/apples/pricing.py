"""Precio de cada Nivel en @pples: todo el costo de prestarlo dividido entre 0,10 (margen bruto del 90 %).

El costo por llamada sale de lo medido con Kimi en el piloto de Xmart Travel (tabla `llm_usage`, oct-2026): una
llamada estructurada cuesta ~USD 0,0061, una con búsqueda en internet ~USD 0,034 y un documento largo ~USD 0,05.
Cada Nivel se estima con las llamadas que de verdad hace ADÁN en él (conversación, Board de 7 roles dos veces,
búsquedas, documentos), con un factor de holgura por reintentos y segundas vueltas.

"Todo costo" incluye lo que se va con cada venta: la comisión de Wompi y el 3,5 % de referidos. Como esos dos son
un porcentaje del precio, el precio se despeja así:  precio = (costo directo + fijo de pasarela) / (0,10 − % variables).
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
TARGET_COST_SHARE = 0.10     # el costo es el 10 % del precio: margen del 90 %
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
    direct_usd: float
    gateway_usd: float
    referral_usd: float
    total_cost_usd: float
    apples: int
    margin: float


def level_price(level: int) -> LevelPrice:
    calls = LEVEL_CALLS[level]
    llm = sum(CALL_COST_USD[k] * n for k, n in calls.items()) * SAFETY_FACTOR
    direct = llm + INFRA_USD_PER_LEVEL
    variable = gateway_rate() + REFERRAL_RATE * REFERRAL_DEPTH
    raw = (direct + gateway_fixed_usd()) / (TARGET_COST_SHARE - variable)
    apples = int(math.ceil(raw))
    gateway = apples * gateway_rate() + gateway_fixed_usd()
    referral = apples * REFERRAL_RATE * REFERRAL_DEPTH
    total = direct + gateway + referral
    return LevelPrice(level=level, name=LEVEL_NAMES[level], llm_usd=round(llm, 3), infra_usd=INFRA_USD_PER_LEVEL,
                      direct_usd=round(direct, 3), gateway_usd=round(gateway, 3), referral_usd=round(referral, 3),
                      total_cost_usd=round(total, 3), apples=apples, margin=round(1 - total / apples, 4))


def price_table() -> dict:
    levels = [level_price(n) for n in range(1, 8)]
    return {
        "levels": [asdict(p) for p in levels],
        "total_apples": sum(p.apples for p in levels),
        "assumptions": {
            "call_cost_usd": CALL_COST_USD, "safety_factor": SAFETY_FACTOR, "infra_usd_per_level": INFRA_USD_PER_LEVEL,
            "target_cost_share": TARGET_COST_SHARE, "gateway_rate": round(gateway_rate(), 4),
            "gateway_fixed_usd": round(gateway_fixed_usd(), 3), "referral_rate": REFERRAL_RATE,
            "referral_depth": REFERRAL_DEPTH, "trm": settings.APPLE_TRM,
        },
    }


def apples_for(level: int) -> int:
    return level_price(level).apples
