"""Comunidad: perfiles públicos opcionales, vitrina con Sello ADÁN, conexiones y Selecciones Paradixe."""
from app.core.config import settings
from tests.test_discovery import _setup


def test_profiles_are_private_until_published(client):
    _, ana = _setup(client, "ana@example.com")
    _, beto = _setup(client, "beto@example.com")
    assert client.get("/api/v1/comunidad/perfil", headers=ana).json()["public"] is False
    client.put("/api/v1/comunidad/perfil", headers=ana, json={"display_name": "Ana", "headline": "Fundadora", "kind": "emprendedor"})
    assert client.get("/api/v1/comunidad/personas", headers=beto).json() == []
    client.put("/api/v1/comunidad/perfil", headers=ana, json={"display_name": "Ana", "kind": "inversionista", "public": True,
                                                              "ticket_min_usd": 25000, "stages": ["idea", "inventada"]})
    people = client.get("/api/v1/comunidad/personas?kind=inversionista", headers=beto).json()
    assert people[0]["display_name"] == "Ana" and people[0]["stages"] == ["idea"]


def test_a_listing_carries_the_adan_seal_and_can_be_found(client):
    cid, ana = _setup(client, "vitrina@example.com")
    _, beto = _setup(client, "visitante@example.com")
    listing = client.put(f"/api/v1/comunidad/mis-empresas/{cid}", headers=ana, json={
        "tagline": "Viajes con IA", "stage": "validacion", "looking_for": ["inversion", "otra"], "amount_sought_usd": 50000}).json()
    assert listing["seal"]["current_level"] == 1 and listing["seal"]["levels_closed"] == []
    assert listing["looking_for"] == ["inversion"] and listing["mine"] is True
    found = client.get("/api/v1/comunidad/empresas?looking_for=inversion&q=viajes", headers=beto).json()
    assert [x["id"] for x in found] == [listing["id"]] and found[0]["mine"] is False
    # Nadie publica la empresa de otro
    assert client.put(f"/api/v1/comunidad/mis-empresas/{cid}", headers=beto, json={}).status_code == 404


def test_contact_details_are_shared_only_after_accepting(client):
    cid, ana = _setup(client, "duena@example.com")
    _, inv = _setup(client, "inversor@example.com")
    listing = client.put(f"/api/v1/comunidad/mis-empresas/{cid}", headers=ana, json={"stage": "idea"}).json()
    req = client.post("/api/v1/comunidad/conexiones", headers=inv, json={"kind": "interes_inversion", "listing_id": listing["id"],
                                                                          "message": "Me interesa"}).json()
    assert req["status"] == "pendiente" and req["other_email"] is None
    inbox = client.get("/api/v1/comunidad/conexiones", headers=ana).json()
    assert inbox["received"][0]["message"] == "Me interesa" and inbox["received"][0]["listing_name"]
    assert client.post(f"/api/v1/comunidad/conexiones/{req['id']}/responder", headers=inv, json={"accept": True}).status_code == 403
    client.post(f"/api/v1/comunidad/conexiones/{req['id']}/responder", headers=ana, json={"accept": True})
    sent = client.get("/api/v1/comunidad/conexiones", headers=inv).json()["sent"][0]
    assert sent["status"] == "aceptada" and sent["other_email"] == "duena@example.com"
    # No se conecta consigo mismo
    assert client.post("/api/v1/comunidad/conexiones", headers=ana, json={"kind": "contacto", "listing_id": listing["id"]}).status_code == 400


def test_only_paradixe_curators_select_companies(client, monkeypatch):
    cid, ana = _setup(client, "seleccion@example.com")
    _, cur = _setup(client, "curador@paradixe.xyz")
    listing = client.put(f"/api/v1/comunidad/mis-empresas/{cid}", headers=ana, json={}).json()
    url = f"/api/v1/comunidad/empresas/{listing['id']}/seleccion"
    assert client.post(url, headers=cur, json={"selected": True}).status_code == 403
    monkeypatch.setattr(settings, "PARADIXE_CURATORS", "curador@paradixe.xyz")
    assert client.get("/api/v1/comunidad/perfil", headers=cur).json()["is_curator"] is True
    picked = client.post(url, headers=cur, json={"selected": True, "note": "Equipo y evidencia sólidos"}).json()
    assert picked["paradixe_selection"] is True
    assert client.get("/api/v1/comunidad/empresas?seleccion=true", headers=ana).json()[0]["selection_note"] == "Equipo y evidencia sólidos"
