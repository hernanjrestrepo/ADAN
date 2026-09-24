"""Regresión de WO-095 — Estabilización funcional (bugs B1–B19 de la auditoría 2026-09)."""
import json
from unittest.mock import AsyncMock, MagicMock

import pytest

import app.api.v1.cognitive as cognitive_api
import app.api.v1.nivel1 as nivel1_api
import app.ems.store as ems_store
from app.agents.board import ExecutiveBoard, _to_percent
from app.agents.ceo import CEOAgent
from app.ai.base import LLMAdapter, LLMResponse
from app.ai.normalize import normalize_vote
from app.core.disclaimer import AI_DISCLAIMER, strip_disclaimer, with_disclaimer
from app.dka.pipeline import KnowledgeAcquisitionPipeline
from app.ems.memory import EnterpriseMemorySystem
from app.ems.models import EMSChunk, EMSDocument, KnowledgeFact
from app.ems.providers import LocalEmbeddingProvider, LocalVectorStoreProvider
from app.models.models import (
    Card, CardStatus, Conversation, Decision, DecisionStatus, Document, Event, Level,
    Message, NivelStatus, Project,
)
from app.nivel1.board_room import AgentVote, BoardConsensus, BoardRoom
from app.nivel1.service import MAX_CONTEXT_MESSAGES, Nivel1Service
from app.services.gemelo_digital import GemeloDigitalService

VALID_VOTE = (
    '{"analysis":"A","justification":"J","vote":"PROCEED","confidence":80,'
    '"key_strengths":["s"],"key_concerns":["c"],"questions":["q"]}'
)


class FakeLLM(LLMAdapter):
    """LLM de prueba: respuestas configurables y conteo de llamadas."""

    def __init__(self, chat_replies=None, generate_reply="Documento generado", stream_tokens=None):
        self.chat_replies = list(chat_replies or [VALID_VOTE])
        self.generate_reply = generate_reply
        self.stream_tokens = stream_tokens or ["Hola", "\nmundo"]
        self.chat_calls = 0
        self.generate_calls = 0
        self.last_messages = None

    async def chat(self, messages, model=None, temperature=0.7, max_tokens=2048):
        self.chat_calls += 1
        self.last_messages = messages
        reply = self.chat_replies[(self.chat_calls - 1) % len(self.chat_replies)]
        return LLMResponse(content=reply, model="fake")

    async def chat_stream(self, messages, model=None, temperature=0.7, max_tokens=2048):
        self.last_messages = messages
        for token in self.stream_tokens:
            yield token

    async def generate(self, prompt, model=None, system=None, temperature=0.7, max_tokens=2048):
        self.generate_calls += 1
        return LLMResponse(content=self.generate_reply, model="fake")

    async def health_check(self):
        return True

    def list_models(self):
        return []


def _headers(client, email="wo095@example.com"):
    resp = client.post("/api/v1/auth/register", json={"email": email, "name": "U", "password": "password123"})
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


@pytest.fixture
def company(client, db_session):
    """Empresa con su proyecto y los 7 Niveles, creada por la API."""
    headers = _headers(client)
    company_id = client.post("/api/v1/companies/", json={"name": "Acme"}, headers=headers).json()["id"]
    project = db_session.query(Project).filter_by(company_id=company_id).one()
    return {"id": company_id, "headers": headers, "project": project}


def _pain_conversation(db_session, project, user_messages=1):
    level = db_session.query(Level).filter_by(project_id=project.id, number=1).one()
    card = Card(project_id=project.id, level_id=level.id, title="Dolor", card_type="pain_discovery",
                status=CardStatus.ACTIVE)
    db_session.add(card)
    db_session.flush()
    conversation = Conversation(card_id=card.id)
    db_session.add(conversation)
    db_session.flush()
    for i in range(user_messages):
        db_session.add(Message(conversation_id=conversation.id, role="user", content=f"mensaje {i}"))
    db_session.commit()
    return conversation


# ============================================================
# B1 — recomendaciones
# ============================================================

def test_b1_save_recommendation_records_event(db_session, company):
    doc = GemeloDigitalService(db_session).save_recommendation(company["project"], "Recs", "contenido")
    assert doc.doc_type == "recommendation"
    event = db_session.query(Event).filter_by(entity_id=doc.id).one()
    assert event.event_type == "recommendation_saved"


# ============================================================
# B2 — el sistema cognitivo persiste
# ============================================================

def test_b2_cognitive_think_persists_events_and_messages(client, db_session, company, monkeypatch):
    monkeypatch.setattr(cognitive_api, "get_llm_adapter", lambda: FakeLLM(chat_replies=["respuesta"]))
    resp = client.post("/api/v1/cognitive/think", json={"message": "hola", "company_id": company["id"]},
                       headers=company["headers"])
    assert resp.status_code == 200
    assert resp.json()["disclaimer"] == AI_DISCLAIMER
    assert db_session.query(Event).filter_by(project_id=company["project"].id).count() > 0
    assert db_session.query(Message).filter_by(role="user", content="hola").count() == 1


# ============================================================
# B3, B7, B17 — votos del Board Room
# ============================================================

def test_b3_normalize_vote_defaults_to_abstain():
    assert normalize_vote(None) == "ABSTAIN"
    assert normalize_vote("sí, adelante") == "ABSTAIN"
    assert normalize_vote("proceed") == "PROCEED"


@pytest.mark.asyncio
async def test_b3_invalid_responses_abstain_and_do_not_approve():
    consensus = await BoardRoom(FakeLLM(chat_replies=["no es JSON"])).run("Problema")
    assert all(v.vote == "ABSTAIN" for v in consensus.votes)
    assert consensus.decision == "NO_CONSENSUS"
    assert consensus.score == 0


@pytest.mark.asyncio
async def test_b3_abstentions_do_not_count():
    llm = FakeLLM(chat_replies=[VALID_VOTE, "no es JSON"])
    consensus = await BoardRoom(llm).run("Problema")
    assert sum(v.vote == "ABSTAIN" for v in consensus.votes) == 2
    assert consensus.decision == "PROCEED"
    assert consensus.confidence == 80
    assert "Abstenciones" in consensus.summary


@pytest.mark.asyncio
async def test_b3_one_valid_vote_is_not_quorum():
    llm = FakeLLM(chat_replies=[VALID_VOTE, "no es JSON", "no es JSON", "no es JSON"])
    consensus = await BoardRoom(llm).run("Problema")
    assert consensus.decision == "NO_CONSENSUS"
    assert "quórum" in consensus.summary


@pytest.mark.asyncio
async def test_b17_json_list_is_abstention_not_crash():
    consensus = await BoardRoom(FakeLLM(chat_replies=['["no", "es", "objeto"]'])).run("Problema")
    assert consensus.decision == "NO_CONSENSUS"


def test_b7_every_dissenting_agent_is_recorded():
    room = BoardRoom(FakeLLM())
    votes = [
        AgentVote(agent="CEO", analysis="", justification="sí", vote="PROCEED", confidence=80),
        AgentVote(agent="CTO", analysis="", justification="sí", vote="PROCEED", confidence=80),
        AgentVote(agent="CFO", analysis="", justification="caja", vote="PIVOT", confidence=70),
        AgentVote(agent="CMO", analysis="", justification="demanda", vote="PIVOT", confidence=60),
    ]
    consensus = room._build_consensus(votes)
    assert consensus.decision == "PIVOT"
    assert "CEO" in consensus.dissent and "CTO" in consensus.dissent


@pytest.mark.asyncio
async def test_b3_executive_board_failures_abstain():
    llm = MagicMock()
    llm.chat = AsyncMock(side_effect=Exception("Ollama caído"))
    ems = AsyncMock()
    ems.retrieve_for_llm = AsyncMock(return_value="")
    result = await ExecutiveBoard(llm, ems, MagicMock()).run("¿Expandimos?", "c", "u")
    assert all(r.vote == "ABSTAIN" for r in result.deliberation.rounds)
    assert result.decision_record.final_decision == "NO_CONSENSUS"


# ============================================================
# B14 — escala de confianza del Board de 7
# ============================================================

@pytest.mark.parametrize("raw, expected", [(0.8, 80.0), (85, 85.0), ("0.5", 50.0), (None, 0.0), (250, 100.0)])
def test_b14_confidence_is_0_to_100(raw, expected):
    assert _to_percent(raw) == expected


# ============================================================
# B4 — aprobación del cliente
# ============================================================

def test_b4_board_room_result_is_only_proposed(db_session, company):
    decision = GemeloDigitalService(db_session).save_board_room_result(
        company["project"], "PROCEED", 80.0, "Resumen", [{"agent": "CEO", "vote": "PROCEED"}],
    )
    assert decision.status == DecisionStatus.PROPOSED


def test_b4_level_closes_only_when_client_approves(client, db_session, company):
    project = company["project"]
    decision = GemeloDigitalService(db_session).propose_level_completion(project, 1, 85.0, "Gate aprobado")
    level1 = db_session.query(Level).filter_by(project_id=project.id, number=1).one()
    assert level1.status == NivelStatus.ACTIVE

    url = f"/api/v1/nivel1/{company['id']}/decisions/{decision.id}"
    resp = client.post(url, json={"action": "approve"}, headers=company["headers"])
    assert resp.status_code == 200
    assert resp.json()["status"] == "executed"

    db_session.expire_all()
    levels = {lvl.number: lvl.status for lvl in db_session.query(Level).filter_by(project_id=project.id)}
    assert levels[1] == NivelStatus.COMPLETED
    assert levels[2] == NivelStatus.ACTIVE

    # Una decisión ya resuelta no se vuelve a decidir
    assert client.post(url, json={"action": "reject"}, headers=company["headers"]).status_code == 409


def test_b4_rejecting_keeps_level_open(client, db_session, company):
    project = company["project"]
    decision = GemeloDigitalService(db_session).propose_level_completion(project, 1, 85.0, "Gate aprobado")
    resp = client.post(f"/api/v1/nivel1/{company['id']}/decisions/{decision.id}", json={"action": "reject"},
                       headers=company["headers"])
    assert resp.json()["status"] == "rejected"
    db_session.expire_all()
    assert db_session.query(Level).filter_by(project_id=project.id, number=1).one().status == NivelStatus.ACTIVE


def test_b4_decisions_are_private(client, db_session, company):
    decision = GemeloDigitalService(db_session).propose_level_completion(company["project"], 1, 85.0, "Gate")
    other = _headers(client, "otro@example.com")
    assert client.get(f"/api/v1/nivel1/{company['id']}/decisions", headers=other).status_code == 404
    resp = client.post(f"/api/v1/nivel1/{company['id']}/decisions/{decision.id}", json={"action": "approve"},
                       headers=other)
    assert resp.status_code == 404


def test_b4_proposing_twice_reuses_pending_decision(db_session, company):
    service = GemeloDigitalService(db_session)
    first = service.propose_level_completion(company["project"], 1, 85.0, "Gate")
    second = service.propose_level_completion(company["project"], 1, 90.0, "Gate otra vez")
    assert first.id == second.id


# ============================================================
# B6 — recomendaciones y Gate Review reutilizan el Board guardado
# ============================================================

def test_b6_recommendations_reuse_stored_board_room(client, db_session, company):
    project = company["project"]
    consensus = BoardConsensus(
        decision="PROCEED", score=80, confidence=80, summary="s",
        votes=[AgentVote(agent="CEO", analysis="a", justification="j", vote="PROCEED", confidence=80)],
        concerns_majority=["c"],
    )
    GemeloDigitalService(db_session).save_board_room_result(
        project, "PROCEED", 80, "s", [{"agent": "CEO"}], consensus=consensus.to_dict(),
    )
    db_session.add(Document(project_id=project.id, title="Diag", content="diagnóstico", doc_type="diagnosis",
                            origin="generated_by_adan"))
    db_session.commit()
    decisions_before = db_session.query(Decision).count()

    llm = FakeLLM()
    client.app.dependency_overrides[nivel1_api.get_llm] = lambda: llm
    resp = client.post(f"/api/v1/nivel1/{company['id']}/recommendations", headers=company["headers"])

    assert resp.status_code == 200
    assert resp.json()["content"].endswith(f"{AI_DISCLAIMER}\n")
    assert llm.chat_calls == 0 and llm.generate_calls == 1
    assert db_session.query(Decision).count() == decisions_before


def test_b6_recommendations_require_board_room(client, db_session, company):
    db_session.add(Document(project_id=company["project"].id, title="Diag", content="d", doc_type="diagnosis",
                            origin="generated_by_adan"))
    db_session.commit()
    client.app.dependency_overrides[nivel1_api.get_llm] = lambda: FakeLLM()
    resp = client.post(f"/api/v1/nivel1/{company['id']}/recommendations", headers=company["headers"])
    assert resp.status_code == 400


# ============================================================
# B8 — ventana de contexto del chat
# ============================================================

def test_b8_long_conversations_are_summarized(db_session, company):
    conversation = _pain_conversation(db_session, company["project"], user_messages=MAX_CONTEXT_MESSAGES + 5)
    messages = Nivel1Service(FakeLLM(), db_session).build_llm_messages(conversation)
    assert len(messages) == MAX_CONTEXT_MESSAGES + 1  # system + recientes
    # Lo antiguo llega resumido en el system prompt
    assert conversation.summary.count("mensaje") == 5
    assert conversation.summary in messages[0].content


# ============================================================
# B9 — chat-stream
# ============================================================

def test_b9_stream_events_are_json_and_response_is_saved(client, db_session, company):
    llm = FakeLLM(stream_tokens=["línea 1", "\nlínea 2"])
    client.app.dependency_overrides[nivel1_api.get_llm] = lambda: llm
    resp = client.post(f"/api/v1/nivel1/{company['id']}/chat-stream", json={"message": "hola"},
                       headers=company["headers"])
    events = [json.loads(line[len("data: "):]) for line in resp.text.split("\n\n") if line.startswith("data: ")]
    assert [e["token"] for e in events if "token" in e] == ["línea 1", "\nlínea 2"]
    assert events[-1]["done"] is True and events[-1]["disclaimer"] == AI_DISCLAIMER
    saved = db_session.query(Message).filter_by(role="assistant").one()
    assert saved.content == "línea 1\nlínea 2"


# ============================================================
# B11 — índice vectorial compartido y reconstruido desde la BD
# ============================================================

def test_b11_shared_store_rebuilds_from_database(db_session, company, monkeypatch):
    if db_session.get_bind().dialect.name != "sqlite":
        pytest.skip("índice en memoria: solo con SQLite (en PostgreSQL es pgvector, ver test_wo091)")
    doc = EMSDocument(company_id=company["id"], title="Doc", source_type="text", status="processed")
    db_session.add(doc)
    db_session.flush()
    db_session.add(EMSChunk(document_id=doc.id, company_id=company["id"], chunk_index=0, content="contenido guardado"))
    db_session.commit()

    monkeypatch.setattr(ems_store, "_vector_store", LocalVectorStoreProvider())
    monkeypatch.setattr(ems_store, "_loaded", False)
    store = ems_store.get_vector_store(db_session)
    assert store.count() == 1
    assert ems_store.get_vector_store(db_session) is store


# ============================================================
# B12 — el CEO no inventa resultados de herramientas
# ============================================================

@pytest.mark.asyncio
async def test_b12_ceo_does_not_run_placeholder_tools():
    llm = FakeLLM(chat_replies=[
        '{"available": [], "gaps": ["ventas del trimestre", "mercado"], "needs_more": false}',
        '{"summary": "plan", "priorities": [], "confidence": 0.5}',
    ])
    ems = AsyncMock()
    ems.retrieve_for_llm = AsyncMock(return_value="")
    executor = MagicMock()
    executor.execute = AsyncMock()
    result = await CEOAgent(llm, ems, executor).process("¿Cómo van las ventas?", "c", "u")
    executor.execute.assert_not_called()
    assert result.tools_used == []


# ============================================================
# B13 — DKA no inventa fuentes
# ============================================================

@pytest.mark.asyncio
async def test_b13_acquire_without_urls_does_not_use_demo_sources():
    ems = MagicMock()
    ems.ingest = AsyncMock()
    result = await KnowledgeAcquisitionPipeline(ems).acquire(query="mercado colombiano", company_id="c")
    assert result.sources_scraped == 0
    assert result.errors
    ems.ingest.assert_not_called()


# ============================================================
# B15 — el Nivel 7 es el último
# ============================================================

def test_b15_completing_level_7_does_not_create_level_8(db_session, company):
    project = company["project"]
    GemeloDigitalService(db_session).complete_level(project, 7)
    assert db_session.query(Level).filter_by(project_id=project.id, number=8).count() == 0


# ============================================================
# B16 — EMS: correcciones y archivado
# ============================================================

def _ems(db_session):
    return EnterpriseMemorySystem(db_session, LocalEmbeddingProvider(dim=128), LocalVectorStoreProvider())


def test_b16_correction_lowers_fact_confidence_persistently(db_session, company):
    ems = _ems(db_session)
    fact = ems.add_fact(company_id=company["id"], fact_type="dato", subject="ventas", confidence=0.9)
    ems.record_correction(company_id=company["id"], original_text="x", corrected_text="y", fact_id=fact.id)
    db_session.expire_all()
    assert db_session.query(KnowledgeFact).filter_by(id=fact.id).one().confidence == pytest.approx(0.8)


@pytest.mark.asyncio
async def test_b16_delete_document_archives_instead_of_deleting(db_session, company):
    ems = _ems(db_session)
    result = await ems.ingest(company_id=company["id"], text="Documento a archivar con contenido.", title="Doc")
    assert ems.delete_document(result.document_id) is True
    assert ems.get_document(result.document_id) is None
    assert ems.list_documents(company["id"]) == []
    archived = db_session.query(EMSDocument).filter_by(id=result.document_id).one()
    assert archived.status == "archived"


# ============================================================
# B10 y B18 — código muerto y rutas de base de datos
# ============================================================

def test_b10_broken_memory_service_is_gone():
    import importlib.util
    assert importlib.util.find_spec("app.services.memory") is None


def test_b18_non_sqlite_urls_do_not_create_directories(tmp_path):
    from app.core.database import ensure_sqlite_dir
    ensure_sqlite_dir(f"postgresql://u:p@localhost/{tmp_path}/pg/adan")
    assert not (tmp_path / "pg").exists()
    ensure_sqlite_dir(f"sqlite:///{tmp_path}/lite/adan.db")
    assert (tmp_path / "lite").is_dir()


# ============================================================
# Avisos de IA y respuestas simuladas
# ============================================================

def test_disclaimer_is_added_to_documents_and_ignored_by_gate(db_session, company):
    doc = GemeloDigitalService(db_session).save_diagnosis(company["project"], "Diagnóstico", "Contenido real")
    assert doc.content.endswith(f"{AI_DISCLAIMER}\n")
    assert strip_disclaimer(doc.content) == "Contenido real"
    assert strip_disclaimer(with_disclaimer("x")) == "x"


def test_simulated_integrations_are_labelled(client, company):
    headers = company["headers"]
    stt = client.post("/voice/stt", json={"audio_base64": "AAAA"}, headers=headers).json()
    assert stt["mock"] is True
    sent = client.post("/omnichannel/respond", json={"channel": "web", "recipient_id": "r", "content": "hola"},
                       headers=headers).json()
    assert sent["delivered"] is False and sent["mock"] is True
    gmail = client.post("/integrations/execute", json={"connector_id": "gmail", "action": "list_emails",
                                                       "params": {}}, headers=headers).json()
    assert gmail["mock"] is True
