"""Primer Agente end-to-end: Diagnostico del Dolor (Nivel 1, AD-FUNC-01). Rol CEO porque
el CEO Agent preside el Board Room y es como ADAN habla con el cliente (AD-FUNC-02 SS0).

Instrucciones ancladas en el blueprint, no inventadas aqui:
- AD-FUNC-01 Nivel 1: produce el Entregable 'Diagnostico del Dolor' - problema, evidencia
  externa, perfil del emprendedor.
- AD-FUNC-03: la emocion objetivo de Nivel 1 es Comprendido, nunca Juzgado.
- AD-FUNC-06 SS0: onboarding/primer contacto llega a la primera pregunta real rapido, sin
  formulario previo - este Agente ES esa primera pregunta real."""

from agents.base import AgentDefinition

DIAGNOSTICO_AGENT_ID = "diagnostico-nivel-1"

_INSTRUCCIONES = """\
Tu tarea es producir un Diagnostico del Dolor (Nivel 1 de ADán, "El Dolor") a partir de \
lo que el emprendedor te cuenta sobre su problema de negocio.

Debes hacer que la persona se sienta Comprendida, nunca Juzgada - sin importar que tan \
vago o informal sea su relato.

Responde en este formato exacto, en español:

PROBLEMA: <una descripcion clara y honesta del problema real, en una o dos frases>
EVIDENCIA: <que evidencia o señal externa respalda que el problema es real, o "sin \
evidencia externa todavia" si no la hay>
PERFIL: <una frase breve sobre el perfil del emprendedor a partir de como describe el \
problema>

No inventes evidencia que la persona no haya mencionado. Si falta evidencia, dilo \
explicitamente - la honestidad sobre lo que no se sabe es mas valiosa que aparentar certeza.
"""


def build_diagnostico_agent() -> AgentDefinition:
    return AgentDefinition(
        agent_id=DIAGNOSTICO_AGENT_ID,
        rol="CEO",
        instrucciones=_INSTRUCCIONES,
        max_steps=1,
        max_tokens=1000,
        # Solo lectura de memoria (contexto de conversaciones/diagnosticos previos del
        # mismo Proyecto) - nunca kg_write ni memory_store: un Diagnostico no decide por
        # si solo que hechos quedan permanentes en el grafo (WO-003 Sprint 4).
        allowed_tools=["memory_search"],
    )
