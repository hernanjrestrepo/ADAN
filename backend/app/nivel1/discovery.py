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
from dataclasses import dataclass

TOPICS = [
    # Nivel 1 según Customer Development (Blank), Running Lean (Maurya) y Value Proposition Design (Osterwalder)
    ("problema", "El problema (trabajo por hacer)", "el problema en una frase, como el trabajo que el cliente intenta hacer y no logra bien"),
    ("afectados", "Cliente inicial y persona", "el primer segmento (mercado de entrada) y la persona concreta que más sufre el problema"),
    ("momento", "Cuándo y cada cuánto pasa", "en qué situación aparece el problema y con qué frecuencia"),
    ("costo", "Intensidad y costo del dolor", "qué pierde: tiempo, dinero, riesgo o frustración; qué tanto duele (con cifras si existen)"),
    ("alternativas", "Cómo lo resuelven hoy", "qué usan hoy, cuánto gastan en eso y por qué no les basta"),
    ("urgencia", "Disposición a actuar", "por qué lo resolverían ya y si actuarían (comprar, cambiar de proveedor, registrarse)"),
    ("evidencia", "Validación (simulada y real)", "qué respalda el dolor: encuesta simulada con el Simulador de Mercado y encuesta real en curso, entrevistas, datos o fuentes"),
]
TOPIC_IDS = [t[0] for t in TOPICS]


@dataclass(frozen=True)
class Script:
    """El guion de un Nivel: qué busca, sus temas (id, nombre, qué hay que lograr), su método y entregables."""
    number: int
    name: str
    goal: str
    topics: tuple
    method: str
    deliverables: tuple = ()
    kpis: tuple = ()
    team: tuple = ()
    dimension: str | None = "problem"
    board: bool = False
    arena: bool = False

    @property
    def topic_ids(self) -> list[str]:
        return [t[0] for t in self.topics]


LEVEL1 = Script(
    number=1, name="El Dolor", goal="entender a fondo el problema y a quién le duele, antes de hablar de soluciones",
    topics=tuple(TOPICS),
    method=("en el Nivel 1 solo se define el DOLOR. No hables de temas legales, de financiación ni de soluciones "
            "avanzadas: eso viene en otros Niveles (el Board entra desde el Nivel 3). Siempre se valida antes de "
            "construir: propón la ENCUESTA SIMULADA con el Simulador de Mercado para seguir avanzando ya."),
    deliverables=("Problema en una frase (trabajo por hacer)", "Cliente inicial y persona", "Alternativas actuales",
                  "Mapa de dolores", "Encuesta simulada"),
    kpis=("% del segmento que confirma el dolor", "Intensidad del dolor (1 a 5)", "Gasto actual en alternativas"),
    team=("ceo", "cmo", "investigador", "csi"), dimension="problem",
)
STATUSES = ("pendiente", "parcial", "respondido", "sin_dato")
CLOSED = ("respondido", "sin_dato")  # "sin_dato": el cliente no lo sabe; queda como tarea de validación
BASES = ("dato", "supuesto", "desconocida")
MAX_SUMMARY = 300

def schema_for(topic_ids: list[str]) -> dict:
    schema = deepcopy(_SCHEMA)
    schema["properties"]["temas"]["items"]["properties"]["id"]["enum"] = list(topic_ids)
    return schema


_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["respuesta", "habla", "mesa", "temas", "evidencia_sugerida", "investigar", "reaccion"],
    "properties": {
        "respuesta": {"type": "string"},
        # Quién del equipo responde este turno (habla en primera persona)
        "habla": {"type": "string", "enum": ["ceo", "cto", "cfo", "cmo", "legal", "producto", "operaciones", "investigador"]},
        # Mesa de trabajo: otros personajes que complementan o debaten frente al fundador
        "mesa": {"type": "array", "items": {
            "type": "object", "additionalProperties": False, "required": ["habla", "texto", "emocion"],
            "properties": {"habla": {"type": "string", "enum": ["ceo", "cto", "cfo", "cmo", "legal", "producto",
                                                                 "operaciones", "investigador"]},
                           "texto": {"type": "string"},
                           "emocion": {"type": "string", "enum": ["feliz", "riendo", "preocupado", "pensando", "hablando"]}}}},
        # Si hace falta un dato del mundo (mercado, competencia, cifras), qué buscar en internet; vacío si no
        "investigar": {"type": "string"},
        # Cómo reacciona el equipo en el Universo a lo que se está hablando
        "reaccion": {
            "type": "object",
            "additionalProperties": False,
            "required": ["agente", "emocion", "frase"],
            "properties": {
                "agente": {"type": "string", "enum": ["ceo", "cto", "cfo", "cmo", "legal", "producto", "operaciones",
                                                      "csi", "eva", "investigador", "analista"]},
                "emocion": {"type": "string", "enum": ["feliz", "riendo", "preocupado", "estresado", "celebrando",
                                                       "pensando", "hablando"]},
                "frase": {"type": "string"},
            },
        },
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
SCHEMA = schema_for(TOPIC_IDS)


def empty_state(script: Script | None = None) -> dict:
    ids = (script or LEVEL1).topic_ids
    return {"temas": {tid: {"estado": "pendiente", "resumen": "", "base": "desconocida"} for tid in ids},
            "evidencia_sugerida": []}


def current_state(messages, script: Script | None = None) -> dict:
    """El último estado guardado en la conversación (o uno vacío)."""
    for msg in reversed(messages):
        data = (msg.metadata_json or {}).get("discovery")
        if data:
            state = empty_state(script)
            state["temas"].update({k: v for k, v in data.get("temas", {}).items() if k in state["temas"]})
            state["evidencia_sugerida"] = list(data.get("evidencia_sugerida", []))
            return state
    return empty_state(script)


def next_topic(state: dict, script: Script | None = None) -> str | None:
    for tid in (script or LEVEL1).topic_ids:
        if state["temas"][tid]["estado"] not in CLOSED:
            return tid
    return None


def progress(state: dict, script: Script | None = None) -> dict:
    """Lo que la interfaz muestra: cada tema con su estado y resumen, y el siguiente en el guion."""
    script = script or LEVEL1
    topics = [{"id": tid, "label": label, **state["temas"][tid]} for tid, label, _goal in script.topics]
    done = sum(1 for t in topics if t["estado"] in CLOSED)
    return {"topics": topics, "done": done, "total": len(topics), "next": next_topic(state, script),
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
    seen = [_words(e["afirmacion"]) for e in new["evidencia_sugerida"]]
    for ev in parsed.get("evidencia_sugerida") or []:
        claim = (ev.get("afirmacion") or "").strip()
        words = _words(claim)
        if len(claim) >= 10 and ev.get("tipo") in ("testimony", "external") and not any(_same(words, s) for s in seen):
            new["evidencia_sugerida"].append({"afirmacion": claim[:1000], "tipo": ev["tipo"],
                                              "fuente": (ev.get("fuente") or "").strip()[:500]})
            seen.append(words)
    return new


def _words(text: str) -> set[str]:
    """Palabras con contenido (sin tildes ni signos) para reconocer la misma afirmación dicha distinto."""
    import unicodedata

    plain = unicodedata.normalize("NFKD", text.lower()).encode("ascii", "ignore").decode()
    tokens = "".join(c if c.isalnum() else " " for c in plain).split()
    return {t for t in tokens if len(t) > 2 or t.isdigit()}


def _same(a: set[str], b: set[str]) -> bool:
    """Misma evidencia si casi todas las palabras de la más corta están en la otra."""
    if not a or not b:
        return False
    return len(a & b) / min(len(a), len(b)) >= 0.75


def brief(state: dict, script: Script | None = None) -> str:
    """Resumen del guion para el Board: cada tema con lo dicho y si es dato o supuesto."""
    script = script or LEVEL1
    lines = []
    for tid, label, _goal in script.topics:
        t = state["temas"][tid]
        if t["estado"] == "sin_dato":
            lines.append(f"- {label}: sin dato (el cliente no lo sabe; hay que validarlo)")
        elif t["resumen"]:
            lines.append(f"- {label}: {t['resumen']} [{t['base']}{', incompleto' if t['estado'] == 'parcial' else ''}]")
        else:
            lines.append(f"- {label}: no se ha hablado")
    return "\n".join(lines) if any(state["temas"][tid]["resumen"] or state["temas"][tid]["estado"] == "sin_dato"
                                    for tid in script.topic_ids) else ""


# Cómo conversa ADÁN (lecciones de las conversaciones reales: era repetitivo, preguntaba lo ya contestado, anclaba
# en el primer mensaje aunque el cliente lo corrigiera y le pedía al cliente investigar lo que ADÁN puede buscar)
CONVERSATION_RULES = (
    "CÓMO ERES: el equipo es el patrocinador del proyecto, no un auditor. Te importa que la empresa salga adelante: "
    "eres cálido, motivador y realista a la vez. Celebras los avances concretos, reconoces el esfuerzo y la "
    "experiencia del fundador, y cuando algo no está claro lo dices con respeto y SIEMPRE traes una propuesta para "
    "resolverlo (qué hacemos, cómo, y si lo hace el equipo). Nunca cuestionas por cuestionar ni repites una exigencia "
    "que el fundador ya explicó: construyes sobre lo que trae.\n"
    "1. Ritmo humano: máximo 90 palabras, una idea y UNA pregunta. Reconoce lo que dijo en media frase (sin «Entiendo:»"
    " ni repetirlo), aporta algo y propone el siguiente paso. Varía cómo empiezas; no empieces siempre con su nombre.\n"
    "2. Escucha primero: si trae un dato, un perfil o una decisión, úsalo y constrúyelo («ese es tu cliente ideal; lo "
    "dejo así»), no lo reemplaces por estadísticas. Si corrige algo, la corrección manda. Si un tema no aplica a su "
    "modelo (p. ej., gana por comisión), adáptalo y no lo repitas.\n"
    "3. Datos: el equipo los busca (no se los pides). Escribe en `investigar` una consulta concreta SOLO si un dato del "
    "mundo cambia una decisión de este Nivel o el fundador lo pide; no investigues en cada turno. Cuando haya datos, "
    "NO los vuelques: digiérelos y aterrízalos a ESTA empresa (qué significan para su negocio, qué decisión cambian, "
    "qué hacemos con eso). Una tabla corta solo si ayuda.\n"
    "Puedes abrir páginas web: cuando el fundador pega un enlace (su sitio, un competidor, una nota), ADÁN lo abre y "
    "te da su contenido. Si menciona su web o redes sin el enlace, pídeselo para revisarlas.\n"
    "4. CERO cifras inventadas: cada número trae su fuente con enlace, o va marcado como «estimación» explicando "
    "cómo se calculó. Revisa el sentido común antes de escribirlo (orden de magnitud frente a la población y el "
    "mercado reales). Si las cifras del fundador no cuadran, dilo con tacto y propone cómo validarlas.\n"
    "5. Gráficos solo con números reales o marcados como estimación, con este formato:\n```chart\n{\"type\":\"bar\","
    "\"title\":\"…\",\"labels\":[\"…\"],\"series\":[{\"name\":\"…\",\"data\":[1,2]}]}\n```\n(type: bar, line o pie).\n"
    "6. METODOLOGÍA (híbrido de Customer Development de Steve Blank, Lean Startup de Eric Ries, Running Lean de Ash "
    "Maurya, The Mom Test, Value Proposition Design, Disciplined Entrepreneurship, Lean Analytics y Traction): "
    "trabaja SOLO lo de este Nivel (el método del Nivel está arriba); lo de Niveles siguientes se deja para su "
    "momento. Siempre se valida antes de construir: cuando haga falta saber qué opina el mercado, propón la "
    "ENCUESTA SIMULADA con el Simulador de Mercado. No pongas «(Tema N de M)».\n"
    "7. `habla`: responde quien corresponde al tema, en primera persona: Santiago (cmo) el mercado y los clientes, "
    "Iris (investigador) la investigación, Camila (cfo) el dinero, Andrés (producto) la solución, Sofía (operaciones), "
    "Mateo (cto), Lucía (legal); ADÁN (ceo) cuando es general, saluda, resume o presenta a alguien («te paso con "
    "Santiago»). Si el fundador nombra a alguien, responde esa persona.\n"
    "8. `mesa`: cuando el tema cruza dos áreas o vale la pena una conversación del equipo frente al fundador, agrega "
    "1 o 2 intervenciones cortas de OTROS personajes (máximo 30 palabras cada una) que complementan, proponen o "
    "debaten con respeto y algo de humor humano (una risa, un «yo lo veo distinto…»), siempre construyendo. Vacía si "
    "no hace falta.\n"
    "9. `reaccion`: quién reacciona en la oficina, con su emoción y una frase de máximo 10 palabras, humana y con "
    "humor cuando cabe.\n"
)


def system_prompt(state: dict, structured: bool = True, script: Script | None = None) -> str:
    """Las instrucciones del turno: el guion, lo que ya se sabe y qué toca preguntar.

    `structured=False` (chat en streaming) pide solo el texto de la respuesta, sin actualizar el estado.
    """
    script = script or LEVEL1
    lines = []
    for tid, label, goal in script.topics:
        t = state["temas"][tid]
        known = f" — ya dijo: «{t['resumen']}» ({t['base']})" if t["resumen"] else ""
        lines.append(f"- {tid} [{t['estado']}] {label}: {goal}{known}")
    nxt = next_topic(state, script)
    n = len(script.topics)
    if nxt:
        goal = next(g for tid, _l, g in script.topics if tid == nxt)
        step = f"El siguiente tema del guion es «{nxt}» (tema {script.topic_ids.index(nxt) + 1} de {n}): {goal}."
    else:
        step = (f"Los {n} temas están cubiertos: no hagas más preguntas. Resume en viñetas lo logrado y los "
                "entregables listos, separando datos de supuestos, y propón cerrar el Nivel"
                + (" (después de la sesión del Board)." if script.board else "."))
    intro = (
        "Eres el equipo de ADÁN (un CEO y sus especialistas), patrocinador del proyecto del fundador. Estás en el "
        f"Nivel {script.number}, {script.name}: {script.goal}. Hablas en español, cálido, claro y directo, de tú.\n"
        f"Método de este Nivel: {script.method}\n"
        + (f"Entregables del Nivel: {'; '.join(script.deliverables)}. Indicadores: {'; '.join(script.kpis)}.\n"
           if script.deliverables else "")
        + f"\nSigues un guion de {n} temas, en este orden. Estado actual:\n" + "\n".join(lines) + "\n\n"
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
    reply = CONVERSATION_RULES
    evidence = (
        "\n`evidencia_sugerida`: se registra AUTOMÁTICAMENTE como evidencia, así que solo HECHOS que ya existen, "
        "nunca evidencia por conseguir ni tareas (nada de 'un mensaje donde alguien describa…'). Incluye lo que "
        "encontraste investigando en internet (external, con la URL o el informe en `fuente`) y lo verificable que el "
        "cliente reporte en su último mensaje: lo que dijeron "
        "o hicieron clientes reales (testimony: entrevistas, ventas, mensajes) o una fuente externa con nombre "
        "(external: estudio, informe, cifra pública). Nunca la opinión o hipótesis del fundador, ni lo que cuenta "
        "de su propio producto, equipo o avance (eso no es testimonio de clientes). Sin repetir una afirmación ya "
        "sugerida. Si no hay, deja la lista vacía."
    )
    if not structured:
        return intro + "Tu respuesta al cliente:\n" + reply
    return intro + update + reply + evidence
