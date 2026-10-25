"""El Expediente de creación: todo lo que hay que hacer para que la empresa exista y opere, según el país.

Cada ítem dice qué es, quién lo hace (`modo`: ADÁN lo produce, el fundador hace el trámite presencial o en línea),
qué documento lo prueba (lo que se carga para validarlo) y dónde se trabaja en ADÁN. En Colombia el registro en la
Cámara de Comercio se deja listo para que el fundador lo radique; en Estados Unidos se prepara todo para radicar en
línea (el pago y la firma son del fundador). Las cifras y tarifas oficiales se consultan en la fuente vigente.
"""
from __future__ import annotations

GROUPS = {"identidad": "Identidad", "numeros": "Números", "legal": "Legal y registro", "operacion": "Operación"}

# id, grupo, título, qué es, modo, documento que lo prueba (vacío si lo produce ADÁN), herramienta en ADÁN
_COMMON = [
    ("nombre", "identidad", "Nombre de la empresa", "Un nombre fácil de recordar y de mercadear, libre en registros y marcas.",
     "adan", "", "/marca"),
    ("dominio", "identidad", "Dominio web", "La dirección web (.com y del país). ADÁN te explica cómo comprarlo paso a paso.",
     "cliente_en_linea", "Factura o confirmación de compra del dominio", "/marca"),
    ("logo", "identidad", "Logo y manual de marca", "Logo, colores, tipografía y tono: la identidad que se usa en todo.",
     "adan", "", "/marca"),
    ("presupuesto", "numeros", "Presupuesto de arranque y flujo de caja", "Cuánto cuesta arrancar, flujo a 24 meses y punto de equilibrio.",
     "adan", "", "/finanzas"),
    ("organigrama", "numeros", "Organigrama con IA y Paradixe", "Quién hace qué: personas, agentes de IA y servicios de Paradixe.",
     "adan", "", "/finanzas"),
]

CO = _COMMON + [
    ("marca_registro", "identidad", "Registro de marca (SIC)", "Proteger el nombre y el logo ante la Superintendencia de Industria y Comercio.",
     "cliente_en_linea", "Radicado o certificado de registro de marca de la SIC", ""),
    ("estatutos", "legal", "Estatutos de la SAS", "El documento de constitución de la sociedad (SAS), listo para firmar.",
     "adan", "", "/constitucion"),
    ("registro_mercantil", "legal", "Registro en la Cámara de Comercio", "Matrícula de la sociedad en la Cámara de Comercio de tu ciudad. ADÁN alista todo el paquete; tú lo radicas.",
     "cliente_presencial", "Certificado de existencia y representación legal", ""),
    ("rut", "legal", "RUT ante la DIAN", "El registro tributario de la empresa (con el NIT).",
     "cliente_en_linea", "RUT de la empresa (formulario 001)", ""),
    ("cuenta_bancaria", "operacion", "Cuenta bancaria de la empresa", "Cuenta a nombre de la sociedad para recibir y pagar.",
     "cliente_presencial", "Certificación bancaria a nombre de la empresa", ""),
    ("facturacion", "operacion", "Facturación electrónica", "Habilitación ante la DIAN para facturar electrónicamente.",
     "cliente_en_linea", "Resolución de habilitación de facturación electrónica", ""),
    ("datos_personales", "legal", "Protección de datos (Ley 1581)", "Política de tratamiento de datos y, si aplica, registro de bases de datos (RNBD).",
     "adan", "", ""),
    ("contratos", "legal", "Contratos base", "Acuerdo de socios, términos y condiciones y contrato con clientes o proveedores clave.",
     "adan", "", ""),
    ("licencias", "legal", "Licencias y registros del sector", "Permisos propios de tu actividad (por ejemplo, el RNT para turismo).",
     "cliente_en_linea", "Certificado de la licencia o registro del sector", ""),
    ("seguridad_social", "operacion", "Nómina y seguridad social", "Afiliaciones (salud, pensión, riesgos laborales, caja) cuando contrates personas.",
     "cliente_en_linea", "Planilla o certificado de afiliación", ""),
]

US = _COMMON + [
    ("marca_registro", "identidad", "Trademark (USPTO)", "Proteger el nombre y el logo ante la oficina de marcas de EE. UU.",
     "cliente_en_linea", "Serial number o certificado de la USPTO", ""),
    ("estado", "legal", "Estado y tipo de empresa", "Elegir estado (Delaware, Wyoming, Florida…) y tipo (LLC o C-Corp) según tu caso.",
     "adan", "", ""),
    ("articles", "legal", "Articles of Organization (registro en línea)", "El registro de la LLC en el portal del estado. ADÁN deja todos los campos listos; tú pagas y radicas.",
     "cliente_en_linea", "Articles of Organization o Certificate of Formation aprobado", ""),
    ("registered_agent", "legal", "Registered Agent", "El agente registrado obligatorio en el estado elegido.",
     "cliente_en_linea", "Contrato o confirmación del Registered Agent", ""),
    ("operating_agreement", "legal", "Operating Agreement", "Las reglas internas de la LLC entre los socios.",
     "adan", "", ""),
    ("ein", "legal", "EIN ante el IRS", "El número tributario federal. ADÁN prepara las respuestas del formulario SS-4.",
     "cliente_en_linea", "Carta del IRS con el EIN (CP 575 o 147C)", ""),
    ("boi", "legal", "Reporte BOI (FinCEN)", "Reporte de beneficiarios finales: revisa si aplica según la norma vigente de FinCEN.",
     "cliente_en_linea", "Confirmación del reporte BOI (si aplica)", ""),
    ("cuenta_bancaria", "operacion", "Cuenta bancaria en EE. UU.", "Cuenta de la LLC (bancos en línea aceptan dueños extranjeros con EIN).",
     "cliente_en_linea", "Confirmación de apertura de la cuenta", ""),
    ("impuestos_estatales", "operacion", "Impuestos y licencias estatales", "Sales tax y licencias del estado o la ciudad, si aplican a tu actividad.",
     "cliente_en_linea", "Registro de sales tax o licencia", ""),
    ("contratos", "legal", "Contratos base", "Terms of Service, Privacy Policy y acuerdos con clientes o proveedores.",
     "adan", "", ""),
]

GENERIC = _COMMON + [
    ("marca_registro", "identidad", "Registro de marca", "Proteger el nombre y el logo ante la oficina de marcas del país.",
     "cliente_en_linea", "Radicado o certificado de registro de marca", ""),
    ("estatutos", "legal", "Estatutos o documento de constitución", "El documento que crea la sociedad según la ley del país.",
     "adan", "", "/constitucion"),
    ("registro_mercantil", "legal", "Registro mercantil", "Inscribir la sociedad ante la entidad de registro del país.",
     "cliente_presencial", "Certificado de existencia o de registro de la sociedad", ""),
    ("registro_tributario", "legal", "Registro tributario", "El número de identificación tributaria de la empresa.",
     "cliente_en_linea", "Constancia del registro tributario", ""),
    ("cuenta_bancaria", "operacion", "Cuenta bancaria de la empresa", "Cuenta a nombre de la sociedad.",
     "cliente_presencial", "Certificación bancaria", ""),
    ("facturacion", "operacion", "Facturación", "Habilitación para facturar según el país.",
     "cliente_en_linea", "Habilitación de facturación", ""),
    ("datos_personales", "legal", "Protección de datos", "Política de privacidad y tratamiento de datos según la ley del país.",
     "adan", "", ""),
    ("contratos", "legal", "Contratos base", "Acuerdo de socios, términos y condiciones.", "adan", "", ""),
    ("licencias", "legal", "Licencias del sector", "Permisos propios de la actividad.", "cliente_en_linea", "Certificado de la licencia", ""),
]

COUNTRIES = {"CO": ("Colombia", CO), "US": ("Estados Unidos", US), "OTRO": ("Otro país", GENERIC)}

MODES = {"adan": "Lo hace ADÁN contigo", "cliente_presencial": "Lo radicas tú (presencial)",
         "cliente_en_linea": "Lo haces tú en línea (ADÁN lo deja listo)"}


def country_code(country: str | None) -> str:
    c = (country or "").strip().lower()
    if c in ("co", "colombia"):
        return "CO"
    if c in ("us", "usa", "eeuu", "ee. uu.", "estados unidos", "united states"):
        return "US"
    return "OTRO"


def items_for(code: str) -> list[dict]:
    _, rows = COUNTRIES.get(code, COUNTRIES["OTRO"])
    return [{"id": i, "grupo": g, "titulo": t, "que_es": q, "modo": m, "documento": d, "herramienta": h}
            for i, g, t, q, m, d, h in rows]
