from app import create_app
from app.models import User
from app.approval_roles import UserApprovalRole

app = create_app()
with app.app_context():
    users = User.query.filter_by(is_active=True).all()
    print(f'活跃用户数: {len(users)}')
    
    for user in users[:5]:
        print(f'\n用户: {user.username} (ID: {user.id})')
        print(f'  部门: {user.get_department_name()}')
        
        # 检查用户的审批角色
        assignments = UserApprovalRole.query.filter_by(
            user_id=user.id,
            is_active=True
        ).all()
        print(f'  审批角色数: {len(assignments)}')
