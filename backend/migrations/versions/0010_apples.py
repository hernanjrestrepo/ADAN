"""@pples: billetera, compras, Niveles pagados y red de referidos; identidad visual de cada empresa.

Revision ID: 0010
Revises: 0009
Create Date: 2026-10-24 18:00:00
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '0010'
down_revision: Union[str, None] = '0009'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('apple_referrals',
    sa.Column('user_id', sa.String(length=36), nullable=False),
    sa.Column('code', sa.String(length=8), nullable=False),
    sa.Column('sponsor_id', sa.String(length=36), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['sponsor_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('user_id')
    )
    op.create_index(op.f('ix_apple_referrals_code'), 'apple_referrals', ['code'], unique=True)
    op.create_index(op.f('ix_apple_referrals_sponsor_id'), 'apple_referrals', ['sponsor_id'], unique=False)
    op.create_table('apple_movements',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('user_id', sa.String(length=36), nullable=False),
    sa.Column('kind', sa.String(length=12), nullable=False),
    sa.Column('amount', sa.Numeric(precision=14, scale=3), nullable=False),
    sa.Column('reference', sa.String(length=80), nullable=False),
    sa.Column('company_id', sa.String(length=36), nullable=True),
    sa.Column('level_number', sa.Integer(), nullable=True),
    sa.Column('depth', sa.Integer(), nullable=True),
    sa.Column('source_user_id', sa.String(length=36), nullable=True),
    sa.Column('detail', sa.String(length=200), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
    sa.ForeignKeyConstraint(['source_user_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('kind', 'reference', 'user_id', name='uq_apple_movement_once')
    )
    op.create_index('idx_apple_movements_user', 'apple_movements', ['user_id', 'created_at'], unique=False)
    op.create_table('apple_purchases',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('user_id', sa.String(length=36), nullable=False),
    sa.Column('apples', sa.Integer(), nullable=False),
    sa.Column('amount_cop', sa.Integer(), nullable=False),
    sa.Column('trm', sa.Integer(), nullable=False),
    sa.Column('provider', sa.String(length=20), nullable=False),
    sa.Column('external_id', sa.String(length=80), nullable=True),
    sa.Column('status', sa.String(length=12), nullable=False),
    sa.Column('checkout_url', sa.String(length=1000), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('resolved_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_apple_purchases_user_id'), 'apple_purchases', ['user_id'], unique=False)
    op.create_table('apple_level_unlocks',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('company_id', sa.String(length=36), nullable=False),
    sa.Column('level_number', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.String(length=36), nullable=False),
    sa.Column('apples', sa.Numeric(precision=14, scale=3), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('company_id', 'level_number', name='uq_apple_level_unlock')
    )
    with op.batch_alter_table('companies') as batch:
        batch.add_column(sa.Column('brand_color', sa.String(length=9), nullable=True))
        batch.add_column(sa.Column('brand_accent', sa.String(length=9), nullable=True))
        batch.add_column(sa.Column('logo', sa.Text(), nullable=True))
        batch.add_column(sa.Column('origin_stage', sa.String(length=12), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table('companies') as batch:
        batch.drop_column('origin_stage')
        batch.drop_column('logo')
        batch.drop_column('brand_accent')
        batch.drop_column('brand_color')
    op.drop_table('apple_level_unlocks')
    op.drop_index(op.f('ix_apple_purchases_user_id'), table_name='apple_purchases')
    op.drop_table('apple_purchases')
    op.drop_index('idx_apple_movements_user', table_name='apple_movements')
    op.drop_table('apple_movements')
    op.drop_index(op.f('ix_apple_referrals_sponsor_id'), table_name='apple_referrals')
    op.drop_index(op.f('ix_apple_referrals_code'), table_name='apple_referrals')
    op.drop_table('apple_referrals')
