"""验证部门负责人角色分配"""
import sys
sys.path.insert(0, '.')

from app import create_app, db
from app.approval_roles import ApprovalRole, UserApprovalRole

app = create_app()

with app.app_context():
    dept_role = ApprovalRole.query.filter_by(name='部门负责人').first()
    
    if dept_role:
        assignments = UserApprovalRole.query.filter_by(
            role_id=dept_role.id,
            is_active=True
        ).all()
        
        print(f"Department Head Role Users: {len(assignments)}")
        for a in assignments:
            if a.user:
                print(f"  - {a.user.username} ({a.user.department})")
        
        if len(assignments) > 0:
            print("\nSTATUS: OK - Role has users assigned")
        else:
            print("\nSTATUS: ERROR - No users assigned to role")
    else:
        print("ERROR: Department Head role not found")
