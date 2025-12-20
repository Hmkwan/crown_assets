#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""检查审批角色表中的图标字段"""

from app import create_app, db
from app.approval_roles import ApprovalRole

app = create_app()

with app.app_context():
    print("=" * 80)
    print("审批角色图标检查")
    print("=" * 80)
    
    roles = ApprovalRole.query.all()
    print(f"\n总共 {len(roles)} 个审批角色:\n")
    
    for role in roles:
        print(f"ID={role.id}: {role.name}")
        print(f"  图标: {role.icon}")
        print(f"  描述: {role.description}")
        print()
    
    print("=" * 80)
    print("检查完成!")
    print("=" * 80)
