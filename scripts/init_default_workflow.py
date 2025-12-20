#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
初始化默认审批流程模板和示例配置

创建6个默认工作流模板，包括：
1. 维修工单审批流程
2. 配件申请审批流程
3. 设备调拨审批流程
4. 设备报废审批流程
5. 设备借用审批流程
6. 设备申请审批流程

每个流程都包含3-4个审批步骤的示例配置。
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/..'))

from app import create_app, db
from app.approval_models import WorkflowTemplate, WorkflowNode
from app.models import WorkflowStep, User
from datetime import datetime

def get_admin_user():
    """获取管理员用户，作为流程创建者"""
    admin = User.query.filter_by(role='admin').first()
    if not admin:
        # 如果没有管理员，创建一个
        admin = User(
            username='admin',
            email='admin@example.com',
            password_hash='admin',  # 实际应使用密码哈希
            role='admin',
            is_active=True
        )
        db.session.add(admin)
        db.session.commit()
    return admin

def create_default_templates(app):
    """创建默认工作流模板"""
    with app.app_context():
        admin = get_admin_user()
        
        templates_config = [
            {
                'name': '标准维修工单审批',
                'order_type': 'repair_order',
                'description': '标准的维修工单审批流程：部门领导 → 管理员 → 技术员',
                'steps': [
                    {
                        'step_name': '部门领导审批',
                        'approver_role': 'department_head',
                        'sequence': 1,
                        'required_approvals': 1,
                    },
                    {
                        'step_name': '管理员审批',
                        'approver_role': 'admin',
                        'sequence': 2,
                        'required_approvals': 1,
                    },
                    {
                        'step_name': '技术员处理',
                        'approver_role': 'technician',
                        'sequence': 3,
                        'required_approvals': 1,
                    }
                ]
            },
            {
                'name': '标准配件申请审批',
                'order_type': 'part_request_order',
                'description': '配件申请工单审批流程：部门领导 → 管理员',
                'steps': [
                    {
                        'step_name': '部门领导审批',
                        'approver_role': 'department_head',
                        'sequence': 1,
                        'required_approvals': 1,
                    },
                    {
                        'step_name': '管理员审批',
                        'approver_role': 'admin',
                        'sequence': 2,
                        'required_approvals': 1,
                    }
                ]
            },
            {
                'name': '设备调拨审批流程',
                'order_type': 'equipment_transfer',
                'description': '设备调拨申请审批：部门领导 → 管理员',
                'steps': [
                    {
                        'step_name': '原部门领导审批',
                        'approver_role': 'department_head',
                        'sequence': 1,
                        'required_approvals': 1,
                    },
                    {
                        'step_name': '管理员审批',
                        'approver_role': 'admin',
                        'sequence': 2,
                        'required_approvals': 1,
                    }
                ]
            },
            {
                'name': '设备报废审批流程',
                'order_type': 'equipment_scrap',
                'description': '设备报废申请审批：部门领导 → 管理员',
                'steps': [
                    {
                        'step_name': '部门领导审批',
                        'approver_role': 'department_head',
                        'sequence': 1,
                        'required_approvals': 1,
                    },
                    {
                        'step_name': '管理员审批',
                        'approver_role': 'admin',
                        'sequence': 2,
                        'required_approvals': 1,
                    }
                ]
            },
            {
                'name': '设备借用审批流程',
                'order_type': 'equipment_loan',
                'description': '设备借用申请审批：部门领导 → 管理员',
                'steps': [
                    {
                        'step_name': '部门领导审批',
                        'approver_role': 'department_head',
                        'sequence': 1,
                        'required_approvals': 1,
                    },
                    {
                        'step_name': '管理员审批',
                        'approver_role': 'admin',
                        'sequence': 2,
                        'required_approvals': 1,
                    }
                ]
            },
            {
                'name': '设备申请审批流程',
                'order_type': 'equipment_application',
                'description': '新设备申请审批：部门领导 → 管理员',
                'steps': [
                    {
                        'step_name': '部门领导审批',
                        'approver_role': 'department_head',
                        'sequence': 1,
                        'required_approvals': 1,
                    },
                    {
                        'step_name': '管理员审批',
                        'approver_role': 'admin',
                        'sequence': 2,
                        'required_approvals': 1,
                    }
                ]
            }
        ]
        
        created_count = 0
        for config in templates_config:
            # 检查模板是否已存在
            existing = WorkflowTemplate.query.filter_by(
                order_type=config['order_type'],
                name=config['name']
            ).first()
            
            if existing:
                print(f"✓ 模板已存在: {config['name']} ({config['order_type']})")
                continue
            
            # 创建新模板
            template = WorkflowTemplate(
                name=config['name'],
                order_type=config['order_type'],
                description=config['description'],
                is_active=True,
                is_default=True,  # 将所有初始模板设为默认
                created_by_id=admin.id,
                created_date=datetime.utcnow()
            )
            db.session.add(template)
            db.session.flush()  # 获取模板ID
            
            # 创建步骤
            for step_config in config['steps']:
                step = WorkflowStep(
                    template_id=template.id,
                    sequence=step_config['sequence'],
                    step_name=step_config['step_name'],
                    approver_role=step_config['approver_role'],
                    is_parallel=False,
                    required_approvals=step_config.get('required_approvals', 1),
                    actions_on_reject='{"return_to": "requester"}'  # 默认拒绝时返回给申请人
                )
                db.session.add(step)
            
            created_count += 1
            print(f"✓ 创建模板: {config['name']} ({config['order_type']}) - {len(config['steps'])} 个步骤")
        
        db.session.commit()
        print(f"\n✓ 成功创建 {created_count} 个新工作流模板")

def sync_templates_to_nodes(app):
    """将模板步骤同步到工作流节点"""
    with app.app_context():
        templates = WorkflowTemplate.query.filter_by(is_default=True).all()
        total_nodes = 0
        
        for template in templates:
            for step in template.steps:
                # 检查节点是否已存在
                existing_node = WorkflowNode.query.filter_by(
                    order_type=template.order_type,
                    sequence=step.sequence,
                    name=step.step_name
                ).first()
                
                if existing_node:
                    continue
                
                # 创建新节点
                node = WorkflowNode(
                    name=step.step_name,
                    order_type=template.order_type,
                    role_required=step.approver_role,
                    sequence=step.sequence,
                    is_active=True,
                    is_parallel=step.is_parallel,
                    required_approvals=step.required_approvals,
                    actions_on_reject=step.actions_on_reject,
                    approver_user_id=None  # 默认不指定特定用户
                )
                db.session.add(node)
                total_nodes += 1
        
        db.session.commit()
        if total_nodes > 0:
            print(f"✓ 同步 {total_nodes} 个新工作流节点")
        else:
            print("✓ 所有节点已同步")

def print_workflow_summary(app):
    """打印工作流摘要信息"""
    with app.app_context():
        print("\n" + "="*60)
        print("工作流配置摘要")
        print("="*60)
        
        templates = WorkflowTemplate.query.all()
        print(f"\n模板总数: {len(templates)}")
        
        for template in templates:
            print(f"\n【{template.name}】")
            print(f"  订单类型: {template.order_type}")
            print(f"  是否默认: {'是' if template.is_default else '否'}")
            print(f"  步骤数: {len(template.steps)}")
            for step in template.steps:
                print(f"    {step.sequence}. {step.step_name} (角色: {step.approver_role})")
        
        print("\n" + "="*60)
        print("工作流节点总数: " + str(WorkflowNode.query.count()))
        print("="*60 + "\n")

if __name__ == '__main__':
    app = create_app()
    
    print("初始化默认工作流模板...\n")
    
    # 创建模板
    create_default_templates(app)
    
    # 同步节点
    sync_templates_to_nodes(app)
    
    # 打印摘要
    print_workflow_summary(app)
    
    print("✓ 初始化完成！")
