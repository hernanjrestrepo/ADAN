"""El nombre del producto se escribe ADAN, sin tilde (confunde en otros idiomas).

Los mensajes ya guardados dejan de mostrar la grafía anterior como autor.

Revision ID: 0013
Revises: 0012
Create Date: 2026-10-31 12:00:00
"""
from typing import Sequence, Union

from alembic import op

revision: str = '0013'
down_revision: Union[str, None] = '0012'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

OLD = "ADÁN"


def upgrade() -> None:
    op.execute(f"UPDATE messages SET agent_name = 'ADAN' WHERE agent_name = '{OLD}'")


def downgrade() -> None:
    op.execute(f"UPDATE messages SET agent_name = '{OLD}' WHERE agent_name = 'ADAN'")
