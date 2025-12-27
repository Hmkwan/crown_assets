"""Add recalled_date to chat_message if missing (idempotent)

Revision ID: add_chat_message_recalled_date
Revises: ensure_wf_node_fields
Create Date: 2026-01-04
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = 'add_chat_message_recalled_date'
down_revision = 'ensure_wf_node_fields'
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

    if has_table('chat_message') and not has_col('chat_message', 'recalled_date'):
        try:
            op.add_column('chat_message', sa.Column('recalled_date', sa.DateTime(), nullable=True))
            print('Added chat_message.recalled_date')
        except Exception as e:
            print('Skip adding chat_message.recalled_date (non-fatal):', e)


def downgrade():
    print('Downgrade: no-op for add_chat_message_recalled_date')
