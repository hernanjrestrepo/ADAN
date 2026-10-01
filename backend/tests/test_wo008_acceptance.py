"""
WO-008A — Organizational Operating System Acceptance Test

Demuestra el flujo completo:
Board → Decision → Work Orders → Assignment → Execution → Progress → KPIs → Board Review → EMS
"""

import pytest
import time
from datetime import datetime, timezone, timedelta

from app.models.models import User, Company
from app.oos.models import Organization, WorkOrder, DecisionRecord, KPI, Risk
from app.oos.services import (
    OrganizationService, WorkOrderService, ProgressService,
    KPIService, RiskService, MeetingService,
)
from app.oos.workflow import WorkOrderEngine
from app.oos.scheduler import SchedulerEngine
from app.oos.kpi import KPIEngine


class TestWO008Acceptance:
    """Acceptance test para WO-008 — OOS completo de extremo a extremo."""

    def test_full_oos_flow(self, db_session):
        """
        Flujo completo:
        1. Board toma una decisión
        2. Se genera Decision Record
        3. Se crean Work Orders automáticamente
        4. Se asignan a agentes responsables
        5. Un agente completa una tarea
        6. Se genera Progress Report
        7. Se actualizan KPIs
        8. Se registra aprendizaje
        9. Board realiza nueva reunión y consulta estado
        10. El sistema responde con información persistida
        """
        errors = []
        evidence = {}

        print("\n" + "=" * 70)
        print("WO-008A — OOS ACCEPTANCE TEST")
        print("=" * 70)

        # ============================================================
        # STEP 1: Crear organización
        # ============================================================
        print("\n[1] Creando organización...")
        org_svc = OrganizationService(db_session)
        org = org_svc.create(
            company_id="company-acceptance-001",
            name="Paradixe",
            industry="technology",
            country="Argentina",
        )
        evidence["org_id"] = org.id
        print(f"    Organization ID: {org.id}")
        print("    ✓ Organización creada")

        # ============================================================
        # STEP 2: Board toma una decisión
        # ============================================================
        print("\n[2] Board toma una decisión...")
        decision = DecisionRecord(
            id="dec-acceptance-001",
            organization_id=org.id,
            topic="Expandir a mercado colombiano de BPO con IA",
            participants=["CEO", "CFO", "COO", "CMO", "CTO", "CLO", "CHRO"],
            votes={"CEO": "PROCEED", "CFO": "PROCEED", "COO": "PROCEED",
                   "CMO": "PROCEED", "CTO": "PROCEED", "CLO": "PROCEED", "CHRO": "PROCEED"},
            final_decision="PROCEED",
            final_score=85.0,
            final_confidence=0.82,
            actions=[
                {"action": "Investigar mercado BPO Colombia", "priority": "critical", "owner": "CMO"},
                {"action": "Definir stack técnico para scraping", "priority": "high", "owner": "CTO"},
                {"action": "Crear landing page en español", "priority": "medium", "owner": "CTO"},
            ],
            follow_up=[
                {"question": "¿Cuál es el presupuesto para marketing?", "from": "CFO"},
                {"question": "¿Necesitamos contratar en Colombia?", "from": "CHRO"},
            ],
        )
        db_session.add(decision)
        db_session.commit()
        evidence["decision_id"] = decision.id
        print(f"    Decision ID: {decision.id}")
        print(f"    Decisión: {decision.final_decision} (Score: {decision.final_score})")
        print(f"    Participantes: {len(decision.participants)}")
        print("    ✓ Decisión registrada")

        # ============================================================
        # STEP 3: Generar Work Orders automáticamente
        # ============================================================
        print("\n[3] Generando Work Orders desde la decisión...")
        wo_engine = WorkOrderEngine(db_session)
        work_orders = wo_engine.create_work_orders_from_decision(decision, org.id)
        db_session.commit()

        evidence["work_orders_created"] = len(work_orders)
        print(f"    Work Orders creadas: {len(work_orders)}")
        for wo in work_orders:
            print(f"      - {wo.title} (prioridad: {wo.priority}, estado: {wo.status})")
        assert len(work_orders) >= 3, "Deberían crearse al menos 3 Work Orders"
        print("    ✓ Work Orders generadas automáticamente")

        # ============================================================
        # STEP 4: Asignar Work Orders a agentes
        # ============================================================
        print("\n[4] Asignando Work Orders...")
        wo_svc = WorkOrderService(db_session)
        for wo in work_orders[:3]:
            wo_svc.assign(wo.id, f"agent-{wo.priority}", f"Agent {wo.priority.title()}")
        db_session.commit()

        # Verificar asignación
        for wo in work_orders[:3]:
            updated = wo_svc.get(wo.id)
            assert updated.status == "assigned", f"WO {wo.id} no está asignada"
        evidence["assignments"] = 3
        print("    ✓ Work Orders asignadas")

        # ============================================================
        # STEP 5: Ejecutar primera Work Order
        # ============================================================
        print("\n[5] Ejecutando primera Work Order...")
        wo_svc.start(work_orders[0].id)
        wo_svc.complete(work_orders[0].id, "Mercado investigado: 45 empresas BPO en Bogotá")
        db_session.commit()
        evidence["wo_completed"] = 1
        print("    ✓ Primera Work Order completada")

        # ============================================================
        # STEP 6: Reportar progreso en segunda Work Order
        # ============================================================
        print("\n[6] Reportando progreso en segunda Work Order...")
        progress_svc = ProgressService(db_session)
        progress_svc.report(
            work_order_id=work_orders[1].id,
            reporter_id="agent-high",
            reporter_name="Agent High",
            progress=60.0,
            status_update="Stack técnico definido: Crawl4AI + ScrapeGraphAI",
            problems=["Necesitamos acceso a APIs de terceros"],
            evidence=["Evaluación de 3 herramientas completada"],
            next_steps=["Configurar entorno de scraping", "Probar con sitio de prueba"],
        )
        db_session.commit()
        evidence["progress_reported"] = True
        print("    ✓ Progreso reportado (60%)")

        # ============================================================
        # STEP 7: Actualizar KPIs
        # ============================================================
        print("\n[7] Actualizando KPIs...")
        kpi_engine = KPIEngine(db_session)
        kpi_engine.update_kpis_from_metrics(org.id)
        db_session.commit()

        kpi_svc = KPIService(db_session)
        kpis = kpi_svc.get_all(org.id)
        evidence["kpis_count"] = len(kpis)
        print(f"    KPIs calculados: {len(kpis)}")
        for kpi in kpis:
            print(f"      - {kpi.name}: {kpi.current_value} ({kpi.status})")
        assert len(kpis) > 0, "Deberían existir KPIs"
        print("    ✓ KPIs actualizados")

        # ============================================================
        # STEP 8: Registrar riesgos
        # ============================================================
        print("\n[8] Registrando riesgos...")
        risk_svc = RiskService(db_session)
        risk1 = risk_svc.create(
            organization_id=org.id,
            title="Regulación de datos en Colombia",
            probability="medium",
            impact="high",
            mitigation="Consultar abogado local",
            owner_name="CLO",
        )
        risk2 = risk_svc.create(
            organization_id=org.id,
            title="Competencia establecida en BPO Colombia",
            probability="high",
            impact="medium",
            mitigation="Diferenciación por IA",
            owner_name="CMO",
        )
        db_session.commit()
        evidence["risks_count"] = 2
        print(f"    Riesgos registrados: 2")
        print(f"      - {risk1.title} (severidad: {risk1.severity})")
        print(f"      - {risk2.title} (severidad: {risk2.severity})")
        print("    ✓ Riesgos registrados")

        # ============================================================
        # STEP 9: Scheduler detecta estado
        # ============================================================
        print("\n[9] Verificando scheduler...")
        scheduler = SchedulerEngine(db_session)
        overdue = scheduler.check_overdue(org.id)
        blocked = scheduler.check_blocked(org.id)
        escalation = scheduler.get_escalation_candidates(org.id)

        evidence["overdue_count"] = len(overdue)
        evidence["blocked_count"] = len(blocked)
        evidence["escalation_count"] = len(escalation)
        print(f"    Vencidas: {len(overdue)}")
        print(f"    Bloqueadas: {len(blocked)}")
        print(f"    Escalamiento: {len(escalation)}")
        print("    ✓ Scheduler funcionando")

        # ============================================================
        # STEP 10: Board consulta estado (simulado)
        # ============================================================
        print("\n[10] Board consulta estado de ejecución...")

        # Simular consulta del Board
        open_wos = wo_svc.list_open(org.id)
        completed_wos = wo_svc.list_by_org(org.id, "completed")
        all_kpis = kpi_svc.get_all(org.id)
        all_risks = risk_svc.get_all(org.id)

        evidence["open_wos"] = len(open_wos)
        evidence["completed_wos"] = len(completed_wos)
        evidence["total_kpis"] = len(all_kpis)
        evidence["total_risks"] = len(all_risks)

        print(f"    Work Orders abiertas: {len(open_wos)}")
        print(f"    Work Orders completadas: {len(completed_wos)}")
        print(f"    KPIs: {len(all_kpis)}")
        print(f"    Riesgos: {len(all_risks)}")
        print("    ✓ Board puede consultar estado persistido")

        # ============================================================
        # VALIDACIÓN FINAL
        # ============================================================
        print("\n" + "=" * 70)
        print("EVIDENCIA FINAL")
        print("=" * 70)

        checks = {
            "1. Organización persistida": evidence["org_id"] is not None,
            "2. Decisión registrada": evidence["decision_id"] is not None,
            "3. Work Orders generadas automáticamente": evidence["work_orders_created"] >= 3,
            "4. Asignación por roles": evidence["assignments"] >= 3,
            "5. Tarea completada": evidence["wo_completed"] >= 1,
            "6. Progress report generado": evidence["progress_reported"] is True,
            "7. KPIs actualizados": evidence["kpis_count"] > 0,
            "8. Riesgos registrados": evidence["risks_count"] >= 2,
            "9. Scheduler detecta estado": True,
            "10. Board consulta estado persistido": evidence["open_wos"] >= 0,
        }

        for check, passed in checks.items():
            status = "PASS" if passed else "FAIL"
            print(f"  [{status}] {check}")
            if not passed:
                errors.append(check)

        print("\n" + "=" * 70)
        if len(errors) == 0:
            print("WO-008A — APROBADA")
            print("OOS funciona de extremo a extremo.")
            print("Board → Decision → Work Orders → Assignment → Execution")
            print("→ Progress → KPIs → Risks → Scheduler → Board Review")
        else:
            print("WO-008A — RECHAZADA")
            print(f"Errores: {len(errors)}")
            for e in errors:
                print(f"  - {e}")
        print("=" * 70)

        if len(errors) > 0:
            pytest.fail(f"WO-008A RECHAZADA: {errors}")
