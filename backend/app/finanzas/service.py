"""Finanzas y estrategia: organigrama híbrido (personas, agentes de ADAN y servicios de Paradixe), supuestos
financieros contrastados con benchmarks y el informe ejecutivo (estilo consultora: la respuesta primero).
"""
from __future__ import annotations

import json
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.ai.base import LLMAdapter, LLMMessage
from app.ai.normalize import normalize_list, normalize_string
from app.ai.router import for_tier
from app.finanzas import modelo
from app.models.models import Company, Document, Project

# Servicios del ecosistema Paradixe que pueden ocupar un rol de la empresa (AD-000 v2.0).
# Precios de Paradixe (Hernán, 2026-10-24): EVA, BPO y Omnicanal cobran USD 0,10 por minuto, con descuento por volumen,
# e incluyen LLM, marcador, PBX, análisis inteligente, voz, transcripción, grabaciones y asesoría. La membresía mensual
# de USD 100 incluye el CRM y las demás plataformas. Agentes por tiempo, Genexis y CSI van como estimado de mercado.
PER_MINUTE_USD = 0.10
PER_MINUTE_SERVICES = ("EVA", "BPO Paradixe", "Omnicanal")
MEMBERSHIP_USD = 100.0
MEMBERSHIP = "Membresía Paradixe"
# Respaldo si el modelo no da la tasa de cambio (moneda local por 1 USD, referencia de octubre de 2026)
FX_FALLBACK = {"USD": 1.0, "COP": 4000.0, "MXN": 18.5, "EUR": 0.92, "PEN": 3.75, "CLP": 950.0, "ARS": 1200.0, "BRL": 5.5}
PARADIXE_SERVICES = {
    "EVA": "Ventas y marketing con IA: campañas inbound y outbound, voz, agentes conversacionales y seguimiento comercial. "
           "USD 0,10 por minuto.",
    "Omnicanal": "Atención al cliente en WhatsApp, web, redes y teléfono con un mismo agente de IA, 24/7, que escala a una "
                 "persona. USD 0,10 por minuto.",
    "BPO Paradixe": "Procesos tercerizados operados por agentes y personas: contabilidad, facturación, nómina, cobranza, "
                    "soporte, llamadas. USD 0,10 por minuto.",
    "Agentes por tiempo": "Agentes de ADAN por hora, día, semana o mes: investigación, análisis financiero, redacción, operaciones.",
    "Genexis": "Construcción del MVP y del software de la empresa (Nivel 4).",
    "CSI": "Inteligencia de mercado: competencia, regulación, tendencias y benchmarks.",
}
ROLE_TYPES = ("humano", "agente_adan", "servicio_paradixe")

ORG_SCHEMA = {
    "type": "object", "additionalProperties": False, "required": ["moneda", "tasa_usd", "resumen", "roles"],
    "properties": {
        "moneda": {"type": "string"},
        "tasa_usd": {"type": "number"},
        "resumen": {"type": "string"},
        "roles": {"type": "array", "items": {
            "type": "object", "additionalProperties": False,
            "required": ["area", "cargo", "tipo", "servicio", "responsabilidades", "desde_mes", "minutos_mes",
                         "costo_mensual", "costo_humano_equivalente", "por_que"],
            "properties": {"area": {"type": "string"}, "cargo": {"type": "string"},
                           "tipo": {"type": "string", "enum": list(ROLE_TYPES)},
                           "servicio": {"type": "string"}, "responsabilidades": {"type": "array", "items": {"type": "string"}},
                           "desde_mes": {"type": "integer"}, "minutos_mes": {"type": "number"},
                           "costo_mensual": {"type": "number"},
                           "costo_humano_equivalente": {"type": "number"}, "por_que": {"type": "string"}}}},
    },
}

_LINE = {"type": "object", "additionalProperties": False, "required": ["concepto", "monto", "mes", "base"],
         "properties": {"concepto": {"type": "string"}, "monto": {"type": "number"}, "mes": {"type": "integer"},
                        "base": {"type": "string"}}}
ASSUMPTIONS_SCHEMA = {
    "type": "object", "additionalProperties": False,
    "required": ["moneda", "unidad", "precio_unitario", "mes_inicio_ventas", "unidades_mes_1", "crecimiento_mensual_pct",
                 "unidades_max_mes",
                 "costo_variable_pct", "comision_pagos_pct", "marketing_mensual", "impuesto_renta_pct", "capital_inicial",
                 "gastos_fijos_adicionales", "capex", "bases", "advertencias"],
    "properties": {
        "moneda": {"type": "string"}, "unidad": {"type": "string"}, "precio_unitario": {"type": "number"},
        "mes_inicio_ventas": {"type": "integer"}, "unidades_mes_1": {"type": "number"},
        "crecimiento_mensual_pct": {"type": "number"},
        "unidades_max_mes": {"type": "number"}, "costo_variable_pct": {"type": "number"},
        "comision_pagos_pct": {"type": "number"}, "marketing_mensual": {"type": "number"},
        "impuesto_renta_pct": {"type": "number"}, "capital_inicial": {"type": "number"},
        "gastos_fijos_adicionales": {"type": "array", "items": _LINE},
        "capex": {"type": "array", "items": _LINE},
        "bases": {"type": "object", "additionalProperties": {"type": "string"}},
        "advertencias": {"type": "array", "items": {"type": "string"}},
    },
}

REPORT_SCHEMA = {
    "type": "object", "additionalProperties": False,
    "required": ["titulo", "respuesta", "scqa", "argumentos", "lean_canvas", "benchmark", "riesgos", "six_sigma",
                 "plan_90_dias", "recomendacion"],
    "properties": {
        "titulo": {"type": "string"},
        "respuesta": {"type": "string"},
        "scqa": {"type": "object", "additionalProperties": False, "required": ["situacion", "complicacion", "pregunta", "respuesta"],
                 "properties": {k: {"type": "string"} for k in ("situacion", "complicacion", "pregunta", "respuesta")}},
        "argumentos": {"type": "array", "items": {"type": "object", "additionalProperties": False, "required": ["titulo", "evidencia"],
                                                   "properties": {"titulo": {"type": "string"},
                                                                  "evidencia": {"type": "array", "items": {"type": "string"}}}}},
        "lean_canvas": {"type": "object", "additionalProperties": False,
                        "required": ["problema", "segmentos", "propuesta_unica", "solucion", "canales", "ingresos", "costos",
                                     "metricas_clave", "ventaja_injusta"],
                        "properties": {k: {"type": "string"} for k in ("problema", "segmentos", "propuesta_unica", "solucion",
                                                                       "canales", "ingresos", "costos", "metricas_clave",
                                                                       "ventaja_injusta")}},
        "benchmark": {"type": "array", "items": {"type": "object", "additionalProperties": False,
                                                  "required": ["competidor", "fortalezas", "debilidades", "como_ganarle"],
                                                  "properties": {k: {"type": "string"} for k in ("competidor", "fortalezas",
                                                                                                  "debilidades", "como_ganarle")}}},
        "riesgos": {"type": "array", "items": {"type": "object", "additionalProperties": False,
                                                "required": ["riesgo", "probabilidad", "impacto", "mitigacion"],
                                                "properties": {"riesgo": {"type": "string"},
                                                               "probabilidad": {"type": "string", "enum": ["alta", "media", "baja"]},
                                                               "impacto": {"type": "string", "enum": ["alto", "medio", "bajo"]},
                                                               "mitigacion": {"type": "string"}}}},
        "six_sigma": {"type": "object", "additionalProperties": False, "required": ["ctq", "definir", "medir", "analizar", "mejorar", "controlar"],
                      "properties": {"ctq": {"type": "array", "items": {"type": "string"}},
                                     **{k: {"type": "string"} for k in ("definir", "medir", "analizar", "mejorar", "controlar")}}},
        "plan_90_dias": {"type": "array", "items": {"type": "object", "additionalProperties": False,
                                                     "required": ["semanas", "accion", "responsable", "entregable"],
                                                     "properties": {k: {"type": "string"} for k in ("semanas", "accion",
                                                                                                     "responsable", "entregable")}}},
        "recomendacion": {"type": "string"},
    },
}

CFO = ("Eres el CFO de ADAN. Tus cifras se contrastan con datos reales del sector y del país: nada de soñar con cifras "
       "que no son. Eres conservador: ante la duda, menos ventas y más costos. Cada supuesto dice de dónde sale. "
       "Explicas para alguien que no sabe de finanzas. Español.")
STRATEGIST = ("Eres el socio de estrategia de ADAN y escribes como una consultora de primer nivel: principio de la "
              "pirámide (la respuesta primero, luego los argumentos con evidencia), frases cortas, cifras concretas, cero "
              "relleno. Usas Lean Startup, Lean Canvas, Six Sigma (DMAIC) y benchmark. Eres honesto: si la empresa no está "
              "lista, lo dices y dices qué falta. Español, de tú.")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class Finanzas:
    def __init__(self, llm: LLMAdapter | None, db: Session):
        self.llm = for_tier(llm, "complex") if llm is not None else None
        self.db = db

    # --- documentos guardados ---

    def _latest(self, project: Project, doc_type: str) -> dict | None:
        doc = self.db.query(Document).filter(Document.project_id == project.id, Document.doc_type == doc_type) \
            .order_by(Document.created_at.desc()).first()
        return json.loads(doc.content) if doc and doc.content else None

    def _save(self, project: Project, doc_type: str, title: str, data: dict) -> dict:
        self.db.add(Document(project_id=project.id, title=title[:255], doc_type=doc_type, origin="generated_by_adan",
                             content=json.dumps(data, ensure_ascii=False)))
        self.db.commit()
        return data

    def org(self, project: Project) -> dict | None:
        return self._latest(project, "org_chart")

    def model(self, project: Project) -> dict | None:
        return self._latest(project, "financial_model")

    def report(self, project: Project) -> dict | None:
        return self._latest(project, "executive_report")

    # --- organigrama híbrido ---

    async def build_org(self, project: Project, context: str) -> dict:
        catalog = "\n".join(f"- {k}: {v}" for k, v in PARADIXE_SERVICES.items())
        prompt = (f"{context}\n\nDiseña el organigrama de esta empresa para sus primeros 24 meses, como organización híbrida "
                  "eficiente. Cada rol es de uno de tres tipos: `humano` (lo que exige criterio, relaciones, firma legal o "
                  "trabajo físico), `agente_adan` (tareas repetibles de conocimiento que hace un agente de IA de ADAN) o "
                  "`servicio_paradixe` (cuando un servicio del ecosistema cubre el rol mejor que contratar):\n"
                  f"{catalog}\n\nReglas: no reemplaces con IA lo que exige una persona (dirección, ventas complejas, "
                  "responsabilidad legal, oficio físico). `servicio`: el nombre exacto del servicio de Paradixe, o vacío. "
                  "`desde_mes`: cuándo hace falta el rol (1 a 24): no contrates todo desde el día uno. `moneda`: el código "
                  "ISO de la moneda del país donde opera la empresa (COP, MXN, USD…); TODOS los costos van en esa moneda. "
                  "`tasa_usd`: cuántas unidades de esa moneda vale 1 USD hoy. `minutos_mes`: para EVA, BPO Paradixe y "
                  "Omnicanal, los minutos de atención, llamadas o voz que el rol consumiría al mes (realista para el volumen "
                  "de esta empresa; 0 en los demás roles): su costo lo calcula el sistema a USD 0,10 por minuto. "
                  "`costo_mensual`: salario con prestaciones para humanos y un estimado de mercado para agentes por tiempo, "
                  "Genexis y CSI. La membresía de Paradixe (USD 100 al mes, CRM y plataformas) la agrega el sistema: no la "
                  "pongas como rol. "
                  "`costo_humano_equivalente`: lo que costaría ese rol con una persona (igual al costo si es humano). "
                  "`por_que`: una frase que diga qué costo o riesgo reduce y qué oportunidad abre. Usa SIEMPRE la IA y "
                  "los servicios de Paradixe donde aporten: por ejemplo, EVA en ventas y marketing baja el costo de "
                  "adquirir clientes (CAC) y escala sin contratar un equipo comercial grande; el BPO convierte costos "
                  "fijos en variables. `resumen`: en 3 a 4 frases, cómo queda la organización, cuánto ahorra frente a "
                  "hacerlo todo con personas, cómo baja el riesgo y cómo mejora el CAC y la escalabilidad. "
                  "Entre 6 y 14 roles.")
        resp = await self.llm.chat_json([LLMMessage("system", CFO), LLMMessage("user", prompt)], ORG_SCHEMA,
                                        temperature=0.3, max_tokens=5000)
        data = resp.parsed if isinstance(resp.parsed, dict) else {}
        currency = (normalize_string(data.get("moneda")) or "COP")[:5].upper()
        fx = float(data.get("tasa_usd") or 0) or FX_FALLBACK.get(currency, 0.0) or 1.0
        roles = []
        for r in data.get("roles") or []:
            if not isinstance(r, dict) or not normalize_string(r.get("cargo")):
                continue
            kind = r.get("tipo") if r.get("tipo") in ROLE_TYPES else "humano"
            service = normalize_string(r.get("servicio")) if kind == "servicio_paradixe" else ""
            if service.lower().startswith("membres"):
                continue  # la membresía la agrega el sistema una sola vez
            per_minute = next((s for s in PER_MINUTE_SERVICES if s.lower() in service.lower()), None)
            minutes = max(0.0, float(r.get("minutos_mes") or 0)) if per_minute else 0.0
            if per_minute:
                cost = minutes * PER_MINUTE_USD * fx
                price = f"USD {PER_MINUTE_USD:.2f} por minuto × {minutes:,.0f} min al mes (descuento por volumen)"
            else:
                cost = max(0.0, float(r.get("costo_mensual") or 0))
                price = "salario de mercado con prestaciones" if kind == "humano" else "estimado de mercado; se cotiza con Paradixe"
            roles.append({"area": normalize_string(r.get("area")) or "General", "cargo": normalize_string(r.get("cargo")),
                          "tipo": kind, "servicio": service, "responsabilidades": normalize_list(r.get("responsabilidades"))[:5],
                          "desde_mes": int(min(24, max(1, int(r.get("desde_mes") or 1)))), "minutos_mes": minutes,
                          "costo_mensual": round(cost), "por_que": normalize_string(r.get("por_que")), "precio": price,
                          "costo_humano_equivalente": round(max(cost, float(r.get("costo_humano_equivalente") or cost)))})
        if not roles:
            raise ValueError("No se pudo diseñar el organigrama esta vez; intenta de nuevo en un momento.")
        paradixe = [r for r in roles if r["tipo"] != "humano"]
        if paradixe:
            fee = round(MEMBERSHIP_USD * fx)
            roles.append({"area": "Plataformas", "cargo": "Membresía Paradixe: CRM y plataformas", "tipo": "servicio_paradixe",
                          "servicio": MEMBERSHIP, "responsabilidades": ["CRM", "Acceso a las plataformas de Paradixe"],
                          "desde_mes": min(r["desde_mes"] for r in paradixe), "minutos_mes": 0.0, "costo_mensual": fee,
                          "costo_humano_equivalente": fee, "por_que": "Incluye el CRM y todas las plataformas del ecosistema.",
                          "precio": f"USD {MEMBERSHIP_USD:.0f} al mes"})
        hybrid = sum(r["costo_mensual"] for r in roles)
        human = sum(r["costo_humano_equivalente"] for r in roles)
        org = {"moneda": currency, "tasa_usd": fx,
               "resumen": normalize_string(data.get("resumen")), "roles": roles, "generated_at": _now(),
               "costo_mensual_total": round(hybrid), "costo_todo_humano": round(human),
               "ahorro_mensual": round(human - hybrid), "ahorro_pct": round(100 * (human - hybrid) / human, 1) if human else 0}
        return self._save(project, "org_chart", "Organigrama híbrido", org)

    # --- supuestos y flujo de caja ---

    async def build_model(self, project: Project, context: str) -> dict:
        org = self.org(project)
        org_lines = "\n".join(f"- {r['cargo']} ({r['tipo']}{', ' + r['servicio'] if r['servicio'] else ''}): "
                              f"{r['costo_mensual']:.0f} al mes desde el mes {r['desde_mes']}" for r in (org or {}).get("roles", []))
        research, searched = "", False
        search = getattr(self.llm, "chat_search", None)
        if search is not None:
            r = await search([LLMMessage("system", CFO), LLMMessage("user",
                              f"{context}\n\nBusca benchmarks reales del sector y del país de esta empresa: precio promedio, "
                              "margen bruto y costo variable típicos, costo de adquisición de clientes, crecimiento mensual "
                              "realista de un negocio nuevo, comisiones de pasarelas de pago, tarifa de impuesto de renta "
                              "aplicable y costos de arriendo y servicios. Cita las fuentes.")], max_tokens=5000)
            research, searched = r.content, bool(r.metadata.get("searched"))
        currency = (org or {}).get("moneda")
        prompt = (f"{context}\n\n" + (f"Benchmarks investigados:\n{research[:8000]}\n\n" if research else "")
                  + (f"MONEDA OBLIGATORIA: {currency}. Todos los valores (precio, gastos, marketing, capital) van en {currency}; "
                     "si un dato está en otra moneda, conviértelo con la tasa vigente y dilo en su base.\n\n" if currency else "")
                  + (f"El organigrama ya cuesta esto (entra solo al modelo, NO lo repitas en gastos fijos):\n{org_lines}\n\n" if org_lines else "")
                  + "Propón los supuestos del flujo de caja a 24 meses. Sé conservador. `unidad`: qué se vende (ej. "
                    "'suscripción mensual'). `mes_inicio_ventas`: el mes (1 a 24) en que realistamente llega la primera venta "
                    "(si es una idea sin validar, no antes de que termine la validación). `unidades_mes_1`: unidades vendidas "
                    "en ese primer mes de ventas (mayor que 0). `crecimiento_mensual_pct`: realista para una empresa nueva en "
                    "este mercado. `unidades_max_mes`: el techo de capacidad. "
                    "`costo_variable_pct`: % del precio. `gastos_fijos_adicionales`: arriendo, servicios, software, "
                    "contador, seguros… (no repitas el organigrama), con `monto` mensual, `mes` de inicio y `base`. `capex`: "
                    "inversiones únicas con su mes. `capital_inicial`: lo que el fundador dice tener, o 0 si no se sabe. "
                    "`bases`: para cada supuesto numérico, de dónde sale: 'dato del cliente: …', 'benchmark: … (fuente)' o "
                    "'supuesto: …'. `advertencias`: los supuestos más frágiles que hay que validar primero.")
        resp = await self.llm.chat_json([LLMMessage("system", CFO), LLMMessage("user", prompt)], ASSUMPTIONS_SCHEMA,
                                        temperature=0.2, max_tokens=5000)
        a = resp.parsed if isinstance(resp.parsed, dict) else {}
        if not a:
            raise ValueError("No se pudieron proponer los supuestos esta vez; intenta de nuevo en un momento.")
        fixed = [{"concepto": f"{r['cargo']} ({'persona' if r['tipo'] == 'humano' else r['servicio'] or 'agente ADAN'})",
                  "monto_mensual": r["costo_mensual"], "desde_mes": r["desde_mes"], "tipo": r["tipo"],
                  "base": "organigrama híbrido"} for r in (org or {}).get("roles", [])]
        fixed += [{"concepto": g.get("concepto"), "monto_mensual": g.get("monto"), "desde_mes": g.get("mes") or 1,
                   "tipo": "gasto", "base": g.get("base")} for g in a.get("gastos_fijos_adicionales") or [] if isinstance(g, dict)]
        if currency:
            a["moneda"] = currency
        assumptions = {**{k: a.get(k) for k in ("moneda", "unidad", "precio_unitario", "mes_inicio_ventas", "unidades_mes_1",
                                                "crecimiento_mensual_pct",
                                                "unidades_max_mes", "costo_variable_pct", "comision_pagos_pct", "marketing_mensual",
                                                "impuesto_renta_pct", "capital_inicial", "bases")},
                       "gastos_fijos": fixed,
                       "capex": [{"concepto": c.get("concepto"), "monto": c.get("monto"), "mes": c.get("mes"), "base": c.get("base")}
                                 for c in a.get("capex") or [] if isinstance(c, dict)]}
        result = {**modelo.full(assumptions), "advertencias": normalize_list(a.get("advertencias")),
                  "searched": searched, "generated_at": _now()}
        return self._save(project, "financial_model", "Modelo financiero", result)

    def recompute(self, project: Project, assumptions: dict) -> dict:
        previous = self.model(project) or {}
        result = {**modelo.full(assumptions), "advertencias": previous.get("advertencias", []),
                  "searched": previous.get("searched", False), "generated_at": _now(), "edited": True}
        return self._save(project, "financial_model", "Modelo financiero (editado)", result)

    # --- informe ejecutivo ---

    async def build_report(self, project: Project, context: str, company: Company) -> dict:
        model = self.model(project)
        org = self.org(project)
        extras = []
        if model:
            k = model["base"]["kpis"]
            extras.append(f"Modelo financiero (escenario base, {model['assumptions']['moneda']}): punto de equilibrio en el mes "
                          f"{k['punto_equilibrio_mes'] or 'no se alcanza en 24 meses'}, caja mínima {k['caja_minima']} en el mes "
                          f"{k['caja_minima_mes']}, capital necesario {k['capital_necesario']}, ingresos año 1 {k['ingresos_ano_1']}, "
                          f"año 2 {k['ingresos_ano_2']}. Escenarios: " + json.dumps(model["scenarios"], ensure_ascii=False))
        if org:
            extras.append(f"Organigrama híbrido: {org['resumen']} Costo mensual {org['costo_mensual_total']} vs "
                          f"{org['costo_todo_humano']} todo con personas.")
        for doc_type, label in (("board_minutes", "Última acta del Board"), ("legal_guide", "Ruta legal")):
            doc = self.db.query(Document).filter(Document.project_id == project.id, Document.doc_type == doc_type) \
                .order_by(Document.created_at.desc()).first()
            if doc and doc.content:
                extras.append(f"{label}:\n{doc.content[:2500]}")
        arena = self._latest(project, "arena")
        if arena and arena.get("verdict"):
            extras.append(f"La Arena (inversionistas simulados): {arena['verdict']}")
        prompt = (f"{context}\n\n" + "\n\n".join(extras)
                  + f"\n\nEscribe el informe ejecutivo de {company.name}. `respuesta`: la conclusión principal en 2 o 3 frases "
                    "(¿está lista esta empresa para avanzar?, ¿qué es lo decisivo?). `scqa`: situación, complicación, pregunta "
                    "y respuesta. `argumentos`: 3, cada uno con evidencia concreta (cifras y fuentes de lo que se sabe). "
                    "`lean_canvas`: los 9 bloques, específicos. `benchmark`: 3 o 4 competidores o alternativas reales. "
                    "`riesgos`: 5 a 7 con probabilidad, impacto y mitigación. `six_sigma`: los CTQ (lo crítico para la "
                    "calidad según el cliente) y un ciclo DMAIC aplicado al proceso clave de esta empresa (si es una idea, "
                    "al proceso que debe diseñar para que nazca bien). `plan_90_dias`: 6 a 10 acciones con semanas, "
                    "responsable y entregable. `recomendacion`: qué hacer ahora, sin rodeos.")
        resp = await self.llm.chat_json([LLMMessage("system", STRATEGIST), LLMMessage("user", prompt)], REPORT_SCHEMA,
                                        temperature=0.3, max_tokens=8000)
        data = resp.parsed if isinstance(resp.parsed, dict) else {}
        if not data.get("respuesta"):
            raise ValueError("No se pudo escribir el informe esta vez; intenta de nuevo en un momento.")
        report = {**data, "company": company.name, "generated_at": _now(), "kpis": (model or {}).get("base", {}).get("kpis"),
                  "moneda": (model or {}).get("assumptions", {}).get("moneda")}
        return self._save(project, "executive_report", f"Informe ejecutivo: {company.name}", report)


def report_markdown(r: dict) -> str:
    """El informe en Markdown (para Word)."""
    lines = [f"# {r.get('titulo') or 'Informe ejecutivo'}", "", f"**{r.get('company', '')}** · ADAN by Paradixe", "",
             "## La respuesta", r.get("respuesta", ""), "", "## Situación, complicación, pregunta y respuesta"]
    s = r.get("scqa") or {}
    lines += [f"- **Situación:** {s.get('situacion', '')}", f"- **Complicación:** {s.get('complicacion', '')}",
              f"- **Pregunta:** {s.get('pregunta', '')}", f"- **Respuesta:** {s.get('respuesta', '')}", ""]
    for i, a in enumerate(r.get("argumentos") or [], 1):
        lines += [f"## {i}. {a.get('titulo', '')}"] + [f"- {e}" for e in a.get("evidencia") or []] + [""]
    lc = r.get("lean_canvas") or {}
    lines += ["## Lean Canvas"] + [f"- **{k.replace('_', ' ').capitalize()}:** {v}" for k, v in lc.items()] + [""]
    lines += ["## Benchmark"] + [f"- **{b.get('competidor')}:** fortalezas: {b.get('fortalezas')}; debilidades: "
                                 f"{b.get('debilidades')}; cómo ganarle: {b.get('como_ganarle')}" for b in r.get("benchmark") or []] + [""]
    lines += ["## Riesgos"] + [f"- **{x.get('riesgo')}** (probabilidad {x.get('probabilidad')}, impacto {x.get('impacto')}): "
                               f"{x.get('mitigacion')}" for x in r.get("riesgos") or []] + [""]
    ss = r.get("six_sigma") or {}
    lines += ["## Six Sigma", "- **Crítico para la calidad:** " + "; ".join(ss.get("ctq") or [])]
    lines += [f"- **{k.capitalize()}:** {ss.get(k, '')}" for k in ("definir", "medir", "analizar", "mejorar", "controlar")] + [""]
    lines += ["## Plan de 90 días"] + [f"- **Semanas {p.get('semanas')}:** {p.get('accion')} · {p.get('responsable')} · "
                                       f"entregable: {p.get('entregable')}" for p in r.get("plan_90_dias") or []] + [""]
    lines += ["## Recomendación", r.get("recomendacion", ""), "",
              "ADAN es una inteligencia artificial: este informe orienta y no reemplaza la asesoría profesional."]
    return "\n".join(lines)
