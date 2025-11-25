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
    role = db.Column(db.String(64), default='user')  # 'admin', 'user', 'technician'
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'))
    department = db.Column(db.String(120))
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
        
    def is_admin(self):
        return self.role == 'admin'
        
    def __repr__(self):
        return f'<User {self.username}>'


class Equipment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), index=True)
    type = db.Column(db.String(64))  # 电脑, 打印机, 投影仪等
    brand = db.Column(db.String(64))
    model = db.Column(db.String(64))
    serial_number = db.Column(db.String(120), unique=True)
    purchase_date = db.Column(db.Date)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'))
    department = db.Column(db.String(120))
    status = db.Column(db.String(64), default='active')  # active, repair, retired
    
    def __repr__(self):
        return f'<Equipment {self.name}>'


class RepairOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'))
    requester_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    technician_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    fault_description = db.Column(db.Text)
    repair_description = db.Column(db.Text)
    status = db.Column(db.String(64), default='submitted')  # submitted, in_progress, completed, cancelled
    priority = db.Column(db.String(64), default='medium')  # low, medium, high
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    updated_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_date = db.Column(db.DateTime)
    is_external_repair = db.Column(db.Boolean, default=False)
    external_repair_details = db.Column(db.Text)
    
    # 关联关系
    equipment = db.relationship('Equipment', backref='repair_orders')
    requester = db.relationship('User', foreign_keys=[requester_id], backref='requested_orders')
    technician = db.relationship('User', foreign_keys=[technician_id], backref='assigned_orders')
    
    def __repr__(self):
        return f'<RepairOrder {self.id}>'


class SparePart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    part_number = db.Column(db.String(120))
    price = db.Column(db.Float)
    stock_quantity = db.Column(db.Integer, default=0)
    
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
    name = db.Column(db.String(120), unique=True, nullable=False)
    code = db.Column(db.String(64), unique=True, nullable=False)  # 部门代码
    cost_center = db.Column(db.String(120))  # 成本中心
    location = db.Column(db.String(120))  # 所在位置
    description = db.Column(db.Text)
    
    def __repr__(self):
        return f'<Department {self.name}>'


class UserActivityLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    action = db.Column(db.String(120), nullable=False)  # 操作类型
    description = db.Column(db.Text)  # 操作描述
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # 关联关系
    user = db.relationship('User', backref='activity_logs')
    
    def __repr__(self):
        return f'<UserActivityLog {self.action} by {self.user.username} at {self.timestamp}>'


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    title = db.Column(db.String(120))
    content = db.Column(db.Text)
    is_read = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关联关系
    user = db.relationship('User', backref='notifications')
    
    def __repr__(self):
        return f'<Notification {self.title}>'
