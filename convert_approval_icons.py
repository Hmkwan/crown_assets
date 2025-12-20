#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""将数据库中所有emoji图标转换为FontAwesome图标"""

from app import create_app, db
from app.approval_roles import ApprovalRole

app = create_app()

# emoji到FontAwesome的映射
ICON_MAPPING = {
    '👨‍💼': 'fa-user-tie',
    '👔': 'fa-user-tie',
    '🔧': 'fa-wrench',
    '📦': 'fa-box',
    '💰': 'fa-dollar-sign',
    '👤': 'fa-user'
}

with app.app_context():
    print("=" * 80)
    print("开始转换审批角色图标")
    print("=" * 80)
    
    roles = ApprovalRole.query.all()
    updated_count = 0
    
    for role in roles:
        old_icon = role.icon
        
        # 如果是emoji,转换为FontAwesome
        if old_icon in ICON_MAPPING:
            new_icon = ICON_MAPPING[old_icon]
            role.icon = new_icon
            updated_count += 1
            print(f"✓ ID={role.id}: {role.name}")
            print(f"  {old_icon} -> {new_icon}")
        else:
            print(f"- ID={role.id}: {role.name}")
            print(f"  图标已是FontAwesome: {old_icon}")
        print()
    
    if updated_count > 0:
        db.session.commit()
        print(f"\n成功更新 {updated_count} 个角色图标!")
    else:
        print("\n无需更新,所有图标已是FontAwesome格式")
    
    print("=" * 80)
    print("转换完成!")
    print("=" * 80)
