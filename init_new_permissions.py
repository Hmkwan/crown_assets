"""添加新功能权限配置

为系统公告和企业微信集成功能添加权限配置
"""

from app import create_app, db
from app.models import Permission, RoleDefinition

app = create_app()

def add_announcement_permissions():
    """添加公告相关权限"""
    with app.app_context():
        # 查找或创建角色
        roles_to_update = {
            'admin': ['view', 'create', 'edit', 'delete', 'publish'],
            'announcement_publisher': ['view', 'create', 'edit', 'publish'],  # 新角色:公告发布员
        }
        
        # 先创建公告发布员角色(如果不存在)
        publisher_role = RoleDefinition.query.filter_by(name='公告发布员').first()
        if not publisher_role:
            publisher_role = RoleDefinition(
                name='公告发布员',
                description='可以创建、编辑和发布系统公告',
                is_custom=True,
                is_active=True
            )
            db.session.add(publisher_role)
            db.session.commit()
            print(f"✓ 创建角色: 公告发布员")
        
        # 为admin角色添加公告权限
        admin_role = RoleDefinition.query.filter_by(name='admin').first()
        if admin_role:
            for action in ['view', 'create', 'edit', 'delete', 'publish']:
                perm = Permission.query.filter_by(
                    role_id=admin_role.id,
                    module='announcement',
                    action=action
                ).first()
                
                if not perm:
                    perm = Permission(
                        role_id=admin_role.id,
                        module='announcement',
                        action=action,
                        is_granted=True
                    )
                    db.session.add(perm)
                    print(f"✓ 为Admin添加权限: announcement.{action}")
        
        # 为公告发布员角色添加权限
        for action in ['view', 'create', 'edit', 'publish']:
            perm = Permission.query.filter_by(
                role_id=publisher_role.id,
                module='announcement',
                action=action
            ).first()
            
            if not perm:
                perm = Permission(
                    role_id=publisher_role.id,
                    module='announcement',
                    action=action,
                    is_granted=True
                )
                db.session.add(perm)
                print(f"✓ 为公告发布员添加权限: announcement.{action}")
        
        db.session.commit()
        print("\n✓ 公告权限配置完成!")


def add_wework_permissions():
    """添加企业微信相关权限"""
    with app.app_context():
        # 只有admin可以管理企业微信
        admin_role = RoleDefinition.query.filter_by(name='admin').first()
        if not admin_role:
            print("✗ Admin角色不存在")
            return
        
        for action in ['view', 'config', 'sync']:
            perm = Permission.query.filter_by(
                role_id=admin_role.id,
                module='wework',
                action=action
            ).first()
            
            if not perm:
                perm = Permission(
                    role_id=admin_role.id,
                    module='wework',
                    action=action,
                    is_granted=True
                )
                db.session.add(perm)
                print(f"✓ 为Admin添加权限: wework.{action}")
        
        db.session.commit()
        print("\n✓ 企业微信权限配置完成!")


def list_current_permissions():
    """列出当前所有权限配置"""
    with app.app_context():
        print("\n" + "="*60)
        print("当前权限配置:")
        print("="*60)
        
        roles = RoleDefinition.query.all()
        for role in roles:
            print(f"\n角色: {role.name}")
            perms = Permission.query.filter_by(role_id=role.id).all()
            if perms:
                for perm in perms:
                    status = "✓" if perm.is_granted else "✗"
                    print(f"  {status} {perm.module}.{perm.action}")
            else:
                print("  (无权限配置)")


if __name__ == '__main__':
    print("="*60)
    print("添加新功能权限配置")
    print("="*60)
    
    # 添加公告权限
    print("\n1. 配置公告模块权限...")
    add_announcement_permissions()
    
    # 添加企业微信权限
    print("\n2. 配置企业微信模块权限...")
    add_wework_permissions()
    
    # 列出所有权限
    list_current_permissions()
    
    print("\n" + "="*60)
    print("权限配置完成!")
    print("="*60)
    print("\n使用说明:")
    print("1. 公告发布权限:")
    print("   - Admin: 拥有所有权限(查看/创建/编辑/删除/发布)")
    print("   - 公告发布员: 可以创建、编辑和发布公告")
    print("   - 如需授权其他用户,在'权限管理'中分配'公告发布员'角色")
    print("\n2. 企业微信管理权限:")
    print("   - 仅限Admin角色使用")
    print("   - 包括查看、配置和同步功能")
    print("\n3. 分配角色给用户:")
    print("   访问: /admin/role_permission_management")
    print("   选择用户 → 分配自定义角色 → 选择'公告发布员'")
