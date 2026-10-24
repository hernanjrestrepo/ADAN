"""Comunidad ADÁN (AD-000 v2.0, componente Comunidad): la red de empresas, emprendedores, inversionistas y
mentores del ecosistema Paradixe.

- `community_profiles`: el perfil público de cada persona (opcional: solo aparece si la persona lo publica).
- `community_listings`: la vitrina de una empresa. Lo que la empresa declara (qué hace, qué busca) va junto al
  **Sello ADÁN**, que no lo escribe nadie: sale del Gemelo Digital (Niveles cerrados, Problem Score, evidencia,
  decisión del Board, La Arena). Las Selecciones Paradixe las marcan los curadores de Paradixe.
- `community_connections`: seguir, pedir contacto o mostrar interés de inversión. El correo de cada parte solo se
  comparte cuando la otra acepta (Ley 1581: mínimo dato).
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, String, Text

from app.core.database import Base, JSONType


def utcnow():
    return datetime.now(timezone.utc)


def gen_uuid():
    return str(uuid.uuid4())


PROFILE_KINDS = ("emprendedor", "empresa", "inversionista", "mentor", "proveedor")
STAGES = ("idea", "validacion", "operando", "escalando")
LOOKING_FOR = ("inversion", "socios", "clientes", "proveedores", "talento", "mentoria")
CONNECTION_KINDS = ("seguir", "contacto", "interes_inversion")
CONNECTION_STATUS = ("pendiente", "aceptada", "rechazada")


class CommunityProfile(Base):
    __tablename__ = "community_profiles"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), unique=True, nullable=False, index=True)
    display_name = Column(String(120), nullable=False)
    headline = Column(String(200), nullable=False, default="")
    bio = Column(Text, nullable=False, default="")
    kind = Column(String(20), nullable=False, default="emprendedor")
    city = Column(String(80), nullable=False, default="")
    country = Column(String(80), nullable=False, default="")
    website = Column(String(300), nullable=False, default="")
    linkedin = Column(String(300), nullable=False, default="")
    public = Column(Boolean, nullable=False, default=False)
    # Inversionistas: qué buscan (para que las empresas sepan a quién acercarse)
    ticket_min_usd = Column(Float, nullable=True)
    ticket_max_usd = Column(Float, nullable=True)
    sectors = Column(JSONType, nullable=False, default=list)
    stages = Column(JSONType, nullable=False, default=list)
    created_at = Column(DateTime, default=utcnow, nullable=False)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow, nullable=False)


class CompanyListing(Base):
    __tablename__ = "community_listings"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    company_id = Column(String(36), ForeignKey("companies.id"), unique=True, nullable=False, index=True)
    owner_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    published = Column(Boolean, nullable=False, default=True)
    name = Column(String(160), nullable=False)
    tagline = Column(String(200), nullable=False, default="")
    description = Column(Text, nullable=False, default="")
    sector = Column(String(120), nullable=False, default="")
    country = Column(String(80), nullable=False, default="")
    city = Column(String(80), nullable=False, default="")
    stage = Column(String(20), nullable=False, default="idea")
    looking_for = Column(JSONType, nullable=False, default=list)
    amount_sought_usd = Column(Float, nullable=True)
    website = Column(String(300), nullable=False, default="")
    # Sello ADÁN: calculado del Gemelo Digital al publicar y al actualizar (nunca lo edita la empresa)
    seal = Column(JSONType, nullable=False, default=dict)
    paradixe_selection = Column(Boolean, nullable=False, default=False)
    selection_note = Column(Text, nullable=False, default="")
    selected_by = Column(String(36), nullable=True)
    created_at = Column(DateTime, default=utcnow, nullable=False)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow, nullable=False)


class Connection(Base):
    __tablename__ = "community_connections"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    from_user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    to_user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    listing_id = Column(String(36), ForeignKey("community_listings.id"), nullable=True, index=True)
    kind = Column(String(20), nullable=False)
    message = Column(Text, nullable=False, default="")
    status = Column(String(12), nullable=False, default="pendiente")
    created_at = Column(DateTime, default=utcnow, nullable=False)
    responded_at = Column(DateTime, nullable=True)
