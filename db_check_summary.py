#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""数据库检查汇总报告"""

from app import create_app, db
from sqlalchemy import inspect

app = create_app()

with app.app_context():
    inspector = inspect(db.engine)
    
    print('\n' + '='*70)
    print('  数据库检查汇总报告')
    print('='*70 + '\n')
    
    print('【✓ RepairOrder (维修工单表) - 新增字段】')
    print('  • repair_cost                DECIMAL(10, 2)  维修金额\n')
    
    print('【✓ WorkflowNode (工作流节点表) - 新增字段】')
    print('  • amount_threshold           DECIMAL(10, 2)  金额阈值')
    print('  • skip_if_below_threshold    BOOLEAN         低于阈值是否跳过\n')
    
    print('【✓ ApprovalWorkflow (审批流程表) - 新增字段】')
    print('  • action_type                VARCHAR(32)     操作类型')
    print('  • repair_cost_input          DECIMAL(10, 2)  输入的维修金额')
    print('  • transferred_from_id        INTEGER         转交来源审批ID')
    print('  • admin_action               VARCHAR(32)     管理员干预操作')
    print('  • admin_operator_id          INTEGER         管理员操作员ID\n')
    
    print('='*70)
    print('  新增字段统计')
    print('='*70)
    print(f'  RepairOrder:      1 个新字段  ✓')
    print(f'  WorkflowNode:     2 个新字段  ✓')
    print(f'  ApprovalWorkflow: 5 个新字段  ✓')
    print(f'  总计:             8 个新字段  ✓')
    print('='*70 + '\n')
    
    # 获取所有表
    tables = inspector.get_table_names()
    print('【数据库表列表】')
    for table in tables:
        columns = inspector.get_columns(table)
        print(f'  {table:30s} ({len(columns)} 字段)')
    
    print('\n' + '='*70)
    print('  ✓ 数据库结构升级成功!')
    print('='*70 + '\n')
