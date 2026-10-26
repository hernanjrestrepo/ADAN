"""Interesados que dejan sus datos en la landing que construye Genexis (con autorización, Ley 1581).

Revision ID: 0012
Revises: 0011
Create Date: 2026-10-26 16:00:00
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '0012'
down_revision: Union[str, None] = '0011'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('mvp_leads',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('company_id', sa.String(length=36), nullable=False),
    sa.Column('site', sa.String(length=80), nullable=False),
    sa.Column('name', sa.String(length=120), nullable=True),
    sa.Column('email', sa.String(length=200), nullable=True),
    sa.Column('phone', sa.String(length=40), nullable=True),
    sa.Column('message', sa.Text(), nullable=True),
    sa.Column('consent', sa.Boolean(), nullable=False),
    sa.Column('consent_version', sa.String(length=20), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_mvp_leads_company_id'), 'mvp_leads', ['company_id'], unique=False)
    op.create_index(op.f('ix_mvp_leads_created_at'), 'mvp_leads', ['created_at'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_mvp_leads_created_at'), table_name='mvp_leads')
    op.drop_index(op.f('ix_mvp_leads_company_id'), table_name='mvp_leads')
    op.drop_table('mvp_leads')
