"""BP-0007 - AD-006 SS4: Usuario, Usuario Principal (entidades operativas de ADAN)."""

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.mixins import ContratoBaseMixin


class Usuario(Base, ContratoBaseMixin):
    """Persona con acceso a ADAN (AD-006 SS4). N:M con Proyecto - modelado en Sprint 4."""

    __tablename__ = "usuarios"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    display_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_principal: Mapped[bool] = mapped_column(
        Boolean, default=False
    )  # True cuando es Usuario Principal / "Responsable de Empresa" (AD-FUNC-06 SS3.1)
