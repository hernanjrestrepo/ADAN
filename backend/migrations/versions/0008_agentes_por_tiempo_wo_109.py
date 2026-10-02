"""WO-109: agentes por tiempo (catálogo, contratos y registro de trabajo append-only).

Revision ID: 0008
Revises: 0007
Create Date: 2026-10-02 14:45:24.224885
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '0008'
down_revision: Union[str, None] = '0007'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('hire_offerings',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('code', sa.String(length=50), nullable=False),
    sa.Column('name', sa.String(length=120), nullable=False),
    sa.Column('role', sa.String(length=120), nullable=False),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('skills', sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql'), nullable=False),
    sa.Column('tools', sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql'), nullable=False),
    sa.Column('tier', sa.String(length=20), nullable=False),
    sa.Column('system_prompt', sa.Text(), nullable=False),
    sa.Column('active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('code')
    )
    op.create_table('hire_contracts',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('company_id', sa.String(length=36), nullable=False),
    sa.Column('offering_id', sa.String(length=36), nullable=False),
    sa.Column('period', sa.String(length=10), nullable=False),
    sa.Column('units', sa.Integer(), nullable=False),
    sa.Column('hours_capacity', sa.Float(), nullable=False),
    sa.Column('starts_at', sa.DateTime(), nullable=False),
    sa.Column('ends_at', sa.DateTime(), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('hired_by', sa.String(length=36), nullable=False),
    sa.Column('price_note', sa.String(length=200), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('cancelled_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
    sa.ForeignKeyConstraint(['hired_by'], ['users.id'], ),
    sa.ForeignKeyConstraint(['offering_id'], ['hire_offerings.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('hire_contracts', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_hire_contracts_company_id'), ['company_id'], unique=False)

    op.create_table('hire_work_logs',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('contract_id', sa.String(length=36), nullable=False),
    sa.Column('work_order_id', sa.String(length=36), nullable=False),
    sa.Column('started_at', sa.DateTime(), nullable=False),
    sa.Column('seconds', sa.Float(), nullable=False),
    sa.Column('prompt_tokens', sa.Integer(), nullable=False),
    sa.Column('completion_tokens', sa.Integer(), nullable=False),
    sa.Column('cost_usd', sa.Float(), nullable=False),
    sa.Column('model', sa.String(length=120), nullable=True),
    sa.Column('degraded', sa.Boolean(), nullable=False),
    sa.Column('tools_used', sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql'), nullable=False),
    sa.Column('outcome', sa.String(length=20), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['contract_id'], ['hire_contracts.id'], ),
    sa.ForeignKeyConstraint(['work_order_id'], ['oos_work_orders.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('hire_work_logs', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_hire_work_logs_contract_id'), ['contract_id'], unique=False)


    _append_only('hire_work_logs')


def downgrade() -> None:
    _drop_append_only('hire_work_logs')
    with op.batch_alter_table('hire_work_logs', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_hire_work_logs_contract_id'))

    op.drop_table('hire_work_logs')
    with op.batch_alter_table('hire_contracts', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_hire_contracts_company_id'))

    op.drop_table('hire_contracts')
    op.drop_table('hire_offerings')


def _append_only(table: str) -> None:
    if op.get_bind().dialect.name == "postgresql":  # la función adan_append_only() la crea 0004
        op.execute(f"CREATE TRIGGER trg_{table}_append_only BEFORE UPDATE OR DELETE ON {table} "
                   f"FOR EACH ROW EXECUTE FUNCTION adan_append_only()")
    else:
        for op_name in ("UPDATE", "DELETE"):
            op.execute(f"CREATE TRIGGER trg_{table}_no_{op_name.lower()} BEFORE {op_name} ON {table} "
                       f"BEGIN SELECT RAISE(ABORT, 'append-only: {table} no admite {op_name}'); END")


def _drop_append_only(table: str) -> None:
    if op.get_bind().dialect.name == "postgresql":
        op.execute(f"DROP TRIGGER IF EXISTS trg_{table}_append_only ON {table}")
    else:
        for op_name in ("update", "delete"):
            op.execute(f"DROP TRIGGER IF EXISTS trg_{table}_no_{op_name}")
