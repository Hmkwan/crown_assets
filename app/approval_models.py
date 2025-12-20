#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
审批流程系统 - 增强版数据模型
支持多级审批、并行审批、条件分支、自动化规则等企业级功能
"""

from app import db
from datetime import datetime, timedelta
from app.models import User
import json


class WorkflowTemplate(db.Model):
    """工作流模板 - 定义审批流程的蓝图"""
    __tablename__ = 'workflow_template'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(64), unique=True, nullable=False, index=True)  # 模板代码,如 REPAIR_WORKFLOW
    name = db.Column(db.String(128), nullable=False)  # 模板名称
    order_type = db.Column(db.String(64), nullable=False, index=True)  # 工单类型
    version = db.Column(db.Integer, default=1)  # 版本号
    is_active = db.Column(db.Boolean, default=True)  # 是否启用
    is_default = db.Column(db.Boolean, default=False)  # 是否为该类型的默认模板
    description = db.Column(db.Text)  # 模板描述
    
    # 流程配置
    config = db.Column(db.JSON)  # 流程配置JSON,包含超时设置、自动化规则等
    
    # 元数据
    created_by_id = db.Column(db.Integer, db.ForeignKey('app_user.id'))
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    updated_date = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # 关系
    nodes = db.relationship('WorkflowNode', backref='template', lazy='dynamic', 
                           cascade='all, delete-orphan')
    instances = db.relationship('ApprovalInstance', backref='template', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'order_type': self.order_type,
            'version': self.version,
            'is_active': self.is_active,
            'is_default': self.is_default,
            'description': self.description,
            'node_count': self.nodes.count(),
            'created_date': self.created_date.isoformat() if self.created_date else None
        }


class WorkflowNode(db.Model):
    """工作流节点 - 定义审批流程中的每个步骤"""
    __tablename__ = 'workflow_node'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    template_id = db.Column(db.Integer, db.ForeignKey('workflow_template.id'), nullable=False)
    
    # 节点基本信息
    code = db.Column(db.String(64), nullable=False)  # 节点代码,如 DEPT_APPROVE
    name = db.Column(db.String(128), nullable=False)  # 节点名称
    sequence = db.Column(db.Integer, nullable=False)  # 执行顺序
    node_type = db.Column(db.String(32), default='approval')  # approval/condition/parallel/auto

    # 兼容旧字段: 一些测试/脚本可能在构造时传入 order_type / role_required
    # 我们通过实例级的 override 字段来兼容这些用法，而不在模型层增加冲突的列名。
    _order_type_override = None
    _role_required_override = None

    @property
    def order_type(self):
        # 优先使用实例 override，否则回退到关联模板
        return self._order_type_override or (self.template.order_type if self.template else None)

    @order_type.setter
    def order_type(self, value):
        self._order_type_override = value

    @property
    def role_required(self):
        # 优先使用持久化字段, 其次实例 override, 最后回退到关联 approval_role 的 name
        return (getattr(self, 'role_required_name', None) or self._role_required_override or
                (self.approval_role.name if self.approval_role else None))

    @role_required.setter
    def role_required(self, value):
        # 在属性和持久字段上都写入以确保构造函数传入能被持久化
        self._role_required_override = value
        try:
            self.role_required_name = value
        except Exception:
            # 如果映射尚未就绪, 忽略
            pass
    
    # 审批角色配置
    approval_role_id = db.Column(db.Integer, db.ForeignKey('approval_role.id'))  # 审批角色
    # 持久化的角色名覆盖, 用于测试/脚本兼容
    role_required_name = db.Column(db.String(64))
    approver_user_ids = db.Column(db.Text)  # 指定审批人ID列表(JSON格式)
    
    # 条件判断
    condition_expr = db.Column(db.Text)  # 条件表达式,Python表达式
    amount_threshold = db.Column(db.Numeric(15, 2))  # 金额阈值
    skip_if_below_threshold = db.Column(db.Boolean, default=False)  # 低于阈值跳过
    
    # 并行审批配置
    is_parallel = db.Column(db.Boolean, default=False)  # 是否并行审批
    required_approvals = db.Column(db.Integer, default=1)  # 需要的审批数量(并行时)
    parallel_mode = db.Column(db.String(32))  # all/any/count - 全部通过/任一通过/达到数量
    
    # 超时设置
    timeout_hours = db.Column(db.Integer)  # 超时小时数
    timeout_action = db.Column(db.String(32))  # auto_approve/escalate/notify - 超时动作
    escalate_to_role_id = db.Column(db.Integer, db.ForeignKey('approval_role.id'))  # 升级到的角色
    
    # 自动化规则
    auto_approve_rules = db.Column(db.JSON)  # 自动通过规则
    auto_reject_rules = db.Column(db.JSON)  # 自动拒绝规则
    
    # 通知配置
    notify_on_start = db.Column(db.Boolean, default=True)  # 开始时通知
    notify_on_complete = db.Column(db.Boolean, default=True)  # 完成时通知
    notify_methods = db.Column(db.JSON)  # 通知方式: ['system', 'email', 'sms']
    
    # 状态
    is_active = db.Column(db.Boolean, default=True)
    
    # 关系
    approval_role = db.relationship('ApprovalRole', foreign_keys=[approval_role_id])
    escalate_to_role = db.relationship('ApprovalRole', foreign_keys=[escalate_to_role_id])
    # template关系已在WorkflowTemplate中通过backref定义
    

    
    def get_approver_users(self):
        """获取该节点的所有潜在审批人"""
        from app.models import User
        from app.approval_roles import UserApprovalRole
        
        if not self.approval_role:
            return []
        
        # 查找所有拥有此审批角色的用户
        assignments = UserApprovalRole.query.filter_by(
            role_id=self.approval_role_id,
            is_active=True
        ).all()
        
        # 返回有效的用户列表
        users = []
        for assignment in assignments:
            if assignment.is_valid() and assignment.user and assignment.user.is_active:
                users.append(assignment.user)
        
        return users
    
    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'sequence': self.sequence,
            'node_type': self.node_type,
            'approval_role': self.approval_role.to_dict() if self.approval_role else None,
            'is_parallel': self.is_parallel,
            'required_approvals': self.required_approvals,
            'timeout_hours': self.timeout_hours,
            'is_active': self.is_active
        }


class ApprovalInstance(db.Model):
    """审批实例 - 具体工单的审批流程实例"""
    __tablename__ = 'approval_instance'
    
    id = db.Column(db.Integer, primary_key=True)
    instance_no = db.Column(db.String(64), unique=True, nullable=False, index=True)  # 实例编号
    
    # 关联信息
    template_id = db.Column(db.Integer, db.ForeignKey('workflow_template.id'), nullable=False)
    order_type = db.Column(db.String(64), nullable=False, index=True)
    order_id = db.Column(db.Integer, nullable=False, index=True)
    
    # 申请信息
    requester_id = db.Column(db.Integer, db.ForeignKey('app_user.id'), nullable=False)
    requester_dept_id = db.Column(db.Integer, db.ForeignKey('department.id'))
    
    # 流程状态
    status = db.Column(db.String(32), default='pending', index=True)
    # pending/in_progress/approved/rejected/cancelled/terminated
    
    current_node_id = db.Column(db.Integer, db.ForeignKey('workflow_node.id'))  # 当前节点
    
    # 时间信息
    started_date = db.Column(db.DateTime, default=datetime.utcnow)
    completed_date = db.Column(db.DateTime)
    expected_complete_date = db.Column(db.DateTime)  # 预计完成时间
    
    # 流程数据
    form_data = db.Column(db.JSON)  # 表单数据快照
    context_data = db.Column(db.JSON)  # 上下文数据,用于条件判断
    
    # 审批结果
    final_result = db.Column(db.String(32))  # approved/rejected
    final_comment = db.Column(db.Text)  # 最终意见
    
    # 关系
    requester = db.relationship('User', foreign_keys=[requester_id])
    current_node = db.relationship('WorkflowNode', foreign_keys=[current_node_id])
    steps = db.relationship('ApprovalStep', backref='instance', lazy='dynamic',
                           cascade='all, delete-orphan', order_by='ApprovalStep.sequence')
    
    def to_dict(self):
        return {
            'id': self.id,
            'instance_no': self.instance_no,
            'order_type': self.order_type,
            'order_id': self.order_id,
            'status': self.status,
            'requester': self.requester.username if self.requester else None,
            'current_node': self.current_node.name if self.current_node else None,
            'started_date': self.started_date.isoformat() if self.started_date else None,
            'completed_date': self.completed_date.isoformat() if self.completed_date else None
        }


class ApprovalStep(db.Model):
    """审批步骤 - 审批实例中的每个具体审批环节"""
    __tablename__ = 'approval_step'
    
    id = db.Column(db.Integer, primary_key=True)
    instance_id = db.Column(db.Integer, db.ForeignKey('approval_instance.id'), nullable=False, index=True)
    node_id = db.Column(db.Integer, db.ForeignKey('workflow_node.id'), nullable=False)
    
    # 步骤信息
    sequence = db.Column(db.Integer, nullable=False)  # 步骤顺序
    step_no = db.Column(db.String(64))  # 步骤编号,如 STEP-001
    
    # 审批人信息
    approver_id = db.Column(db.Integer, db.ForeignKey('app_user.id'))
    approver_role_id = db.Column(db.Integer, db.ForeignKey('approval_role.id'))
    assigned_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 并行审批
    parallel_group_id = db.Column(db.String(64))  # 并行组ID
    parallel_approvers = db.Column(db.JSON)  # 并行审批人列表 [user_id1, user_id2, ...]
    approved_count = db.Column(db.Integer, default=0)  # 已审批数量
    
    # 状态
    status = db.Column(db.String(32), default='pending', index=True)
    # pending/in_progress/approved/rejected/skipped/timeout/transferred
    
    # 审批结果
    result = db.Column(db.String(32))  # approved/rejected
    comment = db.Column(db.Text)  # 审批意见
    approved_date = db.Column(db.DateTime)
    
    # 转交记录
    transferred_from_id = db.Column(db.Integer, db.ForeignKey('app_user.id'))  # 转交自
    transferred_to_id = db.Column(db.Integer, db.ForeignKey('app_user.id'))  # 转交给
    transfer_reason = db.Column(db.Text)  # 转交原因
    
    # 超时处理
    deadline = db.Column(db.DateTime)  # 截止时间
    is_timeout = db.Column(db.Boolean, default=False)
    timeout_handled_date = db.Column(db.DateTime)
    
    # 管理员干预
    admin_action = db.Column(db.String(32))  # skip/force_approve/force_reject/reassign
    admin_operator_id = db.Column(db.Integer, db.ForeignKey('app_user.id'))
    admin_comment = db.Column(db.Text)
    
    # 关系
    node = db.relationship('WorkflowNode')
    approver = db.relationship('User', foreign_keys=[approver_id])
    approver_role = db.relationship('ApprovalRole')
    transferred_from = db.relationship('User', foreign_keys=[transferred_from_id])
    transferred_to = db.relationship('User', foreign_keys=[transferred_to_id])
    admin_operator = db.relationship('User', foreign_keys=[admin_operator_id])
    
    def to_dict(self):
        return {
            'id': self.id,
            'step_no': self.step_no,
            'sequence': self.sequence,
            'node_name': self.node.name if self.node else None,
            'approver': self.approver.username if self.approver else None,
            'status': self.status,
            'result': self.result,
            'comment': self.comment,
            'assigned_date': self.assigned_date.isoformat() if self.assigned_date else None,
            'approved_date': self.approved_date.isoformat() if self.approved_date else None,
            'is_timeout': self.is_timeout
        }


class ApprovalLog(db.Model):
    """审批日志 - 记录所有审批操作,用于审计"""
    __tablename__ = 'approval_log'
    
    id = db.Column(db.Integer, primary_key=True)
    instance_id = db.Column(db.Integer, db.ForeignKey('approval_instance.id'), index=True)
    step_id = db.Column(db.Integer, db.ForeignKey('approval_step.id'), index=True)
    
    # 操作信息
    action = db.Column(db.String(64), nullable=False)  # start/approve/reject/transfer/skip/timeout等
    operator_id = db.Column(db.Integer, db.ForeignKey('app_user.id'))
    operator_role = db.Column(db.String(64))
    
    # 详细信息
    old_value = db.Column(db.JSON)  # 操作前的值
    new_value = db.Column(db.JSON)  # 操作后的值
    comment = db.Column(db.Text)
    
    # 环境信息
    ip_address = db.Column(db.String(64))
    user_agent = db.Column(db.String(512))
    created_date = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # 关系
    operator = db.relationship('User')
    
    def to_dict(self):
        return {
            'id': self.id,
            'action': self.action,
            'operator': self.operator.username if self.operator else None,
            'comment': self.comment,
            'created_date': self.created_date.isoformat() if self.created_date else None
        }


class ApprovalDelegate(db.Model):
    """审批代理 - 用户可以设置审批代理人"""
    __tablename__ = 'approval_delegate'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('app_user.id'), nullable=False)
    delegate_to_id = db.Column(db.Integer, db.ForeignKey('app_user.id'), nullable=False)
    
    # 代理范围
    order_types = db.Column(db.JSON)  # 代理的工单类型列表
    role_ids = db.Column(db.JSON)  # 代理的角色ID列表
    
    # 有效期
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    
    # 原因
    reason = db.Column(db.Text)  # 代理原因,如"出差"、"休假"
    
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    user = db.relationship('User', foreign_keys=[user_id])
    delegate_to = db.relationship('User', foreign_keys=[delegate_to_id])
    
    def is_valid(self):
        """检查代理是否在有效期内"""
        now = datetime.utcnow()
        return self.is_active and self.start_date <= now <= self.end_date


class ApprovalReminder(db.Model):
    """审批提醒记录"""
    __tablename__ = 'approval_reminder'
    
    id = db.Column(db.Integer, primary_key=True)
    step_id = db.Column(db.Integer, db.ForeignKey('approval_step.id'), nullable=False)
    
    # 提醒信息
    reminder_type = db.Column(db.String(32))  # pending/timeout/escalate
    sent_to_id = db.Column(db.Integer, db.ForeignKey('app_user.id'))
    sent_date = db.Column(db.DateTime, default=datetime.utcnow)
    send_method = db.Column(db.String(32))  # system/email/sms
    
    # 状态
    is_sent = db.Column(db.Boolean, default=False)
    sent_result = db.Column(db.Text)  # 发送结果
    
    # 关系
    step = db.relationship('ApprovalStep')
    sent_to = db.relationship('User')


