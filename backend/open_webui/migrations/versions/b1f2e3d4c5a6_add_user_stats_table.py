"""add user_stats table

Revision ID: b1f2e3d4c5a6
Revises: a8f5b2c7d9e0
Create Date: 2025-05-08 09:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import open_webui.internal.db

# revision identifiers, used by Alembic.
revision: str = 'b1f2e3d4c5a6'
down_revision: Union[str, None] = 'a8f5b2c7d9e0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create the user_stats table
    op.create_table(
        'user_stats',
        sa.Column('user_id', sa.String(), primary_key=True),
        sa.Column('query_count', sa.Integer(), nullable=False, default=0),
        sa.Column('created_at', sa.BigInteger(), nullable=False),
        sa.Column('updated_at', sa.BigInteger(), nullable=False),
        sa.PrimaryKeyConstraint('user_id')
    )


def downgrade() -> None:
    # Drop the user_stats table
    op.drop_table('user_stats')
