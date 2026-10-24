"""@pples: precio con margen del 90 %, compras idempotentes, pago de Niveles y referidos de 7 niveles hacia arriba."""
import hashlib

from app.apples import pricing
from app.core.config import settings


def _user(client, email, ref=None):
    body = {"email": email, "name": "Ana Pérez", "password": "password123", "accept_data_policy": True}
    if ref:
        body["referral_code"] = ref
    token = client.post("/api/v1/auth/register", json=body).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _buy(client, h, apples):
    p = client.post("/api/v1/apples/compras", headers=h, json={"apples": apples}).json()
    return client.post(f"/api/v1/apples/compras/{p['id']}/simular", headers=h, json={"approve": True}).json()


def test_each_level_costs_ten_percent_of_its_price():
    table = pricing.price_table()
    assert len(table["levels"]) == 7
    for lv in table["levels"]:
        # Todo costo (IA, infraestructura, pasarela y referidos) es como máximo el 10 % del precio
        assert lv["total_cost_usd"] <= lv["apples"] * 0.10 + 1e-9
        assert lv["margin"] >= 0.90


def test_a_purchase_credits_once_even_if_confirmed_twice(client):
    h = _user(client, "compra@example.com")
    p = client.post("/api/v1/apples/compras", headers=h, json={"apples": 25}).json()
    assert p["status"] == "pendiente" and p["amount_cop"] == 25 * settings.APPLE_TRM and "simulador=1" in p["checkout_url"]
    url = f"/api/v1/apples/compras/{p['id']}/simular"
    assert client.post(url, headers=h, json={"approve": True}).json()["balance"] == 25
    assert client.post(url, headers=h, json={"approve": True}).json()["balance"] == 25
    # Nadie consulta la compra de otro
    other = _user(client, "otro@example.com")
    assert client.get(f"/api/v1/apples/compras/{p['id']}", headers=other).status_code == 404


def test_paying_a_level_pays_seven_levels_up_and_nothing_for_signing_up(client):
    heads = [_user(client, "u0@example.com")]
    codes = [client.get("/api/v1/apples/red", headers=heads[0]).json()["code"]]
    for i in range(1, 9):  # cadena de 9 personas: u8 paga, ganan u7 (nivel 1) … u1 (nivel 7); u0 no
        heads.append(_user(client, f"u{i}@example.com", ref=codes[-1]))
        codes.append(client.get("/api/v1/apples/red", headers=heads[-1]).json()["code"])
    # Inscribir a alguien no da nada
    assert client.get("/api/v1/apples/billetera", headers=heads[0]).json()["balance"] == 0
    payer = heads[8]
    cid = client.post("/api/v1/companies/", json={"name": "Café Andino"}, headers=payer).json()["id"]
    price = pricing.apples_for(1)
    assert client.post(f"/api/v1/apples/niveles/{cid}/1", headers=payer).status_code == 409  # sin saldo
    _buy(client, payer, price + 5)
    paid = client.post(f"/api/v1/apples/niveles/{cid}/1", headers=payer).json()
    assert paid["balance"] == 5
    assert client.post(f"/api/v1/apples/niveles/{cid}/1", headers=payer).status_code == 409  # una sola vez
    each = round(price * 0.005, 3)
    for i in range(1, 8):
        assert client.get("/api/v1/apples/billetera", headers=heads[i]).json()["balance"] == each
    assert client.get("/api/v1/apples/billetera", headers=heads[0]).json()["balance"] == 0
    red = client.get("/api/v1/apples/red", headers=heads[7]).json()
    assert red["levels"][0]["people"] == 1 and red["levels"][0]["earned"] == each


def test_wompi_events_need_a_valid_signature(client, monkeypatch):
    h = _user(client, "wompi@example.com")
    p = client.post("/api/v1/apples/compras", headers=h, json={"apples": 10}).json()
    monkeypatch.setattr(settings, "WOMPI_EVENTS_SECRET", "secreto_de_prueba")
    tx = {"id": "tx-1", "status": "APPROVED", "reference": p["id"], "amount_in_cents": p["amount_cop"] * 100}
    props = ["transaction.id", "transaction.status", "transaction.amount_in_cents"]
    ts = 1761330000
    checksum = hashlib.sha256(f"tx-1APPROVED{tx['amount_in_cents']}{ts}secreto_de_prueba".encode()).hexdigest()
    event = {"event": "transaction.updated", "data": {"transaction": tx}, "timestamp": ts,
             "signature": {"properties": props, "checksum": "malo"}}
    assert client.post("/api/v1/apples/webhook/wompi", json=event).status_code == 401
    event["signature"]["checksum"] = checksum
    assert client.post("/api/v1/apples/webhook/wompi", json=event).json()["ok"] is True
    assert client.get("/api/v1/apples/billetera", headers=h).json()["balance"] == 10


def test_explore_starts_without_an_idea_and_brand_is_saved(client):
    h = _user(client, "explora@example.com")
    started = client.post("/api/v1/onboarding/start", headers=h, json={"company_name": "", "stage": "explore"}).json()
    assert "No necesitas tener una idea" in started["first_question"]
    assert client.post("/api/v1/onboarding/start", headers=h, json={"company_name": "", "stage": "idea"}).status_code == 422
    cid = started["company_id"]
    logo = "data:image/png;base64,iVBORw0KGgo="
    company = client.put(f"/api/v1/companies/{cid}/marca", headers=h,
                         json={"brand_color": "#0f766e", "brand_accent": "#f59e0b", "logo": logo}).json()
    assert company["brand_color"] == "#0f766e" and company["logo"] == logo and company["origin_stage"] == "explore"
    assert client.put(f"/api/v1/companies/{cid}/marca", headers=h, json={"logo": "javascript:alert(1)"}).status_code == 422


def test_levels_require_apples_only_when_enabled(client, monkeypatch):
    h = _user(client, "exige@example.com")
    cid = client.post("/api/v1/companies/", json={"name": "Taller"}, headers=h).json()["id"]
    monkeypatch.setattr(settings, "APPLES_REQUIRED", True)
    assert client.post(f"/api/v1/nivel1/{cid}/chat", headers=h, json={"message": "Hola"}).status_code == 402
    levels = client.get(f"/api/v1/apples/niveles/{cid}", headers=h).json()
    assert levels["required"] is True and levels["levels"][0]["paid"] is False
