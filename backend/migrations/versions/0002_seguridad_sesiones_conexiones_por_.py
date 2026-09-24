"""seguridad: sesiones, conexiones por empresa y auditoría TEF (WO-097)

- users.token_version: cerrar sesión invalida los tokens emitidos antes.
- integration_connections: credenciales de conectores por empresa, cifradas.
- tef_audit_log: auditoría persistente de herramientas.

Revision ID: 0002
Revises: 0001
Create Date: 2026-09-24 22:48:18.975435
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '0002'
down_revision: Union[str, None] = '0001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('tef_audit_log',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('tool_id', sa.String(length=100), nullable=False),
    sa.Column('status', sa.String(length=30), nullable=False),
    sa.Column('error', sa.Text(), nullable=True),
    sa.Column('company_id', sa.String(length=36), nullable=False),
    sa.Column('user_id', sa.String(length=36), nullable=False),
    sa.Column('trace_id', sa.String(length=100), nullable=False),
    sa.Column('duration_ms', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_tef_audit_company_created', 'tef_audit_log', ['company_id', 'created_at'], unique=False)
    op.create_table('integration_connections',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('company_id', sa.String(length=36), nullable=False),
    sa.Column('connector_id', sa.String(length=50), nullable=False),
    sa.Column('credentials_encrypted', sa.Text(), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('created_by', sa.String(length=36), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('company_id', 'connector_id', name='uq_integration_company_connector')
    )
    op.create_index(op.f('ix_integration_connections_company_id'), 'integration_connections', ['company_id'], unique=False)
    op.add_column('users', sa.Column('token_version', sa.Integer(), server_default='0', nullable=False))


def downgrade() -> None:
    with op.batch_alter_table('users') as batch:  # SQLite no soporta DROP COLUMN directo
        batch.drop_column('token_version')
    op.drop_index(op.f('ix_integration_connections_company_id'), table_name='integration_connections')
    op.drop_table('integration_connections')
    op.drop_index('idx_tef_audit_company_created', table_name='tef_audit_log')
    op.drop_table('tef_audit_log')
