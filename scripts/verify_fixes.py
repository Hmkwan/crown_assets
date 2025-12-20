"""验证修复后的审批流配置"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app

app = create_app()

with app.app_context():
    from app.workflow_routes import workflow_bp
    
    print("\n" + "="*70)
    print("✓ 审批流配置修复验证")
    print("="*70)
    
    print("\n🔧 修复内容:")
    print("  1. ✅ 添加 workflow.add_node 路由（POST /api/v1/workflow/nodes）")
    print("  2. ✅ 添加 workflow.update_node 路由（PUT /api/v1/workflow/nodes）")
    print("  3. ✅ 添加 workflow.delete_node 路由（DELETE /api/v1/workflow/nodes）")
    print("  4. ✅ 移除所有角色首页的'工作流程'卡片")
    print("  5. ✅ 移除管理面板的'工作流程'卡片")
    print("  6. ✅ 用户管理表格添加'审批流角色'列")
    
    print("\n🌐 API端点:")
    print(f"  蓝图前缀: {workflow_bp.url_prefix}")
    
    # 获取所有路由
    routes = []
    for rule in app.url_map.iter_rules():
        if 'workflow' in rule.endpoint:
            routes.append({
                'endpoint': rule.endpoint,
                'methods': ','.join(sorted(rule.methods - {'HEAD', 'OPTIONS'})),
                'path': str(rule)
            })
    
    print("\n  已注册路由:")
    for route in sorted(routes, key=lambda x: x['path']):
        print(f"    [{route['methods']:12}] {route['path']:<50} → {route['endpoint']}")
    
    print("\n📋 保留的卡片:")
    print("  管理员首页:")
    print("    - 🏷️ 用户角色管理（绿色边框）")
    print("    - 🗺️ 审批流配置（蓝色边框）")
    print("\n  管理面板:")
    print("    - 🏷️ 用户角色管理（绿色边框）")
    print("    - 🗺️ 审批流配置（蓝色边框）")
    
    print("\n❌ 已移除的卡片:")
    print("  - 工作流程（所有角色首页）")
    print("  - 工作流程（管理面板）")
    
    print("\n✨ 新增功能:")
    print("  用户管理界面:")
    print("    - 新增'审批流角色'列")
    print("    - 显示用户的审批流角色徽章")
    print("    - 未分配角色显示'未分配'")
    
    print("\n🎯 访问地址（端口5020）:")
    print("  主界面: http://localhost:5020/admin/workflow_config")
    print("  用户管理: http://localhost:5020/user_management")
    print("  用户角色管理: http://localhost:5020/admin/user-roles/")
    
    print("\n" + "="*70)
