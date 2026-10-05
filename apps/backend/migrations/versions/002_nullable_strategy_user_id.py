"""Make strategies.user_id nullable (pre-auth ownerless strategies)

Revision ID: 002
Revises: 001
Create Date: 2026-10-05

See SPECS/strategy-graph.md §11 (U1).
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        'strategies',
        'user_id',
        existing_type=postgresql.UUID(as_uuid=True),
        nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        'strategies',
        'user_id',
        existing_type=postgresql.UUID(as_uuid=True),
        nullable=False,
    )
