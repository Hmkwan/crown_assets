#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""创建管理员账户脚本"""
from app import create_app, db
from app.models import User, Department

app = create_app()
with app.app_context():
    # 检查是否有部门
    dept = Department.query.first()
    if not dept:
        print("创建默认部门...")
        dept = Department(name='系统管理', code='SYS')
        db.session.add(dept)
        db.session.flush()
    else:
        print(f"使用现有部门: {dept.name}")
    
    # 检查管理员是否已存在
    admin = User.query.filter_by(username='admin').first()
    if admin:
        print(f"管理员 'admin' 已存在，邮箱: {admin.email}")
        # 重设密码为 admin123
        admin.set_password('admin123')
        db.session.commit()
        print("密码已重置为: admin123")
    else:
        print("创建管理员账户...")
        admin = User(
            username='admin',
            email='admin@system.local',
            role='admin',
            department_id=dept.id,
            department=dept.name,
            can_manage_equipment=True,
            can_manage_spare_parts=True,
            can_manage_repairs=True,
            can_manage_part_requests=True,
            can_view_workflow=True,
            can_view_reports=True,
            can_view_logs=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("✓ 管理员账户创建成功！")
    
    print(f"\n登录凭证:")
    print(f"  用户名: admin")
    print(f"  密码: admin123")
