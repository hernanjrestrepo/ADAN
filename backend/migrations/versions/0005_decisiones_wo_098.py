"""Decisión de ADÁN completa (WO-098): AD-CMP-03 y AD-FUNC-02 §2.5

- options: opciones con fundamento, nivel de evidencia y Confidence Level.
- recommended_option / chosen_option.
- divergence: los 6 campos cuando el cliente decide distinto a lo recomendado.
- prior_decisions: la consulta previa (decisiones ya aprobadas o ejecutadas).
- presented_at, decided_at, executed_at: cuándo se dio cada paso del Patrón A.

Revision ID: 0005
Revises: 0004
Create Date: 2026-10-02 00:51:55.924137
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '0005'
down_revision: Union[str, None] = '0004'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('decisions', schema=None) as batch_op:
        batch_op.add_column(sa.Column('options', sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql'), nullable=True))
        batch_op.add_column(sa.Column('recommended_option', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('chosen_option', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('divergence', sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql'), nullable=True))
        batch_op.add_column(sa.Column('prior_decisions', sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql'), nullable=True))
        batch_op.add_column(sa.Column('presented_at', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('decided_at', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('executed_at', sa.DateTime(), nullable=True))



def downgrade() -> None:
    with op.batch_alter_table('decisions', schema=None) as batch_op:
        batch_op.drop_column('executed_at')
        batch_op.drop_column('decided_at')
        batch_op.drop_column('presented_at')
        batch_op.drop_column('prior_decisions')
        batch_op.drop_column('divergence')
        batch_op.drop_column('chosen_option')
        batch_op.drop_column('recommended_option')
        batch_op.drop_column('options')

