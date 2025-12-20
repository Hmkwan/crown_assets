#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
更新默认审批流程节点,使用新的审批角色系统
"""

from app import create_app, db
from app.approval_models import WorkflowNode
from app.approval_roles import ApprovalRole

app = create_app()

# 角色映射: 旧role_required -> 新approval_role code
ROLE_MAPPING = {
    'admin': 'admin',
    'department_head': 'department_head',
    'technician': 'technician',
    'warehouse': 'warehouse',
    'finance': 'finance'
}

def update_workflow_nodes():
    """更新工作流节点,设置approval_role_id"""
    
    with app.app_context():
        print('\n' + '='*70)
        print('  更新工作流节点 - 迁移到审批角色系统')
        print('='*70 + '\n')
        
        # 获取所有审批角色
        roles = ApprovalRole.query.all()
        role_dict = {role.code: role for role in roles}
        
        print(f'已加载 {len(role_dict)} 个审批角色:\n')
        for code, role in role_dict.items():
            print(f'  {code:20} -> ID={role.id}, {role.name}')
        
        print('\n' + '-'*70)
        print('  开始更新节点')
        print('-'*70 + '\n')
        
        # 获取所有节点
        nodes = WorkflowNode.query.filter(WorkflowNode.approval_role_id.is_(None)).all()
        
        if not nodes:
            print('✓ 所有节点已经设置了审批角色,无需更新')
            return
        
        updated_count = 0
        skipped_count = 0
        
        for node in nodes:
            old_role = node.role_required
            
            if not old_role:
                print(f'  跳过节点 #{node.id}: {node.name} (无角色要求)')
                skipped_count += 1
                continue
            
            # 查找对应的新角色
            role_code = ROLE_MAPPING.get(old_role)
            
            if role_code and role_code in role_dict:
                approval_role = role_dict[role_code]
                node.approval_role_id = approval_role.id
                
                print(f'✓ 节点 #{node.id}: {node.name:30} | {old_role:20} -> {approval_role.name} (ID={approval_role.id})')
                updated_count += 1
            else:
                print(f'  跳过节点 #{node.id}: {node.name:30} | 未找到匹配角色: {old_role}')
                skipped_count += 1
        
        if updated_count > 0:
            db.session.commit()
            print(f'\n✓ 成功更新 {updated_count} 个节点')
        
        if skipped_count > 0:
            print(f'  跳过 {skipped_count} 个节点')
        
        print('\n' + '='*70)
        print('  更新完成!')
        print('='*70 + '\n')


if __name__ == '__main__':
    update_workflow_nodes()
