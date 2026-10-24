"""Board crítico: avanzar exige que la empresa esté a prueba de balas (9 de cada 10 cierran en 5 años)."""
import json

import pytest

from app.nivel1.board_room import BoardRoom, AgentVote, SPECIALISTS, VOTE_SCHEMA
from tests.fakes import FakeLLM


def _v(agent, vote="PROCEED", conf=85, shielded=True):
    return AgentVote(agent=agent, analysis="", justification=f"{agent} opina", vote=vote, confidence=conf,
                     bulletproof=shielded, failure_mode=f"riesgo de {agent}")


def _board(*votes):
    return BoardRoom(FakeLLM())._build_consensus(list(votes))


def test_proceed_needs_five_of_six():
    six = [_v(r) for r in SPECIALISTS]
    assert _board(*six).decision == "PROCEED"
    four = [_v(r) for r in list(SPECIALISTS)[:4]] + [_v(r, "PIVOT", 70, False) for r in list(SPECIALISTS)[4:]]
    assert _board(*four).decision == "PIVOT"


def test_a_single_stop_or_an_unshielded_area_blocks_proceed():
    roles = list(SPECIALISTS)
    assert _board(*[_v(r) for r in roles[:5]], _v(roles[5], "STOP", 80, False)).decision == "PIVOT"
    not_shielded = [_v(r) for r in roles[:5]] + [_v(roles[5], "PROCEED", 85, shielded=False)]
    consensus = _board(*not_shielded)
    assert consensus.decision == "PIVOT" and consensus.bulletproof_gaps == [roles[5]]


def test_low_confidence_is_not_enough():
    assert _board(*[_v(r, conf=60) for r in SPECIALISTS]).decision == "PIVOT"


def test_failure_modes_are_collected():
    consensus = _board(*[_v(r) for r in SPECIALISTS])
    assert "CFO: riesgo de CFO" in consensus.failure_modes


def test_every_vote_must_declare_its_failure_mode():
    assert {"failure_mode", "bulletproof"} <= set(VOTE_SCHEMA["required"])


class Recorder(FakeLLM):
    def __init__(self):
        super().__init__(chat_replies=[json.dumps({"analysis": "a", "justification": "j", "vote": "PIVOT",
                                                   "confidence": 60, "key_strengths": [], "key_concerns": [],
                                                   "questions": [], "failure_mode": "caja", "bulletproof": False})])
        self.systems = []

    async def chat(self, messages, model=None, temperature=0.7, max_tokens=2048):
        self.systems.append(messages[0].content)
        return await super().chat(messages, model, temperature, max_tokens)


@pytest.mark.asyncio
async def test_the_devils_advocate_rotates_each_session():
    for n in (0, 1):
        llm = Recorder()
        consensus = await BoardRoom(llm).run("Dolor", session_number=n)
        devils = [v.agent for v in consensus.votes if v.devils_advocate]
        assert devils == [list(SPECIALISTS)[n]]
        assert sum("ABOGADO DEL DIABLO" in s for s in llm.systems) == 1
        assert all("9 de cada 10 empresas" in s for s in llm.systems if "Board Room de ADÁN" in s and "Eres el C" in s
                   or "Eres el L" in s or "Eres el P" in s or "Eres el O" in s)
