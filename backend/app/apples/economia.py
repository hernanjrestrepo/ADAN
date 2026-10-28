"""Economía de ADÁN: cuánto cuesta un caso y qué margen deja (meta: 90 %).

Parte de lo medido en el piloto de Xmart Travel (`pricing.CALL_COST_USD`, con Kimi) y lo reexpresa con el precio
de cualquier modelo del catálogo (`app/ai/catalog.py`). Es una ESTIMACIÓN por razón de precios: supone los
mismos tokens por llamada que midió Kimi; otro modelo puede gastar más o menos tokens, y su calidad se valida
con evaluaciones antes de usarlo.
"""
from __future__ import annotations

from app.ai import catalog
from app.apples import pricing
from app.core.config import settings

# Tokens de un MVP construido por Genexis (entrada, salida). Landing y app: los supuestos de `pricing`; plataforma:
# estimación de Paradixe, sin medir.
MVP_SIZES = {"landing": (2_000_000, 300_000), "app": (10_000_000, 1_500_000), "plataforma": (30_000_000, 5_000_000)}
TASK_MIX = (3, 1)   # relación entrada:salida de una llamada típica de conversación, para comparar precios


def blended_ratio(spec: catalog.ModelSpec) -> float:
    """Cuánto cuesta una llamada típica con `spec` frente a Kimi (el modelo con el que se midió el piloto)."""
    kimi = (TASK_MIX[0] * settings.KIMI_PRICE_INPUT + TASK_MIX[1] * settings.KIMI_PRICE_OUTPUT)
    return (TASK_MIX[0] * spec.input_per_m + TASK_MIX[1] * spec.output_per_m) / kimi


def mvp_case(size: str, spec: catalog.ModelSpec, margin: float = pricing.TARGET_MARGIN) -> dict:
    tokens_in, tokens_out = MVP_SIZES[size]
    cost = catalog.estimate_cost(spec, tokens_in, tokens_out) * pricing.SAFETY_FACTOR
    price = cost / (1 - margin)
    return {"size": size, "model": spec.id, "quality": spec.quality, "cost_usd": round(cost, 2),
            "price_usd": round(price, 2), "apples": round(price * pricing.APPLES_PER_USD)}


def mvp_cases(providers: set[str] | None = None) -> list[dict]:
    """Cada tamaño de MVP con el modelo más barato de calidad 3 y de calidad 4 (código)."""
    rows = []
    for size in MVP_SIZES:
        for floor in (3, 4):
            task = catalog.Task(floor, needs=("tools",), input_tokens=MVP_SIZES[size][0],
                                output_tokens=MVP_SIZES[size][1])
            choice = catalog.select(task, providers=providers)
            rows.append({**mvp_case(size, choice.spec), "min_quality": floor})
    return rows


def seven_levels(spec: catalog.ModelSpec | None = None, infra_per_level: float | None = None,
                 price_usd: float | None = None) -> dict:
    """Costo y margen de los 7 Niveles con otro modelo y/o otra infraestructura por Nivel."""
    ratio = 1.0 if spec is None else blended_ratio(spec)
    infra = pricing.INFRA_USD_PER_LEVEL if infra_per_level is None else infra_per_level
    price = sum(pricing.LEVEL_USD.values()) if price_usd is None else price_usd
    llm = sum(pricing.level_cost(n)[0] for n in range(1, 8)) * ratio
    cost = llm + infra * 7
    fees = price * (pricing.gateway_rate() + pricing.REFERRAL_RATE * pricing.REFERRAL_DEPTH) + pricing.gateway_fixed_usd()
    return {"model": spec.id if spec else "kimi (medido en el piloto)", "llm_usd": round(llm, 2),
            "infra_usd": round(infra * 7, 2), "cost_usd": round(cost, 2), "price_usd": price,
            "margin": round(1 - cost / price, 4), "margin_after_fees": round(1 - (cost + fees) / price, 4),
            "meets_target": 1 - cost / price >= pricing.TARGET_MARGIN}


def infra_for_target(spec: catalog.ModelSpec | None = None, price_usd: float | None = None) -> float:
    """Cuánta infraestructura por Nivel (USD) admite la meta del 90 % con ese modelo; negativo = imposible."""
    price = sum(pricing.LEVEL_USD.values()) if price_usd is None else price_usd
    ratio = 1.0 if spec is None else blended_ratio(spec)
    llm = sum(pricing.level_cost(n)[0] for n in range(1, 8)) * ratio
    return round((price * (1 - pricing.TARGET_MARGIN) - llm) / 7, 3)
