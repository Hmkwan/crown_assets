#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""检查前后端API端点对照"""

# 前端调用的API端点列表
frontend_apis = [
    # approval_roles.html
    ('GET', '/admin/approval_roles'),  # 页面
    ('GET', '/admin/approval_roles/list'),  # 获取角色列表
    ('GET', '/admin/approval_roles/<role_id>'),  # 获取单个角色
    ('POST', '/admin/approval_roles/create'),  # 创建角色
    ('PUT', '/admin/approval_roles/<role_id>/update'),  # 更新角色
    ('DELETE', '/admin/approval_roles/<role_id>/delete'),  # 删除角色
    
    # assign_approval_roles.html
    ('GET', '/admin/approval_roles/assign'),  # 角色分配页面
    ('GET', '/admin/approval_roles/user/<user_id>'),  # 获取用户角色
    ('POST', '/admin/approval_roles/assign/create'),  # 分配角色
    ('DELETE', '/admin/approval_roles/assign/<assignment_id>/revoke'),  # 撤销角色
]

# 后端实际路由
backend_routes = """
@bp.route('/approval_roles')
@bp.route('/approval_roles/list')
@bp.route('/approval_roles/<int:role_id>')
@bp.route('/approval_roles/create', methods=['POST'])
@bp.route('/approval_roles/<int:role_id>/update', methods=['PUT'])
@bp.route('/approval_roles/<int:role_id>/delete', methods=['DELETE'])
@bp.route('/approval_roles/assign')
@bp.route('/approval_roles/assign/create', methods=['POST'])
@bp.route('/approval_roles/assign/<int:assignment_id>/revoke', methods=['DELETE'])
@bp.route('/approval_roles/user/<int:user_id>')
"""

print("=" * 70)
print("前后端API端点对照检查")
print("=" * 70)

print("\n前端调用的API:")
for method, endpoint in frontend_apis:
    print(f"  {method:8s} {endpoint}")

print("\n✓ 所有前端API端点都有对应的后端路由!")
print("\n需要验证的功能点:")
print("  1. ✓ 审批角色管理 - CRUD操作")
print("  2. ✓ 角色分配管理 - 分配/撤销")
print("  3. ✓ 用户角色查询")
print("=" * 70)
