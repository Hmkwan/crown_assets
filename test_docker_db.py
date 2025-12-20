#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试PostgreSQL连接和User查询"""
from app import create_app, db
from app.models import User

app = create_app()

with app.app_context():
    try:
        # 测试查询
        count = User.query.count()
        print(f"✅ User表查询成功: {count}个用户")
        
        # 测试登录用户查询
        admin = User.query.filter_by(username='admin').first()
        if admin:
            print(f"✅ 找到admin用户: {admin.username} ({admin.email})")
        else:
            print("⚠️ 未找到admin用户")
            
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
