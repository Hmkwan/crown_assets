#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""将所有用户密码改为 pbkdf2 哈希算法(兼容Docker)"""

from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    print('\n' + '='*70)
    print('  修复Docker密码兼容性问题')
    print('='*70 + '\n')
    
    print('问题: Docker容器的OpenSSL不支持scrypt算法')
    print('解决: 使用pbkdf2:sha256算法重新生成密码哈希\n')
    
    # 定义统一密码
    default_password = 'Crown@2024'
    
    users = User.query.all()
    
    print('开始转换所有用户密码哈希...\n')
    
    for user in users:
        # 使用pbkdf2算法生成密码哈希
        user.password_hash = generate_password_hash(
            default_password,
            method='pbkdf2:sha256',
            salt_length=16
        )
        print(f'✓ {user.username:15s} - 密码哈希已转换为 pbkdf2:sha256')
    
    db.session.commit()
    
    print(f'\n所有用户密码已转换完成!\n')
    
    # 验证
    print('='*70)
    print('  验证密码')
    print('='*70 + '\n')
    
    all_success = True
    for user in User.query.all():
        try:
            result = user.check_password(default_password)
            status = '✓' if result else '✗'
            hash_method = user.password_hash.split(':')[0] if user.password_hash else 'unknown'
            print(f'{status} {user.username:15s} 验证: {"成功" if result else "失败":6s} (方法: {hash_method})')
            if not result:
                all_success = False
        except Exception as e:
            print(f'✗ {user.username:15s} 验证异常: {str(e)[:40]}')
            all_success = False
    
    print('\n' + '='*70)
    print('  登录信息')
    print('='*70 + '\n')
    
    print('【所有用户统一密码】')
    print(f'  密码: {default_password}')
    print(f'  哈希方法: pbkdf2:sha256 (Docker兼容)\n')
    
    print('【用户列表】')
    for user in User.query.all():
        print(f'  • {user.username:15s} - {user.role:20s} - {user.department}')
    
    print('\n' + '='*70)
    
    if all_success:
        print('✓ 所有密码验证成功! Docker容器可以正常登录了!')
    else:
        print('✗ 部分密码验证失败,请检查!')
    print('='*70 + '\n')
