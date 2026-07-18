"""BP-0006 - AD-005 SS2.3: Mercado y Comercial."""

import uuid

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.mixins import ContratoBaseMixin


class ClienteFinal(Base, ContratoBaseMixin):
    """AD-005 SS2.3. Entidad 1:N con Empresa."""

    __tablename__ = "clientes_finales"

    empresa_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("empresas.id"))
    segmento: Mapped[str | None] = mapped_column(String(255), nullable=True)


class Mercado(Base, ContratoBaseMixin):
    """AD-005 SS2.3. Entidad N:M con Empresa - tambien destino de la Estrategia 'Internacionalizarse'."""

    __tablename__ = "mercados"

    nombre: Mapped[str] = mapped_column(String(255))
    tamano: Mapped[str | None] = mapped_column(String(100), nullable=True)


class ProductoServicio(Base, ContratoBaseMixin):
    """AD-005 SS2.3. Entidad 1:N con Empresa - destino de la Estrategia 'Cambiar modelo de negocio'."""

    __tablename__ = "productos_servicios"

    empresa_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("empresas.id"))
    categoria: Mapped[str | None] = mapped_column(String(255), nullable=True)
    propuesta_valor: Mapped[str | None] = mapped_column(String, nullable=True)


class Competidor(Base, ContratoBaseMixin):
    """AD-005 SS2.3. Relacion ternaria con Empresa y Mercado (Workshop de Relaciones SS2)."""

    __tablename__ = "competidores"

    empresa_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("empresas.id"))
    mercado_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("mercados.id"))
    nombre: Mapped[str] = mapped_column(String(255))


class Proveedor(Base, ContratoBaseMixin):
    """AD-005 SS2.3. Entidad N:1 con Empresa. Destino de las Estrategias 'Comprar software'/'Tercerizar'."""

    __tablename__ = "proveedores"

    empresa_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("empresas.id"))
    nombre: Mapped[str] = mapped_column(String(255))
    criticidad: Mapped[str | None] = mapped_column(String(50), nullable=True)
