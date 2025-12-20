"""快速为用户分配审批角色"""
import sys
sys.path.insert(0, '.')

from app import create_app, db
from app.models import User
from app.approval_roles import ApprovalRole, UserApprovalRole

app = create_app()

with app.app_context():
    print("="*70)
    print("快速分配审批角色")
    print("="*70)
    
    # 1. 查找所有审批角色
    roles = ApprovalRole.query.filter_by(is_active=True).all()
    
    print(f"\n找到 {len(roles)} 个审批角色:")
    for role in roles:
        print(f"  - {role.name} (ID={role.id})")
    
    # 2. 为admin用户分配"系统管理员"角色
    admin_role = ApprovalRole.query.filter_by(name='系统管理员').first()
    admin_users = User.query.filter_by(role='admin', is_active=True).all()
    
    if admin_role and admin_users:
        print(f"\n[1] 为系统管理员角色分配用户")
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
                    is_active=True
                )
                db.session.add(assignment)
                print(f"  ✓ 分配 {user.username} → {admin_role.name}")
            else:
                if not existing.is_active:
                    existing.is_active = True
                    print(f"  ✓ 激活 {user.username} → {admin_role.name}")
                else:
                    print(f"  - {user.username} 已有此角色")
    
    # 3. 为部门用户分配"部门负责人"角色
    dept_role = ApprovalRole.query.filter_by(name='部门负责人').first()
    
    if dept_role:
        print(f"\n[2] 为部门负责人角色分配用户")
        
        # 查找所有部门负责人
        dept_heads = User.query.filter_by(role='department_head', is_active=True).all()
        
        if dept_heads:
            for user in dept_heads:
                existing = UserApprovalRole.query.filter_by(
                    user_id=user.id,
                    role_id=dept_role.id
                ).first()
                
                if not existing:
                    assignment = UserApprovalRole(
                        user_id=user.id,
                        role_id=dept_role.id,
                        is_active=True
                    )
                    db.session.add(assignment)
                    print(f"  ✓ 分配 {user.username} ({user.department}) → {dept_role.name}")
                else:
                    if not existing.is_active:
                        existing.is_active = True
                        print(f"  ✓ 激活 {user.username} ({user.department}) → {dept_role.name}")
                    else:
                        print(f"  - {user.username} 已有此角色")
        else:
            print("  ⚠ 没有找到 role='department_head' 的用户")
            print("  提示: 可以为现有的部门用户临时分配此角色:")
            
            # 查找有部门的用户（非admin）
            dept_users = User.query.filter(
                User.department.isnot(None),
                User.department != '',
                User.role != 'admin',
                User.is_active == True
            ).all()
            
            if dept_users:
                print("\n  可选的部门用户:")
                for user in dept_users[:5]:  # 只显示前5个
                    print(f"    - {user.username} ({user.department})")
                
                print(f"\n  建议操作:")
                print(f"  1. 通过管理界面修改用户角色为 'department_head'")
                print(f"  2. 或者直接为这些用户分配'部门负责人'审批角色")
                print(f"\n  示例SQL (选择一个部门用户并分配角色):")
                if dept_users:
                    example_user = dept_users[0]
                    print(f"    INSERT INTO user_approval_role (user_id, role_id, is_active)")
                    print(f"    VALUES ({example_user.id}, {dept_role.id}, true);")
    
    # 4. 采购角色
    procurement_role = ApprovalRole.query.filter_by(name='采购').first()
    if procurement_role:
        print(f"\n[3] 采购角色")
        assignments = UserApprovalRole.query.filter_by(
            role_id=procurement_role.id,
            is_active=True
        ).count()
        if assignments > 0:
            print(f"  ✓ 已有 {assignments} 个用户")
        else:
            print(f"  ⚠ 没有用户分配到此角色")
            print(f"  建议: 通过管理界面手动分配")
    
    # 提交更改
    try:
        db.session.commit()
        print("\n" + "="*70)
        print("✓ 审批角色分配完成")
        print("="*70)
        
        # 显示最终统计
        print("\n角色分配统计:")
        for role in roles:
            count = UserApprovalRole.query.filter_by(
                role_id=role.id,
                is_active=True
            ).count()
            status = "✓" if count > 0 else "⚠"
            print(f"  {status} {role.name}: {count} 个用户")
        
        print("\n提示:")
        print("  - 重启Docker容器以加载更改: docker-compose restart")
        print("  - 创建新的维修工单测试审批流程")
        
    except Exception as e:
        db.session.rollback()
        print(f"\n✗ 分配失败: {e}")
