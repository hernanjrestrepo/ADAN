"""Gemelo Digital (WO-098): 26 entidades nuevas, Contrato Base, versiones, linaje y eventos

- 23 entidades de negocio de AD-005 y 3 operativas de AD-006 (Workspace, Agente, Tarea),
  Riesgo como propiedad transversal, versiones (entity_versions) y linaje (twin_lineage).
- Contrato Base en las entidades existentes: `updated_by`; versión en founding_narratives.
- Empresa: jurisdicción, fecha de fundación (Edad) e intangibles.
- Score con sujeto polimórfico (AD-006 v1.2); eventos con categoría, empresa y actor.
- Registros permanentes (Patrón C, AD-008): triggers que impiden UPDATE y DELETE en
  events, scores, business_occurrences, entity_versions y twin_lineage.
- Siembra el catálogo de Agentes (los 7 roles del Board y ADÁN).

Revision ID: 0004
Revises: 0003
Create Date: 2026-10-02 00:37:41.298817
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '0004'
down_revision: Union[str, None] = '0003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('agents',
    sa.Column('code', sa.String(length=20), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
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
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('code')
    )
    op.create_table('assets',
    sa.Column('company_id', sa.String(length=36), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('kind', sa.String(length=100), nullable=True),
    sa.Column('value', sa.Float(), nullable=True),
    sa.Column('liquidity', sa.String(length=20), nullable=True),
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
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('assets', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_assets_company_id'), ['company_id'], unique=False)

    op.create_table('brands',
    sa.Column('company_id', sa.String(length=36), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('positioning', sa.Text(), nullable=True),
    sa.Column('reputation', sa.Text(), nullable=True),
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
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('brands', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_brands_company_id'), ['company_id'], unique=False)

    op.create_table('departments',
    sa.Column('company_id', sa.String(length=36), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('function', sa.Text(), nullable=True),
    sa.Column('parent_id', sa.String(length=36), nullable=True),
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
    sa.ForeignKeyConstraint(['parent_id'], ['departments.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('departments', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_departments_company_id'), ['company_id'], unique=False)

    op.create_table('end_customers',
    sa.Column('company_id', sa.String(length=36), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('segment', sa.String(length=255), nullable=True),
    sa.Column('relationship_notes', sa.Text(), nullable=True),
    sa.Column('trust', sa.Text(), nullable=True),
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
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('end_customers', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_end_customers_company_id'), ['company_id'], unique=False)

    op.create_table('entity_versions',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('company_id', sa.String(length=36), nullable=True),
    sa.Column('entity_type', sa.String(length=50), nullable=False),
    sa.Column('entity_id', sa.String(length=36), nullable=False),
    sa.Column('version', sa.Integer(), nullable=False),
    sa.Column('change', sa.String(length=20), nullable=False),
    sa.Column('changes', sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql'), nullable=True),
    sa.Column('snapshot', sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql'), nullable=False),
    sa.Column('actor_type', sa.String(length=10), nullable=False),
    sa.Column('actor_id', sa.String(length=120), nullable=True),
    sa.Column('reason', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('entity_type', 'entity_id', 'version', name='uq_entity_version')
    )
    with op.batch_alter_table('entity_versions', schema=None) as batch_op:
        batch_op.create_index('idx_entity_versions_entity', ['entity_type', 'entity_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_entity_versions_company_id'), ['company_id'], unique=False)

    op.create_table('expenses',
    sa.Column('company_id', sa.String(length=36), nullable=False),
    sa.Column('category', sa.String(length=255), nullable=False),
    sa.Column('amount', sa.Float(), nullable=True),
    sa.Column('periodicity', sa.String(length=50), nullable=True),
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
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('expenses', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_expenses_company_id'), ['company_id'], unique=False)

    op.create_table('functional_roles',
    sa.Column('company_id', sa.String(length=36), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('skills', sa.Text(), nullable=True),
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
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('functional_roles', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_functional_roles_company_id'), ['company_id'], unique=False)

    op.create_table('liabilities',
    sa.Column('company_id', sa.String(length=36), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('kind', sa.String(length=100), nullable=True),
    sa.Column('amount', sa.Float(), nullable=True),
    sa.Column('term', sa.String(length=50), nullable=True),
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
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('liabilities', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_liabilities_company_id'), ['company_id'], unique=False)

    op.create_table('markets',
    sa.Column('company_id', sa.String(length=36), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('segment_definition', sa.Text(), nullable=True),
    sa.Column('size', sa.String(length=100), nullable=True),
    sa.Column('trends', sa.Text(), nullable=True),
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
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('markets', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_markets_company_id'), ['company_id'], unique=False)

    op.create_table('objectives',
    sa.Column('company_id', sa.String(length=36), nullable=False),
    sa.Column('statement', sa.Text(), nullable=False),
    sa.Column('horizon', sa.String(length=50), nullable=True),
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
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('objectives', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_objectives_company_id'), ['company_id'], unique=False)

    op.create_table('processes',
    sa.Column('company_id', sa.String(length=36), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('objective', sa.Text(), nullable=True),
    sa.Column('frequency', sa.String(length=100), nullable=True),
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
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('processes', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_processes_company_id'), ['company_id'], unique=False)

    op.create_table('revenues',
    sa.Column('company_id', sa.String(length=36), nullable=False),
    sa.Column('source', sa.String(length=255), nullable=False),
    sa.Column('amount', sa.Float(), nullable=True),
    sa.Column('periodicity', sa.String(length=50), nullable=True),
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
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('revenues', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_revenues_company_id'), ['company_id'], unique=False)

    op.create_table('shareholders',
    sa.Column('company_id', sa.String(length=36), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('participation_type', sa.String(length=100), nullable=True),
    sa.Column('participation_pct', sa.Float(), nullable=True),
    sa.Column('since', sa.Date(), nullable=True),
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
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('shareholders', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_shareholders_company_id'), ['company_id'], unique=False)

    op.create_table('suppliers',
    sa.Column('company_id', sa.String(length=36), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('supplies', sa.Text(), nullable=True),
    sa.Column('criticality', sa.String(length=20), nullable=True),
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
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('suppliers', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_suppliers_company_id'), ['company_id'], unique=False)

    op.create_table('twin_risks',
    sa.Column('company_id', sa.String(length=36), nullable=False),
    sa.Column('subject_type', sa.String(length=30), nullable=False),
    sa.Column('subject_id', sa.String(length=36), nullable=False),
    sa.Column('kind', sa.String(length=30), nullable=False),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('severity', sa.String(length=10), nullable=True),
    sa.Column('probability', sa.Float(), nullable=True),
    sa.Column('materialized', sa.Boolean(), nullable=False),
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
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('twin_risks', schema=None) as batch_op:
        batch_op.create_index('idx_twin_risks_subject', ['subject_type', 'subject_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_twin_risks_company_id'), ['company_id'], unique=False)

    op.create_table('competitors',
    sa.Column('company_id', sa.String(length=36), nullable=False),
    sa.Column('market_id', sa.String(length=36), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('notes', sa.Text(), nullable=True),
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
    sa.ForeignKeyConstraint(['market_id'], ['markets.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('competitors', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_competitors_company_id'), ['company_id'], unique=False)

    op.create_table('goals',
    sa.Column('company_id', sa.String(length=36), nullable=False),
    sa.Column('objective_id', sa.String(length=36), nullable=False),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('target_value', sa.Float(), nullable=True),
    sa.Column('unit', sa.String(length=50), nullable=True),
    sa.Column('due_on', sa.Date(), nullable=True),
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
    sa.ForeignKeyConstraint(['objective_id'], ['objectives.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('goals', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_goals_company_id'), ['company_id'], unique=False)

    op.create_table('initiatives',
    sa.Column('company_id', sa.String(length=36), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('objective', sa.Text(), nullable=True),
    sa.Column('budget', sa.Float(), nullable=True),
    sa.Column('process_id', sa.String(length=36), nullable=True),
    sa.Column('state', sa.String(length=20), nullable=False),
    sa.Column('spun_off_company_id', sa.String(length=36), nullable=True),
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
    sa.ForeignKeyConstraint(['process_id'], ['processes.id'], ),
    sa.ForeignKeyConstraint(['spun_off_company_id'], ['companies.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('initiatives', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_initiatives_company_id'), ['company_id'], unique=False)

    op.create_table('offerings',
    sa.Column('company_id', sa.String(length=36), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('kind', sa.String(length=20), nullable=True),
    sa.Column('category', sa.String(length=255), nullable=True),
    sa.Column('value_proposition', sa.Text(), nullable=True),
    sa.Column('market_id', sa.String(length=36), nullable=True),
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
    sa.ForeignKeyConstraint(['market_id'], ['markets.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('offerings', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_offerings_company_id'), ['company_id'], unique=False)

    op.create_table('positions',
    sa.Column('company_id', sa.String(length=36), nullable=False),
    sa.Column('department_id', sa.String(length=36), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('hierarchy_level', sa.Integer(), nullable=True),
    sa.Column('reports_to_id', sa.String(length=36), nullable=True),
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
    sa.ForeignKeyConstraint(['department_id'], ['departments.id'], ),
    sa.ForeignKeyConstraint(['reports_to_id'], ['positions.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('positions', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_positions_company_id'), ['company_id'], unique=False)

    op.create_table('workspaces',
    sa.Column('project_id', sa.String(length=36), nullable=False),
    sa.Column('company_id', sa.String(length=36), nullable=False),
    sa.Column('preferences', sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql'), nullable=True),
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
    sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('project_id')
    )
    with op.batch_alter_table('workspaces', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_workspaces_company_id'), ['company_id'], unique=False)

    op.create_table('employees',
    sa.Column('company_id', sa.String(length=36), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('position_id', sa.String(length=36), nullable=True),
    sa.Column('hired_on', sa.Date(), nullable=True),
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
    sa.ForeignKeyConstraint(['position_id'], ['positions.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('employees', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_employees_company_id'), ['company_id'], unique=False)

    op.create_table('indicators',
    sa.Column('company_id', sa.String(length=36), nullable=False),
    sa.Column('goal_id', sa.String(length=36), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('kind', sa.String(length=20), nullable=True),
    sa.Column('formula', sa.Text(), nullable=True),
    sa.Column('frequency', sa.String(length=50), nullable=True),
    sa.Column('current_value', sa.Float(), nullable=True),
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
    sa.ForeignKeyConstraint(['goal_id'], ['goals.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('indicators', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_indicators_company_id'), ['company_id'], unique=False)

    op.create_table('position_roles',
    sa.Column('position_id', sa.String(length=36), nullable=False),
    sa.Column('functional_role_id', sa.String(length=36), nullable=False),
    sa.ForeignKeyConstraint(['functional_role_id'], ['functional_roles.id'], ),
    sa.ForeignKeyConstraint(['position_id'], ['positions.id'], ),
    sa.PrimaryKeyConstraint('position_id', 'functional_role_id')
    )
    op.create_table('twin_lineage',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('company_id', sa.String(length=36), nullable=False),
    sa.Column('source_company_id', sa.String(length=36), nullable=False),
    sa.Column('relation', sa.String(length=20), nullable=False),
    sa.Column('initiative_id', sa.String(length=36), nullable=True),
    sa.Column('note', sa.Text(), nullable=True),
    sa.Column('actor_type', sa.String(length=10), nullable=False),
    sa.Column('actor_id', sa.String(length=120), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
    sa.ForeignKeyConstraint(['initiative_id'], ['initiatives.id'], ),
    sa.ForeignKeyConstraint(['source_company_id'], ['companies.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('twin_lineage', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_twin_lineage_company_id'), ['company_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_twin_lineage_source_company_id'), ['source_company_id'], unique=False)

    op.create_table('business_contracts',
    sa.Column('company_id', sa.String(length=36), nullable=False),
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('counterparty_type', sa.String(length=20), nullable=False),
    sa.Column('supplier_id', sa.String(length=36), nullable=True),
    sa.Column('end_customer_id', sa.String(length=36), nullable=True),
    sa.Column('employee_id', sa.String(length=36), nullable=True),
    sa.Column('counterparty_name', sa.String(length=255), nullable=True),
    sa.Column('valid_from', sa.Date(), nullable=True),
    sa.Column('valid_to', sa.Date(), nullable=True),
    sa.Column('state', sa.String(length=20), nullable=False),
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
    sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ),
    sa.ForeignKeyConstraint(['end_customer_id'], ['end_customers.id'], ),
    sa.ForeignKeyConstraint(['supplier_id'], ['suppliers.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('business_contracts', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_business_contracts_company_id'), ['company_id'], unique=False)

    op.create_table('business_decisions',
    sa.Column('company_id', sa.String(length=36), nullable=False),
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('decided_by_employee_id', sa.String(length=36), nullable=True),
    sa.Column('learning_loop', sa.String(length=10), nullable=True),
    sa.Column('adan_decision_id', sa.String(length=36), nullable=True),
    sa.Column('state', sa.String(length=20), nullable=False),
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
    sa.ForeignKeyConstraint(['adan_decision_id'], ['decisions.id'], ),
    sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
    sa.ForeignKeyConstraint(['decided_by_employee_id'], ['employees.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('business_decisions', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_business_decisions_company_id'), ['company_id'], unique=False)

    op.create_table('tasks',
    sa.Column('company_id', sa.String(length=36), nullable=False),
    sa.Column('project_id', sa.String(length=36), nullable=False),
    sa.Column('level_id', sa.String(length=36), nullable=False),
    sa.Column('card_id', sa.String(length=36), nullable=True),
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('state', sa.String(length=20), nullable=False),
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
    sa.ForeignKeyConstraint(['card_id'], ['cards.id'], ),
    sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
    sa.ForeignKeyConstraint(['level_id'], ['levels.id'], ),
    sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('tasks', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_tasks_company_id'), ['company_id'], unique=False)

    op.create_table('business_occurrences',
    sa.Column('company_id', sa.String(length=36), nullable=False),
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('nature', sa.String(length=20), nullable=False),
    sa.Column('occurred_on', sa.Date(), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('business_decision_id', sa.String(length=36), nullable=True),
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
    sa.ForeignKeyConstraint(['business_decision_id'], ['business_decisions.id'], ),
    sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('business_occurrences', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_business_occurrences_company_id'), ['company_id'], unique=False)

    op.create_table('contract_documents',
    sa.Column('contract_id', sa.String(length=36), nullable=False),
    sa.Column('document_id', sa.String(length=36), nullable=False),
    sa.ForeignKeyConstraint(['contract_id'], ['business_contracts.id'], ),
    sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ),
    sa.PrimaryKeyConstraint('contract_id', 'document_id')
    )
    op.create_table('conversation_agents',
    sa.Column('conversation_id', sa.String(length=36), nullable=False),
    sa.Column('agent_id', sa.String(length=36), nullable=False),
    sa.ForeignKeyConstraint(['agent_id'], ['agents.id'], ),
    sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ),
    sa.PrimaryKeyConstraint('conversation_id', 'agent_id')
    )
    with op.batch_alter_table('cards', schema=None) as batch_op:
        batch_op.add_column(sa.Column('updated_by', sa.String(length=120), nullable=True))

    with op.batch_alter_table('companies', schema=None) as batch_op:
        batch_op.add_column(sa.Column('jurisdiction', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('founded_on', sa.Date(), nullable=True))
        batch_op.add_column(sa.Column('intangibles', sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql'), nullable=True))
        batch_op.add_column(sa.Column('updated_by', sa.String(length=120), nullable=True))

    with op.batch_alter_table('conversations', schema=None) as batch_op:
        batch_op.add_column(sa.Column('updated_by', sa.String(length=120), nullable=True))

    with op.batch_alter_table('decisions', schema=None) as batch_op:
        batch_op.add_column(sa.Column('updated_by', sa.String(length=120), nullable=True))

    with op.batch_alter_table('documents', schema=None) as batch_op:
        batch_op.add_column(sa.Column('updated_by', sa.String(length=120), nullable=True))

    with op.batch_alter_table('events', schema=None) as batch_op:
        batch_op.add_column(sa.Column('category', sa.String(length=20), server_default='domain', nullable=False))
        batch_op.add_column(sa.Column('company_id', sa.String(length=36), nullable=True))
        batch_op.add_column(sa.Column('actor_type', sa.String(length=10), nullable=True))
        batch_op.add_column(sa.Column('actor_id', sa.String(length=120), nullable=True))
        batch_op.alter_column('project_id',
               existing_type=sa.VARCHAR(length=36),
               nullable=True)
        batch_op.create_index(batch_op.f('ix_events_company_id'), ['company_id'], unique=False)
        batch_op.create_foreign_key('fk_events_company_id_companies', 'companies', ['company_id'], ['id'])

    with op.batch_alter_table('founding_narratives', schema=None) as batch_op:
        batch_op.add_column(sa.Column('version', sa.Integer(), server_default='1', nullable=False))
        batch_op.add_column(sa.Column('updated_by', sa.String(length=120), nullable=True))

    with op.batch_alter_table('levels', schema=None) as batch_op:
        batch_op.add_column(sa.Column('updated_by', sa.String(length=120), nullable=True))

    with op.batch_alter_table('projects', schema=None) as batch_op:
        batch_op.add_column(sa.Column('updated_by', sa.String(length=120), nullable=True))

    with op.batch_alter_table('scores', schema=None) as batch_op:
        batch_op.add_column(sa.Column('subject', sa.String(length=20), server_default='company', nullable=False))
        batch_op.add_column(sa.Column('user_id', sa.String(length=36), nullable=True))
        batch_op.create_foreign_key('fk_scores_user_id_users', 'users', ['user_id'], ['id'])

    _seed_agents()
    _create_append_only_triggers()


def downgrade() -> None:
    _drop_append_only_triggers()
    with op.batch_alter_table('scores', schema=None) as batch_op:
        batch_op.drop_constraint('fk_scores_user_id_users', type_='foreignkey')
        batch_op.drop_column('user_id')
        batch_op.drop_column('subject')

    with op.batch_alter_table('projects', schema=None) as batch_op:
        batch_op.drop_column('updated_by')

    with op.batch_alter_table('levels', schema=None) as batch_op:
        batch_op.drop_column('updated_by')

    with op.batch_alter_table('founding_narratives', schema=None) as batch_op:
        batch_op.drop_column('updated_by')
        batch_op.drop_column('version')

    with op.batch_alter_table('events', schema=None) as batch_op:
        batch_op.drop_constraint('fk_events_company_id_companies', type_='foreignkey')
        batch_op.drop_index(batch_op.f('ix_events_company_id'))
        batch_op.alter_column('project_id',
               existing_type=sa.VARCHAR(length=36),
               nullable=False)
        batch_op.drop_column('actor_id')
        batch_op.drop_column('actor_type')
        batch_op.drop_column('company_id')
        batch_op.drop_column('category')

    with op.batch_alter_table('documents', schema=None) as batch_op:
        batch_op.drop_column('updated_by')

    with op.batch_alter_table('decisions', schema=None) as batch_op:
        batch_op.drop_column('updated_by')

    with op.batch_alter_table('conversations', schema=None) as batch_op:
        batch_op.drop_column('updated_by')

    with op.batch_alter_table('companies', schema=None) as batch_op:
        batch_op.drop_column('updated_by')
        batch_op.drop_column('intangibles')
        batch_op.drop_column('founded_on')
        batch_op.drop_column('jurisdiction')

    with op.batch_alter_table('cards', schema=None) as batch_op:
        batch_op.drop_column('updated_by')

    op.drop_table('conversation_agents')
    op.drop_table('contract_documents')
    with op.batch_alter_table('business_occurrences', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_business_occurrences_company_id'))

    op.drop_table('business_occurrences')
    with op.batch_alter_table('tasks', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_tasks_company_id'))

    op.drop_table('tasks')
    with op.batch_alter_table('business_decisions', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_business_decisions_company_id'))

    op.drop_table('business_decisions')
    with op.batch_alter_table('business_contracts', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_business_contracts_company_id'))

    op.drop_table('business_contracts')
    with op.batch_alter_table('twin_lineage', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_twin_lineage_source_company_id'))
        batch_op.drop_index(batch_op.f('ix_twin_lineage_company_id'))

    op.drop_table('twin_lineage')
    op.drop_table('position_roles')
    with op.batch_alter_table('indicators', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_indicators_company_id'))

    op.drop_table('indicators')
    with op.batch_alter_table('employees', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_employees_company_id'))

    op.drop_table('employees')
    with op.batch_alter_table('workspaces', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_workspaces_company_id'))

    op.drop_table('workspaces')
    with op.batch_alter_table('positions', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_positions_company_id'))

    op.drop_table('positions')
    with op.batch_alter_table('offerings', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_offerings_company_id'))

    op.drop_table('offerings')
    with op.batch_alter_table('initiatives', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_initiatives_company_id'))

    op.drop_table('initiatives')
    with op.batch_alter_table('goals', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_goals_company_id'))

    op.drop_table('goals')
    with op.batch_alter_table('competitors', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_competitors_company_id'))

    op.drop_table('competitors')
    with op.batch_alter_table('twin_risks', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_twin_risks_company_id'))
        batch_op.drop_index('idx_twin_risks_subject')

    op.drop_table('twin_risks')
    with op.batch_alter_table('suppliers', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_suppliers_company_id'))

    op.drop_table('suppliers')
    with op.batch_alter_table('shareholders', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_shareholders_company_id'))

    op.drop_table('shareholders')
    with op.batch_alter_table('revenues', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_revenues_company_id'))

    op.drop_table('revenues')
    with op.batch_alter_table('processes', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_processes_company_id'))

    op.drop_table('processes')
    with op.batch_alter_table('objectives', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_objectives_company_id'))

    op.drop_table('objectives')
    with op.batch_alter_table('markets', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_markets_company_id'))

    op.drop_table('markets')
    with op.batch_alter_table('liabilities', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_liabilities_company_id'))

    op.drop_table('liabilities')
    with op.batch_alter_table('functional_roles', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_functional_roles_company_id'))

    op.drop_table('functional_roles')
    with op.batch_alter_table('expenses', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_expenses_company_id'))

    op.drop_table('expenses')
    with op.batch_alter_table('entity_versions', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_entity_versions_company_id'))
        batch_op.drop_index('idx_entity_versions_entity')

    op.drop_table('entity_versions')
    with op.batch_alter_table('end_customers', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_end_customers_company_id'))

    op.drop_table('end_customers')
    with op.batch_alter_table('departments', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_departments_company_id'))

    op.drop_table('departments')
    with op.batch_alter_table('brands', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_brands_company_id'))

    op.drop_table('brands')
    with op.batch_alter_table('assets', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_assets_company_id'))

    op.drop_table('assets')
    op.drop_table('agents')


# Registros permanentes: no admiten UPDATE ni DELETE (TRUNCATE queda para administración)
APPEND_ONLY_TABLES = ("events", "scores", "business_occurrences", "entity_versions", "twin_lineage")


def _create_append_only_triggers() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("""
            CREATE OR REPLACE FUNCTION adan_append_only() RETURNS trigger AS $$
            BEGIN
                RAISE EXCEPTION 'append-only: % no admite %', TG_TABLE_NAME, TG_OP;
            END;
            $$ LANGUAGE plpgsql
        """)
        for table in APPEND_ONLY_TABLES:
            op.execute(f"CREATE TRIGGER trg_{table}_append_only BEFORE UPDATE OR DELETE ON {table} "
                       f"FOR EACH ROW EXECUTE FUNCTION adan_append_only()")
    else:
        # SQLite: una operación "batch" futura sobre estas tablas las recrea y borra sus
        # triggers; esa migración debe volver a llamar a esta función.
        for table in APPEND_ONLY_TABLES:
            for op_name in ("UPDATE", "DELETE"):
                op.execute(f"CREATE TRIGGER trg_{table}_no_{op_name.lower()} BEFORE {op_name} ON {table} "
                           f"BEGIN SELECT RAISE(ABORT, 'append-only: {table} no admite {op_name}'); END")


def _drop_append_only_triggers() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        for table in APPEND_ONLY_TABLES:
            op.execute(f"DROP TRIGGER IF EXISTS trg_{table}_append_only ON {table}")
        op.execute("DROP FUNCTION IF EXISTS adan_append_only()")
    else:
        for table in APPEND_ONLY_TABLES:
            for op_name in ("update", "delete"):
                op.execute(f"DROP TRIGGER IF EXISTS trg_{table}_no_{op_name}")


AGENTS = [
    ("ADAN", "ADÁN", "Orquestador: conversa con el cliente y coordina a los agentes"),
    ("CEO", "CEO Agent", "Preside el Board: abre la sesión y da la síntesis (no vota)"),
    ("CTO", "CTO", "Viabilidad técnica: factibilidad, arquitectura, riesgos tecnológicos"),
    ("CFO", "CFO", "Viabilidad financiera: costos, ingresos, caja, sostenibilidad"),
    ("CMO", "CMO", "Mercado: dolor real, demanda, diferenciación, canales"),
    ("Legal", "Legal", "Riesgos legales: regulación, contratos, propiedad intelectual, datos personales"),
    ("Producto", "Producto", "Producto: problema-solución, usuario, alcance del MVP, experiencia"),
    ("Operaciones", "Operaciones", "Operación: procesos, recursos, proveedores, capacidad de ejecutar"),
]


def _seed_agents() -> None:
    import uuid
    from datetime import datetime, timezone

    agents = sa.table(
        "agents",
        sa.column("id", sa.String), sa.column("code", sa.String), sa.column("name", sa.String),
        sa.column("description", sa.Text), sa.column("version", sa.Integer), sa.column("status", sa.String),
        sa.column("created_at", sa.DateTime), sa.column("updated_at", sa.DateTime),
        sa.column("created_by", sa.String), sa.column("updated_by", sa.String),
    )
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    op.bulk_insert(agents, [
        {"id": str(uuid.uuid4()), "code": code, "name": name, "description": desc, "version": 1,
         "status": "active", "created_at": now, "updated_at": now, "created_by": "system", "updated_by": "system"}
        for code, name, desc in AGENTS
    ])
