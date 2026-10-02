"""WO-107: evidencia clasificada por la jerarquía de validez de AD-CMP-05.

Los Scores del Responsable y Venture (AD-FUNC-07) no necesitan migración: `scores.score_type`
es texto sin restricción CHECK.

Revision ID: 0006
Revises: 0005
Create Date: 2026-10-02 13:21:03.368107
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '0006'
down_revision: Union[str, None] = '0005'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('evidence',
    sa.Column('company_id', sa.String(length=36), nullable=False),
    sa.Column('project_id', sa.String(length=36), nullable=False),
    sa.Column('level_number', sa.Integer(), nullable=True),
    sa.Column('dimension', sa.String(length=30), nullable=False),
    sa.Column('claim', sa.Text(), nullable=False),
    sa.Column('kind', sa.String(length=20), nullable=False),
    sa.Column('polarity', sa.String(length=20), nullable=False),
    sa.Column('source', sa.Text(), nullable=True),
    sa.Column('document_id', sa.String(length=36), nullable=True),
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('version', sa.Integer(), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('created_by', sa.String(length=120), nullable=True),
    sa.Column('updated_by', sa.String(length=120), nullable=True),
    sa.Column('evidence_source', sa.Text(), nullable=True),
    sa.Column('confidence_level', sa.Float(), nullable=True),
    sa.Column('reasoning', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
    sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ),
    sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('evidence', schema=None) as batch_op:
        batch_op.create_index('idx_evidence_project_dimension', ['project_id', 'dimension'], unique=False)
        batch_op.create_index(batch_op.f('ix_evidence_company_id'), ['company_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_evidence_project_id'), ['project_id'], unique=False)



def downgrade() -> None:
    with op.batch_alter_table('evidence', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_evidence_project_id'))
        batch_op.drop_index(batch_op.f('ix_evidence_company_id'))
        batch_op.drop_index('idx_evidence_project_dimension')

    op.drop_table('evidence')
