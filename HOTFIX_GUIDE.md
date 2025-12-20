# 高优先级问题修复指南

本文档提供了快速修复系统中发现的高优先级问题的具体代码修改方案。

---

## 问题1: 配件库存并发控制 🔴

### 影响文件
- `app/main/routes.py` (约3222行 和 2932行)

### 修复方案

#### 1.1 修复配件申请审批 (routes.py 约3222行)

**查找代码块**:
```python
def approve_part_order(order_id, action):
    # ... 省略权限检查
    
    if action == 'approve':
        # ... 省略审批逻辑
        next_ = _get_next_pending_approval('part_request_order', order_id)
        if not next_:
            # 所有审批完成
            part_order.status = 'approved'
            
            # ❌ 旧代码: 缺少并发锁
            part = part_order.part
            if part.quantity >= part_order.quantity:
                part.quantity -= part_order.quantity
```

**替换为**:
```python
def approve_part_order(order_id, action):
    try:
        # ... 省略权限检查
        
        if action == 'approve':
            approval.status = 'approved'
            approval.approved_date = get_beijing_now()
            approval.comments = request.form.get('comments', '')
            
            next_ = _get_next_pending_approval('part_request_order', order_id)
            if not next_:
                # ✅ 新代码: 使用悲观锁
                part = db.session.query(SparePart).with_for_update().filter_by(
                    id=part_order.part_id
                ).first()
                
                if not part:
                    raise ValueError("配件不存在")
                
                if part.quantity < part_order.quantity:
                    raise ValueError(f"库存不足! 当前库存:{part.quantity}, 需求:{part_order.quantity}")
                
                # 扣减库存
                part.quantity -= part_order.quantity
                part_order.status = 'approved'
                
                # 检查低库存预警
                if part.low_stock_threshold and part.quantity <= part.low_stock_threshold:
                    admins = User.query.filter_by(role='admin').all()
                    for admin in admins:
                        notification = Notification(
                            user_id=admin.id,
                            title='配件库存预警',
                            message=f'配件 {part.name} 库存不足,当前库存: {part.quantity}'
                        )
                        db.session.add(notification)
                
                # 通知申请人
                note = Notification(
                    user_id=part_order.requester_id,
                    title='配件申请已批准',
                    message=f'您的配件申请 #{part_order.id} 已批准'
                )
                db.session.add(note)
            
            db.session.commit()
            flash('审批成功')
        
        elif action == 'reject':
            approval.status = 'rejected'
            approval.approved_date = get_beijing_now()
            approval.comments = request.form.get('comments', '')
            part_order.status = 'cancelled'
            
            note = Notification(
                user_id=part_order.requester_id,
                title='配件申请被拒绝',
                message=f'您的配件申请 #{part_order.id} 已被拒绝'
            )
            db.session.add(note)
            db.session.commit()
            flash('已拒绝')
    
    except ValueError as e:
        db.session.rollback()
        flash(str(e), 'danger')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'配件申请审批失败: {e}')
        flash('操作失败,请联系管理员', 'danger')
    
    return redirect(url_for('main.approvals'))
```

#### 1.2 修复维修工单添加配件 (routes.py 约2932行)

**查找代码块**:
```python
def add_parts_to_repair(order_id):
    # ... 省略参数获取
    
    # ❌ 旧代码: 缺少并发锁
    part = SparePart.query.get(part_id)
    if part.quantity < quantity:
        flash('配件库存不足')
        return redirect(...)
    
    part.quantity -= quantity
```

**替换为**:
```python
def add_parts_to_repair(order_id):
    try:
        repair_order = RepairOrder.query.get_or_404(order_id)
        
        # 权限检查
        if current_user.role not in ['admin', 'technician']:
            if repair_order.assigned_technician_id != current_user.id:
                abort(403)
        
        part_id = request.form.get('part_id', type=int)
        quantity = request.form.get('quantity', type=int)
        
        if not part_id or not quantity or quantity <= 0:
            flash('请选择配件并输入有效数量', 'warning')
            return redirect(url_for('main.repair_order_detail', id=order_id))
        
        # ✅ 新代码: 使用悲观锁
        part = db.session.query(SparePart).with_for_update().filter_by(
            id=part_id
        ).first()
        
        if not part:
            raise ValueError("配件不存在")
        
        if part.quantity < quantity:
            raise ValueError(f"库存不足! 当前库存:{part.quantity}, 需求:{quantity}")
        
        # 扣减库存
        part.quantity -= quantity
        
        # 添加到工单 (使用原生SQL插入中间表)
        from app.models import repair_order_parts
        db.session.execute(
            repair_order_parts.insert().values(
                repair_order_id=order_id,
                spare_part_id=part_id,
                quantity=quantity,
                price=part.price
            )
        )
        
        db.session.commit()
        flash(f'成功添加配件: {part.name} × {quantity}', 'success')
    
    except ValueError as e:
        db.session.rollback()
        flash(str(e), 'danger')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'添加配件失败: {e}')
        flash('添加配件失败,请联系管理员', 'danger')
    
    return redirect(url_for('main.repair_order_detail', id=order_id))
```

---

## 问题2: 设备借用归还功能缺失 🔴

### 影响文件
- `app/main/routes.py` (新增路由)
- `app/templates/main/equipment_loan_detail.html` (新增模板)

### 修复方案

#### 2.1 添加归还路由 (routes.py)

**在 routes.py 中添加新路由** (建议在 ~4800行 附近):

```python
@bp.route('/equipment/loan/<int:id>/return', methods=['POST'])
@login_required
def return_equipment(id):
    """
    归还借用设备
    
    只有借用人或管理员可以归还
    """
    try:
        loan = EquipmentLoan.query.get_or_404(id)
        
        # 权限检查: 只有借用人或管理员可以归还
        if current_user.role not in ['admin', 'super_admin']:
            if loan.requester_id != current_user.id:
                abort(403)
        
        # 检查是否已归还
        if loan.status == 'returned':
            flash('该设备已归还', 'warning')
            return redirect(url_for('main.index'))
        
        # 检查是否已批准
        if loan.status != 'approved':
            flash('只能归还已批准的借用设备', 'warning')
            return redirect(url_for('main.index'))
        
        # 更新借用记录
        loan.actual_return_date = get_beijing_now()
        loan.status = 'returned'
        
        # 更新设备状态
        equipment = loan.equipment
        equipment.status = 'available'
        
        # 通知管理员
        admins = User.query.filter_by(role='admin').all()
        for admin in admins:
            notification = Notification(
                user_id=admin.id,
                title='设备已归还',
                message=f'用户 {current_user.username} 已归还设备: {equipment.name}'
            )
            db.session.add(notification)
        
        # 记录日志
        _log_activity('归还设备', f'归还设备借用 #{loan.id}, 设备: {equipment.name}')
        
        db.session.commit()
        flash('设备归还成功', 'success')
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'归还设备失败: {e}')
        flash('归还失败,请联系管理员', 'danger')
    
    return redirect(url_for('main.index'))


@bp.route('/my_loans')
@login_required
def my_loans():
    """
    查看我的借用记录
    """
    # 我申请的借用
    my_loans = EquipmentLoan.query.filter_by(
        requester_id=current_user.id
    ).order_by(EquipmentLoan.created_date.desc()).all()
    
    return render_template('main/my_loans.html', 
                         title='我的借用记录',
                         loans=my_loans)
```

#### 2.2 创建借用列表模板

**创建文件**: `app/templates/main/my_loans.html`

```html
{% extends "base.html" %}

{% block content %}
<div class="container mt-4">
    <h2>我的借用记录</h2>
    
    <div class="table-responsive mt-3">
        <table class="table table-striped">
            <thead>
                <tr>
                    <th>借用ID</th>
                    <th>设备名称</th>
                    <th>借用时间</th>
                    <th>计划归还时间</th>
                    <th>实际归还时间</th>
                    <th>状态</th>
                    <th>操作</th>
                </tr>
            </thead>
            <tbody>
                {% for loan in loans %}
                <tr>
                    <td>{{ loan.id }}</td>
                    <td>{{ loan.equipment.name }}</td>
                    <td>{{ loan.start_date.strftime('%Y-%m-%d') if loan.start_date else '-' }}</td>
                    <td>{{ loan.end_date.strftime('%Y-%m-%d') if loan.end_date else '-' }}</td>
                    <td>{{ loan.actual_return_date.strftime('%Y-%m-%d %H:%M') if loan.actual_return_date else '-' }}</td>
                    <td>
                        {% if loan.status == 'submitted' %}
                            <span class="badge badge-secondary">待审批</span>
                        {% elif loan.status == 'approved' %}
                            <span class="badge badge-success">已批准</span>
                        {% elif loan.status == 'returned' %}
                            <span class="badge badge-info">已归还</span>
                        {% elif loan.status == 'cancelled' %}
                            <span class="badge badge-danger">已取消</span>
                        {% endif %}
                    </td>
                    <td>
                        {% if loan.status == 'approved' %}
                        <form method="POST" action="{{ url_for('main.return_equipment', id=loan.id) }}" style="display:inline;">
                            <button type="submit" class="btn btn-sm btn-primary" 
                                    onclick="return confirm('确认归还设备: {{ loan.equipment.name }}?')">
                                归还设备
                            </button>
                        </form>
                        {% endif %}
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>
{% endblock %}
```

#### 2.3 添加导航链接

**修改 base.html** (约150行附近):

在用户菜单中添加"我的借用"链接:

```html
<li class="nav-item dropdown">
    <a class="nav-link dropdown-toggle" href="#" id="navbarDropdown" role="button" 
       data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
        {{ current_user.username }}
    </a>
    <div class="dropdown-menu" aria-labelledby="navbarDropdown">
        <!-- ... 其他菜单项 -->
        <a class="dropdown-item" href="{{ url_for('main.my_loans') }}">我的借用</a>
        <!-- ... -->
    </div>
</li>
```

---

## 问题3: 设备状态更新缺失 🔴

### 影响文件
- `app/main/routes.py` (约2652行, 3037行, 5500行)

### 修复方案

#### 3.1 维修工单创建时更新设备状态

**查找代码块** (routes.py 约2652行):
```python
def create_repair_order():
    # ... 省略前面代码
    
    repair_order = RepairOrder(
        equipment_id=equipment_id,
        description=description,
        requester_id=current_user.id,
        urgency=urgency,
        status='submitted'
    )
    db.session.add(repair_order)
    db.session.flush()
    
    # ❌ 旧代码: 缺少设备状态更新
```

**在 db.session.flush() 后添加**:
```python
    # ✅ 新代码: 更新设备状态为维修中
    equipment = Equipment.query.get(equipment_id)
    if equipment:
        equipment.status = 'repair'
        _log_activity('设备进入维修', f'设备 {equipment.name} 状态变更为维修中 (工单 #{repair_order.id})')
```

#### 3.2 维修完成时恢复设备状态

**查找代码块** (routes.py 约3037行):
```python
def complete_repair_order(order_id):
    # ... 省略前面代码
    
    if new_status == 'completed' and not repair_order.completed_date:
        repair_order.completed_date = get_beijing_now()
        
        # 计算成本
        # ...
        
        # ❌ 旧代码: 缺少设备状态恢复
```

**在成本记录后添加**:
```python
        # ✅ 新代码: 恢复设备状态
        equipment = repair_order.equipment
        if equipment:
            equipment.status = 'available'
            _log_activity('维修完成', f'设备 {equipment.name} 维修完成,状态恢复为可用 (工单 #{repair_order.id})')
```

#### 3.3 借用审批完成时更新设备状态

**查找代码块** (routes.py,搜索 `approve_loan`):
```python
def approve_loan(order_id, action):
    # ... 省略审批逻辑
    
    if action == 'approve':
        # ... 省略前面代码
        next_ = _get_next_pending_approval('equipment_loan', order_id)
        if not next_:
            # 所有审批完成
            loan.status = 'approved'
            
            # ❌ 旧代码: 缺少设备状态更新
```

**在 loan.status = 'approved' 后添加**:
```python
            # ✅ 新代码: 更新设备状态为已借出
            equipment = loan.equipment
            if equipment:
                equipment.status = 'loaned'
                _log_activity('设备借出', f'设备 {equipment.name} 已借出给 {loan.requester.username} (借用 #{loan.id})')
```

---

## 问题4: 异常处理完善 🟡

### 影响文件
- 所有审批相关路由 (routes.py)

### 修复模式

**标准异常处理模板**:

```python
@bp.route('/some_route', methods=['POST'])
@login_required
def some_function():
    try:
        # 业务逻辑
        # ...
        
        db.session.commit()
        flash('操作成功', 'success')
        return redirect(url_for('main.index'))
    
    except ValueError as e:
        # 业务逻辑错误 (如库存不足)
        db.session.rollback()
        flash(str(e), 'warning')
        return redirect(request.referrer or url_for('main.index'))
    
    except IntegrityError as e:
        # 数据库完整性错误 (如唯一约束冲突)
        db.session.rollback()
        current_app.logger.error(f'数据库完整性错误: {e}')
        flash('数据冲突,请检查后重试', 'danger')
        return redirect(request.referrer or url_for('main.index'))
    
    except Exception as e:
        # 其他未知错误
        db.session.rollback()
        current_app.logger.error(f'操作失败: {e}', exc_info=True)
        flash('操作失败,请联系管理员', 'danger')
        return redirect(request.referrer or url_for('main.index'))
```

**需要添加异常处理的路由**:
- `approve_repair_order`
- `approve_part_order` (已在问题1中修复)
- `approve_transfer`
- `approve_scrap`
- `approve_loan`
- `approve_equipment_application`
- `create_repair_order`
- `assign_repair_order`
- `add_parts_to_repair` (已在问题1中修复)

---

## 实施步骤

### 步骤1: 备份代码和数据库

```bash
# 备份数据库
python -c "from app.utils.db_management import backup_database; backup_database('before_hotfix_20251130')"

# 备份关键文件
cp app/main/routes.py app/main/routes.py.backup_20251130
```

### 步骤2: 应用修复

按以下顺序修改代码:

1. ✅ 修复配件库存并发控制 (问题1)
2. ✅ 添加设备归还功能 (问题2)
3. ✅ 修复设备状态更新 (问题3)
4. ✅ 添加异常处理 (问题4)

### 步骤3: 测试验证

```python
# 测试脚本: tests/test_hotfix.py

def test_concurrent_inventory():
    """测试并发库存扣减"""
    # 创建配件,库存10
    # 两个请求同时扣减8和5
    # 预期: 一个成功,一个失败

def test_equipment_return():
    """测试设备归还"""
    # 创建借用记录
    # 调用归还接口
    # 验证状态变为returned
    # 验证设备状态变为available

def test_repair_equipment_status():
    """测试维修时设备状态"""
    # 创建维修工单
    # 验证设备状态变为repair
    # 完成维修
    # 验证设备状态变为available
```

运行测试:
```bash
pytest tests/test_hotfix.py -v
```

### 步骤4: 部署

```bash
# 1. 停止服务
docker-compose stop

# 2. 更新代码
git pull  # 如果使用Git

# 3. 重启服务
docker-compose up -d

# 4. 查看日志
docker-compose logs -f --tail=100
```

### 步骤5: 验证

手动测试以下场景:

- [ ] 两个用户同时申请相同配件 (库存不足时应拒绝第二个)
- [ ] 借用设备后归还
- [ ] 创建维修工单,设备状态变为维修中
- [ ] 完成维修,设备状态恢复为可用
- [ ] 故意触发错误 (如库存不足),检查是否有友好提示

---

## 回滚方案

如果修复后出现问题,执行以下回滚:

```bash
# 1. 恢复代码
cp app/main/routes.py.backup_20251130 app/main/routes.py

# 2. 恢复数据库
python -c "from app.utils.db_management import restore_database; restore_database('backups/before_hotfix_20251130.db')"

# 3. 重启服务
docker-compose restart
```

---

## 联系支持

如有问题,请查阅:
- `SYSTEM_AUDIT_SUMMARY.md` - 完整审计报告
- `BUSINESS_LOOP_AUDIT.md` - 业务流程详细分析
- `DATABASE_INTEGRITY_IMPROVEMENTS.md` - 数据库优化建议

或联系开发团队。

---

**最后更新**: 2025-11-30  
**预计修复时间**: 4-6小时  
**建议修复人员**: 熟悉Flask和SQLAlchemy的后端开发
