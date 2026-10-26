"""Visitas: cada página abierta (país, día, dispositivo) para el mapa y las cifras de la consola.

Revision ID: 0011
Revises: 0010
Create Date: 2026-10-25 22:30:00
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '0011'
down_revision: Union[str, None] = '0010'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('visits',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('path', sa.String(length=200), nullable=False),
    sa.Column('referrer', sa.String(length=120), nullable=True),
    sa.Column('country', sa.String(length=2), nullable=True),
    sa.Column('visitor', sa.String(length=24), nullable=False),
    sa.Column('mobile', sa.Boolean(), nullable=False),
    sa.Column('user_id', sa.String(length=36), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_visits_created_at'), 'visits', ['created_at'], unique=False)
    op.create_index(op.f('ix_visits_country'), 'visits', ['country'], unique=False)
    op.create_index(op.f('ix_visits_visitor'), 'visits', ['visitor'], unique=False)
    op.create_index('ix_visits_created_country', 'visits', ['created_at', 'country'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_visits_created_country', table_name='visits')
    op.drop_index(op.f('ix_visits_visitor'), table_name='visits')
    op.drop_index(op.f('ix_visits_country'), table_name='visits')
    op.drop_index(op.f('ix_visits_created_at'), table_name='visits')
    op.drop_table('visits')
