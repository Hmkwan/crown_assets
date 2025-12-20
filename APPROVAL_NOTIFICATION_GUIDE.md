# 审批待办提醒功能说明

## 功能概述

审批待办提醒功能会定期检查系统中的待审批事项,并向相关审批人发送汇总通知,提醒他们及时处理待办审批任务。

## 实现细节

### 1. 定时任务配置

- **执行时间**: 每天上午10:30和下午15:00
- **任务ID**: `check_pending_approvals`
- **任务名称**: 检查待审批事项

### 2. 检查逻辑

任务会执行以下操作:

1. **查询待审批节点**:
   - 查找所有 `status='pending'` 的 `ApprovalWorkflow` 记录
   - 这包括所有类型的审批流程(维修工单、配件申请、设备采购、借用申请、报废申请等)

2. **按审批人分组统计**:
   ```python
   - 审批人1: 
     - 维修工单 2条
     - 配件申请 1条
   - 审批人2:
     - 设备采购 3条
     - 借用申请 1条
   ```

3. **发送汇总通知**:
   - 标题: "审批待办提醒"
   - 内容: "您有X条待审批事项(维修工单Y条,配件申请Z条...),请及时处理。"
   - 通知类型: `order_type='approval'`

### 3. 支持的审批类型

系统自动识别以下类型的审批:

| 类型标识 | 显示名称 |
|---------|---------|
| repair_order | 维修工单 |
| part_request_order | 配件申请 |
| equipment_application | 设备申请 |
| equipment_loan | 设备借用 |
| equipment_transfer | 设备调拨 |
| equipment_scrap | 设备报废 |

### 4. 开关配置

可以通过环境变量控制此功能:

```bash
# 全局开关
SCHEDULER_ENABLED=true

# 审批提醒独立开关
SCHEDULER_PENDING_APPROVALS=true
```

配置文件位置:
- `config.py` - 定义配置项
- `.env.scheduler.example` - 环境变量示例
- 使用时复制为 `.env` 并修改

### 5. 禁用方法

如需禁用审批提醒,可以:

**方法1: 环境变量**
```bash
# 在 .env 文件中设置
SCHEDULER_PENDING_APPROVALS=false
```

**方法2: Docker Compose**
```yaml
services:
  web:
    environment:
      - SCHEDULER_PENDING_APPROVALS=false
```

**方法3: 禁用所有定时任务**
```bash
SCHEDULER_ENABLED=false
```

## 通知示例

### 场景1: 单一审批人,多种类型

**审批人**: 张三 (@zhangsan)

**待审批事项**:
- 维修工单 2条
- 配件申请 1条
- 设备采购 1条

**发送通知**:
```
标题: 审批待办提醒
内容: 您有4条待审批事项(维修工单2条,配件申请1条,设备申请1条),请及时处理。
```

### 场景2: 多个审批人

系统会为每个审批人单独统计并发送通知:

**审批人1**: 部门经理
- 维修工单 3条

**审批人2**: 采购负责人
- 设备采购 5条
- 配件申请 2条

每个人收到的通知只包含自己待处理的审批事项。

## 日志输出

### 成功执行示例

```log
[2025-12-04 10:30:00,123] INFO in scheduler: [定时任务] 发送审批提醒给用户 zhangsan: 4条待审批
[2025-12-04 10:30:00,234] INFO in scheduler: [定时任务] 发送审批提醒给用户 lisi: 7条待审批
[2025-12-04 10:30:00,345] INFO in scheduler: [定时任务] 审批提醒检查完成,发现11条待审批,通知2个审批人
```

### 无待审批示例

```log
[2025-12-04 10:30:00,123] INFO in scheduler: [定时任务] 审批提醒检查完成,无待审批事项 (2025-12-04 10:30)
```

### 异常处理示例

```log
[2025-12-04 10:30:00,123] ERROR in scheduler: [定时任务] 审批提醒检查失败: Database connection error
```

## 技术实现

### 核心代码位置

- **调度器配置**: `app/scheduler.py`
  - `check_pending_approvals()` 函数 (line 243-310)
  - `init_scheduler()` 函数中的任务注册 (line 390-397)

- **配置定义**: `config.py`
  - `SCHEDULER_ENABLED` - 全局开关
  - `SCHEDULER_JOBS['pending_approvals']` - 审批提醒开关

- **环境变量示例**: `.env.scheduler.example`

### 数据库查询

```python
# 查询所有待审批节点
pending_approvals = ApprovalWorkflow.query.filter(
    ApprovalWorkflow.status == 'pending'
).all()

# 按审批人分组
for approval in pending_approvals:
    approver_id = approval.approver_id
    order_type = approval.order_type  # 工单类型
    order_id = approval.order_id      # 工单ID
```

### 通知创建

```python
notification = Notification(
    user_id=approver_id,
    title="审批待办提醒",
    message=f"您有{len(items)}条待审批事项({type_summary}),请及时处理。",
    order_type='approval',
    order_id=None
)
db.session.add(notification)
```

## 与其他提醒任务的对比

| 功能 | 执行时间 | 提醒对象 | 提醒内容 |
|-----|---------|---------|---------|
| **审批待办提醒** | 10:30, 15:00 | 审批人 | 待审批事项汇总 |
| 逾期借用提醒 | 09:00 | 借用人 | 逾期未归还设备 |
| 即将到期提醒 | 09:00 | 借用人 | 3天内需归还设备 |
| 待验收提醒 | 10:00 | 管理员 | 待验收的归还设备 |
| 保养提醒 | 08:00 | 负责人 | 即将到期的保养计划 |

## 未来改进方向

1. **优先级标记**:
   - 区分紧急和普通审批
   - 高优先级审批单独提醒

2. **个性化配置**:
   - 允许审批人自定义提醒时间
   - 支持邮件/短信通知

3. **智能提醒**:
   - 根据审批人的活跃时间调整提醒频率
   - 逾期未处理的审批增加提醒频率

4. **详细统计**:
   - 提供审批人的待办清单页面
   - 显示每个审批的详细信息和优先级

## 测试方法

### 1. 手动触发测试

```python
# 在容器中执行
docker exec equipment-management-system python -c "
from app import create_app
from app.scheduler import check_pending_approvals
app = create_app()
with app.app_context():
    check_pending_approvals()
"
```

### 2. 创建测试数据

创建包含待审批节点的工单:
1. 登录系统
2. 创建维修工单/借用申请/设备采购等
3. 等待审批流程启动
4. 查看待审批节点是否创建成功

### 3. 验证通知

1. 等待定时任务执行(10:30或15:00)
2. 以审批人身份登录系统
3. 查看通知图标是否显示新通知
4. 点击查看通知内容

### 4. 检查日志

```bash
# 查看容器日志
docker logs equipment-management-system --tail 50 | grep "审批提醒"

# 实时监控
docker logs -f equipment-management-system | grep "定时任务"
```

## 常见问题

### Q1: 为什么没有收到审批提醒?

**可能原因**:
1. 审批提醒功能被禁用 - 检查 `SCHEDULER_PENDING_APPROVALS` 配置
2. 全局调度器被禁用 - 检查 `SCHEDULER_ENABLED` 配置
3. 当前没有待审批事项 - 查询 `ApprovalWorkflow` 表
4. 审批节点没有指定审批人 - 检查 `approver_id` 字段

### Q2: 可以修改提醒时间吗?

可以。修改 `app/scheduler.py` 中的 CronTrigger 配置:

```python
# 原配置: 10:30 和 15:00
trigger=CronTrigger(hour='10,15', minute=30)

# 修改为: 09:00, 14:00, 17:00
trigger=CronTrigger(hour='9,14,17', minute=0)
```

### Q3: 通知太频繁怎么办?

减少执行频率:

```python
# 改为每天只提醒一次(上午10:00)
trigger=CronTrigger(hour=10, minute=0)
```

### Q4: 可以禁用特定类型的审批提醒吗?

当前版本不支持按类型禁用,但可以修改 `check_pending_approvals()` 函数:

```python
# 排除某些类型
excluded_types = ['equipment_loan']  # 不提醒借用审批
pending_approvals = ApprovalWorkflow.query.filter(
    ApprovalWorkflow.status == 'pending',
    ~ApprovalWorkflow.order_type.in_(excluded_types)
).all()
```

## 总结

审批待办提醒功能通过定时检查待审批事项,向审批人发送汇总通知,帮助提高审批效率,避免审批积压。该功能:

✅ 自动化 - 无需人工干预,定时执行
✅ 可配置 - 支持通过环境变量控制开关
✅ 智能统计 - 按审批人分组,按类型汇总
✅ 日志完善 - 详细记录执行情况
✅ 异常安全 - 错误不影响其他任务执行

配合其他定时提醒任务,共同构建完善的通知系统。
