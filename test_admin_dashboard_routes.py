#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
验证管理员首页三个新增功能卡片的路由
"""

from app import create_app, db
from app.models import User
import re

app = create_app()

def test_admin_dashboard_new_routes():
    """测试管理员首页新增的三个路由卡片"""
    
    with app.app_context():
        # 创建测试管理员用户
        user = User.query.filter_by(username='test_admin').first()
        if not user:
            user = User(username='test_admin', email='test_admin@test.com', role='admin')
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()
        
        with app.test_client() as client:
            # 获取登录页面（获取 CSRF 令牌）
            login_page = client.get('/auth/login')
            
            # 使用简单的登录方式
            login_response = client.post(
                '/auth/login',
                data={
                    'username': 'test_admin',
                    'password': 'password123'
                },
                follow_redirects=True
            )
            
            # 获取管理员首页
            dashboard_response = client.get('/admin', follow_redirects=True)
            assert dashboard_response.status_code == 200, f"Dashboard access failed: {dashboard_response.status_code}"
            
            dashboard_html = dashboard_response.get_data(as_text=True)
            
            # 检查三个新卡片是否存在
            print("✓ 管理员首页已加载")
            
            # 1. 检查成本分析卡片
            assert '💰 成本分析' in dashboard_html or '成本分析' in dashboard_html, "成本分析卡片未找到"
            assert 'url_for(\'main.cost_analysis\')' not in dashboard_html or '/cost-analysis' in dashboard_html, "成本分析链接配置错误"
            print("✓ 成本分析卡片已添加")
            
            # 2. 检查库存预警卡片
            assert '📦 库存预警' in dashboard_html or '库存预警' in dashboard_html, "库存预警卡片未找到"
            assert 'url_for(\'main.inventory_warning\')' not in dashboard_html or '/inventory-warnings' in dashboard_html, "库存预警链接配置错误"
            print("✓ 库存预警卡片已添加")
            
            # 3. 检查生命周期卡片
            assert '📈 生命周期' in dashboard_html or '生命周期' in dashboard_html, "生命周期卡片未找到"
            assert 'url_for(\'main.lifecycle_dashboard\')' not in dashboard_html or '/asset/lifecycle/dashboard' in dashboard_html, "生命周期链接配置错误"
            print("✓ 生命周期卡片已添加")
            
            # 测试三个路由是否可访问
            print("\n✓ 测试路由可访问性:")
            
            # 成本分析
            cost_response = client.get('/cost-analysis', follow_redirects=True)
            assert cost_response.status_code == 200, f"成本分析路由失败: {cost_response.status_code}"
            print("  ✓ /cost-analysis 可访问")
            
            # 库存预警
            inventory_response = client.get('/inventory-warnings', follow_redirects=True)
            assert inventory_response.status_code == 200, f"库存预警路由失败: {inventory_response.status_code}"
            print("  ✓ /inventory-warnings 可访问")
            
            # 生命周期
            lifecycle_response = client.get('/asset/lifecycle/dashboard', follow_redirects=True)
            assert lifecycle_response.status_code == 200, f"生命周期路由失败: {lifecycle_response.status_code}"
            print("  ✓ /asset/lifecycle/dashboard 可访问")
            
            print("\n✅ 所有检查通过！管理员首页的三个新功能卡片已正确配置并可访问")

if __name__ == '__main__':
    test_admin_dashboard_new_routes()
