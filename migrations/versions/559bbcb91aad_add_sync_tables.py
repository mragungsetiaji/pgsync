"""add_sync_tables

Revision ID: 559bbcb91aad
Revises: f3fd2813dd0f
Create Date: 2025-03-05 13:52:21.300855

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '559bbcb91aad'
down_revision: Union[str, None] = 'f3fd2813dd0f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('sync_tables',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('source_db_id', sa.Integer(), nullable=False),
    sa.Column('table_name', sa.String(length=100), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('cursor_column', sa.String(length=100), nullable=False),
    sa.Column('batch_size', sa.Integer(), nullable=True),
    sa.Column('sync_interval', sa.Integer(), nullable=True),
    sa.Column('last_synced_at', sa.DateTime(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['source_db_id'], ['source_databases.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('source_db_id', 'table_name', name='uix_sync_table')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('sync_tables')
    # ### end Alembic commands ###
