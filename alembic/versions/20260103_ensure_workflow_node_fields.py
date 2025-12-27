"""Ensure common WorkflowNode fields exist (idempotent)

Revision ID: ensure_wf_node_fields
Revises: ensure_wf_node_seq
Create Date: 2026-01-03
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = 'ensure_wf_node_fields'
down_revision = 'ensure_wf_node_seq'
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

    if has_table('workflow_node'):
        # node_type
        if not has_col('workflow_node', 'node_type'):
            try:
                op.add_column('workflow_node', sa.Column('node_type', sa.String(length=32), nullable=True, server_default='approval'))
                print('Added workflow_node.node_type')
            except Exception as e:
                print('Skip adding workflow_node.node_type (non-fatal):', e)

        # approval_role_id (foreign key to approval_role) - add as nullable for safety
        if not has_col('workflow_node', 'approval_role_id'):
            try:
                op.add_column('workflow_node', sa.Column('approval_role_id', sa.Integer(), nullable=True))
                print('Added workflow_node.approval_role_id')
            except Exception as e:
                print('Skip adding workflow_node.approval_role_id (non-fatal):', e)

        # condition_expr
        if not has_col('workflow_node', 'condition_expr'):
            try:
                op.add_column('workflow_node', sa.Column('condition_expr', sa.Text(), nullable=True))
                print('Added workflow_node.condition_expr')
            except Exception as e:
                print('Skip adding workflow_node.condition_expr (non-fatal):', e)

        # amount_threshold
        if not has_col('workflow_node', 'amount_threshold'):
            try:
                op.add_column('workflow_node', sa.Column('amount_threshold', sa.Numeric(15, 2), nullable=True))
                print('Added workflow_node.amount_threshold')
            except Exception as e:
                print('Skip adding workflow_node.amount_threshold (non-fatal):', e)

        # skip_if_below_threshold
        if not has_col('workflow_node', 'skip_if_below_threshold'):
            try:
                op.add_column('workflow_node', sa.Column('skip_if_below_threshold', sa.Boolean(), nullable=True, server_default=sa.text('false')))
                print('Added workflow_node.skip_if_below_threshold')
            except Exception as e:
                print('Skip adding workflow_node.skip_if_below_threshold (non-fatal):', e)

        # is_parallel
        if not has_col('workflow_node', 'is_parallel'):
            try:
                op.add_column('workflow_node', sa.Column('is_parallel', sa.Boolean(), nullable=True, server_default=sa.text('false')))
                print('Added workflow_node.is_parallel')
            except Exception as e:
                print('Skip adding workflow_node.is_parallel (non-fatal):', e)

        # required_approvals
        if not has_col('workflow_node', 'required_approvals'):
            try:
                op.add_column('workflow_node', sa.Column('required_approvals', sa.Integer(), nullable=True, server_default=sa.text('1')))
                print('Added workflow_node.required_approvals')
            except Exception as e:
                print('Skip adding workflow_node.required_approvals (non-fatal):', e)

        # parallel_mode
        if not has_col('workflow_node', 'parallel_mode'):
            try:
                op.add_column('workflow_node', sa.Column('parallel_mode', sa.String(length=32), nullable=True))
                print('Added workflow_node.parallel_mode')
            except Exception as e:
                print('Skip adding workflow_node.parallel_mode (non-fatal):', e)

        # timeout and escalation
        if not has_col('workflow_node', 'timeout_hours'):
            try:
                op.add_column('workflow_node', sa.Column('timeout_hours', sa.Integer(), nullable=True))
                print('Added workflow_node.timeout_hours')
            except Exception as e:
                print('Skip adding workflow_node.timeout_hours (non-fatal):', e)
        if not has_col('workflow_node', 'timeout_action'):
            try:
                op.add_column('workflow_node', sa.Column('timeout_action', sa.String(length=32), nullable=True))
                print('Added workflow_node.timeout_action')
            except Exception as e:
                print('Skip adding workflow_node.timeout_action (non-fatal):', e)
        if not has_col('workflow_node', 'escalate_to_role_id'):
            try:
                op.add_column('workflow_node', sa.Column('escalate_to_role_id', sa.Integer(), nullable=True))
                print('Added workflow_node.escalate_to_role_id')
            except Exception as e:
                print('Skip adding workflow_node.escalate_to_role_id (non-fatal):', e)

        # auto approve/reject rules, notify settings
        if not has_col('workflow_node', 'auto_approve_rules'):
            try:
                op.add_column('workflow_node', sa.Column('auto_approve_rules', sa.JSON(), nullable=True))
                print('Added workflow_node.auto_approve_rules')
            except Exception as e:
                print('Skip adding workflow_node.auto_approve_rules (non-fatal):', e)
        if not has_col('workflow_node', 'auto_reject_rules'):
            try:
                op.add_column('workflow_node', sa.Column('auto_reject_rules', sa.JSON(), nullable=True))
                print('Added workflow_node.auto_reject_rules')
            except Exception as e:
                print('Skip adding workflow_node.auto_reject_rules (non-fatal):', e)

        if not has_col('workflow_node', 'notify_on_start'):
            try:
                op.add_column('workflow_node', sa.Column('notify_on_start', sa.Boolean(), nullable=True, server_default=sa.text('true')))
                print('Added workflow_node.notify_on_start')
            except Exception as e:
                print('Skip adding workflow_node.notify_on_start (non-fatal):', e)
        if not has_col('workflow_node', 'notify_on_complete'):
            try:
                op.add_column('workflow_node', sa.Column('notify_on_complete', sa.Boolean(), nullable=True, server_default=sa.text('true')))
                print('Added workflow_node.notify_on_complete')
            except Exception as e:
                print('Skip adding workflow_node.notify_on_complete (non-fatal):', e)
        if not has_col('workflow_node', 'notify_methods'):
            try:
                op.add_column('workflow_node', sa.Column('notify_methods', sa.JSON(), nullable=True))
                print('Added workflow_node.notify_methods')
            except Exception as e:
                print('Skip adding workflow_node.notify_methods (non-fatal):', e)

        if not has_col('workflow_node', 'is_active'):
            try:
                op.add_column('workflow_node', sa.Column('is_active', sa.Boolean(), nullable=True, server_default=sa.text('true')))
                print('Added workflow_node.is_active')
            except Exception as e:
                print('Skip adding workflow_node.is_active (non-fatal):', e)


def downgrade():
    print('Downgrade: no-op for ensure_wf_node_fields')
