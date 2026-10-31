"""Construcción de la empresa: Expediente de creación (lo que la hace existir y operar) e identidad de marca
(nombre, logo, slogan y manual). Todo queda en Documentos del proyecto: nada se pierde ni se reescribe en silencio."""
from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.ai.base import LLMAdapter, LLMMessage
from app.ai.normalize import normalize_list, normalize_string
from app.ai.router import for_tier
from app.constitucion import dominios
from app.empresa.catalog import COUNTRIES, country_code, items_for
from app.models.models import Company, Document, Project

STATUSES = ("pendiente", "en_curso", "preparado", "validado", "observado", "no_aplica")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _latest(db: Session, project: Project, doc_type: str) -> Document | None:
    return db.query(Document).filter(Document.project_id == project.id, Document.doc_type == doc_type) \
        .order_by(Document.created_at.desc()).first()


def _load(db: Session, project: Project, doc_type: str) -> dict:
    doc = _latest(db, project, doc_type)
    try:
        return json.loads(doc.content) if doc and doc.content else {}
    except json.JSONDecodeError:
        return {}


def _save(db: Session, project: Project, doc_type: str, title: str, data: dict) -> dict:
    doc = _latest(db, project, doc_type)
    if doc is None:
        db.add(Document(project_id=project.id, title=title, doc_type=doc_type, origin="generated_by_adan",
                        content=json.dumps(data, ensure_ascii=False)))
    else:
        doc.content = json.dumps(data, ensure_ascii=False)
    db.commit()
    return data


# =========================================================================================
# Expediente de creación
# =========================================================================================

PREPARER = (
    "Eres el área legal, tributaria y de operación de ADAN. Preparas para el fundador TODO lo necesario de un trámite "
    "de creación de empresa, para alguien que no sabe nada de empresas: qué es y para qué sirve, documentos que debe "
    "llevar o cargar, los textos ya redactados con los datos de su empresa (dejando entre [corchetes] lo que solo él "
    "sabe), el paso a paso exacto (presencial o en línea), dónde se hace (entidad y sitio oficial con su URL) y "
    "cuánto cuesta según la fuente oficial vigente (si no estás seguro de una tarifa, dilo y di dónde consultarla; "
    "nunca inventes cifras). Termina con una lista de verificación. Markdown claro, de tú, en español."
)

VALIDATOR = (
    "Eres el validador de documentos de ADAN. Revisas un documento oficial cargado por el fundador y comparas sus "
    "datos con los de su empresa. Eres estricto y honesto: si el documento no es del tipo esperado, está incompleto o "
    "los datos no coinciden, lo dices con precisión."
)

VALIDATION_SCHEMA = {
    "type": "object", "additionalProperties": False,
    "required": ["valido", "tipo_detectado", "nombre_en_documento", "coincide_nombre", "numero_identificacion",
                 "fecha", "observaciones"],
    "properties": {
        "valido": {"type": "boolean"}, "tipo_detectado": {"type": "string"},
        "nombre_en_documento": {"type": "string"}, "coincide_nombre": {"type": "boolean"},
        "numero_identificacion": {"type": "string"}, "fecha": {"type": "string"},
        "observaciones": {"type": "array", "items": {"type": "string"}},
    },
}


class Expediente:
    def __init__(self, llm: LLMAdapter | None, db: Session):
        self.llm = for_tier(llm, "standard") if llm is not None else None
        self.db = db

    def view(self, project: Project, company: Company) -> dict:
        data = _load(self.db, project, "expediente")
        code = data.get("pais") or country_code(company.country)
        state = data.get("items", {})
        items = []
        for it in items_for(code):
            st = state.get(it["id"], {})
            items.append({**it, "estado": st.get("estado", "pendiente"), "nota": st.get("nota", ""),
                          "preparado_doc": st.get("preparado_doc"), "validacion": st.get("validacion"),
                          "actualizado": st.get("actualizado")})
        # Lo que ya existe en ADAN cuenta solo
        marca = _load(self.db, project, "marca")
        auto = {"nombre": bool(marca.get("nombre_elegido")), "logo": bool(marca.get("logo_elegido")),
                "presupuesto": _latest(self.db, project, "financial_model") is not None,
                "organigrama": _latest(self.db, project, "org_chart") is not None,
                "estatutos": _latest(self.db, project, "statutes") is not None}
        for it in items:
            if auto.get(it["id"]) and it["estado"] in ("pendiente", "en_curso"):
                it["estado"] = "validado" if it["modo"] == "adan" else "preparado"
                it["nota"] = it["nota"] or "Hecho en ADAN."
        done = sum(1 for i in items if i["estado"] in ("validado", "no_aplica"))
        return {"pais": code, "pais_nombre": COUNTRIES.get(code, COUNTRIES["OTRO"])[0], "items": items,
                "hechos": done, "total": len(items), "identificacion": data.get("identificacion", {})}

    def set_country(self, project: Project, code: str) -> None:
        data = _load(self.db, project, "expediente")
        data["pais"] = code if code in COUNTRIES else "OTRO"
        _save(self.db, project, "expediente", "Expediente de creación", data)

    def set_status(self, project: Project, item_id: str, estado: str, nota: str = "", **extra) -> None:
        data = _load(self.db, project, "expediente")
        items = data.setdefault("items", {})
        items[item_id] = {**items.get(item_id, {}), "estado": estado, "nota": nota[:500], "actualizado": _now(), **extra}
        _save(self.db, project, "expediente", "Expediente de creación", data)

    async def prepare(self, project: Project, company: Company, item: dict, context: str, country_name: str) -> Document:
        prompt = (f"{context}\n\nPaís: {country_name}.\nTrámite: {item['titulo']} — {item['que_es']}\n"
                  f"Quién lo hace: {item['modo']}. Documento que lo prueba: {item['documento'] or 'lo produce ADAN'}.\n\n"
                  "Prepara el paquete completo de este trámite para ESTA empresa. Si es un documento que ADAN redacta "
                  "(política de datos, contratos, Operating Agreement, campos de los Articles, respuestas del SS-4), "
                  "redáctalo completo. Si es presencial, deja el checklist de lo que debe llevar y el paso a paso en la "
                  "oficina. Si es en línea, el portal oficial y qué poner en cada campo.")
        resp = await self.llm.chat([LLMMessage("system", PREPARER), LLMMessage("user", prompt)], max_tokens=6000)
        doc = Document(project_id=project.id, title=f"Expediente · {item['titulo']}"[:255], doc_type="expediente_paquete",
                       origin="generated_by_adan", content=resp.content or "")
        self.db.add(doc)
        self.db.commit()
        self.db.refresh(doc)
        self.set_status(project, item["id"], "preparado", "ADAN dejó listo el paquete.", preparado_doc=doc.id)
        return doc

    async def validate(self, project: Project, company: Company, item: dict, filename: str, text: str) -> dict:
        prompt = (f"Empresa: {company.name}. Documento esperado: {item['documento']} (trámite: {item['titulo']}).\n"
                  f"Archivo cargado: {filename}\nTexto del documento:\n{text[:15000]}\n\n"
                  "`valido`: true solo si es el documento esperado, está a nombre de la empresa (o de su representante "
                  "cuando aplica) y no tiene inconsistencias. `nombre_en_documento`: la razón social que aparece. "
                  "`numero_identificacion`: NIT, EIN, número de matrícula o radicado que aparezca (vacío si no hay). "
                  "`fecha`: fecha de expedición. `observaciones`: lo que no cuadra o lo que falta (vacío si nada).")
        resp = await self.llm.chat_json([LLMMessage("system", VALIDATOR), LLMMessage("user", prompt)], VALIDATION_SCHEMA,
                                        temperature=0.1, max_tokens=1500)
        data = resp.parsed if isinstance(resp.parsed, dict) else {}
        result = {"valido": bool(data.get("valido")), "tipo_detectado": normalize_string(data.get("tipo_detectado")),
                  "nombre_en_documento": normalize_string(data.get("nombre_en_documento")),
                  "coincide_nombre": bool(data.get("coincide_nombre")),
                  "numero_identificacion": normalize_string(data.get("numero_identificacion")),
                  "fecha": normalize_string(data.get("fecha")), "observaciones": normalize_list(data.get("observaciones")),
                  "archivo": filename, "revisado": _now()}
        self.db.add(Document(project_id=project.id, title=f"Soporte · {item['titulo']} · {filename}"[:255],
                             doc_type="expediente_soporte", origin="received_from_client", content=text[:200000]))
        self.db.commit()
        self.set_status(project, item["id"], "validado" if result["valido"] else "observado",
                        "Documento validado por ADAN." if result["valido"] else "; ".join(result["observaciones"])[:500],
                        validacion=result)
        if result["valido"] and result["numero_identificacion"]:
            data = _load(self.db, project, "expediente")
            data.setdefault("identificacion", {})[item["id"]] = result["numero_identificacion"]
            _save(self.db, project, "expediente", "Expediente de creación", data)
        return result


# =========================================================================================
# Marca: nombre, logo, slogan y manual
# =========================================================================================

NAMER = (
    "Eres el estratega de marca de ADAN. Creas nombres de empresa pegajosos y fáciles de mercadear con base en la "
    "ciencia del naming:\n"
    "- Fluidez de procesamiento (Alter y Oppenheimer): nombres fáciles de pronunciar y leer se perciben más confiables "
    "y se recuerdan mejor; 2 o 3 sílabas, idealmente menos de 10 letras.\n"
    "- Simbolismo fonético (efecto bouba/kiki; Klink, Yorkston y Menon): vocales anteriores (i, e) y consonantes "
    "oclusivas sordas (k, t, p) evocan rapidez, precisión y tecnología; vocales posteriores (o, u) y consonantes "
    "suaves (b, m, l) evocan solidez, calidez y confianza. Elige el sonido según la personalidad de la marca.\n"
    "- Distintividad y memorabilidad: evita lo genérico y descriptivo; prefiere nombres evocadores, metáforas o "
    "inventados con raíz reconocible.\n"
    "- Pruebas SMILE y SCRATCH (Alexandra Watkins, Hello, My Name Is Awesome): Sugerente, Significativo, con "
    "Imaginería, con Recorrido y Emotivo; sin ortografía difícil, sin copiar a la competencia, sin restringir el "
    "crecimiento, sin ser molesto, aburrido, críptico o difícil de pronunciar.\n"
    "- Funciona en español y en inglés, sin connotaciones negativas, y es fácil de dictar por teléfono.\n"
    "Español. Sé honesto con los puntajes."
)

NAMES_SCHEMA = {
    "type": "object", "additionalProperties": False, "required": ["nombres"],
    "properties": {"nombres": {"type": "array", "items": {
        "type": "object", "additionalProperties": False,
        "required": ["nombre", "tipo", "por_que", "fluidez", "memorabilidad", "distintividad", "sonido"],
        "properties": {"nombre": {"type": "string"},
                       "tipo": {"type": "string", "enum": ["evocador", "metafora", "inventado", "compuesto", "descriptivo"]},
                       "por_que": {"type": "string"}, "sonido": {"type": "string"},
                       "fluidez": {"type": "integer"}, "memorabilidad": {"type": "integer"}, "distintividad": {"type": "integer"}}}}},
}

# Íconos disponibles para los logos (Lucide, licencia ISC) y tipografías incluidas en ADAN
ICONS = ["Plane", "Globe", "Map", "Compass", "Rocket", "Leaf", "Heart", "Star", "Sun", "Mountain", "Coffee", "ShoppingBag",
         "Store", "Briefcase", "Building2", "House", "Car", "Truck", "Ship", "Wallet", "CreditCard", "PiggyBank",
         "TrendingUp", "Lightbulb", "Brain", "Cpu", "Code", "Shield", "Lock", "Key", "Zap", "Flame", "Droplet", "Wind",
         "Sprout", "Apple", "Utensils", "Shirt", "Scissors", "Camera", "Music", "Book", "GraduationCap", "Stethoscope",
         "Activity", "Smile", "Users", "Handshake", "Sparkles", "Crown", "Gem", "Anchor", "Feather", "Palette", "Wrench",
         "Hammer", "Package", "Gift", "Bike", "Dumbbell", "PawPrint", "Infinity", "Target", "Award", "Cloud", "Wifi"]
FONTS = ["Montserrat", "Poppins", "Playfair Display", "Bebas Neue", "Space Grotesk", "Nunito", "Raleway", "Oswald"]
LAYOUTS = ["icono_texto", "monograma", "emblema", "solo_texto"]

LOGO_SCHEMA = {
    "type": "object", "additionalProperties": False, "required": ["conceptos"],
    "properties": {"conceptos": {"type": "array", "items": {
        "type": "object", "additionalProperties": False,
        "required": ["nombre_concepto", "estilo", "icono", "tipografia", "primario", "acento", "fondo", "por_que"],
        "properties": {"nombre_concepto": {"type": "string"}, "estilo": {"type": "string", "enum": LAYOUTS},
                       "icono": {"type": "string", "enum": ICONS}, "tipografia": {"type": "string", "enum": FONTS},
                       "primario": {"type": "string"}, "acento": {"type": "string"}, "fondo": {"type": "string"},
                       "por_que": {"type": "string"}}}}},
}

SLOGAN_SCHEMA = {
    "type": "object", "additionalProperties": False, "required": ["slogans"],
    "properties": {"slogans": {"type": "array", "items": {
        "type": "object", "additionalProperties": False, "required": ["texto", "por_que"],
        "properties": {"texto": {"type": "string"}, "por_que": {"type": "string"}}}}},
}

DESIGNER = (
    "Eres el director de arte de ADAN. Diseñas identidades corporativas con psicología del color (azul confianza, verde "
    "crecimiento y sostenibilidad, naranja energía, violeta creatividad y premium, rojo urgencia, negro lujo), "
    "contraste suficiente para leer (WCAG AA) y formas coherentes con la personalidad de la marca. Los colores van en "
    "hexadecimal #RRGGBB. Español."
)


def _hex(value: str, default: str) -> str:
    v = (value or "").strip()
    return v if len(v) == 7 and v.startswith("#") and all(c in "0123456789abcdefABCDEF" for c in v[1:]) else default


class Marca:
    def __init__(self, llm: LLMAdapter | None, db: Session):
        self.llm = for_tier(llm, "standard") if llm is not None else None
        self.db = db

    def view(self, project: Project) -> dict:
        return _load(self.db, project, "marca")

    def _store(self, project: Project, **changes) -> dict:
        data = {**_load(self.db, project, "marca"), **changes}
        return _save(self.db, project, "marca", "Marca de la empresa", data)

    async def names(self, project: Project, context: str, ideas: str = "") -> dict:
        prompt = (f"{context}\n\n" + (f"Lo que el fundador quiere transmitir: {ideas}\n\n" if ideas else "")
                  + "Propón 10 nombres. `tipo`, `por_que` (qué evoca y por qué se recuerda, en una frase), `sonido` (qué "
                    "transmite su sonido según el simbolismo fonético) y puntajes de 1 a 5 en `fluidez`, `memorabilidad` "
                    "y `distintividad`. Que al menos 3 sean inventados o metáforas con buen dominio probable.")
        resp = await self.llm.chat_json([LLMMessage("system", NAMER), LLMMessage("user", prompt)], NAMES_SCHEMA,
                                        temperature=0.9, max_tokens=3000)
        data = resp.parsed if isinstance(resp.parsed, dict) else {}
        raw = [n for n in data.get("nombres") or [] if isinstance(n, dict) and normalize_string(n.get("nombre"))][:10]

        async def with_domains(n: dict) -> dict:
            try:
                d = await dominios.check(n["nombre"])
                free = [x["domain"] for x in d["domains"] if x["status"] in ("disponible", "probable_libre")]
            except Exception:  # noqa: BLE001 - sin red, el nombre igual sirve
                free = []
            score = sum(max(1, min(5, int(n.get(k) or 3))) for k in ("fluidez", "memorabilidad", "distintividad"))
            return {"nombre": normalize_string(n["nombre"])[:60], "tipo": n.get("tipo", "evocador"),
                    "por_que": normalize_string(n.get("por_que")), "sonido": normalize_string(n.get("sonido")),
                    "fluidez": int(n.get("fluidez") or 3), "memorabilidad": int(n.get("memorabilidad") or 3),
                    "distintividad": int(n.get("distintividad") or 3), "puntaje": score, "dominios_libres": free[:4]}

        # Primero los que tienen dominio libre; luego por puntaje
        names = sorted(await asyncio.gather(*(with_domains(n) for n in raw)),
                       key=lambda x: (0 if x["dominios_libres"] else 1, -x["puntaje"]))
        return self._store(project, nombres=names, nombres_generados=_now())

    def choose_name(self, project: Project, company: Company, name: str, adopt: bool) -> dict:
        if adopt:
            company.name = name[:255]
            self.db.commit()
        return self._store(project, nombre_elegido=name)

    async def logos(self, project: Project, context: str, name: str) -> dict:
        prompt = (f"{context}\n\nNombre de la marca: {name}\n\nDiseña 4 conceptos de logo MUY distintos entre sí, uno por "
                  f"estilo ({', '.join(LAYOUTS)}). `icono`: el ícono que mejor representa la idea (de la lista). "
                  "`tipografia`: de la lista, según la personalidad. `primario`, `acento` y `fondo` en #RRGGBB con buen "
                  "contraste entre primario y fondo. `por_que`: qué transmite (color, forma y letra) en una frase.")
        resp = await self.llm.chat_json([LLMMessage("system", DESIGNER), LLMMessage("user", prompt)], LOGO_SCHEMA,
                                        temperature=0.8, max_tokens=2500)
        data = resp.parsed if isinstance(resp.parsed, dict) else {}
        concepts = []
        for i, c in enumerate(data.get("conceptos") or []):
            if not isinstance(c, dict):
                continue
            concepts.append({"id": f"c{i + 1}", "nombre_concepto": normalize_string(c.get("nombre_concepto")) or f"Concepto {i + 1}",
                             "estilo": c.get("estilo") if c.get("estilo") in LAYOUTS else LAYOUTS[i % 4],
                             "icono": c.get("icono") if c.get("icono") in ICONS else "Sparkles",
                             "tipografia": c.get("tipografia") if c.get("tipografia") in FONTS else "Montserrat",
                             "primario": _hex(c.get("primario"), "#2563eb"), "acento": _hex(c.get("acento"), "#f59e0b"),
                             "fondo": _hex(c.get("fondo"), "#ffffff"), "por_que": normalize_string(c.get("por_que"))})
        return self._store(project, logos=concepts[:4], logo_nombre=name)

    def choose_logo(self, project: Project, company: Company, concept_id: str, image: str | None) -> dict:
        data = _load(self.db, project, "marca")
        concept = next((c for c in data.get("logos", []) if c["id"] == concept_id), None)
        if concept is None:
            raise ValueError("Ese concepto de logo no existe")
        company.brand_color = concept["primario"]
        company.brand_accent = concept["acento"]
        if image:
            company.logo = image
        self.db.commit()
        return self._store(project, logo_elegido=concept)

    def adopt_existing(self, project: Project, company: Company, image: str, colors: list[str], source: str) -> dict:
        """El logo que la empresa ya tiene (de su web o subido por el fundador) pasa a ser su identidad en ADAN."""
        primary = colors[0] if colors else (company.brand_color or "#2563eb")
        accent = colors[1] if len(colors) > 1 else (company.brand_accent or primary)
        concept = {"id": "actual", "nombre_concepto": "Logo actual de la empresa", "estilo": "actual", "icono": "",
                   "tipografia": "", "primario": primary, "acento": accent, "fondo": "#ffffff",
                   "por_que": f"Es el logo que la empresa ya usa ({source})."}
        company.logo = image
        company.brand_color = primary
        company.brand_accent = accent
        self.db.commit()
        return self._store(project, logo_elegido=concept, nombre_elegido=company.name, logo_fuente=source)

    async def slogans(self, project: Project, context: str, name: str) -> dict:
        prompt = (f"{context}\n\nMarca: {name}\n\nPropón 6 slogans cortos (máximo 6 palabras), memorables, que digan el "
                  "beneficio principal o la emoción, con ritmo; `por_que` en una frase.")
        resp = await self.llm.chat_json([LLMMessage("system", NAMER), LLMMessage("user", prompt)], SLOGAN_SCHEMA,
                                        temperature=0.9, max_tokens=1500)
        data = resp.parsed if isinstance(resp.parsed, dict) else {}
        slogans = [{"texto": normalize_string(s.get("texto"))[:80], "por_que": normalize_string(s.get("por_que"))}
                   for s in data.get("slogans") or [] if isinstance(s, dict) and normalize_string(s.get("texto"))][:6]
        return self._store(project, slogans=slogans)

    def choose_slogan(self, project: Project, text: str) -> dict:
        return self._store(project, slogan=text[:120])

    async def manual(self, project: Project, context: str) -> dict:
        data = _load(self.db, project, "marca")
        logo = data.get("logo_elegido") or {}
        prompt = (f"{context}\n\nMarca: {data.get('nombre_elegido') or ''}. Slogan: {data.get('slogan') or ''}. "
                  f"Logo: estilo {logo.get('estilo')}, ícono {logo.get('icono')}, tipografía {logo.get('tipografia')}, "
                  f"colores {logo.get('primario')} / {logo.get('acento')} / {logo.get('fondo')}.\n\n"
                  "Escribe el manual de marca básico en Markdown: esencia (propósito, promesa, personalidad), tono de voz "
                  "con ejemplos de cómo sí y cómo no hablar, paleta con usos de cada color, tipografías (títulos y "
                  "textos), uso correcto e incorrecto del logo, y aplicaciones (redes, web, tarjeta, WhatsApp).")
        resp = await self.llm.chat([LLMMessage("system", DESIGNER), LLMMessage("user", prompt)], max_tokens=5000)
        return self._store(project, manual=resp.content or "", manual_generado=_now())

    def identity(self, company: Company, project: Project) -> dict:
        data = _load(self.db, project, "marca")
        return {"nombre": company.name, "slogan": data.get("slogan") or "", "logo": company.logo,
                "color": company.brand_color, "acento": company.brand_accent}
