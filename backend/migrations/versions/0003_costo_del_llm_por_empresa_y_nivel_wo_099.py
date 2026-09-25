"""costo del LLM por empresa y Nivel (WO-099)

- llm_usage: una fila por llamada al modelo hecha para una empresa (proveedor, modelo,
  nivel de complejidad, tokens y costo estimado en USD).

Revision ID: 0003
Revises: 0002
Create Date: 2026-09-25 01:10:47.418105
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '0003'
down_revision: Union[str, None] = '0002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('llm_usage',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('company_id', sa.String(length=36), nullable=False),
    sa.Column('level_number', sa.Integer(), nullable=True),
    sa.Column('operation', sa.String(length=50), nullable=False),
    sa.Column('tier', sa.String(length=20), nullable=False),
    sa.Column('provider', sa.String(length=20), nullable=False),
    sa.Column('model', sa.String(length=100), nullable=False),
    sa.Column('input_tokens', sa.Integer(), nullable=False),
    sa.Column('output_tokens', sa.Integer(), nullable=False),
    sa.Column('cost_usd', sa.Float(), nullable=False),
    sa.Column('degraded', sa.String(length=200), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('llm_usage', schema=None) as batch_op:
        batch_op.create_index('idx_llm_usage_company_created', ['company_id', 'created_at'], unique=False)



def downgrade() -> None:
    with op.batch_alter_table('llm_usage', schema=None) as batch_op:
        batch_op.drop_index('idx_llm_usage_company_created')

    op.drop_table('llm_usage')
