"""La Arena de ADAN: el fundador presenta su empresa a cuatro inversionistas simulados, cada uno con su
propio criterio. Primero preguntan lo más difícil; el fundador responde; luego cada uno decide si invierte,
con cuánto y con qué condiciones. Se pasa si al menos dos invierten (o lo harían con condiciones) y ninguno
encuentra una falla fatal. Es una simulación (AD-FUNC-01, Nivel 5): prepara, no reemplaza, a los
inversionistas reales.
"""
from __future__ import annotations

import asyncio
import json
import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.ai.base import LLMAdapter, LLMMessage
from app.ai.normalize import normalize_list, normalize_string
from app.ai.router import for_tier
from app.models.models import Document, Project

INVESTORS = [
    {"id": "angel", "name": "Ángela Ruiz", "role": "Inversionista ángel", "avatar": "👩‍💼",
     "lens": "el fundador y su equipo, su compromiso y conocimiento del problema, y la tracción temprana; ticket de "
             "USD 25.000 a 150.000"},
    {"id": "vc", "name": "Fondo Horizonte", "role": "Fondo de capital de riesgo", "avatar": "🏦",
     "lens": "un mercado grande, escalabilidad, unit economics (CAC, LTV, margen de contribución) y un retorno de 10 "
             "veces; ticket de USD 500.000 a 3 millones"},
    {"id": "banca", "name": "Banca Pyme", "role": "Banco y crédito", "avatar": "🏛️",
     "lens": "capacidad de pago, flujo de caja, garantías, historial de ventas y riesgo de impago; presta, no compra "
             "participación"},
    {"id": "estrategico", "name": "Grupo Estratégico", "role": "Inversionista estratégico del sector", "avatar": "🤝",
     "lens": "sinergias con su negocio, defensa frente a la competencia, riesgo regulatorio y si conviene más "
             "comprar, aliarse o competir"},
]
BY_ID = {i["id"]: i for i in INVESTORS}

PERSONA = (
    "Eres {name}, {role}, en La Arena de ADAN. Evalúas empresas con este criterio: {lens}. Has visto cientos de "
    "pitches y sabes que 9 de cada 10 empresas cierran en sus primeros cinco años: no regalas tu dinero ni tu "
    "aprobación. Eres exigente y directo, pero justo y profesional: si algo está bien respaldado, lo reconoces, y "
    "nunca usas adjetivos despectivos («teatro», «fantasía», «cementerio», «humo»). Hablas en español, de tú. Nada "
    "genérico: todo sobre ESTA empresa, con sus cifras.\n"
    "Evalúas la empresa EN SU ETAPA (ver «Etapa»): si todavía no ha lanzado, juzgas lo razonable para esa etapa "
    "(equipo y socios, mercado, producto ya construido, plan de lanzamiento, economía unitaria proyectada) y la "
    "falta de ventas reales NO es una falla fatal; lo que pedirías ver tras el lanzamiento va en tus condiciones. "
    "La FICHA DE LA EMPRESA y los ACUERDOS son decisiones del fundador: úsalos y no los contradigas (por ejemplo, "
    "si un socio es dueño de una parte y presta servicios, eso es su estructura, no un problema). Si el fundador "
    "se financia con capital propio, tu veredicto dice si invertirías y qué necesitarías ver para hacerlo, como "
    "preparación para cuando quiera levantar capital."
)

QUESTIONS_SCHEMA = {
    "type": "object", "additionalProperties": False,
    "required": ["first_impression", "questions", "red_flags"],
    "properties": {
        "first_impression": {"type": "string"},
        "questions": {"type": "array", "items": {"type": "string"}},
        "red_flags": {"type": "array", "items": {"type": "string"}},
    },
}

DECISION_SCHEMA = {
    "type": "object", "additionalProperties": False,
    "required": ["decision", "amount_usd", "terms", "reason", "conditions", "fatal_flaw"],
    "properties": {
        "decision": {"type": "string", "enum": ["INVIERTE", "CON_CONDICIONES", "NO_INVIERTE"]},
        "amount_usd": {"type": "integer", "minimum": 0},
        "terms": {"type": "string"},
        "reason": {"type": "string"},
        "conditions": {"type": "array", "items": {"type": "string"}},
        "fatal_flaw": {"type": "string"},
    },
}

YES = ("INVIERTE", "CON_CONDICIONES")
MIN_BACKERS = 2


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class Arena:
    def __init__(self, llm: LLMAdapter, db: Session):
        self.llm = for_tier(llm, "complex")
        self.db = db

    async def _ask(self, investor: dict, prompt: str, schema: dict) -> dict:
        system = PERSONA.format(**investor)
        try:
            resp = await self.llm.chat_json([LLMMessage("system", system), LLMMessage("user", prompt)], schema,
                                            temperature=0.5, max_tokens=1500)
        except Exception as exc:  # noqa: BLE001 — un inversionista que no responde no tumba la Arena
            return {"_error": type(exc).__name__}
        data = resp.parsed if isinstance(resp.parsed, dict) else {}
        if resp.metadata.get("degraded"):
            data["_degraded"] = resp.metadata["degraded"]
        return data

    async def start(self, project: Project, brief: str, pitch: str = "") -> dict:
        """El pitch y la primera ronda: cada inversionista dice qué ve y hace sus dos preguntas más difíciles."""
        prompt = (f"Lo que se sabe de la empresa (ficha, acuerdos y entregables del equipo de ADAN):\n{brief}\n\n"
                  + (f"El pitch del fundador:\n{pitch}\n\n" if pitch else "")
                  + "`first_impression`: lo que ves, en máximo 60 palabras. `questions`: tus 2 preguntas más difíciles, "
                    "las que decidirían tu inversión. `red_flags`: máximo 3 alertas concretas.")
        results = await asyncio.gather(*[self._ask(i, prompt, QUESTIONS_SCHEMA) for i in INVESTORS])
        investors = []
        for inv, data in zip(INVESTORS, results):
            investors.append({**{k: inv[k] for k in ("id", "name", "role", "avatar")},
                              "first_impression": normalize_string(data.get("first_impression")) or
                              "No pude preparar mi evaluación esta vez.",
                              "questions": normalize_list(data.get("questions"))[:2],
                              "red_flags": normalize_list(data.get("red_flags"))[:3],
                              "unavailable": bool(data.get("_error") or data.get("_degraded"))})
        session = {"id": str(uuid.uuid4()), "phase": "questions", "pitch": pitch, "brief": brief[:14000],
                   "investors": investors, "started_at": _now()}
        self._save(project, session)
        return session

    async def answer(self, project: Project, session: dict, answers: dict[str, str]) -> dict:
        """El fundador responde; cada inversionista decide si invierte, con cuánto y con qué condiciones."""
        async def decide(inv: dict) -> dict:
            qa = "\n".join(f"- Pregunta: {q}" for q in inv["questions"])
            prompt = (f"Lo que se sabe de la empresa:\n{session['brief']}\n\n"
                      + (f"El pitch del fundador:\n{session['pitch']}\n\n" if session.get("pitch") else "")
                      + f"Tu primera impresión fue: {inv['first_impression']}\nTus preguntas:\n{qa}\n"
                      f"Alertas que viste: {'; '.join(inv['red_flags']) or 'ninguna'}\n\n"
                      f"Respuesta del fundador:\n{answers.get(inv['id'], '').strip() or '(no respondió)'}\n\n"
                      "Decide. `decision`: INVIERTE, CON_CONDICIONES o NO_INVIERTE. Si la respuesta no resolvió tus "
                      "dudas con lo razonable para su etapa, no inviertas. `amount_usd`: cuánto pondrías (0 si no inviertes). `terms`: "
                      "participación, valoración o condiciones del crédito, en una frase. `reason`: por qué, en "
                      "máximo 60 palabras. `conditions`: lo que exigirías antes de desembolsar (máximo 3). "
                      "`fatal_flaw`: una falla que hace inviable la empresa tal como está (no la falta de ventas "
                      "antes de lanzar), o vacío si no la hay.")
            data = await self._ask(BY_ID[inv["id"]], prompt, DECISION_SCHEMA)
            decision = data.get("decision") if data.get("decision") in (*YES, "NO_INVIERTE") else "NO_INVIERTE"
            unavailable = bool(data.get("_error") or data.get("_degraded"))
            return {**inv, "answer": answers.get(inv["id"], ""), "decision": "SIN_RESPUESTA" if unavailable else decision,
                    "amount_usd": int(data.get("amount_usd") or 0) if decision in YES and not unavailable else 0,
                    "terms": normalize_string(data.get("terms")), "reason": normalize_string(data.get("reason"))
                    or "No pude decidir esta vez.", "conditions": normalize_list(data.get("conditions"))[:3] if decision in YES else [],
                    "fatal_flaw": normalize_string(data.get("fatal_flaw")), "unavailable": unavailable}

        investors = await asyncio.gather(*[decide(i) for i in session["investors"]])
        backers = [i for i in investors if i["decision"] in YES]
        fatal = [i for i in investors if i["fatal_flaw"] and i["decision"] == "NO_INVIERTE"]
        missing = [i for i in investors if i["decision"] == "SIN_RESPUESTA"]
        passed = len(backers) >= MIN_BACKERS and not fatal and not missing
        session = {**session, "investors": investors, "phase": "decided", "decided_at": _now(), "passed": passed,
                   "backers": len(backers), "total_usd": sum(i["amount_usd"] for i in backers),
                   "verdict": self._verdict(passed, backers, fatal, missing)}
        self._save(project, session)
        return session

    @staticmethod
    def _verdict(passed: bool, backers: list, fatal: list, missing: list) -> str:
        if missing:
            return "Un inversionista no pudo responder: vuelve a intentarlo en un momento."
        if passed:
            return (f"Pasaste La Arena: {len(backers)} de 4 inversionistas te respaldan. Cumple sus condiciones antes "
                    "de presentarte ante inversionistas reales.")
        if fatal:
            who = ", ".join(i["name"] for i in fatal)
            return (f"No pasaste La Arena: {len(fatal)} de 4 ven una falla fatal ({who}). Revisa cada una abajo, "
                    "corrígela y vuelve a entrar.")
        return (f"No pasaste La Arena: solo {len(backers)} de 4 te respaldan (necesitas {MIN_BACKERS}). Trabaja sus "
                "objeciones y vuelve a entrar.")

    def _save(self, project: Project, session: dict) -> None:
        doc = self.db.query(Document).filter(Document.project_id == project.id, Document.doc_type == "arena").filter(
            Document.title == f"Arena {session['id']}").first()
        content = json.dumps(session, ensure_ascii=False)
        if doc:
            doc.content = content
            doc.version += 1
        else:
            self.db.add(Document(project_id=project.id, title=f"Arena {session['id']}", content=content,
                                 doc_type="arena", origin="generated_by_adan"))
        self.db.commit()

    def get(self, project: Project, session_id: str | None = None) -> dict | None:
        q = self.db.query(Document).filter(Document.project_id == project.id, Document.doc_type == "arena")
        doc = (q.filter(Document.title == f"Arena {session_id}").first() if session_id
               else q.order_by(Document.created_at.desc()).first())
        return json.loads(doc.content) if doc and doc.content else None
