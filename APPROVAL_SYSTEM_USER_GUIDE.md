# 企业级审批系统使用手册

## 📋 目录
- [系统概述](#系统概述)
- [快速开始](#快速开始)
- [核心功能](#核心功能)
- [API文档](#api文档)
- [定时任务](#定时任务)
- [故障排查](#故障排查)

## 系统概述

企业级审批系统是一个功能完善的工作流审批平台,支持:
- ✅ 多级审批流程
- ✅ 并行审批
- ✅ 条件分支
- ✅ 超时处理
- ✅ 审批委托
- ✅ 自动审批规则
- ✅ 完整审计日志

## 快速开始

### 1. 数据库迁移

```bash
# 执行迁移脚本
python migrate_approval_system.py

# 修复表结构(如需要)
python fix_workflow_template_schema.py
```

### 2. 初始化审批模板

```bash
# 创建默认审批模板
python init_approval_templates.py
```

### 3. 启动应用

```bash
# 开发环境
python app.py

# 生产环境
gunicorn -w 4 -b 0.0.0.0:5020 wsgi:app
```

### 4. 配置定时任务

Windows:
```powershell
# 查看crontab_approval.txt中的PowerShell脚本
# 使用任务计划程序创建定时任务
```

Linux:
```bash
# 编辑crontab
crontab -e

# 添加定时任务(参考crontab_approval.txt)
```

## 核心功能

### 1. 审批流程

#### 发起审批
```python
from app.approval_engine import ApprovalEngine

# 启动工作流
instance = ApprovalEngine.start_workflow(
    order_type='repair_order',
    order_id=123,
    requester_id=current_user.id,
    form_data={'total_cost': 5000}
)
```

#### 审批操作
```python
# 通过
ApprovalEngine.approve_step(
    step_id=step.id,
    approver_id=current_user.id,
    comment='同意'
)

# 拒绝
ApprovalEngine.reject_step(
    step_id=step.id,
    approver_id=current_user.id,
    comment='不同意,理由是...'
)
```

### 2. 审批委托

```python
from app.approval_models import ApprovalDelegate

# 创建委托
delegate = ApprovalDelegate(
    delegator_id=current_user.id,
    delegate_to_id=target_user.id,
    start_date=datetime.now(),
    end_date=datetime.now() + timedelta(days=7),
    scope='all',  # 或 'order_type'
    order_types=['repair_order'],  # scope为order_type时必填
    reason='出差期间委托'
)
db.session.add(delegate)
db.session.commit()
```

### 3. 查询待审批

#### 前端页面
访问: `/my_pending_approvals`

#### API查询
```bash
GET /api/approval/my-pending?page=1&per_page=20
```

### 4. 工作流配置

#### 创建模板
```python
template = WorkflowTemplate(
    code='custom_workflow_v1',
    name='自定义工作流',
    order_type='custom_order',
    version=1,
    is_active=True,
    is_default=True
)
db.session.add(template)
```

#### 添加节点
```python
# 普通审批节点
node1 = WorkflowNode(
    template_id=template.id,
    code='DEPT_APPROVE',
    name='部门审批',
    sequence=1,
    node_type='approval',
    approval_role_id=role.id,
    timeout_hours=24,
    timeout_action='escalate'
)

# 条件节点
node2 = WorkflowNode(
    template_id=template.id,
    code='AMOUNT_CHECK',
    name='金额检查',
    sequence=2,
    node_type='condition',
    condition_expr="context.get('total_cost', 0) > 10000"
)

# 并行审批节点
node3 = WorkflowNode(
    template_id=template.id,
    code='PARALLEL_APPROVE',
    name='并行审批',
    sequence=3,
    node_type='parallel',
    is_parallel=True,
    parallel_mode='all',  # all/any/count
    required_approvals=2
)
```

## API文档

### 启动工作流
```
POST /api/approval/start
Content-Type: application/json

{
    "order_type": "repair_order",
    "order_id": 123,
    "template_code": "repair_workflow_v1"  // 可选
}

Response:
{
    "success": true,
    "message": "审批流程已启动",
    "data": {
        "instance_id": 1,
        "status": "in_progress",
        "current_node": "部门审批"
    }
}
```

### 审批通过
```
POST /api/approval/approve/{step_id}
Content-Type: application/json

{
    "comments": "同意",
    "ip_address": "192.168.1.100",
    "user_agent": "Mozilla/5.0..."
}

Response:
{
    "success": true,
    "message": "审批通过",
    "data": {
        "instance_status": "approved",
        "next_node": null,
        "is_completed": true
    }
}
```

### 审批拒绝
```
POST /api/approval/reject/{step_id}
Content-Type: application/json

{
    "comments": "不同意,理由是...",
    "ip_address": "192.168.1.100",
    "user_agent": "Mozilla/5.0..."
}

Response:
{
    "success": true,
    "message": "审批已拒绝",
    "data": {
        "instance_status": "rejected",
        "is_completed": true
    }
}
```

### 查询待审批
```
GET /api/approval/my-pending?page=1&per_page=20

Response:
{
    "success": true,
    "data": {
        "items": [
            {
                "step_id": 1,
                "instance_id": 1,
                "order_type": "repair_order",
                "order_id": 123,
                "node_name": "部门审批",
                "initiator": "张三",
                "deadline": "2025-12-04T10:00:00",
                "is_overdue": false,
                "assigned_at": "2025-12-03T10:00:00",
                "is_parallel": false
            }
        ],
        "total": 5,
        "page": 1,
        "per_page": 20,
        "pages": 1
    }
}
```

### 查询审批实例详情
```
GET /api/approval/instance/{instance_id}

Response:
{
    "success": true,
    "data": {
        "id": 1,
        "order_type": "repair_order",
        "order_id": 123,
        "status": "in_progress",
        "initiator": "张三",
        "current_node": "财务审批",
        "started_at": "2025-12-03T10:00:00",
        "completed_at": null,
        "steps": [
            {
                "id": 1,
                "node_name": "部门审批",
                "approver": "李四",
                "status": "approved",
                "decision": "approve",
                "comments": "同意",
                "assigned_at": "2025-12-03T10:00:00",
                "processed_at": "2025-12-03T11:00:00",
                "deadline": null,
                "is_parallel": false
            }
        ],
        "logs": [
            {
                "action": "start",
                "actor": "张三",
                "comments": "流程启动",
                "created_at": "2025-12-03T10:00:00"
            }
        ]
    }
}
```

### 创建委托
```
POST /api/approval/delegate
Content-Type: application/json

{
    "delegate_id": 5,
    "start_date": "2025-01-15T00:00:00",
    "end_date": "2025-01-20T23:59:59",
    "scope": "all",
    "order_types": [],
    "reason": "出差期间委托"
}

Response:
{
    "success": true,
    "message": "委托创建成功",
    "data": {
        "delegate_id": 1
    }
}
```

### 取消委托
```
DELETE /api/approval/delegate/{delegate_id}

Response:
{
    "success": true,
    "message": "委托已取消"
}
```

### 转交审批(管理员)
```
POST /api/approval/transfer/{step_id}
Content-Type: application/json

{
    "to_user_id": 10,
    "reason": "原审批人请假"
}

Response:
{
    "success": true,
    "message": "转交成功"
}
```

## 定时任务

### 超时检查
```bash
python app/tasks/approval_tasks.py timeout
```
- 频率: 每5分钟
- 功能: 检查超时审批并执行超时动作(自动通过/拒绝/升级/通知)

### 截止提醒
```bash
python app/tasks/approval_tasks.py reminder
```
- 频率: 每小时
- 功能: 发送即将到期提醒(24小时内)

### 自动审批
```bash
python app/tasks/approval_tasks.py auto_approve
```
- 频率: 每10分钟
- 功能: 根据规则自动审批

### 清理通知
```bash
python app/tasks/approval_tasks.py cleanup
```
- 频率: 每天凌晨2点
- 功能: 清理30天前的已读通知

### 生成统计
```bash
python app/tasks/approval_tasks.py stats
```
- 频率: 每天凌晨3点
- 功能: 生成审批统计报告

### 运行所有任务
```bash
python app/tasks/approval_tasks.py all
```

## 故障排查

### 1. 审批不自动流转
- 检查节点配置是否正确
- 检查审批角色分配
- 查看日志: `approval_instance` 和 `approval_log` 表

### 2. 通知未发送
- 确认通知服务已启用
- 检查 `approval_reminder` 表
- 确认定时任务正常运行

### 3. 超时未处理
- 确认定时任务已配置并运行
- 检查节点的 `timeout_action` 配置
- 查看日志文件

### 4. 委托未生效
- 检查委托时间范围
- 确认委托状态为active
- 检查委托范围配置

### 5. 并行审批问题
- 确认 `parallel_mode` 配置正确
- 检查 `required_approvals` 数量
- 查看 `parallel_group_id` 是否一致

## 日志查看

### 数据库日志
```sql
-- 查看审批日志
SELECT * FROM approval_log WHERE instance_id = 1 ORDER BY created_at DESC;

-- 查看审批步骤
SELECT * FROM approval_step WHERE instance_id = 1 ORDER BY sequence;

-- 查看提醒记录
SELECT * FROM approval_reminder WHERE step_id = 1;
```

### 应用日志
```bash
# 超时处理日志
tail -f logs/approval_timeout.log

# 提醒日志
tail -f logs/approval_reminder.log

# 自动审批日志
tail -f logs/approval_auto.log
```

## 性能优化

### 1. 数据库索引
已创建的索引:
- `approval_instance`: order_type, order_id, status, initiator_id
- `approval_step`: instance_id, approver_id+status, deadline
- `approval_log`: instance_id, actor_id, created_at

### 2. 查询优化
- 使用分页查询
- 避免N+1查询
- 使用 `joinedload` 预加载关联

### 3. 缓存策略
- 审批模板缓存
- 用户角色缓存
- 工作流节点缓存

## 扩展开发

### 自定义节点类型
```python
# 在 ApprovalEngine._execute_node 中添加新类型
if node.node_type == 'custom':
    # 自定义逻辑
    pass
```

### 自定义通知渠道
```python
# 在 ApprovalNotificationService 中添加
@staticmethod
def send_email_notification(user, message):
    # 邮件发送逻辑
    pass
```

### 自定义自动审批规则
```python
# 在 approval_tasks.py 的 check_auto_approval 中添加
if rules.get('custom_rule'):
    # 自定义规则逻辑
    pass
```

## 测试

### 运行单元测试
```bash
python tests/test_approval_system.py
```

### 测试覆盖
- ✅ 简单工作流
- ✅ 多级审批
- ✅ 并行审批
- ✅ 审批委托
- ✅ 拒绝流程
- ✅ 通知创建

## 技术支持

遇到问题请:
1. 查看日志文件
2. 检查数据库数据
3. 运行测试用例
4. 查看源代码注释

## 更新日志

### v1.0.0 (2025-12-03)
- ✅ 核心工作流引擎
- ✅ 7个数据表
- ✅ REST API接口
- ✅ 通知系统
- ✅ 定时任务
- ✅ 前端界面
- ✅ 单元测试
- ✅ 完整文档
