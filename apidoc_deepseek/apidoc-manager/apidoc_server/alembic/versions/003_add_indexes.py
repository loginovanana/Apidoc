"""Add indexes for performance

Revision ID: 003_add_indexes
Revises: 002_add_metadata
Create Date: 2024-01-03 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '003_add_indexes'
down_revision: Union[str, None] = '002_add_metadata'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index('ix_spec_versions_spec_id_created_at', 'spec_versions', ['spec_id', 'created_at'])
    op.create_index('ix_specifications_name_title', 'specifications', ['name', 'title'])
    op.create_index('ix_specifications_updated_at', 'specifications', ['updated_at'])


def downgrade() -> None:
    op.drop_index('ix_specifications_updated_at', table_name='specifications')
    op.drop_index('ix_specifications_name_title', table_name='specifications')
    op.drop_index('ix_spec_versions_spec_id_created_at', table_name='spec_versions')
