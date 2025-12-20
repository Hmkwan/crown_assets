# 用户审批流角色管理功能说明

## 🎯 问题背景

原有的审批流引擎设计了9种企业角色（员工、部门经理、IT管理员、采购、库房、安全、财务、高层、审计），但 User 模型中只有4种系统角色（admin、user、technician、department_head），导致无法正确分配审批流角色。

## ✅ 解决方案

### 1. 数据模型增强

在 User 模型中添加了 `workflow_roles` 字段：

```python
class User(UserMixin, db.Model):
    # ... 原有字段 ...
    
    # 审批流角色（可多选，JSON格式存储）
    # 例如: '["department_head", "procurement"]' 表示该用户既是部门经理又是采购
    workflow_roles = db.Column(db.Text, nullable=True)
```

### 2. 支持的9种审批流角色

| 角色标识 | 角色名称 | 说明 |
|---------|---------|------|
| employee | 员工 | 普通员工，可发起申请 |
| department_head | 部门经理 | 一级审批 |
| admin | IT资产管理员 | IT部门审核与分配 |
| procurement | 采购 | 采购评估与执行 |
| warehouse | 库房 | 仓库管理与出入库 |
| security | 安全/合规 | 安全审核与合规检查 |
| finance | 财务 | 财务审核与预算确认 |
| executive | 总经理/高层 | 最高审批权限 |
| auditor | 审计/稽核 | 审计监督与留档 |

### 3. 新增的 User 方法

#### get_workflow_roles()
```python
user = User.query.get(1)
roles = user.get_workflow_roles()
# 返回: ['department_head', 'procurement']
```

获取用户的审批流角色列表。如果未设置 `workflow_roles`，会根据系统角色自动映射：
- `admin` → `['admin']`
- `department_head` → `['department_head']`
- `technician` → `['admin']`
- `user` → `['employee']`

#### has_workflow_role(role)
```python
if user.has_workflow_role('procurement'):
    # 用户拥有采购角色
    pass
```

检查用户是否拥有指定的审批流角色。

#### set_workflow_roles(roles)
```python
user.set_workflow_roles(['finance', 'executive'])
db.session.commit()
```

设置用户的审批流角色（批量设置）。

#### get_workflow_roles_display()
```python
display = user.get_workflow_roles_display()
# 返回: "部门经理, 采购"
```

获取审批流角色的中文显示名称。

### 4. 管理界面

访问路径：`/admin/user-roles/`

**功能**：
- ✅ 查看所有用户的审批流角色
- ✅ 为单个用户编辑角色（支持多选）
- ✅ 实时保存并更新显示
- ✅ 批量保存功能（预留）

**界面截图**：
```
用户名    部门      系统角色    审批流角色              操作
--------------------------------------------------------------
admin    IT部      管理员      IT资产管理员            [编辑角色]
张三     财务部    用户        财务, 审计/稽核         [编辑角色]
李四     采购部    用户        采购                    [编辑角色]
王五     IT部      部门主管    部门经理, IT资产管理员  [编辑角色]
```

### 5. 数据库迁移

已执行迁移脚本 `migrations/004_add_user_workflow_roles.sql`：

```sql
-- 添加字段
ALTER TABLE user ADD COLUMN workflow_roles TEXT;

-- 为现有用户自动设置默认角色
UPDATE user SET workflow_roles = '["admin"]' WHERE role = 'admin';
UPDATE user SET workflow_roles = '["department_head"]' WHERE role = 'department_head';
UPDATE user SET workflow_roles = '["admin"]' WHERE role = 'technician';
UPDATE user SET workflow_roles = '["employee"]' WHERE role = 'user' OR workflow_roles IS NULL;
```

### 6. API 接口

#### GET /admin/user-roles/
管理界面首页

#### GET /admin/user-roles/api/get/<user_id>
获取指定用户的审批流角色

**响应示例**：
```json
{
  "user_id": 5,
  "username": "张三",
  "workflow_roles": ["finance", "auditor"],
  "workflow_roles_display": "财务, 审计/稽核"
}
```

#### POST /admin/user-roles/api/set/<user_id>
设置指定用户的审批流角色

**请求示例**：
```json
{
  "roles": ["finance", "auditor"]
}
```

**响应示例**：
```json
{
  "success": true,
  "user_id": 5,
  "username": "张三",
  "workflow_roles": ["finance", "auditor"],
  "workflow_roles_display": "财务, 审计/稽核"
}
```

#### POST /admin/user-roles/api/batch-set
批量设置多个用户的角色

**请求示例**：
```json
{
  "updates": [
    {"user_id": 5, "roles": ["finance"]},
    {"user_id": 6, "roles": ["procurement", "warehouse"]}
  ]
}
```

## 🔄 使用场景

### 场景1：为采购人员分配角色

```python
from app import db
from app.models import User

# 找到采购部门的用户
procurement_user = User.query.filter_by(username='李采购').first()

# 分配采购角色
procurement_user.set_workflow_roles(['procurement'])
db.session.commit()

# 验证
print(procurement_user.get_workflow_roles_display())
# 输出: 采购
```

### 场景2：一人多角色

某些用户可能身兼多职，例如小公司的财务主管同时负责审计：

```python
cfo = User.query.filter_by(username='王财务').first()
cfo.set_workflow_roles(['finance', 'auditor', 'executive'])
db.session.commit()

# 检查角色
if cfo.has_workflow_role('finance'):
    print('可以进行财务审核')
if cfo.has_workflow_role('executive'):
    print('可以进行高层审批')
```

### 场景3：审批流程中的角色匹配

在审批流引擎中，系统会根据节点的 `role_required` 字段查找对应角色的用户：

```python
from app.models import WorkflowNode, User

# 查找需要财务审核的节点
finance_node = WorkflowNode.query.filter_by(
    template_id=3, 
    role_required='finance'
).first()

# 查找所有拥有财务角色的用户
finance_users = User.query.all()
finance_users = [u for u in finance_users if u.has_workflow_role('finance')]

print(f"可执行财务审核的用户: {[u.username for u in finance_users]}")
# 输出: 可执行财务审核的用户: ['王财务', '李会计']
```

## 📊 角色分配建议

### 典型企业配置

**IT部门**：
- IT经理：`['admin', 'department_head']`
- IT工程师：`['admin']`

**财务部门**：
- 财务总监：`['finance', 'executive', 'auditor']`
- 会计：`['finance']`

**采购部门**：
- 采购经理：`['procurement', 'department_head']`
- 采购专员：`['procurement']`

**库房**：
- 库房主管：`['warehouse', 'department_head']`
- 库管员：`['warehouse']`

**安全/合规**：
- 信息安全主管：`['security', 'department_head']`

**普通部门**：
- 部门经理：`['department_head']`
- 员工：`['employee']`

**高层**：
- 总经理：`['executive']`
- 副总：`['executive']`

**审计**：
- 审计主管：`['auditor', 'department_head']`

## 🚀 快速开始

### 1. 访问管理界面

启动应用后，管理员访问：
```
http://localhost:5000/admin/user-roles/
```

### 2. 编辑用户角色

1. 在用户列表中点击"编辑角色"按钮
2. 在弹出的对话框中勾选/取消勾选角色
3. 点击"保存"按钮
4. 页面会实时更新显示

### 3. 验证角色设置

```bash
# 查看所有用户的审批流角色
python -c "from app import create_app; from app.models import User; app = create_app(); app.app_context().push(); users = User.query.all(); [print(f'{u.username}: {u.get_workflow_roles_display()}') for u in users]"
```

## 🔒 权限控制

- ✅ 只有管理员（`current_user.is_admin()`）可以访问角色管理界面
- ✅ 非管理员访问会重定向到首页并显示"无权访问"提示
- ✅ API 接口都需要登录认证（`@login_required`）

## 📝 注意事项

1. **系统角色 vs 审批流角色**：
   - `role` 字段：控制系统权限（admin可以管理所有模块）
   - `workflow_roles` 字段：控制审批流程中的业务角色

2. **多角色用户**：
   - 一个用户可以拥有多个审批流角色
   - 存储格式为 JSON 数组：`'["finance", "executive"]'`

3. **默认角色映射**：
   - 未设置 `workflow_roles` 时，会根据 `role` 自动映射
   - 设置后，以 `workflow_roles` 为准

4. **数据一致性**：
   - 修改角色后需要提交事务：`db.session.commit()`
   - 建议定期检查角色设置的合理性

## 🔮 未来扩展

1. **角色组管理**：创建预设角色组（如"财务组"包含finance和auditor）
2. **角色继承**：高层自动继承下级角色权限
3. **临时授权**：支持临时分配角色（带过期时间）
4. **角色审计**：记录角色变更历史
5. **部门级角色**：根据部门自动分配默认角色

---

**相关文件**：
- 模型定义：`app/models.py` (User 类)
- 路由：`app/user_roles_routes.py`
- 模板：`app/templates/admin/user_workflow_roles.html`
- 迁移：`migrations/004_add_user_workflow_roles.sql`

**访问地址**：`http://localhost:5000/admin/user-roles/`
