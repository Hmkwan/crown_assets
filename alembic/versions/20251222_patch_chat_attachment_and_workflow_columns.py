"""Patch migration: add missing columns and be idempotent across dialects

Revision ID: 20251222_patch_chat_attachment_and_workflow_columns
Revises: patch_normalize_attachment_paths
Create Date: 2025-12-22

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = '20251222_patch_chat_attachment_and_workflow_columns'
down_revision = 'patch_normalize_attachment_paths'
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

    # Helper to attempt an operation and ignore unsupported dialect errors
    def safe(f, *args, **kwargs):
        try:
            f(*args, **kwargs)
        except Exception as e:
            print(f"Migration skip (non-fatal): {e}")

    # chat_attachment.upload_user_id (add as nullable for safe backfill)
    if not has_column('chat_attachment', 'upload_user_id'):
        safe(op.add_column, 'chat_attachment', sa.Column('upload_user_id', sa.Integer(), nullable=True))

    # Ensure chat_attachment.message_id is nullable (may not be supported by SQLite)
    if has_column('chat_attachment', 'message_id'):
        cols = {c['name']: c for c in insp.get_columns('chat_attachment')}
        if not cols['message_id'].get('nullable', True):
            safe(op.alter_column, 'chat_attachment', 'message_id', existing_type=sa.Integer(), nullable=True)

    # workflow_node.role_required_name
    if not has_column('workflow_node', 'role_required_name'):
        safe(op.add_column, 'workflow_node', sa.Column('role_required_name', sa.String(length=64), nullable=True))

    # workflow_node.approver_user_id
    if not has_column('workflow_node', 'approver_user_id'):
        safe(op.add_column, 'workflow_node', sa.Column('approver_user_id', sa.Integer(), nullable=True))

    # workflow_node.approver_user_ids
    if not has_column('workflow_node', 'approver_user_ids'):
        safe(op.add_column, 'workflow_node', sa.Column('approver_user_ids', sa.Text(), nullable=True))

    # approval_workflow.required_approvals
    if not has_column('approval_workflow', 'required_approvals'):
        safe(op.add_column, 'approval_workflow', sa.Column('required_approvals', sa.Integer(), nullable=True, server_default=sa.text('1')))

    # approval_workflow.actions_on_reject
    if not has_column('approval_workflow', 'actions_on_reject'):
        safe(op.add_column, 'approval_workflow', sa.Column('actions_on_reject', sa.Text(), nullable=True))

    # workflow_template.is_default
    if not has_column('workflow_template', 'is_default'):
        safe(op.add_column, 'workflow_template', sa.Column('is_default', sa.Boolean(), nullable=True, server_default=sa.false()))

    # app_user workflow-related flags
    if not has_column('app_user', 'can_edit_workflow'):
        safe(op.add_column, 'app_user', sa.Column('can_edit_workflow', sa.Boolean(), nullable=True, server_default=sa.false()))
    if not has_column('app_user', 'can_manage_workflow_templates'):
        safe(op.add_column, 'app_user', sa.Column('can_manage_workflow_templates', sa.Boolean(), nullable=True, server_default=sa.false()))
    if not has_column('app_user', 'is_active'):
        safe(op.add_column, 'app_user', sa.Column('is_active', sa.Boolean(), nullable=True, server_default=sa.true()))


def downgrade():
    bind = op.get_bind()
    insp = inspect(bind)

    def has_column(table_name, col_name):
        try:
            cols = [c['name'] for c in insp.get_columns(table_name)]
            return col_name in cols
        except Exception:
            return False

    if has_column('chat_attachment', 'upload_user_id'):
        op.drop_column('chat_attachment', 'upload_user_id')

    if has_column('workflow_node', 'role_required_name'):
        op.drop_column('workflow_node', 'role_required_name')
    if has_column('workflow_node', 'approver_user_id'):
        op.drop_column('workflow_node', 'approver_user_id')
    if has_column('workflow_node', 'approver_user_ids'):
        op.drop_column('workflow_node', 'approver_user_ids')

    if has_column('approval_workflow', 'required_approvals'):
        op.drop_column('approval_workflow', 'required_approvals')
    if has_column('approval_workflow', 'actions_on_reject'):
        op.drop_column('approval_workflow', 'actions_on_reject')

    if has_column('workflow_template', 'is_default'):
        op.drop_column('workflow_template', 'is_default')

    if has_column('app_user', 'can_edit_workflow'):
        op.drop_column('app_user', 'can_edit_workflow')
    if has_column('app_user', 'can_manage_workflow_templates'):
        op.drop_column('app_user', 'can_manage_workflow_templates')
    if has_column('app_user', 'is_active'):
        op.drop_column('app_user', 'is_active')
