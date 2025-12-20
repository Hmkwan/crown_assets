#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""完整测试Docker容器登录流程(带CSRF)"""
import requests
from bs4 import BeautifulSoup

def test_full_login():
    """测试完整登录流程"""
    session = requests.Session()
    
    print("步骤1: 访问登录页面获取CSRF token")
    try:
        r = session.get('http://localhost:5020/auth/login')
        print(f"  状态码: {r.status_code}")
        
        if r.status_code != 200:
            print(f"  ❌ 登录页面访问失败")
            return False
            
        # 解析HTML获取CSRF token
        soup = BeautifulSoup(r.text, 'html.parser')
        csrf_token = soup.find('input', {'name': 'csrf_token'})
        
        if csrf_token:
            token_value = csrf_token.get('value')
            print(f"  ✅ 获取到CSRF token: {token_value[:20]}...")
        else:
            print("  ⚠️ 未找到CSRF token (可能已禁用)")
            token_value = None
            
    except Exception as e:
        print(f"  ❌ 错误: {e}")
        return False
    
    print("\n步骤2: 提交登录表单")
    try:
        login_data = {
            'username': 'admin',
            'password': 'admin123'
        }
        if token_value:
            login_data['csrf_token'] = token_value
            
        r = session.post('http://localhost:5020/auth/login', data=login_data, allow_redirects=False)
        print(f"  状态码: {r.status_code}")
        
        if r.status_code == 302:
            redirect_url = r.headers.get('Location', '')
            print(f"  ✅ 登录成功,重定向到: {redirect_url}")
            return True
        elif r.status_code == 200:
            # 检查是否有错误消息
            if 'Invalid username or password' in r.text or '用户名或密码错误' in r.text:
                print("  ❌ 用户名或密码错误")
            else:
                print("  ⚠️ 登录未重定向,可能需要检查")
            return False
        else:
            print(f"  ❌ 意外状态码: {r.status_code}")
            print(f"  响应: {r.text[:200]}")
            return False
            
    except Exception as e:
        print(f"  ❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("="*60)
    print("Docker容器登录完整测试")
    print("="*60)
    print()
    
    result = test_full_login()
    
    print()
    print("="*60)
    if result:
        print("✅ 测试通过: 可以正常登录")
    else:
        print("❌ 测试失败: 需要检查日志")
    print("="*60)
