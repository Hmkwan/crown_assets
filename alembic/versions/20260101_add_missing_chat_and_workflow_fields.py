"""Add missing chat and workflow fields that may be absent in some DB states

Revision ID: add_missing_chat_workflow_fields
Revises: ensure_workflow_chat_cols
Create Date: 2026-01-01
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = 'add_missing_chat_workflow_fields'
down_revision = 'ensure_workflow_chat_cols'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    insp = inspect(bind)

    def has_table(t):
        try:
            return insp.has_table(t)
        except Exception:
            return False

    def has_col(t, c):
        if not has_table(t):
            return False
        try:
            return c in [col['name'] for col in insp.get_columns(t)]
        except Exception:
            return False

    # chat_participant.role
    if has_table('chat_participant') and not has_col('chat_participant', 'role'):
        try:
            op.add_column('chat_participant', sa.Column('role', sa.String(length=32), nullable=True, server_default='member'))
            print('Added chat_participant.role')
        except Exception as e:
            print('Skip adding chat_participant.role (non-fatal):', e)

    # workflow_node.code
    if has_table('workflow_node') and not has_col('workflow_node', 'code'):
        try:
            op.add_column('workflow_node', sa.Column('code', sa.String(length=64), nullable=True))
            print('Added workflow_node.code')
        except Exception as e:
            print('Skip adding workflow_node.code (non-fatal):', e)

    # workflow_template created_date/updated_date (fallback)
    if has_table('workflow_template'):
        if not has_col('workflow_template', 'created_date'):
            try:
                op.add_column('workflow_template', sa.Column('created_date', sa.DateTime(), nullable=True))
                op.execute("UPDATE workflow_template SET created_date = created_at WHERE created_date IS NULL AND created_at IS NOT NULL")
                print('Added workflow_template.created_date')
            except Exception as e:
                print('Skip adding workflow_template.created_date (non-fatal):', e)
        if not has_col('workflow_template', 'updated_date'):
            try:
                op.add_column('workflow_template', sa.Column('updated_date', sa.DateTime(), nullable=True))
                op.execute("UPDATE workflow_template SET updated_date = updated_at WHERE updated_date IS NULL AND updated_at IS NOT NULL")
                print('Added workflow_template.updated_date')
            except Exception as e:
                print('Skip adding workflow_template.updated_date (non-fatal):', e)


def downgrade():
    print('Downgrade: not implemented for add_missing_chat_workflow_fields')
