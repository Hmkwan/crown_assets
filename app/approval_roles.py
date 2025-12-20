"""
审批角色管理模块
提供完整的审批角色定义、分配、权限管理功能
"""
from app import db
from datetime import datetime
import json


def get_beijing_now():
    """获取北京时间"""
    from datetime import timezone, timedelta
    return datetime.now(timezone(timedelta(hours=8))).replace(tzinfo=None)


class ApprovalRole(db.Model):
    """审批角色定义表"""
    __tablename__ = 'approval_role'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(64), unique=True, nullable=False)  # 角色代码(唯一标识)
    name = db.Column(db.String(120), nullable=False)  # 角色名称
    description = db.Column(db.Text)  # 角色描述
    category = db.Column(db.String(64))  # 角色类别: system(系统), department(部门), custom(自定义)
    level = db.Column(db.Integer, default=0)  # 角色级别(用于审批流优先级)
    icon = db.Column(db.String(64))  # 图标(emoji或fa图标)
    color = db.Column(db.String(32))  # 显示颜色
    
    # 审批权限配置
    can_approve_repair = db.Column(db.Boolean, default=False)  # 可审批维修工单
    can_approve_part_request = db.Column(db.Boolean, default=False)  # 可审批配件申请
    can_approve_equipment_transfer = db.Column(db.Boolean, default=False)  # 可审批设备调拨
    can_approve_equipment_scrap = db.Column(db.Boolean, default=False)  # 可审批设备报废
    can_approve_equipment_loan = db.Column(db.Boolean, default=False)  # 可审批设备借用
    can_approve_equipment_application = db.Column(db.Boolean, default=False)  # 可审批设备申请
    
    # 金额权限
    max_approval_amount = db.Column(db.Float)  # 最大审批金额
    
    # 状态
    is_active = db.Column(db.Boolean, default=True)
    is_system_role = db.Column(db.Boolean, default=False)  # 是否系统角色(不可删除)
    
    # 时间戳
    created_date = db.Column(db.DateTime, default=get_beijing_now)
    updated_date = db.Column(db.DateTime, default=get_beijing_now, onupdate=get_beijing_now)
    created_by_id = db.Column(db.Integer, db.ForeignKey('app_user.id'))
    
    # 关系
    created_by = db.relationship('User', foreign_keys=[created_by_id])
    
    @property
    def users(self):
        """获取拥有此角色的所有活跃用户"""
        return [assignment.user for assignment in UserApprovalRole.query.filter_by(
            role_id=self.id, is_active=True
        ).all() if assignment.user and assignment.user.is_active]
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'level': self.level,
            'icon': self.icon,
            'color': self.color,
            'can_approve_repair': self.can_approve_repair,
            'can_approve_part_request': self.can_approve_part_request,
            'can_approve_equipment_transfer': self.can_approve_equipment_transfer,
            'can_approve_equipment_scrap': self.can_approve_equipment_scrap,
            'can_approve_equipment_loan': self.can_approve_equipment_loan,
            'can_approve_equipment_application': self.can_approve_equipment_application,
            'max_approval_amount': self.max_approval_amount,
            'is_active': self.is_active,
            'is_system_role': self.is_system_role
        }
    
    def __repr__(self):
        return f'<ApprovalRole {self.code}: {self.name}>'


class UserApprovalRole(db.Model):
    """用户审批角色关联表"""
    __tablename__ = 'user_approval_role'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('app_user.id', ondelete='CASCADE'), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('approval_role.id', ondelete='CASCADE'), nullable=False)
    
    # 分配信息
    assigned_by_id = db.Column(db.Integer, db.ForeignKey('app_user.id'))
    assigned_date = db.Column(db.DateTime, default=get_beijing_now)
    
    # 有效期
    start_date = db.Column(db.DateTime, default=get_beijing_now)
    end_date = db.Column(db.DateTime)  # null表示永久
    
    # 状态
    is_active = db.Column(db.Boolean, default=True)
    notes = db.Column(db.Text)  # 备注
    
    # 关系
    user = db.relationship('User', foreign_keys=[user_id], backref='approval_role_assignments')
    role = db.relationship('ApprovalRole', backref='user_assignments')
    assigned_by = db.relationship('User', foreign_keys=[assigned_by_id])
    
    def is_valid(self):
        """检查角色是否在有效期内"""
        if not self.is_active:
            return False
        
        now = get_beijing_now()
        
        # 检查开始时间
        if self.start_date and now < self.start_date:
            return False
        
        # 检查结束时间
        if self.end_date and now > self.end_date:
            return False
        
        return True
    
    def __repr__(self):
        return f'<UserApprovalRole user_id={self.user_id} role_id={self.role_id}>'


def init_system_approval_roles():
    """初始化系统默认审批角色"""
    from app import db
    
    # 检查是否已经初始化
    existing = ApprovalRole.query.filter_by(code='admin').first()
    if existing:
        print("系统审批角色已存在,跳过初始化")
        return
    
    system_roles = [
        {
            'code': 'admin',
            'name': '系统管理员',
            'description': '拥有所有审批权限',
            'category': 'system',
            'level': 100,
            'icon': 'fa-user-tie',
            'color': '#4e73df',
            'can_approve_repair': True,
            'can_approve_part_request': True,
            'can_approve_equipment_transfer': True,
            'can_approve_equipment_scrap': True,
            'can_approve_equipment_loan': True,
            'can_approve_equipment_application': True,
            'max_approval_amount': None,
            'is_system_role': True
        },
        {
            'code': 'department_head',
            'name': '部门负责人',
            'description': '部门主管,可审批部门内工单',
            'category': 'system',
            'level': 50,
            'icon': 'fa-user-tie',
            'color': '#1cc88a',
            'can_approve_repair': True,
            'can_approve_part_request': True,
            'can_approve_equipment_transfer': True,
            'can_approve_equipment_scrap': False,
            'can_approve_equipment_loan': True,
            'can_approve_equipment_application': True,
            'max_approval_amount': 10000.0,
            'is_system_role': True
        },
        {
            'code': 'technician',
            'name': '技术员',
            'description': '技术人员,可审批维修相关工单',
            'category': 'system',
            'level': 30,
            'icon': 'fa-wrench',
            'color': '#36b9cc',
            'can_approve_repair': True,
            'can_approve_part_request': True,
            'can_approve_equipment_transfer': False,
            'can_approve_equipment_scrap': False,
            'can_approve_equipment_loan': False,
            'can_approve_equipment_application': False,
            'max_approval_amount': 5000.0,
            'is_system_role': True
        },
        {
            'code': 'warehouse',
            'name': '仓库管理员',
            'description': '仓库管理人员,可审批配件相关工单',
            'category': 'system',
            'level': 30,
            'icon': 'fa-box',
            'color': '#f6c23e',
            'can_approve_repair': False,
            'can_approve_part_request': True,
            'can_approve_equipment_transfer': True,
            'can_approve_equipment_scrap': False,
            'can_approve_equipment_loan': True,
            'can_approve_equipment_application': False,
            'max_approval_amount': 3000.0,
            'is_system_role': True
        },
        {
            'code': 'finance',
            'name': '财务审批',
            'description': '财务人员,可审批高金额工单',
            'category': 'system',
            'level': 70,
            'icon': 'fa-dollar-sign',
            'color': '#e74a3b',
            'can_approve_repair': True,
            'can_approve_part_request': True,
            'can_approve_equipment_transfer': True,
            'can_approve_equipment_scrap': True,
            'can_approve_equipment_loan': False,
            'can_approve_equipment_application': True,
            'max_approval_amount': None,
            'is_system_role': True
        }
    ]
    
    for role_data in system_roles:
        role = ApprovalRole(**role_data)
        db.session.add(role)
    
    try:
        db.session.commit()
        print(f"成功初始化 {len(system_roles)} 个系统审批角色")
    except Exception as e:
        db.session.rollback()
        print(f"初始化审批角色失败: {e}")


