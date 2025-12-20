#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
初始化默认审批流程和节点
为各种工单类型创建标准的审批流程
"""

from app import create_app, db
from app.approval_models import WorkflowNode, WorkflowTemplate
from app.approval_roles import ApprovalRole
from datetime import datetime

app = create_app()

def init_default_workflows():
    """初始化默认审批流程"""
    
    with app.app_context():
        print('\n' + '='*70)
        print('  初始化默认审批流程和节点')
        print('='*70 + '\n')
        
        # 1. 创建默认工作流模板
        templates = [
            {
                'code': 'repair_order_std_v1',
                'name': '维修工单标准流程',
                'order_type': 'repair_order',
                'version': 1,
                'is_active': True,
                'is_default': True
            },
            {
                'code': 'part_request_std_v1',
                'name': '配件申请标准流程',
                'order_type': 'part_request_order',
                'version': 1,
                'is_active': True,
                'is_default': True
            },
            {
                'code': 'equipment_transfer_std_v1',
                'name': '设备调拨标准流程',
                'order_type': 'equipment_transfer',
                'version': 1,
                'is_active': True,
                'is_default': True
            },
            {
                'code': 'equipment_scrap_std_v1',
                'name': '设备报废标准流程',
                'order_type': 'equipment_scrap',
                'version': 1,
                'is_active': True,
                'is_default': True
            },
            {
                'code': 'equipment_loan_std_v1',
                'name': '设备借用标准流程',
                'order_type': 'equipment_loan',
                'version': 1,
                'is_active': True,
                'is_default': True
            },
            {
                'code': 'equipment_application_std_v1',
                'name': '设备申请标准流程',
                'order_type': 'equipment_application',
                'version': 1,
                'is_active': True,
                'is_default': True
            }
        ]
        
        created_templates = {}
        for tpl_data in templates:
            existing = WorkflowTemplate.query.filter_by(
                order_type=tpl_data['order_type']
            ).first()
            
            if not existing:
                template = WorkflowTemplate(**tpl_data)
                db.session.add(template)
                db.session.flush()  # 获取ID
                created_templates[tpl_data['order_type']] = template
                print(f'[OK] 创建模板: {tpl_data["name"]}')
            else:
                created_templates[tpl_data['order_type']] = existing
                print(f'  模板已存在: {tpl_data["name"]}')
        
        db.session.commit()
        
        print('\n' + '-'*70)
        print('  创建默认工作流节点')
        print('-'*70 + '\n')
        
        # 2. 创建默认工作流节点
        workflow_nodes = [
            # === 维修工单流程 ===
            {
                'template_id': created_templates['repair_order'].id,
                'name': '部门负责人初审',
                'order_type': 'repair_order',
                'node_type': 'approval',
                'role_required': 'department_head',
                'sequence': 1,
                'is_active': True,
                'amount_threshold': None,
                'skip_if_below_threshold': False
            },
            {
                'template_id': created_templates['repair_order'].id,
                'name': '管理员评估金额',
                'order_type': 'repair_order',
                'node_type': 'approval',
                'role_required': 'admin',
                'sequence': 2,
                'is_active': True,
                'amount_threshold': None,
                'skip_if_below_threshold': False
            },
            {
                'template_id': created_templates['repair_order'].id,
                'name': '部门负责人确认金额',
                'order_type': 'repair_order',
                'node_type': 'approval',
                'role_required': 'department_head',
                'sequence': 3,
                'is_active': True,
                'amount_threshold': 5000.00,  # 超过5000元需要此节点
                'skip_if_below_threshold': False
            },
            {
                'template_id': created_templates['repair_order'].id,
                'name': '技术员执行',
                'order_type': 'repair_order',
                'node_type': 'execution',
                'role_required': 'technician',
                'sequence': 4,
                'is_active': True,
                'amount_threshold': None,
                'skip_if_below_threshold': False
            },
            
            # === 配件申请流程 ===
            {
                'template_id': created_templates['part_request_order'].id,
                'name': '部门负责人审批',
                'order_type': 'part_request_order',
                'node_type': 'approval',
                'role_required': 'department_head',
                'sequence': 1,
                'is_active': True
            },
            {
                'template_id': created_templates['part_request_order'].id,
                'name': '管理员审批',
                'order_type': 'part_request_order',
                'node_type': 'approval',
                'role_required': 'admin',
                'sequence': 2,
                'is_active': True,
                'amount_threshold': 1000.00,  # 超过1000元需要管理员审批
                'skip_if_below_threshold': True  # 低于1000元跳过此节点
            },
            {
                'template_id': created_templates['part_request_order'].id,
                'name': '仓库管理员发货',
                'order_type': 'part_request_order',
                'node_type': 'execution',
                'role_required': 'warehouse',
                'sequence': 3,
                'is_active': True
            },
            
            # === 设备调拨流程 ===
            {
                'template_id': created_templates['equipment_transfer'].id,
                'name': '调出部门负责人审批',
                'order_type': 'equipment_transfer',
                'node_type': 'approval',
                'role_required': 'department_head',
                'sequence': 1,
                'is_active': True
            },
            {
                'template_id': created_templates['equipment_transfer'].id,
                'name': '管理员审批',
                'order_type': 'equipment_transfer',
                'node_type': 'approval',
                'role_required': 'admin',
                'sequence': 2,
                'is_active': True
            },
            {
                'template_id': created_templates['equipment_transfer'].id,
                'name': '调入部门负责人确认',
                'order_type': 'equipment_transfer',
                'node_type': 'approval',
                'role_required': 'department_head',
                'sequence': 3,
                'is_active': True
            },
            
            # === 设备报废流程 ===
            {
                'template_id': created_templates['equipment_scrap'].id,
                'name': '部门负责人审批',
                'order_type': 'equipment_scrap',
                'node_type': 'approval',
                'role_required': 'department_head',
                'sequence': 1,
                'is_active': True
            },
            {
                'template_id': created_templates['equipment_scrap'].id,
                'name': '管理员审批',
                'order_type': 'equipment_scrap',
                'node_type': 'approval',
                'role_required': 'admin',
                'sequence': 2,
                'is_active': True
            },
            {
                'template_id': created_templates['equipment_scrap'].id,
                'name': '财务审批',
                'order_type': 'equipment_scrap',
                'node_type': 'approval',
                'role_required': 'finance',
                'sequence': 3,
                'is_active': True,
                'amount_threshold': 10000.00,  # 价值超过1万元需要财务审批
                'skip_if_below_threshold': True
            },
            
            # === 设备借用流程 ===
            {
                'template_id': created_templates['equipment_loan'].id,
                'name': '设备所属部门负责人审批',
                'order_type': 'equipment_loan',
                'node_type': 'approval',
                'role_required': 'department_head',
                'sequence': 1,
                'is_active': True
            },
            {
                'template_id': created_templates['equipment_loan'].id,
                'name': '管理员审批',
                'order_type': 'equipment_loan',
                'node_type': 'approval',
                'role_required': 'admin',
                'sequence': 2,
                'is_active': True
            },
            
            # === 设备申请流程 ===
            {
                'template_id': created_templates['equipment_application'].id,
                'name': '部门负责人审批',
                'order_type': 'equipment_application',
                'node_type': 'approval',
                'role_required': 'department_head',
                'sequence': 1,
                'is_active': True
            },
            {
                'template_id': created_templates['equipment_application'].id,
                'name': '管理员审批',
                'order_type': 'equipment_application',
                'node_type': 'approval',
                'role_required': 'admin',
                'sequence': 2,
                'is_active': True
            },
            {
                'template_id': created_templates['equipment_application'].id,
                'name': '资产管理员分配',
                'order_type': 'equipment_application',
                'node_type': 'execution',
                'role_required': 'asset_manager',
                'sequence': 3,
                'is_active': True
            }
        ]
        
        created_count = 0
        for node_data in workflow_nodes:
            # 移除 order_type 字段(新模型不再使用)
            order_type = node_data.pop('order_type', None)
            role_required = node_data.pop('role_required', None)
            
            # 生成 code 字段(如果不存在)
            if 'code' not in node_data:
                template_id = node_data['template_id']
                sequence = node_data['sequence']
                # 从 template 获取 order_type
                template = WorkflowTemplate.query.get(template_id)
                if template:
                    node_data['code'] = f"{template.order_type}_node_{sequence}"
            
            # 根据 role_required 查找审批角色
            if role_required:
                # 角色名称映射
                role_mapping = {
                    'technician': 'TECHNICIAN',
                    'admin': 'SYSTEM_ADMIN',
                    'department_head': 'DEPT_HEAD',
                    'warehouse_manager': 'WAREHOUSE_MGR',
                    'warehouse': 'WAREHOUSE_MGR',
                    'asset_manager': 'SYSTEM_ADMIN'  # 暂时映射到系统管理员
                }
                role_code = role_mapping.get(role_required, 'SYSTEM_ADMIN')
                approval_role = ApprovalRole.query.filter_by(code=role_code).first()
                if approval_role:
                    node_data['approval_role_id'] = approval_role.id
            
            existing = WorkflowNode.query.filter_by(
                template_id=node_data['template_id'],
                sequence=node_data['sequence']
            ).first()
            
            if not existing:
                node = WorkflowNode(**node_data)
                db.session.add(node)
                created_count += 1
                print(f'[OK] 创建节点: {node_data["name"]} (序号: {node_data["sequence"]})')
            else:
                print(f'  节点已存在: {node_data["name"]}')
        
        db.session.commit()
        
        print('\n' + '='*70)
        print('  初始化完成')
        print('='*70)
        print(f'\n创建了 {len(created_templates)} 个工作流模板')
        print(f'创建了 {created_count} 个工作流节点')
        print('\n工作流概览:\n')
        
        # 显示工作流概览
        for order_type, template in created_templates.items():
            nodes = WorkflowNode.query.filter_by(
                template_id=template.id
            ).order_by(WorkflowNode.sequence).all()
            
            print(f'【{template.name}】')
            for node in nodes:
                threshold_info = ''
                if node.amount_threshold:
                    if node.skip_if_below_threshold:
                        threshold_info = f' (金额 < ¥{node.amount_threshold:.2f} 时跳过)'
                    else:
                        threshold_info = f' (金额 >= ¥{node.amount_threshold:.2f} 时需要)'
                role_name = node.approval_role.name if node.approval_role else node.node_type
                print(f'  {node.sequence}. {node.name} [{role_name}]{threshold_info}')
            print()
        
        print('='*70 + '\n')


if __name__ == '__main__':
    init_default_workflows()

