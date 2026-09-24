"""
WO-003A — Acceptance Test del Cerebro Cognitivo

Solo validar. No modificar código.
Flujo: Registrar → Crear empresa → Ejecutar cognición → Validar evidencia.
"""

import time
import uuid
import pytest



# `client` viene de conftest.py: base de pruebas aislada, no data/adan.db


class TestWO003Acceptance:
    """Acceptance test para WO-003 — Vertical Slice Cognitivo."""

    def test_full_cognitive_flow(self, client):
        """
        Flujo obligatorio de aceptación:
        1. Registrar usuario
        2. Crear empresa
        3. Verificar proyecto y niveles
        4. Ejecutar caso: "Analiza mi empresa y dime los tres problemas más importantes"
        5. Validar evidencia de cada componente
        """
        errors = []
        evidence = {}

        # ============================================================
        # STEP 1: Register user
        # ============================================================
        print("\n[1] Registrando usuario...")
        unique_id = uuid.uuid4().hex[:8]
        resp = client.post("/api/v1/auth/register", json={
            "email": f"acceptance_{unique_id}@test.com",
            "name": "Acceptance Tester",
            "password": "acceptance-pass-2026",
        })
        assert resp.status_code == 201, f"Register failed: {resp.text}"
        token = resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print(f"    Status: {resp.status_code}")
        print("    Usuario registrado")

        # ============================================================
        # STEP 2: Create company
        # ============================================================
        print("\n[2] Creando empresa...")
        resp = client.post("/api/v1/companies/", json={
            "name": "TechStartup Argentina",
            "description": "Startup de tecnologia SaaS para PYMEs en Latinoamerica",
            "industry": "technology",
            "country": "Argentina",
        }, headers=headers)
        assert resp.status_code == 201, f"Create company failed: {resp.text}"
        company_data = resp.json()
        company_id = company_data["id"]
        print(f"    Status: {resp.status_code}")
        print(f"    Company ID: {company_id}")
        print("    Empresa creada")

        # ============================================================
        # STEP 3: Verify project and levels
        # ============================================================
        print("\n[3] Verificando proyecto y niveles...")
        resp = client.get(f"/api/v1/companies/{company_id}/project", headers=headers)
        assert resp.status_code == 200
        project_data = resp.json()
        project_id = project_data["id"]
        print(f"    Project ID: {project_id}")

        resp = client.get(f"/api/v1/nivel1/{company_id}/status", headers=headers)
        assert resp.status_code == 200
        status_data = resp.json()
        levels_count = len(status_data.get("levels", []))
        print(f"    Levels: {levels_count}")
        print("    Proyecto y niveles verificados")

        # ============================================================
        # STEP 4: Execute cognitive flow
        # ============================================================
        print("\n[4] Ejecutando flujo cognitivo...")
        message = "Analiza mi empresa y dime cuales son los tres problemas mas importantes"
        print(f'    Mensaje: "{message}"')

        start_time = time.time()
        resp = client.post("/api/v1/cognitive/think", json={
            "message": message,
            "company_id": company_id,
        }, headers=headers)
        duration_ms = int((time.time() - start_time) * 1000)

        print(f"    Status: {resp.status_code}")
        print(f"    Duration: {duration_ms}ms")

        # ============================================================
        # VALIDATION: HTTP 200
        # ============================================================
        if resp.status_code != 200:
            print(f"    ERROR: {resp.text}")
            errors.append(f"HTTP {resp.status_code}")
            print("\n    WO-003 RECHAZADA — Endpoint fallo")
            pytest.fail(f"WO-003 RECHAZADA: {errors}")

        data = resp.json()

        # ============================================================
        # VALIDATION: Trace ID
        # ============================================================
        trace_id = data.get("trace_id", "")
        print(f"\n    Trace ID: {trace_id}")
        if not trace_id or not trace_id.startswith("trace-"):
            errors.append("Trace ID invalido")
        else:
            evidence["trace_id"] = trace_id

        # ============================================================
        # VALIDATION: Components used
        # ============================================================
        components = data.get("components_used", [])
        required_components = [
            "knowledge_engine",
            "planner",
            "llm",
            "decision_engine",
            "memory_engine",
        ]
        print(f"    Components: {components}")
        for comp in required_components:
            if comp in components:
                print(f"    [OK] {comp}")
            else:
                print(f"    [FAIL] {comp} MISSING")
                errors.append(f"Missing component: {comp}")

        # ============================================================
        # VALIDATION: Response
        # ============================================================
        response_text = data.get("response", "")
        print(f"\n    Response length: {len(response_text)} chars")
        if len(response_text) < 50:
            errors.append("Response too short")
        else:
            evidence["response_length"] = len(response_text)

        # ============================================================
        # VALIDATION: Justification
        # ============================================================
        justification = data.get("justification")
        if justification:
            print(f"    Justification decision: {justification.get('decision')}")
            print(f"    Justification confidence: {justification.get('confidence')}")
            print(f"    Supporting facts: {len(justification.get('supporting_facts', []))}")
            print(f"    Alternatives: {len(justification.get('alternatives', []))}")
            evidence["justification"] = True
        else:
            errors.append("Justification missing")

        # ============================================================
        # VALIDATION: Events published
        # ============================================================
        events_count = data.get("events_published", 0)
        print(f"\n    Events published: {events_count}")
        if events_count < 5:
            errors.append(f"Too few events: {events_count}")
        else:
            evidence["events_count"] = events_count

        # ============================================================
        # VALIDATION: Plan steps
        # ============================================================
        plan_steps = data.get("plan_steps", 0)
        print(f"    Plan steps: {plan_steps}")
        if plan_steps < 1:
            errors.append("No plan steps")
        else:
            evidence["plan_steps"] = plan_steps

        # ============================================================
        # VALIDATION: Knowledge units
        # ============================================================
        knowledge_units = data.get("knowledge_units", 0)
        print(f"    Knowledge units: {knowledge_units}")
        evidence["knowledge_units"] = knowledge_units

        # ============================================================
        # VALIDATION: Quality score
        # ============================================================
        quality_score = data.get("quality_score", 0)
        print(f"    Quality score: {quality_score}")
        if quality_score <= 0:
            errors.append("Zero quality score")
        else:
            evidence["quality_score"] = quality_score

        # ============================================================
        # VALIDATION: Duration
        # ============================================================
        print(f"    Duration: {duration_ms}ms")
        if duration_ms > 30000:
            print("    [WARN] Duration > 30s (slow but not fatal)")
        evidence["duration_ms"] = duration_ms

        # ============================================================
        # FINAL VERDICT
        # ============================================================
        print("\n" + "=" * 60)
        print("EVIDENCIA FINAL")
        print("=" * 60)
        for key, val in evidence.items():
            print(f"  {key}: {val}")

        print("\n" + "=" * 60)
        if len(errors) == 0:
            print("WO-003 — APROBADA")
            print("Todos los componentes funcionan end-to-end.")
            print("=" * 60)
        else:
            print("WO-003 — RECHAZADA")
            print(f"Errores encontrados: {len(errors)}")
            for e in errors:
                print(f"  - {e}")
            print("=" * 60)
            pytest.fail(f"WO-003 RECHAZADA: {errors}")
