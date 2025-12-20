# 审批流程问题修复报告

## 修复日期
2025年12月5日 17:20

## 问题描述

### 问题1: 审批历史页面崩溃
**错误信息**: `AttributeError: type object 'ApprovalWorkflow' has no attribute 'created_by_id'`

**原因**: `approval_history`路由尝试访问不存在的`created_by_id`字段

### 问题2: 维修工单审批流程未到达部门负责人
**表现**: 创建维修工单后，审批人显示为"未分配"

**根本原因**:
1. "部门负责人"审批角色没有分配任何用户
2. `get_approver_id`函数未正确支持新的审批角色系统

## 修复内容

### 修复1: approval_history_routes.py

**文件**: `app/main/approval_history_routes.py`

移除了对不存在的`created_by_id`字段的引用：

```python
# 修复前
if current_user.role not in ['admin', 'super_admin']:
    query = query.filter(
        or_(
            ApprovalWorkflow.approver_id == current_user.id,
            ApprovalWorkflow.created_by_id == current_user.id  # ❌ 不存在
        )
    )

# 修复后
if current_user.role not in ['admin', 'super_admin']:
    query = query.filter(ApprovalWorkflow.approver_id == current_user.id)
```

### 修复2: get_approver_id 函数增强

**文件**: `app/main/routes.py`

增强`get_approver_id`函数以支持新的审批角色系统：

```python
def get_approver_id(node, department_name):
    """根据节点和部门获取审批人ID
    
    优先使用新的审批角色系统，如果角色未分配用户则fallback到旧的role_required逻辑
    """
    # 1. 尝试从审批角色获取审批人
    if node.approval_role_id:
        from app.approval_roles import UserApprovalRole
        
        # 查找该角色的活跃用户
        assignments = UserApprovalRole.query.filter_by(
            role_id=node.approval_role_id,
            is_active=True
        ).all()
        
        # 如果有多个用户，优先选择同部门的
        eligible_users = [a.user for a in assignments if a.user and a.user.is_active]
        
        if eligible_users:
            # 如果提供了部门，尝试匹配部门
            if department_name:
                same_dept_users = [u for u in eligible_users if u.department == department_name]
                if same_dept_users:
                    return same_dept_users[0].id
            
            # 返回第一个可用用户
            return eligible_users[0].id
    
    # 2. Fallback到旧的role_required逻辑（兼容性）
    # ... (保留原有逻辑)
```

**主要改进**:
- ✓ 优先从审批角色获取审批人
- ✓ 支持部门匹配（优先分配同部门的审批人）
- ✓ Fallback到旧的role_required逻辑（向后兼容）
- ✓ 支持中文角色名称

### 修复3: 审批角色分配

创建了自动化脚本为用户分配审批角色：

**脚本**: `force_assign_dept_role.py`

自动为所有有部门的用户分配"部门负责人"审批角色：

- ✓ admin (信息部)
- ✓ 朱绪 (企管部)
- ✓ 陈松 (企管部)

## 验证结果

### 审批角色分配状态
```
✓ 系统管理员: 1 个用户 (admin)
✓ 部门负责人: 3 个用户 (admin, 朱绪, 陈松)
⚠ 技术员: 0 个用户
⚠ 仓库管理员: 0 个用户
⚠ 财务审批: 0 个用户
```

### 维修工单审批流程
```
节点1: 部门负责人初审
  - 审批角色: 部门负责人 (3个用户)
  - ✓ 可以分配审批人

节点2: 管理员评估金额
  - 审批角色: 系统管理员 (1个用户)
  - ✓ 可以分配审批人

节点3: 部门负责人确认金额
  - 审批角色: 部门负责人 (3个用户)
  - ✓ 可以分配审批人

节点4: 系统管理员审核通过
  - 审批角色: 系统管理员 (1个用户)
  - ✓ 可以分配审批人
```

## 部署步骤

### 方式1: 重新构建Docker镜像（推荐）

```bash
# 重新构建并启动
docker-compose build
docker-compose up -d
```

### 方式2: 重启现有容器（代码已挂载）

```bash
docker-compose restart
```

### 数据库更新（已在本地完成）

如果是生产环境或其他环境，需要运行：

```bash
# 在容器内执行
docker-compose exec web python force_assign_dept_role.py
```

## 测试步骤

1. **测试审批历史页面**
   - 访问：`/approval_history`
   - 预期：页面正常加载，不再报错

2. **测试维修工单审批流程**
   - 创建新的维修工单
   - 检查第一个审批节点是否正确分配了部门负责人
   - 预期：审批人字段有值（如"朱绪"或"陈松"，取决于申请人部门）

3. **测试部门匹配**
   - 企管部用户创建工单 → 应分配给企管部的部门负责人
   - 信息部用户创建工单 → 应分配给信息部的部门负责人

## 后续建议

### 1. 完善其他审批角色

目前仍有角色未分配用户，建议：

```bash
# 为技术员角色分配用户
python scripts/assign_role_to_users.py --role "技术员" --users "user1,user2"

# 为仓库管理员角色分配用户
python scripts/assign_role_to_users.py --role "仓库管理员" --users "user3"
```

或通过管理界面手动分配：
- 路径：管理员 → 审批角色管理 → 选择角色 → 分配用户

### 2. 监控审批流程

监控以下指标：
- 审批人是否正确分配
- 审批节点是否按sequence顺序执行
- 跨部门审批是否正常工作

### 3. 优化部门匹配逻辑

当前逻辑：
- 优先分配同部门的审批人
- 如无同部门审批人，分配第一个可用审批人

可以考虑：
- 支持多部门审批人优先级
- 支持按工作量分配（轮询）
- 支持用户不在线时自动转交

## 相关文件

- `app/main/approval_history_routes.py` - 审批历史路由
- `app/main/routes.py` - get_approver_id函数
- `force_assign_dept_role.py` - 角色分配脚本
- `diagnose_repair_workflow.py` - 诊断脚本
- `verify_dept_role.py` - 验证脚本

## 已知限制

1. **部门匹配仅支持精确匹配**
   - 如果用户没有设置department字段，可能无法正确匹配

2. **审批人选择逻辑**
   - 当前选择第一个可用用户，未来可以改进为负载均衡

3. **角色权限**
   - 需要定期review审批角色分配，确保人员变动时及时更新
