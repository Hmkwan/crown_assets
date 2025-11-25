from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(64), default='user')  # 'admin', 'user', 'technician', 'department_head'
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'))
    department = db.Column(db.String(120))
    
    # 用户模块权限
    can_manage_equipment = db.Column(db.Boolean, default=False)
    can_manage_spare_parts = db.Column(db.Boolean, default=False)
    can_manage_repairs = db.Column(db.Boolean, default=False)
    can_manage_part_requests = db.Column(db.Boolean, default=False)
    can_view_workflow = db.Column(db.Boolean, default=False)
    can_view_reports = db.Column(db.Boolean, default=False)
    can_view_logs = db.Column(db.Boolean, default=False)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
        
    def is_admin(self):
        return self.role == 'admin'
        
    def is_department_head(self):
        return self.role == 'department_head'
        
    def has_module_access(self, module):
        """检查用户是否具有特定模块的访问权限"""
        if self.is_admin():
            return True
            
        module_permissions = {
            'equipment': self.can_manage_equipment,
            'spare_parts': self.can_manage_spare_parts,
            'repairs': self.can_manage_repairs,
            'part_requests': self.can_manage_part_requests,
            'workflow': getattr(self, 'can_view_workflow', False),
            'reports': getattr(self, 'can_view_reports', False),
            'logs': getattr(self, 'can_view_logs', False)
        }
        
        return module_permissions.get(module, False)
        
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
    purchase_date = db.Column(db.Date)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'))
    department = db.Column(db.String(120))
    status = db.Column(db.String(64), default='active')  # active, repair, retired, available
    is_public_pool = db.Column(db.Boolean, default=False)
    
    # 关联设备类型
    equipment_type = db.relationship('EquipmentType', backref='equipments')
    
    def __repr__(self):
        return f'<Equipment {self.name}>'


class RepairOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'))
    requester_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    technician_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    department_head_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # 部门领导审批人
    admin_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # 管理员审批人
    
    description = db.Column(db.Text)
    status = db.Column(db.String(64), default='submitted')  # submitted, department_head_approved, admin_approved, in_progress, completed, cancelled
    
    # 时间字段
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    updated_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
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
    price = db.Column(db.Float)
    stock_quantity = db.Column(db.Integer, default=0)
    min_stock_level = db.Column(db.Integer, default=10)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'))
    department = db.Column(db.String(120))
    location = db.Column(db.String(120))
    purchase_date = db.Column(db.Date)
    
    def __repr__(self):
        return f'<SparePart {self.name}>'


class PartReplacement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    repair_order_id = db.Column(db.Integer, db.ForeignKey('repair_order.id'))
    spare_part_id = db.Column(db.Integer, db.ForeignKey('spare_part.id'))
    quantity = db.Column(db.Integer, default=1)
    replacement_date = db.Column(db.DateTime, default=datetime.utcnow)
    
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
    requester_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    department_head_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # 部门领导审批人
    admin_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # 管理员审批人
    
    part_name = db.Column(db.String(120))
    part_number = db.Column(db.String(120))
    quantity = db.Column(db.Integer, default=1)
    reason = db.Column(db.Text)
    
    status = db.Column(db.String(64), default='submitted')  # submitted, department_head_approved, admin_approved, completed, cancelled
    
    # 审批状态
    department_head_approved = db.Column(db.Boolean, default=False)
    admin_approved = db.Column(db.Boolean, default=False)
    
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    updated_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
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
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    processed_date = db.Column(db.DateTime)
    approver_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    approver_comments = db.Column(db.Text)
    
    approver = db.relationship('User', foreign_keys=[approver_id])
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<AccountRequest {self.username}>'


class ApprovalWorkflow(db.Model):
    """审批流程"""
    id = db.Column(db.Integer, primary_key=True)
    order_type = db.Column(db.String(64))  # 'repair_order', 'part_request_order'
    order_id = db.Column(db.Integer)
    approver_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    approval_level = db.Column(db.String(64))  # 'department_head', 'admin'
    node_id = db.Column(db.Integer, db.ForeignKey('workflow_node.id'))  # 添加节点ID关联
    status = db.Column(db.String(64), default='pending')  # 'pending', 'approved', 'rejected'
    comments = db.Column(db.Text)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    approved_date = db.Column(db.DateTime)
    auto_assigned = db.Column(db.Boolean, default=False)
    
    # 关联关系
    approver = db.relationship('User', backref='approvals')
    workflow_node = db.relationship('WorkflowNode', backref='approvals')  # 添加工作流节点关联
    
    def __repr__(self):
        return f'<ApprovalWorkflow {self.id}>'


class EquipmentTransfer(db.Model):
    """设备调拨申请"""
    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'))
    from_department = db.Column(db.String(120))
    to_department = db.Column(db.String(120))
    requester_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    description = db.Column(db.Text)
    status = db.Column(db.String(64), default='submitted')
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    updated_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    equipment = db.relationship('Equipment', backref='transfer_orders')
    requester = db.relationship('User', foreign_keys=[requester_id], backref='transfer_requests')

    def __repr__(self):
        return f'<EquipmentTransfer {self.id}>'


class EquipmentScrap(db.Model):
    """设备报废申请"""
    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'))
    requester_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    description = db.Column(db.Text)
    status = db.Column(db.String(64), default='submitted')
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    updated_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    equipment = db.relationship('Equipment', backref='scrap_requests')
    requester = db.relationship('User', foreign_keys=[requester_id], backref='scrap_requests')

    def __repr__(self):
        return f'<EquipmentScrap {self.id}>'


class EquipmentLoan(db.Model):
    """设备借用申请"""
    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'))
    requester_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    requester_dept = db.Column(db.String(120))

    # 计划借用起止时间
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)

    # 状态：submitted, approved, borrowed, returned, cancelled, rejected
    status = db.Column(db.String(64), default='submitted')

    # 审批/借出/归还记录
    approved_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    approved_date = db.Column(db.DateTime)
    borrowed_date = db.Column(db.DateTime)
    returned_date = db.Column(db.DateTime)

    notes = db.Column(db.Text)
    pickup_notified = db.Column(db.Boolean, default=False)

    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    updated_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联关系
    equipment = db.relationship('Equipment', backref='loan_requests')
    requester = db.relationship('User', foreign_keys=[requester_id], backref='loan_requests')
    approver = db.relationship('User', foreign_keys=[approved_by], backref='approved_loans')

    def __repr__(self):
        return f'<EquipmentLoan {self.id}>'


class EquipmentApplication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'))
    applicant_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    applicant_dept = db.Column(db.String(120))
    reason = db.Column(db.Text)
    status = db.Column(db.String(64), default='submitted')  # submitted, approved, rejected, cancelled
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    approved_date = db.Column(db.DateTime)

    equipment = db.relationship('Equipment', backref=db.backref('applications', cascade='all, delete-orphan'))
    applicant = db.relationship('User', foreign_keys=[applicant_id], backref='equipment_applications')

    def __repr__(self):
        return f'<EquipmentApplication {self.id}>'


class WorkflowNode(db.Model):
    """工作流节点"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    order_type = db.Column(db.String(64))  # 'repair_order' 或 'part_request_order'
    role_required = db.Column(db.String(64))  # 所需角色: 'department_head', 'admin', 'technician'
    sequence = db.Column(db.Integer)  # 执行顺序
    is_active = db.Column(db.Boolean, default=True)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<WorkflowNode {self.name}>'


class Notification(db.Model):
    """通知"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    title = db.Column(db.String(120))
    message = db.Column(db.Text)
    is_read = db.Column(db.Boolean, default=False)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    # 支持跳转到相关订单
    order_type = db.Column(db.String(64))  # repair_order, part_request_order, equipment_application, etc.
    order_id = db.Column(db.Integer)  # 相关订单ID
    
    user = db.relationship('User', backref='notifications')
    

class EquipmentType(db.Model):
    """设备类型"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.Text)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<EquipmentType {self.name}>'


class UserActivityLog(db.Model):
    """用户活动日志"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    action = db.Column(db.String(120))
    description = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='activity_logs')
    
    def __repr__(self):
        return f'<UserActivityLog {self.id}>'
