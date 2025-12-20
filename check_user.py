from app import create_app, db
from app.models import User, Department

app = create_app()

with app.app_context():
    admin_user = User.query.filter_by(username='admin').first()
    if admin_user:
        print(f'\n管理员用户信息:')
        print(f'  用户名: {admin_user.username}')
        print(f'  角色: {admin_user.role}')
        dept = Department.query.get(admin_user.department_id) if admin_user.department_id else None
        dept_name = dept.name if dept else "无"
        print(f'  部门: {dept_name} (ID: {admin_user.department_id})')
