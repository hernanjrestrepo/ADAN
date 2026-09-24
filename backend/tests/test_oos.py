"""
Tests para el Organizational Operating System — WO-008.
"""

import pytest
from datetime import datetime, timezone, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base
from app.models.models import User, Company
from app.ems.models import EMSBase
from app.oos.models import OOSBase, Organization, WorkOrder, DecisionRecord, KPI, Risk
from app.oos.services import (
    OrganizationService, WorkOrderService, ProgressService,
    KPIService, RiskService, MeetingService,
)
from app.oos.workflow import WorkOrderEngine
from app.oos.scheduler import SchedulerEngine
from app.oos.kpi import KPIEngine


# ============================================================
# Fixtures
# ============================================================

@pytest.fixture(scope="function")
def db_session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    EMSBase.metadata.create_all(bind=engine)
    OOSBase.metadata.create_all(bind=engine)
    TestSession = sessionmaker(bind=engine)
    session = TestSession()
    yield session
    session.close()


@pytest.fixture
def test_org(db_session):
    org = Organization(
        id="org-test-001",
        company_id="company-test-001",
        name="Test Organization",
        industry="technology",
    )
    db_session.add(org)
    db_session.commit()
    return org


@pytest.fixture
def org_service(db_session):
    return OrganizationService(db_session)


@pytest.fixture
def wo_service(db_session):
    return WorkOrderService(db_session)


@pytest.fixture
def progress_service(db_session):
    return ProgressService(db_session)


@pytest.fixture
def kpi_service(db_session):
    return KPIService(db_session)


@pytest.fixture
def risk_service(db_session):
    return RiskService(db_session)


# ============================================================
# Tests: Organization Service
# ============================================================

class TestOrganizationService:
    def test_create_org(self, org_service):
        org = org_service.create("company-1", "Test Org")
        assert org.id is not None
        assert org.name == "Test Org"

    def test_get_org(self, org_service, test_org):
        org = org_service.get(test_org.id)
        assert org is not None
        assert org.name == "Test Organization"

    def test_get_by_company(self, org_service, test_org):
        org = org_service.get_by_company("company-test-001")
        assert org is not None


# ============================================================
# Tests: Work Order Service
# ============================================================

class TestWorkOrderService:
    def test_create_from_decision(self, wo_service, test_org):
        wo = wo_service.create_from_decision(
            organization_id=test_org.id,
            decision_id="decision-1",
            title="Test Work Order",
            description="Test description",
            priority="high",
            assigned_to_name="CEO Agent",
        )
        assert wo.id is not None
        assert wo.title == "Test Work Order"
        assert wo.status == "pending"
        assert wo.priority == "high"

    def test_create_task(self, wo_service, test_org):
        wo = wo_service.create_from_decision(
            organization_id=test_org.id,
            decision_id=None,
            title="Parent WO",
        )
        task = wo_service.create_task(wo.id, "Subtask 1")
        assert task.id is not None
        assert task.work_order_id == wo.id

    def test_assign(self, wo_service, test_org):
        wo = wo_service.create_from_decision(
            organization_id=test_org.id,
            decision_id=None,
            title="Test WO",
        )
        assignment = wo_service.assign(wo.id, "agent-ceo", "CEO Agent")
        assert assignment.id is not None
        updated_wo = wo_service.get(wo.id)
        assert updated_wo.status == "assigned"

    def test_start(self, wo_service, test_org):
        wo = wo_service.create_from_decision(
            organization_id=test_org.id,
            decision_id=None,
            title="Test WO",
        )
        wo_service.assign(wo.id, "agent-ceo", "CEO")
        wo_service.start(wo.id)
        updated = wo_service.get(wo.id)
        assert updated.status == "in_progress"
        assert updated.started_at is not None

    def test_complete(self, wo_service, test_org):
        wo = wo_service.create_from_decision(
            organization_id=test_org.id,
            decision_id=None,
            title="Test WO",
        )
        wo_service.complete(wo.id, "Done")
        updated = wo_service.get(wo.id)
        assert updated.status == "completed"
        assert updated.progress == 100.0

    def test_block(self, wo_service, test_org):
        wo = wo_service.create_from_decision(
            organization_id=test_org.id,
            decision_id=None,
            title="Test WO",
        )
        wo_service.block(wo.id, "Waiting for approval")
        updated = wo_service.get(wo.id)
        assert updated.status == "blocked"
        assert updated.blocking_reason == "Waiting for approval"

    def test_list_open(self, wo_service, test_org):
        wo_service.create_from_decision(test_org.id, None, "WO 1")
        wo_service.create_from_decision(test_org.id, None, "WO 2")
        wo = wo_service.create_from_decision(test_org.id, None, "WO 3")
        wo_service.complete(wo.id)

        open_wos = wo_service.list_open(test_org.id)
        assert len(open_wos) == 2

    def test_list_blocked(self, wo_service, test_org):
        wo = wo_service.create_from_decision(test_org.id, None, "Blocked WO")
        wo_service.block(wo.id, "Reason")

        blocked = wo_service.list_blocked(test_org.id)
        assert len(blocked) == 1


# ============================================================
# Tests: Work Order Engine
# ============================================================

class TestWorkOrderEngine:
    def test_create_from_decision(self, db_session, test_org):
        engine = WorkOrderEngine(db_session)
        decision = DecisionRecord(
            id="dec-001",
            organization_id=test_org.id,
            topic="Test Decision",
            final_decision="PROCEED",
            actions=[
                {"action": "Hire 3 engineers", "priority": "high"},
                {"action": "Launch marketing campaign", "priority": "medium"},
            ],
            follow_up=[
                {"question": "What's the budget?", "from": "CFO"},
            ],
        )
        db_session.add(decision)
        db_session.commit()

        wos = engine.create_work_orders_from_decision(decision, test_org.id)

        assert len(wos) == 3  # 2 actions + 1 follow-up
        assert wos[0].title == "Hire 3 engineers"
        assert wos[1].title == "Launch marketing campaign"
        assert "budget" in wos[2].title.lower()

    def test_create_from_actions(self, db_session, test_org):
        engine = WorkOrderEngine(db_session)
        actions = [
            {"title": "Action 1", "priority": "critical"},
            {"title": "Action 2", "priority": "low"},
        ]
        wos = engine.create_work_orders_from_actions(test_org.id, "dec-002", actions)
        assert len(wos) == 2
        assert wos[0].priority == "critical"
        assert wos[1].priority == "low"


# ============================================================
# Tests: Scheduler
# ============================================================

class TestScheduler:
    def test_check_overdue(self, db_session, test_org):
        wo_service = WorkOrderService(db_session)
        wo = wo_service.create_from_decision(
            organization_id=test_org.id,
            decision_id=None,
            title="Overdue WO",
            due_date=datetime.now(timezone.utc) - timedelta(days=3),
        )
        db_session.commit()

        scheduler = SchedulerEngine(db_session)
        overdue = scheduler.check_overdue(test_org.id)
        assert len(overdue) == 1
        assert overdue[0]["days_overdue"] == 3

    def test_check_blocked(self, db_session, test_org):
        wo_service = WorkOrderService(db_session)
        wo = wo_service.create_from_decision(
            organization_id=test_org.id,
            decision_id=None,
            title="Blocked WO",
        )
        wo_service.block(wo.id, "Waiting for approval")
        db_session.commit()

        scheduler = SchedulerEngine(db_session)
        blocked = scheduler.check_blocked(test_org.id)
        assert len(blocked) == 1

    def test_get_reminders(self, db_session, test_org):
        wo_service = WorkOrderService(db_session)
        wo = wo_service.create_from_decision(
            organization_id=test_org.id,
            decision_id=None,
            title="Due Soon",
            due_date=datetime.now(timezone.utc) + timedelta(days=2),
        )
        db_session.commit()

        scheduler = SchedulerEngine(db_session)
        reminders = scheduler.get_reminders(test_org.id)
        assert len(reminders) == 1

    def test_escalation_candidates(self, db_session, test_org):
        wo_service = WorkOrderService(db_session)
        wo = wo_service.create_from_decision(
            organization_id=test_org.id,
            decision_id=None,
            title="Critical Overdue",
            priority="critical",
            due_date=datetime.now(timezone.utc) - timedelta(days=5),
        )
        db_session.commit()

        scheduler = SchedulerEngine(db_session)
        candidates = scheduler.get_escalation_candidates(test_org.id)
        assert len(candidates) == 1
        assert candidates[0]["reason"] == "critical_overdue"


# ============================================================
# Tests: KPI Engine
# ============================================================

class TestKPIEngine:
    def test_calculate_metrics(self, db_session, test_org):
        wo_service = WorkOrderService(db_session)
        wo_service.create_from_decision(test_org.id, None, "WO 1")
        wo2 = wo_service.create_from_decision(test_org.id, None, "WO 2")
        wo_service.complete(wo2.id)
        db_session.commit()

        kpi_engine = KPIEngine(db_session)
        metrics = kpi_engine.calculate_from_work_orders(test_org.id)

        assert metrics["total"] == 2
        assert metrics["completed"] == 1
        assert metrics["completion_rate"] == 50.0

    def test_update_kpis(self, db_session, test_org):
        wo_service = WorkOrderService(db_session)
        wo_service.create_from_decision(test_org.id, None, "WO 1")
        db_session.commit()

        kpi_engine = KPIEngine(db_session)
        kpi_engine.update_kpis_from_metrics(test_org.id)

        kpi_svc = KPIService(db_session)
        kpis = kpi_svc.get_all(test_org.id)
        assert len(kpis) > 0


# ============================================================
# Tests: Integration
# ============================================================

class TestOOSIntegration:
    def test_full_flow(self, db_session, test_org):
        """Test completo: decisión → Work Orders → progreso → KPIs."""
        # 1. Crear decisión
        decision = DecisionRecord(
            id="dec-int-001",
            organization_id=test_org.id,
            topic="Expandir a LATAM",
            final_decision="PROCEED",
            actions=[
                {"action": "Hire LATAM team", "priority": "high"},
                {"action": "Launch website in Spanish", "priority": "medium"},
            ],
            follow_up=[],
        )
        db_session.add(decision)
        db_session.commit()

        # 2. Generar Work Orders
        engine = WorkOrderEngine(db_session)
        wos = engine.create_work_orders_from_decision(decision, test_org.id)
        assert len(wos) == 2

        # 3. Asignar Work Orders
        wo_svc = WorkOrderService(db_session)
        wo_svc.assign(wos[0].id, "agent-ceo", "CEO Agent")
        wo_svc.assign(wos[1].id, "agent-cto", "CTO Agent")
        db_session.commit()

        # 4. Completar primera Work Order
        wo_svc.start(wos[0].id)
        wo_svc.complete(wos[0].id, "Team hired")
        db_session.commit()

        # 5. Reportar progreso en segunda
        progress_svc = ProgressService(db_session)
        progress_svc.report(
            work_order_id=wos[1].id,
            reporter_id="agent-cto",
            reporter_name="CTO Agent",
            progress=50.0,
            status_update="Website 50% done",
        )
        db_session.commit()

        # 6. Actualizar KPIs
        kpi_engine = KPIEngine(db_session)
        kpi_engine.update_kpis_from_metrics(test_org.id)
        db_session.commit()

        # 7. Verificar estado
        kpi_svc = KPIService(db_session)
        kpis = kpi_svc.get_all(test_org.id)
        assert len(kpis) > 0

        # 8. Verificar Work Orders
        open_wos = wo_svc.list_open(test_org.id)
        assert len(open_wos) == 1  # Solo la segunda sigue abierta

        completed_wos = wo_svc.list_by_org(test_org.id, "completed")
        assert len(completed_wos) == 1
