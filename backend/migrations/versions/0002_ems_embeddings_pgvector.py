"""WO-091 — vector store persistente del EMS (pgvector en PostgreSQL).

Revision ID: 0002
Revises: 0001
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '0002'
down_revision: Union[str, None] = '0001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    is_pg = op.get_bind().dialect.name == 'postgresql'
    if is_pg:
        from pgvector.sqlalchemy import Vector

        op.execute('CREATE EXTENSION IF NOT EXISTS vector')
        embedding_type = Vector()
    else:
        embedding_type = sa.JSON()

    op.create_table(
        'ems_embeddings',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('company_id', sa.String(length=36), nullable=False),
        sa.Column('document_id', sa.String(length=36), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('metadata_json', sa.JSON(), nullable=True),
        sa.Column('dim', sa.Integer(), nullable=False),
        sa.Column('embedding', embedding_type, nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('idx_ems_emb_company_dim', 'ems_embeddings', ['company_id', 'dim'])
    op.create_index('idx_ems_emb_document', 'ems_embeddings', ['document_id'])


def downgrade() -> None:
    op.drop_index('idx_ems_emb_document', table_name='ems_embeddings')
    op.drop_index('idx_ems_emb_company_dim', table_name='ems_embeddings')
    op.drop_table('ems_embeddings')
