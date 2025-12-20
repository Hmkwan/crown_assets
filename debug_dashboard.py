#!/usr/bin/env python
# -*- coding: utf-8 -*-
from app import create_app, db
from app.models import User

app = create_app()

with app.app_context():
    user = User.query.filter_by(username='test_verify').first()
    if not user:
        user = User(username='test_verify', email='verify@test.com', role='admin')
        user.set_password('test123')
        db.session.add(user)
        db.session.commit()
    
    with app.test_client() as client:
        # 登录
        login_resp = client.post('/auth/login', data={'username': 'test_verify', 'password': 'test123'}, follow_redirects=True)
        print(f'Login status: {login_resp.status_code}')
        
        # 获取管理员页面
        resp = client.get('/admin', follow_redirects=True)
        print(f'Admin page status: {resp.status_code}')
        
        html = resp.get_data(as_text=True)
        print(f'\n检查渲染内容:')
        print(f'  - 管理面板标题: {"管理面板" in html}')
        print(f'  - 资产/配件管理中心 (else分支): {"资产/配件管理中心" in html}')
        print(f'  - 成本分析: {"成本分析" in html}')
        print(f'  - 库存预警: {"库存预警" in html}')
        print(f'  - 生命周期: {"生命周期" in html}')
        print(f'  - 报表统计: {"报表统计" in html}')
        
        # 检查具体位置
        if "管理面板" in html:
            idx = html.find("管理面板")
            snippet = html[idx:idx+1000]
            print(f'\n管理面板后的片段（查找成本分析）:')
            if "成本分析" in snippet:
                print("  ✓ 成本分析在该片段中")
            else:
                print("  ✗ 成本分析不在该片段中")
                # 在整个HTML中查找
                if "成本分析" in html:
                    cost_idx = html.find("成本分析")
                    print(f"  成本分析在HTML的位置：{cost_idx}")
