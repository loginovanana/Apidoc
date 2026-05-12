"""Initial schema.
Revision ID: 0001
Revises:
Create Date: 2026-04-11
"""
from alembic import op
import sqlalchemy as sa
revision = "0001"; down_revision = None; branch_labels = None; depends_on = None

def upgrade():
    op.create_table("specs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("latest_version", sa.String(50), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False))
    op.create_index("ix_specs_name","specs",["name"])
    op.create_table("spec_versions",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("spec_id", sa.Integer(), sa.ForeignKey("specs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("version", sa.String(50), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("content_hash", sa.String(64), nullable=False),
        sa.Column("changelog", sa.Text(), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False))
    op.create_index("ix_spec_versions_spec_id","spec_versions",["spec_id"])
    op.create_index("ix_spec_versions_hash","spec_versions",["content_hash"])

def downgrade():
    op.drop_table("spec_versions"); op.drop_table("specs")
