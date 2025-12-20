"""
快速测试新功能 - 打开管理界面
"""
import webbrowser
import time
from app import create_app

print('='*60)
print('企业级审批流引擎 - 功能验证')
print('='*60)

app = create_app()
with app.app_context():
    from app.models import User
    from app.approval_models import WorkflowTemplate, WorkflowNode
    
    print('\n✓ 系统状态:')
    print(f'  用户总数: {User.query.count()}')
    print(f'  流程模板: {WorkflowTemplate.query.count()}')
    print(f'  流程节点: {WorkflowNode.query.filter(WorkflowNode.template_id.isnot(None)).count()}')
    
    print('\n✓ 新增功能入口:')
    print('  1. 用户角色管理: http://localhost:5000/admin/user-roles/')
    print('  2. 管理面板 (查看新卡片): http://localhost:5000/admin_dashboard')
    
    print('\n✓ 用户角色示例:')
    users = User.query.limit(5).all()
    for u in users:
        roles_display = u.get_workflow_roles_display()
        print(f'  {u.username}: {roles_display}')
    
    print('\n✓ 审批流模板:')
    templates = WorkflowTemplate.query.all()
    for t in templates:
        node_count = WorkflowNode.query.filter_by(template_id=t.id).count()
        print(f'  {t.name} ({node_count}节点)')

print('\n' + '='*60)
print('请启动应用后访问管理面板查看新增功能')
print('提示: 在管理面板会看到绿色的"用户角色管理"卡片')
print('='*60)
