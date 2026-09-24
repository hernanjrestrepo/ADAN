"""
OOS Workflow — Motor de Work Orders.

Convierte decisiones del Board en Work Orders ejecutables.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.oos.models import Organization, DecisionRecord, WorkOrder, OOSBase
from app.oos.services import WorkOrderService, OrganizationService


class WorkOrderEngine:
    """
    Motor que convierte decisiones del Board en Work Orders.
    
    Flujo:
    1. Recibe Decision Record del Board
    2. Analiza las acciones y follow_ups
    3. Crea Work Orders automáticamente
    4. Asigna responsables según roles
    5. Establece dependencias
    """

    def __init__(self, db: Session):
        self.db = db
        self.wo_service = WorkOrderService(db)
        self.org_service = OrganizationService(db)

    def create_work_orders_from_decision(
        self,
        decision: DecisionRecord,
        organization_id: str,
    ) -> list[WorkOrder]:
        """
        Crea Work Orders automáticamente desde una decisión del Board.
        """
        work_orders = []

        # 1. Crear Work Orders desde actions
        for action in decision.actions:
            wo = self.wo_service.create_from_decision(
                organization_id=organization_id,
                decision_id=decision.id,
                title=action.get("action", "Acción del Board"),
                description=f"Generada desde decisión: {decision.topic}",
                priority=self._map_priority(action.get("priority", "medium")),
                assigned_to=action.get("owner"),
                assigned_to_name=action.get("owner_name"),
                due_date=self._parse_date(action.get("deadline")),
            )
            work_orders.append(wo)

        # 2. Crear Work Orders desde follow_ups
        for follow in decision.follow_up:
            wo = self.wo_service.create_from_decision(
                organization_id=organization_id,
                decision_id=decision.id,
                title=f"Follow-up: {follow.get('question', 'Seguimiento')}",
                description=f"Pregunta de {follow.get('from', 'Board')}: {follow.get('question', '')}",
                priority="medium",
                assigned_to=follow.get("responsible"),
                assigned_to_name=follow.get("responsible_name"),
            )
            work_orders.append(wo)

        # 3. Si no hay actions ni follow_ups, crear una Work Order genérica
        if not work_orders:
            wo = self.wo_service.create_from_decision(
                organization_id=organization_id,
                decision_id=decision.id,
                title=f"Ejecutar: {decision.topic[:200]}",
                description=f"Decisión del Board: {decision.final_decision}",
                priority="high",
            )
            work_orders.append(wo)

        self.db.commit()
        return work_orders

    def create_work_orders_from_actions(
        self,
        organization_id: str,
        decision_id: str,
        actions: list[dict],
    ) -> list[WorkOrder]:
        """Crea Work Orders desde una lista de acciones."""
        work_orders = []
        for action in actions:
            wo = self.wo_service.create_from_decision(
                organization_id=organization_id,
                decision_id=decision_id,
                title=action.get("title", action.get("action", "Acción")),
                description=action.get("description", ""),
                priority=action.get("priority", "medium"),
                assigned_to=action.get("assigned_to"),
                assigned_to_name=action.get("assigned_to_name"),
                due_date=self._parse_date(action.get("due_date") or action.get("deadline")),
            )
            work_orders.append(wo)
        self.db.commit()
        return work_orders

    def _map_priority(self, priority: str) -> str:
        """Mapea prioridades a formato estándar."""
        mapping = {
            "critical": "critical",
            "high": "high",
            "medium": "medium",
            "low": "low",
        }
        return mapping.get(priority.lower(), "medium")

    def _parse_date(self, date_str: str | None) -> datetime | None:
        """Parsea una fecha desde string."""
        if not date_str:
            return None
        try:
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            return None
