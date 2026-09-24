"""
Autonomous Organization Engine — Organización que opera sin intervención humana.

Ciclo: Objetivos → Proyectos → Work Orders → Asignación → Seguimiento → KPIs → Reunión → Aprendizaje
"""

import uuid
from datetime import datetime, timezone
from dataclasses import dataclass, field


@dataclass
class AutonomousCycle:
    """Un ciclo completo de operación autónoma."""
    id: str
    organization_id: str
    started_at: datetime
    completed_at: datetime | None = None
    objectives_created: int = 0
    projects_created: int = 0
    work_orders_created: int = 0
    tasks_completed: int = 0
    kpis_updated: int = 0
    meetings_held: int = 0
    lessons_learned: int = 0
    status: str = "running"              # running, completed, paused
    events: list[dict] = field(default_factory=list)


class AutonomousEngine:
    """
    Motor de organización autónoma.
    
    Ejecuta el ciclo completo sin intervención humana:
    1. Evaluar estado actual
    2. Identificar objetivos
    3. Generar Work Orders
    4. Asignar responsables
    5. Hacer seguimiento
    6. Evaluar KPIs
    7. Convocar reuniones
    8. Aprender del resultado
    """

    def __init__(self):
        self._cycles: list[AutonomousCycle] = []

    def start_cycle(self, organization_id: str) -> AutonomousCycle:
        """Inicia un ciclo autónomo."""
        cycle = AutonomousCycle(
            id=str(uuid.uuid4()),
            organization_id=organization_id,
            started_at=datetime.now(timezone.utc),
        )
        self._cycles.append(cycle)
        return cycle

    def complete_cycle(self, cycle_id: str) -> AutonomousCycle | None:
        """Completa un ciclo autónomo."""
        for cycle in self._cycles:
            if cycle.id == cycle_id:
                cycle.status = "completed"
                cycle.completed_at = datetime.now(timezone.utc)
                return cycle
        return None

    def get_cycle(self, cycle_id: str) -> AutonomousCycle | None:
        for cycle in self._cycles:
            if cycle.id == cycle_id:
                return cycle
        return None

    def get_cycles(self, organization_id: str) -> list[AutonomousCycle]:
        return [c for c in self._cycles if c.organization_id == organization_id]

    def get_status(self, organization_id: str) -> dict:
        """Retorna el estado de la organización autónoma."""
        cycles = self.get_cycles(organization_id)
        active = [c for c in cycles if c.status == "running"]
        completed = [c for c in cycles if c.status == "completed"]

        return {
            "total_cycles": len(cycles),
            "active_cycles": len(active),
            "completed_cycles": len(completed),
            "total_objectives": sum(c.objectives_created for c in cycles),
            "total_work_orders": sum(c.work_orders_created for c in cycles),
            "total_tasks_completed": sum(c.tasks_completed for c in cycles),
            "total_lessons": sum(c.lessons_learned for c in cycles),
        }
