"""Catálogo de Agentes (AD-006 §4): los 7 roles del Board Room (AD-FUNC-02) y ADÁN."""
from __future__ import annotations

from sqlalchemy.orm import Session

# Copia fija de los roles de app/nivel1/board_room.py y app/agents/board.py. La migración
# 0004 siembra esta misma lista; si el Board cambia de roles, se agrega una migración.
AGENT_CATALOG: list[tuple[str, str, str]] = [
    ("ADAN", "ADÁN", "Orquestador: conversa con el cliente y coordina a los agentes"),
    ("CEO", "CEO Agent", "Preside el Board: abre la sesión y da la síntesis (no vota)"),
    ("CTO", "CTO", "Viabilidad técnica: factibilidad, arquitectura, riesgos tecnológicos"),
    ("CFO", "CFO", "Viabilidad financiera: costos, ingresos, caja, sostenibilidad"),
    ("CMO", "CMO", "Mercado: dolor real, demanda, diferenciación, canales"),
    ("Legal", "Legal", "Riesgos legales: regulación, contratos, propiedad intelectual, datos personales"),
    ("Producto", "Producto", "Producto: problema-solución, usuario, alcance del MVP, experiencia"),
    ("Operaciones", "Operaciones", "Operación: procesos, recursos, proveedores, capacidad de ejecutar"),
]


def ensure_agent_catalog(db: Session) -> None:
    """Crea los agentes que falten (bases creadas con create_all, sin la migración 0004)."""
    from app.twin.models import Agent

    existing = {code for (code,) in db.query(Agent.code).all()}
    missing = [Agent(code=code, name=name, description=desc)
               for code, name, desc in AGENT_CATALOG if code not in existing]
    if missing:
        db.add_all(missing)
        db.flush()
