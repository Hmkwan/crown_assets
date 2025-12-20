# 审批流引擎快速使用指南

## 🎯 5分钟快速开始

### 1. 查看已有流程模板

```bash
# 方法1：使用 Python 脚本
python -c "from app import create_app, db; from app.models import WorkflowTemplate; app = create_app(); app.app_context().push(); [print(f'{t.id}. {t.name} ({t.order_type})') for t in WorkflowTemplate.query.all()]"

# 方法2：使用 API（需要先启动服务器）
curl http://localhost:5000/api/v1/workflow/templates
```

**输出示例**：
```
1. 标准维修工单流程 (repair_order)
2. 标准配件申请流程 (part_request_order)
3. 设备申请流程（新购/补件-企业级） (equipment_application)
4. 设备借用流程 (equipment_loan)
5. 设备调拨流程 (equipment_transfer)
6. 设备报废流程 (equipment_scrap)
7. 高额采购并行审批流程 (high_value_procurement)
8. 权限申请流程 (permission_request)
9. 设备报废流程（企业级） (equipment_scrap_enhanced)
```

### 2. 查看流程详情

```python
from app import create_app, db
from app.models import WorkflowTemplate, WorkflowNode

app = create_app()
with app.app_context():
    # 查询企业级设备申请流程
    template = WorkflowTemplate.query.filter_by(order_type='equipment_application').first()
    nodes = WorkflowNode.query.filter_by(template_id=template.id).order_by(WorkflowNode.sequence).all()
    
    print(f"流程: {template.name}")
    print(f"节点数: {len(nodes)}\n")
    
    for node in nodes:
        print(f"{node.sequence}. {node.name}")
        print(f"   类型: {node.node_type}")
        print(f"   角色: {node.role_required or '自动'}")
        if node.timeout_seconds:
            print(f"   超时: {node.timeout_seconds//86400} 天")
        print()
```

**输出示例**：
```
流程: 设备申请流程（新购/补件-企业级）
节点数: 8

1. 直属主管审批
   类型: approval
   角色: department_head
   超时: 2 天

2. IT资产管理员审核
   类型: approval
   角色: admin
   超时: 3 天

3. 采购评估与报价
   类型: approval
   角色: procurement
   超时: 5 天

4. 金额阈值检查
   类型: condition
   角色: 自动

5. 财务预算确认
   类型: approval
   角色: finance
   超时: 3 天

...
```

### 3. API 使用示例

#### 3.1 查询流程模板

```bash
# GET /api/v1/workflow/templates
curl -X GET http://localhost:5000/api/v1/workflow/templates

# 响应示例
{
  "templates": [
    {
      "id": 3,
      "name": "设备申请流程（新购/补件-企业级）",
      "order_type": "equipment_application",
      "is_active": true,
      "node_count": 8
    },
    ...
  ]
}
```

#### 3.2 启动审批流程

```bash
# POST /api/v1/workflow/start
curl -X POST http://localhost:5000/api/v1/workflow/start \
  -H "Content-Type: application/json" \
  -d '{
    "order_type": "equipment_application",
    "order_id": 123,
    "template_id": 3,
    "initiator_id": 5
  }'

# 响应示例
{
  "success": true,
  "instance_id": 456,
  "current_node": "直属主管审批",
  "pending_approver": "张经理"
}
```

#### 3.3 执行审批操作

```bash
# POST /api/v1/workflow/approve
curl -X POST http://localhost:5000/api/v1/workflow/approve \
  -H "Content-Type: application/json" \
  -d '{
    "approval_id": 789,
    "comments": "同意申请，预算充足",
    "decision": "approve"
  }'

# 响应示例
{
  "success": true,
  "next_node": "IT资产管理员审核",
  "next_approver": "李管理员",
  "workflow_status": "in_progress"
}
```

#### 3.4 查询待审批事项

```bash
# GET /api/v1/workflow/pending
curl -X GET http://localhost:5000/api/v1/workflow/pending

# 响应示例
{
  "pending_approvals": [
    {
      "id": 789,
      "order_type": "equipment_application",
      "order_id": 123,
      "node_name": "直属主管审批",
      "created_at": "2024-01-15T10:00:00",
      "timeout_at": "2024-01-17T10:00:00"
    },
    ...
  ]
}
```

## 🔄 典型业务流程

### 流程1：设备新购（金额 > 5000元）

```
步骤1: 员工提交设备申请
  POST /api/v1/workflow/start
  {
    "order_type": "equipment_application",
    "order_id": 123,
    "template_id": 3
  }

步骤2: 部门经理审批
  POST /api/v1/workflow/approve
  {
    "approval_id": xxx,
    "decision": "approve",
    "comments": "同意购买"
  }

步骤3: IT管理员审核
  POST /api/v1/workflow/approve
  {
    "approval_id": xxx,
    "decision": "approve"
  }

步骤4: 采购评估
  POST /api/v1/workflow/approve
  {
    "approval_id": xxx,
    "decision": "approve",
    "metadata": {"estimated_price": 6000}
  }

步骤5: 系统自动判断（金额>5000）→ 进入财务审核

步骤6: 财务确认
  POST /api/v1/workflow/approve
  {
    "approval_id": xxx,
    "decision": "approve"
  }

步骤7: 总经理审批
  POST /api/v1/workflow/approve
  {
    "approval_id": xxx,
    "decision": "approve"
  }

步骤8: 系统自动下单（auto节点）

步骤9: IT分配设备
  POST /api/v1/workflow/approve
  {
    "approval_id": xxx,
    "decision": "approve",
    "metadata": {"device_serial": "ABC123"}
  }
```

### 流程2：权限申请

```
员工 → 部门经理 → IT审核 → 安全审核 → IT授权

POST /api/v1/workflow/start
{
  "order_type": "permission_request",
  "order_id": 456,
  "template_id": 8
}

# 4步审批后完成
```

### 流程3：设备报废（企业级）

```
IT提交 → 部门确认 → 安全审核 → 财务评估 → 高层审批 → 审计留档

POST /api/v1/workflow/start
{
  "order_type": "equipment_scrap_enhanced",
  "order_id": 789,
  "template_id": 9
}

# 6步审批，涉及6个不同角色
```

## 📊 数据查询

### 查询流程实例状态

```python
from app.workflow_models_new import WorkflowInstance

# 查询某个订单的流程实例
instance = WorkflowInstance.query.filter_by(
    order_type='equipment_application',
    order_id=123
).first()

print(f"状态: {instance.status}")
print(f"当前节点: {instance.current_node_id}")
print(f"开始时间: {instance.started_at}")
```

### 查询审批历史

```python
from app.models import ApprovalWorkflow

# 查询某个订单的所有审批记录
approvals = ApprovalWorkflow.query.filter_by(
    order_type='equipment_application',
    order_id=123
).order_by(ApprovalWorkflow.created_at).all()

for approval in approvals:
    print(f"{approval.approval_level}: {approval.status}")
    print(f"  审批人: {approval.approver.username if approval.approver else '未分配'}")
    print(f"  时间: {approval.created_at}")
    print(f"  意见: {approval.comments}")
```

### 统计审批效率

```python
from sqlalchemy import func
from datetime import datetime, timedelta

# 统计最近30天的审批平均耗时
recent_approvals = ApprovalWorkflow.query.filter(
    ApprovalWorkflow.created_at >= datetime.now() - timedelta(days=30),
    ApprovalWorkflow.acted_at.isnot(None)
).all()

total_time = sum([
    (a.acted_at - a.created_at).total_seconds() / 3600
    for a in recent_approvals
])

avg_hours = total_time / len(recent_approvals) if recent_approvals else 0
print(f"平均审批耗时: {avg_hours:.1f} 小时")
```

## ⚙️ 配置与扩展

### 创建自定义流程模板

```python
from app import db
from app.models import WorkflowTemplate, WorkflowNode

# 创建模板
custom_template = WorkflowTemplate(
    name='自定义流程',
    order_type='custom_process',
    description='我的自定义审批流程',
    is_active=True,
    created_by_id=1
)
db.session.add(custom_template)
db.session.flush()

# 添加节点
node1 = WorkflowNode(
    template_id=custom_template.id,
    name='第一步审批',
    node_type='approval',
    role_required='department_head',
    sequence=1,
    timeout_seconds=86400 * 2  # 2天
)

node2 = WorkflowNode(
    template_id=custom_template.id,
    name='第二步审批',
    node_type='approval',
    role_required='admin',
    sequence=2,
    timeout_seconds=86400 * 3  # 3天
)

db.session.add_all([node1, node2])
db.session.commit()

print(f"✓ 创建流程模板: {custom_template.id}")
```

### 配置并行审批

```python
# 财务+法务并行审批示例
parallel_node = WorkflowNode(
    template_id=template_id,
    name='财务和法务并行审批',
    node_type='parallel',
    approver_user_ids='[3, 5]',  # 财务ID:3, 法务ID:5
    is_parallel=True,
    required_approvals=2,  # 都需要通过
    sequence=4
)
```

### 配置条件分支

```python
# 基于金额的条件分支
condition_node = WorkflowNode(
    template_id=template_id,
    name='金额阈值检查',
    node_type='condition',
    condition_expr='amount > 5000',  # 条件表达式
    actions_on_approve='{"next_node": 5}',  # 金额>5000 → 节点5（财务）
    actions_on_reject='{"next_node": 7}',   # 金额≤5000 → 节点7（采购）
    sequence=4
)
```

## 🐛 常见问题

### Q1: 如何重置流程？

```python
# 取消当前流程
instance.status = 'cancelled'
instance.finished_at = datetime.now()
db.session.commit()

# 重新启动
POST /api/v1/workflow/start {...}
```

### Q2: 如何处理审批超时？

```python
# 查询超时的审批
from datetime import datetime, timedelta

timeout_approvals = ApprovalWorkflow.query.filter(
    ApprovalWorkflow.status == 'pending',
    ApprovalWorkflow.created_at < datetime.now() - timedelta(days=3)
).all()

# 升级处理
for approval in timeout_approvals:
    node = WorkflowNode.query.get(approval.node_id)
    if node.escalation_target:
        # 分配给升级目标
        ...
```

### Q3: 如何查看流程执行日志？

```python
from app.workflow_models_new import ActionLog

logs = ActionLog.query.filter_by(
    approval_workflow_id=approval_id
).order_by(ActionLog.executed_at).all()

for log in logs:
    print(f"{log.executed_at}: {log.action_name} - {log.status}")
```

## 📚 相关文档

- **技术规格书**: `docs/workflow_spec.md`
- **角色配置指南**: `docs/workflow_roles_and_templates.md`
- **实现报告**: `docs/workflow_implementation_report.md`
- **API 文档**: `app/workflow_routes.py` (代码注释)

## 🚀 下一步

1. **前端集成**: 在管理界面添加流程设计器
2. **实时通知**: 集成 WebSocket 实时推送审批通知
3. **移动端**: 开发移动审批界面
4. **数据迁移**: 将现有审批数据迁移到新引擎

---

**快速链接**:
- 初始化脚本: `python scripts/init_workflow_templates.py`
- 测试脚本: `python scripts/test_workflow_engine.py`
- 数据库: `app.db`
