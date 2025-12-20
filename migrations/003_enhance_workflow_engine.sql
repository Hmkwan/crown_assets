-- 为 WorkflowNode 添加新字段以支持审批流引擎
-- Migration 003: Enhance WorkflowNode for Workflow Engine

ALTER TABLE workflow_node ADD COLUMN template_id INTEGER;
ALTER TABLE workflow_node ADD COLUMN node_type VARCHAR(32);
ALTER TABLE workflow_node ADD COLUMN actions_on_approve TEXT;
ALTER TABLE workflow_node ADD COLUMN condition_expr TEXT;
ALTER TABLE workflow_node ADD COLUMN timeout_seconds INTEGER;
ALTER TABLE workflow_node ADD COLUMN escalation_target VARCHAR(128);

-- 创建新表：workflow_instance (流程实例)
CREATE TABLE IF NOT EXISTS workflow_instance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    template_id INTEGER,
    order_type VARCHAR(64) NOT NULL,
    order_id INTEGER NOT NULL,
    current_node_id INTEGER,
    status VARCHAR(32) DEFAULT 'draft',
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    finished_at TIMESTAMP,
    FOREIGN KEY (template_id) REFERENCES workflow_template(id)
);

-- 创建新表：approval_decision (审批决策，用于并行审批)
CREATE TABLE IF NOT EXISTS approval_decision (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    approval_workflow_id INTEGER,
    approver_id INTEGER,
    decision VARCHAR(32),
    comments TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (approval_workflow_id) REFERENCES approval_workflow(id),
    FOREIGN KEY (approver_id) REFERENCES user(id)
);

-- 创建新表：action_log (自动动作日志)
CREATE TABLE IF NOT EXISTS action_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    action_name VARCHAR(120),
    workflow_node_id INTEGER,
    approval_workflow_id INTEGER,
    payload TEXT,
    status VARCHAR(32) DEFAULT 'pending',
    result TEXT,
    executed_at TIMESTAMP,
    retry_count INTEGER DEFAULT 0
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_workflow_instance_order ON workflow_instance(order_type, order_id);
CREATE INDEX IF NOT EXISTS idx_approval_decision_workflow ON approval_decision(approval_workflow_id);
CREATE INDEX IF NOT EXISTS idx_action_log_workflow ON action_log(approval_workflow_id);
