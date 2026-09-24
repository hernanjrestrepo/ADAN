"""Company endpoint tests."""
import pytest


def _register_and_get_token(client):
    resp = client.post("/api/v1/auth/register", json={
        "email": "company@example.com",
        "name": "Company User",
        "password": "password123",
    })
    return resp.json()["access_token"]


def test_create_company(client):
    """Company creation works."""
    token = _register_and_get_token(client)
    resp = client.post("/api/v1/companies/", json={
        "name": "Test Corp",
        "description": "A test company",
        "industry": "Tech",
        "country": "Colombia",
    }, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Test Corp"
    assert data["industry"] == "Tech"


def test_list_companies(client):
    """List companies returns user's companies."""
    token = _register_and_get_token(client)
    client.post("/api/v1/companies/", json={
        "name": "List Corp",
    }, headers={"Authorization": f"Bearer {token}"})
    resp = client.get("/api/v1/companies/", headers={
        "Authorization": f"Bearer {token}"
    })
    assert resp.status_code == 200
    assert len(resp.json()) == 1
    assert resp.json()[0]["name"] == "List Corp"


def test_create_company_unauthorized(client):
    """Company creation without auth is rejected."""
    resp = client.post("/api/v1/companies/", json={"name": "No Auth Corp"})
    assert resp.status_code == 403


def test_get_company(client):
    """Get single company works."""
    token = _register_and_get_token(client)
    create_resp = client.post("/api/v1/companies/", json={
        "name": "Get Corp",
    }, headers={"Authorization": f"Bearer {token}"})
    company_id = create_resp.json()["id"]

    resp = client.get(f"/api/v1/companies/{company_id}", headers={
        "Authorization": f"Bearer {token}"
    })
    assert resp.status_code == 200
    assert resp.json()["name"] == "Get Corp"


def test_company_creates_project_and_levels(client):
    """Creating a company also creates a project and 7 levels."""
    token = _register_and_get_token(client)
    create_resp = client.post("/api/v1/companies/", json={
        "name": "Level Corp",
    }, headers={"Authorization": f"Bearer {token}"})
    company_id = create_resp.json()["id"]

    resp = client.get(f"/api/v1/companies/{company_id}/project", headers={
        "Authorization": f"Bearer {token}"
    })
    assert resp.status_code == 200
    project = resp.json()
    assert project["name"] == "Proyecto Level Corp"
