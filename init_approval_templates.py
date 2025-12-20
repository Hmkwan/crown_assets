#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
初始化审批流程模板
为6种工单类型创建标准审批流程模板
"""

from app import create_app, db
from app.approval_models import WorkflowTemplate, WorkflowNode
from app.approval_roles import ApprovalRole
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = create_app()


def get_role_id(role_code):
    """根据角色代码获取审批角色ID"""
    with app.app_context():
        role = ApprovalRole.query.filter_by(code=role_code).first()
        if role:
            return role.id
        logging.warning(f"未找到角色: {role_code}")
        return None


def create_repair_order_template():
    """创建维修工单审批模板
    流程: 维修技师审核 → 部门负责人审批 → (金额>¥5000时) 系统管理员终审
    """
    with app.app_context():
        # 检查模板是否已存在
        existing = WorkflowTemplate.query.filter_by(
            order_type='repair_order',
            is_default=True
        ).first()
        
        if existing:
            logging.info("维修工单模板已存在,跳过创建")
            return existing
        
        # 创建模板
        template = WorkflowTemplate(
            name='标准维修工单审批流程',
            description='适用于设备维修工单的标准审批流程。维修技师初审→部门负责人审批→高金额需管理员终审',
            order_type='repair_order',
            is_default=True,
            is_active=True
        )
        db.session.add(template)
        db.session.flush()  # 获取template.id
        
        # 节点1: 维修技师审核
        node1 = WorkflowNode(
            template_id=template.id,
            name='维修技师审核',
            order_type='repair_order',
            node_type='approval',
            sequence=1,
            approval_role_id=get_role_id('technician'),
            is_parallel=False,
            timeout_seconds=24*3600
        )
        db.session.add(node1)
        
        # 节点2: 部门负责人审批
        node2 = WorkflowNode(
            template_id=template.id,
            name='部门负责人审批',
            order_type='repair_order',
            node_type='approval',
            sequence=2,
            approval_role_id=get_role_id('department_head'),
            is_parallel=False,
            timeout_seconds=48*3600
        )
        db.session.add(node2)
        
        # 节点3: 系统管理员终审 (条件: 金额>¥5000)
        node3 = WorkflowNode(
            template_id=template.id,
            name='系统管理员终审',
            order_type='repair_order',
            node_type='approval',
            sequence=3,
            approval_role_id=get_role_id('admin'),
            is_parallel=False,
            amount_threshold=5000.0,
            skip_if_below_threshold=True,
            timeout_seconds=72*3600
        )
        db.session.add(node3)
        
        db.session.commit()
        logging.info(f"✅ 创建维修工单模板成功: {template.name} (ID: {template.id})")
        return template


def create_part_request_template():
    """创建备件领用工单审批模板
    流程: 仓库管理审核 → 部门负责人审批 → (金额>¥3000时) 财务审批
    """
    with app.app_context():
        existing = WorkflowTemplate.query.filter_by(
            order_type='part_request_order',
            is_default=True
        ).first()
        
        if existing:
            logging.info("备件领用工单模板已存在,跳过创建")
            return existing
        
        template = WorkflowTemplate(
            name='标准备件领用审批流程',
            description='适用于备件领用的标准审批流程。仓库管理审核库存→部门负责人审批→高金额需财务审批',
            order_type='part_request_order',
            is_default=True,
            is_active=True
        )
        db.session.add(template)
        db.session.flush()
        
        # 节点1: 仓库管理审核
        node1 = WorkflowNode(
            workflow_template_id=template.id,
            name='仓库管理审核',
            description='仓库管理员审核备件库存和领用申请',
            node_type='approval',
            sequence=1,
            approval_role_id=get_role_id('warehouse'),
            is_required=True,
            is_parallel=False,
            timeout_hours=24,
            action_on_reject='return'
        )
        db.session.add(node1)
        
        # 节点2: 部门负责人审批
        node2 = WorkflowNode(
            workflow_template_id=template.id,
            name='部门负责人审批',
            description='部门负责人审批备件领用申请',
            node_type='approval',
            sequence=2,
            approval_role_id=get_role_id('department_head'),
            is_required=True,
            is_parallel=False,
            timeout_hours=48,
            action_on_reject='return'
        )
        db.session.add(node2)
        
        # 节点3: 财务审批 (条件: 金额>¥3000)
        node3 = WorkflowNode(
            workflow_template_id=template.id,
            name='财务审批',
            description='高金额备件领用需要财务审批(金额>¥3000)',
            node_type='approval',
            sequence=3,
            approval_role_id=get_role_id('finance'),
            is_required=False,
            is_parallel=False,
            amount_threshold=3000.0,
            timeout_hours=72,
            action_on_reject='return'
        )
        db.session.add(node3)
        
        db.session.commit()
        logging.info(f"✅ 创建备件领用工单模板成功: {template.name} (ID: {template.id})")
        return template


def create_equipment_transfer_template():
    """创建设备调拨工单审批模板
    流程: 部门负责人审批 → 系统管理员终审
    """
    with app.app_context():
        existing = WorkflowTemplate.query.filter_by(
            order_type='equipment_transfer',
            is_default=True
        ).first()
        
        if existing:
            logging.info("设备调拨工单模板已存在,跳过创建")
            return existing
        
        template = WorkflowTemplate(
            name='标准设备调拨审批流程',
            description='适用于设备调拨的标准审批流程。部门负责人审批→系统管理员终审',
            order_type='equipment_transfer',
            is_default=True,
            is_active=True
        )
        db.session.add(template)
        db.session.flush()
        
        # 节点1: 部门负责人审批
        node1 = WorkflowNode(
            workflow_template_id=template.id,
            name='部门负责人审批',
            description='部门负责人审批设备调拨申请',
            node_type='approval',
            sequence=1,
            approval_role_id=get_role_id('department_head'),
            is_required=True,
            is_parallel=False,
            timeout_hours=48,
            action_on_reject='return'
        )
        db.session.add(node1)
        
        # 节点2: 系统管理员终审
        node2 = WorkflowNode(
            workflow_template_id=template.id,
            name='系统管理员终审',
            description='系统管理员终审设备调拨申请',
            node_type='approval',
            sequence=2,
            approval_role_id=get_role_id('admin'),
            is_required=True,
            is_parallel=False,
            timeout_hours=72,
            action_on_reject='return'
        )
        db.session.add(node2)
        
        db.session.commit()
        logging.info(f"✅ 创建设备调拨工单模板成功: {template.name} (ID: {template.id})")
        return template


def create_equipment_scrap_template():
    """创建设备报废工单审批模板
    流程: 部门负责人审批 → 财务审批
    """
    with app.app_context():
        existing = WorkflowTemplate.query.filter_by(
            order_type='equipment_scrap',
            is_default=True
        ).first()
        
        if existing:
            logging.info("设备报废工单模板已存在,跳过创建")
            return existing
        
        template = WorkflowTemplate(
            name='标准设备报废审批流程',
            description='适用于设备报废的标准审批流程。部门负责人审批→财务审批',
            order_type='equipment_scrap',
            is_default=True,
            is_active=True
        )
        db.session.add(template)
        db.session.flush()
        
        # 节点1: 部门负责人审批
        node1 = WorkflowNode(
            workflow_template_id=template.id,
            name='部门负责人审批',
            description='部门负责人审批设备报废申请',
            node_type='approval',
            sequence=1,
            approval_role_id=get_role_id('department_head'),
            is_required=True,
            is_parallel=False,
            timeout_hours=48,
            action_on_reject='return'
        )
        db.session.add(node1)
        
        # 节点2: 财务审批
        node2 = WorkflowNode(
            workflow_template_id=template.id,
            name='财务审批',
            description='财务部门审批设备报废并处理资产核销',
            node_type='approval',
            sequence=2,
            approval_role_id=get_role_id('finance'),
            is_required=True,
            is_parallel=False,
            timeout_hours=72,
            action_on_reject='return'
        )
        db.session.add(node2)
        
        db.session.commit()
        logging.info(f"✅ 创建设备报废工单模板成功: {template.name} (ID: {template.id})")
        return template


def create_equipment_loan_template():
    """创建设备借用工单审批模板
    流程: 部门负责人审批
    """
    with app.app_context():
        existing = WorkflowTemplate.query.filter_by(
            order_type='equipment_loan',
            is_default=True
        ).first()
        
        if existing:
            logging.info("设备借用工单模板已存在,跳过创建")
            return existing
        
        template = WorkflowTemplate(
            name='标准设备借用审批流程',
            description='适用于设备借用的标准审批流程。部门负责人审批即可',
            order_type='equipment_loan',
            is_default=True,
            is_active=True
        )
        db.session.add(template)
        db.session.flush()
        
        # 节点1: 部门负责人审批
        node1 = WorkflowNode(
            workflow_template_id=template.id,
            name='部门负责人审批',
            description='部门负责人审批设备借用申请',
            node_type='approval',
            sequence=1,
            approval_role_id=get_role_id('department_head'),
            is_required=True,
            is_parallel=False,
            timeout_hours=24,
            action_on_reject='return'
        )
        db.session.add(node1)
        
        db.session.commit()
        logging.info(f"✅ 创建设备借用工单模板成功: {template.name} (ID: {template.id})")
        return template


def create_equipment_application_template():
    """创建设备申请工单审批模板
    流程: 部门负责人审批 → 系统管理员审批 → 财务审批
    """
    with app.app_context():
        existing = WorkflowTemplate.query.filter_by(
            order_type='equipment_application',
            is_default=True
        ).first()
        
        if existing:
            logging.info("设备申请工单模板已存在,跳过创建")
            return existing
        
        template = WorkflowTemplate(
            name='标准设备申请审批流程',
            description='适用于新设备采购申请的标准审批流程。部门负责人→管理员→财务三级审批',
            order_type='equipment_application',
            is_default=True,
            is_active=True
        )
        db.session.add(template)
        db.session.flush()
        
        # 节点1: 部门负责人审批
        node1 = WorkflowNode(
            workflow_template_id=template.id,
            name='部门负责人审批',
            description='部门负责人审批设备采购申请',
            node_type='approval',
            sequence=1,
            approval_role_id=get_role_id('department_head'),
            is_required=True,
            is_parallel=False,
            timeout_hours=48,
            action_on_reject='return'
        )
        db.session.add(node1)
        
        # 节点2: 系统管理员审批
        node2 = WorkflowNode(
            workflow_template_id=template.id,
            name='系统管理员审批',
            description='系统管理员审批设备采购的必要性和合理性',
            node_type='approval',
            sequence=2,
            approval_role_id=get_role_id('admin'),
            is_required=True,
            is_parallel=False,
            timeout_hours=72,
            action_on_reject='return'
        )
        db.session.add(node2)
        
        # 节点3: 财务审批
        node3 = WorkflowNode(
            workflow_template_id=template.id,
            name='财务审批',
            description='财务部门审批采购预算和资金安排',
            node_type='approval',
            sequence=3,
            approval_role_id=get_role_id('finance'),
            is_required=True,
            is_parallel=False,
            timeout_hours=72,
            action_on_reject='return'
        )
        db.session.add(node3)
        
        db.session.commit()
        logging.info(f"✅ 创建设备申请工单模板成功: {template.name} (ID: {template.id})")
        return template


def main():
    """主函数"""
    logging.info("=" * 80)
    logging.info("开始初始化审批流程模板...")
    logging.info("=" * 80)
    
    with app.app_context():
        # 检查审批角色是否已初始化
        role_count = ApprovalRole.query.count()
        if role_count == 0:
            logging.error("❌ 请先运行 init_approval_roles.py 初始化审批角色!")
            return
        
        logging.info(f"✅ 检测到 {role_count} 个审批角色")
        
        # 创建6种工单类型的标准模板
        templates = []
        
        logging.info("\n1️⃣ 创建维修工单审批模板...")
        templates.append(create_repair_order_template())
        
        logging.info("\n2️⃣ 创建备件领用工单审批模板...")
        templates.append(create_part_request_template())
        
        logging.info("\n3️⃣ 创建设备调拨工单审批模板...")
        templates.append(create_equipment_transfer_template())
        
        logging.info("\n4️⃣ 创建设备报废工单审批模板...")
        templates.append(create_equipment_scrap_template())
        
        logging.info("\n5️⃣ 创建设备借用工单审批模板...")
        templates.append(create_equipment_loan_template())
        
        logging.info("\n6️⃣ 创建设备申请工单审批模板...")
        templates.append(create_equipment_application_template())
        
        # 统计信息
        logging.info("\n" + "=" * 80)
        logging.info("📊 初始化完成统计:")
        logging.info("=" * 80)
        
        template_count = WorkflowTemplate.query.filter_by(is_default=True).count()
        node_count = WorkflowNode.query.count()
        
        logging.info(f"✅ 标准模板总数: {template_count}")
        logging.info(f"✅ 工作流节点总数: {node_count}")
        
        logging.info("\n📋 模板清单:")
        for template in templates:
            if template:
                nodes = WorkflowNode.query.filter_by(
                    workflow_template_id=template.id
                ).order_by(WorkflowNode.sequence).all()
                
                logging.info(f"\n  • {template.name}")
                logging.info(f"    类型: {template.order_type}")
                logging.info(f"    节点数: {len(nodes)}")
                logging.info(f"    流程: " + " → ".join([node.name for node in nodes]))
        
        logging.info("\n" + "=" * 80)
        logging.info("✅ 所有审批流程模板初始化完成!")
        logging.info("=" * 80)


if __name__ == '__main__':
    main()
