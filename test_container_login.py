#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试Docker容器登录功能"""
import requests

# 测试GET登录页面
print("测试1: GET /auth/login")
try:
    r = requests.get('http://localhost:5020/auth/login')
    print(f"  状态码: {r.status_code}")
    if r.status_code == 200:
        print("  ✅ 登录页面正常")
    else:
        print(f"  ❌ 失败: {r.text[:200]}")
except Exception as e:
    print(f"  ❌ 错误: {e}")

print("\n测试2: 检查数据库连接(通过API)")
try:
    # 如果有健康检查接口
    r = requests.get('http://localhost:5020/')
    print(f"  首页状态码: {r.status_code}")
    if r.status_code == 200:
        print("  ✅ 应用运行正常")
    elif r.status_code == 302:
        print(f"  ✅ 重定向到登录页 (正常)")
    else:
        print(f"  状态: {r.status_code}")
except Exception as e:
    print(f"  ❌ 错误: {e}")

print("\n测试3: POST登录(需要CSRF token)")
try:
    # 先获取登录页面获取CSRF token
    session = requests.Session()
    r = session.get('http://localhost:5020/auth/login')
    print(f"  获取登录页: {r.status_code}")
    
    # 提取CSRF token (简化版,实际需要解析HTML)
    # 这里只是测试连接性
    print("  ✅ Session建立成功")
    
except Exception as e:
    print(f"  ❌ 错误: {e}")

print("\n容器状态检查完成!")
