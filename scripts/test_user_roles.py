"""
测试用户审批流角色功能
"""
from app import create_app, db
from app.models import User

app = create_app()
with app.app_context():
    print('\n' + '='*50)
    print('用户审批流角色功能测试')
    print('='*50)
    
    # 1. 测试获取角色
    print('\n1. 测试现有用户的默认角色:')
    users = User.query.limit(5).all()
    for user in users:
        print(f'  {user.username}: {user.get_workflow_roles()} → {user.get_workflow_roles_display()}')
    
    # 2. 测试设置角色
    print('\n2. 测试设置新角色:')
    test_user = User.query.filter_by(username='admin').first()
    if test_user:
        print(f'  原角色: {test_user.get_workflow_roles()}')
        
        # 设置多个角色
        test_user.set_workflow_roles(['admin', 'executive'])
        db.session.commit()
        
        print(f'  新角色: {test_user.get_workflow_roles()}')
        print(f'  显示名: {test_user.get_workflow_roles_display()}')
        
        # 恢复原角色
        test_user.set_workflow_roles(['admin'])
        db.session.commit()
        print(f'  恢复为: {test_user.get_workflow_roles()}')
    
    # 3. 测试角色检查
    print('\n3. 测试角色检查:')
    if test_user:
        print(f'  has_workflow_role("admin"): {test_user.has_workflow_role("admin")}')
        print(f'  has_workflow_role("finance"): {test_user.has_workflow_role("finance")}')
    
    # 4. 统计各角色的用户数
    print('\n4. 各角色用户统计:')
    all_users = User.query.all()
    
    role_counts = {}
    for user in all_users:
        for role in user.get_workflow_roles():
            role_counts[role] = role_counts.get(role, 0) + 1
    
    role_names = {
        'employee': '员工',
        'department_head': '部门经理',
        'admin': 'IT资产管理员',
        'procurement': '采购',
        'warehouse': '库房',
        'security': '安全/合规',
        'finance': '财务',
        'executive': '总经理/高层',
        'auditor': '审计/稽核'
    }
    
    for role, count in sorted(role_counts.items()):
        display_name = role_names.get(role, role)
        print(f'  {display_name} ({role}): {count} 人')
    
    print('\n' + '='*50)
    print('✅ 测试完成！')
    print('='*50)
    print(f'\n访问管理界面: http://localhost:5000/admin/user-roles/')
