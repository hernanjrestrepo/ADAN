"""Coherencia entre el equipo, la memoria, el Board y La Arena: todos parten de la misma verdad."""
import json

from app.ai.base import LLMAdapter, LLMResponse
from app.nivel1 import memoria
from app.nivel1.board_room import BoardRoom
from tests.test_discovery import _setup, _use


class Consolidator(LLMAdapter):
    def __init__(self):
        self.prompts = []

    async def chat_json(self, messages, schema, model=None, temperature=0.3, max_tokens=2048):
        self.prompts.append((messages[0].content, messages[-1].content))
        props = schema["properties"]
        if "ficha" in props:
            data = {"ficha": [{"campo": "Mercado", "valor": "Global, todos los idiomas, nacional e internacional"},
                              {"campo": "Pasarela de pagos", "valor": "La paga el cliente con recargo"}],
                    "acuerdos": [{"tipo": "descartado", "texto": "Irene no es el segmento", "nivel": 3},
                                 {"tipo": "dato", "texto": "Paradixe es socio y presta tecnología", "nivel": 2}]}
        else:
            data = {"analysis": "a", "justification": "j", "vote": "PROCEED", "confidence": 80, "key_strengths": [],
                    "key_concerns": [], "questions": [], "failure_mode": "caja", "bulletproof": True, "readiness": 72,
                    "blockers": [], "assumed_risks": ["Contrato con Paradixe se formaliza después del lanzamiento"],
                    "post_launch": ["CAC real por canal"], "objective": "o", "decision_at_stake": "d",
                    "synthesis": "s", "evidence_requests": [], "next_steps": [], "failure_modes": []}
        return LLMResponse(content=json.dumps(data), model="fake", parsed=data)

    async def chat(self, messages, model=None, temperature=0.7, max_tokens=2048):
        return LLMResponse(content="ok", model="fake")

    async def generate(self, *a, **k):
        return LLMResponse(content="", model="fake")

    async def health_check(self):
        return True

    def list_models(self):
        return []


def test_consolidation_builds_the_fact_sheet_and_the_founder_can_edit_it(client, db_session):
    from app.models.models import Project
    cid, h = _setup(client, "ficha@example.com")
    _use(client, Consolidator())
    res = client.post(f"/api/v1/empresa/{cid}/memoria/consolidar", headers=h).json()
    assert res["ficha"]["Mercado"].startswith("Global") and res["acuerdos"] == 2
    client.put(f"/api/v1/empresa/{cid}/ficha", headers=h, json={"ficha": {"Mercado": "Global", "Comisión": "5%"}})
    lib = client.get(f"/api/v1/empresa/{cid}/biblioteca", headers=h).json()
    assert lib["ficha"] == {"Mercado": "Global", "Comisión": "5%"}
    project = db_session.query(Project).filter(Project.company_id == cid).first()
    ctx = memoria.context(db_session, project)
    assert "FICHA DE LA EMPRESA" in ctx and "Comisión: 5%" in ctx and "Irene no es el segmento" in ctx


def test_the_board_scores_readiness_for_the_stage_and_separates_assumed_risks():
    import asyncio
    consensus = asyncio.run(BoardRoom(Consolidator()).run("brief", stage="Nivel 7, Escalamiento"))
    assert consensus.decision == "PROCEED" and round(consensus.score) == 72  # la preparación, no 0,5 × confianza
    assert consensus.assumed_risks and "Contrato con Paradixe" in consensus.assumed_risks[0]
    assert "Etapa evaluada:** Nivel 7" in consensus.minutes and "Riesgos que el fundador decidió asumir" in consensus.minutes
    assert "Para medir después de lanzar" in consensus.minutes
