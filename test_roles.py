from app import create_app
from app.approval_roles import ApprovalRole

app = create_app()
with app.app_context():
    roles = ApprovalRole.query.filter_by(is_active=True).all()
    print(f'活跃审批角色数: {len(roles)}')
    
    for role in roles:
        print(f'  - {role.name} (代码: {role.code}, 级别: {role.level})')
