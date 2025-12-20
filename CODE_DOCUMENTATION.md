# 核心代码功能说明

## 目录结构说明

```
app/
├── __init__.py              # Flask应用工厂,初始化所有扩展
├── models.py                # 数据库模型定义(23个核心表)
├── main.py                  # 应用入口(已废弃,使用__init__.py)
│
├── auth/                    # 认证模块
│   ├── __init__.py         # 认证蓝图初始化
│   ├── routes.py           # 登录/登出/密码重置路由
│   └── forms.py            # 登录/注册表单
│
├── main/                    # 主业务模块
│   ├── __init__.py         # 主业务蓝图初始化
│   ├── routes.py           # 核心业务路由(5900+行,包含所有CRUD)
│   ├── approval_history_routes.py  # 审批历史查询
│   ├── workflow_routes.py  # 工作流配置路由
│   ├── asset_routes.py     # 资产管理路由
│   ├── cost_routes.py      # 成本分析路由
│   ├── inventory_routes.py # 库存预警路由
│   ├── lifecycle_routes.py # 生命周期路由
│   └── user_api_routes.py  # 用户API路由
│
├── admin/                   # 管理员模块
│   ├── __init__.py         # 管理员蓝图初始化
│   ├── routes.py           # 管理员专用路由
│   ├── workflow_config_routes.py    # 审批流程配置
│   └── approval_management_routes.py # 审批流程管理
│
├── api/                     # RESTful API(预留)
│   └── __init__.py
│
├── services/                # 业务服务层
│   └── (待完善)
│
├── utils/                   # 工具模块
│   ├── __init__.py
│   ├── db_management.py    # 数据库备份/恢复/重置
│   ├── import_export.py    # 批量导入/导出
│   ├── permission_helpers.py # 权限辅助函数
│   └── qrcode_generator.py  # 二维码生成
│
├── templates/               # Jinja2模板
│   ├── base.html           # 基础模板(导航栏、侧边栏)
│   ├── auth/               # 认证相关模板
│   ├── main/               # 主业务模板
│   └── admin/              # 管理员模板
│
└── static/                  # 静态资源
    ├── css/
    ├── js/
    └── vendor/             # 第三方库
```

---

## 核心文件功能详解

### 1. `app/__init__.py` - 应用工厂

**作用**: 创建和配置Flask应用实例

**核心功能**:
```python
def create_app(config_name='default'):
    """
    应用工厂函数
    
    流程:
    1. 创建Flask实例
    2. 加载配置(config.py)
    3. 初始化扩展(SQLAlchemy, Login, Migrate等)
    4. 注册蓝图(auth, main, admin)
    5. 注册错误处理器
    6. 注册CLI命令
    """
```

**关键扩展**:
- `db`: SQLAlchemy ORM
- `login_manager`: Flask-Login会话管理
- `migrate`: Flask-Migrate数据库迁移
- `csrf`: Flask-WTF CSRF保护

**注册的蓝图**:
```python
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(main_bp)
app.register_blueprint(admin_bp, url_prefix='/admin')
```

---

### 2. `app/models.py` - 数据库模型

**包含23个核心表**:

#### 用户和权限
- `User`: 用户表(登录、角色、部门)
- `Department`: 部门表
- `Role`: 角色表(RBAC)
- `UserModuleAccess`: 用户模块权限
- `AccountRequest`: 账号申请

#### 设备管理
- `Equipment`: 设备主表
- `EquipmentType`: 设备类型
- `EquipmentTransfer`: 设备调拨记录
- `EquipmentScrap`: 设备报废记录
- `EquipmentLoan`: 设备借用记录
- `EquipmentApplication`: 设备申请

#### 配件管理
- `SparePart`: 配件主表
- `SparePartType`: 配件类型
- `PartRequestOrder`: 配件申请单

#### 维修管理
- `RepairOrder`: 维修工单主表
- `repair_order_parts`: 维修工单-配件关联表(多对多)

#### 审批流程
- `WorkflowTemplate`: 流程模板
- `WorkflowNode`: 流程节点
- `ApprovalWorkflow`: 审批实例

#### 成本和分析
- `AssetCost`: 资产成本表
- `Budget`: 预算表

#### 系统功能
- `Notification`: 通知表
- `UserActivityLog`: 操作日志

**关键字段说明**:

**Equipment 设备表**:
```python
class Equipment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))         # 设备名称
    type = db.Column(db.String(50))          # 设备类型
    serial_number = db.Column(db.String(100), unique=True)  # 序列号
    status = db.Column(db.String(20))        # 状态: available/in_use/repair/retired
    department_id = db.Column(db.Integer)    # 所属部门
    user_id = db.Column(db.Integer)          # 当前使用人
    purchase_date = db.Column(db.Date)       # 采购日期
    # ... 更多字段
```

**ApprovalWorkflow 审批流程表**:
```python
class ApprovalWorkflow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_type = db.Column(db.String(50))    # 工单类型
    order_id = db.Column(db.Integer)         # 工单ID
    workflow_node_id = db.Column(db.Integer) # 流程节点ID
    approver_id = db.Column(db.Integer)      # 审批人ID
    status = db.Column(db.String(20))        # pending/approved/rejected/terminated
    repair_cost_input = db.Column(db.Numeric(10, 2))  # 维修金额评估
    admin_action = db.Column(db.String(100)) # 管理员干预操作
    # ... 更多字段
```

---

### 3. `app/main/routes.py` - 主业务路由(5928行)

**这是系统最核心的文件,包含所有主要业务逻辑**

#### 路由分类:

**首页和仪表板**:
- `/` - 首页(动态tiles)
- `/admin_dashboard` - 管理员仪表板
- `/technician_dashboard` - 技术员仪表板

**设备管理**(约500行):
- `/equipment` - 设备列表
- `/equipment/<id>` - 设备详情
- `/equipment/create` - 创建设备
- `/equipment/<id>/edit` - 编辑设备
- `/equipment/<id>/delete` - 删除设备
- `/equipment/<id>/qr` - 生成二维码
- `/equipment/transfer` - 设备调拨
- `/equipment/scrap` - 设备报废
- `/equipment/loan` - 设备借用

**维修工单**(约800行):
- `/repair_orders` - 工单列表
- `/repair_order/<id>` - 工单详情
- `/repair_order/create` - 创建工单
- `/repair_order/<id>/assign` - 分配技术员
- `/repair_order/<id>/complete` - 完成维修
- `/repair_order/<id>/add_parts` - 添加配件
- `/approvals/repair_order/<id>/<action>` - 审批工单

**配件管理**(约400行):
- `/spare_parts` - 配件列表
- `/spare_part/<id>` - 配件详情
- `/spare_part/create` - 创建配件
- `/part_request_orders` - 配件申请列表
- `/part_request_order/create` - 创建申请
- `/approvals/part_order/<id>/<action>` - 审批申请

**审批流程**(约600行):
- `/approvals` - 我的待审批
- `/approvals/repair_order/<id>/<action>` - 审批维修工单
- `/approvals/part_order/<id>/<action>` - 审批配件申请
- `/approvals/equipment_application/<id>/<action>` - 审批设备申请
- `/approvals/loan/<id>/<action>` - 审批借用申请
- `/approvals/transfer/<id>/<action>` - 审批调拨申请
- `/approvals/scrap/<id>/<action>` - 审批报废申请

**用户和部门管理**(约300行):
- `/user_management` - 用户管理
- `/department_management` - 部门管理
- `/account_requests` - 账号申请管理

**导入导出**(约200行):
- `/equipment/import` - 批量导入设备
- `/equipment/export` - 导出设备列表
- `/spare_parts/import` - 批量导入配件
- `/spare_parts/export` - 导出配件列表

**报表和分析**(约300行):
- `/reports` - 报表中心
- `/cost_analysis` - 成本分析
- `/inventory_warning` - 库存预警
- `/lifecycle_dashboard` - 生命周期

**系统功能**(约200行):
- `/notifications` - 通知中心
- `/user_activity_logs` - 操作日志
- `/database_management` - 数据库管理

---

### 4. `app/admin/workflow_config_routes.py` - 审批流程配置

**作用**: 管理员配置审批流程和金额阈值

**核心路由**:

```python
@admin_bp.route('/workflow_config')
def workflow_config():
    """
    审批流程配置主页
    
    功能:
    1. 选择工单类型
    2. 显示该类型的所有审批节点
    3. 显示节点的金额阈值和跳过规则
    """

@admin_bp.route('/workflow_config/add_node', methods=['POST'])
def add_workflow_node():
    """
    添加审批节点
    
    参数:
    - order_type: 工单类型
    - name: 节点名称
    - role_required: 所需角色
    - sequence: 执行序号
    - amount_threshold: 金额阈值(可选)
    - skip_if_below_threshold: 跳过规则
    
    逻辑:
    1. 创建WorkflowNode记录
    2. 关联到对应的WorkflowTemplate
    3. 返回成功/失败
    """

@admin_bp.route('/workflow_config/update_node/<int:node_id>', methods=['POST'])
def update_workflow_node(node_id):
    """
    更新节点配置
    
    支持修改:
    - 节点名称
    - 所需角色
    - 执行序号
    - 金额阈值
    - 跳过规则
    """

@admin_bp.route('/workflow_config/delete_node/<int:node_id>', methods=['POST'])
def delete_workflow_node(node_id):
    """
    删除节点
    
    注意: 删除前检查是否有关联的审批记录
    """
```

**金额阈值判断逻辑**:
```python
# 在创建审批流程时
for node in nodes:
    if node.amount_threshold:
        if node.skip_if_below_threshold:
            # 规则: 金额 < 阈值时跳过
            if order_amount < node.amount_threshold:
                continue  # 跳过该节点
        else:
            # 规则: 金额 >= 阈值时需要
            if order_amount < node.amount_threshold:
                continue  # 跳过该节点
    
    # 创建审批实例
    approval = ApprovalWorkflow(
        workflow_node_id=node.id,
        order_type=order_type,
        order_id=order_id,
        approver_id=find_approver(node.role_required),
        status='pending'
    )
```

---

### 5. `app/admin/approval_management_routes.py` - 审批流程管理

**作用**: 管理员查看和干预所有审批流程

**核心功能**:

```python
@admin_bp.route('/approval_flows')
def approval_flows():
    """
    审批流程管理主页
    
    功能:
    1. 显示所有审批流程(所有工单类型)
    2. 支持筛选(工单类型、审批状态)
    3. 显示当前审批人、节点、状态
    """

@admin_bp.route('/approval_flow/<int:approval_id>')
def approval_flow_detail(approval_id):
    """
    审批流程详情
    
    显示:
    1. 当前审批节点信息
    2. 工单基本信息
    3. 所有审批历史
    4. 管理员干预按钮
    """

@admin_bp.route('/approval_flow/<int:approval_id>/jump_to_node', methods=['POST'])
def jump_to_node(approval_id):
    """
    打回到指定节点
    
    操作:
    1. 终止当前审批
    2. 重新从指定节点创建审批
    3. 记录管理员操作
    4. 发送通知
    """

@admin_bp.route('/approval_flow/<int:approval_id>/skip_node', methods=['POST'])
def skip_node(approval_id):
    """
    跳过当前节点
    
    操作:
    1. 自动批准当前节点
    2. 创建下一个节点的审批
    3. 记录为管理员操作
    """

@admin_bp.route('/approval_flow/<int:approval_id>/reassign', methods=['POST'])
def reassign_approver(approval_id):
    """
    重新分配审批人
    
    操作:
    1. 更新approver_id
    2. 发送通知给新审批人
    3. 记录操作
    """
```

---

### 6. `app/main/approval_history_routes.py` - 审批历史

**作用**: 用户查看自己的审批历史

```python
@bp.route('/approval_history')
def approval_history():
    """
    我的审批历史
    
    查询:
    - approver_id = current_user.id
    
    分类显示:
    - 待审批 (pending)
    - 已批准 (approved)
    - 已拒绝 (rejected)
    - 已终止 (terminated)
    """

@bp.route('/approval_detail/<int:approval_id>')
def approval_detail(approval_id):
    """
    审批详情页
    
    显示:
    1. 审批基本信息
    2. 工单详细信息
    3. 所有审批节点历史
    4. 管理员干预记录(如果有)
    """
```

---

### 7. `app/utils/db_management.py` - 数据库管理

**作用**: 数据库备份/恢复/重置

```python
def backup_database(backup_name=None):
    """
    备份数据库
    
    流程:
    1. 创建backups目录
    2. 复制app.db到backup文件
    3. 命名格式: app.db.backup_YYYYMMDD_HHMMSS
    
    返回: 备份文件路径
    """

def restore_database(backup_file):
    """
    恢复数据库
    
    流程:
    1. 先备份当前数据库
    2. 复制backup文件覆盖app.db
    3. 重启应用(如果在Docker中)
    
    风险: 当前数据会被覆盖
    """

def reset_database():
    """
    重置数据库
    
    警告: 删除所有数据!
    
    流程:
    1. 备份当前数据库
    2. 删除app.db
    3. 重新创建所有表
    4. 创建默认管理员账号
    """
```

---

### 8. `app/utils/import_export.py` - 批量导入导出

**作用**: Excel/CSV批量操作

```python
def import_equipment_from_csv(file):
    """
    从CSV导入设备
    
    步骤:
    1. 读取CSV文件
    2. 验证必填字段
    3. 验证数据格式
    4. 批量插入数据库
    5. 返回成功/失败统计
    
    必填字段:
    - name (设备名称)
    - type (设备类型)
    - serial_number (序列号,唯一)
    """

def export_equipment_to_csv():
    """
    导出设备到CSV
    
    包含字段:
    - 所有Equipment表字段
    - 关联的部门名称
    - 关联的用户名称
    
    返回: CSV文件流
    """
```

---

## 关键业务逻辑详解

### 1. 审批流程自动创建

**触发点**: 提交维修工单/配件申请/设备申请等

```python
def create_approval_workflow(order_type, order_id, order_amount=0):
    """
    创建审批流程实例
    
    参数:
    - order_type: 'repair_order', 'part_request_order'等
    - order_id: 工单ID
    - order_amount: 工单金额(用于阈值判断)
    
    流程:
    1. 查找对应的WorkflowTemplate
    2. 获取所有WorkflowNode(按sequence排序)
    3. 遍历每个节点:
       a. 检查金额阈值条件
       b. 如果不满足跳过条件,创建ApprovalWorkflow
       c. 找到对应角色的审批人
    4. 发送通知给第一个审批人
    """
    
    # 查找流程模板
    template = WorkflowTemplate.query.filter_by(
        order_type=order_type
    ).first()
    
    if not template:
        return False
    
    # 获取所有节点
    nodes = WorkflowNode.query.filter_by(
        template_id=template.id
    ).order_by(WorkflowNode.sequence).all()
    
    for node in nodes:
        # 金额阈值判断
        if node.amount_threshold:
            if node.skip_if_below_threshold:
                # 金额 < 阈值时跳过
                if order_amount < node.amount_threshold:
                    continue
            else:
                # 金额 >= 阈值时需要
                if order_amount < node.amount_threshold:
                    continue
        
        # 找到审批人
        approver = find_approver_by_role(node.role_required)
        
        # 创建审批实例
        approval = ApprovalWorkflow(
            workflow_node_id=node.id,
            order_type=order_type,
            order_id=order_id,
            approver_id=approver.id,
            status='pending'
        )
        db.session.add(approval)
    
    db.session.commit()
    
    # 通知第一个审批人
    send_approval_notification(approvals[0])
```

---

### 2. 审批通过后的后续处理

```python
def handle_approval_approved(approval):
    """
    审批通过后的处理
    
    流程:
    1. 更新当前审批状态为approved
    2. 检查是否还有下一个节点
    3. 如果有下一个节点:
       - 通知下一个审批人
    4. 如果没有下一个节点(全部通过):
       - 更新工单状态
       - 执行工单特定逻辑(如配件出库)
    """
    
    # 更新当前审批
    approval.status = 'approved'
    approval.approved_date = get_beijing_now()
    
    # 查找下一个待审批节点
    next_approval = ApprovalWorkflow.query.filter_by(
        order_type=approval.order_type,
        order_id=approval.order_id,
        status='pending'
    ).order_by(ApprovalWorkflow.created_date).first()
    
    if next_approval:
        # 通知下一个审批人
        send_notification(
            user_id=next_approval.approver_id,
            message=f"您有新的审批待处理"
        )
    else:
        # 所有审批完成
        complete_order(approval.order_type, approval.order_id)
```

---

### 3. 配件出库逻辑

```python
def process_part_request_approval(part_order_id, approved):
    """
    配件申请审批后处理
    
    如果批准:
    1. 扣减库存
    2. 记录出库历史
    3. 更新工单状态为completed
    4. 通知申请人
    
    如果拒绝:
    1. 更新工单状态为rejected
    2. 通知申请人拒绝原因
    """
    
    order = PartRequestOrder.query.get(part_order_id)
    
    if approved:
        # 扣减库存
        part = SparePart.query.get(order.part_id)
        if part.quantity < order.quantity:
            raise Exception("库存不足")
        
        part.quantity -= order.quantity
        
        # 更新状态
        order.status = 'completed'
        
        # 通知
        send_notification(
            user_id=order.requester_id,
            message=f"您的配件申请已批准,请到仓库领取"
        )
    else:
        order.status = 'rejected'
        send_notification(
            user_id=order.requester_id,
            message=f"您的配件申请已被拒绝"
        )
```

---

## 常见问题和解决方案

### Q1: 如何添加新的工单类型?

**步骤**:
1. 创建新的数据库模型(如EquipmentMaintenance)
2. 在WorkflowTemplate中添加新类型
3. 配置审批流程节点
4. 在routes.py中添加CRUD路由
5. 创建对应的模板

### Q2: 如何修改审批流程?

**答**: 使用管理员账号访问:
- 审批 → 金额阈值配置
- 选择工单类型
- 添加/编辑/删除节点
- 设置金额阈值和跳过规则

### Q3: 如何批量导入数据?

**答**:
1. 下载CSV模板
2. 填写数据
3. 在对应页面上传CSV文件
4. 系统自动验证并导入

### Q4: 数据库损坏怎么办?

**答**:
1. 使用备份恢复:
   ```python
   from app.utils.db_management import restore_database
   restore_database('backups/app.db.backup_20251130')
   ```
2. 如果没有备份,只能重置数据库(数据丢失)

---

**文档版本**: v2.0  
**最后更新**: 2025-11-30
