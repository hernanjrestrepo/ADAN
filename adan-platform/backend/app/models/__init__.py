"""Import every model module so SQLAlchemy's mapper registry resolves all relationships,
and so Alembic autogenerate sees the full metadata. BP-0006, BP-0007 (38 entidades)."""

from app.models.comercial import ClienteFinal, Competidor, Mercado, ProductoServicio, Proveedor
from app.models.conversacion import Agente, Conversacion, Tarea
from app.models.decision_score_evento import DecisionAdan, Evento, Score
from app.models.direccion import DecisionNegocio, Indicador, Meta, Objetivo
from app.models.empresa import AccionistaInversionista, Empresa, Marca, NarrativaFundacional
from app.models.finanzas import Activo, Gasto, Ingreso, Pasivo
from app.models.nivel import Card, Nivel
from app.models.operacion import ContratoNegocio, Documento, Iniciativa, Proceso, SucesoEmpresarial
from app.models.organizacion import Cargo, Departamento, Empleado, RolFuncional
from app.models.proyecto import Proyecto, Workspace
from app.models.usuario import Usuario

__all__ = [
    "AccionistaInversionista",
    "Activo",
    "Agente",
    "Card",
    "Cargo",
    "ClienteFinal",
    "Competidor",
    "Conversacion",
    "ContratoNegocio",
    "DecisionAdan",
    "DecisionNegocio",
    "Departamento",
    "Documento",
    "Empleado",
    "Empresa",
    "Evento",
    "Gasto",
    "Indicador",
    "Ingreso",
    "Iniciativa",
    "Marca",
    "Mercado",
    "Meta",
    "NarrativaFundacional",
    "Nivel",
    "Objetivo",
    "Pasivo",
    "Proceso",
    "ProductoServicio",
    "Proveedor",
    "Proyecto",
    "RolFuncional",
    "Score",
    "SucesoEmpresarial",
    "Tarea",
    "Usuario",
    "Workspace",
]
