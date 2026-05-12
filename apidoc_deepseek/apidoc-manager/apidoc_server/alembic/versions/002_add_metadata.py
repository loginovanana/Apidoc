"""Add metadata columns

Revision ID: 002_add_metadata
Revises: 001_initial
Create Date: 2024-01-02 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '002_add_metadata'
down_revision: Union[str, None] = '001_initial'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('specifications', sa.Column('owner', sa.String(length=255), nullable=True))
    op.add_column('specifications', sa.Column('visibility', sa.String(length=20), server_default='private', nullable=False))
    op.add_column('specifications', sa.Column('contact_email', sa.String(length=255), nullable=True))
    op.add_column('specifications', sa.Column('license_name', sa.String(length=100), nullable=True))
    op.add_column('specifications', sa.Column('license_url', sa.String(length=500), nullable=True))


def downgrade() -> None:
    op.drop_column('specifications', 'license_url')
    op.drop_column('specifications', 'license_name')
    op.drop_column('specifications', 'contact_email')
    op.drop_column('specifications', 'visibility')
    op.drop_column('specifications', 'owner')
