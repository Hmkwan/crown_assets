"""Add workflow_node.approval_role_id if missing

Revision ID: 20260105_add_workflow_node_approval_role_id
Revises: patch_chat_attachment_and_workflow_columns
Create Date: 2026-01-05
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = '20260105_add_workflow_node_approval_role_id'
down_revision = 'add_chat_message_recalled_date'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    insp = inspect(bind)

    def has_column(table_name, col_name):
        try:
            cols = [c['name'] for c in insp.get_columns(table_name)]
            return col_name in cols
        except Exception:
            return False

    def safe(f, *args, **kwargs):
        try:
            f(*args, **kwargs)
        except Exception as e:
            print(f"Migration skip (non-fatal): {e}")

    if not has_column('workflow_node', 'approval_role_id'):
        safe(op.add_column, 'workflow_node', sa.Column('approval_role_id', sa.Integer(), nullable=True))


def downgrade():
    bind = op.get_bind()
    insp = inspect(bind)

    def has_column(table_name, col_name):
        try:
            cols = [c['name'] for c in insp.get_columns(table_name)]
            return col_name in cols
        except Exception:
            return False

    if has_column('workflow_node', 'approval_role_id'):
        op.drop_column('workflow_node', 'approval_role_id')
