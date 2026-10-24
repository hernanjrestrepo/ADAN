"""Comunidad: perfiles, vitrina de empresas con Sello ADÁN y conexiones.

Revision ID: 0009
Revises: 0008
Create Date: 2026-10-24 12:00:00
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '0009'
down_revision: Union[str, None] = '0008'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

JSON = sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql')


def upgrade() -> None:
    op.create_table('community_profiles',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('user_id', sa.String(length=36), nullable=False),
    sa.Column('display_name', sa.String(length=120), nullable=False),
    sa.Column('headline', sa.String(length=200), nullable=False),
    sa.Column('bio', sa.Text(), nullable=False),
    sa.Column('kind', sa.String(length=20), nullable=False),
    sa.Column('city', sa.String(length=80), nullable=False),
    sa.Column('country', sa.String(length=80), nullable=False),
    sa.Column('website', sa.String(length=300), nullable=False),
    sa.Column('linkedin', sa.String(length=300), nullable=False),
    sa.Column('public', sa.Boolean(), nullable=False),
    sa.Column('ticket_min_usd', sa.Float(), nullable=True),
    sa.Column('ticket_max_usd', sa.Float(), nullable=True),
    sa.Column('sectors', JSON, nullable=False),
    sa.Column('stages', JSON, nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('community_profiles', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_community_profiles_user_id'), ['user_id'], unique=True)

    op.create_table('community_listings',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('company_id', sa.String(length=36), nullable=False),
    sa.Column('owner_id', sa.String(length=36), nullable=False),
    sa.Column('published', sa.Boolean(), nullable=False),
    sa.Column('name', sa.String(length=160), nullable=False),
    sa.Column('tagline', sa.String(length=200), nullable=False),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('sector', sa.String(length=120), nullable=False),
    sa.Column('country', sa.String(length=80), nullable=False),
    sa.Column('city', sa.String(length=80), nullable=False),
    sa.Column('stage', sa.String(length=20), nullable=False),
    sa.Column('looking_for', JSON, nullable=False),
    sa.Column('amount_sought_usd', sa.Float(), nullable=True),
    sa.Column('website', sa.String(length=300), nullable=False),
    sa.Column('seal', JSON, nullable=False),
    sa.Column('paradixe_selection', sa.Boolean(), nullable=False),
    sa.Column('selection_note', sa.Text(), nullable=False),
    sa.Column('selected_by', sa.String(length=36), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
    sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('community_listings', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_community_listings_company_id'), ['company_id'], unique=True)
        batch_op.create_index(batch_op.f('ix_community_listings_owner_id'), ['owner_id'], unique=False)

    op.create_table('community_connections',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('from_user_id', sa.String(length=36), nullable=False),
    sa.Column('to_user_id', sa.String(length=36), nullable=False),
    sa.Column('listing_id', sa.String(length=36), nullable=True),
    sa.Column('kind', sa.String(length=20), nullable=False),
    sa.Column('message', sa.Text(), nullable=False),
    sa.Column('status', sa.String(length=12), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('responded_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['from_user_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['listing_id'], ['community_listings.id'], ),
    sa.ForeignKeyConstraint(['to_user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('community_connections', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_community_connections_from_user_id'), ['from_user_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_community_connections_to_user_id'), ['to_user_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_community_connections_listing_id'), ['listing_id'], unique=False)


def downgrade() -> None:
    op.drop_table('community_connections')
    op.drop_table('community_listings')
    op.drop_table('community_profiles')
