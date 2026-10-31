"""Encuestas de validación: ADAN las redacta a partir del dolor que entendió, se comparten por enlace (el cliente
las envía por WhatsApp desde su teléfono) y las respuestas se vuelven evidencia que el cliente decide registrar.

Privacidad (Ley 1581 de 2012): la encuesta no pide datos personales, exige consentimiento informado y los números
de teléfono a los que se envía nunca llegan al servidor (los enlaces de WhatsApp se arman en el navegador).
"""
from __future__ import annotations

import json
import secrets
from collections import Counter
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.ai.base import LLMAdapter, LLMMessage
from app.ai.normalize import normalize_list, normalize_string
from app.ai.router import for_tier
from app.models.models import Company, Document, Project

MAX_QUESTIONS = 10
MAX_RESPONSES = 500
QUESTION_TYPES = ("opcion", "multiple", "escala", "numero", "texto")

QUESTIONS_SCHEMA = {
    "type": "object", "additionalProperties": False, "required": ["titulo", "intro", "preguntas"],
    "properties": {
        "titulo": {"type": "string"},
        "intro": {"type": "string"},
        "preguntas": {"type": "array", "items": {
            "type": "object", "additionalProperties": False, "required": ["texto", "tipo", "opciones", "por_que"],
            "properties": {"texto": {"type": "string"}, "tipo": {"type": "string", "enum": list(QUESTION_TYPES)},
                           "opciones": {"type": "array", "items": {"type": "string"}}, "por_que": {"type": "string"}}}},
    },
}

INSIGHTS_SCHEMA = {
    "type": "object", "additionalProperties": False, "required": ["resumen", "hallazgos", "evidencia_sugerida", "alertas"],
    "properties": {
        "resumen": {"type": "string"},
        "hallazgos": {"type": "array", "items": {"type": "string"}},
        "evidencia_sugerida": {"type": "array", "items": {
            "type": "object", "additionalProperties": False, "required": ["afirmacion", "polaridad"],
            "properties": {"afirmacion": {"type": "string"},
                           "polaridad": {"type": "string", "enum": ["supports", "contradicts"]}}}},
        "alertas": {"type": "array", "items": {"type": "string"}},
    },
}

DESIGNER = (
    "Eres el investigador de mercado de ADAN. Diseñas encuestas cortas para validar si un problema es real, siguiendo "
    "el método The Mom Test: preguntas por lo que la persona HIZO y PAGÓ en el pasado, nunca por lo que haría o "
    "pagaría en hipótesis, y nunca vendes la idea dentro de la pregunta. Lenguaje sencillo, sin tecnicismos. Español."
)


SIM_SCHEMA = {
    "type": "object", "additionalProperties": False, "required": ["perfil", "respuestas", "supuestos"],
    "properties": {
        "perfil": {"type": "string"},
        "supuestos": {"type": "array", "items": {"type": "string"}},
        "respuestas": {"type": "array", "items": {
            "type": "object", "additionalProperties": False, "required": ["id", "conteos", "promedio", "textos"],
            "properties": {"id": {"type": "string"},
                           "conteos": {"type": "object", "additionalProperties": {"type": "number"}},
                           "promedio": {"type": "number"},
                           "textos": {"type": "array", "items": {"type": "string"}}}}},
    },
}
SIM_SIZE = 50

SIMULATOR = (
    "Eres el Simulador de Mercado de ADAN. Simulas cómo respondería una muestra de personas REALISTA del segmento "
    "descrito, con diversidad (no todas sufren el problema igual; algunas no lo sufren). No eres optimista: te basas "
    "en cómo se comporta la gente de verdad. Es una simulación para avanzar mientras llega la encuesta real; nunca la "
    "presentes como datos reales. Español."
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _clean_questions(raw: list) -> list[dict]:
    out = []
    for q in raw[:MAX_QUESTIONS]:
        if not isinstance(q, dict) or not normalize_string(q.get("texto")):
            continue
        kind = q.get("tipo") if q.get("tipo") in QUESTION_TYPES else "texto"
        options = normalize_list(q.get("opciones"))[:8] if kind in ("opcion", "multiple") else []
        if kind in ("opcion", "multiple") and len(options) < 2:
            kind, options = "texto", []
        out.append({"id": f"q{len(out) + 1}", "texto": normalize_string(q.get("texto"))[:300], "tipo": kind,
                    "opciones": [o[:120] for o in options], "por_que": normalize_string(q.get("por_que"))[:300]})
    return out


class Surveys:
    def __init__(self, llm: LLMAdapter | None, db: Session):
        self.llm = for_tier(llm, "standard") if llm is not None else None
        self.db = db

    async def create(self, project: Project, company: Company, brief: str, objective: str = "") -> dict:
        prompt = (f"Empresa: {company.name}\nLo que ADAN sabe del problema y del segmento:\n{brief or 'sin datos aún'}\n\n"
                  + (f"Lo que el fundador quiere averiguar: {objective}\n\n" if objective else "")
                  + "Diseña una encuesta de 6 a 9 preguntas para personas del segmento. Incluye: una pregunta filtro "
                    "(¿le pasa o le pasó el problema?), con qué frecuencia le pasa, cómo lo resuelve hoy, cuánto le cuesta "
                    "hoy (tiempo o dinero, en rangos), qué tan grave es (escala 1 a 5), si ya pagó por resolverlo y cuánto, "
                    "y una abierta sobre lo que más le frustra. `tipo`: opcion (una respuesta), multiple, escala (1 a 5), "
                    "numero o texto; `opciones` solo en opcion y multiple. `intro`: 2 frases que expliquen quién pregunta "
                    "y para qué, sin vender. `por_que`: qué hipótesis valida cada pregunta (lo ve solo el fundador).")
        resp = await self.llm.chat_json([LLMMessage("system", DESIGNER), LLMMessage("user", prompt)], QUESTIONS_SCHEMA,
                                        temperature=0.4, max_tokens=3000)
        data = resp.parsed if isinstance(resp.parsed, dict) else {}
        questions = _clean_questions(data.get("preguntas") or [])
        if not questions:
            raise ValueError("No se pudo diseñar la encuesta esta vez; intenta de nuevo en un momento.")
        survey = {"token": secrets.token_urlsafe(16), "company": company.name,
                  "titulo": normalize_string(data.get("titulo"))[:160] or f"Encuesta de {company.name}",
                  "intro": normalize_string(data.get("intro"))[:600], "preguntas": questions, "objective": objective,
                  "open": True, "created_at": _now(), "responses": []}
        self.db.add(Document(project_id=project.id, title=f"Encuesta {survey['token']}", doc_type="survey",
                             origin="generated_by_adan", content=json.dumps(survey, ensure_ascii=False)))
        self.db.commit()
        return survey

    def _doc(self, token: str, project: Project | None = None) -> Document | None:
        q = self.db.query(Document).filter(Document.doc_type == "survey", Document.title == f"Encuesta {token}")
        if project is not None:
            q = q.filter(Document.project_id == project.id)
        return q.first()

    def get(self, token: str, project: Project | None = None) -> dict | None:
        doc = self._doc(token, project)
        return json.loads(doc.content) if doc and doc.content else None

    def list(self, project: Project) -> list[dict]:
        docs = self.db.query(Document).filter(Document.project_id == project.id, Document.doc_type == "survey") \
            .order_by(Document.created_at.desc()).all()
        return [self._summary(json.loads(d.content)) for d in docs if d.content]

    @staticmethod
    def _summary(s: dict) -> dict:
        return {k: s[k] for k in ("token", "titulo", "created_at", "open")} | {"responses": len(s.get("responses", []))}

    @staticmethod
    def public(s: dict) -> dict:
        """Lo que ve quien responde: sin datos privados de la empresa ni el porqué de cada pregunta."""
        return {"token": s["token"], "company": s["company"], "titulo": s["titulo"], "intro": s["intro"], "open": s["open"],
                "preguntas": [{k: q[k] for k in ("id", "texto", "tipo", "opciones")} for q in s["preguntas"]]}

    def answer(self, token: str, answers: dict, consent: bool) -> None:
        if not consent:
            raise PermissionError("Para enviar tus respuestas debes aceptar el tratamiento de datos.")
        doc = self._doc(token)
        if not doc:
            raise LookupError("La encuesta no existe")
        survey = json.loads(doc.content)
        if not survey.get("open"):
            raise PermissionError("Esta encuesta ya está cerrada.")
        if len(survey["responses"]) >= MAX_RESPONSES:
            raise PermissionError("Esta encuesta ya recibió el máximo de respuestas.")
        clean = {}
        for q in survey["preguntas"]:
            value = answers.get(q["id"])
            if value in (None, "", []):
                continue
            if q["tipo"] == "opcion" and value in q["opciones"]:
                clean[q["id"]] = value
            elif q["tipo"] == "multiple" and isinstance(value, list):
                picked = [v for v in value if v in q["opciones"]]
                if picked:
                    clean[q["id"]] = picked
            elif q["tipo"] == "escala" and str(value).isdigit() and 1 <= int(value) <= 5:
                clean[q["id"]] = int(value)
            elif q["tipo"] == "numero":
                try:
                    clean[q["id"]] = float(value)
                except (TypeError, ValueError):
                    pass
            elif q["tipo"] == "texto" and isinstance(value, str):
                clean[q["id"]] = value.strip()[:1000]
        if not clean:
            raise ValueError("Responde al menos una pregunta.")
        survey["responses"].append({"at": _now(), "answers": clean})
        doc.content = json.dumps(survey, ensure_ascii=False)
        doc.version += 1
        self.db.commit()

    def close(self, project: Project, token: str, open_: bool) -> dict:
        doc = self._doc(token, project)
        if not doc:
            raise LookupError("La encuesta no existe")
        survey = json.loads(doc.content)
        survey["open"] = open_
        doc.content = json.dumps(survey, ensure_ascii=False)
        self.db.commit()
        return survey

    @staticmethod
    def results(survey: dict) -> dict:
        """Totales por pregunta, calculados aquí (no por el modelo)."""
        out = []
        responses = survey.get("responses", [])
        for q in survey["preguntas"]:
            values = [r["answers"][q["id"]] for r in responses if q["id"] in r["answers"]]
            item = {**{k: q[k] for k in ("id", "texto", "tipo", "opciones", "por_que")}, "answered": len(values)}
            if q["tipo"] == "opcion":
                c = Counter(values)
                item["counts"] = {o: c.get(o, 0) for o in q["opciones"]}
            elif q["tipo"] == "multiple":
                c = Counter(v for vs in values for v in vs)
                item["counts"] = {o: c.get(o, 0) for o in q["opciones"]}
            elif q["tipo"] in ("escala", "numero"):
                nums = [float(v) for v in values]
                item["average"] = round(sum(nums) / len(nums), 2) if nums else None
                if q["tipo"] == "escala":
                    c = Counter(int(v) for v in nums)
                    item["counts"] = {str(i): c.get(i, 0) for i in range(1, 6)}
            else:
                item["texts"] = values[-50:]
            out.append(item)
        return {"token": survey["token"], "titulo": survey["titulo"], "open": survey["open"],
                "responses": len(responses), "questions": out, "simulation": survey.get("simulation")}

    async def simulate(self, project: Project, survey: dict, brief: str) -> dict:
        """Respuestas simuladas de 50 personas del segmento. Se guardan aparte y se contrastan con las reales."""
        qs = [{k: q[k] for k in ("id", "texto", "tipo", "opciones")} for q in survey["preguntas"]]
        prompt = (f"Segmento y problema (lo que ADAN sabe):\n{brief[:5000]}\n\nEncuesta:\n"
                  f"{json.dumps(qs, ensure_ascii=False)}\n\n"
                  f"Simula {SIM_SIZE} respuestas. Por pregunta (`id`): `conteos` = cuántas personas eligieron cada opción "
                  "(opcion y multiple; en escala, las claves '1' a '5'); `promedio` = promedio para escala y numero (0 si no "
                  "aplica); `textos` = 3 a 5 respuestas abiertas típicas para preguntas de texto (vacío si no aplica). "
                  "`perfil`: a quiénes simulaste, en una frase. `supuestos`: en qué te basaste y los límites de la "
                  "simulación (máximo 4).")
        resp = await self.llm.chat_json([LLMMessage("system", SIMULATOR), LLMMessage("user", prompt)], SIM_SCHEMA,
                                        temperature=0.5, max_tokens=4000)
        data = resp.parsed if isinstance(resp.parsed, dict) else {}
        by_id = {r.get("id"): r for r in data.get("respuestas") or [] if isinstance(r, dict)}
        questions = []
        for q in survey["preguntas"]:
            r = by_id.get(q["id"]) or {}
            item = {"id": q["id"], "texto": q["texto"], "tipo": q["tipo"]}
            if q["tipo"] in ("opcion", "multiple", "escala"):
                keys = q["opciones"] if q["tipo"] != "escala" else [str(i) for i in range(1, 6)]
                raw = r.get("conteos") if isinstance(r.get("conteos"), dict) else {}
                item["counts"] = {k: max(0, int(float(raw.get(k, 0) or 0))) for k in keys}
            if q["tipo"] in ("escala", "numero"):
                item["average"] = round(float(r.get("promedio") or 0), 2)
            if q["tipo"] == "texto":
                item["texts"] = normalize_list(r.get("textos"))[:5]
            questions.append(item)
        simulation = {"size": SIM_SIZE, "perfil": normalize_string(data.get("perfil")),
                      "supuestos": normalize_list(data.get("supuestos"))[:4], "questions": questions, "created_at": _now()}
        doc = self._doc(survey["token"], project)
        if doc is not None:
            stored = json.loads(doc.content)
            stored["simulation"] = simulation
            doc.content = json.dumps(stored, ensure_ascii=False)
            self.db.commit()
        return simulation

    async def insights(self, survey: dict) -> dict:
        results = self.results(survey)
        if results["responses"] < 3:
            raise ValueError("Se necesitan al menos 3 respuestas para sacar conclusiones.")
        prompt = ("Resultados de la encuesta (totales calculados):\n" + json.dumps(results, ensure_ascii=False)[:20000]
                  + "\n\n`resumen`: qué dicen los datos, en 3 a 5 frases, con cifras (n de N). `hallazgos`: hasta 6, con "
                    "cifras. `evidencia_sugerida`: hasta 5 afirmaciones verificables con el número de respuestas que las "
                    "respaldan (ej. '7 de 10 encuestados pagaron más de COP 200.000 por…'); `polaridad` contradicts si "
                    "la cifra va en contra del problema planteado. `alertas`: límites de la muestra (tamaño, sesgo de a "
                    "quién se le envió). Sé honesto: pocas respuestas son una señal, no una prueba.")
        resp = await self.llm.chat_json([LLMMessage("system", DESIGNER), LLMMessage("user", prompt)], INSIGHTS_SCHEMA,
                                        temperature=0.2, max_tokens=2500)
        data = resp.parsed if isinstance(resp.parsed, dict) else {}
        source = f"Encuesta ADAN «{survey['titulo']}» ({results['responses']} respuestas, {survey['created_at'][:10]})"
        return {"resumen": normalize_string(data.get("resumen")), "hallazgos": normalize_list(data.get("hallazgos")),
                "alertas": normalize_list(data.get("alertas")),
                "evidencia_sugerida": [{"afirmacion": normalize_string(e.get("afirmacion")), "tipo": "testimony",
                                        "polaridad": e.get("polaridad") if e.get("polaridad") == "contradicts" else "supports",
                                        "fuente": source}
                                       for e in data.get("evidencia_sugerida") or [] if isinstance(e, dict)
                                       and normalize_string(e.get("afirmacion"))][:5]}
