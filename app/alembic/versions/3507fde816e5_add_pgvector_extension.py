"""add_pgvector_extension

Revision ID: 3507fde816e5
Revises: 002_add_ai_fields
Create Date: 2025-11-23 21:57:14.417970

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3507fde816e5'
down_revision: Union[str, Sequence[str], None] = '002_add_ai_fields'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')


def downgrade() -> None:
    """Downgrade schema."""
    op.execute('DROP EXTENSION IF EXISTS vector')
