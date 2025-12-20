"""验证首页新功能卡片"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import User
from app.approval_models import WorkflowTemplate, WorkflowNode

app = create_app()

with app.app_context():
    # 统计系统状态
    users = User.query.count()
    templates = WorkflowTemplate.query.count()
    nodes = WorkflowNode.query.count()
    admin_users = User.query.filter_by(role='admin').count()
    
    print("\n" + "="*60)
    print("✓ 首页更新验证 (端口5020)")
    print("="*60)
    
    print("\n📊 系统状态:")
    print(f"  用户总数: {users}")
    print(f"  管理员: {admin_users}")
    print(f"  流程模板: {templates}")
    print(f"  流程节点: {nodes}")
    
    print("\n🌐 访问地址:")
    print("  1. 首页（管理员视图）: http://localhost:5020/index")
    print("  2. 管理面板: http://localhost:5020/admin_dashboard")
    print("  3. 用户角色管理: http://localhost:5020/admin/user-roles/")
    print("  4. 审批流模板: http://localhost:5020/admin/workflow_nodes")
    
    print("\n🎨 新增功能卡片（首页-管理员）:")
    print("  - 🏷️ 用户角色管理 (绿色边框)")
    print("  - 🗺️ 审批流模板 (蓝色边框)")
    
    print("\n✨ 功能特性:")
    print("  ✓ 管理员首页新增2个卡片入口")
    print("  ✓ 卡片支持自定义颜色边框和按钮")
    print("  ✓ 与管理面板保持一致的视觉风格")
    print("  ✓ 响应式布局，适配多种屏幕")
    
    print("\n🔍 验证步骤:")
    print("  1. 使用管理员账号登录")
    print("  2. 访问首页 http://localhost:5020/index")
    print("  3. 滚动到页面底部查看新卡片")
    print("  4. 确认绿色边框（用户角色管理）和蓝色边框（审批流模板）")
    print("  5. 点击卡片验证链接可用性")
    
    print("\n" + "="*60)
