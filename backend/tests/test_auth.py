"""Auth endpoint tests."""
import pytest


def test_health(client):
    """Health endpoint returns OK."""
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["app"] == "ADÁN"


def test_register(client):
    """User registration works."""
    resp = client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "name": "Test User",
        "password": "password123",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert "access_token" in data
    assert data["user"]["email"] == "test@example.com"
    assert data["user"]["name"] == "Test User"


def test_register_duplicate(client):
    """Duplicate email is rejected."""
    client.post("/api/v1/auth/register", json={
        "email": "dup@example.com",
        "name": "User 1",
        "password": "password123",
    })
    resp = client.post("/api/v1/auth/register", json={
        "email": "dup@example.com",
        "name": "User 2",
        "password": "password456",
    })
    assert resp.status_code == 409


def test_login(client):
    """Login with valid credentials returns token."""
    client.post("/api/v1/auth/register", json={
        "email": "login@example.com",
        "name": "Login User",
        "password": "password123",
    })
    resp = client.post("/api/v1/auth/login", json={
        "email": "login@example.com",
        "password": "password123",
    })
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_login_wrong_password(client):
    """Login with wrong password is rejected."""
    client.post("/api/v1/auth/register", json={
        "email": "wrong@example.com",
        "name": "Wrong User",
        "password": "password123",
    })
    resp = client.post("/api/v1/auth/login", json={
        "email": "wrong@example.com",
        "password": "wrongpassword",
    })
    assert resp.status_code == 401


def test_me(client):
    """GET /me returns current user."""
    reg = client.post("/api/v1/auth/register", json={
        "email": "me@example.com",
        "name": "Me User",
        "password": "password123",
    })
    token = reg.json()["access_token"]
    resp = client.get("/api/v1/auth/me", headers={
        "Authorization": f"Bearer {token}"
    })
    assert resp.status_code == 200
    assert resp.json()["email"] == "me@example.com"


def test_me_no_token(client):
    """GET /me without token is rejected."""
    resp = client.get("/api/v1/auth/me")
    assert resp.status_code == 401  # sin credenciales: 401 (antes HTTPBearer devolvía 403)
