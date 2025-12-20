#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""检查数据库用户信息"""

from app import create_app, db
from app.models import User

app = create_app()

with app.app_context():
    users = User.query.all()
    print(f'\n========== 数据库用户检查 ==========')
    print(f'总用户数: {len(users)}\n')
    
    for u in users:
        print(f'用户名: {u.username}')
        print(f'  角色: {u.role}')
        print(f'  激活状态: {u.is_active}')
        print(f'  密码哈希: {u.password_hash[:50] if u.password_hash else "无密码"}...')
        print(f'  哈希方法: {"scrypt" if u.password_hash and u.password_hash.startswith("scrypt:") else "pbkdf2" if u.password_hash and u.password_hash.startswith("pbkdf2:") else "未知"}')
        print()
    
    # 尝试验证管理员密码
    print('========== 密码验证测试 ==========')
    admin = User.query.filter_by(username='admin').first()
    if admin:
        test_passwords = ['admin', 'admin123', '123456']
        for pwd in test_passwords:
            try:
                result = admin.check_password(pwd)
                print(f'admin 用户密码 "{pwd}" 验证: {"✓ 成功" if result else "✗ 失败"}')
            except Exception as e:
                print(f'admin 用户密码 "{pwd}" 验证异常: {str(e)}')
    else:
        print('未找到 admin 用户!')
