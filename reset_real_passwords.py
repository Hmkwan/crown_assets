#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""重置所有真实用户的密码"""

from app import create_app, db
from app.models import User

app = create_app()

with app.app_context():
    print('\n' + '='*60)
    print('  重置所有用户密码')
    print('='*60 + '\n')
    
    # 为所有用户设置统一密码
    default_password = 'Crown@2024'
    
    users = User.query.all()
    
    for user in users:
        user.set_password(default_password)
        print(f'✓ {user.username:15s} ({user.role:20s}) 密码已重置')
    
    db.session.commit()
    
    print(f'\n所有用户密码已统一重置为: {default_password}\n')
    
    # 验证所有密码
    print('='*60)
    print('  验证密码')
    print('='*60 + '\n')
    
    all_success = True
    for user in User.query.all():
        result = user.check_password(default_password)
        status = '✓' if result else '✗'
        print(f'{status} {user.username:15s} 密码验证: {"成功" if result else "失败"}')
        if not result:
            all_success = False
    
    print('\n' + '='*60)
    print('  登录信息')
    print('='*60 + '\n')
    
    print('【所有用户统一密码】')
    print(f'  密码: {default_password}\n')
    
    print('【用户列表】')
    for user in User.query.all():
        print(f'  • {user.username:15s} - {user.role:20s} - {user.department}')
    
    print('\n' + '='*60)
    
    if all_success:
        print('✓ 所有密码验证成功!')
    else:
        print('✗ 部分密码验证失败,请检查!')
    print('='*60 + '\n')
