"""BP-0007 - AD-006 SS4: Usuario (entidad operativa de ADAN).

'Usuario Principal' (AD-006 Hallazgo 1, renombrado de "Fundador"; "Responsable de Empresa"
en AD-FUNC-06 SS3.1) no es una tabla separada: es un ROL - la relacion 1:N se modela como
el campo `usuario_principal_id` en Proyecto (ver proyecto.py), no como un flag en Usuario,
porque la responsabilidad es por Proyecto, no un atributo global de la persona."""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.mixins import ContratoBaseMixin


class Usuario(Base, ContratoBaseMixin):
    """Persona con acceso a ADAN (AD-006 SS4). N:M con Proyecto via tabla usuarios_proyectos."""

    __tablename__ = "usuarios"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    display_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
