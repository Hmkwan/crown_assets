#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""检查数据库表结构和新增字段"""

from app import create_app, db
from app.models import RepairOrder, WorkflowNode, ApprovalWorkflow
from sqlalchemy import inspect

app = create_app()

with app.app_context():
    inspector = inspect(db.engine)
    
    print('\n' + '='*70)
    print('  数据库表结构检查 - 新增审批流字段')
    print('='*70 + '\n')
    
    # 1. 检查 RepairOrder 表
    print('【1. RepairOrder (维修工单表)】')
    print('-'*70)
    repair_order_columns = inspector.get_columns('repair_order')
    
    # 查找 repair_cost 字段
    repair_cost_found = False
    for col in repair_order_columns:
        if col['name'] == 'repair_cost':
            repair_cost_found = True
            print(f'✓ repair_cost 字段存在')
            print(f'  类型: {col["type"]}')
            print(f'  可空: {col["nullable"]}')
            print(f'  默认值: {col.get("default", "无")}')
    
    if not repair_cost_found:
        print('✗ repair_cost 字段不存在!')
    
    print(f'\n所有字段 ({len(repair_order_columns)} 个):')
    for col in repair_order_columns:
        print(f'  • {col["name"]:30s} {str(col["type"]):20s}')
    
    # 2. 检查 WorkflowNode 表
    print('\n' + '='*70)
    print('【2. WorkflowNode (工作流节点表)】')
    print('-'*70)
    workflow_node_columns = inspector.get_columns('workflow_node')
    
    new_fields = ['amount_threshold', 'skip_if_below_threshold']
    for field in new_fields:
        found = False
        for col in workflow_node_columns:
            if col['name'] == field:
                found = True
                print(f'✓ {field} 字段存在')
                print(f'  类型: {col["type"]}')
                print(f'  可空: {col["nullable"]}')
                print(f'  默认值: {col.get("default", "无")}')
        if not found:
            print(f'✗ {field} 字段不存在!')
    
    print(f'\n所有字段 ({len(workflow_node_columns)} 个):')
    for col in workflow_node_columns:
        print(f'  • {col["name"]:30s} {str(col["type"]):20s}')
    
    # 3. 检查 ApprovalWorkflow 表
    print('\n' + '='*70)
    print('【3. ApprovalWorkflow (审批流程表)】')
    print('-'*70)
    approval_workflow_columns = inspector.get_columns('approval_workflow')
    
    new_approval_fields = [
        'action_type',
        'repair_cost_input',
        'transferred_from_id',
        'admin_action',
        'admin_operator_id'
    ]
    
    for field in new_approval_fields:
        found = False
        for col in approval_workflow_columns:
            if col['name'] == field:
                found = True
                print(f'✓ {field} 字段存在')
                print(f'  类型: {col["type"]}')
                print(f'  可空: {col["nullable"]}')
                print(f'  默认值: {col.get("default", "无")}')
        if not found:
            print(f'✗ {field} 字段不存在!')
    
    print(f'\n所有字段 ({len(approval_workflow_columns)} 个):')
    for col in approval_workflow_columns:
        print(f'  • {col["name"]:30s} {str(col["type"]):20s}')
    
    # 4. 测试数据检查
    print('\n' + '='*70)
    print('【4. 测试数据检查】')
    print('-'*70)
    
    # 检查是否有维修工单数据
    repair_count = RepairOrder.query.count()
    print(f'\n维修工单数量: {repair_count}')
    
    if repair_count > 0:
        sample = RepairOrder.query.first()
        print(f'\n示例工单 (ID: {sample.id}):')
        print(f'  设备名称: {sample.equipment_name if hasattr(sample, "equipment_name") else "N/A"}')
        if hasattr(sample, 'repair_cost'):
            print(f'  维修金额: {sample.repair_cost}')
        else:
            print(f'  维修金额: 字段不存在!')
    
    # 检查工作流节点
    node_count = WorkflowNode.query.count()
    print(f'\n工作流节点数量: {node_count}')
    
    if node_count > 0:
        sample_node = WorkflowNode.query.first()
        print(f'\n示例节点 (ID: {sample_node.id}):')
        print(f'  节点名称: {sample_node.name}')
        if hasattr(sample_node, 'amount_threshold'):
            print(f'  金额阈值: {sample_node.amount_threshold}')
        else:
            print(f'  金额阈值: 字段不存在!')
        if hasattr(sample_node, 'skip_if_below_threshold'):
            print(f'  低于阈值跳过: {sample_node.skip_if_below_threshold}')
        else:
            print(f'  低于阈值跳过: 字段不存在!')
    
    # 检查审批记录
    approval_count = ApprovalWorkflow.query.count()
    print(f'\n审批记录数量: {approval_count}')
    
    if approval_count > 0:
        sample_approval = ApprovalWorkflow.query.first()
        print(f'\n示例审批 (ID: {sample_approval.id}):')
        print(f'  审批人: {sample_approval.approver_id}')
        print(f'  状态: {sample_approval.status}')
        if hasattr(sample_approval, 'action_type'):
            print(f'  操作类型: {sample_approval.action_type}')
        else:
            print(f'  操作类型: 字段不存在!')
        if hasattr(sample_approval, 'repair_cost_input'):
            print(f'  输入金额: {sample_approval.repair_cost_input}')
        else:
            print(f'  输入金额: 字段不存在!')
    
    print('\n' + '='*70)
    print('  检查完成')
    print('='*70 + '\n')
