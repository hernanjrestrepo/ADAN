"""WO-108: constancias de consentimiento (Ley 1581) y evidencia externa confirmada y verificada.

`consents` es Registro Permanente: triggers append-only en PostgreSQL y SQLite, como 0004.

Revision ID: 0007
Revises: 0006
Create Date: 2026-10-02 13:44:49.587458
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '0007'
down_revision: Union[str, None] = '0006'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('consents',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('user_id', sa.String(length=36), nullable=False),
    sa.Column('purpose', sa.String(length=40), nullable=False),
    sa.Column('granted', sa.Boolean(), nullable=False),
    sa.Column('policy_version', sa.String(length=20), nullable=False),
    sa.Column('channel', sa.String(length=20), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('consents', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_consents_user_id'), ['user_id'], unique=False)

    with op.batch_alter_table('evidence', schema=None) as batch_op:
        batch_op.add_column(sa.Column('confirmed', sa.Boolean(), server_default=sa.true(), nullable=False))
        batch_op.add_column(sa.Column('verification', sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql'), nullable=True))

    _append_only("consents")



def downgrade() -> None:
    _drop_append_only("consents")
    with op.batch_alter_table('evidence', schema=None) as batch_op:
        batch_op.drop_column('verification')
        batch_op.drop_column('confirmed')

    with op.batch_alter_table('consents', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_consents_user_id'))

    op.drop_table('consents')


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
