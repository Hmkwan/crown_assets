#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
验证管理员首页确实包含三个新卡片的入口
"""

from app import create_app, db
from app.models import User

app = create_app()

with app.app_context():
    # 创建测试管理员
    admin = User.query.filter_by(username='admin_verify').first()
    if not admin:
        admin = User(username='admin_verify', email='admin@verify.com', role='admin')
        admin.set_password('password123')
        db.session.add(admin)
        db.session.commit()
    
    with app.test_client() as client:
        # 登录
        login_response = client.post(
            '/auth/login',
            data={'username': 'admin_verify', 'password': 'password123'},
            follow_redirects=True
        )
        
        # 获取首页
        response = client.get('/index', follow_redirects=True)
        html = response.get_data(as_text=True)
        
        print("✓ 首页已加载")
        
        # 检查三个卡片
        checks = [
            ('成本分析', '💰 成本分析' in html or '成本分析' in html),
            ('库存预警', '📦 库存预警' in html or '库存预警' in html),
            ('生命周期', '📈 生命周期' in html or '生命周期' in html),
            ('成本分析链接', 'cost_analysis' in html),
            ('库存预警链接', 'inventory_warning' in html),
            ('生命周期链接', 'lifecycle_dashboard' in html),
        ]
        
        all_pass = True
        for name, result in checks:
            status = '✓' if result else '✗'
            print(f"{status} {name}")
            if not result:
                all_pass = False
        
        if all_pass:
            print("\n✅ 所有检查通过！三个新卡片已正确添加到管理员首页")
        else:
            print("\n❌ 某些检查未通过，请检查")
