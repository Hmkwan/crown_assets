"""演示如何给用户分配公告发布权限"""

from app import create_app, db
from app.models import User, RoleDefinition, UserCustomRole, Permission
from datetime import datetime

app = create_app()

def list_users():
    """列出所有用户"""
    with app.app_context():
        users = User.query.filter(User.role != 'admin').all()
        print("\n" + "="*60)
        print("系统用户列表 (非管理员):")
        print("="*60)
        for user in users:
            print(f"ID: {user.id:3d} | 用户名: {user.username:15s} | 角色: {user.get_role_display()}")
        return users


def show_role_permissions(role_name):
    """显示角色的权限"""
    with app.app_context():
        role = RoleDefinition.query.filter_by(name=role_name).first()
        if not role:
            print(f"✗ 角色'{role_name}'不存在")
            return
        
        print(f"\n角色: {role.name}")
        print(f"描述: {role.description}")
        print("权限列表:")
        
        perms = Permission.query.filter_by(role_id=role.id, is_granted=True).all()
        if perms:
            for perm in perms:
                print(f"  ✓ {perm.module}.{perm.action}")
        else:
            print("  (无权限)")


def assign_publisher_role(username):
    """给用户分配公告发布员角色"""
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        if not user:
            print(f"✗ 用户'{username}'不存在")
            return False
        
        role = RoleDefinition.query.filter_by(name='公告发布员').first()
        if not role:
            print("✗ 公告发布员角色不存在,请先运行 init_new_permissions.py")
            return False
        
        # 检查是否已经分配
        existing = UserCustomRole.query.filter_by(
            user_id=user.id,
            role_id=role.id
        ).first()
        
        if existing:
            if existing.is_active:
                print(f"✓ 用户'{username}'已拥有公告发布员角色")
                return True
            else:
                existing.is_active = True
                db.session.commit()
                print(f"✓ 重新激活用户'{username}'的公告发布员角色")
                return True
        
        # 创建新的角色分配
        admin = User.query.filter_by(role='admin').first()
        assignment = UserCustomRole(
            user_id=user.id,
            role_id=role.id,
            assigned_by_id=admin.id if admin else None,
            is_active=True,
            notes=f'通过脚本分配于{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
        )
        
        db.session.add(assignment)
        db.session.commit()
        
        print(f"✓ 成功为用户'{username}'分配公告发布员角色")
        return True


def test_user_permissions(username):
    """测试用户权限"""
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        if not user:
            print(f"✗ 用户'{username}'不存在")
            return
        
        print(f"\n" + "="*60)
        print(f"用户权限测试: {username}")
        print("="*60)
        
        # 测试各种操作权限
        tests = [
            ('announcement', 'view', '查看公告'),
            ('announcement', 'create', '创建公告'),
            ('announcement', 'edit', '编辑公告'),
            ('announcement', 'delete', '删除公告'),
            ('announcement', 'publish', '发布公告'),
            ('wework', 'view', '查看企业微信'),
            ('wework', 'sync', '同步企业微信'),
        ]
        
        for module, action, desc in tests:
            has_perm = user.has_permission(module, action)
            status = "✓" if has_perm else "✗"
            print(f"{status} {desc:15s} ({module}.{action})")
        
        # 显示所有权限
        print("\n所有权限:")
        all_perms = user.get_all_permissions()
        if all_perms:
            for module, actions in all_perms.items():
                print(f"  {module}: {', '.join(actions)}")
        else:
            print("  (无自定义权限)")


def remove_publisher_role(username):
    """移除用户的公告发布员角色"""
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        if not user:
            print(f"✗ 用户'{username}'不存在")
            return False
        
        role = RoleDefinition.query.filter_by(name='公告发布员').first()
        if not role:
            print("✗ 公告发布员角色不存在")
            return False
        
        assignment = UserCustomRole.query.filter_by(
            user_id=user.id,
            role_id=role.id,
            is_active=True
        ).first()
        
        if not assignment:
            print(f"✓ 用户'{username}'没有公告发布员角色")
            return True
        
        assignment.is_active = False
        db.session.commit()
        
        print(f"✓ 已移除用户'{username}'的公告发布员角色")
        return True


if __name__ == '__main__':
    print("="*60)
    print("公告发布权限管理演示")
    print("="*60)
    
    # 1. 显示公告发布员角色的权限
    print("\n1. 公告发布员角色权限:")
    show_role_permissions('公告发布员')
    
    # 2. 列出所有用户
    users = list_users()
    
    if not users:
        print("\n✗ 没有非管理员用户,无法演示")
    else:
        # 3. 选择第一个用户进行演示
        demo_user = users[0]
        print(f"\n" + "="*60)
        print(f"将为用户 '{demo_user.username}' 演示权限分配")
        print("="*60)
        
        # 4. 测试分配前的权限
        print("\n【分配前】")
        test_user_permissions(demo_user.username)
        
        # 5. 分配公告发布员角色
        print("\n【分配角色】")
        assign_publisher_role(demo_user.username)
        
        # 6. 测试分配后的权限
        print("\n【分配后】")
        test_user_permissions(demo_user.username)
        
        print("\n" + "="*60)
        print("提示:")
        print("="*60)
        print("1. 用户现在可以访问以下页面:")
        print("   - /admin/announcements (查看公告管理)")
        print("   - /admin/announcements/create (创建公告)")
        print("   - /admin/announcements/<id>/edit (编辑公告)")
        print("   - /admin/announcements/<id>/toggle-publish (发布/取消发布)")
        print("\n2. 要移除权限,运行:")
        print(f"   python -c \"from demo_permissions import remove_publisher_role; remove_publisher_role('{demo_user.username}')\"")
        print("\n3. 在Web界面分配权限:")
        print("   访问: /admin/role_permission_management")
        print("   选择用户 → 分配自定义角色 → 选择'公告发布员'")
