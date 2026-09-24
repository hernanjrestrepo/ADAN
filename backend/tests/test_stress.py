"""Stress tests — concurrent user simulation.

Necesitan el backend en localhost:8050 con Ollama. Simulan muchos usuarios desde una sola
IP, así que el servidor debe levantarse con REGISTER_PER_IP_PER_HOUR alto (p. ej. 1000).
"""
import asyncio
import time
import aiohttp
import pytest

BASE_URL = "http://localhost:8050"


async def register_and_create_company(session, user_id):
    """Register a user and create a company."""
    import uuid
    unique_id = f"{user_id}_{uuid.uuid4().hex[:8]}"
    async with session.post(f"{BASE_URL}/api/v1/auth/register", json={
        "email": f"stress{unique_id}@adan.ai",
        "name": f"Stress User {user_id}",
        "password": "stress-pass-2026",
    }) as resp:
        data = await resp.json()
        token = data["access_token"]

    async with session.post(f"{BASE_URL}/api/v1/companies/", json={
        "name": f"StressCorp{user_id}",
        "description": f"Test company {user_id}",
        "industry": "Tech",
        "country": "Colombia",
    }, headers={"Authorization": f"Bearer {token}"}) as resp:
        company = await resp.json()
        return token, company["id"]


async def start_conversation(session, token, company_id):
    """El Board Room delibera sobre la conversación del Nivel 1: sin ella responde 400."""
    async with session.post(f"{BASE_URL}/api/v1/nivel1/{company_id}/chat",
        headers={"Authorization": f"Bearer {token}"},
        json={"message": "Las panaderías de barrio pierden entre 15% y 20% del pan porque no saben cuánto hornear."},
    ) as resp:
        assert resp.status == 200, await resp.text()


async def run_board_room(session, token, company_id):
    """Run Board Room for a company."""
    start = time.monotonic()
    async with session.post(f"{BASE_URL}/api/v1/nivel1/{company_id}/board-room",
        headers={"Authorization": f"Bearer {token}"},
        json={},
    ) as resp:
        duration = time.monotonic() - start
        status = resp.status
        try:
            data = await resp.json()
        except:
            data = {}
        return {"status": status, "duration": duration, "data": data}


@pytest.mark.asyncio
async def test_concurrent_registrations():
    """Test 10 concurrent registrations."""
    async with aiohttp.ClientSession() as session:
        tasks = [register_and_create_company(session, i) for i in range(10)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        successes = [r for r in results if not isinstance(r, Exception)]
        assert len(successes) == 10


@pytest.mark.asyncio
async def test_concurrent_board_room():
    """Test 5 concurrent Board Rooms."""
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=900)) as session:
        # Create users and companies first
        pairs = []
        for i in range(5):
            token, company_id = await register_and_create_company(session, i)
            pairs.append((token, company_id))

        for token, company_id in pairs:
            await start_conversation(session, token, company_id)

        # Run Board Rooms concurrently
        tasks = [run_board_room(session, t, c) for t, c in pairs]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Antes no se verificaba el código: con el token mal formado todo era 401 en 0 s
        assert all(not isinstance(r, Exception) and r["status"] == 200 for r in results), results
        durations = [r["duration"] for r in results]
        if durations:
            avg_duration = sum(durations) / len(durations)
            max_duration = max(durations)
            assert avg_duration < 120  # Should complete within 2 minutes
            print(f"Board Room stress: avg={avg_duration:.1f}s, max={max_duration:.1f}s")
