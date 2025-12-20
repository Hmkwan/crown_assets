# 数据库完整性改进建议

**生成日期**: 2025-11-30  
**审计范围**: SQLAlchemy模型定义,外键约束,级联删除,事务处理

---

## 一、外键级联删除配置

### 当前状态
- ✅ 只有3个关系配置了级联删除:
  - `EquipmentApplication.equipment` (cascade='all, delete-orphan')
  - `Role.permissions` (cascade='all, delete-orphan')
  - `WorkflowTemplate.steps` (cascade='all, delete-orphan')

- ❌ 大部分外键未配置级联删除规则

### 问题影响

**场景1**: 删除设备时
```python
# 当前行为:
equipment = Equipment.query.get(1)
db.session.delete(equipment)
db.session.commit()  # ❌ 报错: 外键约束violation

# 原因: RepairOrder表中有equipment_id=1的记录
```

**场景2**: 删除用户时
```python
# 当前行为:
user = User.query.get(1)
db.session.delete(user)
db.session.commit()  # ❌ 报错: 外键约束violation

# 原因: ApprovalWorkflow表中有approver_id=1的记录
```

### 修复方案

#### 1. Equipment 设备表的关联记录

**需要级联删除的关系**:
```python
class RepairOrder(db.Model):
    # 修改前
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'))
    
    # 修改后 - 设备删除时,维修工单也删除
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id', ondelete='CASCADE'))
```

**需要设置为NULL的关系**:
```python
class Equipment(db.Model):
    # 修改前
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    # 修改后 - 用户删除时,设备的使用人设为NULL
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='SET NULL'))
```

#### 2. 完整的外键配置建议

**models.py 需要修改的字段**:

```python
# ==================== Equipment 设备 ====================
class Equipment(db.Model):
    department_id = db.Column(db.Integer, db.ForeignKey('department.id', ondelete='SET NULL'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='SET NULL'))
    # 设备删除用户/部门时保留记录,只是清空关联


# ==================== RepairOrder 维修工单 ====================
class RepairOrder(db.Model):
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id', ondelete='CASCADE'))
    requester_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='SET NULL'))
    assigned_technician_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='SET NULL'))
    # 设备删除→工单删除
    # 用户删除→保留工单,清空申请人/技术员字段


# ==================== SparePart 配件 ====================
class SparePart(db.Model):
    type_id = db.Column(db.Integer, db.ForeignKey('spare_part_type.id', ondelete='SET NULL'))
    department_id = db.Column(db.Integer, db.ForeignKey('department.id', ondelete='SET NULL'))
    # 删除类型/部门时,配件保留但关联清空


# ==================== PartRequestOrder 配件申请单 ====================
class PartRequestOrder(db.Model):
    part_id = db.Column(db.Integer, db.ForeignKey('spare_part.id', ondelete='CASCADE'))
    requester_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='SET NULL'))
    # 配件删除→申请单删除
    # 用户删除→保留申请单,清空申请人


# ==================== ApprovalWorkflow 审批流程 ====================
class ApprovalWorkflow(db.Model):
    workflow_node_id = db.Column(db.Integer, db.ForeignKey('workflow_node.id', ondelete='CASCADE'))
    approver_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='SET NULL'))
    # 节点删除→审批记录删除
    # 用户删除→保留审批记录,清空审批人(用于历史记录)


# ==================== WorkflowNode 流程节点 ====================
class WorkflowNode(db.Model):
    template_id = db.Column(db.Integer, db.ForeignKey('workflow_template.id', ondelete='CASCADE'))
    # 模板删除→节点删除


# ==================== EquipmentTransfer 设备调拨 ====================
class EquipmentTransfer(db.Model):
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id', ondelete='CASCADE'))
    requester_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='SET NULL'))
    # 设备删除→调拨记录删除
    # 用户删除→保留调拨记录


# ==================== EquipmentScrap 设备报废 ====================
class EquipmentScrap(db.Model):
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id', ondelete='CASCADE'))
    requester_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='SET NULL'))
    # 同上


# ==================== EquipmentLoan 设备借用 ====================
class EquipmentLoan(db.Model):
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id', ondelete='CASCADE'))
    requester_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='SET NULL'))
    actual_user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='SET NULL'))
    # 同上


# ==================== EquipmentApplication 设备申请 ====================
class EquipmentApplication(db.Model):
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id', ondelete='CASCADE'))
    applicant_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='SET NULL'))
    # 同上


# ==================== AssetCost 资产成本 ====================
class AssetCost(db.Model):
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id', ondelete='CASCADE'))
    # 设备删除→成本记录也删除


# ==================== Notification 通知 ====================
class Notification(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    # 用户删除→通知删除


# ==================== UserActivityLog 操作日志 ====================
class UserActivityLog(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='SET NULL'))
    # 用户删除→保留日志,清空用户ID(用于审计)


# ==================== AccountRequest 账号申请 ====================
class AccountRequest(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    approved_by = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='SET NULL'))
    # 申请人删除→申请删除
    # 审批人删除→保留申请,清空审批人
```

---

## 二、并发控制问题

### 问题场景: 配件库存超卖

**当前代码** (routes.py):
```python
def approve_part_order(order_id):
    part = part_order.part
    
    # ❌ 问题: 两个请求同时到达
    # Request A: 读取 part.quantity = 10
    # Request B: 读取 part.quantity = 10
    
    if part.quantity >= part_order.quantity:  # 都满足条件
        part.quantity -= part_order.quantity
        # Request A: 扣减5, quantity = 5
        # Request B: 扣减8, quantity = 2
        # 实际应该是: 10 - 5 - 8 = -3 (负库存!)
```

### 解决方案1: 悲观锁 (推荐)

```python
def approve_part_order(order_id):
    # 使用 SELECT FOR UPDATE 锁定行
    part = db.session.query(SparePart).with_for_update().filter_by(
        id=part_order.part_id
    ).first()
    
    # 此时其他请求会等待,直到当前事务提交
    if part.quantity >= part_order.quantity:
        part.quantity -= part_order.quantity
        db.session.commit()
    else:
        db.session.rollback()
        raise Exception("库存不足")
```

### 解决方案2: 乐观锁

```python
class SparePart(db.Model):
    # 添加版本号字段
    version = db.Column(db.Integer, default=0)

def approve_part_order(order_id):
    part = SparePart.query.get(part_order.part_id)
    old_version = part.version
    
    if part.quantity >= part_order.quantity:
        # 更新时检查版本号
        result = db.session.execute(
            update(SparePart).
            where(SparePart.id == part.id).
            where(SparePart.version == old_version).
            values(
                quantity=SparePart.quantity - part_order.quantity,
                version=SparePart.version + 1
            )
        )
        
        if result.rowcount == 0:
            # 版本号不匹配,说明被其他请求修改了
            raise Exception("库存已被其他操作修改,请重试")
        
        db.session.commit()
```

### 解决方案3: 数据库约束 (最简单)

```python
class SparePart(db.Model):
    # 添加CHECK约束
    __table_args__ = (
        db.CheckConstraint('quantity >= 0', name='check_quantity_non_negative'),
    )
```

**修改 alembic migration**:
```python
# migrations/versions/xxx_add_quantity_check.py
def upgrade():
    op.execute('''
        ALTER TABLE spare_part 
        ADD CONSTRAINT check_quantity_non_negative 
        CHECK (quantity >= 0)
    ''')
```

**结果**: 如果扣减后库存为负,数据库会拒绝提交,抛出异常

---

## 三、事务处理改进

### 问题: 部分操作缺少事务保护

**场景: 审批完成后的多步骤操作**
```python
# ❌ 当前代码 (routes.py:3222-3322)
def approve_part_order(order_id):
    approval.status = 'approved'
    db.session.add(approval)  # Step 1
    
    part.quantity -= part_order.quantity  # Step 2
    
    notification = Notification(...)
    db.session.add(notification)  # Step 3
    
    db.session.commit()  # 如果Step 3失败,Step 1和2已经执行了
```

**问题**: 如果中间某步失败,前面的步骤已经提交,导致数据不一致

### 解决方案: 显式事务 + 异常处理

```python
def approve_part_order(order_id):
    try:
        # 开始事务
        approval.status = 'approved'
        db.session.add(approval)
        
        # 扣减库存
        part = db.session.query(SparePart).with_for_update().get(part_order.part_id)
        if part.quantity < part_order.quantity:
            raise ValueError("库存不足")
        part.quantity -= part_order.quantity
        
        # 创建通知
        notification = Notification(...)
        db.session.add(notification)
        
        # 记录日志
        log = UserActivityLog(...)
        db.session.add(log)
        
        # 统一提交
        db.session.commit()
        
        flash('审批成功')
        
    except ValueError as e:
        db.session.rollback()
        flash(str(e))
        return redirect(url_for('main.approvals'))
    
    except Exception as e:
        db.session.rollback()
        app.logger.error(f'审批失败: {e}')
        flash('审批失败,请联系管理员')
        return redirect(url_for('main.approvals'))
```

**改进点**:
1. 使用 try-except 包裹所有数据库操作
2. 任何异常都会触发 rollback
3. 显式记录错误日志
4. 给用户明确的错误提示

---

## 四、修复实施步骤

### 步骤1: 创建数据库迁移脚本

```bash
# 1. 创建新的迁移
flask db revision -m "add_cascade_delete_and_constraints"

# 2. 编辑生成的迁移文件
# migrations/versions/xxx_add_cascade_delete.py
```

**迁移文件内容**:
```python
def upgrade():
    # 1. 删除旧的外键
    op.drop_constraint('repair_order_ibfk_1', 'repair_order', type_='foreignkey')
    
    # 2. 添加新的外键(带级联删除)
    op.create_foreign_key(
        'repair_order_equipment_fk',
        'repair_order', 'equipment',
        ['equipment_id'], ['id'],
        ondelete='CASCADE'
    )
    
    # 3. 添加库存检查约束
    op.execute('''
        ALTER TABLE spare_part 
        ADD CONSTRAINT check_quantity_non_negative 
        CHECK (quantity >= 0)
    ''')
    
    # ... 重复上述步骤for所有需要修改的外键

def downgrade():
    # 回滚操作
    op.drop_constraint('repair_order_equipment_fk', 'repair_order', type_='foreignkey')
    op.create_foreign_key(
        'repair_order_ibfk_1',
        'repair_order', 'equipment',
        ['equipment_id'], ['id']
    )
```

### 步骤2: 修改 models.py

在所有 `db.ForeignKey()` 中添加 `ondelete` 参数:

```python
# 查找所有未配置ondelete的ForeignKey
# 使用正则: db\.ForeignKey\('[^']+'\)(?!.*ondelete)

# 逐个修改
```

### 步骤3: 添加并发控制

**修改配件审批路由** (routes.py:3222):
```python
@bp.route('/approvals/part_order/<int:order_id>/<action>', methods=['POST'])
def approve_part_order(order_id, action):
    try:
        # ... 省略审批权限检查
        
        if action == 'approve':
            # 使用悲观锁
            part = db.session.query(SparePart).with_for_update().filter_by(
                id=part_order.part_id
            ).first()
            
            if not part:
                raise ValueError("配件不存在")
            
            if part.quantity < part_order.quantity:
                raise ValueError(f"库存不足,当前库存:{part.quantity},需求:{part_order.quantity}")
            
            # 扣减库存
            part.quantity -= part_order.quantity
            
            # ... 其他操作
            
            db.session.commit()
            flash('审批成功')
        
    except ValueError as e:
        db.session.rollback()
        flash(str(e))
    except Exception as e:
        db.session.rollback()
        app.logger.error(f'配件审批失败: {e}')
        flash('操作失败,请联系管理员')
    
    return redirect(url_for('main.approvals'))
```

**修改维修工单添加配件** (routes.py:2932):
```python
@bp.route('/repair_order/<int:order_id>/add_parts', methods=['POST'])
def add_parts_to_repair(order_id):
    try:
        # 使用悲观锁
        part = db.session.query(SparePart).with_for_update().filter_by(
            id=part_id
        ).first()
        
        if part.quantity < quantity:
            raise ValueError(f"库存不足,当前库存:{part.quantity}")
        
        part.quantity -= quantity
        
        # 添加到工单
        # ...
        
        db.session.commit()
        
    except ValueError as e:
        db.session.rollback()
        flash(str(e))
    except Exception as e:
        db.session.rollback()
        flash('添加配件失败')
    
    return redirect(...)
```

### 步骤4: 测试

**测试用例1: 级联删除**
```python
# 测试脚本: tests/test_cascade_delete.py

def test_delete_equipment_cascades_repair_orders():
    # 创建设备
    equipment = Equipment(name='测试设备', serial_number='TEST001')
    db.session.add(equipment)
    db.session.commit()
    
    # 创建维修工单
    repair = RepairOrder(equipment_id=equipment.id, ...)
    db.session.add(repair)
    db.session.commit()
    
    repair_id = repair.id
    
    # 删除设备
    db.session.delete(equipment)
    db.session.commit()
    
    # 验证工单也被删除
    repair = RepairOrder.query.get(repair_id)
    assert repair is None  # 应该为None
```

**测试用例2: 并发库存扣减**
```python
import threading

def test_concurrent_inventory_deduction():
    # 设置初始库存
    part = SparePart(name='测试配件', quantity=10)
    db.session.add(part)
    db.session.commit()
    
    # 模拟两个并发请求
    def deduct_inventory(amount):
        # 使用with_for_update锁
        p = db.session.query(SparePart).with_for_update().get(part.id)
        p.quantity -= amount
        db.session.commit()
    
    # 启动两个线程
    t1 = threading.Thread(target=deduct_inventory, args=(7,))
    t2 = threading.Thread(target=deduct_inventory, args=(5,))
    
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    
    # 验证: 应该只有一个成功,或者第二个抛出异常
    part = SparePart.query.get(part.id)
    assert part.quantity >= 0  # 不应该出现负库存
```

---

## 五、优先级和时间估算

| 改进项 | 优先级 | 影响范围 | 预计工时 |
|--------|--------|----------|----------|
| 添加外键级联删除 | 🔴 高 | 所有表 | 4小时 |
| 配件库存并发控制 | 🔴 高 | 配件申请、维修工单 | 2小时 |
| 事务处理优化 | 🟡 中 | 所有审批路由 | 3小时 |
| 数据库约束(CHECK) | 🟢 低 | 数值字段 | 1小时 |
| 单元测试 | 🟡 中 | 所有改动 | 4小时 |

**总计**: 约14小时 (2个工作日)

---

## 六、风险评估

### 风险1: 迁移失败导致数据丢失
- **概率**: 低
- **影响**: 高
- **缓解措施**: 
  - 在测试环境先执行迁移
  - 生产环境迁移前完整备份数据库
  - 准备回滚脚本

### 风险2: 级联删除误删重要数据
- **概率**: 中
- **影响**: 高
- **缓解措施**:
  - 在删除设备/用户前添加确认提示
  - 实现软删除(添加is_deleted字段)
  - 定期自动备份

### 风险3: 并发锁影响性能
- **概率**: 低
- **影响**: 中
- **缓解措施**:
  - 只在库存扣减等关键操作使用锁
  - 监控数据库锁等待时间
  - 考虑使用Redis分布式锁

---

**建议**: 先在开发环境测试所有改动,验证通过后再部署到生产环境。

**下一步**: 创建数据库迁移脚本,逐步实施改进。
