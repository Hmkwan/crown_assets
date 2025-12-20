#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""详细检查数据库用户信息"""

from app import create_app, db
from app.models import User, Department

app = create_app()

with app.app_context():
    users = User.query.all()
    departments = Department.query.all()
    
    print('\n' + '='*60)
    print('  数据库用户详细信息')
    print('='*60)
    
    print(f'\n总用户数: {len(users)}')
    print(f'总部门数: {len(departments)}\n')
    
    # 显示所有部门
    print('【部门列表】')
    for dept in departments:
        print(f'  - {dept.name} ({dept.code})')
    print()
    
    # 显示所有用户
    print('【用户详细信息】\n')
    for idx, user in enumerate(users, 1):
        print(f'{idx}. 用户名: {user.username}')
        print(f'   邮箱: {user.email}')
        print(f'   角色: {user.role}')
        print(f'   部门: {user.department}')
        print(f'   部门ID: {user.department_id}')
        print(f'   激活状态: {"✓ 已激活" if user.is_active else "✗ 未激活"}')
        print(f'   密码哈希: {user.password_hash[:60]}...' if user.password_hash else '   密码哈希: 无')
        print(f'   哈希方法: {"scrypt" if user.password_hash and user.password_hash.startswith("scrypt:") else "pbkdf2" if user.password_hash and "pbkdf2" in user.password_hash else "未知"}')
        print()
    
    # 测试登录
    print('='*60)
    print('  密码验证测试')
    print('='*60 + '\n')
    
    test_cases = [
        ('admin', 'admin123'),
        ('admin', 'admin'),
        ('test_admin', 'admin123'),
        ('requester_test', 'test123'),
        ('approver_test', 'test123'),
        ('testuser', 'test123'),
    ]
    
    for username, password in test_cases:
        user = User.query.filter_by(username=username).first()
        if user:
            try:
                result = user.check_password(password)
                status = '✓ 成功' if result else '✗ 失败'
                print(f'{username:20s} 密码 "{password:15s}" : {status}')
            except Exception as e:
                print(f'{username:20s} 密码 "{password:15s}" : ✗ 异常 - {str(e)[:50]}')
        else:
            print(f'{username:20s} : 用户不存在')
    
    print('\n' + '='*60)
    print('  登录信息汇总')
    print('='*60 + '\n')
    
    print('【管理员账号】')
    print('  用户名: admin')
    print('  密码: admin123')
    print('  角色: super_admin (超级管理员)\n')
    
    print('  用户名: test_admin')
    print('  密码: admin123')
    print('  角色: admin (管理员)\n')
    
    print('【普通用户】')
    print('  用户名: requester_test / approver_test / testuser')
    print('  密码: test123 (统一密码)\n')
    
    print('='*60 + '\n')
