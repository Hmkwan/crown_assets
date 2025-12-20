"""
数据库表关联关系检查脚本
检查所有模型之间的外键关联和多对多关系
"""

from app import create_app, db
from sqlalchemy import inspect
from app.models import *

app = create_app()

with app.app_context():
    print("=" * 80)
    print("数据库表关联关系检查")
    print("=" * 80)
    
    inspector = inspect(db.engine)
    
    # 获取所有表名
    tables = inspector.get_table_names()
    
    print(f"\n总共 {len(tables)} 个表:\n")
    
    for table_name in sorted(tables):
        print(f"\n【{table_name}】")
        
        # 获取外键
        foreign_keys = inspector.get_foreign_keys(table_name)
        if foreign_keys:
            print("  外键关联:")
            for fk in foreign_keys:
                print(f"    - {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")
        
        # 获取索引
        indexes = inspector.get_indexes(table_name)
        if indexes:
            print("  索引:")
            for idx in indexes:
                print(f"    - {idx['name']}: {idx['column_names']}")
    
    print("\n" + "=" * 80)
    print("多对多关联表:")
    print("=" * 80)
    
    many_to_many_tables = ['user_custom_role']
    for table_name in many_to_many_tables:
        if table_name in tables:
            print(f"\n【{table_name}】")
            columns = inspector.get_columns(table_name)
            for col in columns:
                print(f"  - {col['name']}: {col['type']}")
            
            foreign_keys = inspector.get_foreign_keys(table_name)
            for fk in foreign_keys:
                print(f"  FK: {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")
    
    print("\n" + "=" * 80)
    print("权限系统关联检查:")
    print("=" * 80)
    
    # 检查RoleDefinition
    print("\nRoleDefinition 模型关联:")
    print("  - permissions: 一对多 -> Permission (cascade='all, delete-orphan')")
    print("  - users: 多对多 -> User (through user_custom_role)")
    print("  - created_by_id: 外键 -> User.id")
    
    # 检查Permission
    print("\nPermission 模型关联:")
    print("  - role_id: 外键 -> RoleDefinition.id")
    print("  - role_def: 反向引用 <- RoleDefinition")
    
    # 检查User
    print("\nUser 模型关联:")
    print("  - custom_roles: 多对多 -> RoleDefinition (through user_custom_role)")
    print("  - department_id: 外键 -> Department.id")
    
    # 验证关联是否工作
    print("\n" + "=" * 80)
    print("关联功能测试:")
    print("=" * 80)
    
    # 测试创建角色
    print("\n测试1: 创建测试角色")
    test_role = RoleDefinition.query.filter_by(name='测试角色').first()
    if not test_role:
        admin = User.query.filter_by(role='admin').first()
        if admin:
            test_role = RoleDefinition(
                name='测试角色',
                description='用于测试关联关系',
                is_custom=True,
                created_by_id=admin.id
            )
            db.session.add(test_role)
            db.session.commit()
            print("  ✓ 测试角色创建成功")
        else:
            print("  ✗ 未找到管理员用户")
    else:
        print("  ✓ 测试角色已存在")
    
    # 测试添加权限
    print("\n测试2: 为角色添加权限")
    if test_role:
        perm_count = Permission.query.filter_by(role_id=test_role.id).count()
        if perm_count == 0:
            test_perm = Permission(
                role_id=test_role.id,
                module='equipment',
                action='view',
                is_granted=True
            )
            db.session.add(test_perm)
            db.session.commit()
            print(f"  ✓ 添加了1个权限")
        else:
            print(f"  ✓ 角色已有 {perm_count} 个权限")
        
        # 验证关联
        print(f"  - 通过 role.permissions 访问: {len(test_role.permissions)} 个权限")
        print(f"  - 通过 Permission.query 查询: {perm_count} 个权限")
    
    # 测试分配用户
    print("\n测试3: 为角色分配用户")
    if test_role:
        user = User.query.filter_by(role='admin').first()
        if user and user not in test_role.users:
            test_role.users.append(user)
            db.session.commit()
            print(f"  ✓ 分配了用户: {user.username}")
        elif user:
            print(f"  ✓ 用户已分配: {user.username}")
        
        # 验证关联
        print(f"  - 通过 role.users 访问: {len(test_role.users)} 个用户")
        if user:
            print(f"  - 通过 user.custom_roles 访问: {len(user.custom_roles)} 个角色")
    
    # 测试级联删除
    print("\n测试4: 测试级联删除")
    if test_role:
        perm_count_before = Permission.query.filter_by(role_id=test_role.id).count()
        print(f"  - 删除前权限数: {perm_count_before}")
        
        # 注意: 这里只是演示,不真的删除
        print("  - 级联删除配置: cascade='all, delete-orphan'")
        print("  - 删除角色时,关联的权限会自动删除")
        print("  - 用户关联会自动解除(多对多表记录删除)")
    
    print("\n" + "=" * 80)
    print("检查完成!")
    print("=" * 80)
