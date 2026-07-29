"""rename price history table

Revision ID: a79db36d35c7
Revises: 9122546b10b4
Create Date: 2026-07-29 14:41:59.049891

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a79db36d35c7'
down_revision: Union[str, Sequence[str], None] = '9122546b10b4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.rename_table("PriceHistory", "price_history")


def downgrade() -> None:
    """Downgrade schema."""
    op.rename_table("price_history", "PriceHistory")
