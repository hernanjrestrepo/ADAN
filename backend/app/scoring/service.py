"""Evidencia y Scoring sobre el Gemelo Digital (WO-107).

- La evidencia la registran el cliente (dato externo o testimonio) y los Agentes (solo
  inferencias, siempre marcadas como tales; AD-CMP-05 §1).
- Cada cálculo es un Score nuevo (Patrón C): cita la evidencia que usó y su desglose.
- El Gate de un Nivel se evalúa sobre esa evidencia, no sobre palabras clave de un texto que
  escribió el mismo modelo (cierra B5 de la auditoría).
"""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.models import (
    Company, Decision, DecisionStatus, Event, Level, NivelStatus, Project, Score, ScoreType, User,
)
from app.scoring import engine
from app.twin.actor import Actor, acting_as, current_actor
from app.twin.models import Evidence

SCORING_AGENT = "Motor de Scoring"


class EvidenceError(ValueError):
    """La evidencia no cumple las reglas de AD-CMP-05."""


def _event(db: Session, project: Project, event_type: str, entity_type: str, entity_id: str, data: dict) -> None:
    actor = current_actor()
    db.add(Event(project_id=project.id, company_id=project.company_id, event_type=event_type,
                 entity_type=entity_type, entity_id=entity_id, data=data, category="domain",
                 actor_type=actor.kind, actor_id=actor.id or actor.label))


def record_evidence(db: Session, project: Project, user: User, *, dimension: str, claim: str, kind: str,
                    polarity: str = engine.SUPPORTS, source: str | None = None,
                    level_number: int | None = None, document_id: str | None = None) -> Evidence:
    """El cliente registra un dato externo o un testimonio. Las inferencias son de los Agentes."""
    if kind not in (engine.EXTERNAL, engine.TESTIMONY):
        raise EvidenceError("El cliente registra datos externos o testimonios; las inferencias son de los Agentes")
    if dimension not in engine.DIAGNOSTIC:
        raise EvidenceError(f"Dimensión desconocida: {dimension}")
    if polarity not in (engine.SUPPORTS, engine.CONTRADICTS):
        raise EvidenceError("La evidencia respalda o contradice; no hay otra opción")
    claim = (claim or "").strip()
    if len(claim) < 10:
        raise EvidenceError("Describe la afirmación con al menos 10 caracteres")
    if kind == engine.EXTERNAL and not (source or document_id):
        raise EvidenceError("Un dato verificable externamente necesita su fuente (enlace, documento o referencia)")
    with acting_as(Actor.user(user.id, user.name), reason="Evidencia registrada por el cliente"):
        item = Evidence(company_id=project.company_id, project_id=project.id, dimension=dimension, claim=claim,
                        kind=kind, polarity=polarity, source=(source or "").strip() or None,
                        level_number=level_number or engine.DIAGNOSTIC[dimension]["level"], document_id=document_id,
                        evidence_source=f"cliente:{kind}")
        db.add(item)
        db.commit()
    db.refresh(item)
    return item


def record_agent_inference(db: Session, project: Project, agent: str, *, dimension: str, claim: str,
                           polarity: str, confidence: float, reasoning: str | None = None) -> Evidence:
    """Un Agente deja una inferencia razonada: la evidencia más débil, marcada como tal."""
    with acting_as(Actor.agent(agent), reason="Inferencia de un Agente"):
        item = Evidence(company_id=project.company_id, project_id=project.id, dimension=dimension,
                        claim=claim[:5000], kind=engine.INFERENCE, polarity=polarity,
                        level_number=engine.DIAGNOSTIC[dimension]["level"], evidence_source=f"agente:{agent}",
                        confidence_level=min(confidence, engine.TIERS[engine.INFERENCE]["ceiling"]),
                        reasoning=reasoning)
        db.add(item)
        db.flush()
    return item


def record_board_inference(db: Session, project: Project, consensus) -> Evidence | None:
    """El resultado del Board Room entra como inferencia sobre el problema (nunca como prueba)."""
    decision = getattr(consensus, "decision", None)
    polarity = {"PROCEED": engine.SUPPORTS, "STOP": engine.CONTRADICTS}.get(decision)
    if polarity is None:  # PIVOT o sin consenso: no afirma ni niega que el problema sea real
        return None
    claim = (f"El Board Room votó {decision} con {getattr(consensus, 'confidence', 0):.0f} % de confianza "
             "sobre el problema planteado.")
    return record_agent_inference(db, project, "Board Room", dimension="problem", claim=claim, polarity=polarity,
                                  confidence=float(getattr(consensus, "confidence", 0) or 0))


def active_evidence(db: Session, project: Project, dimension: str | None = None) -> list[Evidence]:
    q = db.query(Evidence).filter(Evidence.project_id == project.id, Evidence.status == "active")
    if dimension:
        q = q.filter(Evidence.dimension == dimension)
    return q.order_by(Evidence.created_at.desc()).all()


def _items(rows: list[Evidence]) -> list[engine.EvidenceItem]:
    return [engine.EvidenceItem(r.kind, r.polarity, r.id) for r in rows]


def _save(db: Session, project: Project, result: engine.ScoreResult, evidence_ids: list[str],
          user_id: str | None = None) -> Score:
    with acting_as(Actor.agent(SCORING_AGENT), reason="Cálculo de Score (AD-ARQ-10 v0)"):
        score = Score(project_id=project.id, score_type=ScoreType(result.score_type), value=result.value,
                      confidence_level=result.confidence, reasoning=result.reasoning,
                      subject="responsible" if result.score_type == "responsible" else "company",
                      user_id=user_id,
                      evidence={"evidence_ids": evidence_ids, "breakdown": result.breakdown,
                                "engine": "AD-ARQ-10 v0"})
        db.add(score)
        db.flush()
        _event(db, project, "score_calculated", "scores", score.id,
               {"label": engine.ALL_SCORES[result.score_type]["label"], "type": result.score_type,
                "value": result.value, "confidence": result.confidence})
    return score


def calculate_dimension(db: Session, project: Project, dimension: str) -> Score:
    rows = active_evidence(db, project, dimension)
    score = _save(db, project, engine.score_dimension(dimension, _items(rows)), [r.id for r in rows])
    db.commit()
    db.refresh(score)
    return score


def evaluate_gate(db: Session, project: Project, level_number: int = 1) -> tuple[engine.GateEvaluation, Score]:
    """Gate de Nivel sobre la evidencia registrada; guarda el Score que lo sustenta."""
    rule = engine.GATE_RULES[level_number]
    rows = active_evidence(db, project, rule.score_type)
    evaluation = engine.evaluate_gate(level_number, _items(rows))
    score = _save(db, project, evaluation.score, [r.id for r in rows])
    db.commit()
    db.refresh(score)
    return evaluation, score


def calculate_responsible(db: Session, project: Project, company: Company) -> Score:
    decisions = db.query(Decision).filter(Decision.project_id == project.id).all()
    decided = [d for d in decisions if d.status in (DecisionStatus.APPROVED, DecisionStatus.REJECTED,
                                                     DecisionStatus.EXECUTED)]
    executed = sum(1 for d in decided if d.status == DecisionStatus.EXECUTED)
    divergent = sum(1 for d in decided if d.divergence)
    completed = db.query(Level).filter(Level.project_id == project.id, Level.status == NivelStatus.COMPLETED).count()
    result = engine.responsible_score(len(decided), executed, divergent, completed)
    score = _save(db, project, result, [d.id for d in decided], user_id=company.primary_user_id)
    db.commit()
    db.refresh(score)
    return score


def latest_scores(db: Session, project: Project) -> dict[str, Score]:
    latest: dict[str, Score] = {}
    for s in db.query(Score).filter(Score.project_id == project.id).order_by(Score.created_at).all():
        latest[s.score_type.value] = s
    return latest


def venture_available(db: Session, project: Project) -> bool:
    """El Venture Score nace en el Nivel 6 (AD-FUNC-07 §2)."""
    return db.query(Level).filter(Level.project_id == project.id, Level.number >= 6,
                                  Level.status != NivelStatus.BLOCKED).count() > 0


def calculate_venture(db: Session, project: Project) -> Score:
    latest = {t: (s.value, s.confidence_level) for t, s in latest_scores(db, project).items()}
    score = _save(db, project, engine.venture_score(latest), [])
    db.commit()
    db.refresh(score)
    return score


def overview(db: Session, project: Project) -> list[dict]:
    """Los 8 Scores de AD-FUNC-07, cada uno con su último cálculo o por qué aún no existe."""
    latest = latest_scores(db, project)
    levels = {lv.number: lv.status for lv in db.query(Level).filter(Level.project_id == project.id).all()}
    counts = {d: 0 for d in engine.DIAGNOSTIC}
    for row in active_evidence(db, project):
        counts[row.dimension] = counts.get(row.dimension, 0) + 1
    out = []
    for key, meta in engine.ALL_SCORES.items():
        level = meta["level"]
        status = levels.get(level) if level else None
        if key == "venture":
            available = venture_available(db, project)
        elif key == "responsible":
            available = True
        else:
            available = status is not None and status != NivelStatus.BLOCKED
        s = latest.get(key)
        out.append({
            "key": key, "label": meta["label"], "measures": meta["measures"], "level": level,
            "family": "diagnostic" if key in engine.DIAGNOSTIC else "continuous",
            "available": available,
            "unavailable_reason": None if available else (
                "Nace en el Nivel 6" if key == "venture" else f"Se abre en el Nivel {level}"),
            "evidence_count": counts.get(key, 0),
            "latest": None if s is None else {
                "id": s.id, "value": s.value, "confidence": s.confidence_level, "reasoning": s.reasoning,
                "breakdown": (s.evidence or {}).get("breakdown"), "created_at": s.created_at.isoformat()},
        })
    return out
