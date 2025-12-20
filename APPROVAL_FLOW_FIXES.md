# 审批流程问题修复报告

## 修复时间
2024年12月3日

## 问题清单

### ❌ 问题1: 重新分配审批人报错
**错误信息**: `'NoneType' object has no attribute 'username'`

**原因**: 
- 当 `approval.approver` 为 `None` 时,访问 `approver.username` 导致空指针异常
- 发生在管理员重新分配审批人功能中

**修复**:
```python
# 修复前
old_approver = approval.approver
approval.comments = f'管理员重新分配: {old_approver.username} → {new_approver.username}. 原因: {reason}'

# 修复后
old_approver = approval.approver
old_name = old_approver.username if old_approver else '未分配'
new_name = new_approver.username
approval.comments = f'管理员重新分配: {old_name} → {new_name}. 原因: {reason}'
```

**文件**: `app/admin/approval_management_routes.py` 第218-223行

---

### ❌ 问题2: 模态框关闭按钮异常
**现象**: 
- 模态框的 ✕ 关闭按钮无法点击
- 使用了Bootstrap 5的语法 (`data-bs-dismiss`, `btn-close`)
- 但项目使用的是Bootstrap 4

**修复**:
```html
<!-- 修复前 (Bootstrap 5) -->
<button type="button" class="btn-close" data-bs-dismiss="modal"></button>

<!-- 修复后 (Bootstrap 4) -->
<button type="button" class="close" data-dismiss="modal" aria-label="Close">
    <span aria-hidden="true">&times;</span>
</button>
```

**影响模态框**:
- ✅ 跳过节点模态框
- ✅ 重新分配审批人模态框
- ✅ 打回节点模态框

**文件**: `app/templates/admin/approval_flow_detail.html`

---

### ❌ 问题3: 模态框打开方式错误
**现象**: JavaScript 使用了Bootstrap 5的API

**修复**:
```javascript
// 修复前 (Bootstrap 5)
function showReassignModal() {
    const modal = new bootstrap.Modal(document.getElementById('reassignModal'));
    modal.show();
}

// 修复后 (Bootstrap 4 + jQuery)
function showReassignModal() {
    $('#reassignModal').modal('show');
}
```

**文件**: `app/templates/admin/approval_flow_detail.html` 第312-324行

---

### ❌ 问题4: 工单类型中文映射错误
**现象**: 配件申请显示为 `part_request` 而非 `part_request_order`

**修复**:
```html
<!-- 修复前 -->
{% elif order_info.type == 'part_request' %}配件申请

<!-- 修复后 -->
{% elif order_info.type == 'part_request_order' %}配件申请
```

**文件**: `app/templates/admin/approval_flow_detail.html` 第79行

---

### ❌ 问题5: 节点角色显示使用旧字段
**现象**: 
- 流程节点列表中显示的是 `role_required` 字段
- 未使用新的 `approval_role` 关系

**修复**:
```html
<!-- 修复前 -->
<small class="text-muted d-block">
    {% if node.role_required == 'department_head' %}部门审核
    {% elif node.role_required == 'admin' %}管理员审核
    {% else %}{{ node.role_required }}
    {% endif %}
</small>

<!-- 修复后 -->
<small class="text-muted d-block">
    {% if node.approval_role %}
        <i class="fas {{ node.approval_role.icon }}"></i> {{ node.approval_role.name }}
    {% elif node.role_required %}
        {{ node.role_required }}
    {% else %}
        未设置角色
    {% endif %}
</small>
```

**文件**: `app/templates/admin/approval_flow_detail.html` 第202-214行

---

### ❌ 问题6: 审批人列表未根据角色筛选
**现象**: 
- 重新分配审批人时,显示所有用户
- 未根据当前节点的审批角色筛选

**修复**:
```python
# 修复前
users = User.query.filter_by(is_active=True).all()

# 修复后
eligible_users = []
if approval.workflow_node and approval.workflow_node.approval_role_id:
    # 根据审批角色获取有资格的用户
    from app.models import UserApprovalRole
    role_assignments = UserApprovalRole.query.filter_by(
        role_id=approval.workflow_node.approval_role_id,
        is_active=True
    ).all()
    eligible_users = [assignment.user for assignment in role_assignments 
                      if assignment.user and assignment.user.is_active]
else:
    # 如果没有设置审批角色,获取所有活跃用户
    eligible_users = User.query.filter_by(is_active=True).all()
```

**文件**: `app/admin/approval_management_routes.py` 第86-97行

---

## 修复文件清单

| 文件 | 修复内容 | 行数 |
|------|---------|------|
| `app/admin/approval_management_routes.py` | 空指针异常、审批人筛选 | 218-223, 86-97 |
| `app/templates/admin/approval_flow_detail.html` | 模态框按钮、工单类型映射、角色显示、JavaScript | 多处 |
| `update_workflow_approval_roles.py` | 新建:更新节点使用审批角色 | 全文件 |

---

## 测试建议

### 1. 测试重新分配审批人
- [ ] 打开审批流程详情页面
- [ ] 点击"重新分配审批人"按钮
- [ ] 检查下拉列表是否只显示有该角色的用户
- [ ] 选择新审批人并提交
- [ ] 验证是否成功分配且无报错

### 2. 测试模态框关闭
- [ ] 点击跳过节点按钮,检查 ✕ 是否能关闭
- [ ] 点击重新分配按钮,检查 ✕ 是否能关闭
- [ ] 点击打回节点按钮,检查 ✕ 是否能关闭
- [ ] 点击"取消"按钮是否能关闭

### 3. 测试中文显示
- [ ] 检查工单类型是否正确显示中文
- [ ] 检查流程节点列表是否显示审批角色名称和图标
- [ ] 检查审批状态是否正确显示中文

### 4. 测试默认流程
- [ ] 创建维修工单,检查是否自动创建审批流程
- [ ] 检查审批节点是否正确设置了审批角色
- [ ] 检查审批人是否从角色分配中正确选择

---

## 后续优化建议

1. **完全移除 role_required 字段**
   - 目前仍保留作为后备字段
   - 待所有节点迁移完成后可删除

2. **增强审批人智能分配**
   - 根据部门、金额自动筛选
   - 支持审批人轮询分配
   - 支持审批人负载均衡

3. **审批流程可视化**
   - 添加流程图展示
   - 显示当前进度
   - 支持流程预览

4. **审批历史增强**
   - 显示每个节点的所有候选人
   - 显示转交历史
   - 显示管理员干预记录

---

**修复状态**: ✅ 全部完成
**测试状态**: ⏳ 待测试
**上线建议**: 需要先在测试环境验证
