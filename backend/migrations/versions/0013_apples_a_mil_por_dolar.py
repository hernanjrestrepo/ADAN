"""La @pple pasa de valer US$ 1 a US$ 0,001 (US$ 1 = 1.000 @pples).

Los saldos, las compras y los Niveles pagados quedaban en la unidad anterior; se multiplican por 1.000 para que
cada persona conserve exactamente su valor en dólares (quien tenía 25 @pples queda con 25.000). Los pesos
cobrados en cada compra no cambian. La bajada divide entre 1.000 (redondea las compras a la @pple entera).

Revision ID: 0013
Revises: 0012
Create Date: 2026-10-29 12:00:00
"""
from typing import Sequence, Union

from alembic import op

revision: str = '0013'
down_revision: Union[str, None] = '0012'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

FACTOR = 1000


def upgrade() -> None:
    op.execute(f"UPDATE apple_movements SET amount = amount * {FACTOR}")
    op.execute(f"UPDATE apple_purchases SET apples = apples * {FACTOR}")
    op.execute(f"UPDATE apple_level_unlocks SET apples = apples * {FACTOR}")


def downgrade() -> None:
    # Divisiones con decimales: en SQLite 25 / 1000 entero daría 0
    op.execute(f"UPDATE apple_movements SET amount = amount / {FACTOR}.0")
    op.execute(f"UPDATE apple_purchases SET apples = CAST(ROUND(apples / {FACTOR}.0) AS INTEGER)")
    op.execute(f"UPDATE apple_level_unlocks SET apples = apples / {FACTOR}.0")
