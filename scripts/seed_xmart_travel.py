"""Carga Xmart Travel en ADÁN desde las respuestas de Hernán (2026-10-02).

Regla de honestidad (AD-CMP-05): solo lo marcado [Sé] entra como dato; los [Supuesto] quedan
como hipótesis en el texto (nunca como evidencia), y lo [Solo Hernán] queda listado como pendiente.
No hay entrevistas con clientes: el Gate del Nivel 1 debe decir, con razón, que falta evidencia.

Uso (con ADÁN corriendo, p. ej. `docker compose up`):
    python scripts/seed_xmart_travel.py --base http://localhost:5174 \
        --email tu@correo.com --name "Hernán Restrepo" --password '...'
Crea la cuenta si no existe (aceptando la política de datos) o entra con ella.
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request

DESCRIPTION = (
    "Plataforma de viajes con una consultora de IA (avatar \"Xime\") que perfila al cliente y le arma, "
    "reserva y acompaña el viaje completo, 24/7. Opera bajo la agencia socia We Travel (RNT 101006, "
    "Barranquilla) como agencia legal y operadora. Etapa conceptual: plan de negocio y blueprint, sin "
    "producto ni clientes."
)

FIRST_MESSAGE = (
    "Te cuento Xmart Travel. Planear un viaje exige muchas herramientas y decisiones separadas: vuelos, "
    "hotel, seguros, requisitos legales, presupuesto, comida y alergias, equipaje, grupo; nadie lo integra "
    "ni acompaña durante el viaje. Afecta a viajeros individuales y familias, a empresas con gastos de viaje "
    "y a colegios y grupos (viajes de grado). Mi hipótesis, sin validar: hoy lo resuelven con OTAs, agencias "
    "por WhatsApp y mucha improvisación. Quiero ser honesto: no he hecho entrevistas con clientes, no tengo "
    "cifras de cuánto les cuesta el problema y no hay producto. Lo que tengo es el plan de negocio, el "
    "blueprint y la alianza con We Travel. ¿Qué evidencia necesito para validar que el dolor es real?"
)

MARKETS = [
    ("Viajeros individuales y familias (Colombia)",
     "Supuesto de arranque, sin confirmar: familias y parejas de ingreso medio-alto que viajan en vacaciones."),
    ("Empresas con gastos de viaje (Xmart Empresas)", "Control de gastos de viaje corporativo."),
    ("Colegios y grupos (viajes de grado)", "Canal B2B."),
]
COMPETITORS = [
    ("OTAs (Booking, Expedia, Despegar)", 0), ("Agencias tradicionales colombianas", 0),
    ("Planificadores con IA (Mindtrip y similares)", 0), ("Plataformas corporativas (Navan y similares)", 1),
]
OFFERINGS = [
    ("Consultora IA \"Xime\" (WhatsApp y web)", "Perfilado del viajero, plan con presupuesto, reserva y soporte en viaje."),
    ("Xmart Empresas", "Control de gastos de viaje: SaaS + tarifa por viaje + comisión."),
    ("Viajes de grado y grupos", "Venta B2B a colegios y empresas."),
    ("Ancillaries", "Seguros y traslados."),
]
RISKS = [
    ("operativo", "We Travel sin API utilizable: crítico para el cronograma.", "alta"),
    ("legal", "Políticas de WhatsApp 2026 que limitan chatbots de propósito general.", "alta"),
    ("legal", "Cumplimiento: Ley 1581 (datos de salud), Ley 2300 (horarios de contacto), RNT para plataformas, menores.", "alta"),
    ("reputacional", "Alucinaciones de la IA en información crítica (precios, requisitos de viaje).", "alta"),
    ("financiero", "Costo y latencia de la IA por reserva.", "media"),
    ("operativo", "Dependencia de un solo socio operativo (We Travel).", "media"),
    ("reputacional", "Marca: existe una página de Facebook \"Xmart travel agency\" sin revisar.", "media"),
    ("mercado", "Falta total de validación con clientes.", "alta"),
]
# [Sé] Dato externo citado en el plan. Respalda la tendencia del sector, no el dolor del cliente:
EXTERNAL = [(
    "El sector se mueve hacia la reserva agéntica con IA: Sabre, PayPal y Mindtrip anunciaron reserva "
    "agéntica (mayo de 2026). Prueba la tendencia del sector, no que los clientes de Xmart tengan el dolor.",
    "Plan de negocio Xmart Travel, que cita el anuncio de Sabre, PayPal y Mindtrip (mayo de 2026)",
)]
PENDING_FOR_HERNAN = [
    "Razón social y si Xmart tiene entidad propia", "Fecha real de inicio",
    "Cifras de cuánto le cuesta el problema al cliente (tiempo, dinero)",
    "Primeras 15-20 entrevistas con viajeros, empresas y colegios",
    "Segmento de arranque confirmado", "Precios de Empresas y Plus",
    "Inversión ya hecha y capital disponible", "Dedicación, socios y composición accionaria",
    "Quién del equipo existe hoy", "Contrato con We Travel y acceso a su API",
    "Objetivos a 12 meses confirmados", "Autorización de datos anonimizados (decisión personal)",
]


class Api:
    def __init__(self, base: str):
        self.base = base.rstrip("/") + "/api/v1"
        self.token: str | None = None

    def call(self, method: str, path: str, body: dict | None = None):
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(self.base + path, data=data, method=method)
        req.add_header("Content-Type", "application/json")
        req.add_header("X-Requested-With", "adan")
        if self.token:
            req.add_header("Authorization", f"Bearer {self.token}")
        try:
            with urllib.request.urlopen(req, timeout=180) as resp:
                raw = resp.read()
                return resp.status, (json.loads(raw) if raw else None)
        except urllib.error.HTTPError as exc:
            return exc.code, json.loads(exc.read() or b"null")


def must(result, what):
    status, body = result
    if status >= 400:
        sys.exit(f"Falló {what}: {status} {body}")
    return body


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--base", default="http://localhost:5174")
    ap.add_argument("--email", required=True)
    ap.add_argument("--name", default="Hernán Restrepo")
    ap.add_argument("--password", required=True)
    ap.add_argument("--no-chat", action="store_true", help="no enviar el primer mensaje a ADÁN (no usa el modelo)")
    args = ap.parse_args()
    api = Api(args.base)

    status, body = api.call("POST", "/auth/login", {"email": args.email, "password": args.password})
    if status != 200:
        body = must(api.call("POST", "/auth/register", {"email": args.email, "name": args.name,
                                                        "password": args.password, "accept_data_policy": True}),
                    "el registro")
    api.token = body["access_token"]

    company = must(api.call("POST", "/companies/", {"name": "Xmart Travel", "description": DESCRIPTION,
                                                    "industry": "Turismo — agencia de viajes con IA",
                                                    "country": "Colombia"}), "crear la empresa")
    cid = company["id"]
    twin = f"/twin/{cid}/entities"
    print(f"Empresa creada: {cid}")

    must(api.call("POST", f"{twin}/brands", {"name": "Xmart Travel",
                                             "positioning": "Agencia de viajes con IA de punta a punta"}), "marca")
    market_ids = [must(api.call("POST", f"{twin}/markets", {"name": n, "segment_definition": d}), "mercado")["id"]
                  for n, d in MARKETS]
    for name, idx in COMPETITORS:
        must(api.call("POST", f"{twin}/competitors", {"name": name, "market_id": market_ids[idx],
                                                      "notes": "Benchmark del plan con información pública"}), "competidor")
    for name, prop in OFFERINGS:
        must(api.call("POST", f"{twin}/offerings", {"name": name, "kind": "servicio", "value_proposition": prop}),
             "oferta")
    must(api.call("POST", f"{twin}/suppliers", {"name": "We Travel (RNT 101006, Barranquilla)", "criticality": "alta",
                                                "supplies": "Licencia, emisión, mayoristas y respaldo humano 24/7"}),
         "proveedor")
    must(api.call("POST", f"{twin}/initiatives", {"name": "MVP de 16 semanas", "state": "proposed", "objective": (
        "Xime en WhatsApp y web, perfil con consentimientos, planificador con presupuesto, cotizador con inventario "
        "de We Travel, pago por enlace con emisión humana. Salida: 100 reservas pagadas, CSAT ≥ 4,6, conversión "
        "≥ 5 %, 75 % resuelto por IA, costo de IA ≤ USD 7 por reserva.")}), "iniciativa")
    for kind, desc, severity in RISKS:
        must(api.call("POST", f"{twin}/risks", {"subject_type": "company", "subject_id": cid, "kind": kind,
                                                "description": desc, "severity": severity}), "riesgo")
    for claim, source in EXTERNAL:
        must(api.call("POST", f"/scoring/{cid}/evidence", {"claim": claim, "kind": "external", "source": source}),
             "evidencia")

    gate = must(api.call("GET", f"/scoring/{cid}/gate/1"), "gate")
    print(f"Gate del Nivel 1: {'alcanza' if gate['sufficient'] else 'falta evidencia'}")
    for item in gate["missing"]:
        print(f"  - {item}")
    print("Pendiente de Hernán (no se inventa):")
    for item in PENDING_FOR_HERNAN:
        print(f"  - {item}")

    if not args.no_chat:
        reply = must(api.call("POST", f"/nivel1/{cid}/chat", {"message": FIRST_MESSAGE}), "primer mensaje")
        print("\nADÁN responde:\n" + reply["message"]["content"])
    print(f"\nListo: entra a {args.base.rstrip('/')}/nivel1/{cid}")


if __name__ == "__main__":
    main()
