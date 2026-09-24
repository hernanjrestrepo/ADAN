"""esquema inicial de Build C (WO-091)

Las 33 tablas del núcleo, EMS y OOS, en una sola base declarativa, más los embeddings
del EMS (pgvector en PostgreSQL, JSON en SQLite).

Revision ID: 0001
Revises: 
Create Date: 2026-09-24 22:30:33.235175
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import pgvector.sqlalchemy
from sqlalchemy.dialects import postgresql

revision: str = '0001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    is_postgres = op.get_bind().dialect.name == "postgresql"
    if is_postgres:
        op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.create_table('ems_documents',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('company_id', sa.String(length=36), nullable=False),
    sa.Column('title', sa.String(length=500), nullable=False),
    sa.Column('source_type', sa.String(length=50), nullable=False),
    sa.Column('source_name', sa.String(length=500), nullable=True),
    sa.Column('source_url', sa.String(length=2000), nullable=True),
    sa.Column('content', sa.Text(), nullable=True),
    sa.Column('content_type', sa.String(length=100), nullable=True),
    sa.Column('language', sa.String(length=10), nullable=True),
    sa.Column('status', sa.String(length=20), nullable=True),
    sa.Column('version', sa.Integer(), nullable=True),
    sa.Column('is_latest', sa.Boolean(), nullable=True),
    sa.Column('parent_version_id', sa.String(length=36), nullable=True),
    sa.Column('confidence', sa.Float(), nullable=True),
    sa.Column('metadata_json', sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql'), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('processed_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_ems_doc_company', 'ems_documents', ['company_id'], unique=False)
    op.create_index('idx_ems_doc_source', 'ems_documents', ['source_type'], unique=False)
    op.create_index('idx_ems_doc_status', 'ems_documents', ['status'], unique=False)
    op.create_index(op.f('ix_ems_documents_company_id'), 'ems_documents', ['company_id'], unique=False)
    op.create_table('ems_facts',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('company_id', sa.String(length=36), nullable=False),
    sa.Column('document_id', sa.String(length=36), nullable=True),
    sa.Column('chunk_id', sa.String(length=36), nullable=True),
    sa.Column('fact_type', sa.String(length=50), nullable=False),
    sa.Column('subject', sa.String(length=500), nullable=False),
    sa.Column('predicate', sa.String(length=200), nullable=True),
    sa.Column('object_value', sa.Text(), nullable=True),
    sa.Column('confidence', sa.Float(), nullable=True),
    sa.Column('source', sa.String(length=500), nullable=True),
    sa.Column('metadata_json', sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql'), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('superseded_by', sa.String(length=36), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_ems_fact_company', 'ems_facts', ['company_id'], unique=False)
    op.create_index('idx_ems_fact_subject', 'ems_facts', ['subject'], unique=False)
    op.create_index('idx_ems_fact_type', 'ems_facts', ['fact_type'], unique=False)
    op.create_index(op.f('ix_ems_facts_company_id'), 'ems_facts', ['company_id'], unique=False)
    op.create_table('oos_organizations',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('company_id', sa.String(length=36), nullable=False),
    sa.Column('name', sa.String(length=200), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('industry', sa.String(length=100), nullable=True),
    sa.Column('country', sa.String(length=100), nullable=True),
    sa.Column('maturity_level', sa.Float(), nullable=True),
    sa.Column('status', sa.String(length=20), nullable=True),
    sa.Column('metadata_json', sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql'), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('created_by', sa.String(length=36), nullable=True),
    sa.Column('version', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_oos_organizations_company_id'), 'oos_organizations', ['company_id'], unique=False)
    op.create_table('users',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('hashed_password', sa.String(length=255), nullable=False),
    sa.Column('role', sa.Enum('USER', 'PRIMARY_USER', name='userrole', native_enum=False, length=50), nullable=False),
    sa.Column('status', sa.Enum('ACTIVE', 'ARCHIVED', name='entitystatus', native_enum=False, length=50), nullable=False),
    sa.Column('version', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('created_by', sa.String(length=36), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_table('companies',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('industry', sa.String(length=255), nullable=True),
    sa.Column('country', sa.String(length=100), nullable=True),
    sa.Column('legal_structure', sa.String(length=100), nullable=True),
    sa.Column('founding_narrative', sa.Text(), nullable=True),
    sa.Column('maturity', sa.Float(), nullable=False),
    sa.Column('status', sa.Enum('ACTIVE', 'ARCHIVED', name='entitystatus', native_enum=False, length=50), nullable=False),
    sa.Column('version', sa.Integer(), nullable=False),
    sa.Column('confidence_level', sa.Float(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('created_by', sa.String(length=36), nullable=False),
    sa.Column('primary_user_id', sa.String(length=36), nullable=False),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
    sa.ForeignKeyConstraint(['primary_user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('ems_chunks',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('document_id', sa.String(length=36), nullable=False),
    sa.Column('company_id', sa.String(length=36), nullable=False),
    sa.Column('chunk_index', sa.Integer(), nullable=False),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('content_hash', sa.String(length=64), nullable=True),
    sa.Column('token_count', sa.Integer(), nullable=True),
    sa.Column('metadata_json', sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql'), nullable=True),
    sa.Column('embedding_id', sa.String(length=36), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['document_id'], ['ems_documents.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_ems_chunk_company', 'ems_chunks', ['company_id'], unique=False)
    op.create_index('idx_ems_chunk_doc', 'ems_chunks', ['document_id'], unique=False)
    op.create_index(op.f('ix_ems_chunks_company_id'), 'ems_chunks', ['company_id'], unique=False)
    op.create_table('ems_corrections',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('company_id', sa.String(length=36), nullable=False),
    sa.Column('fact_id', sa.String(length=36), nullable=True),
    sa.Column('chunk_id', sa.String(length=36), nullable=True),
    sa.Column('original_text', sa.Text(), nullable=False),
    sa.Column('corrected_text', sa.Text(), nullable=False),
    sa.Column('reason', sa.Text(), nullable=True),
    sa.Column('confidence_adjustment', sa.Float(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('created_by', sa.String(length=36), nullable=True),
    sa.ForeignKeyConstraint(['fact_id'], ['ems_facts.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ems_corrections_company_id'), 'ems_corrections', ['company_id'], unique=False)
    op.create_table('ems_versions',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('document_id', sa.String(length=36), nullable=False),
    sa.Column('version_number', sa.Integer(), nullable=False),
    sa.Column('content_hash', sa.String(length=64), nullable=True),
    sa.Column('change_summary', sa.Text(), nullable=True),
    sa.Column('confidence', sa.Float(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('created_by', sa.String(length=36), nullable=True),
    sa.ForeignKeyConstraint(['document_id'], ['ems_documents.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('oos_business_units',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('organization_id', sa.String(length=36), nullable=False),
    sa.Column('name', sa.String(length=200), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('head_id', sa.String(length=36), nullable=True),
    sa.Column('status', sa.String(length=20), nullable=True),
    sa.Column('metadata_json', sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql'), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['organization_id'], ['oos_organizations.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('oos_decisions',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('organization_id', sa.String(length=36), nullable=False),
    sa.Column('topic', sa.String(length=500), nullable=False),
    sa.Column('participants', sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql'), nullable=True),
    sa.Column('votes', sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql'), nullable=True),
    sa.Column('deliberation_summary', sa.Text(), nullable=True),
    sa.Column('final_decision', sa.String(length=20), nullable=False),
    sa.Column('final_score', sa.Float(), nullable=True),
    sa.Column('final_confidence', sa.Float(), nullable=True),
    sa.Column('key_objections', sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql'), nullable=True),
    sa.Column('key_agreements', sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql'), nullable=True),
    sa.Column('dissent_details', sa.Text(), nullable=True),
    sa.Column('actions', sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql'), nullable=True),
    sa.Column('follow_up', sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql'), nullable=True),
    sa.Column('status', sa.String(length=20), nullable=True),
    sa.Column('metadata_json', sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql'), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('version', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['organization_id'], ['oos_organizations.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('oos_meetings',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('organization_id', sa.String(length=36), nullable=False),
    sa.Column('title', sa.String(length=500), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('meeting_type', sa.String(length=50), nullable=True),
    sa.Column('participants', sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql'), nullable=True),
    sa.Column('status', sa.String(length=20), nullable=True),
    sa.Column('scheduled_at', sa.DateTime(), nullable=True),
    sa.Column('started_at', sa.DateTime(), nullable=True),
    sa.Column('completed_at', sa.DateTime(), nullable=True),
    sa.Column('agenda', sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql'), nullable=True),
    sa.Column('decisions', sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql'), nullable=True),
    sa.Column('action_items', sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql'), nullable=True),
    sa.Column('metadata_json', sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql'), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['organization_id'], ['oos_organizations.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('oos_objectives',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('organization_id', sa.String(length=36), nullable=False),
    sa.Column('title', sa.String(length=500), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('type', sa.String(length=50), nullable=True),
    sa.Column('priority', sa.String(length=20), nullable=True),
    sa.Column('status', sa.String(length=20), nullable=True),
    sa.Column('target_date', sa.DateTime(), nullable=True),
    sa.Column('owner_id', sa.String(length=36), nullable=True),
    sa.Column('progress', sa.Float(), nullable=True),
    sa.Column('metadata_json', sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql'), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('version', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['organization_id'], ['oos_organizations.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('oos_risks',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('organization_id', sa.String(length=36), nullable=False),
    sa.Column('decision_id', sa.String(length=36), nullable=True),
    sa.Column('title', sa.String(length=500), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('category', sa.String(length=50), nullable=True),
    sa.Column('probability', sa.String(length=20), nullable=True),
    sa.Column('impact', sa.String(length=20), nullable=True),
    sa.Column('severity', sa.Float(), nullable=True),
    sa.Column('status', sa.String(length=20), nullable=True),
    sa.Column('mitigation', sa.Text(), nullable=True),
    sa.Column('owner_id', sa.String(length=36), nullable=True),
    sa.Column('owner_name', sa.String(length=200), nullable=True),
    sa.Column('metadata_json', sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql'), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['organization_id'], ['oos_organizations.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('ems_chunk_embeddings',
    sa.Column('chunk_id', sa.String(length=36), nullable=False),
    sa.Column('document_id', sa.String(length=36), nullable=False),
    sa.Column('company_id', sa.String(length=36), nullable=False),
    sa.Column('embedding', pgvector.sqlalchemy.vector.VECTOR(dim=768).with_variant(sa.JSON(), 'sqlite'), nullable=False),
    sa.Column('embedding_model', sa.String(length=100), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['chunk_id'], ['ems_chunks.id'], ),
    sa.ForeignKeyConstraint(['document_id'], ['ems_documents.id'], ),
    sa.PrimaryKeyConstraint('chunk_id')
    )
    op.create_index('idx_ems_embedding_company', 'ems_chunk_embeddings', ['company_id'], unique=False)
    op.create_index('idx_ems_embedding_document', 'ems_chunk_embeddings', ['document_id'], unique=False)
    if is_postgres:
        op.create_index('idx_ems_embedding_hnsw', 'ems_chunk_embeddings', ['embedding'], unique=False,
                        postgresql_using='hnsw', postgresql_ops={'embedding': 'vector_cosine_ops'})
    op.create_table('founding_narratives',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('company_id', sa.String(length=36), nullable=False),
    sa.Column('origin_story', sa.Text(), nullable=True),
    sa.Column('founding_motivation', sa.Text(), nullable=True),
    sa.Column('irreversible_commitment', sa.Text(), nullable=True),
    sa.Column('status', sa.Enum('ACTIVE', 'ARCHIVED', name='entitystatus', native_enum=False, length=50), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('company_id')
    )
    op.create_table('oos_departments',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('organization_id', sa.String(length=36), nullable=False),
    sa.Column('business_unit_id', sa.String(length=36), nullable=True),
    sa.Column('name', sa.String(length=200), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('head_id', sa.String(length=36), nullable=True),
    sa.Column('status', sa.String(length=20), nullable=True),
    sa.Column('metadata_json', sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql'), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['business_unit_id'], ['oos_business_units.id'], ),
    sa.ForeignKeyConstraint(['organization_id'], ['oos_organizations.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('oos_initiatives',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('objective_id', sa.String(length=36), nullable=False),
    sa.Column('title', sa.String(length=500), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('status', sa.String(length=20), nullable=True),
    sa.Column('owner_id', sa.String(length=36), nullable=True),
    sa.Column('start_date', sa.DateTime(), nullable=True),
    sa.Column('end_date', sa.DateTime(), nullable=True),
    sa.Column('progress', sa.Float(), nullable=True),
    sa.Column('metadata_json', sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql'), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['objective_id'], ['oos_objectives.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('oos_kpis',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('organization_id', sa.String(length=36), nullable=False),
    sa.Column('objective_id', sa.String(length=36), nullable=True),
    sa.Column('name', sa.String(length=200), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('category', sa.String(length=50), nullable=True),
    sa.Column('metric_type', sa.String(length=20), nullable=True),
    sa.Column('current_value', sa.Float(), nullable=True),
    sa.Column('target_value', sa.Float(), nullable=True),
    sa.Column('unit', sa.String(length=50), nullable=True),
    sa.Column('direction', sa.String(length=20), nullable=True),
    sa.Column('status', sa.String(length=20), nullable=True),
    sa.Column('history', sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql'), nullable=True),
    sa.Column('metadata_json', sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql'), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['objective_id'], ['oos_objectives.id'], ),
    sa.ForeignKeyConstraint(['organization_id'], ['oos_organizations.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('oos_meeting_minutes',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('meeting_id', sa.String(length=36), nullable=False),
    sa.Column('topic', sa.String(length=500), nullable=False),
    sa.Column('discussion', sa.Text(), nullable=True),
    sa.Column('decision', sa.Text(), nullable=True),
    sa.Column('action_item', sa.Text(), nullable=True),
    sa.Column('owner', sa.String(length=200), nullable=True),
    sa.Column('due_date', sa.DateTime(), nullable=True),
    sa.Column('metadata_json', sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql'), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['meeting_id'], ['oos_meetings.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('oos_work_orders',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('organization_id', sa.String(length=36), nullable=False),
    sa.Column('decision_id', sa.String(length=36), nullable=True),
    sa.Column('title', sa.String(length=500), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('priority', sa.String(length=20), nullable=True),
    sa.Column('status', sa.String(length=20), nullable=True),
    sa.Column('assigned_to', sa.String(length=36), nullable=True),
    sa.Column('assigned_to_name', sa.String(length=200), nullable=True),
    sa.Column('due_date', sa.DateTime(), nullable=True),
    sa.Column('started_at', sa.DateTime(), nullable=True),
    sa.Column('completed_at', sa.DateTime(), nullable=True),
    sa.Column('progress', sa.Float(), nullable=True),
    sa.Column('dependencies', sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql'), nullable=True),
    sa.Column('blocking_reason', sa.Text(), nullable=True),
    sa.Column('result', sa.Text(), nullable=True),
    sa.Column('metadata_json', sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql'), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('version', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['decision_id'], ['oos_decisions.id'], ),
    sa.ForeignKeyConstraint(['organization_id'], ['oos_organizations.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('projects',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('company_id', sa.String(length=36), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('status', sa.Enum('ACTIVE', 'ARCHIVED', name='entitystatus', native_enum=False, length=50), nullable=False),
    sa.Column('version', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('decisions',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('project_id', sa.String(length=36), nullable=False),
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('proposed_by', sa.String(length=100), nullable=True),
    sa.Column('approved_by', sa.String(length=36), nullable=True),
    sa.Column('status', sa.Enum('PROPOSED', 'APPROVED', 'REJECTED', 'EXECUTED', name='decisionstatus', native_enum=False, length=50), nullable=False),
    sa.Column('reasoning', sa.Text(), nullable=True),
    sa.Column('disagreement', sa.Text(), nullable=True),
    sa.Column('confidence_level', sa.Float(), nullable=True),
    sa.Column('version', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['approved_by'], ['users.id'], ),
    sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('documents',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('project_id', sa.String(length=36), nullable=False),
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('content', sa.Text(), nullable=True),
    sa.Column('doc_type', sa.String(length=100), nullable=False),
    sa.Column('origin', sa.String(length=100), nullable=False),
    sa.Column('version', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('events',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('project_id', sa.String(length=36), nullable=False),
    sa.Column('event_type', sa.String(length=100), nullable=False),
    sa.Column('entity_type', sa.String(length=100), nullable=False),
    sa.Column('entity_id', sa.String(length=36), nullable=False),
    sa.Column('data', sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql'), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('levels',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('project_id', sa.String(length=36), nullable=False),
    sa.Column('number', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('status', sa.Enum('BLOCKED', 'ACTIVE', 'COMPLETED', name='nivelstatus', native_enum=False, length=50), nullable=False),
    sa.Column('completed_at', sa.DateTime(), nullable=True),
    sa.Column('version', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('project_id', 'number')
    )
    op.create_table('oos_assignments',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('work_order_id', sa.String(length=36), nullable=False),
    sa.Column('assigned_to', sa.String(length=36), nullable=False),
    sa.Column('assigned_to_name', sa.String(length=200), nullable=False),
    sa.Column('assigned_to_type', sa.String(length=50), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=True),
    sa.Column('accepted_at', sa.DateTime(), nullable=True),
    sa.Column('completed_at', sa.DateTime(), nullable=True),
    sa.Column('metadata_json', sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql'), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['work_order_id'], ['oos_work_orders.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('oos_progress_reports',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('work_order_id', sa.String(length=36), nullable=False),
    sa.Column('reporter_id', sa.String(length=36), nullable=False),
    sa.Column('reporter_name', sa.String(length=200), nullable=False),
    sa.Column('progress', sa.Float(), nullable=True),
    sa.Column('status_update', sa.String(length=200), nullable=True),
    sa.Column('problems', sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql'), nullable=True),
    sa.Column('evidence', sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql'), nullable=True),
    sa.Column('next_steps', sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql'), nullable=True),
    sa.Column('metadata_json', sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql'), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['work_order_id'], ['oos_work_orders.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('oos_roles',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('department_id', sa.String(length=36), nullable=False),
    sa.Column('name', sa.String(length=200), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('level', sa.Integer(), nullable=True),
    sa.Column('agent_type', sa.String(length=50), nullable=True),
    sa.Column('permissions', sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql'), nullable=True),
    sa.Column('status', sa.String(length=20), nullable=True),
    sa.Column('metadata_json', sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql'), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['department_id'], ['oos_departments.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('oos_tasks',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('work_order_id', sa.String(length=36), nullable=False),
    sa.Column('title', sa.String(length=500), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('status', sa.String(length=20), nullable=True),
    sa.Column('assigned_to', sa.String(length=36), nullable=True),
    sa.Column('assigned_to_name', sa.String(length=200), nullable=True),
    sa.Column('due_date', sa.DateTime(), nullable=True),
    sa.Column('completed_at', sa.DateTime(), nullable=True),
    sa.Column('result', sa.Text(), nullable=True),
    sa.Column('metadata_json', sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql'), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['work_order_id'], ['oos_work_orders.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('scores',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('project_id', sa.String(length=36), nullable=False),
    sa.Column('score_type', sa.Enum('PROBLEM', 'SOLUTION', 'BUSINESS', 'PRODUCT', 'MARKET', 'EXECUTION', name='scoretype', native_enum=False, length=50), nullable=False),
    sa.Column('value', sa.Float(), nullable=False),
    sa.Column('confidence_level', sa.Float(), nullable=False),
    sa.Column('reasoning', sa.Text(), nullable=True),
    sa.Column('evidence', sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql'), nullable=True),
    sa.Column('version', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('cards',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('project_id', sa.String(length=36), nullable=False),
    sa.Column('level_id', sa.String(length=36), nullable=False),
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('card_type', sa.String(length=100), nullable=False),
    sa.Column('status', sa.Enum('BLOCKED', 'ACTIVE', 'COMPLETED', name='cardstatus', native_enum=False, length=50), nullable=False),
    sa.Column('version', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['level_id'], ['levels.id'], ),
    sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('conversations',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('card_id', sa.String(length=36), nullable=False),
    sa.Column('title', sa.String(length=255), nullable=True),
    sa.Column('status', sa.Enum('ACTIVE', 'ARCHIVED', name='entitystatus', native_enum=False, length=50), nullable=False),
    sa.Column('summary', sa.Text(), nullable=True),
    sa.Column('version', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['card_id'], ['cards.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('messages',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('conversation_id', sa.String(length=36), nullable=False),
    sa.Column('role', sa.String(length=50), nullable=False),
    sa.Column('agent_name', sa.String(length=100), nullable=True),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('metadata_json', sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql'), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('messages')
    op.drop_table('conversations')
    op.drop_table('cards')
    op.drop_table('scores')
    op.drop_table('oos_tasks')
    op.drop_table('oos_roles')
    op.drop_table('oos_progress_reports')
    op.drop_table('oos_assignments')
    op.drop_table('levels')
    op.drop_table('events')
    op.drop_table('documents')
    op.drop_table('decisions')
    op.drop_table('projects')
    op.drop_table('oos_work_orders')
    op.drop_table('oos_meeting_minutes')
    op.drop_table('oos_kpis')
    op.drop_table('oos_initiatives')
    op.drop_table('oos_departments')
    op.drop_table('founding_narratives')
    op.drop_index('idx_ems_embedding_document', table_name='ems_chunk_embeddings')
    op.drop_index('idx_ems_embedding_company', table_name='ems_chunk_embeddings')
    op.drop_table('ems_chunk_embeddings')
    op.drop_table('oos_risks')
    op.drop_table('oos_objectives')
    op.drop_table('oos_meetings')
    op.drop_table('oos_decisions')
    op.drop_table('oos_business_units')
    op.drop_table('ems_versions')
    op.drop_index(op.f('ix_ems_corrections_company_id'), table_name='ems_corrections')
    op.drop_table('ems_corrections')
    op.drop_index(op.f('ix_ems_chunks_company_id'), table_name='ems_chunks')
    op.drop_index('idx_ems_chunk_doc', table_name='ems_chunks')
    op.drop_index('idx_ems_chunk_company', table_name='ems_chunks')
    op.drop_table('ems_chunks')
    op.drop_table('companies')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    op.drop_index(op.f('ix_oos_organizations_company_id'), table_name='oos_organizations')
    op.drop_table('oos_organizations')
    op.drop_index(op.f('ix_ems_facts_company_id'), table_name='ems_facts')
    op.drop_index('idx_ems_fact_type', table_name='ems_facts')
    op.drop_index('idx_ems_fact_subject', table_name='ems_facts')
    op.drop_index('idx_ems_fact_company', table_name='ems_facts')
    op.drop_table('ems_facts')
    op.drop_index(op.f('ix_ems_documents_company_id'), table_name='ems_documents')
    op.drop_index('idx_ems_doc_status', table_name='ems_documents')
    op.drop_index('idx_ems_doc_source', table_name='ems_documents')
    op.drop_index('idx_ems_doc_company', table_name='ems_documents')
    op.drop_table('ems_documents')
