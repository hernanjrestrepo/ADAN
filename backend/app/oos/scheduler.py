"""
OOS Scheduler — Detección de tareas vencidas, bloqueos y escalamiento.
"""

from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.oos.models import WorkOrder


class SchedulerEngine:
    """
    Motor de scheduler que:
    - Detecta tareas vencidas
    - Detecta bloqueos
    - Genera recordatorios
    - Escala al Board cuando una tarea crítica falla
    """

    def __init__(self, db: Session):
        self.db = db

    def check_overdue(self, organization_id: str) -> list[dict]:
        """Detecta Work Orders vencidas."""
        now = datetime.now(timezone.utc)
        overdue = []

        work_orders = self.db.query(WorkOrder).filter(
            WorkOrder.organization_id == organization_id,
            WorkOrder.status.notin_(["completed", "cancelled"]),
            WorkOrder.due_date.isnot(None),
        ).all()

        for wo in work_orders:
            due = wo.due_date
            if due.tzinfo is None:
                due = due.replace(tzinfo=timezone.utc)
            if due < now:
                days_overdue = (now - due).days
                overdue.append({
                    "work_order_id": wo.id,
                    "title": wo.title,
                    "priority": wo.priority,
                    "due_date": wo.due_date.isoformat(),
                    "days_overdue": days_overdue,
                    "status": wo.status,
                    "assigned_to": wo.assigned_to_name,
                    "escalate": wo.priority in ["critical", "high"],
                })

        return overdue

    def check_blocked(self, organization_id: str) -> list[dict]:
        """Detecta Work Orders bloqueadas."""
        blocked = []

        work_orders = self.db.query(WorkOrder).filter(
            WorkOrder.organization_id == organization_id,
            WorkOrder.status == "blocked",
        ).all()

        for wo in work_orders:
            blocked.append({
                "work_order_id": wo.id,
                "title": wo.title,
                "priority": wo.priority,
                "blocking_reason": wo.blocking_reason,
                "assigned_to": wo.assigned_to_name,
                "escalate": wo.priority in ["critical", "high"],
            })

        return blocked

    def get_reminders(self, organization_id: str) -> list[dict]:
        """Genera recordatorios para Work Orders próximas a vencer."""
        now = datetime.now(timezone.utc)
        reminders = []

        work_orders = self.db.query(WorkOrder).filter(
            WorkOrder.organization_id == organization_id,
            WorkOrder.status.notin_(["completed", "cancelled"]),
            WorkOrder.due_date.isnot(None),
        ).all()

        for wo in work_orders:
            due = wo.due_date
            if due.tzinfo is None:
                due = due.replace(tzinfo=timezone.utc)
            days_until_due = (due - now).days
            if 0 <= days_until_due <= 3:  # Vence en 3 días o menos
                reminders.append({
                    "work_order_id": wo.id,
                    "title": wo.title,
                    "due_date": wo.due_date.isoformat(),
                    "days_until_due": days_until_due,
                    "assigned_to": wo.assigned_to_name,
                    "priority": wo.priority,
                })

        return reminders

    def get_escalation_candidates(self, organization_id: str) -> list[dict]:
        """Identifica Work Orders que deben escalarse al Board."""
        candidates = []

        # Tareas críticas vencidas
        overdue = self.check_overdue(organization_id)
        for item in overdue:
            if item["escalate"]:
                candidates.append({
                    "reason": "critical_overdue",
                    "work_order_id": item["work_order_id"],
                    "title": item["title"],
                    "detail": f"Vencida por {item['days_overdue']} días",
                })

        # Tareas bloqueadas críticas
        blocked = self.check_blocked(organization_id)
        for item in blocked:
            if item["escalate"]:
                candidates.append({
                    "reason": "critical_blocked",
                    "work_order_id": item["work_order_id"],
                    "title": item["title"],
                    "detail": f"Bloqueada: {item['blocking_reason']}",
                })

        return candidates
