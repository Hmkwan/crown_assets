#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
初始化审批流程模板 (精简版)
为6种工单类型创建标准审批流程模板
"""

from app import create_app, db
from app.approval_models import WorkflowTemplate, WorkflowNode
from app.approval_roles import ApprovalRole
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = create_app()


# 模板定义: 每个模板包含名称、描述、工单类型、节点列表
TEMPLATES = [
    {
        'name': '标准维修工单审批流程',
        'description': '适用于设备维修工单的标准审批流程',
        'order_type': 'repair_order',
        'nodes': [
            {'name': '维修技师审核', 'role': 'technician', 'sequence': 1, 'timeout': 24},
            {'name': '部门负责人审批', 'role': 'department_head', 'sequence': 2, 'timeout': 48},
            {'name': '系统管理员终审', 'role': 'admin', 'sequence': 3, 'timeout': 72, 'amount_threshold': 5000.0, 'skip_below': True}
        ]
    },
    {
        'name': '标准备件领用审批流程',
        'description': '适用于备件领用的标准审批流程',
        'order_type': 'part_request_order',
        'nodes': [
            {'name': '仓库管理审核', 'role': 'warehouse', 'sequence': 1, 'timeout': 24},
            {'name': '部门负责人审批', 'role': 'department_head', 'sequence': 2, 'timeout': 48},
            {'name': '财务审批', 'role': 'finance', 'sequence': 3, 'timeout': 72, 'amount_threshold': 3000.0, 'skip_below': True}
        ]
    },
    {
        'name': '标准设备调拨审批流程',
        'description': '适用于设备调拨的标准审批流程',
        'order_type': 'equipment_transfer',
        'nodes': [
            {'name': '部门负责人审批', 'role': 'department_head', 'sequence': 1, 'timeout': 48},
            {'name': '系统管理员终审', 'role': 'admin', 'sequence': 2, 'timeout': 72}
        ]
    },
    {
        'name': '标准设备报废审批流程',
        'description': '适用于设备报废的标准审批流程',
        'order_type': 'equipment_scrap',
        'nodes': [
            {'name': '部门负责人审批', 'role': 'department_head', 'sequence': 1, 'timeout': 48},
            {'name': '财务审批', 'role': 'finance', 'sequence': 2, 'timeout': 72}
        ]
    },
    {
        'name': '标准设备借用审批流程',
        'description': '适用于设备借用的标准审批流程',
        'order_type': 'equipment_loan',
        'nodes': [
            {'name': '部门负责人审批', 'role': 'department_head', 'sequence': 1, 'timeout': 24}
        ]
    },
    {
        'name': '标准设备申请审批流程',
        'description': '适用于新设备采购申请的标准审批流程',
        'order_type': 'equipment_application',
        'nodes': [
            {'name': '部门负责人审批', 'role': 'department_head', 'sequence': 1, 'timeout': 48},
            {'name': '系统管理员审批', 'role': 'admin', 'sequence': 2, 'timeout': 72},
            {'name': '财务审批', 'role': 'finance', 'sequence': 3, 'timeout': 72}
        ]
    }
]


def get_role_id(role_code):
    """根据角色代码获取审批角色ID"""
    role = ApprovalRole.query.filter_by(code=role_code).first()
    if role:
        return role.id
    logging.warning(f"未找到角色: {role_code}")
    return None


def create_template(template_def):
    """创建单个模板及其节点"""
    # 检查是否已存在
    existing = WorkflowTemplate.query.filter_by(
        order_type=template_def['order_type'],
        is_default=True
    ).first()
    
    if existing:
        logging.info(f"模板已存在: {template_def['name']}, 跳过创建")
        return existing
    
    # 创建模板
    template = WorkflowTemplate(
        name=template_def['name'],
        description=template_def['description'],
        order_type=template_def['order_type'],
        is_default=True,
        is_active=True
    )
    db.session.add(template)
    db.session.flush()
    
    # 创建节点
    for node_def in template_def['nodes']:
        node = WorkflowNode(
            template_id=template.id,
            name=node_def['name'],
            order_type=template_def['order_type'],
            node_type='approval',
            sequence=node_def['sequence'],
            approval_role_id=get_role_id(node_def['role']),
            is_parallel=False,
            timeout_seconds=node_def['timeout'] * 3600,
            amount_threshold=node_def.get('amount_threshold'),
            skip_if_below_threshold=node_def.get('skip_below', False)
        )
        db.session.add(node)
    
    db.session.commit()
    logging.info(f"✅ 创建模板: {template.name} (ID: {template.id}, 节点数: {len(template_def['nodes'])})")
    return template


def main():
    """主函数"""
    logging.info("=" * 80)
    logging.info("开始初始化审批流程模板...")
    logging.info("=" * 80)
    
    with app.app_context():
        # 检查审批角色
        role_count = ApprovalRole.query.count()
        if role_count == 0:
            logging.error("❌ 请先运行 init_approval_roles.py 初始化审批角色!")
            return
        
        logging.info(f"✅ 检测到 {role_count} 个审批角色\n")
        
        # 创建所有模板
        created_templates = []
        for i, template_def in enumerate(TEMPLATES, 1):
            logging.info(f"{i}️⃣ 创建 {template_def['name']}...")
            template = create_template(template_def)
            if template:
                created_templates.append(template)
        
        # 统计信息
        logging.info("\n" + "=" * 80)
        logging.info("📊 初始化完成统计:")
        logging.info("=" * 80)
        
        template_count = WorkflowTemplate.query.filter_by(is_default=True).count()
        node_count = WorkflowNode.query.filter(WorkflowNode.template_id.isnot(None)).count()
        
        logging.info(f"✅ 标准模板总数: {template_count}")
        logging.info(f"✅ 模板节点总数: {node_count}")
        
        logging.info("\n📋 模板清单:")
        for template in created_templates:
            nodes = WorkflowNode.query.filter_by(
                template_id=template.id
            ).order_by(WorkflowNode.sequence).all()
            
            node_names = " → ".join([
                f"{node.name}" + (f"(>{node.amount_threshold})" if node.amount_threshold else "")
                for node in nodes
            ])
            
            logging.info(f"  • {template.name}")
            logging.info(f"    类型: {template.order_type}")
            logging.info(f"    流程: {node_names}\n")
        
        logging.info("=" * 80)
        logging.info("✅ 所有审批流程模板初始化完成!")
        logging.info("=" * 80)


if __name__ == '__main__':
    main()
