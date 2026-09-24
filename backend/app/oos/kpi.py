"""
OOS KPI Engine — Cálculo automático de KPIs.
"""

from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.oos.models import KPI, WorkOrder


class KPIEngine:
    """
    Motor de KPIs que:
    - Calcula métricas automáticamente desde Work Orders
    - Actualiza valores de KPIs
    - Detecta tendencias
    """

    def __init__(self, db: Session):
        self.db = db

    def calculate_from_work_orders(self, organization_id: str) -> dict:
        """Calcula KPIs basándose en el estado de las Work Orders."""
        work_orders = self.db.query(WorkOrder).filter(
            WorkOrder.organization_id == organization_id
        ).all()

        total = len(work_orders)
        if total == 0:
            return {"total": 0, "completed": 0, "in_progress": 0, "blocked": 0, "overdue": 0}

        completed = sum(1 for wo in work_orders if wo.status == "completed")
        in_progress = sum(1 for wo in work_orders if wo.status == "in_progress")
        blocked = sum(1 for wo in work_orders if wo.status == "blocked")

        now = datetime.now(timezone.utc)
        overdue = sum(
            1 for wo in work_orders
            if wo.due_date and wo.due_date < now and wo.status not in ["completed", "cancelled"]
        )

        # Calcular métricas adicionales
        avg_progress = sum(wo.progress for wo in work_orders) / total if total > 0 else 0
        completion_rate = (completed / total * 100) if total > 0 else 0

        return {
            "total": total,
            "completed": completed,
            "in_progress": in_progress,
            "blocked": blocked,
            "overdue": overdue,
            "avg_progress": round(avg_progress, 1),
            "completion_rate": round(completion_rate, 1),
        }

    def update_kpis_from_metrics(self, organization_id: str):
        """Actualiza los KPIs de la organización con las métricas calculadas."""
        metrics = self.calculate_from_work_orders(organization_id)

        # Buscar o crear KPIs de Work Orders
        kpi_mappings = {
            "work_orders_total": ("total", "Total Work Orders", "number"),
            "work_orders_completed": ("completed", "Work Orders Completadas", "number"),
            "work_orders_in_progress": ("in_progress", "Work Orders en Progreso", "number"),
            "work_orders_blocked": ("blocked", "Work Orders Bloqueadas", "number"),
            "work_orders_overdue": ("overdue", "Work Orders Vencidas", "number"),
            "completion_rate": ("completion_rate", "Tasa de Completitud", "percentage"),
            "avg_progress": ("avg_progress", "Progreso Promedio", "percentage"),
        }

        for kpi_name, (metric_key, display_name, metric_type) in kpi_mappings.items():
            value = metrics.get(metric_key, 0)

            # Buscar KPI existente
            existing = self.db.query(KPI).filter(
                KPI.organization_id == organization_id,
                KPI.name == kpi_name,
            ).first()

            if existing:
                # Actualizar
                history = existing.history or []
                history.append({
                    "date": datetime.now(timezone.utc).isoformat(),
                    "value": existing.current_value,
                })
                existing.history = history[-50:]  # Mantener últimos 50
                existing.current_value = value
            else:
                # Crear
                kpi = KPI(
                    id=str(uuid.uuid4()),
                    organization_id=organization_id,
                    name=kpi_name,
                    category="execution",
                    metric_type=metric_type,
                    current_value=value,
                    unit="%" if metric_type == "percentage" else None,
                )
                self.db.add(kpi)

        self.db.flush()


import uuid
