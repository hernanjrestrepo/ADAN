"""Economía de IA: el Board no se repite sin motivo, y los precios y márgenes salen de los costos medidos."""
import pytest

from app.core.config import settings
from app.models.models import Event
from tests.test_discovery import BoardLLM, _setup, _use


def _boards(db_session):
    db_session.expire_all()
    return db_session.query(Event).filter(Event.event_type == "board_room_completed").count()


def test_diagnosis_reuses_the_current_board_instead_of_running_another(client, db_session):
    cid, headers = _setup(client, "unboard@example.com")
    llm = _use(client, BoardLLM())
    client.post(f"/api/v1/nivel1/{cid}/chat", json={"message": "A las familias les cuesta planear viajes"},
                headers=headers)
    assert client.post(f"/api/v1/nivel1/{cid}/board-room", headers=headers).status_code == 200
    assert _boards(db_session) == 1
    calls = len(llm.board_prompts)

    diagnosis = client.post(f"/api/v1/nivel1/{cid}/diagnosis", headers=headers)
    assert diagnosis.status_code == 200
    assert _boards(db_session) == 1               # no se ejecutó otro Board
    assert len(llm.board_prompts) == calls        # ni una llamada de votos de más

    # Si el cliente aporta algo nuevo, el Board anterior ya no vale y el diagnóstico corre uno nuevo
    client.post(f"/api/v1/nivel1/{cid}/chat", json={"message": "Entrevisté a 15 familias más"}, headers=headers)
    assert client.post(f"/api/v1/nivel1/{cid}/diagnosis", headers=headers).status_code == 200
    assert _boards(db_session) == 2


def test_diagnosis_without_a_board_runs_exactly_one(client, db_session):
    cid, headers = _setup(client, "sinboardprevio@example.com")
    _use(client, BoardLLM())
    client.post(f"/api/v1/nivel1/{cid}/chat", json={"message": "A las familias les cuesta planear viajes"},
                headers=headers)
    assert client.post(f"/api/v1/nivel1/{cid}/diagnosis", headers=headers).status_code == 200
    assert _boards(db_session) == 1


def test_structured_output_schemas_use_only_what_claude_accepts():
    """La API de Claude rechaza minimum/maximum en enteros (400 visto con la clave real)."""
    from app.arena import service as arena
    from app.nivel1 import board_room

    schemas = [value for module in (board_room, arena) for name, value in vars(module).items()
               if name.endswith("_SCHEMA") and isinstance(value, dict)]
    assert len(schemas) >= 3

    def walk(node):
        if isinstance(node, dict):
            if node.get("type") == "integer":
                assert not {"minimum", "maximum"} & set(node), node
            for value in node.values():
                walk(value)

    for schema in schemas:
        walk(schema)


# ============================================================
# Migración 0013: cada persona conserva su valor en dólares
# ============================================================

def test_rescale_migration_multiplies_balances_by_1000_and_back(tmp_path):
    from alembic import command
    from sqlalchemy import create_engine, text

    from app.core.migrations import alembic_config

    engine = create_engine(f"sqlite:///{tmp_path / 'm.db'}")
    with engine.begin() as conn:
        command.upgrade(alembic_config(conn), "0012")
        conn.execute(text("INSERT INTO apple_movements (id, user_id, kind, amount, reference, detail, created_at) "
                          "VALUES ('m1', 'u1', 'compra', 25, 'p1', 'x', '2026-10-20'), "
                          "('m2', 'u1', 'nivel', -5, 'c:1', 'x', '2026-10-21'), "
                          "('m3', 'u2', 'referido', 0.025, 'c:1', 'x', '2026-10-21')"))
        conn.execute(text("INSERT INTO apple_purchases (id, user_id, apples, amount_cop, trm, provider, status, "
                          "checkout_url, created_at) VALUES ('p1', 'u1', 25, 100000, 4000, 'wompi', 'aprobada', '', "
                          "'2026-10-20')"))
        conn.execute(text("INSERT INTO apple_level_unlocks (id, company_id, level_number, user_id, apples, created_at) "
                          "VALUES ('l1', 'c', 1, 'u1', 5, '2026-10-21')"))
        command.upgrade(alembic_config(conn), "0013")
        amounts = {r[0]: float(r[1]) for r in conn.execute(text("SELECT id, amount FROM apple_movements"))}
        assert amounts == {"m1": 25_000, "m2": -5_000, "m3": 25}                       # 25 → 25.000; 0,025 → 25
        assert conn.execute(text("SELECT apples, amount_cop FROM apple_purchases")).one() == (25_000, 100000)
        assert float(conn.execute(text("SELECT apples FROM apple_level_unlocks")).scalar()) == 5_000
        command.downgrade(alembic_config(conn), "0012")
        assert {r[0]: float(r[1]) for r in conn.execute(text("SELECT id, amount FROM apple_movements"))} == {
            "m1": 25, "m2": -5, "m3": 0.025}
        assert conn.execute(text("SELECT apples FROM apple_purchases")).scalar() == 25


# ============================================================
# Modo inteligente: catálogo, selector costo-beneficio y OpenRouter
# ============================================================

ALL = {"anthropic", "kimi", "openrouter", "ollama"}


def test_selector_picks_the_cheapest_model_that_meets_the_task():
    from app.ai import catalog

    def pick(task, **kw):
        return catalog.select(task, providers=kw.pop("providers", ALL), **kw).spec

    assert pick("clasificar").quality >= 2 and pick("clasificar").json
    assert pick("conversacion").quality >= 3
    # Lo que decide la plata del cliente no baja de calidad 4, aunque haya modelos más baratos
    assert pick("decision").quality >= 4 and pick("codigo_mvp").quality >= 4 and pick("codigo_mvp").tools
    # Más calidad exigida nunca sale más barato
    cheap = catalog.select("conversacion", providers=ALL)
    better = catalog.select("conversacion", providers=ALL, min_quality=4)
    assert better.est_cost_usd >= cheap.est_cost_usd and better.spec.quality >= 4
    assert pick("vision").vision


def test_selector_only_uses_providers_with_keys_and_never_lowers_quality_silently():
    from app.ai import catalog

    with pytest.raises(LookupError):      # solo Ollama (calidad 1): no alcanza para una decisión
        catalog.select("decision", providers={"ollama"})
    assert catalog.select("decision", providers={"anthropic"}).spec.provider == "anthropic"
    assert catalog.select("decision", providers={"openrouter"}).spec.provider == "openrouter"
    # Excluir el elegido da el siguiente, no el mismo
    first = catalog.select("conversacion", providers=ALL)
    second = catalog.select("conversacion", providers=ALL, exclude=(first.spec.id,))
    assert second.spec.id != first.spec.id and second.est_cost_usd >= first.est_cost_usd


def test_selector_handles_images_and_has_no_video_provider_yet():
    from app.ai import catalog

    draft = catalog.select("imagen", providers=ALL, images=4)
    final = catalog.select("imagen_final", providers=ALL, images=4)
    assert draft.spec.modality == final.spec.modality == "image"
    assert final.spec.quality >= 4 and final.est_cost_usd >= draft.est_cost_usd > 0
    with pytest.raises(LookupError, match="video"):
        catalog.select("video", providers=ALL)


def test_catalog_prices_are_dated_and_kimi_uses_the_configured_price(monkeypatch):
    from app.ai import catalog

    assert catalog._raw()["as_of"] and "ASIGNADO" in catalog._raw()["source"]
    kimi = next(m for m in catalog.load() if m.provider == "kimi")
    assert (kimi.input_per_m, kimi.output_per_m) == (settings.KIMI_PRICE_INPUT, settings.KIMI_PRICE_OUTPUT)
    haiku = next(m for m in catalog.load() if m.model == "anthropic/claude-haiku-5.5")
    assert catalog.estimate_cost(haiku, 1_000_000, 1_000_000) == 0.10 + 0.50


def test_router_uses_the_selector_only_when_smart_routing_is_on(monkeypatch):
    from app.ai import router

    monkeypatch.setattr(settings, "OPENROUTER_API_KEY", "sk-or-prueba")
    monkeypatch.setattr(settings, "ANTHROPIC_API_KEY", "")
    monkeypatch.setattr(settings, "KIMI_API_KEY", "")
    monkeypatch.setattr(settings, "LLM_SMART_ROUTING", False)
    assert router.smart_choice("complex") is None            # apagado: nada cambia
    monkeypatch.setattr(settings, "LLM_SMART_ROUTING", True)
    choice = router.smart_choice("complex")
    assert choice.spec.provider == "openrouter" and choice.spec.quality >= 4
    assert router.tier_model("complex") == choice.spec.model
    assert router.smart_choice("simple") is None             # lo simple sigue en Ollama
    assert router._smart_factory("complex").__class__.__name__ == "OpenRouterAdapter"
    monkeypatch.setattr(settings, "OPENROUTER_API_KEY", "")
    assert router.smart_choice("complex") is None and router._smart_factory("complex") is None


@pytest.mark.asyncio
async def test_openrouter_adapter_reads_the_real_cost_and_asks_for_structured_output():
    import httpx

    from app.ai.base import LLMMessage
    from app.ai.openrouter_adapter import OpenRouterAdapter

    seen = {}

    def handler(request):
        seen["body"] = __import__("json").loads(request.content)
        seen["auth"] = request.headers["authorization"]
        return httpx.Response(200, json={"model": "anthropic/claude-haiku-5.5", "choices": [
            {"message": {"content": '{"vote": "STOP"}'}, "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 1000, "completion_tokens": 400, "cost": 0.0123}})

    adapter = OpenRouterAdapter(api_key="k", client=httpx.AsyncClient(transport=httpx.MockTransport(handler)))
    r = await adapter.chat_json([LLMMessage("user", "x")], {"type": "object"}, model="anthropic/claude-haiku-5.5",
                                max_tokens=1500)
    assert seen["auth"] == "Bearer k"
    assert seen["body"]["response_format"]["json_schema"]["strict"] is True
    assert seen["body"]["max_tokens"] >= 4000                       # margen para el razonamiento
    assert r.parsed == {"vote": "STOP"} and r.provider == "openrouter" and r.cost_usd == 0.0123


# ============================================================
# Economía: casos de MVP y margen de los 7 Niveles
# ============================================================

def test_mvp_cases_price_at_90_percent_and_never_use_a_model_below_the_asked_quality():
    from app.apples import economia

    cases = economia.mvp_cases({"anthropic", "kimi", "openrouter"})
    assert {c["size"] for c in cases} == {"landing", "app", "plataforma"}
    for c in cases:
        assert c["price_usd"] == pytest.approx(c["cost_usd"] / 0.10, abs=0.06)        # costo ÷ 0,10 = 90 %
        assert c["quality"] >= c["min_quality"]
        assert abs(c["apples"] - c["price_usd"] * 1000) < 10
    landing = {c["min_quality"]: c for c in cases if c["size"] == "landing"}
    assert landing[4]["cost_usd"] > landing[3]["cost_usd"]                            # más calidad, más costo


def test_seven_levels_at_45_dollars_need_cheap_models_and_light_infrastructure_for_90_percent():
    from app.ai import catalog
    from app.apples import economia

    haiku = next(m for m in catalog.load() if m.model == "anthropic/claude-haiku-5.5")
    today = economia.seven_levels()
    assert today["price_usd"] == 45 and today["margin"] < 0.90 and not today["meets_target"]
    assert economia.infra_for_target() < 0                      # con Kimi y US$ 45 no alcanza ni sin infraestructura
    assert economia.seven_levels(haiku, infra_per_level=0.15)["meets_target"]
    assert economia.infra_for_target(haiku) > 0.15
    # La misma infraestructura con un modelo caro empeora el margen
    sonnet = next(m for m in catalog.load() if m.model == "anthropic/claude-sonnet-5.5")
    assert economia.seven_levels(sonnet, 0.15)["margin"] < economia.seven_levels(haiku, 0.15)["margin"]
    # Las comisiones (Wompi y red) siempre se descuentan: el margen después de comisiones es menor
    assert economia.seven_levels(haiku, 0.15)["margin_after_fees"] < economia.seven_levels(haiku, 0.15)["margin"]
