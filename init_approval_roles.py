"""
初始化审批角色系统
创建新表并导入初始数据
"""
from app import create_app, db
from app.approval_roles import ApprovalRole, UserApprovalRole, init_system_approval_roles
from app.models import User

def init_approval_system():
    """初始化审批系统"""
    app = create_app()
    with app.app_context():
        print("开始初始化审批角色系统...")
        
        # 1. 创建新表
        print("\n1. 创建数据库表...")
        try:
            db.create_all()
            print("✓ 数据库表创建成功")
        except Exception as e:
            print(f"✗ 数据库表创建失败: {e}")
            return False
        
        # 2. 初始化系统角色
        print("\n2. 初始化系统审批角色...")
        try:
            init_system_approval_roles()
            print("✓ 系统审批角色初始化成功")
        except Exception as e:
            print(f"✗ 系统审批角色初始化失败: {e}")
            return False
        
        # 3. 为现有管理员用户分配角色
        print("\n3. 为管理员用户分配审批角色...")
        try:
            admin_role = ApprovalRole.query.filter_by(code='admin').first()
            dept_head_role = ApprovalRole.query.filter_by(code='department_head').first()
            tech_role = ApprovalRole.query.filter_by(code='technician').first()
            
            if admin_role:
                # 为所有 role='admin' 的用户分配审批角色
                admin_users = User.query.filter_by(role='admin', is_active=True).all()
                for user in admin_users:
                    # 检查是否已分配
                    existing = UserApprovalRole.query.filter_by(
                        user_id=user.id, 
                        role_id=admin_role.id
                    ).first()
                    
                    if not existing:
                        assignment = UserApprovalRole(
                            user_id=user.id,
                            role_id=admin_role.id,
                            assigned_by_id=user.id,
                            notes='系统自动分配'
                        )
                        db.session.add(assignment)
                        print(f"  ✓ 为管理员 {user.username} 分配审批角色")
            
            if dept_head_role:
                # 为所有 role='department_head' 的用户分配角色
                dept_heads = User.query.filter_by(role='department_head', is_active=True).all()
                for user in dept_heads:
                    existing = UserApprovalRole.query.filter_by(
                        user_id=user.id,
                        role_id=dept_head_role.id
                    ).first()
                    
                    if not existing:
                        assignment = UserApprovalRole(
                            user_id=user.id,
                            role_id=dept_head_role.id,
                            assigned_by_id=user.id,
                            notes='系统自动分配'
                        )
                        db.session.add(assignment)
                        print(f"  ✓ 为部门负责人 {user.username} 分配审批角色")
            
            if tech_role:
                # 为所有 role='technician' 的用户分配角色
                techs = User.query.filter_by(role='technician', is_active=True).all()
                for user in techs:
                    existing = UserApprovalRole.query.filter_by(
                        user_id=user.id,
                        role_id=tech_role.id
                    ).first()
                    
                    if not existing:
                        assignment = UserApprovalRole(
                            user_id=user.id,
                            role_id=tech_role.id,
                            assigned_by_id=user.id,
                            notes='系统自动分配'
                        )
                        db.session.add(assignment)
                        print(f"  ✓ 为技术员 {user.username} 分配审批角色")
            
            db.session.commit()
            print("✓ 用户审批角色分配完成")
            
        except Exception as e:
            db.session.rollback()
            print(f"✗ 用户审批角色分配失败: {e}")
            return False
        
        # 4. 统计信息
        print("\n4. 系统统计信息:")
        try:
            role_count = ApprovalRole.query.count()
            assignment_count = UserApprovalRole.query.count()
            print(f"  • 审批角色总数: {role_count}")
            print(f"  • 角色分配总数: {assignment_count}")
            
            # 显示每个角色的分配情况
            roles = ApprovalRole.query.filter_by(is_active=True).all()
            for role in roles:
                user_count = UserApprovalRole.query.filter_by(
                    role_id=role.id,
                    is_active=True
                ).count()
                print(f"  • {role.icon} {role.name}: {user_count} 个用户")
        
        except Exception as e:
            print(f"统计信息获取失败: {e}")
        
        print("\n✅ 审批角色系统初始化完成!")
        return True


if __name__ == '__main__':
    success = init_approval_system()
    if success:
        print("\n可以开始使用审批角色功能了!")
    else:
        print("\n初始化失败,请检查错误信息")
