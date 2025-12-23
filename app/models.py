from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, get_beijing_now
import pytz



class User(UserMixin, db.Model):
    __tablename__ = 'app_user'  # 避免PostgreSQL保留关键字user冲突
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(256))  # 增加长度以支持scrypt哈希(175字符)
    role = db.Column(db.String(64), default='user')  # 'admin', 'user', 'technician', 'department_head'
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'))
    department = db.Column(db.String(120))
    is_active = db.Column(db.Boolean, default=True)  # 用户是否活跃（用于选择审批人时过滤）
    
    # 审批流角色（可多选，JSON格式存储）
    # 例如: '["department_head", "procurement"]' 表示该用户既是部门经理又是采购
    workflow_roles = db.Column(db.Text, nullable=True)  # JSON array of roles
    
    # 用户模块权限
    can_manage_equipment = db.Column(db.Boolean, default=False)
    can_manage_spare_parts = db.Column(db.Boolean, default=False)
    can_manage_repairs = db.Column(db.Boolean, default=False)
    can_manage_part_requests = db.Column(db.Boolean, default=False)
    can_view_workflow = db.Column(db.Boolean, default=False)
    can_edit_workflow = db.Column(db.Boolean, default=False)  # 编辑/创建工作流节点
    can_manage_workflow_templates = db.Column(db.Boolean, default=False)  # 管理工作流模板
    can_view_reports = db.Column(db.Boolean, default=False)
    can_view_logs = db.Column(db.Boolean, default=False)
    
    @property
    def custom_roles(self):
        """获取用户的所有活跃自定义角色"""
        try:
            assignments = UserCustomRole.query.filter_by(
                user_id=self.id, 
                is_active=True
            ).all()
            return [assignment.role for assignment in assignments if assignment.role and assignment.role.is_active]
        except:
            return []
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
        
    def is_admin(self):
        return self.role == 'admin'
        
    def is_department_head(self):
        return self.role == 'department_head'

    def get_department_name(self):
        """返回用户所属部门的显示名称。
        优先返回关联的 Department 对象的 name 字段，若不存在则回退到 `department` 文本字段，最后返回空字符串。
        这样可以避免模板中直接调用未定义方法导致的错误。
        """
        try:
            if hasattr(self, 'dept') and self.dept:
                return getattr(self.dept, 'name', '') or ''
            return self.department or ''
        except Exception:
            return ''

    def get_role_display(self):
        """将内部 role 值映射为中文显示文本。"""
        mapping = {
            'admin': '管理员',
            'user': '普通用户',
            'technician': '技术员',
            'department_head': '部门主管'
        }
        return mapping.get(self.role, self.role or '')
    
    def get_workflow_roles(self):
        """获取用户的审批流角色列表"""
        if not self.workflow_roles:
            # 如果没有设置workflow_roles，根据role字段自动映射
            role_mapping = {
                'admin': ['admin'],
                'department_head': ['department_head'],
                'technician': ['admin'],  # 技术员默认有IT管理员权限
            }
            return role_mapping.get(self.role, ['employee'])
        
        try:
            import json
            roles = json.loads(self.workflow_roles)
            return roles if isinstance(roles, list) else []
        except Exception:
            return []
    
    def has_workflow_role(self, role):
        """检查用户是否拥有指定的审批流角色"""
        return role in self.get_workflow_roles()
    
    def set_workflow_roles(self, roles):
        """设置用户的审批流角色"""
        import json
        if isinstance(roles, list):
            self.workflow_roles = json.dumps(roles)
        else:
            self.workflow_roles = None
    
    def get_workflow_roles_display(self):
        """获取审批流角色的中文显示"""
        role_display_mapping = {
            'employee': '员工',
            'department_head': '部门经理',
            'admin': '系统管理员',
            'procurement': '采购',
            'warehouse': '库房',
            'security': '安全/合规',
            'finance': '财务',
            'executive': '总经理/高层',
            'auditor': '审计/稽核'
        }
        roles = self.get_workflow_roles()
        return ', '.join([role_display_mapping.get(r, r) for r in roles])

    @property
    def name(self):
        """容错的显示姓名属性，优先 full_name，否则 username。"""
        return getattr(self, 'full_name', None) or self.username
        
    def has_module_access(self, module):
        """检查用户是否具有特定模块的访问权限"""
        # 兼容性: 有些测试/代码会将 is_admin 作为布尔字段注入实例（is_admin=True），
        # 也有代码通过方法 is_admin() 查询。这里兼容两种情况。
        admin_check = getattr(self, 'is_admin', None)
        if callable(admin_check):
            if admin_check():
                return True
        elif admin_check:
            return True

        module_permissions = {
            'equipment': self.can_manage_equipment,
            'spare_parts': self.can_manage_spare_parts,
            'repairs': self.can_manage_repairs,
            'part_requests': self.can_manage_part_requests,
            'workflow': getattr(self, 'can_view_workflow', False),
            'workflow_edit': getattr(self, 'can_edit_workflow', False),
            'workflow_templates': getattr(self, 'can_manage_workflow_templates', False),
            'reports': getattr(self, 'can_view_reports', False),
            'logs': getattr(self, 'can_view_logs', False)
        }
        
        return module_permissions.get(module, False)
    
    def has_permission(self, module, action, context=None):
        """
        检查用户是否具有特定的模块+操作权限(细粒度控制)
        
        Args:
            module: 模块名(如'equipment', 'repair', 'announcement')
            action: 操作名(如'view', 'create', 'edit', 'delete', 'approve', 'publish')
            context: 上下文条件字典(如{'department_id': 1, 'amount': 5000})
        
        Returns:
            bool: 是否有权限
        """
        if self.is_admin():
            return True
        
        context = context or {}
        
        # 先检查传统权限标志
        if self.has_module_access(module):
            return True
        
        # 检查自定义角色权限
        try:
            from app.models import Permission
            
            # 获取用户的所有活跃角色
            for assignment in self.role_assignments:
                if not assignment.is_active:
                    continue
                    
                # 检查角色的所有权限
                for perm in assignment.role.permissions:
                    if perm.module == module and perm.action == action and perm.is_granted:
                        if perm.check_condition(context):
                            return True
        except Exception as e:
            # 静默失败,避免权限检查时出错
            pass
        
        return False
    
    def get_all_permissions(self):
        """获取用户的所有权限(模块+操作)"""
        if self.is_admin():
            return {
                'equipment': ['view', 'create', 'edit', 'delete'],
                'repair': ['view', 'create', 'edit', 'approve', 'complete'],
                'loan': ['view', 'create', 'approve', 'return'],
                'transfer': ['view', 'create', 'approve'],
                'scrap': ['view', 'create', 'approve'],
                'report': ['view', 'export'],
                'announcement': ['view', 'create', 'edit', 'delete', 'publish'],
                'wework': ['view', 'config', 'sync'],
            }
        
        perms = {}
        try:
            # 遍历用户的所有活跃角色
            for assignment in self.role_assignments:
                if not assignment.is_active:
                    continue
                    
                # 获取角色的所有权限
                for perm in assignment.role.permissions:
                    if perm.is_granted:
                        if perm.module not in perms:
                            perms[perm.module] = []
                        if perm.action not in perms[perm.module]:
                            perms[perm.module].append(perm.action)
        except Exception:
            pass
        
        return perms
        
    def __repr__(self):
        return f'<User {self.username}>'


class Equipment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), index=True)
    type_id = db.Column(db.Integer, db.ForeignKey('equipment_type.id'))  # 添加设备类型外键
    type = db.Column(db.String(64))  # 保留原有type字段以兼容旧数据
    brand = db.Column(db.String(64))
    model = db.Column(db.String(64))
    serial_number = db.Column(db.String(120), unique=True)
    equipment_number = db.Column(db.String(120))  # 设备编号
    purchase_date = db.Column(db.Date)
    price = db.Column(db.Float, default=0.0)  # 设备金额，用于成本分析
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'))
    department = db.Column(db.String(120))
    location = db.Column(db.String(120))  # 存放位置
    status = db.Column(db.String(64), default='active')  # active, repair, retired, available
    is_public_pool = db.Column(db.Boolean, default=False)
    
    # 🆕 借用管理配置
    require_return_inspection = db.Column(db.Boolean, default=False)  # 归还是否需要验收
    allow_loan = db.Column(db.Boolean, default=True)  # 是否允许借用
    
    # 关联设备类型
    equipment_type = db.relationship('EquipmentType', backref='equipments')
    
    def __repr__(self):
        return f'<Equipment {self.name}>'


class RepairOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'))
    requester_id = db.Column(db.Integer, db.ForeignKey('app_user.id'))
    technician_id = db.Column(db.Integer, db.ForeignKey('app_user.id'))
    department_head_id = db.Column(db.Integer, db.ForeignKey('app_user.id'))  # 部门领导审批人
    admin_id = db.Column(db.Integer, db.ForeignKey('app_user.id'))  # 管理员审批人
    
    description = db.Column(db.Text)
    repair_cost = db.Column(db.Float, default=0.00)  # 维修金额
    status = db.Column(db.String(64), default='submitted')  # submitted, department_head_approved, admin_approved, in_progress, completed, cancelled
    
    # 时间字段
    created_date = db.Column(db.DateTime, default=get_beijing_now)
    updated_date = db.Column(db.DateTime, default=get_beijing_now, onupdate=get_beijing_now)
    completed_date = db.Column(db.DateTime)
    
    # 审批状态
    department_head_approved = db.Column(db.Boolean, default=False)
    admin_approved = db.Column(db.Boolean, default=False)
    
    # 关联关系
    equipment = db.relationship('Equipment', backref='repair_orders')
    requester = db.relationship('User', foreign_keys=[requester_id], backref='requested_orders')
    technician = db.relationship('User', foreign_keys=[technician_id], backref='assigned_orders')
    department_head = db.relationship('User', foreign_keys=[department_head_id], backref='department_head_approved_orders')
    admin = db.relationship('User', foreign_keys=[admin_id], backref='admin_approved_orders')
    
    def __repr__(self):
        return f'<RepairOrder {self.id}>'


class SparePart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), index=True)
    part_number = db.Column(db.String(120), unique=True)
    type_id = db.Column(db.Integer, db.ForeignKey('spare_part_type.id'))  # 配件类型ID
    price = db.Column(db.Float)
    stock_quantity = db.Column(db.Integer, default=0)
    min_stock_level = db.Column(db.Integer, default=10)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'))
    department = db.Column(db.String(120))
    location = db.Column(db.String(120))
    purchase_date = db.Column(db.Date)
    is_public = db.Column(db.Boolean, default=False)  # 是否公开到仓库
    
    # 关系
    spare_part_type = db.relationship('SparePartType', backref='spare_parts', foreign_keys=[type_id])
    
    def __repr__(self):
        return f'<SparePart {self.name}>'


class PartReplacement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    repair_order_id = db.Column(db.Integer, db.ForeignKey('repair_order.id'))
    spare_part_id = db.Column(db.Integer, db.ForeignKey('spare_part.id'))
    quantity = db.Column(db.Integer, default=1)
    replacement_date = db.Column(db.DateTime, default=get_beijing_now)
    
    # 关联关系
    repair_order = db.relationship('RepairOrder', backref='part_replacements')
    spare_part = db.relationship('SparePart', backref='part_replacements')
    
    def __repr__(self):
        return f'<PartReplacement {self.id}>'


class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True)
    code = db.Column(db.String(64), unique=True)
    cost_center = db.Column(db.String(64))
    location = db.Column(db.String(120))
    description = db.Column(db.Text)
    
    users = db.relationship('User', backref='dept')
    equipment = db.relationship('Equipment', backref='dept')
    spare_parts = db.relationship('SparePart', backref='dept')
    
    def __repr__(self):
        return f'<Department {self.name}>'


class PartRequestOrder(db.Model):
    """配件申请订单"""
    id = db.Column(db.Integer, primary_key=True)
    requester_id = db.Column(db.Integer, db.ForeignKey('app_user.id'))
    department_head_id = db.Column(db.Integer, db.ForeignKey('app_user.id'))  # 部门领导审批人
    admin_id = db.Column(db.Integer, db.ForeignKey('app_user.id'))  # 管理员审批人
    
    part_name = db.Column(db.String(120))
    part_number = db.Column(db.String(120))
    quantity = db.Column(db.Integer, default=1)
    reason = db.Column(db.Text)
    
    status = db.Column(db.String(64), default='submitted')  # submitted, department_head_approved, admin_approved, completed, cancelled
    
    # 审批状态
    department_head_approved = db.Column(db.Boolean, default=False)
    admin_approved = db.Column(db.Boolean, default=False)
    
    created_date = db.Column(db.DateTime, default=get_beijing_now)
    updated_date = db.Column(db.DateTime, default=get_beijing_now, onupdate=get_beijing_now)
    completed_date = db.Column(db.DateTime)
    
    # 关联关系
    requester = db.relationship('User', foreign_keys=[requester_id], backref='requested_part_orders')
    department_head = db.relationship('User', foreign_keys=[department_head_id], backref='department_head_approved_part_orders')
    admin = db.relationship('User', foreign_keys=[admin_id], backref='admin_approved_part_orders')
    
    def __repr__(self):
        return f'<PartRequestOrder {self.id}>'


class AccountRequest(db.Model):
    __tablename__ = 'account_request'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    full_name = db.Column(db.String(120))
    employee_no = db.Column(db.String(64))
    email = db.Column(db.String(120))
    department = db.Column(db.String(120))
    role_requested = db.Column(db.String(64), default='user')
    reason = db.Column(db.Text)
    password_hash = db.Column(db.String(128))
    status = db.Column(db.String(32), default='pending')  # pending, approved, rejected
    created_date = db.Column(db.DateTime, default=get_beijing_now)
    processed_date = db.Column(db.DateTime)
    approver_id = db.Column(db.Integer, db.ForeignKey('app_user.id'))
    approver_comments = db.Column(db.Text)
    
    approver = db.relationship('User', foreign_keys=[approver_id])
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<AccountRequest {self.username}>'


class ApprovalWorkflow(db.Model):
    """审批流程"""
    id = db.Column(db.Integer, primary_key=True)
    order_type = db.Column(db.String(64))  # 'repair_order', 'part_request_order'
    order_id = db.Column(db.Integer)
    approver_id = db.Column(db.Integer, db.ForeignKey('app_user.id'))
    approval_level = db.Column(db.String(64))  # 'department_head', 'admin'
    node_id = db.Column(db.Integer, db.ForeignKey('workflow_node.id'))  # 添加节点ID关联
    status = db.Column(db.String(64), default='pending')  # 'pending', 'approved', 'rejected', 'transferred', 'terminated'
    comments = db.Column(db.Text)
    created_date = db.Column(db.DateTime, default=get_beijing_now)
    approved_date = db.Column(db.DateTime)
    auto_assigned = db.Column(db.Boolean, default=False)
    
    # 审批操作扩展字段
    action_type = db.Column(db.String(32), default='approve')  # approve, reject, transfer, return, terminate
    repair_cost_input = db.Column(db.Float)  # 技术员输入的维修金额
    transferred_from_id = db.Column(db.Integer, db.ForeignKey('app_user.id'))  # 转交来源审批人
    admin_action = db.Column(db.String(32))  # 管理员干预操作: force_approve, force_reject, transfer, terminate
    admin_operator_id = db.Column(db.Integer, db.ForeignKey('app_user.id'))  # 管理员操作人ID
    
    # 关联关系
    approver = db.relationship('User', foreign_keys=[approver_id], backref='approvals')
    workflow_node = db.relationship('WorkflowNode', backref='approvals')  # 添加工作流节点关联
    transferred_from = db.relationship('User', foreign_keys=[transferred_from_id])
    admin_operator = db.relationship('User', foreign_keys=[admin_operator_id])
    
    def __repr__(self):
        return f'<ApprovalWorkflow {self.id}>'


class EquipmentTransfer(db.Model):
    """设备调拨申请"""
    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'))
    from_department = db.Column(db.String(120))
    to_department = db.Column(db.String(120))
    requester_id = db.Column(db.Integer, db.ForeignKey('app_user.id'))
    description = db.Column(db.Text)
    status = db.Column(db.String(64), default='submitted')
    created_date = db.Column(db.DateTime, default=get_beijing_now)
    updated_date = db.Column(db.DateTime, default=get_beijing_now, onupdate=get_beijing_now)

    equipment = db.relationship('Equipment', backref='transfer_orders')
    requester = db.relationship('User', foreign_keys=[requester_id], backref='transfer_requests')

    def __repr__(self):
        return f'<EquipmentTransfer {self.id}>'


class EquipmentScrap(db.Model):
    """设备报废申请"""
    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'))
    requester_id = db.Column(db.Integer, db.ForeignKey('app_user.id'))
    description = db.Column(db.Text)
    status = db.Column(db.String(64), default='submitted')  # submitted/approved/rejected/disposed
    created_date = db.Column(db.DateTime, default=get_beijing_now)
    updated_date = db.Column(db.DateTime, default=get_beijing_now, onupdate=get_beijing_now)
    
    # 🆕 处置管理字段
    disposal_method = db.Column(db.String(64))  # 处置方式: recycling/donation/destruction/sale
    disposal_date = db.Column(db.DateTime)  # 处置日期
    disposal_handler = db.Column(db.Integer, db.ForeignKey('app_user.id'))  # 处置负责人
    disposal_notes = db.Column(db.Text)  # 处置说明
    disposal_value = db.Column(db.Float, default=0.0)  # 残值/售价
    disposal_company = db.Column(db.String(200))  # 处置公司/机构
    
    # 🆕 财务核销
    financial_cleared = db.Column(db.Boolean, default=False)  # 是否已财务核销
    financial_cleared_date = db.Column(db.DateTime)  # 核销日期
    financial_cleared_by = db.Column(db.Integer, db.ForeignKey('app_user.id'))  # 核销人
    financial_notes = db.Column(db.Text)  # 核销备注

    equipment = db.relationship('Equipment', backref='scrap_requests')
    requester = db.relationship('User', foreign_keys=[requester_id], backref='scrap_requests')
    disposal_handler_user = db.relationship('User', foreign_keys=[disposal_handler], backref='disposal_scraps')
    financial_cleared_user = db.relationship('User', foreign_keys=[financial_cleared_by], backref='cleared_scraps')

    def __repr__(self):
        return f'<EquipmentScrap {self.id}>'


class EquipmentLoan(db.Model):
    """设备借用申请"""
    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'))
    requester_id = db.Column(db.Integer, db.ForeignKey('app_user.id'))
    requester_dept = db.Column(db.String(120))

    # 计划借用起止时间
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)

    # 状态：submitted, approved, borrowed, return_pending, returned, cancelled, rejected
    status = db.Column(db.String(64), default='submitted')

    # 审批/借出记录
    approved_by = db.Column(db.Integer, db.ForeignKey('app_user.id'))
    approved_date = db.Column(db.DateTime)
    borrowed_date = db.Column(db.DateTime)
    
    # 🆕 归还申请相关
    return_request_date = db.Column(db.DateTime)  # 归还申请时间
    return_notes = db.Column(db.Text)  # 归还说明
    return_condition = db.Column(db.String(64))  # good/damaged/lost
    
    # 🆕 验收相关
    inspected_by = db.Column(db.Integer, db.ForeignKey('app_user.id'))  # 验收人
    inspection_date = db.Column(db.DateTime)  # 验收时间
    inspection_notes = db.Column(db.Text)  # 验收备注
    inspection_result = db.Column(db.String(64))  # passed/failed/requires_repair
    
    # 🆕 损坏赔偿相关
    damage_compensation = db.Column(db.Float, default=0)  # 赔偿金额
    damage_description = db.Column(db.Text)  # 损坏描述
    
    # 归还时间
    returned_date = db.Column(db.DateTime)

    notes = db.Column(db.Text)
    pickup_notified = db.Column(db.Boolean, default=False)

    created_date = db.Column(db.DateTime, default=get_beijing_now)
    updated_date = db.Column(db.DateTime, default=get_beijing_now, onupdate=get_beijing_now)

    # 关联关系
    equipment = db.relationship('Equipment', backref='loan_requests')
    requester = db.relationship('User', foreign_keys=[requester_id], backref='loan_requests')
    approver = db.relationship('User', foreign_keys=[approved_by], backref='approved_loans')
    inspector = db.relationship('User', foreign_keys=[inspected_by], backref='inspected_loans')

    def __repr__(self):
        return f'<EquipmentLoan {self.id}>'


class EquipmentApplication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'))
    applicant_id = db.Column(db.Integer, db.ForeignKey('app_user.id'))
    applicant_dept = db.Column(db.String(120))
    reason = db.Column(db.Text)
    status = db.Column(db.String(64), default='submitted')  # submitted, approved, rejected, cancelled
    created_date = db.Column(db.DateTime, default=get_beijing_now)
    approved_date = db.Column(db.DateTime)

    equipment = db.relationship('Equipment', backref=db.backref('applications', cascade='all, delete-orphan'))
    applicant = db.relationship('User', foreign_keys=[applicant_id], backref='equipment_applications')

    def __repr__(self):
        return f'<EquipmentApplication {self.id}>'



class Notification(db.Model):
    """通知"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('app_user.id'))
    title = db.Column(db.String(120))
    message = db.Column(db.Text)
    is_read = db.Column(db.Boolean, default=False)
    created_date = db.Column(db.DateTime, default=get_beijing_now)
    # 支持跳转到相关订单
    order_type = db.Column(db.String(64))  # repair_order, part_request_order, equipment_application, etc.
    order_id = db.Column(db.Integer)  # 相关订单ID
    
    user = db.relationship('User', backref='notifications')
    

class EquipmentType(db.Model):
    """设备类型"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.Text)
    created_date = db.Column(db.DateTime, default=get_beijing_now)
    
    def __repr__(self):
        return f'<EquipmentType {self.name}>'


class SparePartType(db.Model):
    """配件类型"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.Text)
    created_date = db.Column(db.DateTime, default=get_beijing_now)
    
    def __repr__(self):
        return f'<SparePartType {self.name}>'


class UserActivityLog(db.Model):
    """用户活动日志"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('app_user.id'))
    action = db.Column(db.String(120))
    description = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=get_beijing_now)
    
    user = db.relationship('User', backref='activity_logs')
    
    def __repr__(self):
        return f'<UserActivityLog {self.id}>'


class AssetCost(db.Model):
    """资产成本管理"""
    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), unique=True)
    purchase_price = db.Column(db.Float, default=0)  # 采购价格
    purchase_date = db.Column(db.Date)  # 采购日期
    maintenance_cost = db.Column(db.Float, default=0)  # 维护成本
    depreciation_rate = db.Column(db.Float, default=0.2)  # 折旧率（20% 默认）
    residual_value = db.Column(db.Float)  # 残值
    depreciation_method = db.Column(db.String(64), default='straight_line')  # 折旧方法
    expected_lifespan = db.Column(db.Integer, default=5)  # 预期使用年限（年）
    supplier = db.Column(db.String(120))  # 供应商
    warranty_period = db.Column(db.Integer)  # 保修期（月）
    created_date = db.Column(db.DateTime, default=get_beijing_now)
    updated_date = db.Column(db.DateTime, default=get_beijing_now, onupdate=get_beijing_now)
    
    equipment = db.relationship('Equipment', backref='cost')
    
    def calculate_current_value(self):
        """计算当前价值（直线法折旧）"""
        if not self.purchase_price or not self.purchase_date:
            return 0
        
        months_used = (get_beijing_now().date() - self.purchase_date).days / 30
        total_months = self.expected_lifespan * 12
        
        if months_used >= total_months:
            return self.residual_value or 0
        
        depreciation_amount = (self.purchase_price - (self.residual_value or 0)) * (months_used / total_months)
        return self.purchase_price - depreciation_amount
    
    def calculate_total_cost(self):
        """计算总投入成本"""
        return self.purchase_price + self.maintenance_cost
    
    def __repr__(self):
        return f'<AssetCost {self.equipment_id}>'


class AssetLifecycle(db.Model):
    """资产生命周期事件记录"""
    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'))
    event_type = db.Column(db.String(64))  # purchase, deployment, maintenance, upgrade, retirement
    event_date = db.Column(db.DateTime, default=get_beijing_now)
    old_status = db.Column(db.String(64))  # 旧状态
    new_status = db.Column(db.String(64))  # 新状态
    description = db.Column(db.Text)
    responsible_user_id = db.Column(db.Integer, db.ForeignKey('app_user.id'))
    cost_involved = db.Column(db.Float, default=0)  # 相关成本
    documents = db.Column(db.Text)  # 相关文档/附件路径
    
    equipment = db.relationship('Equipment', backref='lifecycle_events')
    responsible_user = db.relationship('User', backref='lifecycle_events')
    
    def __repr__(self):
        return f'<AssetLifecycle {self.equipment_id}>'


class InventoryWarning(db.Model):
    """库存预警规则"""
    id = db.Column(db.Integer, primary_key=True)
    spare_part_id = db.Column(db.Integer, db.ForeignKey('spare_part.id'))
    min_threshold = db.Column(db.Integer)  # 最小库存
    critical_threshold = db.Column(db.Integer)  # 紧急库存
    reorder_quantity = db.Column(db.Integer)  # 建议采购数量
    lead_time_days = db.Column(db.Integer, default=7)  # 采购周期（天）
    enabled = db.Column(db.Boolean, default=True)
    last_warned_date = db.Column(db.DateTime)  # 上次预警时间
    created_date = db.Column(db.DateTime, default=get_beijing_now)
    
    spare_part = db.relationship('SparePart', backref='warning_rule')
    
    def is_critical(self):
        """是否处于紧急状态"""
        return self.spare_part.stock_quantity <= self.critical_threshold if self.spare_part else False
    
    def is_warning(self):
        """是否处于预警状态"""
        return self.spare_part.stock_quantity <= self.min_threshold if self.spare_part else False
    
    def __repr__(self):
        return f'<InventoryWarning {self.spare_part_id}>'


class AssetHandover(db.Model):
    """资产交接单（员工离职/转岗）"""
    id = db.Column(db.Integer, primary_key=True)
    from_user_id = db.Column(db.Integer, db.ForeignKey('app_user.id'))
    to_user_id = db.Column(db.Integer, db.ForeignKey('app_user.id'), nullable=True)
    equipment_ids = db.Column(db.Text)  # JSON 格式存储
    status = db.Column(db.String(64), default='pending')  # pending, in_progress, completed, cancelled
    reason = db.Column(db.String(64))  # resignation, transfer, other
    reason_detail = db.Column(db.Text)
    created_date = db.Column(db.DateTime, default=get_beijing_now)
    completed_date = db.Column(db.DateTime)
    completed_by_id = db.Column(db.Integer, db.ForeignKey('app_user.id'))
    
    # 关联关系
    from_user = db.relationship('User', foreign_keys=[from_user_id], backref='handover_from')
    to_user = db.relationship('User', foreign_keys=[to_user_id], backref='handover_to')
    completed_by = db.relationship('User', foreign_keys=[completed_by_id], backref='completed_handovers')
    

class RoleDefinition(db.Model):
    """自定义角色定义（支持细粒度权限）"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)  # 角色名称
    description = db.Column(db.Text)  # 角色描述
    is_custom = db.Column(db.Boolean, default=True)  # 是否自定义（False为系统内置）
    is_active = db.Column(db.Boolean, default=True)
    created_date = db.Column(db.DateTime, default=get_beijing_now)
    created_by_id = db.Column(db.Integer, db.ForeignKey('app_user.id'))
    
    permissions = db.relationship('Permission', backref='role_def', cascade='all, delete-orphan')
    # 注意: 用户关系现在通过 UserCustomRole 模型访问
    # users = db.relationship('User', secondary='user_custom_role', backref='custom_roles')
    
    @property
    def users(self):
        """获取拥有此角色的所有活跃用户"""
        return [assignment.user for assignment in UserCustomRole.query.filter_by(
            role_id=self.id, is_active=True
        ).all() if assignment.user]
    
    def __repr__(self):
        return f'<RoleDefinition {self.name}>'


class Permission(db.Model):
    """权限定义（模块+操作级别）"""
    id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('role_definition.id'))
    module = db.Column(db.String(64))  # 模块：equipment, repair, loan, transfer, scrap, report等
    action = db.Column(db.String(64))  # 操作：view, create, edit, delete, approve等
    resource_type = db.Column(db.String(64), nullable=True)  # 资源类型
    conditions = db.Column(db.Text)  # JSON格式条件，如{"department_id": [1, 2, 3]}
    is_granted = db.Column(db.Boolean, default=True)  # True表示授权，False表示禁用
    priority = db.Column(db.Integer, default=0)  # 优先级，处理冲突时用
    created_date = db.Column(db.DateTime, default=get_beijing_now)
    
    def check_condition(self, context):
        """检查权限条件是否满足"""
        if not self.conditions:
            return True
        try:
            import json
            cond = json.loads(self.conditions)
            # 简单检查示例
            for key, value in cond.items():
                if key in context and context[key] not in value:
                    return False
            return True
        except:
            return True
    
    def __repr__(self):
        return f'<Permission {self.module}.{self.action}>'


# 用户自定义角色关联模型(从关联表升级为完整模型)
class UserCustomRole(db.Model):
    """用户自定义角色关联 - 记录用户被分配的自定义角色及相关信息"""
    __tablename__ = 'user_custom_role'
    
    user_id = db.Column(db.Integer, db.ForeignKey('app_user.id', ondelete='CASCADE'), primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('role_definition.id', ondelete='CASCADE'), primary_key=True)
    assigned_by_id = db.Column(db.Integer, db.ForeignKey('app_user.id'))  # 由谁分配
    assigned_date = db.Column(db.DateTime, default=get_beijing_now)  # 分配时间
    expired_date = db.Column(db.DateTime, nullable=True)  # 过期时间(可选)
    is_active = db.Column(db.Boolean, default=True)  # 是否启用
    notes = db.Column(db.String(500))  # 备注说明
    
    # 关系
    user = db.relationship('User', foreign_keys=[user_id], backref='role_assignments')
    role = db.relationship('RoleDefinition', foreign_keys=[role_id])
    assigned_by = db.relationship('User', foreign_keys=[assigned_by_id])


class AuditLog(db.Model):
    """审计日志 - 记录所有权限操作"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('app_user.id'))
    action_type = db.Column(db.String(64))  # create, update, delete, approve, deny等
    resource_type = db.Column(db.String(64))  # equipment, repair_order等
    resource_id = db.Column(db.Integer)
    old_value = db.Column(db.Text)  # 修改前值
    new_value = db.Column(db.Text)  # 修改后值
    ip_address = db.Column(db.String(64))
    reason = db.Column(db.Text)  # 操作原因
    created_date = db.Column(db.DateTime, default=get_beijing_now)
    
    user = db.relationship('User', backref='audit_logs')
    
    def __repr__(self):
        return f'<AuditLog {self.action_type} {self.resource_type}#{self.resource_id}>'


# NOTE: WorkflowTemplate 和 WorkflowStep 已移至 app/approval_models.py
# 请使用新的企业级审批系统模型


# ==================== 系统公告模型 ====================
class Announcement(db.Model):
    """系统公告模型"""
    __tablename__ = 'announcements'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, comment='公告标题')
    content = db.Column(db.Text, nullable=False, comment='公告内容')
    
    # 公告类型: system-系统维护, update-功能更新, notice-普通通知, urgent-紧急公告
    type = db.Column(db.String(20), nullable=False, default='notice', comment='公告类型')
    
    # 优先级: low-低, normal-普通, high-高, urgent-紧急
    priority = db.Column(db.String(20), nullable=False, default='normal', comment='优先级')
    
    # 是否置顶
    is_pinned = db.Column(db.Boolean, default=False, comment='是否置顶')
    
    # 是否发布
    is_published = db.Column(db.Boolean, default=False, comment='是否发布')
    
    # 时间字段
    publish_time = db.Column(db.DateTime, nullable=True, comment='发布时间')
    expire_time = db.Column(db.DateTime, nullable=True, comment='过期时间')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    # 创建者
    creator_id = db.Column(db.Integer, db.ForeignKey('app_user.id'), nullable=False, comment='创建者ID')
    creator = db.relationship('User', backref='announcements')
    
    def __repr__(self):
        return f'<Announcement {self.title}>'
    
    def to_dict(self):
        """转换为字典"""
        def format_time(dt):
            if dt:
                import pytz
                # 假定数据库中存储的为 UTC naive (datetime.utcnow)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=pytz.UTC)
                tz = pytz.timezone('Asia/Shanghai')
                return dt.astimezone(tz).strftime('%Y-%m-%d %H:%M:%S')
            return None

        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'type': self.type,
            'priority': self.priority,
            'is_pinned': self.is_pinned,
            'is_published': self.is_published,
            'publish_time': format_time(self.publish_time),
            'expire_time': format_time(self.expire_time),
            'created_at': format_time(self.created_at),
            'updated_at': format_time(self.updated_at),
            'attachments': [att.to_dict() for att in self.announcement_attachments] if hasattr(self, 'announcement_attachments') else [],
            'creator': {
                'id': self.creator.id,
                'username': self.creator.username,
                'name': self.creator.name
            } if self.creator else None
        }
    
    @property
    def is_active(self):
        """判断公告是否有效"""
        # 使用 UTC 时间判断（数据库里按 UTC 存储）
        from datetime import datetime
        now = datetime.utcnow()
        if not self.is_published:
            return False
        if self.publish_time and self.publish_time > now:
            return False
        if self.expire_time and self.expire_time < now:
            return False
        return True
    
    @property
    def type_display(self):
        """公告类型显示名称"""
        type_map = {
            'system': '系统维护',
            'update': '功能更新',
            'notice': '普通通知',
            'urgent': '紧急公告'
        }
        return type_map.get(self.type, '未知')
    
    @property
    def priority_display(self):
        """优先级显示名称"""
        priority_map = {
            'low': '低',
            'normal': '普通',
            'high': '高',
            'urgent': '紧急'
        }
        return priority_map.get(self.priority, '普通')
    
    @classmethod
    def get_active_announcements(cls, limit=None):
        """获取有效的公告列表"""
        from datetime import datetime
        # 使用 UTC 时间判断
        now = datetime.utcnow()
        try:
            query = cls.query.filter(
                cls.is_published == True,
                db.or_(
                    cls.publish_time == None,
                    cls.publish_time <= now
                ),
                db.or_(
                    cls.expire_time == None,
                    cls.expire_time > now
                )
            ).order_by(
                cls.is_pinned.desc(),
                cls.priority.desc(),
                cls.publish_time.desc()
            )
            
            if limit:
                query = query.limit(limit)
            
            return query.all()
        except Exception as e:
            # 在测试或迁移尚未运行的环境下，数据库表可能不存在（如 in-memory sqlite）。
            # 为保持非破坏性，遇到 DB 相关错误时返回空列表并记录调试信息。
            import logging
            logging.getLogger(__name__).debug('get_active_announcements failed: %s', e, exc_info=True)
            return []


# 导入审批角色模型
from app.approval_roles import ApprovalRole, UserApprovalRole

# 从新的审批系统模块重新导出模型,保持向后兼容
try:
    from app.approval_models import (
        WorkflowTemplate,
        WorkflowNode,
        ApprovalInstance,
        ApprovalStep,
        ApprovalLog,
        ApprovalDelegate,
        ApprovalReminder
    )
except ImportError:
    # 如果导入失败,使用占位符以避免完全破坏
    pass

# 兼容旧代码 - WorkflowStep已废弃,请使用新的ApprovalStep
# 为了向后兼容,创建别名
try:
    WorkflowStep = ApprovalStep
except NameError:
    pass



# ==========================================
# 设备保养计划模型
# ==========================================

class MaintenancePlan(db.Model):
    """设备保养计划"""
    __tablename__ = 'maintenance_plan'
    
    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), nullable=False)
    plan_name = db.Column(db.String(200))  # 计划名称
    maintenance_type = db.Column(db.String(64))  # 保养类型: daily/weekly/monthly/quarterly/yearly/custom
    interval_days = db.Column(db.Integer)  # 间隔天数(自定义周期时使用)
    next_maintenance_date = db.Column(db.Date)  # 下次保养日期
    last_maintenance_date = db.Column(db.Date)  # 上次保养日期
    responsible_person = db.Column(db.Integer, db.ForeignKey('app_user.id'))  # 负责人
    description = db.Column(db.Text)  # 保养内容描述
    is_active = db.Column(db.Boolean, default=True)  # 是否启用
    created_by = db.Column(db.Integer, db.ForeignKey('app_user.id'))
    created_date = db.Column(db.DateTime, default=get_beijing_now)
    updated_date = db.Column(db.DateTime, default=get_beijing_now, onupdate=get_beijing_now)
    
    # 关系
    equipment = db.relationship('Equipment', backref='maintenance_plans')
    responsible = db.relationship('User', foreign_keys=[responsible_person], backref='maintenance_plans')
    creator = db.relationship('User', foreign_keys=[created_by], backref='created_plans')
    
    def __repr__(self):
        return f'<MaintenancePlan {self.id}: {self.plan_name}>'


class MaintenanceRecord(db.Model):
    """设备保养记录"""
    __tablename__ = 'maintenance_record'
    
    id = db.Column(db.Integer, primary_key=True)
    plan_id = db.Column(db.Integer, db.ForeignKey('maintenance_plan.id'))
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), nullable=False)
    maintenance_date = db.Column(db.DateTime, default=get_beijing_now)  # 保养时间
    maintenance_type = db.Column(db.String(64))  # 保养类型
    performed_by = db.Column(db.Integer, db.ForeignKey('app_user.id'))  # 执行人
    description = db.Column(db.Text)  # 保养内容
    notes = db.Column(db.Text)  # 备注
    cost = db.Column(db.Float, default=0.0)  # 保养成本
    next_maintenance_date = db.Column(db.Date)  # 建议下次保养日期
    status = db.Column(db.String(64), default='completed')  # completed/pending/cancelled
    created_date = db.Column(db.DateTime, default=get_beijing_now)
    
    # 关系
    plan = db.relationship('MaintenancePlan', backref='records')
    equipment = db.relationship('Equipment', backref='maintenance_records')
    performer = db.relationship('User', foreign_keys=[performed_by], backref='performed_maintenances')
    
    def __repr__(self):
        return f'<MaintenanceRecord {self.id}>'


class AnnouncementAttachment(db.Model):
    """公告附件表"""
    __tablename__ = 'announcement_attachment'
    
    id = db.Column(db.Integer, primary_key=True)
    announcement_id = db.Column(db.Integer, db.ForeignKey('announcements.id'), nullable=False)
    
    # 文件信息
    filename = db.Column(db.String(255), nullable=False)  # 原始文件名
    stored_filename = db.Column(db.String(255), nullable=False)  # 存储文件名(UUID)
    file_path = db.Column(db.String(512), nullable=False)  # 文件路径
    file_size = db.Column(db.Integer, nullable=False)  # 文件大小(字节)
    file_type = db.Column(db.String(128))  # MIME类型
    
    # 预览相关
    thumbnail_path = db.Column(db.String(512))  # 缩略图路径(图片/视频)
    
    # 上传信息
    upload_user_id = db.Column(db.Integer, db.ForeignKey('app_user.id'), nullable=False)
    created_date = db.Column(db.DateTime, default=get_beijing_now)
    
    # 软删除
    is_deleted = db.Column(db.Boolean, default=False)
    deleted_date = db.Column(db.DateTime)
    
    # 关系
    announcement = db.relationship('Announcement', backref='announcement_attachments')
    upload_user = db.relationship('User', foreign_keys=[upload_user_id])
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'announcement_id': self.announcement_id,
            'filename': self.filename,
            'file_size': self.file_size,
            'file_size_formatted': self.format_file_size(self.file_size),
            'file_type': self.file_type,
            'upload_user': self.upload_user.username if self.upload_user else None,
            'created_date': self.created_date.strftime('%Y-%m-%d %H:%M:%S') if self.created_date else None,
            'can_preview': self.can_preview(),
            'is_image': self.is_image(),
            'is_video': self.is_video(),
            'is_pdf': self.is_pdf()
        }
    
    def can_preview(self):
        """判断是否可预览"""
        if not self.file_type:
            return False
        
        previewable_types = [
            'application/pdf',
            'image/jpeg', 'image/png', 'image/gif', 'image/bmp', 'image/webp',
            'video/mp4', 'video/webm', 'video/ogg',
            'audio/mpeg', 'audio/wav', 'audio/ogg'
        ]
        
        return self.file_type in previewable_types
    
    def is_image(self):
        """判断是否为图片"""
        return self.file_type and self.file_type.startswith('image/')
    
    def is_video(self):
        """判断是否为视频"""
        return self.file_type and self.file_type.startswith('video/')
    
    def is_pdf(self):
        """判断是否为PDF"""
        return self.file_type == 'application/pdf'
    
    @staticmethod
    def format_file_size(size_bytes):
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    def __repr__(self):
        return f'<AnnouncementAttachment {self.filename}>'


# Backwards compatibility: chat models live in app.chat_models (split file).
# Expose Chat* symbols through app.models for tests / older imports.
try:
    from app.chat_models import (
        ChatConversation,
        ChatParticipant,
        ChatMessage,
        ChatAttachment,
        ChatPermission,
    )
except Exception:
    # If import fails during early app import (e.g., circular), silently ignore.
    pass

