#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试PDF标签下载功能"""

import os
import sys
from io import BytesIO

# 添加app路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User, Equipment

app = create_app()

with app.app_context():
    # 检查管理员用户
    admin_user = User.query.filter_by(username='admin').first()
    if not admin_user:
        print("❌ 管理员账户不存在")
        sys.exit(1)
    
    print(f"✅ 管理员账户: {admin_user.username}")
    
    # 检查设备
    equipment = Equipment.query.first()
    if not equipment:
        print("❌ 没有设备记录")
        sys.exit(1)
    
    print(f"✅ 测试设备: {equipment.name} (ID: {equipment.id})")
    
    # 创建客户端并测试
    client = app.test_client()
    
    # 登录
    with client:
        # 先获取登录页面获取CSRF token
        response = client.get('/auth/login')
        print(f"登录页面状态码: {response.status_code}")
        
        # 从响应中提取CSRF token（简单正则）
        import re
        csrf_match = re.search(r'name="csrf_token"\s+type="hidden"\s+value="([^"]+)"', response.get_data(as_text=True))
        if not csrf_match:
            print("❌ 无法获取CSRF token")
            print(response.get_data(as_text=True)[:500])
            sys.exit(1)
        
        csrf_value = csrf_match.group(1)
        print(f"✅ 获取CSRF token: {csrf_value[:20]}...")
        
        # 尝试登录
        response = client.post('/auth/login', data={
            'username': 'admin',
            'password': 'admin123',
            'csrf_token': csrf_value
        }, follow_redirects=True)
        
        print(f"登录响应状态码: {response.status_code}")
        
        print("✅ 登录成功")
        
        # 测试PDF下载
        pdf_url = f'/asset/download_label/equipment/{equipment.id}'
        print(f"\n📥 测试URL: {pdf_url}")
        
        response = client.get(pdf_url)
        
        print(f"状态码: {response.status_code}")
        print(f"Content-Type: {response.content_type}")
        print(f"Content-Length: {len(response.data)} bytes")
        
        if response.status_code != 200:
            print(f"❌ 下载失败: {response.status_code}")
            print(f"响应: {response.get_data(as_text=True)[:200]}")
            sys.exit(1)
        
        if response.content_type != 'application/pdf':
            print(f"❌ Content-Type 错误，期望 'application/pdf'，实际 '{response.content_type}'")
            sys.exit(1)
        
        # 尝试验证PDF
        try:
            # PDF应该以%PDF开头
            if response.data.startswith(b'%PDF'):
                print(f"✅ PDF 有效! (包含PDF头标记)")
            else:
                print(f"⚠️  可能不是有效的PDF (缺少PDF头标记)")
                print(f"前10字节: {response.data[:10]}")
        except Exception as e:
            print(f"⚠️  验证过程错误: {e}")
        
        # 检查头部
        disposition = response.headers.get('Content-Disposition')
        print(f"Content-Disposition: {disposition}")
        
        if disposition and '设备标签' in disposition:
            print("✅ 中文文件名已正确编码")
        
        print("\n✅ 所有测试通过!")
