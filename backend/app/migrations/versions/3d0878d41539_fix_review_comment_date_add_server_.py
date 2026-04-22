"""fix review comment_date add server default

Revision ID: 3d0878d41539
Revises: e298347dbd2b
Create Date: 2026-04-23

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3d0878d41539'
down_revision: Union[str, Sequence[str], None] = 'e298347dbd2b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add server-side DEFAULT NOW() to comment_date.
    # The previous migration changed the column type to DateTime(timezone=True)
    # but did not set the server default — causing NOT NULL violations on INSERT.
    op.alter_column(
        'reviews',
        'comment_date',
        server_default=sa.text('now()'),
    )


def downgrade() -> None:
    # Remove the server default — column reverts to requiring explicit value on insert.
    op.alter_column(
        'reviews',
        'comment_date',
        server_default=None,
    )
