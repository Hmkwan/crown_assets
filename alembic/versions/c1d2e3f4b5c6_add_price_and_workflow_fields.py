"""add equipment.price and user/workflow node fields

Revision ID: c1d2e3f4b5c6
Revises: b0a349fa6c4b
Create Date: 2025-11-26 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c1d2e3f4b5c6'
down_revision: Union[str, Sequence[str], None] = 'b0a349fa6c4b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema: add missing columns with safe defaults."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    # Equipment.price
    if 'equipment' in inspector.get_table_names():
        cols = [c['name'] for c in inspector.get_columns('equipment')]
        if 'price' not in cols:
            op.add_column('equipment', sa.Column('price', sa.Float(), nullable=True, server_default=sa.text('0')))

    # User: is_active, can_edit_workflow, can_manage_workflow_templates
    if 'user' in inspector.get_table_names():
        cols = [c['name'] for c in inspector.get_columns('user')]
        if 'is_active' not in cols:
            op.add_column('user', sa.Column('is_active', sa.Boolean(), nullable=True, server_default=sa.text('1')))
        if 'can_edit_workflow' not in cols:
            op.add_column('user', sa.Column('can_edit_workflow', sa.Boolean(), nullable=True, server_default=sa.text('0')))
        if 'can_manage_workflow_templates' not in cols:
            op.add_column('user', sa.Column('can_manage_workflow_templates', sa.Boolean(), nullable=True, server_default=sa.text('0')))

    # WorkflowNode: approver_user_ids, is_parallel, required_approvals, actions_on_reject
    if 'workflow_node' in inspector.get_table_names():
        cols = [c['name'] for c in inspector.get_columns('workflow_node')]
        if 'approver_user_ids' not in cols:
            op.add_column('workflow_node', sa.Column('approver_user_ids', sa.Text(), nullable=True))
        if 'is_parallel' not in cols:
            op.add_column('workflow_node', sa.Column('is_parallel', sa.Boolean(), nullable=True, server_default=sa.text('0')))
        if 'required_approvals' not in cols:
            op.add_column('workflow_node', sa.Column('required_approvals', sa.Integer(), nullable=True, server_default=sa.text('1')))
        if 'actions_on_reject' not in cols:
            op.add_column('workflow_node', sa.Column('actions_on_reject', sa.Text(), nullable=True))


def downgrade() -> None:
    """Downgrade schema: drop columns if present."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if 'workflow_node' in inspector.get_table_names():
        cols = [c['name'] for c in inspector.get_columns('workflow_node')]
        if 'actions_on_reject' in cols:
            op.drop_column('workflow_node', 'actions_on_reject')
        if 'required_approvals' in cols:
            op.drop_column('workflow_node', 'required_approvals')
        if 'is_parallel' in cols:
            op.drop_column('workflow_node', 'is_parallel')
        if 'approver_user_ids' in cols:
            op.drop_column('workflow_node', 'approver_user_ids')

    if 'user' in inspector.get_table_names():
        cols = [c['name'] for c in inspector.get_columns('user')]
        if 'can_manage_workflow_templates' in cols:
            op.drop_column('user', 'can_manage_workflow_templates')
        if 'can_edit_workflow' in cols:
            op.drop_column('user', 'can_edit_workflow')
        if 'is_active' in cols:
            op.drop_column('user', 'is_active')

    if 'equipment' in inspector.get_table_names():
        cols = [c['name'] for c in inspector.get_columns('equipment')]
        if 'price' in cols:
            op.drop_column('equipment', 'price')
