#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""重置所有用户密码为已知密码"""

from app import create_app, db
from app.models import User

app = create_app()

with app.app_context():
    print('\n========== 重置用户密码 ==========\n')
    
    # 定义标准密码
    password_map = {
        'admin': 'admin123',
        'test_admin': 'admin123',
        'requester_test': 'test123',
        'approver_test': 'test123',
        'testuser': 'test123'
    }
    
    users = User.query.all()
    
    for user in users:
        if user.username in password_map:
            pwd = password_map[user.username]
            user.set_password(pwd)
            print(f'✓ 重置 {user.username} 密码为: {pwd}')
        else:
            # 默认密码
            user.set_password('test123')
            print(f'✓ 重置 {user.username} 密码为: test123')
    
    db.session.commit()
    print('\n所有密码已重置!\n')
    
    # 验证
    print('========== 验证密码 ==========\n')
    for user in User.query.all():
        pwd = password_map.get(user.username, 'test123')
        result = user.check_password(pwd)
        print(f'{user.username}: {"✓ 验证成功" if result else "✗ 验证失败"}')
    
    print('\n========== 登录信息汇总 ==========\n')
    print('用户名: admin')
    print('密码: admin123')
    print('角色: 超级管理员\n')
    
    print('用户名: test_admin')
    print('密码: admin123')
    print('角色: 管理员\n')
    
    print('其他测试用户密码统一为: test123\n')
