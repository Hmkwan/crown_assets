#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""审批模块功能测试脚本"""

from app import create_app, db
from app.models import User
from app.approval_roles import ApprovalRole, UserApprovalRole
from datetime import datetime

def test_approval_module():
    """测试审批模块所有功能"""
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print("审批模块功能测试")
        print("=" * 60)
        
        # 1. 检查数据库表
        print("\n1. 检查数据库表...")
        try:
            users_count = User.query.count()
            roles_count = ApprovalRole.query.count()
            assignments_count = UserApprovalRole.query.count()
            print(f"   ✓ 用户数量: {users_count}")
            print(f"   ✓ 审批角色数量: {roles_count}")
            print(f"   ✓ 角色分配数量: {assignments_count}")
        except Exception as e:
            import pytest
            pytest.fail(f"数据库表检查失败: {e}")
        
        # 2. 检查审批角色
        print("\n2. 检查审批角色...")
        try:
            roles = ApprovalRole.query.filter_by(is_active=True).all()
            print(f"   活跃角色数量: {len(roles)}")
            for role in roles:
                print(f"   - {role.icon} {role.name} (Lv.{role.level})")
                # 检查to_dict方法
                role_dict = role.to_dict()
                if not all(k in role_dict for k in ['id', 'code', 'name', 'level']):
                    import pytest
                    pytest.fail("to_dict方法缺少必要字段")
            print("   ✓ 所有角色to_dict方法正常")
        except Exception as e:
            import pytest
            pytest.fail(f"角色检查失败: {e}")
        
        # 3. 检查用户-角色关联
        print("\n3. 检查用户-角色关联...")
        try:
            users = User.query.filter_by(is_active=True).limit(5).all()
            for user in users:
                assignments = UserApprovalRole.query.filter_by(
                    user_id=user.id, 
                    is_active=True
                ).all()
                print(f"   - {user.username}: {len(assignments)}个角色")
                for assignment in assignments:
                    if assignment.is_valid():
                        print(f"     • {assignment.role.name if assignment.role else '角色不存在'}")
        except Exception as e:
            import pytest
            pytest.fail(f"用户-角色关联检查失败: {e}")
        
        # 4. 检查User模型字段
        print("\n4. 检查User模型字段...")
        try:
            user = User.query.first()
            if user:
                # 检查是否有username字段
                if hasattr(user, 'username'):
                    print(f"   ✓ username字段存在: {user.username}")
                else:
                    print(f"   ✗ username字段不存在")
                    return False
                
                # 检查是否错误使用了real_name
                if hasattr(user, 'real_name'):
                    print(f"   ! real_name字段存在(不应该使用)")
                else:
                    print(f"   ✓ 没有real_name字段(正确)")
                
                # 检查get_department_name方法
                dept_name = user.get_department_name()
                print(f"   ✓ get_department_name()方法正常: {dept_name}")
        except Exception as e:
            import pytest
            pytest.fail(f"User模型字段检查失败: {e}")
        
        # 5. 检查路由注册
        print("\n5. 检查路由注册...")
        try:
            from flask import url_for
            routes_to_check = [
                'admin.approval_roles',
                'admin.assign_roles_page',
                'admin.get_approval_roles',
            ]
            with app.test_request_context():
                for route_name in routes_to_check:
                    try:
                        url = url_for(route_name)
                        print(f"   ✓ {route_name}: {url}")
                    except Exception as e:
                        import pytest
                        pytest.fail(f"{route_name}: 路由不存在 - {e}")
        except Exception as e:
            print(f"   ✗ 路由检查失败: {e}")
            return False
        
        # 6. 测试ApprovalRole的to_dict方法
        print("\n6. 测试ApprovalRole.to_dict()...")
        try:
            role = ApprovalRole.query.first()
            if role:
                data = role.to_dict()
                required_fields = [
                    'id', 'code', 'name', 'description', 'icon', 'color',
                    'level', 'max_approval_amount', 'is_system_role',
                    'can_approve_repair', 'can_approve_part_request',
                    'can_approve_equipment_transfer', 'can_approve_equipment_scrap',
                    'can_approve_equipment_loan', 'can_approve_equipment_application'
                ]
                missing_fields = [f for f in required_fields if f not in data]
                if missing_fields:
                    print(f"   ✗ to_dict缺少字段: {missing_fields}")
                    return False
                print(f"   ✓ to_dict包含所有必要字段")
        except Exception as e:
            import pytest
            pytest.fail(f"to_dict测试失败: {e}")
        
        # 7. 测试UserApprovalRole的is_valid方法
        print("\n7. 测试UserApprovalRole.is_valid()...")
        try:
            assignment = UserApprovalRole.query.first()
            if assignment:
                is_valid = assignment.is_valid()
                print(f"   ✓ is_valid()方法正常: {is_valid}")
        except Exception as e:
            print(f"   ✗ is_valid测试失败: {e}")
            return False
        
        print("\n" + "=" * 60)
        print("✓ 所有测试通过!")
        print("=" * 60)

if __name__ == '__main__':
    success = test_approval_module()
    exit(0 if success else 1)
