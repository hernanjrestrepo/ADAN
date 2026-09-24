"""
OOS Services — Servicios del Sistema Operativo Organizacional.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.oos.models import (
    Organization, WorkOrder, Task, Assignment, DecisionRecord,
    KPI, Risk, ProgressReport, Meeting, MeetingMinute, Objective,
    Initiative,
)


class OrganizationService:
    """Servicio de organización."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, company_id: str, name: str, **kwargs) -> Organization:
        org = Organization(
            id=str(uuid.uuid4()),
            company_id=company_id,
            name=name,
            **kwargs,
        )
        self.db.add(org)
        self.db.commit()
        return org

    def get(self, org_id: str) -> Organization | None:
        return self.db.query(Organization).filter(Organization.id == org_id).first()

    def get_by_company(self, company_id: str) -> Organization | None:
        return self.db.query(Organization).filter(
            Organization.company_id == company_id
        ).first()


class WorkOrderService:
    """Servicio de Work Orders."""

    def __init__(self, db: Session):
        self.db = db

    def create_from_decision(
        self,
        organization_id: str,
        decision_id: str | None,
        title: str,
        description: str = "",
        priority: str = "medium",
        assigned_to: str | None = None,
        assigned_to_name: str | None = None,
        due_date: datetime | None = None,
        dependencies: list[str] | None = None,
    ) -> WorkOrder:
        """Crea una Work Order desde una decisión del Board."""
        wo = WorkOrder(
            id=str(uuid.uuid4()),
            organization_id=organization_id,
            decision_id=decision_id,
            title=title,
            description=description,
            priority=priority,
            assigned_to=assigned_to,
            assigned_to_name=assigned_to_name,
            due_date=due_date,
            dependencies=dependencies or [],
            status="pending" if not assigned_to else "assigned",
        )
        self.db.add(wo)
        self.db.flush()
        return wo

    def create_task(
        self,
        work_order_id: str,
        title: str,
        description: str | None = None,
        assigned_to: str | None = None,
        assigned_to_name: str | None = None,
    ) -> Task:
        """Crea una tarea dentro de una Work Order."""
        task = Task(
            id=str(uuid.uuid4()),
            work_order_id=work_order_id,
            title=title,
            description=description,
            assigned_to=assigned_to,
            assigned_to_name=assigned_to_name,
        )
        self.db.add(task)
        self.db.flush()
        return task

    def assign(self, work_order_id: str, agent_id: str, agent_name: str) -> Assignment:
        """Asigna una Work Order a un agente."""
        wo = self.db.query(WorkOrder).filter(WorkOrder.id == work_order_id).first()
        if wo:
            wo.assigned_to = agent_id
            wo.assigned_to_name = agent_name
            wo.status = "assigned"

        assignment = Assignment(
            id=str(uuid.uuid4()),
            work_order_id=work_order_id,
            assigned_to=agent_id,
            assigned_to_name=agent_name,
            assigned_to_type="agent",
            accepted_at=datetime.now(timezone.utc),
        )
        self.db.add(assignment)
        self.db.flush()
        return assignment

    def start(self, work_order_id: str):
        """Marca una Work Order como en progreso."""
        wo = self.db.query(WorkOrder).filter(WorkOrder.id == work_order_id).first()
        if wo:
            wo.status = "in_progress"
            wo.started_at = datetime.now(timezone.utc)
            self.db.flush()

    def complete(self, work_order_id: str, result: str = ""):
        """Marca una Work Order como completada."""
        wo = self.db.query(WorkOrder).filter(WorkOrder.id == work_order_id).first()
        if wo:
            wo.status = "completed"
            wo.completed_at = datetime.now(timezone.utc)
            wo.progress = 100.0
            wo.result = result
            self.db.flush()

    def block(self, work_order_id: str, reason: str):
        """Bloquea una Work Order."""
        wo = self.db.query(WorkOrder).filter(WorkOrder.id == work_order_id).first()
        if wo:
            wo.status = "blocked"
            wo.blocking_reason = reason
            self.db.flush()

    def update_progress(self, work_order_id: str, progress: float):
        """Actualiza el progreso de una Work Order."""
        wo = self.db.query(WorkOrder).filter(WorkOrder.id == work_order_id).first()
        if wo:
            wo.progress = min(progress, 100.0)
            if progress >= 100:
                wo.status = "completed"
                wo.completed_at = datetime.now(timezone.utc)
            self.db.flush()

    def get(self, work_order_id: str) -> WorkOrder | None:
        return self.db.query(WorkOrder).filter(WorkOrder.id == work_order_id).first()

    def list_by_org(self, organization_id: str, status: str | None = None) -> list[WorkOrder]:
        query = self.db.query(WorkOrder).filter(WorkOrder.organization_id == organization_id)
        if status:
            query = query.filter(WorkOrder.status == status)
        return query.order_by(WorkOrder.created_at.desc()).all()

    def list_open(self, organization_id: str) -> list[WorkOrder]:
        """Work Orders abiertas (no completadas ni canceladas)."""
        return self.db.query(WorkOrder).filter(
            WorkOrder.organization_id == organization_id,
            WorkOrder.status.notin_(["completed", "cancelled"]),
        ).all()

    def list_blocked(self, organization_id: str) -> list[WorkOrder]:
        """Work Orders bloqueadas."""
        return self.db.query(WorkOrder).filter(
            WorkOrder.organization_id == organization_id,
            WorkOrder.status == "blocked",
        ).all()


class ProgressService:
    """Servicio de progreso y reportes."""

    def __init__(self, db: Session):
        self.db = db

    def report(
        self,
        work_order_id: str,
        reporter_id: str,
        reporter_name: str,
        progress: float,
        status_update: str,
        problems: list[str] | None = None,
        evidence: list[str] | None = None,
        next_steps: list[str] | None = None,
    ) -> ProgressReport:
        """Genera un reporte de progreso."""
        report = ProgressReport(
            id=str(uuid.uuid4()),
            work_order_id=work_order_id,
            reporter_id=reporter_id,
            reporter_name=reporter_name,
            progress=progress,
            status_update=status_update,
            problems=problems or [],
            evidence=evidence or [],
            next_steps=next_steps or [],
        )
        self.db.add(report)

        # Actualizar progreso de la Work Order
        wo = self.db.query(WorkOrder).filter(WorkOrder.id == work_order_id).first()
        if wo:
            wo.progress = progress
            self.db.flush()

        return report


class KPIService:
    """Servicio de KPIs."""

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        organization_id: str,
        name: str,
        category: str,
        current_value: float = 0.0,
        target_value: float | None = None,
        unit: str | None = None,
        **kwargs,
    ) -> KPI:
        kpi = KPI(
            id=str(uuid.uuid4()),
            organization_id=organization_id,
            name=name,
            category=category,
            current_value=current_value,
            target_value=target_value,
            unit=unit,
            **kwargs,
        )
        self.db.add(kpi)
        self.db.flush()
        return kpi

    def update_value(self, kpi_id: str, new_value: float):
        """Actualiza el valor de un KPI y registra en historial."""
        kpi = self.db.query(KPI).filter(KPI.id == kpi_id).first()
        if kpi:
            history = kpi.history or []
            history.append({
                "date": datetime.now(timezone.utc).isoformat(),
                "value": kpi.current_value,
            })
            kpi.history = history
            kpi.current_value = new_value

            # Verificar si se alcanzó el objetivo
            if kpi.target_value is not None:
                if kpi.direction == "higher_better" and new_value >= kpi.target_value:
                    kpi.status = "achieved"
                elif kpi.direction == "lower_better" and new_value <= kpi.target_value:
                    kpi.status = "achieved"

            self.db.flush()

    def get_all(self, organization_id: str) -> list[KPI]:
        return self.db.query(KPI).filter(
            KPI.organization_id == organization_id
        ).all()

    def get_by_category(self, organization_id: str, category: str) -> list[KPI]:
        return self.db.query(KPI).filter(
            KPI.organization_id == organization_id,
            KPI.category == category,
        ).all()


class RiskService:
    """Servicio de riesgos."""

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        organization_id: str,
        title: str,
        probability: str = "medium",
        impact: str = "medium",
        mitigation: str | None = None,
        owner_name: str | None = None,
        **kwargs,
    ) -> Risk:
        severity = self._calculate_severity(probability, impact)
        risk = Risk(
            id=str(uuid.uuid4()),
            organization_id=organization_id,
            title=title,
            probability=probability,
            impact=impact,
            severity=severity,
            mitigation=mitigation,
            owner_name=owner_name,
            **kwargs,
        )
        self.db.add(risk)
        self.db.flush()
        return risk

    def _calculate_severity(self, probability: str, impact: str) -> float:
        prob_map = {"high": 0.9, "medium": 0.5, "low": 0.2}
        impact_map = {"high": 0.9, "medium": 0.5, "low": 0.2}
        return prob_map.get(probability, 0.5) * impact_map.get(impact, 0.5)

    def get_all(self, organization_id: str) -> list[Risk]:
        return self.db.query(Risk).filter(
            Risk.organization_id == organization_id
        ).all()

    def get_active(self, organization_id: str) -> list[Risk]:
        return self.db.query(Risk).filter(
            Risk.organization_id == organization_id,
            Risk.status.notin_(["mitigated", "accepted"]),
        ).all()

    def mitigate(self, risk_id: str):
        risk = self.db.query(Risk).filter(Risk.id == risk_id).first()
        if risk:
            risk.status = "mitigated"
            self.db.flush()


class MeetingService:
    """Servicio de reuniones."""

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        organization_id: str,
        title: str,
        participants: list[str] | None = None,
        agenda: list[str] | None = None,
        **kwargs,
    ) -> Meeting:
        meeting = Meeting(
            id=str(uuid.uuid4()),
            organization_id=organization_id,
            title=title,
            participants=participants or [],
            agenda=agenda or [],
            **kwargs,
        )
        self.db.add(meeting)
        self.db.flush()
        return meeting

    def add_minute(
        self,
        meeting_id: str,
        topic: str,
        discussion: str | None = None,
        decision: str | None = None,
        action_item: str | None = None,
        owner: str | None = None,
    ) -> MeetingMinute:
        minute = MeetingMinute(
            id=str(uuid.uuid4()),
            meeting_id=meeting_id,
            topic=topic,
            discussion=discussion,
            decision=decision,
            action_item=action_item,
            owner=owner,
        )
        self.db.add(minute)
        self.db.flush()
        return minute

    def complete(self, meeting_id: str):
        meeting = self.db.query(Meeting).filter(Meeting.id == meeting_id).first()
        if meeting:
            meeting.status = "completed"
            meeting.completed_at = datetime.now(timezone.utc)
            self.db.flush()
