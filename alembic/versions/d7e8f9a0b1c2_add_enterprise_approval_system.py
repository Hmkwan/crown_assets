"""add enterprise approval system tables

Revision ID: d7e8f9a0b1c2
Revises: c1d2e3f4b5c6
Create Date: 2025-01-11 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite


# revision identifiers, used by Alembic.
revision: str = 'd7e8f9a0b1c2'
down_revision: Union[str, Sequence[str], None] = 'c1d2e3f4b5c6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    创建企业级审批系统的7个核心表:
    1. workflow_template - 工作流模板
    2. workflow_node (增强) - 工作流节点(已存在,添加新字段)
    3. approval_instance - 审批实例
    4. approval_step - 审批步骤
    5. approval_log - 审批日志
    6. approval_delegate - 审批委托
    7. approval_reminder - 审批提醒
    """
    
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    
    # 1. WorkflowTemplate - 工作流模板表
    if 'workflow_template' not in inspector.get_table_names():
        op.create_table(
            'workflow_template',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(length=128), nullable=False, comment='模板名称'),
            sa.Column('code', sa.String(length=64), nullable=False, comment='模板编码(唯一)'),
            sa.Column('order_type', sa.String(length=64), nullable=False, comment='工单类型'),
            sa.Column('description', sa.Text(), nullable=True, comment='模板描述'),
            sa.Column('version', sa.Integer(), nullable=False, server_default=sa.text('1'), comment='版本号'),
            sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true'), comment='是否启用'),
            sa.Column('is_default', sa.Boolean(), nullable=False, server_default=sa.text('false'), comment='是否默认模板'),
            sa.Column('created_by_id', sa.Integer(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime(), nullable=True, onupdate=sa.func.now()),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('code', 'version', name='uq_template_code_version')
        )
        # Only add the FK to user if the user table already exists in this DB
        if 'user' in inspector.get_table_names():
            op.create_foreign_key('fk_workflow_template_created_by', 'workflow_template', 'user', ['created_by_id'], ['id'], ondelete='SET NULL')

        # Create indexes if they don't already exist
        if 'workflow_template' in inspector.get_table_names():
            existing_indexes = [i['name'] for i in inspector.get_indexes('workflow_template')]
            if 'ix_workflow_template_code' not in existing_indexes:
                op.create_index('ix_workflow_template_code', 'workflow_template', ['code'])
            if 'ix_workflow_template_order_type' not in existing_indexes:
                op.create_index('ix_workflow_template_order_type', 'workflow_template', ['order_type'])
    
    # 2. 增强 WorkflowNode 表 - 添加企业级字段
    # 如果 workflow_node 表不存在（旧库或遗留迁移不完整），先创建一个最小表结构以保证后续迁移成功
    if 'workflow_node' not in inspector.get_table_names():
        op.create_table(
            'workflow_node',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(length=128), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )

    if 'workflow_node' in inspector.get_table_names():
        cols = [c['name'] for c in inspector.get_columns('workflow_node')]
        
        # 添加模板关联
        if 'template_id' not in cols:
            op.add_column('workflow_node', sa.Column('template_id', sa.Integer(), nullable=True))
            op.create_foreign_key('fk_workflow_node_template', 'workflow_node', 'workflow_template', ['template_id'], ['id'], ondelete='CASCADE')
        
        # 添加节点类型和高级功能
        if 'node_type' not in cols:
            op.add_column('workflow_node', sa.Column('node_type', sa.String(length=32), nullable=False, server_default='approval', comment='节点类型: approval/condition/parallel/auto'))
        
        if 'condition_expression' not in cols:
            op.add_column('workflow_node', sa.Column('condition_expression', sa.Text(), nullable=True, comment='条件表达式(Python)'))
        
        if 'parallel_mode' not in cols:
            op.add_column('workflow_node', sa.Column('parallel_mode', sa.String(length=16), nullable=True, comment='并行模式: all/any/count'))
        
        if 'parallel_count' not in cols:
            op.add_column('workflow_node', sa.Column('parallel_count', sa.Integer(), nullable=True, comment='并行所需审批数'))
        
        if 'timeout_hours' not in cols:
            op.add_column('workflow_node', sa.Column('timeout_hours', sa.Integer(), nullable=True, comment='超时时长(小时)'))
        
        if 'timeout_action' not in cols:
            op.add_column('workflow_node', sa.Column('timeout_action', sa.String(length=32), nullable=True, comment='超时动作: auto_approve/auto_reject/escalate/notify'))
        
        if 'escalate_to_user_id' not in cols:
            op.add_column('workflow_node', sa.Column('escalate_to_user_id', sa.Integer(), nullable=True))
            # Only create FK if user table exists to avoid failures on fresh DBs where "user" is created later
            if 'user' in inspector.get_table_names():
                op.create_foreign_key('fk_workflow_node_escalate_user', 'workflow_node', 'user', ['escalate_to_user_id'], ['id'], ondelete='SET NULL')
            else:
                # skip FK creation; migrations that create user table should add appropriate FK later
                pass
        # 3. ApprovalInstance - 审批实例表
    if 'approval_instance' not in inspector.get_table_names():
        op.create_table(
            'approval_instance',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('template_id', sa.Integer(), nullable=True),
            sa.Column('initiator_id', sa.Integer(), nullable=True),
            sa.Column('status', sa.String(length=32), nullable=False, server_default='pending'),
            sa.Column('data', sa.Text(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime(), nullable=True, onupdate=sa.func.now()),
            sa.PrimaryKeyConstraint('id')
        )
        if 'workflow_template' in inspector.get_table_names():
            op.create_foreign_key('fk_approval_instance_template', 'approval_instance', 'workflow_template', ['template_id'], ['id'], ondelete='SET NULL')
        if 'user' in inspector.get_table_names():
            op.create_foreign_key('fk_approval_instance_initiator', 'approval_instance', 'user', ['initiator_id'], ['id'], ondelete='SET NULL')
        if 'approval_instance' in inspector.get_table_names():
            existing_indexes = [i['name'] for i in inspector.get_indexes('approval_instance')]
            if 'ix_approval_instance_status' not in existing_indexes:
                op.create_index('ix_approval_instance_status', 'approval_instance', ['status'])
            if 'ix_approval_instance_initiator' not in existing_indexes:
                op.create_index('ix_approval_instance_initiator', 'approval_instance', ['initiator_id'])

    # 4. ApprovalStep - 审批步骤表
    if 'approval_step' not in inspector.get_table_names():
        op.create_table(
            'approval_step',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('instance_id', sa.Integer(), nullable=False),
            sa.Column('node_id', sa.Integer(), nullable=False),
            sa.Column('approver_id', sa.Integer(), nullable=True, comment='审批人ID(可为空,如条件/自动节点)'),
            sa.Column('delegated_by_id', sa.Integer(), nullable=True, comment='委托人ID'),
            sa.Column('step_order', sa.Integer(), nullable=False, comment='步骤顺序'),
            sa.Column('status', sa.String(length=32), nullable=False, server_default='pending', comment='状态: pending/approved/rejected/skipped/timeout'),
            sa.Column('decision', sa.String(length=32), nullable=True, comment='决策: approve/reject'),
            sa.Column('comments', sa.Text(), nullable=True, comment='审批意见'),
            sa.Column('deadline', sa.DateTime(), nullable=True, comment='截止时间'),
            sa.Column('assigned_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.Column('processed_at', sa.DateTime(), nullable=True),
            sa.Column('is_parallel', sa.Boolean(), nullable=False, server_default=sa.text('false'), comment='是否并行审批'),
            sa.Column('parallel_group_id', sa.String(length=64), nullable=True, comment='并行组ID'),
            sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime(), nullable=True, onupdate=sa.func.now()),
            sa.ForeignKeyConstraint(['instance_id'], ['approval_instance.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['node_id'], ['workflow_node.id'], ondelete='RESTRICT'),
            sa.PrimaryKeyConstraint('id')
        )
        # Add FKs to user if present
        if 'user' in inspector.get_table_names():
            op.create_foreign_key('fk_approval_step_approver', 'approval_step', 'user', ['approver_id'], ['id'], ondelete='SET NULL')
            op.create_foreign_key('fk_approval_step_delegated_by', 'approval_step', 'user', ['delegated_by_id'], ['id'], ondelete='SET NULL')

        if 'approval_step' in inspector.get_table_names():
            existing_indexes = [i['name'] for i in inspector.get_indexes('approval_step')]
            if 'ix_approval_step_instance' not in existing_indexes:
                op.create_index('ix_approval_step_instance', 'approval_step', ['instance_id'])
            if 'ix_approval_step_approver' not in existing_indexes:
                op.create_index('ix_approval_step_approver', 'approval_step', ['approver_id', 'status'])
            if 'ix_approval_step_deadline' not in existing_indexes:
                op.create_index('ix_approval_step_deadline', 'approval_step', ['deadline'])
    
    # 5. ApprovalLog - 审批日志表
    if 'approval_log' not in inspector.get_table_names():
        op.create_table(
            'approval_log',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('instance_id', sa.Integer(), nullable=False),
            sa.Column('step_id', sa.Integer(), nullable=True),
            sa.Column('action', sa.String(length=64), nullable=False, comment='操作: start/approve/reject/transfer/cancel/timeout/auto'),
            sa.Column('actor_id', sa.Integer(), nullable=True, comment='操作人ID'),
            sa.Column('from_user_id', sa.Integer(), nullable=True, comment='转出用户ID'),
            sa.Column('to_user_id', sa.Integer(), nullable=True, comment='转入用户ID'),
            sa.Column('comments', sa.Text(), nullable=True, comment='操作备注'),
            sa.Column('ip_address', sa.String(length=64), nullable=True, comment='IP地址'),
            sa.Column('user_agent', sa.String(length=256), nullable=True, comment='User-Agent'),
            sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.ForeignKeyConstraint(['instance_id'], ['approval_instance.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['step_id'], ['approval_step.id'], ondelete='SET NULL'),
            sa.PrimaryKeyConstraint('id')
        )
        # Add FKs to user if present
        if 'user' in inspector.get_table_names():
            op.create_foreign_key('fk_approval_log_actor', 'approval_log', 'user', ['actor_id'], ['id'], ondelete='SET NULL')
            op.create_foreign_key('fk_approval_log_from_user', 'approval_log', 'user', ['from_user_id'], ['id'], ondelete='SET NULL')
            op.create_foreign_key('fk_approval_log_to_user', 'approval_log', 'user', ['to_user_id'], ['id'], ondelete='SET NULL')

        if 'approval_log' in inspector.get_table_names():
            existing_indexes = [i['name'] for i in inspector.get_indexes('approval_log')]
            if 'ix_approval_log_instance' not in existing_indexes:
                op.create_index('ix_approval_log_instance', 'approval_log', ['instance_id'])
            if 'ix_approval_log_actor' not in existing_indexes:
                op.create_index('ix_approval_log_actor', 'approval_log', ['actor_id'])
            if 'ix_approval_log_created' not in existing_indexes:
                op.create_index('ix_approval_log_created', 'approval_log', ['created_at'])
    
    # 6. ApprovalDelegate - 审批委托表
    if 'approval_delegate' not in inspector.get_table_names():
        op.create_table(
            'approval_delegate',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('delegator_id', sa.Integer(), nullable=False, comment='委托人ID'),
            sa.Column('delegate_id', sa.Integer(), nullable=False, comment='被委托人ID'),
            sa.Column('start_date', sa.DateTime(), nullable=False, comment='委托开始时间'),
            sa.Column('end_date', sa.DateTime(), nullable=False, comment='委托结束时间'),
            sa.Column('scope', sa.String(length=32), nullable=False, server_default='all', comment='委托范围: all/order_type'),
            sa.Column('order_types', sa.Text(), nullable=True, comment='委托的工单类型(JSON数组)'),
            sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true'), comment='是否启用'),
            sa.Column('reason', sa.Text(), nullable=True, comment='委托原因'),
            sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime(), nullable=True, onupdate=sa.func.now()),
            sa.PrimaryKeyConstraint('id')
        )
        if 'user' in inspector.get_table_names():
            op.create_foreign_key('fk_approval_delegate_delegator', 'approval_delegate', 'user', ['delegator_id'], ['id'], ondelete='CASCADE')
            op.create_foreign_key('fk_approval_delegate_delegate', 'approval_delegate', 'user', ['delegate_id'], ['id'], ondelete='CASCADE')

        if 'approval_delegate' in inspector.get_table_names():
            existing_indexes = [i['name'] for i in inspector.get_indexes('approval_delegate')]
            if 'ix_approval_delegate_delegator' not in existing_indexes:
                op.create_index('ix_approval_delegate_delegator', 'approval_delegate', ['delegator_id', 'is_active'])
            if 'ix_approval_delegate_date_range' not in existing_indexes:
                op.create_index('ix_approval_delegate_date_range', 'approval_delegate', ['start_date', 'end_date'])
    
    # 7. ApprovalReminder - 审批提醒表
    if 'approval_reminder' not in inspector.get_table_names():
        op.create_table(
            'approval_reminder',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('step_id', sa.Integer(), nullable=False),
            sa.Column('approver_id', sa.Integer(), nullable=False),
            sa.Column('reminder_type', sa.String(length=32), nullable=False, comment='提醒类型: deadline/overdue/escalate'),
            sa.Column('notify_method', sa.String(length=32), nullable=False, comment='通知方式: email/sms/push/site'),
            sa.Column('sent_at', sa.DateTime(), nullable=True, comment='发送时间'),
            sa.Column('status', sa.String(length=32), nullable=False, server_default='pending', comment='状态: pending/sent/failed'),
            sa.Column('error_message', sa.Text(), nullable=True, comment='错误信息'),
            sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.ForeignKeyConstraint(['step_id'], ['approval_step.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )
        if 'user' in inspector.get_table_names():
            op.create_foreign_key('fk_approval_reminder_approver', 'approval_reminder', 'user', ['approver_id'], ['id'], ondelete='CASCADE')

        if 'approval_reminder' in inspector.get_table_names():
            existing_indexes = [i['name'] for i in inspector.get_indexes('approval_reminder')]
            if 'ix_approval_reminder_step' not in existing_indexes:
                op.create_index('ix_approval_reminder_step', 'approval_reminder', ['step_id'])
            if 'ix_approval_reminder_approver' not in existing_indexes:
                op.create_index('ix_approval_reminder_approver', 'approval_reminder', ['approver_id', 'status'])


def downgrade() -> None:
    """
    回滚企业级审批系统
    """
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    
    # 按照依赖关系逆序删除表
    tables_to_drop = [
        'approval_reminder',
        'approval_delegate',
        'approval_log',
        'approval_step',
        'approval_instance',
        'workflow_template'
    ]
    
    for table_name in tables_to_drop:
        if table_name in inspector.get_table_names():
            op.drop_table(table_name)
    
    # 删除 workflow_node 新增的字段
    if 'workflow_node' in inspector.get_table_names():
        cols = [c['name'] for c in inspector.get_columns('workflow_node')]
        
        columns_to_drop = [
            'template_id',
            'node_type',
            'condition_expression',
            'parallel_mode',
            'parallel_count',
            'timeout_hours',
            'timeout_action',
            'escalate_to_user_id',
            'auto_approve_rules',
            'notify_methods'
        ]
        
        for col_name in columns_to_drop:
            if col_name in cols:
                op.drop_column('workflow_node', col_name)
