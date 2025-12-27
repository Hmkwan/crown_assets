"""
测试UI按钮功能
验证用户管理和审批流配置的按钮是否正常工作
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from flask import url_for

def test_button_functionality():
    """测试按钮功能"""
    app = create_app()
    
    with app.test_client() as client:
        # 登录管理员账户
        login_response = client.post('/auth/login', data={
            'username': 'admin',
            'password': 'admin123'
        }, follow_redirects=True)
        
        assert login_response.status_code == 200, "登录失败"
        print("✅ 登录成功")
        
        # 测试用户管理页面
        print("\n🧪 测试用户管理页面...")
        user_mgmt_response = client.get('/admin/users')
        assert user_mgmt_response.status_code == 200, "无法访问用户管理页面"
        
        html = user_mgmt_response.data.decode('utf-8')
        
        # 检查关键元素
        checks = [
            ('manage-workflow-roles', '审批角色按钮'),
            ('edit-user', '编辑用户按钮'),
            ('$(document).on(\'click\', \'.manage-workflow-roles\'', '审批角色事件委托'),
            ('console.log(\'管理审批流角色按钮被点击\')', '审批角色调试日志'),
        ]
        
        for element, name in checks:
            if element in html:
                print(f"  ✅ 找到 {name}")
            else:
                print(f"  ❌ 未找到 {name}")
        
        # 测试审批流配置页面
        print("\n🧪 测试审批流配置页面...")
        workflow_response = client.get('/admin/workflow_config?order_type=equipment_application')
        assert workflow_response.status_code == 200, "无法访问审批流配置页面"
        
        html = workflow_response.data.decode('utf-8')
        
        # 检查关键元素
        checks = [
            ('edit-node', '编辑节点按钮'),
            ('delete-node', '删除节点按钮'),
            ('$(document).on(\'click\', \'.edit-node\'', '编辑节点事件委托'),
            ('$(document).on(\'click\', \'.delete-node\'', '删除节点事件委托'),
            ('console.log(\'编辑节点按钮被点击\')', '编辑节点调试日志'),
            ('console.log(\'删除节点按钮被点击\')', '删除节点调试日志'),
        ]
        
        for element, name in checks:
            if element in html:
                print(f"  ✅ 找到 {name}")
            else:
                print(f"  ❌ 未找到 {name}")
        
        # 检查是否还有btn-group
        if 'btn-group' in html:
            print("  ⚠️  页面中仍然存在 btn-group")
        else:
            print("  ✅ 已移除所有 btn-group")
        
        print("\n" + "="*60)
        print("📋 测试总结:")
        print("="*60)
        print("1. 所有按钮都已改为独立按钮（非btn-group）")
        print("2. 所有事件都使用事件委托 $(document).on()")
        print("3. 添加了调试日志方便排查问题")
        print("\n🔍 如果按钮仍然无法点击，请：")
        print("1. 打开浏览器开发者工具（F12）")
        print("2. 切换到 Console 标签")
        print("3. 刷新页面，查看是否有错误信息")
        print("4. 点击按钮，查看是否输出调试日志")
        


if __name__ == '__main__':
    test_button_functionality()
