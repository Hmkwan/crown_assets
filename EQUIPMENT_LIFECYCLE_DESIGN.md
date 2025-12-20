# 设备生命周期管理系统设计方案

## 📋 当前系统功能分析

### ✅ 已实现的功能模块

#### 1. **维修工单管理**
- 路由: `/repair_orders`
- 状态流转: submitted → department_head_approved → admin_approved → in_progress → completed
- 功能: 完整的审批流程、技术员分配、成本记录
- **状态**: ✅ 功能完整

#### 2. **设备调拨管理**
- 路由: `/equipment_transfers`
- 状态流转: pending → approved → completed
- 功能: 跨部门设备转移、审批流程
- **状态**: ✅ 功能完整

#### 3. **配件申请管理**
- 路由: `/part_request_orders`
- 状态流转: pending → approved → completed → rejected
- 功能: 配件需求申请、审批、库存管理
- **状态**: ✅ 功能完整

#### 4. **设备借用管理**
- 路由: `/create_loan_request`, `/loan_requests`, `/my_loans`
- 状态流转: submitted → approved → borrowed → returned → (rejected/cancelled)
- 功能:
  - ✅ 借用申请创建
  - ✅ 审批流程
  - ✅ 标记为已借出
  - ✅ 归还功能 (简单归还,无需审批)
  - ⚠️ **问题**: 归还流程过于简单,缺少验收环节
- **状态**: ⚠️ 功能存在但需要完善

#### 5. **设备报废管理**
- 路由: `/create_scrap`, `/admin_scraps`
- 状态: submitted → approved → (rejected)
- 功能:
  - ✅ 报废申请创建
  - ✅ 审批流程
  - ⚠️ **问题**: 审批后没有自动更新设备状态为 'scrapped'
  - ⚠️ **问题**: 缺少报废资产核销功能
  - ⚠️ **问题**: 缺少报废统计报表
- **状态**: ⚠️ 功能不完整

### ❌ 缺失的功能模块

#### 1. **设备采购申请**
- **需求**: 新设备采购流程
- **流程**: 申请 → 部门审批 → 预算审批 → 采购 → 验收 → 入库
- **状态**: ❌ 未实现

#### 2. **设备验收管理**
- **需求**: 新设备/维修后/借用归还的验收流程
- **流程**: 验收申请 → 验收检查 → 验收报告 → 入库/归档
- **状态**: ❌ 未实现

#### 3. **设备盘点管理**
- **需求**: 定期资产盘点
- **流程**: 创建盘点任务 → 盘点执行 → 差异分析 → 调整记录
- **状态**: ❌ 未实现

#### 4. **设备保养计划**
- **需求**: 预防性维护计划
- **流程**: 制定保养计划 → 自动提醒 → 执行保养 → 记录保养
- **状态**: ❌ 未实现

---

## 🎯 核心问题与解决方案

### 问题1: 设备借用归还流程设计

#### 当前问题:
```python
# 现有归还逻辑(routes.py line 5298)
@bp.route('/equipment/loan/<int:id>/return', methods=['POST'])
def return_equipment(id):
    # 直接更新状态,无验收环节
    loan.status = 'returned'
    equipment.status = 'available'
```

**缺陷**:
1. ❌ 归还时无法检查设备状态(是否损坏)
2. ❌ 无法记录设备归还时的备注信息
3. ❌ 没有管理员验收环节
4. ❌ 无法处理设备损坏/丢失情况

#### 🔧 改进方案A: 简单归还模式 (快速归还)

**适用场景**: 短期借用、内部借用、低价值设备

```
流程: 借用人发起归还 → 系统自动处理 → 通知管理员
```

**实现**:
- 保持现有简单归还流程
- 添加归还备注功能
- 归还后设备自动变为 'available'
- 如有问题,管理员事后处理

**优点**: 
- ✅ 快速高效
- ✅ 适合日常借用
- ✅ 减少管理员工作量

**缺点**:
- ❌ 无法及时发现设备损坏
- ❌ 责任追溯不严格

#### 🔧 改进方案B: 验收归还模式 (严格管理)

**适用场景**: 贵重设备、跨部门借用、长期借用

```
流程: 
1. 借用人发起归还申请 (填写归还说明,设备状态)
2. 管理员验收 (检查设备,确认状态)
3. 验收通过 → 设备状态更新为 'available'
4. 验收不通过 → 标记为 'damaged',触发维修流程
```

**实现**:
```python
# 新增状态
loan.status 新增: 'return_pending' (待验收)
# 新增字段
loan.return_notes = db.Column(db.Text)  # 归还说明
loan.return_condition = db.Column(db.String(64))  # 设备状态: good/damaged/lost
loan.inspected_by = db.Column(db.Integer, db.ForeignKey('app_user.id'))  # 验收人
loan.inspection_notes = db.Column(db.Text)  # 验收备注
```

**优点**:
- ✅ 设备状态可控
- ✅ 责任追溯清晰
- ✅ 可及时发现问题

**缺点**:
- ❌ 流程较长
- ❌ 管理员工作量增加

#### 🎯 **推荐方案: 混合模式 (灵活配置)**

根据设备价值/类别自动选择归还模式:

```python
# 设备表添加字段
equipment.require_return_inspection = db.Column(db.Boolean, default=False)

# 归还逻辑
if equipment.require_return_inspection or equipment.price > 5000:
    # 走验收流程
    loan.status = 'return_pending'
else:
    # 走快速归还
    loan.status = 'returned'
    equipment.status = 'available'
```

---

### 问题2: 设备报废流程完善

#### 当前问题:
```python
# 报废审批通过后(routes.py line 6082)
# ❌ 没有更新设备状态
# ❌ 没有记录到资产生命周期
# ❌ 没有生成报废统计
```

#### 🔧 完善方案:

```python
# 报废审批通过后应该:
1. 更新设备状态: equipment.status = 'scrapped'
2. 记录生命周期事件:
   AssetLifecycle(
       equipment_id=equipment.id,
       event_type='scrap',
       description=f'设备报废: {scrap.description}',
       cost=0,
       event_date=datetime.now()
   )
3. 更新设备所属部门为 None (已报废不属于任何部门)
4. 生成报废资产清单
5. 通知财务部门进行资产核销
```

---

### 问题3: 设备借用与申请的关系

#### 当前系统:
- **EquipmentApplication**: 公开仓库设备申请(申请后设备调拨)
- **EquipmentLoan**: 设备借用(临时借用,需归还)

#### 差异对比:

| 特性 | EquipmentApplication | EquipmentLoan |
|------|---------------------|---------------|
| 用途 | 申请公开仓库设备(长期使用) | 临时借用设备 |
| 设备来源 | is_public_pool=True | 任何设备 |
| 归属变更 | ✅ 设备部门会变更 | ❌ 设备部门不变 |
| 需要归还 | ❌ 无需归还 | ✅ 必须归还 |
| 状态影响 | status变为'active' | status变为'loaned' |
| 流程复杂度 | 简单(submitted→approved) | 复杂(approved→borrowed→returned) |

#### 🎯 **建议**: 保持分离,两者职责不同

---

## 🏗️ 完整的设备生命周期状态图

```
                    [采购申请]
                        ↓
                    [验收入库]
                        ↓
    ┌─────────────── [available 可用] ───────────────┐
    │                    ↓                             │
    │         ┌──────────┴──────────┐                │
    │         ↓                     ↓                 │
    │    [申请使用]            [借用申请]             │
    │         ↓                     ↓                 │
    │    [active 使用中]      [loaned 已借出]        │
    │         ↓                     ↓                 │
    │         │                [归还验收]              │
    │         │                     ↓                 │
    │    [故障/损坏]           [returned]             │
    │         ↓                                       │
    │    [repair 维修中] ─────────┐                  │
    │         ↓                    │                  │
    │    [维修完成] ───────────────┴──────────────────┘
    │         
    ├──→ [idle 闲置] ────────────────────────────────┐
    │                                                  │
    ├──→ [maintenance 维护中] ────────────────────────┤
    │                                                  │
    └──→ [报废申请] → [scrapped 已报废]               │
                                                       │
         [调拨流程] ──────────────────────────────────┘
```

---

## 📝 数据库模型改进建议

### 1. EquipmentLoan 表增强

```python
class EquipmentLoan(db.Model):
    # ... 现有字段 ...
    
    # 🆕 归还验收相关字段
    return_request_date = db.Column(db.DateTime)  # 归还申请时间
    return_notes = db.Column(db.Text)  # 归还说明
    return_condition = db.Column(db.String(64))  # good/damaged/lost
    
    inspected_by = db.Column(db.Integer, db.ForeignKey('app_user.id'))  # 验收人
    inspection_date = db.Column(db.DateTime)  # 验收时间
    inspection_notes = db.Column(db.Text)  # 验收备注
    inspection_result = db.Column(db.String(64))  # passed/failed/requires_repair
    
    # 🆕 损坏赔偿相关
    damage_compensation = db.Column(db.Float, default=0)  # 赔偿金额
    damage_description = db.Column(db.Text)  # 损坏描述
    
    # 关联关系
    inspector = db.relationship('User', foreign_keys=[inspected_by], backref='inspected_loans')
```

### 2. EquipmentScrap 表增强

```python
class EquipmentScrap(db.Model):
    # ... 现有字段 ...
    
    # 🆕 审批相关
    approved_by = db.Column(db.Integer, db.ForeignKey('app_user.id'))
    approved_date = db.Column(db.DateTime)
    rejection_reason = db.Column(db.Text)
    
    # 🆕 报废处理
    scrap_value = db.Column(db.Float)  # 残值
    disposal_method = db.Column(db.String(64))  # 处置方式: recycle/donate/destroy
    disposal_date = db.Column(db.DateTime)  # 实际报废日期
    disposal_notes = db.Column(db.Text)
    
    # 🆕 财务核销
    financial_cleared = db.Column(db.Boolean, default=False)
    cleared_by = db.Column(db.Integer, db.ForeignKey('app_user.id'))
    cleared_date = db.Column(db.DateTime)
```

### 3. Equipment 表增强

```python
class Equipment(db.Model):
    # ... 现有字段 ...
    
    # 🆕 借用管理配置
    require_return_inspection = db.Column(db.Boolean, default=False)  # 归还是否需要验收
    allow_loan = db.Column(db.Boolean, default=True)  # 是否允许借用
    
    # 🆕 保养管理
    last_maintenance_date = db.Column(db.Date)  # 上次保养日期
    next_maintenance_date = db.Column(db.Date)  # 下次保养日期
    maintenance_interval_days = db.Column(db.Integer)  # 保养周期(天)
    
    # 🆕 资产信息
    scrap_date = db.Column(db.Date)  # 报废日期
    scrap_reason = db.Column(db.Text)  # 报废原因
```

---

## 🔄 建议的工单状态统一标准

### 维修工单 (RepairOrder)
```
submitted → department_head_approved → admin_approved → 
in_progress → completed / rejected / cancelled
```

### 借用申请 (EquipmentLoan)
```
submitted → approved → borrowed → return_pending → 
inspected → returned / rejected / cancelled
```

### 报废申请 (EquipmentScrap)
```
submitted → approved → disposed → financial_cleared / rejected
```

### 调拨申请 (EquipmentTransfer)
```
pending → approved → completed / rejected
```

### 配件申请 (PartRequestOrder)
```
pending → approved → completed / rejected
```

---

## 🎨 新增功能路由规划

### 借用管理路由增强

```python
# 现有路由
/create_loan_request          # 创建借用申请
/loan_requests               # 借用申请列表(管理员)
/my_loans                    # 我的借用记录
/approvals/loan/<id>/<action> # 审批借用

# 🆕 新增路由
/loans/<id>/request_return    # 发起归还申请
/loans/<id>/inspect           # 验收归还
/loans/return_pending         # 待验收列表
/loans/<id>/mark_damaged      # 标记为损坏
/loans/<id>/compensation      # 处理赔偿
```

### 报废管理路由增强

```python
# 现有路由
/create_scrap                # 创建报废申请
/admin_scraps               # 报废申请列表

# 🆕 新增路由
/scraps/<id>/disposal        # 处置报废设备
/scraps/<id>/financial_clear # 财务核销
/scraps/statistics           # 报废统计报表
/scraps/export              # 导出报废清单
```

---

## 📊 统计报表增强

### 新增报表类型

1. **借用归还报表**
   - 借用中设备清单
   - 逾期未归还列表
   - 借用频率统计
   - 设备损坏率统计

2. **报废资产报表**
   - 报废设备清单
   - 报废原因分析
   - 报废资产价值统计
   - 年度报废趋势

3. **设备健康度报表**
   - 维修频率
   - 故障率分析
   - 保养执行率
   - 设备生命周期成本

---

## ✅ 实施优先级建议

### P0 - 紧急修复 (本周完成)
1. ✅ 修复报废审批后设备状态不更新的问题
2. ✅ 完善借用归还流程(添加归还备注)
3. ✅ 添加报废统计报表

### P1 - 重要优化 (本月完成)
1. 🔄 实现借用归还验收流程
2. 🔄 添加设备损坏处理流程
3. 🔄 完善报废流程(处置+核销)

### P2 - 功能增强 (下月完成)
1. 📅 设备保养计划管理
2. 📅 设备盘点功能
3. 📅 设备验收管理

### P3 - 长期规划 (季度完成)
1. 📅 设备采购申请流程
2. 📅 设备生命周期成本分析
3. 📅 智能预警系统(逾期、保养提醒)

---

## 🔍 关键业务逻辑伪代码

### 1. 借用归还验收流程

```python
# Step 1: 借用人发起归还申请
@bp.route('/loans/<id>/request_return', methods=['POST'])
def request_loan_return(id):
    loan = EquipmentLoan.query.get_or_404(id)
    
    # 更新状态
    loan.status = 'return_pending'
    loan.return_request_date = now()
    loan.return_notes = request.form.get('notes')
    loan.return_condition = request.form.get('condition')  # good/damaged
    
    # 通知管理员
    notify_admins('设备待验收', f'{user}申请归还{equipment.name}')
    
    return redirect('/my_loans')


# Step 2: 管理员验收
@bp.route('/loans/<id>/inspect', methods=['POST'])
def inspect_loan_return(id):
    loan = EquipmentLoan.query.get_or_404(id)
    
    result = request.form.get('result')  # passed/failed/requires_repair
    
    if result == 'passed':
        # 验收通过
        loan.status = 'returned'
        loan.equipment.status = 'available'
    elif result == 'requires_repair':
        # 需要维修
        loan.status = 'returned'
        loan.equipment.status = 'repair'
        # 自动创建维修工单
        create_repair_order(loan.equipment, loan.return_notes)
    else:
        # 验收失败(损坏/丢失)
        loan.status = 'returned'
        loan.equipment.status = 'damaged'
        # 计算赔偿
        calculate_compensation(loan)
    
    loan.inspection_result = result
    loan.inspected_by = current_user.id
    loan.inspection_date = now()
    
    return redirect('/loans/return_pending')
```

### 2. 报废完整流程

```python
# Step 1: 报废审批通过
@bp.route('/approvals/scrap/<id>/approve', methods=['POST'])
def approve_scrap(id):
    scrap = EquipmentScrap.query.get_or_404(id)
    
    # 更新报废申请状态
    scrap.status = 'approved'
    scrap.approved_by = current_user.id
    scrap.approved_date = now()
    
    # 🔑 更新设备状态
    equipment = scrap.equipment
    equipment.status = 'scrapped'
    equipment.scrap_date = now()
    equipment.scrap_reason = scrap.description
    
    # 记录生命周期事件
    lifecycle_event = AssetLifecycle(
        equipment_id=equipment.id,
        event_type='scrap',
        description=f'设备报废审批通过: {scrap.description}',
        event_date=now()
    )
    db.session.add(lifecycle_event)
    
    # 通知财务部门
    notify_finance_dept('设备报废待核销', equipment)
    
    return redirect('/admin_scraps')


# Step 2: 报废处置
@bp.route('/scraps/<id>/disposal', methods=['POST'])
def dispose_scrap(id):
    scrap = EquipmentScrap.query.get_or_404(id)
    
    scrap.disposal_method = request.form.get('method')  # recycle/donate/destroy
    scrap.scrap_value = request.form.get('value', 0)
    scrap.disposal_date = now()
    scrap.disposal_notes = request.form.get('notes')
    scrap.status = 'disposed'
    
    return redirect('/admin_scraps')


# Step 3: 财务核销
@bp.route('/scraps/<id>/financial_clear', methods=['POST'])
def financial_clear_scrap(id):
    scrap = EquipmentScrap.query.get_or_404(id)
    
    scrap.financial_cleared = True
    scrap.cleared_by = current_user.id
    scrap.cleared_date = now()
    scrap.status = 'financial_cleared'
    
    # 记录到资产生命周期
    lifecycle_event = AssetLifecycle(
        equipment_id=scrap.equipment_id,
        event_type='financial_clear',
        description='报废资产财务核销完成',
        cost=-scrap.equipment.price if scrap.equipment else 0,
        event_date=now()
    )
    db.session.add(lifecycle_event)
    
    return redirect('/admin_scraps')
```

---

## 📱 用户界面优化建议

### 1. 设备详情页添加快捷操作

```html
<div class="equipment-actions">
    {% if equipment.status == 'available' %}
        <button>申请使用</button>
        <button>申请借用</button>
    {% elif equipment.status == 'active' %}
        <button>报修</button>
        <button>申请调拨</button>
        <button>申请报废</button>
    {% elif equipment.status == 'loaned' and loan.requester_id == current_user.id %}
        <button>申请归还</button>
    {% endif %}
</div>
```

### 2. 我的借用页面增强

```html
<div class="loan-status">
    {% if loan.status == 'borrowed' %}
        <span class="badge badge-warning">借用中</span>
        <button onclick="requestReturn({{ loan.id }})">申请归还</button>
        
        {% if loan.end_date < now() %}
            <span class="badge badge-danger">已逾期</span>
        {% endif %}
    {% elif loan.status == 'return_pending' %}
        <span class="badge badge-info">待验收</span>
        <p>归还说明: {{ loan.return_notes }}</p>
    {% endif %}
</div>
```

---

## 🎯 总结与建议

### 当前系统评估
- ✅ 基础工单管理功能完整
- ✅ 审批流程设计合理
- ⚠️ 借用归还流程需要完善
- ⚠️ 报废流程不完整
- ❌ 缺少保养、盘点等高级功能

### 优先改进方向
1. **立即修复**: 报废审批后更新设备状态
2. **重点优化**: 借用归还验收流程
3. **逐步完善**: 添加保养计划、盘点管理

### 技术债务
- 需要统一各类工单的状态命名规范
- 需要完善资产生命周期记录
- 建议添加更多自动化通知和提醒

---

**文档版本**: v1.0  
**创建日期**: 2025-12-04  
**最后更新**: 2025-12-04
