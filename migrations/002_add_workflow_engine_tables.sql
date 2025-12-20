-- 审批流引擎数据表迁移脚本
-- 执行前请先备份数据库

-- WorkflowTemplate 表
CREATE TABLE IF NOT EXISTS workflow_template (
    id SERIAL PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    order_type VARCHAR(64) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_by INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_workflow_template_order_type ON workflow_template(order_type);
CREATE INDEX IF NOT EXISTS idx_workflow_template_is_active ON workflow_template(is_active);

-- WorkflowNode 表
CREATE TABLE IF NOT EXISTS workflow_node_new (
    id SERIAL PRIMARY KEY,
    template_id INTEGER REFERENCES workflow_template(id) ON DELETE CASCADE,
    name VARCHAR(120),
    node_type VARCHAR(32),
    sequence INTEGER DEFAULT 0,
    is_parallel BOOLEAN DEFAULT FALSE,
    role_required VARCHAR(64),
    approver_user_id INTEGER,
    approver_user_ids TEXT,
    required_approvals INTEGER DEFAULT 1,
    condition_expr TEXT,
    actions_on_approve TEXT,
    actions_on_reject TEXT,
    timeout_seconds INTEGER,
    escalation_target VARCHAR(128),
    is_active BOOLEAN DEFAULT TRUE,
    metadata TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 如需迁移旧workflow_node表数据，请手动执行：
-- INSERT INTO workflow_node_new (id, name, sequence, role_required, is_active, created_at, updated_at)
-- SELECT id, name, sequence, role_required, is_active, created_at, updated_at FROM workflow_node;
-- 然后再执行：
-- DROP TABLE IF EXISTS workflow_node;

ALTER TABLE workflow_node_new RENAME TO workflow_node;

CREATE INDEX IF NOT EXISTS idx_workflow_node_template_id ON workflow_node(template_id);
CREATE INDEX IF NOT EXISTS idx_workflow_node_sequence ON workflow_node(sequence);

-- WorkflowInstance 表
CREATE TABLE IF NOT EXISTS workflow_instance (
    id SERIAL PRIMARY KEY,
    template_id INTEGER REFERENCES workflow_template(id),
    order_type VARCHAR(64) NOT NULL,
    order_id INTEGER NOT NULL,
    current_node_id INTEGER,
    status VARCHAR(32) DEFAULT 'draft',
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    finished_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_workflow_instance_order ON workflow_instance(order_type, order_id);
CREATE INDEX IF NOT EXISTS idx_workflow_instance_status ON workflow_instance(status);

-- ApprovalDecision 表（并行审批中每个审批人的决策）
CREATE TABLE IF NOT EXISTS approval_decision (
    id SERIAL PRIMARY KEY,
    approval_workflow_id INTEGER NOT NULL REFERENCES approval_workflow(id) ON DELETE CASCADE,
    approver_id INTEGER NOT NULL,
    decision VARCHAR(32),
    comments TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_approval_decision_workflow_id ON approval_decision(approval_workflow_id);
CREATE INDEX IF NOT EXISTS idx_approval_decision_approver_id ON approval_decision(approver_id);

-- ActionLog 表
CREATE TABLE IF NOT EXISTS action_log (
    id SERIAL PRIMARY KEY,
    action_name VARCHAR(120),
    workflow_node_id INTEGER,
    approval_workflow_id INTEGER,
    payload TEXT,
    status VARCHAR(32) DEFAULT 'pending',
    result TEXT,
    executed_at TIMESTAMP,
    retry_count INTEGER DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_action_log_status ON action_log(status);
CREATE INDEX IF NOT EXISTS idx_action_log_workflow_node ON action_log(workflow_node_id);

-- 扩展现有 approval_workflow 表（如果已存在，添加新字段）
-- 注意：PostgreSQL 14+ 支持 IF NOT EXISTS
-- ALTER TABLE IF EXISTS approval_workflow ADD COLUMN IF NOT EXISTS template_id INTEGER;
