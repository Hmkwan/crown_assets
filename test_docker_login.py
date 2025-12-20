#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试Docker容器登录

这个脚本仅用于手动测试。为了避免 pytest 在收集阶段执行网络请求，已将执行逻辑封装在 run() 中。
"""

import requests
import json

# Docker容器地址
BASE_URL = 'http://localhost:5020'


def run():
    print('\n' + '='*70)
    print('  测试 Docker 容器登录')
    print('='*70 + '\n')

    # 测试用户列表
    test_users = [
        ('admin', 'Crown@2024', '超级管理员'),
        ('吴文杨', 'Crown@2024', '信息部管理员'),
        ('陈松', 'Crown@2024', '企管部负责人'),
        ('关鹤鸣', 'Crown@2024', '信息部技术员'),
    ]

    session = requests.Session()

    for username, password, description in test_users:
        print(f'测试登录: {username} ({description})')

        try:
            # 先获取登录页面(获取CSRF token)
            response = session.get(f'{BASE_URL}/auth/login')

            # 登录
            login_data = {
                'username': username,
                'password': password,
                'submit': 'Sign In'
            }

            response = session.post(
                f'{BASE_URL}/auth/login',
                data=login_data,
                allow_redirects=False
            )

            if response.status_code == 302:  # 重定向表示登录成功
                print(f'  ✓ 登录成功! (状态码: {response.status_code})')
                print(f'  重定向到: {response.headers.get("Location", "未知")}')
            elif response.status_code == 200:
                if 'Invalid username or password' in response.text or '用户名或密码错误' in response.text:
                    print(f'  ✗ 登录失败: 用户名或密码错误')
                else:
                    print(f'  ⚠ 登录状态未知 (状态码: {response.status_code})')
            else:
                print(f'  ✗ 登录失败 (状态码: {response.status_code})')

        except Exception as e:
            print(f'  ✗ 请求异常: {str(e)[:50]}')

        # 登出
        try:
            session.get(f'{BASE_URL}/auth/logout')
        except Exception:
            pass
        print()

    print('='*70)
    print('  测试完成')
    print('='*70 + '\n')

    print('【登录信息汇总】')
    print('  URL: http://localhost:5020')
    print('  统一密码: Crown@2024')
    print('  哈希方法: pbkdf2:sha256 (Docker兼容)')
    print('\n  可用账号:')
    print('    • admin   - 超级管理员')
    print('    • 吴文杨   - 信息部管理员')
    print('    • 陈松     - 企管部负责人')
    print('    • 关鹤鸣   - 信息部技术员')
    print('    • 朱绪     - 企管部普通用户')
    print('    • testuser - 测试用户\n')


if __name__ == '__main__':
    run()
