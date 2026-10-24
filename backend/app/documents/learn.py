"""ADÁN aprende de la documentación del cliente: un solo llamado al modelo lee los documentos y devuelve
qué entendió, cómo avanza el guion del dolor, qué evidencia hay de verdad y qué falta.

Regla de honestidad (AD-CMP-05): lo que el documento solo afirma, sin fuente ni cifra verificable, es un
supuesto del fundador, no un dato. Un plan de negocio bonito no valida nada por sí solo.
"""
from __future__ import annotations

from app.ai.base import LLMAdapter, LLMMessage, LLMResponse
from app.nivel1 import discovery

MAX_PER_DOC = 14_000
MAX_TOTAL = 48_000

SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["respuesta", "resumen", "etapa", "hechos", "temas", "evidencia_sugerida", "vacios", "riesgos"],
    "properties": {
        "respuesta": {"type": "string"},
        "resumen": {"type": "string"},
        "etapa": {"type": "string", "enum": ["idea", "empresa_existente", "no_claro"]},
        "hechos": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["dato", "fuente", "base"],
                "properties": {"dato": {"type": "string"}, "fuente": {"type": "string"},
                               "base": {"type": "string", "enum": ["dato", "supuesto"]}},
            },
        },
        "temas": discovery.SCHEMA["properties"]["temas"],
        "evidencia_sugerida": discovery.SCHEMA["properties"]["evidencia_sugerida"],
        "vacios": {"type": "array", "items": {"type": "string"}},
        "riesgos": {"type": "array", "items": {"type": "string"}},
    },
}

INSTRUCTIONS = (
    "Eres ADÁN, el comité ejecutivo de IA que acompaña a la empresa. El cliente te entregó su documentación "
    "para que la conozcas a fondo. Tu misión: que esta empresa no sea parte del 90 % que cierra en sus primeros "
    "cinco años por falta de información, planeación o preparación. Lee con ojo crítico, como un analista "
    "exigente, no como un admirador.\n\n"
    "Devuelve:\n"
    "- `resumen`: qué es la iniciativa o la empresa, en 4 a 6 frases concretas (qué vende, a quién, cómo gana "
    "dinero, en qué etapa está).\n"
    "- `etapa`: idea (aún no opera) o empresa_existente (ya vende), o no_claro.\n"
    "- `hechos`: hasta 15 hechos importantes, cada uno con el documento de donde sale. `base` es dato solo si "
    "el documento lo respalda con una cifra verificable, una fuente externa nombrada o un registro real "
    "(ventas, clientes, estados financieros); si es una afirmación o proyección del fundador, es supuesto.\n"
    "- `temas`: el guion de los siete temas del dolor, con lo que los documentos dicen de cada uno (mismo "
    "formato que en la conversación: estado, resumen y base). No marques respondido algo que el documento "
    "apenas menciona: usa parcial.\n"
    "- `evidencia_sugerida`: solo evidencia verificable: lo que dijeron o hicieron clientes reales "
    "(testimony: entrevistas, ventas, encuestas) o una fuente externa con nombre (external: estudio, informe, "
    "cifra pública). Nunca la opinión del fundador ni la descripción de su propio producto.\n"
    "- `vacios`: lo que falta para que el modelo sea a prueba de balas (cifras sin fuente, segmentos sin "
    "validar, costos ausentes, temas legales sin resolver).\n"
    "- `riesgos`: los riesgos más serios que ves, concretos para esta empresa.\n"
    "- `respuesta`: lo que le dices al cliente, de tú, en máximo 150 palabras: qué entendiste (con datos de "
    "sus documentos), lo más débil que encontraste y UNA pregunta sobre el primer tema del guion que siga "
    "pendiente o parcial."
)


def _corpus(docs: list[tuple[str, str]]) -> str:
    parts, used = [], 0
    for name, text in docs:
        room = min(MAX_PER_DOC, MAX_TOTAL - used)
        if room <= 500:
            parts.append(f"=== {name} ===\n[No se incluyó completo: se superó el máximo de lectura de esta vez]")
            continue
        chunk = text[:room]
        used += len(chunk)
        parts.append(f"=== {name} ===\n{chunk}" + ("\n[...documento recortado]" if len(text) > room else ""))
    return "\n\n".join(parts)


async def learn(llm: LLMAdapter, state: dict, docs: list[tuple[str, str]], context: str = "") -> LLMResponse:
    current = "\n".join(f"- {tid} [{state['temas'][tid]['estado']}]: {state['temas'][tid]['resumen'] or 'sin datos'}"
                        for tid in discovery.TOPIC_IDS)
    goals = "\n".join(f"- {tid}: {label} ({goal})" for tid, label, goal in discovery.TOPICS)
    system = (f"{INSTRUCTIONS}\n\nLos siete temas del guion:\n{goals}\n\nLo que ADÁN ya sabía antes de leer:\n{current}"
              + (f"\n\n{context}" if context else ""))
    messages = [LLMMessage("system", system), LLMMessage("user", "Documentación del cliente:\n\n" + _corpus(docs))]
    return await llm.chat_json(messages, SCHEMA, temperature=0.3, max_tokens=4096)
