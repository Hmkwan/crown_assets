"""
Enhanced Workflow Models for IT Asset Management System
仅包含新增模型：WorkflowInstance, ApprovalDecision, ActionLog
重用 models.py 中已有的：WorkflowTemplate, WorkflowNode, ApprovalWorkflow
"""
from app import db, get_beijing_now


class WorkflowInstance(db.Model):
    """Represents a workflow instance for a specific order/resource."""
    __tablename__ = 'workflow_instance'
    id = db.Column(db.Integer, primary_key=True)
    template_id = db.Column(db.Integer, db.ForeignKey('workflow_template.id'), nullable=True)
    order_type = db.Column(db.String(64), nullable=False)
    order_id = db.Column(db.Integer, nullable=False)
    current_node_id = db.Column(db.Integer, nullable=True)
    status = db.Column(db.String(32), default='draft')  # draft/pending/approved/rejected/cancelled/completed
    started_at = db.Column(db.DateTime, default=get_beijing_now)
    finished_at = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f'<WorkflowInstance {self.order_type}#{self.order_id} ({self.status})>'


class ApprovalDecision(db.Model):
    """Records individual decisions in parallel approval scenarios."""
    __tablename__ = 'approval_decision'
    id = db.Column(db.Integer, primary_key=True)
    approval_workflow_id = db.Column(db.Integer, db.ForeignKey('approval_workflow.id'))
    approver_id = db.Column(db.Integer, db.ForeignKey('app_user.id'))
    decision = db.Column(db.String(32))  # approve/reject/abstain
    comments = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=get_beijing_now)

    def __repr__(self):
        return f'<ApprovalDecision {self.approver_id} {self.decision}>'


class ActionLog(db.Model):
    """Tracks automated actions triggered by workflow transitions."""
    __tablename__ = 'action_log'
    id = db.Column(db.Integer, primary_key=True)
    action_name = db.Column(db.String(120))
    workflow_node_id = db.Column(db.Integer, nullable=True)
    approval_workflow_id = db.Column(db.Integer, nullable=True)
    payload = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(32), default='pending')
    result = db.Column(db.Text, nullable=True)
    executed_at = db.Column(db.DateTime, nullable=True)
    retry_count = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f'<ActionLog {self.action_name} status:{self.status}>'


