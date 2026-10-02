"""Decisión de ADÁN (AD-CMP-03, AD-FUNC-02 §2.5) — WO-098.

Ciclo (Patrón A): Propuesta → Presentada al cliente → Aprobada / Rechazada → Ejecutada.

- **Consulta previa** (§2): al proponer, se guardan las decisiones ya aprobadas o ejecutadas
  del mismo Gemelo, para no contradecirlas sin saberlo.
- **Opciones**: cada propuesta trae sus opciones con fundamento, nivel de evidencia y
  Confidence Level, y cuál recomienda el Board.
- **Decidir distinto** (AD-FUNC-02 §2.5): si el cliente aprueba una opción distinta de la
  recomendada se registran, sin excepción, los 6 campos: opción elegida, opción
  recomendada con su fundamento, evidencia y confianza de cada una, riesgos asumidos
  (también como Riesgos del Gemelo) y la responsabilidad asumida por el cliente.
- **Ejecutar** puede originar una Decisión de Negocio (§4): relación explícita, no fusión.
"""
from __future__ import annotations

from datetime import datetime, timezone
from statistics import mean

from sqlalchemy.orm import Session

from app.models.models import Decision, DecisionStatus, Project
from app.twin.actor import Actor, acting_as

BOARD_OPTION_LABELS = {"PROCEED": "Avanzar", "PIVOT": "Pivotar", "STOP": "Detener"}


class DecisionError(ValueError):
    """La operación no es válida para el estado o los datos de la decisión."""


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def evidence_level(supporting: int, total: int) -> str:
    """Nivel de evidencia de una opción según cuántos agentes la respaldan.

    Heurística declarada (no hay fórmula en el blueprint): alta con la mayoría absoluta,
    media con al menos un tercio, baja por debajo.
    """
    if total <= 0 or supporting <= 0:
        return "baja"
    share = supporting / total
    if share > 0.5:
        return "alta"
    if share >= 1 / 3:
        return "media"
    return "baja"


def board_options(votes: list[dict], recommended: str) -> list[dict]:
    """Opciones de una sesión del Board: Avanzar, Pivotar y Detener con su respaldo."""
    counted = [v for v in votes if (v.get("vote") or "").upper() in BOARD_OPTION_LABELS]
    options = []
    for key, label in BOARD_OPTION_LABELS.items():
        backing = [v for v in counted if v["vote"].upper() == key]
        rationale = " · ".join(
            f"{v.get('agent')}: {v.get('justification') or v.get('analysis') or ''}".strip()
            for v in backing
        )[:2000]
        options.append({
            "key": key,
            "label": label,
            "rationale": rationale or ("Recomendación del Board" if key == recommended else ""),
            "votes": len(backing),
            "evidence_level": evidence_level(len(backing), len(counted)),
            "confidence": round(mean(float(v.get("confidence") or 0) for v in backing), 1) if backing else 0.0,
        })
    return options


def level_close_options(level_number: int, score: float, message: str) -> list[dict]:
    return [
        {"key": "CLOSE", "label": f"Cerrar el Nivel {level_number}", "rationale": message,
         "evidence_level": "alta" if score >= 70 else "media", "confidence": round(score, 1)},
        {"key": "CONTINUE", "label": f"Seguir trabajando el Nivel {level_number}",
         "rationale": "Reunir más evidencia antes de avanzar", "evidence_level": "baja",
         "confidence": round(max(0.0, 100 - score), 1)},
    ]


def prior_decisions(db: Session, project: Project, exclude_id: str | None = None) -> list[dict]:
    """Consulta previa (AD-CMP-03 §2): lo ya aprobado o ejecutado en este Gemelo."""
    rows = db.query(Decision).filter(
        Decision.project_id == project.id,
        Decision.status.in_([DecisionStatus.APPROVED, DecisionStatus.EXECUTED]),
    ).order_by(Decision.created_at).all()
    return [{"id": d.id, "title": d.title, "status": d.status.value, "chosen_option": d.chosen_option}
            for d in rows if d.id != exclude_id]


def present(db: Session, decision: Decision, actor: Actor) -> Decision:
    """La decisión se muestra al cliente con su razonamiento (Propuesta → Presentada)."""
    if decision.status == DecisionStatus.PRESENTED:
        return decision
    if decision.status != DecisionStatus.PROPOSED:
        raise DecisionError("Solo se presenta una decisión propuesta")
    with acting_as(actor, reason="Presentada al cliente"):
        decision.status = DecisionStatus.PRESENTED
        decision.presented_at = utcnow()
        db.commit()
    db.refresh(decision)
    return decision


def record_choice(
    db: Session,
    project: Project,
    decision: Decision,
    chosen_option: str | None,
    risks_assumed: list[str] | None,
    responsibility_statement: str | None,
) -> None:
    """Fija la opción elegida y, si difiere de la recomendada, los 6 campos de §2.5."""
    options = {o["key"]: o for o in (decision.options or [])}
    recommended = decision.recommended_option
    if chosen_option is None:
        chosen_option = recommended
    if chosen_option is not None and options and chosen_option not in options:
        raise DecisionError(f"Opción desconocida: {chosen_option}")
    decision.chosen_option = chosen_option

    if chosen_option is None or recommended is None or chosen_option == recommended:
        return

    risks = [r.strip() for r in (risks_assumed or []) if r and r.strip()]
    statement = (responsibility_statement or "").strip()
    if not risks:
        raise DecisionError("Al decidir distinto a lo recomendado hay que declarar los riesgos asumidos")
    if len(statement) < 10:
        raise DecisionError("Al decidir distinto a lo recomendado hay que declarar la responsabilidad asumida")

    chosen, rec = options.get(chosen_option, {}), options.get(recommended, {})
    decision.divergence = {
        "chosen_option": {"key": chosen_option, "label": chosen.get("label")},
        "recommended_option": {"key": recommended, "label": rec.get("label"), "rationale": rec.get("rationale")},
        "evidence_level": {"chosen": chosen.get("evidence_level"), "recommended": rec.get("evidence_level")},
        "confidence": {"chosen": chosen.get("confidence"), "recommended": rec.get("confidence")},
        "risks_assumed": risks,
        "responsibility_assumed": statement,
    }
    # Riesgos asumidos como propiedad transversal del Gemelo (AD-005 §3)
    from app.twin.models import TwinRisk
    for description in risks:
        db.add(TwinRisk(company_id=project.company_id, subject_type="decision", subject_id=decision.id,
                        kind="otro", description=description, severity="alta",
                        reasoning="Riesgo asumido al decidir distinto a la recomendación del Board"))


def execute(
    db: Session,
    project: Project,
    decision: Decision,
    user_id: str,
    business_title: str | None = None,
) -> Decision:
    """Aprobada → Ejecutada, por el cliente. Puede originar una Decisión de Negocio (§4)."""
    if decision.status != DecisionStatus.APPROVED:
        raise DecisionError("Solo se ejecuta una decisión aprobada")
    from app.twin.models import BusinessDecision
    with acting_as(Actor.user(user_id), reason="El cliente ejecuta la decisión"):
        decision.status = DecisionStatus.EXECUTED
        decision.executed_at = utcnow()
        if business_title:
            db.add(BusinessDecision(
                company_id=project.company_id, title=business_title[:255],
                description=decision.description, adan_decision_id=decision.id, state="executed",
                evidence_source=f"Decisión de ADÁN {decision.id}",
            ))
        db.commit()
    db.refresh(decision)
    return decision
