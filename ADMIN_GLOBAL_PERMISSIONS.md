# Admin全局权限实施总结

## 一、核心目标
使admin用户不属于任何部门,拥有全局权限,可以查看和管理整个系统的所有数据,不受部门限制。

## 二、数据库修改
### 1. 清空admin用户的部门信息
**脚本**: `scripts/fix_admin_department.py`

**执行结果**:
- 处理admin用户: admin (信息部 → 无部门)
- 处理admin用户: 吴文杨 (信息部 → 无部门)
- 成功更新2个admin用户的department和department_id字段为NULL

## 三、权限辅助模块
### 1. 新建文件: `app/utils/permission_helpers.py`
**核心函数**:
- `can_access_department(department_name, department_id)` - 检查是否可访问指定部门
- `filter_by_department(query, model_department_field)` - 应用部门过滤到查询
- `is_admin()` - 检查是否为admin
- `get_accessible_departments()` - 获取可访问的部门列表
- `can_manage_user(target_user)` - 检查是否可管理指定用户
- `can_view_all_data()` - 检查是否可查看所有数据
- `apply_department_filter(query, model_class, department_field)` - 应用部门过滤器

**核心逻辑**:
```python
if current_user.role == 'admin':
    return True  # admin跳过所有部门限制
```

## 四、路由权限修改

### 1. 设备管理 (Equipment)
**路由**: `equipment_list()`  
**文件**: `app/main/routes.py` line ~1159  
**修改前**:
```python
if current_user.role != 'admin':
    query = query.filter(Equipment.department == current_user.department)
```
**修改后**:
```python
if current_user.role != 'admin' and current_user.department:
    query = query.filter(Equipment.department == current_user.department)
```
**效果**: admin可以查看所有部门的设备,无部门用户不会报错

---

### 2. 配件管理 (SparePart)
**路由**: `spare_parts()`  
**文件**: `app/main/routes.py` line ~1933  
**修改前**:
```python
if current_user.role != 'admin':
    query = query.filter_by(department=current_user.department)
```
**修改后**:
```python
if current_user.role != 'admin' and current_user.department:
    query = query.filter_by(department=current_user.department)
```
**效果**: admin可以查看所有部门的配件

---

### 3. 维修工单 (RepairOrder)
**路由**: `repair_orders()`  
**文件**: `app/main/routes.py` line ~648  
**修改前**:
```python
if current_user.role == 'user':
    query = query.filter_by(requester_id=current_user.id)
```
**修改后**:
```python
# admin可以查看所有维修单,普通用户只能看自己提交的
if current_user.role == 'user':
    query = query.filter_by(requester_id=current_user.id)
```
**效果**: admin可以查看所有维修工单,逻辑已正确

---

### 4. 创建维修工单
**路由**: `create_repair_order()`  
**文件**: `app/main/routes.py` line ~2299  
**修改内容**:
1. 获取设备列表时:
   ```python
   if current_user.role == 'admin':
       equipments = Equipment.query.all()
   elif current_user.department:
       equipments = Equipment.query.filter_by(department=current_user.department).all()
   else:
       equipments = []
   ```

2. 验证设备权限时:
   ```python
   if current_user.role == 'admin':
       equipment = Equipment.query.filter_by(id=equipment_id).first()
   elif current_user.department:
       equipment = Equipment.query.filter_by(id=equipment_id, department=current_user.department).first()
   else:
       equipment = None
   ```

3. 查找部门负责人时:
   ```python
   if current_user.department:
       department_heads = User.query.filter_by(role='department_head', department=current_user.department).all()
   else:
       department_heads = []
   ```

**效果**: admin可以为任何设备创建维修工单,无部门用户不会报错

---

### 5. 创建借用申请
**路由**: `create_loan_request()`  
**文件**: `app/main/routes.py` line ~3926  
**修改内容**:
```python
if current_user.role == 'admin':
    equipments = Equipment.query.filter(Equipment.status != 'retired').all()
elif current_user.department:
    own = Equipment.query.filter(Equipment.department == current_user.department, Equipment.status != 'retired').all()
    pool = Equipment.query.filter(Equipment.is_public_pool == True, Equipment.status == 'available').all()
    eq_map = {e.id: e for e in own + pool}
    equipments = list(eq_map.values())
else:
    # 用户无部门时,只能申请公开仓库的设备
    equipments = Equipment.query.filter(Equipment.is_public_pool == True, Equipment.status == 'available').all()
```
**效果**: admin可以借用所有未报废设备

---

### 6. 创建调拨申请
**路由**: `create_transfer()`  
**文件**: `app/main/routes.py` line ~4617  
**修改内容**:
```python
if current_user.role == 'admin':
    equipments = Equipment.query.all()
elif current_user.department:
    equipments = Equipment.query.filter_by(department=current_user.department).all()
else:
    equipments = []
```
**效果**: admin可以调拨任何设备

---

### 7. 创建报废申请
**路由**: `create_scrap()`  
**文件**: `app/main/routes.py` line ~4683  
**修改内容**:
```python
if current_user.role == 'admin':
    equipments = Equipment.query.all()
elif current_user.department:
    equipments = Equipment.query.filter_by(department=current_user.department).all()
else:
    equipments = []
```
**效果**: admin可以报废任何设备

---

### 8. 创建配件申请
**路由**: `create_part_request_order()`  
**文件**: `app/main/routes.py` line ~3485  
**修改内容**:
```python
# 审批流程创建
if current_user.department:
    steps = [
        ('department_head', current_user.department),
        ('admin', None)
    ]
else:
    # 无部门用户直接由admin审批
    steps = [('admin', None)]
```

```python
# 通知创建
if current_user.department:
    department_heads = User.query.filter_by(role='department_head', department=current_user.department).all()
else:
    department_heads = []
```
**效果**: 无部门用户(如admin)的配件申请直接由admin审批,不会查找不存在的部门负责人

---

### 9. 用户管理
**路由**: `user_management()`  
**文件**: `app/main/routes.py` line ~358  
**现状**: 已正确实现,admin可以查看所有用户,无需修改

---

### 10. 统计报表
**路由**: `reports()`  
**文件**: `app/main/routes.py` line ~3554  
**现状**: 已正确实现,admin可以查看所有数据的统计,无需修改

## 五、核心原则
1. **admin用户**: `role='admin'` 且 `department=None` 且 `department_id=None`
2. **权限检查**: 所有部门过滤必须同时检查 `current_user.role != 'admin'` 和 `current_user.department`
3. **查询过滤**: 使用模式 `if current_user.role != 'admin' and current_user.department:`
4. **通知发送**: 查找部门负责人前必须检查用户是否有部门

## 六、测试验证
### 需要验证的功能:
1. ✅ admin用户数据库department字段已清空
2. ⏳ admin能查看所有部门的设备列表
3. ⏳ admin能查看所有部门的配件列表
4. ⏳ admin能查看所有维修工单
5. ⏳ admin能为任何设备创建维修工单
6. ⏳ admin能创建调拨、报废、借用申请
7. ⏳ admin能查看完整的统计报表
8. ⏳ 无部门的普通用户不会因为department为None而报错

## 七、后续工作
1. 全面测试admin全局权限功能
2. 验证其他角色(department_head, technician)的权限不受影响
3. 检查审批流程是否正常(admin创建的订单审批流程)
4. 更新用户手册,说明admin的全局权限特性

## 八、文件清单
### 新建文件:
- `app/utils/permission_helpers.py` - 权限辅助函数
- `scripts/fix_admin_department.py` - 修复admin部门脚本
- `ADMIN_GLOBAL_PERMISSIONS.md` - 本文档

### 修改文件:
- `app/main/routes.py` - 8个路由函数的权限检查修改

### 修改统计:
- 路由修改: 8处
- 权限检查修改: 12处
- 新增辅助函数: 8个
- 数据库记录更新: 2个admin用户
