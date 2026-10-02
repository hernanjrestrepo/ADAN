"""Política de tratamiento de datos (AD-DEC-0002 decisión 8, Ley 1581 de 2012).

La versión se guarda en cada constancia de consentimiento (`consents`): si el texto cambia,
sube la versión y queda claro qué aceptó cada persona y cuándo.
"""
POLICY_VERSION = "2026-10"

DATA_PROCESSING = "data_processing"
AGGREGATED_INTELLIGENCE = "aggregated_intelligence"
PURPOSES = {
    DATA_PROCESSING: "Tratamiento de mis datos para prestarme el servicio de ADÁN",
    AGGREGATED_INTELLIGENCE: ("Uso de mis datos, anonimizados y agregados con los de otras empresas, para "
                              "producir inteligencia de mercado. Nunca se venden datos crudos"),
}
