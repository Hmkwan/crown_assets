# 企业级审批流程系统 - 完整设计方案

## 一、系统架构

### 1.1 核心模型设计

#### WorkflowTemplate (工作流模板)
- 定义审批流程的蓝图
- 支持版本控制
- 支持多个模板共存,设置默认模板

#### WorkflowNode (工作流节点)
- 定义流程中的每个步骤
- 支持4种节点类型:
  - `approval`: 审批节点
  - `condition`: 条件分支
  - `parallel`: 并行审批
  - `auto`: 自动化节点

#### ApprovalInstance (审批实例)
- 具体工单的审批流程实例
- 记录流程状态和进度
- 存储表单数据快照

#### ApprovalStep (审批步骤)
- 审批实例中的具体环节
- 支持转交、代理
- 记录超时信息

#### ApprovalLog (审批日志)
- 完整的操作审计日志
- 记录IP、User Agent等环境信息
- 支持合规性审查

#### ApprovalDelegate (审批代理)
- 用户可设置代理人
- 支持按工单类型、角色范围代理
- 有效期控制

---

## 二、功能实现

### 2.1 审批流程基本设计

#### 设备申请流程
```
员工提交 → 部门负责人审批 → 资产管理员审批 → 财务审批(>5000元) → 完成
```

#### 设备借用流程
```
借用申请 → 部门负责人审批 → 设备管理员确认 → 完成
```

#### 设备调拨流程
```
调拨申请 → 调出部门审批 → 资产管理员审批 → 调入部门确认 → 完成
```

#### 设备报废流程
```
报废申请 → 部门负责人审批 → 技术评估 → 资产管理员审批 → 财务审批 → 完成
```

### 2.2 权限控制

#### 角色分配与权限
```python
# 审批角色包含:
- 基本权限: can_approve_xxx (各种工单类型)
- 金额限制: max_approval_amount
- 部门范围: department_scope
- 角色级别: level (用于升级)
```

#### 多级审批
```python
# 节点按sequence顺序执行
# 支持条件跳过(基于金额、部门等)
# 支持并行审批(多人同时审批)
```

#### 审批依赖关系
```python
# 通过sequence控制执行顺序
# 通过condition_expr设置前置条件
# 支持分支和汇聚
```

### 2.3 状态跟踪与流程控制

#### 流程状态
- `pending`: 待启动
- `in_progress`: 进行中
- `approved`: 已批准
- `rejected`: 已拒绝
- `cancelled`: 已取消
- `terminated`: 已终止

#### 步骤状态
- `pending`: 待审批
- `in_progress`: 审批中
- `approved`: 已通过
- `rejected`: 已拒绝
- `skipped`: 已跳过
- `timeout`: 已超时
- `transferred`: 已转交

#### 超时处理
```python
# 配置timeout_hours
# 超时动作:
- auto_approve: 自动通过
- escalate: 升级到上级
- notify: 仅通知
```

#### 审批历史记录
```python
# ApprovalLog表记录所有操作:
- 审批人、时间、结果、意见
- 转交记录
- 管理员干预记录
- IP地址、User Agent
```

### 2.4 审批通知与提醒

#### 通知机制
```python
# 支持多种通知方式:
- system: 站内消息
- email: 邮件通知
- sms: 短信通知(预留)

# 通知时机:
- 分配审批任务时
- 审批完成时
- 即将超时时(deadline前24小时)
- 超时后
```

#### ApprovalReminder (提醒记录)
```python
# 记录所有提醒发送情况
# 避免重复提醒
# 跟踪提醒效果
```

---

## 三、关键问题解决方案

### 3.1 流程可视化

#### 流程图展示
```javascript
// 使用vis.js或D3.js绘制流程图
// 显示:
- 节点名称、类型
- 当前进度
- 审批人
- 时间信息
```

#### 进度跟踪
```python
# 实时显示:
- 已完成步骤
- 当前步骤
- 待执行步骤
- 预计完成时间
```

### 3.2 灵活性与扩展性

#### 流程模板管理
```python
# 管理员可:
- 创建新模板
- 编辑模板(创建新版本)
- 激活/停用模板
- 设置默认模板
```

#### 节点配置
```python
# 每个节点可配置:
- 审批角色
- 超时设置
- 通知方式
- 条件表达式
- 并行审批规则
```

### 3.3 异常处理

#### 审批人不在
```python
# 解决方案:
1. 审批代理(ApprovalDelegate)
2. 超时自动升级(escalate_to_role)
3. 管理员强制分配
```

#### 审批人拒绝
```python
# 解决方案:
1. 打回到申请人修改
2. 终止流程
3. 跳转到指定节点重新审批
```

#### 流程异常
```python
# 管理员可:
- 跳过当前节点
- 强制通过/拒绝
- 重新分配审批人
- 终止流程
```

### 3.4 合规性和审计

#### 完整日志
```python
# ApprovalLog记录:
- 所有操作(启动、审批、转交、干预)
- 操作人、时间、IP地址
- 操作前后的值变化
- 审批意见
```

#### 数据归档
```python
# 定期归档:
- 已完成的流程实例
- 审批历史记录
- 保留指定期限(如7年)
```

#### 审计报告
```python
# 可生成:
- 审批效率报告
- 异常审批报告
- 用户审批统计
- 流程合规报告
```

---

## 四、预留功能

### 4.1 流程模板管理
```python
# 已实现:
- 模板CRUD
- 版本控制(version字段)
- 激活/停用
- 默认模板设置

# 未来扩展:
- 模板导入/导出
- 模板克隆
- 模板继承
```

### 4.2 流程版本控制
```python
# WorkflowTemplate.version字段
# 修改模板时:
1. 复制当前模板
2. 增加版本号
3. 修改新版本
4. 旧版本实例继续使用旧模板
5. 新实例使用新模板
```

### 4.3 审批权限自定义
```python
# 已支持:
- 基于角色的权限控制
- 金额阈值控制
- 部门范围控制

# 未来扩展:
- 动态权限计算
- 基于属性的访问控制(ABAC)
- 委托授权
```

### 4.4 自动化审批
```python
# WorkflowNode.auto_approve_rules
# 配置自动通过规则:
{
  "conditions": [
    {"field": "amount", "operator": "<", "value": 1000},
    {"field": "requester.level", "operator": ">=", "value": 3}
  ],
  "logic": "AND"  # AND/OR
}

# 满足条件时自动通过,无需人工审批
```

---

## 五、数据库迁移

### 5.1 新增表

```sql
-- 工作流模板
CREATE TABLE workflow_template (
    id INTEGER PRIMARY KEY,
    code VARCHAR(64) UNIQUE NOT NULL,
    name VARCHAR(128) NOT NULL,
    order_type VARCHAR(64) NOT NULL,
    version INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT TRUE,
    is_default BOOLEAN DEFAULT FALSE,
    description TEXT,
    config JSON,
    created_by_id INTEGER,
    created_date DATETIME,
    updated_date DATETIME
);

-- 工作流节点
CREATE TABLE workflow_node (
    id INTEGER PRIMARY KEY,
    template_id INTEGER NOT NULL,
    code VARCHAR(64) NOT NULL,
    name VARCHAR(128) NOT NULL,
    sequence INTEGER NOT NULL,
    node_type VARCHAR(32) DEFAULT 'approval',
    approval_role_id INTEGER,
    condition_expr TEXT,
    amount_threshold DECIMAL(15,2),
    skip_if_below_threshold BOOLEAN DEFAULT FALSE,
    is_parallel BOOLEAN DEFAULT FALSE,
    required_approvals INTEGER DEFAULT 1,
    parallel_mode VARCHAR(32),
    timeout_hours INTEGER,
    timeout_action VARCHAR(32),
    escalate_to_role_id INTEGER,
    auto_approve_rules JSON,
    auto_reject_rules JSON,
    notify_on_start BOOLEAN DEFAULT TRUE,
    notify_on_complete BOOLEAN DEFAULT TRUE,
    notify_methods JSON,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (template_id) REFERENCES workflow_template(id),
    FOREIGN KEY (approval_role_id) REFERENCES approval_role(id)
);

-- 审批实例
CREATE TABLE approval_instance (
    id INTEGER PRIMARY KEY,
    instance_no VARCHAR(64) UNIQUE NOT NULL,
    template_id INTEGER NOT NULL,
    order_type VARCHAR(64) NOT NULL,
    order_id INTEGER NOT NULL,
    requester_id INTEGER NOT NULL,
    requester_dept_id INTEGER,
    status VARCHAR(32) DEFAULT 'pending',
    current_node_id INTEGER,
    started_date DATETIME,
    completed_date DATETIME,
    expected_complete_date DATETIME,
    form_data JSON,
    context_data JSON,
    final_result VARCHAR(32),
    final_comment TEXT,
    FOREIGN KEY (template_id) REFERENCES workflow_template(id),
    FOREIGN KEY (requester_id) REFERENCES user(id),
    FOREIGN KEY (current_node_id) REFERENCES workflow_node(id)
);

-- 审批步骤
CREATE TABLE approval_step (
    id INTEGER PRIMARY KEY,
    instance_id INTEGER NOT NULL,
    node_id INTEGER NOT NULL,
    sequence INTEGER NOT NULL,
    step_no VARCHAR(64),
    approver_id INTEGER,
    approver_role_id INTEGER,
    assigned_date DATETIME,
    parallel_group_id VARCHAR(64),
    parallel_approvers JSON,
    approved_count INTEGER DEFAULT 0,
    status VARCHAR(32) DEFAULT 'pending',
    result VARCHAR(32),
    comment TEXT,
    approved_date DATETIME,
    transferred_from_id INTEGER,
    transferred_to_id INTEGER,
    transfer_reason TEXT,
    deadline DATETIME,
    is_timeout BOOLEAN DEFAULT FALSE,
    timeout_handled_date DATETIME,
    admin_action VARCHAR(32),
    admin_operator_id INTEGER,
    admin_comment TEXT,
    FOREIGN KEY (instance_id) REFERENCES approval_instance(id),
    FOREIGN KEY (node_id) REFERENCES workflow_node(id),
    FOREIGN KEY (approver_id) REFERENCES user(id)
);

-- 审批日志
CREATE TABLE approval_log (
    id INTEGER PRIMARY KEY,
    instance_id INTEGER,
    step_id INTEGER,
    action VARCHAR(64) NOT NULL,
    operator_id INTEGER,
    operator_role VARCHAR(64),
    old_value JSON,
    new_value JSON,
    comment TEXT,
    ip_address VARCHAR(64),
    user_agent VARCHAR(512),
    created_date DATETIME,
    FOREIGN KEY (instance_id) REFERENCES approval_instance(id),
    FOREIGN KEY (step_id) REFERENCES approval_step(id)
);

-- 审批代理
CREATE TABLE approval_delegate (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    delegate_to_id INTEGER NOT NULL,
    order_types JSON,
    role_ids JSON,
    start_date DATETIME NOT NULL,
    end_date DATETIME NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    reason TEXT,
    created_date DATETIME,
    FOREIGN KEY (user_id) REFERENCES user(id),
    FOREIGN KEY (delegate_to_id) REFERENCES user(id)
);

-- 审批提醒
CREATE TABLE approval_reminder (
    id INTEGER PRIMARY KEY,
    step_id INTEGER NOT NULL,
    reminder_type VARCHAR(32),
    sent_to_id INTEGER,
    sent_date DATETIME,
    send_method VARCHAR(32),
    is_sent BOOLEAN DEFAULT FALSE,
    sent_result TEXT,
    FOREIGN KEY (step_id) REFERENCES approval_step(id),
    FOREIGN KEY (sent_to_id) REFERENCES user(id)
);
```

### 5.2 索引优化

```sql
-- 高频查询字段添加索引
CREATE INDEX idx_approval_instance_order ON approval_instance(order_type, order_id);
CREATE INDEX idx_approval_instance_status ON approval_instance(status);
CREATE INDEX idx_approval_step_instance ON approval_step(instance_id);
CREATE INDEX idx_approval_step_approver ON approval_step(approver_id, status);
CREATE INDEX idx_approval_log_instance ON approval_log(instance_id, created_date);
```

---

## 六、实施步骤

### 第一阶段: 核心模型 (已完成)
- [x] 创建approval_models.py
- [x] 创建approval_engine.py
- [ ] 数据库迁移
- [ ] 单元测试

### 第二阶段: API接口
- [ ] 流程启动API
- [ ] 审批操作API
- [ ] 流程查询API
- [ ] 管理后台API

### 第三阶段: 前端界面
- [ ] 流程可视化组件
- [ ] 审批操作界面
- [ ] 流程管理后台
- [ ] 移动端适配

### 第四阶段: 高级功能
- [ ] 通知系统集成
- [ ] 自动化规则引擎
- [ ] 报表统计
- [ ] 性能优化

---

## 七、使用示例

### 7.1 启动审批流程

```python
from app.approval_engine import ApprovalEngine

# 创建维修工单后,启动审批流程
instance = ApprovalEngine.start_workflow(
    order_type='repair_order',
    order_id=repair_order.id,
    requester_id=current_user.id,
    form_data={
        'equipment_id': equipment.id,
        'fault_description': description,
        'estimated_cost': 5000.0
    }
)
```

### 7.2 审批操作

```python
# 审批通过
result = ApprovalEngine.approve_step(
    step_id=step.id,
    approver_id=current_user.id,
    comment='同意维修,金额合理'
)

# 审批拒绝
result = ApprovalEngine.reject_step(
    step_id=step.id,
    approver_id=current_user.id,
    comment='维修金额过高,需重新评估'
)
```

### 7.3 查询我的待审批

```python
# 查询待审批步骤
pending_steps = ApprovalStep.query.filter_by(
    approver_id=current_user.id,
    status='pending'
).order_by(ApprovalStep.assigned_date).all()
```

---

## 八、总结

这是一个企业级的审批流程系统,具有以下特点:

1. **完整性**: 覆盖审批流程的全生命周期
2. **灵活性**: 支持多种审批模式和自定义规则
3. **可扩展性**: 模块化设计,易于添加新功能
4. **合规性**: 完整的审计日志和权限控制
5. **用户友好**: 清晰的流程可视化和通知机制

下一步需要:
1. 执行数据库迁移
2. 开发REST API
3. 构建前端界面
4. 集成到现有系统
5. 测试和优化
