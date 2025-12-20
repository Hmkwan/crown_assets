#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试所有用户的密码"""

from app import create_app, db
from app.models import User

app = create_app()

with app.app_context():
    users = User.query.all()
    
    print('\n========== 测试所有用户密码 ==========\n')
    
    # 常见密码列表
    common_passwords = ['admin', 'admin123', '123456', 'password', 'test123', 'testpassword']
    
    for user in users:
        print(f'测试用户: {user.username} (角色: {user.role})')
        success = False
        
        for pwd in common_passwords:
            try:
                if user.check_password(pwd):
                    print(f'  ✓ 密码是: "{pwd}"')
                    success = True
                    break
            except Exception as e:
                print(f'  验证密码 "{pwd}" 时出错: {str(e)}')
        
        if not success:
            print(f'  ✗ 所有常见密码都不匹配')
        print()
    
    # 创建admin用户如果不存在
    print('========== 创建标准 admin 用户 ==========')
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        print('admin 用户不存在,正在创建...')
        admin = User(
            username='admin',
            email='admin@example.com',
            role='super_admin',
            department='IT',
            is_active=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print('✓ 已创建 admin 用户,密码: admin123')
    else:
        print(f'admin 用户已存在,角色: {admin.role}')
