"""
快速验证 - 端口5020
"""
from app import create_app

print('='*60)
print('企业级审批流引擎 - 功能验证')
print('='*60)

app = create_app()
with app.app_context():
    from app.models import User, WorkflowTemplate, WorkflowNode
    
    print('\n✓ 系统状态:')
    print(f'  用户总数: {User.query.count()}')
    print(f'  流程模板: {WorkflowTemplate.query.count()}')
    print(f'  流程节点: {WorkflowNode.query.filter(WorkflowNode.template_id.isnot(None)).count()}')
    
    print('\n✓ 新增功能入口 (端口5020):')
    print('  1. 管理面板: http://localhost:5020/admin_dashboard')
    print('  2. 用户角色管理: http://localhost:5020/admin/user-roles/')
    print('  3. 审批流模板: http://localhost:5020/admin/workflow_nodes')
    
    print('\n✓ 管理面板卡片:')
    print('  - 在管理面板底部可以看到:')
    print('    🏷️ 用户角色管理 (绿色边框)')
    print('    🗺️ 审批流模板 (蓝色边框)')
    
    print('\n✓ 用户角色示例:')
    users = User.query.limit(5).all()
    for u in users:
        roles_display = u.get_workflow_roles_display()
        print(f'  {u.username}: {roles_display}')

print('\n' + '='*60)
print('✅ 请访问管理面板查看新增的绿色和蓝色卡片')
print('   http://localhost:5020/admin_dashboard')
print('='*60)
