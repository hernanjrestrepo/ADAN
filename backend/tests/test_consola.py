"""Consola de Paradixe: revisar una cuenta en solo lectura, borrar cuentas y empresas, y el mapa de visitas."""
from app.core.config import settings

CSRF = {"X-Requested-With": "adan"}


def _register(client, email):
    r = client.post("/api/v1/auth/register", json={"email": email, "name": email.split("@")[0], "password": "password123",
                                                    "accept_data_policy": True})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def test_the_admin_reviews_an_account_read_only_and_comes_back(client, monkeypatch):
    monkeypatch.setattr(settings, "PARADIXE_SUPERADMINS", "jefe@paradixe.xyz")
    founder = _register(client, "fundadora@example.com")
    cid = client.post("/api/v1/companies/", json={"name": "Vitrina"}, headers=founder).json()["id"]
    client.cookies.clear()
    client.post("/api/v1/auth/register", json={"email": "jefe@paradixe.xyz", "name": "Jefe", "password": "password123",
                                                "accept_data_policy": True})  # deja la cookie del superadmin
    uid = next(u["id"] for u in client.get("/api/v1/admin/usuarios?q=fundadora").json())
    assert client.post(f"/api/v1/admin/usuarios/{uid}/entrar", headers=CSRF).status_code == 204
    me = client.get("/api/v1/auth/me").json()
    assert me["email"] == "fundadora@example.com" and me["revisando_desde"] == "jefe@paradixe.xyz"
    assert any(c["id"] == cid for c in client.get("/api/v1/companies/").json())  # ve lo de ella
    blocked = client.post("/api/v1/companies/", json={"name": "Otra"}, headers=CSRF)
    assert blocked.status_code == 403 and "solo lectura" in blocked.json()["detail"]
    assert client.post("/api/v1/auth/logout", headers=CSRF).status_code == 204  # «salir» = volver, sin cerrarle la sesión
    assert client.get("/api/v1/auth/me").json()["email"] == "jefe@paradixe.xyz"
    assert client.get("/api/v1/auth/me", headers=founder).status_code == 200  # su sesión sigue viva


def test_deleting_companies_and_accounts_needs_the_exact_name(client, monkeypatch):
    monkeypatch.setattr(settings, "PARADIXE_SUPERADMINS", "jefe@paradixe.xyz")
    admin = _register(client, "jefe@paradixe.xyz")
    founder = _register(client, "borrar@example.com")
    cid = client.post("/api/v1/companies/", json={"name": "Empresa Prueba"}, headers=founder).json()["id"]
    client.get(f"/api/v1/nivel1/{cid}/status", headers=founder)  # crea Niveles, conversación y mensajes
    url = f"/api/v1/admin/empresas/{cid}"
    assert client.request("DELETE", url, headers=admin, json={"confirmar": "otra"}).status_code == 422
    assert client.request("DELETE", url, headers=admin, json={"confirmar": "empresa prueba"}).json()["deleted"] is True
    assert all(c["id"] != cid for c in client.get("/api/v1/admin/empresas", headers=admin).json())
    uid = next(u["id"] for u in client.get("/api/v1/admin/usuarios?q=borrar", headers=admin).json())
    me_id = next(u["id"] for u in client.get("/api/v1/admin/usuarios?q=jefe", headers=admin).json())
    assert client.request("DELETE", f"/api/v1/admin/usuarios/{me_id}", headers=admin,
                          json={"confirmar": "jefe@paradixe.xyz"}).status_code == 409
    assert client.request("DELETE", f"/api/v1/admin/usuarios/{uid}", headers=admin,
                          json={"confirmar": "borrar@example.com"}).json()["deleted"] is True
    assert client.get("/api/v1/auth/me", headers=founder).status_code == 401


def test_visits_feed_the_map(client, monkeypatch):
    monkeypatch.setattr(settings, "PARADIXE_SUPERADMINS", "jefe@paradixe.xyz")
    admin = _register(client, "jefe@paradixe.xyz")
    for country, path in (("CO", "/dashboard"), ("CO", "/nivel/3/abc123abc123abc123abc"), ("US", "/login")):
        client.post("/api/v1/visitas", json={"ruta": path, "referente": "https://google.com/search"},
                    headers={"cf-ipcountry": country, "user-agent": "Mozilla iPhone"})
    stats = client.get("/api/v1/admin/visitas?dias=7", headers=admin).json()
    assert stats["visitas"] == 3 and stats["paises"][0] == {"pais": "CO", "visitas": 2, "visitantes": 1}
    assert {"ruta": "/nivel/3", "visitas": 1} in stats["paginas"] and stats["moviles"] == 3
    assert stats["referentes"][0]["origen"] == "google.com"
    assert client.get("/api/v1/admin/visitas", headers=_register(client, "x@example.com")).status_code == 403
