"""Guion del Descubrimiento del Dolor (Nivel 1): siete temas en orden y lo que ADÁN ya entendió.

Antes, la conversación solo dependía de cuántos mensajes llevaba el cliente: ADÁN preguntaba sin
orden, repetía y no dejaba constancia de lo respondido. Ahora cada turno hace dos cosas en una
sola llamada al modelo (salida estructurada):

1. Actualiza el estado de los siete temas con lo que el cliente dijo (resumen en sus palabras y si
   es dato o supuesto), y propone como evidencia solo lo verificable (AD-CMP-05).
2. Responde: confirma lo que entendió y hace UNA pregunta, sobre el primer tema que falte.

El estado queda en los metadatos del mensaje de ADÁN (Registro Permanente): el último es el vigente.
"""
from __future__ import annotations

from copy import deepcopy

TOPICS = [
    ("problema", "El problema", "qué problema concreto existe, dicho en una o dos frases"),
    ("afectados", "A quién le duele", "quién lo sufre: un segmento concreto (tipo de persona o empresa, dónde)"),
    ("momento", "Cuándo y cada cuánto pasa", "en qué situación aparece el problema y con qué frecuencia"),
    ("costo", "Cuánto les cuesta hoy", "qué pierde el afectado: tiempo, dinero, riesgo o frustración, con cifras si existen"),
    ("alternativas", "Cómo lo resuelven hoy", "qué usan hoy en su lugar y por qué no les basta"),
    ("urgencia", "Por qué ahora y si pagarían", "por qué es urgente resolverlo ya y si pagarían por una solución"),
    ("evidencia", "Qué prueba hay", "de dónde sale lo anterior: entrevistas, datos, ventas o fuentes externas"),
]
TOPIC_IDS = [t[0] for t in TOPICS]
STATUSES = ("pendiente", "parcial", "respondido", "sin_dato")
CLOSED = ("respondido", "sin_dato")  # "sin_dato": el cliente no lo sabe; queda como tarea de validación
BASES = ("dato", "supuesto", "desconocida")
MAX_SUMMARY = 300

SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["respuesta", "temas", "evidencia_sugerida"],
    "properties": {
        "respuesta": {"type": "string"},
        "temas": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["id", "estado", "resumen", "base"],
                "properties": {
                    "id": {"type": "string", "enum": TOPIC_IDS},
                    "estado": {"type": "string", "enum": list(STATUSES)},
                    "resumen": {"type": "string"},
                    "base": {"type": "string", "enum": list(BASES)},
                },
            },
        },
        "evidencia_sugerida": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["afirmacion", "tipo", "fuente"],
                "properties": {
                    "afirmacion": {"type": "string"},
                    "tipo": {"type": "string", "enum": ["testimony", "external"]},
                    "fuente": {"type": "string"},
                },
            },
        },
    },
}


def empty_state() -> dict:
    return {"temas": {tid: {"estado": "pendiente", "resumen": "", "base": "desconocida"} for tid in TOPIC_IDS},
            "evidencia_sugerida": []}


def current_state(messages) -> dict:
    """El último estado guardado en la conversación (o uno vacío)."""
    for msg in reversed(messages):
        data = (msg.metadata_json or {}).get("discovery")
        if data:
            state = empty_state()
            state["temas"].update({k: v for k, v in data.get("temas", {}).items() if k in state["temas"]})
            state["evidencia_sugerida"] = list(data.get("evidencia_sugerida", []))
            return state
    return empty_state()


def next_topic(state: dict) -> str | None:
    for tid in TOPIC_IDS:
        if state["temas"][tid]["estado"] not in CLOSED:
            return tid
    return None


def progress(state: dict) -> dict:
    """Lo que la interfaz muestra: cada tema con su estado y resumen, y el siguiente en el guion."""
    topics = [{"id": tid, "label": label, **state["temas"][tid]} for tid, label, _goal in TOPICS]
    done = sum(1 for t in topics if t["estado"] in CLOSED)
    return {"topics": topics, "done": done, "total": len(topics), "next": next_topic(state),
            "complete": done == len(topics), "evidence_suggestions": state["evidencia_sugerida"]}


def merge(state: dict, parsed: dict) -> dict:
    """Aplica lo que devolvió el modelo sin perder lo ya entendido."""
    new = deepcopy(state)
    for item in parsed.get("temas") or []:
        tid = item.get("id")
        if tid not in new["temas"] or item.get("estado") not in STATUSES:
            continue
        old = new["temas"][tid]
        summary = (item.get("resumen") or "").strip()[:MAX_SUMMARY]
        # Un tema respondido no vuelve a "pendiente" porque el modelo lo omitió en este turno
        if old["estado"] in CLOSED and item["estado"] == "pendiente" and not summary:
            continue
        new["temas"][tid] = {"estado": item["estado"], "resumen": summary or old["resumen"],
                             "base": item.get("base") if item.get("base") in BASES else old["base"]}
    seen = {e["afirmacion"].strip().lower() for e in new["evidencia_sugerida"]}
    for ev in parsed.get("evidencia_sugerida") or []:
        claim = (ev.get("afirmacion") or "").strip()
        if len(claim) >= 10 and ev.get("tipo") in ("testimony", "external") and claim.lower() not in seen:
            new["evidencia_sugerida"].append({"afirmacion": claim[:1000], "tipo": ev["tipo"],
                                              "fuente": (ev.get("fuente") or "").strip()[:500]})
            seen.add(claim.lower())
    return new


def brief(state: dict) -> str:
    """Resumen del guion para el Board: cada tema con lo dicho y si es dato o supuesto."""
    lines = []
    for tid, label, _goal in TOPICS:
        t = state["temas"][tid]
        if t["estado"] == "sin_dato":
            lines.append(f"- {label}: sin dato (el cliente no lo sabe; hay que validarlo)")
        elif t["resumen"]:
            lines.append(f"- {label}: {t['resumen']} [{t['base']}{', incompleto' if t['estado'] == 'parcial' else ''}]")
        else:
            lines.append(f"- {label}: no se ha hablado")
    return "\n".join(lines) if any(state["temas"][tid]["resumen"] or state["temas"][tid]["estado"] == "sin_dato"
                                    for tid in TOPIC_IDS) else ""


def system_prompt(state: dict, structured: bool = True) -> str:
    """Las instrucciones del turno: el guion, lo que ya se sabe y qué toca preguntar.

    `structured=False` (chat en streaming) pide solo el texto de la respuesta, sin actualizar el estado.
    """
    lines = []
    for tid, label, goal in TOPICS:
        t = state["temas"][tid]
        known = f" — ya dijo: «{t['resumen']}» ({t['base']})" if t["resumen"] else ""
        lines.append(f"- {tid} [{t['estado']}] {label}: {goal}{known}")
    nxt = next_topic(state)
    if nxt:
        goal = next(g for tid, _l, g in TOPICS if tid == nxt)
        step = f"El siguiente tema del guion es «{nxt}»: {goal}."
    else:
        step = ("Los siete temas están cubiertos: no hagas más preguntas. Resume en viñetas lo entendido, "
                "separando datos de supuestos, di qué falta validar y propón ejecutar el Board Room.")
    intro = (
        "Eres ADÁN, el comité ejecutivo de IA que acompaña al cliente. Estás en el Nivel 1, El Dolor: "
        "entender el problema antes de hablar de soluciones. Hablas en español, claro y directo, de tú.\n\n"
        "Sigues un guion de siete temas, en este orden. Estado actual:\n" + "\n".join(lines) + "\n\n"
        f"{step}\n\n"
    )
    update = (
        "Cada turno haces dos cosas:\n"
        "A) Actualizas `temas` con TODA la conversación (no solo el último mensaje). Para cada tema: "
        "`estado` (pendiente, parcial si la respuesta es vaga o incompleta, respondido, o sin_dato si el "
        "cliente dice que no lo sabe), `resumen` (lo que el cliente dijo, en sus palabras, máximo 2 frases; "
        "vacío si no dijo nada) y `base` (dato si lo respalda algo concreto, supuesto si es su hipótesis, "
        "desconocida si no está claro). Una sola respuesta del cliente puede cubrir varios temas.\n"
        "B) Escribes `respuesta` para el cliente:\n"
    )
    reply = (
        "1. Empieza con una frase que confirme lo que entendiste de su último mensaje, con sus datos "
        "concretos. Si contestó algo, demuéstralo; nunca lo ignores.\n"
        "2. Luego haz UNA sola pregunta, sobre el primer tema pendiente o parcial del guion. Si su respuesta "
        "a ese tema fue vaga, repregunta lo mismo más concreto y da un ejemplo de buena respuesta.\n"
        "3. Nunca preguntes algo que ya está respondido. Si el cliente no sabe un dato, dile en una frase "
        "cómo conseguirlo (p. ej., hablar con 5 clientes) y pasa al siguiente tema; no insistas.\n"
        "4. Máximo 120 palabras, sin listas salvo en el resumen final. Indica el avance al final así: "
        "(Tema N de 7).\n"
    )
    evidence = (
        "\n`evidencia_sugerida`: solo lo verificable que el cliente reporte en su último mensaje: lo que dijeron "
        "o hicieron clientes reales (testimony: entrevistas, ventas, mensajes) o una fuente externa con nombre "
        "(external: estudio, informe, cifra pública). Nunca la opinión o hipótesis del fundador. Si no hay, "
        "deja la lista vacía."
    )
    if not structured:
        return intro + "Tu respuesta al cliente:\n" + reply
    return intro + update + reply + evidence
