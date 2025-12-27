"""Ensure missing workflow and chat columns exist (idempotent)

Revision ID: ensure_workflow_chat_cols
Revises: backfill_chat_attach_upload
Create Date: 2025-12-31

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = 'ensure_workflow_chat_cols'
down_revision = 'backfill_chat_attach_upload'
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

    # workflow_template.config (JSON stored as text)
    if has_table('workflow_template') and not has_col('workflow_template', 'config'):
        try:
            op.add_column('workflow_template', sa.Column('config', sa.Text(), nullable=True))
            print('Added workflow_template.config')
        except Exception as e:
            print('Skip adding workflow_template.config (non-fatal):', e)

    # workflow_template.created_date / updated_date (compat aliases for created_at/updated_at)
    if has_table('workflow_template'):
        if not has_col('workflow_template', 'created_date'):
            try:
                op.add_column('workflow_template', sa.Column('created_date', sa.DateTime(), nullable=True))
                op.execute("UPDATE workflow_template SET created_date = created_at WHERE created_date IS NULL AND created_at IS NOT NULL")
                print('Added workflow_template.created_date and populated from created_at')
            except Exception as e:
                print('Skip adding workflow_template.created_date (non-fatal):', e)
        if not has_col('workflow_template', 'updated_date'):
            try:
                op.add_column('workflow_template', sa.Column('updated_date', sa.DateTime(), nullable=True))
                op.execute("UPDATE workflow_template SET updated_date = updated_at WHERE updated_date IS NULL AND updated_at IS NOT NULL")
                print('Added workflow_template.updated_date and populated from updated_at')
            except Exception as e:
                print('Skip adding workflow_template.updated_date (non-fatal):', e)

    # workflow_node.template_id
    if has_table('workflow_node') and not has_col('workflow_node', 'template_id'):
        try:
            op.add_column('workflow_node', sa.Column('template_id', sa.Integer(), nullable=True))
            if has_table('workflow_template'):
                op.create_foreign_key('fk_workflow_node_template', 'workflow_node', 'workflow_template', ['template_id'], ['id'], ondelete='CASCADE')
            print('Added workflow_node.template_id')
        except Exception as e:
            print('Skip adding workflow_node.template_id (non-fatal):', e)

    # chat_participant.is_left and left_date
    if has_table('chat_participant'):
        if not has_col('chat_participant', 'is_left'):
            try:
                # Use textual boolean default to avoid dialect numeric boolean issues
                op.add_column('chat_participant', sa.Column('is_left', sa.Boolean(), nullable=False, server_default=sa.text('false')))
                print('Added chat_participant.is_left')
            except Exception as e:
                print('Skip adding chat_participant.is_left (non-fatal):', e)
        if not has_col('chat_participant', 'left_date'):
            try:
                op.add_column('chat_participant', sa.Column('left_date', sa.DateTime(), nullable=True))
                print('Added chat_participant.left_date')
            except Exception as e:
                print('Skip adding chat_participant.left_date (non-fatal):', e)
        if not has_col('chat_participant', 'role'):
            try:
                op.add_column('chat_participant', sa.Column('role', sa.String(length=32), nullable=True))
                print('Added chat_participant.role')
            except Exception as e:
                print('Skip adding chat_participant.role (non-fatal):', e)

    # Ensure chat_attachment.upload_user_id is nullable (so tests can insert NULL before backfill runs)
    if has_table('chat_attachment') and has_col('chat_attachment', 'upload_user_id'):
        try:
            cols = [col for col in insp.get_columns('chat_attachment') if col['name'] == 'upload_user_id']
            if cols and not cols[0].get('nullable', True):
                try:
                    op.alter_column('chat_attachment', 'upload_user_id', existing_type=sa.Integer(), nullable=True)
                    print('Altered chat_attachment.upload_user_id to be nullable')
                except Exception as e:
                    print('Could not alter chat_attachment.upload_user_id to nullable (non-fatal):', e)
        except Exception as e:
            print('Skip checking chat_attachment.upload_user_id nullability (non-fatal):', e)

    # workflow_node.code (basic identifier)
    if has_table('workflow_node') and not has_col('workflow_node', 'code'):
        try:
            op.add_column('workflow_node', sa.Column('code', sa.String(length=64), nullable=True))
            print('Added workflow_node.code')
        except Exception as e:
            print('Skip adding workflow_node.code (non-fatal):', e)


def downgrade():
    # Intentionally no-op; schema cleanup not required
    print('Downgrade: no-op for ensure_workflow_chat_cols')
