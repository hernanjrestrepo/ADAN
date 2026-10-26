"""Niveles 2 a 7 en la Sala: guion propio, agenda de bienvenida, contexto de los Niveles anteriores y cierre."""
from app.models.models import Level, NivelStatus, Project
from tests.test_discovery import TURN_1, ScriptLLM, _setup, _use


def _open_level(db_session, cid, n):
    project = db_session.query(Project).filter(Project.company_id == cid).first()
    # Las transiciones válidas son bloqueado → activo → cerrado (Patrón B)
    for lv in sorted(db_session.query(Level).filter(Level.project_id == project.id).all(), key=lambda x: x.number):
        if lv.number <= n and lv.status == NivelStatus.BLOCKED:
            lv.status = NivelStatus.ACTIVE
            db_session.commit()
        if lv.number < n and lv.status == NivelStatus.ACTIVE:
            lv.status = NivelStatus.COMPLETED
            db_session.commit()


def test_a_blocked_level_waits_for_the_previous_one(client):
    cid, h = _setup(client, "bloqueado@example.com")
    view = client.get(f"/api/v1/nivel/2/{cid}/status", headers=h).json()
    assert view["status"] == "blocked" and view["level"]["name"] == "Propuesta de Valor"
    assert client.post(f"/api/v1/nivel/2/{cid}/chat", headers=h, json={"message": "hola"}).status_code == 409
    assert client.get(f"/api/v1/nivel/9/{cid}/status", headers=h).status_code == 404


def test_level_two_opens_with_an_agenda_and_works_its_own_script(client, db_session):
    cid, h = _setup(client, "nivel2@example.com")
    # Lo que se entendió en el Nivel 1 llega como contexto al Nivel 2
    _use(client, ScriptLLM([TURN_1]))
    client.post(f"/api/v1/nivel1/{cid}/chat", json={"message": "A las familias les cuesta planear viajes"}, headers=h)
    _open_level(db_session, cid, 2)
    view = client.get(f"/api/v1/nivel/2/{cid}/status", headers=h).json()
    assert view["status"] == "active" and "Bienvenido al Nivel 2" in view["messages"][0]["content"]
    assert view["level"]["deliverables"][0] == "Lienzo de Propuesta de Valor" and view["discovery"]["total"] == 7
    turn = {"respuesta": "La propuesta queda clara: todo el viaje en un solo pago.", "habla": "producto", "mesa": [],
            "temas": [{"id": "propuesta", "estado": "respondido", "resumen": "Todo el viaje en un solo pago", "base": "supuesto"}],
            "evidencia_sugerida": [], "investigar": "", "reaccion": {"agente": "producto", "emocion": "feliz", "frase": "¡Me gusta!"}}
    llm = _use(client, ScriptLLM([turn]))
    msg = client.post(f"/api/v1/nivel/2/{cid}/chat", headers=h, json={"message": "Un solo pago para todo"}).json()["message"]
    assert msg["agent_name"] == "Andrés · Producto"
    system = llm.calls[0][0].content
    assert "Nivel 2, Propuesta de Valor" in system and "Lienzo de Propuesta de Valor" in system
    assert "Lo acordado en los Niveles anteriores" in system and "Familias de ingreso medio-alto" in system
    assert client.get(f"/api/v1/nivel/2/{cid}/status", headers=h).json()["discovery"]["done"] == 1


def test_closing_a_level_needs_the_topics_or_a_reason_and_opens_the_next(client, db_session):
    cid, h = _setup(client, "cierre@example.com")
    _open_level(db_session, cid, 2)
    client.get(f"/api/v1/nivel/2/{cid}/status", headers=h)
    url = f"/api/v1/nivel/2/{cid}/cerrar"
    assert client.post(url, headers=h, json={"reason": ""}).status_code == 409
    res = client.post(url, headers=h, json={"reason": "Validaremos la propuesta lanzando en dos semanas"}).json()
    assert res["closed"] is True and res["next"] == 3 and len(res["pending"]) == 7
    assert client.get(f"/api/v1/nivel/3/{cid}/status", headers=h).json()["status"] == "active"
    evidence = client.get(f"/api/v1/scoring/{cid}/evidence", headers=h).json()
    assert any("cerró el Nivel 2 con temas pendientes" in e["claim"] for e in evidence)
    assert client.post(url, headers=h, json={"reason": "otra vez"}).status_code == 409


def test_adan_proposes_closing_and_a_yes_closes_the_level(client, db_session):
    cid, h = _setup(client, "cierre-si@example.com")
    _open_level(db_session, cid, 2)
    client.get(f"/api/v1/nivel/2/{cid}/status", headers=h)
    topics = ["trabajos", "solucion", "propuesta", "diferencia", "precio", "adopcion", "validacion"]
    turn = {"respuesta": "Tenemos los 7 temas. ¿Cerramos el Nivel y pasamos al piso 3?", "habla": "ceo", "acuerdos": [],
            "temas": [{"id": t, "estado": "respondido", "resumen": "listo", "base": "supuesto"} for t in topics],
            "evidencia_sugerida": [], "investigar": "", "reaccion": {"agente": "ceo", "emocion": "feliz", "frase": "¡Listo!"}}
    _use(client, ScriptLLM([turn]))
    msg = client.post(f"/api/v1/nivel/2/{cid}/chat", headers=h, json={"message": "La validamos con preventa"}).json()["message"]
    assert msg["metadata_json"]["propone_cierre"] is True
    res = client.post(f"/api/v1/nivel/2/{cid}/chat", headers=h, json={"message": "Sí, dale"}).json()
    assert res["closed"]["next"] == 3 and "Nivel 2 cerrado" in res["message"]["content"]
    assert client.get(f"/api/v1/nivel/3/{cid}/status", headers=h).json()["status"] == "active"
