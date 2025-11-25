#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试登录并导出设备借用列表"""
from app import create_app, db
from app.models import User

app = create_app()

# 创建测试客户端
client = app.test_client()

# 先尝试登录
print("1. 测试登录...")
response = client.post('/auth/login', data={
    'username': 'admin',
    'password': 'admin123'
}, follow_redirects=False)
print(f"   登录状态码: {response.status_code}")
print(f"   响应头: {dict(response.headers)}")

# 尝试访问借用导出页面
print("\n2. 测试借用导出...")
response = client.get('/loans/export', follow_redirects=False)
print(f"   导出状态码: {response.status_code}")
if response.status_code != 200:
    print(f"   错误: {response.data[:500]}")
else:
    print("   ✓ 导出成功")

print("\n3. 测试报表导出...")
response = client.get('/reports/export?report_type=loans', follow_redirects=False)
print(f"   报表状态码: {response.status_code}")
if response.status_code != 200:
    print(f"   错误: {response.data[:500]}")
else:
    print("   ✓ 报表导出成功")
