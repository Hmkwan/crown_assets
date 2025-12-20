"""强制为部门用户分配部门负责人审批角色"""
import sys
sys.path.insert(0, '.')

from app import create_app, db
from app.models import User
from app.approval_roles import ApprovalRole, UserApprovalRole

app = create_app()

with app.app_context():
    print("="*70)
    print("强制分配部门负责人审批角色")
    print("="*70)
    
    # 查找部门负责人角色
    dept_role = ApprovalRole.query.filter_by(name='部门负责人').first()
    
    if not dept_role:
        print("✗ 未找到'部门负责人'审批角色！")
        sys.exit(1)
    
    print(f"\n✓ 找到审批角色: {dept_role.name} (ID={dept_role.id})")
    
    # 查找所有有部门的活跃用户（非admin）
    dept_users = User.query.filter(
        User.department.isnot(None),
        User.department != '',
        User.is_active == True
    ).all()
    
    print(f"\n找到 {len(dept_users)} 个有部门的用户:")
    
    assigned_count = 0
    for user in dept_users:
        # 检查是否已有此角色
        existing = UserApprovalRole.query.filter_by(
            user_id=user.id,
            role_id=dept_role.id
        ).first()
        
        if not existing:
            # 新建分配
            assignment = UserApprovalRole(
                user_id=user.id,
                role_id=dept_role.id,
                is_active=True
            )
            db.session.add(assignment)
            print(f"  ✓ 新分配: {user.username} ({user.department}) → {dept_role.name}")
            assigned_count += 1
        else:
            if not existing.is_active:
                existing.is_active = True
                print(f"  ✓ 激活: {user.username} ({user.department}) → {dept_role.name}")
                assigned_count += 1
            else:
                print(f"  - 已有角色: {user.username} ({user.department})")
    
    if assigned_count > 0:
        try:
            db.session.commit()
            print(f"\n✓ 成功分配/激活 {assigned_count} 个用户到'部门负责人'角色")
        except Exception as e:
            db.session.rollback()
            print(f"\n✗ 分配失败: {e}")
    else:
        print(f"\n- 没有新增分配")
    
    # 验证结果
    print("\n" + "="*70)
    print("验证结果")
    print("="*70)
    
    all_assignments = UserApprovalRole.query.filter_by(
        role_id=dept_role.id,
        is_active=True
    ).all()
    
    print(f"\n'部门负责人'角色的所有用户 (共 {len(all_assignments)} 个):")
    for assignment in all_assignments:
        if assignment.user:
            print(f"  - {assignment.user.username} ({assignment.user.department or '无部门'})")
    
    print("\n提示:")
    print("  1. 在Docker中重启以应用更改: docker-compose restart")
    print("  2. 或者如果代码已挂载，只需刷新页面")
    print("  3. 创建新的维修工单测试审批流程")
