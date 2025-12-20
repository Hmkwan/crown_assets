"""
初始化默认审批流程模板
为常见业务（维修工单、配件申请、设备申请等）创建标准流程模板
"""
from app import db, create_app, get_beijing_now
from app.approval_models import WorkflowTemplate, WorkflowNode
import json


def init_workflow_templates():
    """初始化标准流程模板（企业级完整版本）"""
    app = create_app()
    with app.app_context():
        print("开始初始化审批流程模板...")
        print("\n支持的企业角色:")
        print("  - employee (申请人)")
        print("  - department_head (部门经理)")
        print("  - admin (IT资产管理员)")
        print("  - procurement (采购)")
        print("  - warehouse (库房)")
        print("  - security (安全/合规)")
        print("  - finance (财务)")
        print("  - executive (总经理/高层)")
        print("  - auditor (审计/稽核)")
        print("\n" + "="*50)
        
        # 1. 维修工单流程
        repair_template = WorkflowTemplate.query.filter_by(order_type='repair_order').first()
        if not repair_template:
            repair_template = WorkflowTemplate(
                name='标准维修工单流程',
                order_type='repair_order',
                description='部门负责人审批 → 管理员审批',
                is_active=True,
                created_by_id=1  # admin
            )
            db.session.add(repair_template)
            db.session.flush()
            
            # 节点1: 部门负责人审批
            node1 = WorkflowNode(
                template_id=repair_template.id,
                name='部门负责人审批',
                node_type='approval',
                sequence=1,
                role_required='department_head',
                timeout_seconds=86400 * 2  # 2天
            )
            db.session.add(node1)
            
            # 节点2: 管理员审批
            node2 = WorkflowNode(
                template_id=repair_template.id,
                name='管理员审批',
                node_type='approval',
                sequence=2,
                role_required='admin',
                timeout_seconds=86400 * 3
            )
            db.session.add(node2)
            
            print("✓ 创建维修工单流程模板")
        
        # 2. 配件申请流程
        part_template = WorkflowTemplate.query.filter_by(order_type='part_request_order').first()
        if not part_template:
            part_template = WorkflowTemplate(
                name='标准配件申请流程',
                order_type='part_request_order',
                description='部门负责人审批 → 管理员审批',
                is_active=True,
                created_by_id=1
            )
            db.session.add(part_template)
            db.session.flush()
            
            node1 = WorkflowNode(
                template_id=part_template.id,
                name='部门负责人审批',
                node_type='approval',
                sequence=1,
                role_required='department_head',
                timeout_seconds=86400 * 2
            )
            db.session.add(node1)
            
            node2 = WorkflowNode(
                template_id=part_template.id,
                name='管理员审批',
                node_type='approval',
                sequence=2,
                role_required='admin',
                timeout_seconds=86400 * 3,
                actions_on_approve=json.dumps([
                    {'name': 'update_inventory', 'action': 'deduct_stock'}
                ])
            )
            db.session.add(node2)
            
            print("✓ 创建配件申请流程模板")
        
        # 3. 设备申请流程（企业级完整版：新购/补件）
        equipment_template = WorkflowTemplate.query.filter_by(order_type='equipment_application').first()
        if not equipment_template:
            equipment_template = WorkflowTemplate(
                name='设备申请流程（新购/补件-企业级）',
                order_type='equipment_application',
                description='直属主管→IT审核→采购评估→财务预算→高层审批→采购下单→入库分配',
                is_active=True,
                created_by_id=1
            )
            db.session.add(equipment_template)
            db.session.flush()
            
            # 节点1: 直属主管审批
            node1 = WorkflowNode(
                template_id=equipment_template.id,
                name='直属主管审批',
                node_type='approval',
                sequence=1,
                role_required='department_head',
                timeout_seconds=86400 * 2  # 2天
            )
            db.session.add(node1)
            
            # 节点2: IT资产管理员审核（标准/型号）
            node2 = WorkflowNode(
                template_id=equipment_template.id,
                name='IT资产管理员审核',
                node_type='approval',
                sequence=2,
                role_required='admin',
                timeout_seconds=86400 * 3
            )
            db.session.add(node2)
            
            # 节点3: 采购评估与报价（并行示意）
            node3 = WorkflowNode(
                template_id=equipment_template.id,
                name='采购评估与报价',
                node_type='approval',
                sequence=3,
                role_required='procurement',
                is_parallel=True,
                required_approvals=1,
                timeout_seconds=86400 * 5
            )
            db.session.add(node3)
            
            # 节点4: 条件节点-金额检查
            node4 = WorkflowNode(
                template_id=equipment_template.id,
                name='金额阈值检查',
                node_type='condition',
                sequence=4,
                condition_expr='amount > 50000',
                metadata=json.dumps({'threshold': 50000, 'currency': 'CNY'})
            )
            db.session.add(node4)
            
            # 节点5: 财务预算确认（金额超阈值时）
            node5 = WorkflowNode(
                template_id=equipment_template.id,
                name='财务预算确认',
                node_type='approval',
                sequence=5,
                role_required='finance',
                timeout_seconds=86400 * 3
            )
            db.session.add(node5)
            
            # 节点6: 高层审批（大额或特殊类别）
            node6 = WorkflowNode(
                template_id=equipment_template.id,
                name='高层审批',
                node_type='approval',
                sequence=6,
                role_required='executive',
                timeout_seconds=86400 * 7,
                escalation_target='admin'
            )
            db.session.add(node6)
            
            # 节点7: 采购下单与入库（自动动作）
            node7 = WorkflowNode(
                template_id=equipment_template.id,
                name='采购下单与入库',
                node_type='auto',
                sequence=7,
                actions_on_approve=json.dumps([
                    {'name': 'create_purchase_order', 'action': 'generate_po'},
                    {'name': 'notify_warehouse', 'action': 'send_notification'},
                    {'name': 'update_inventory', 'action': 'add_stock'}
                ])
            )
            db.session.add(node7)
            
            # 节点8: IT分配设备
            node8 = WorkflowNode(
                template_id=equipment_template.id,
                name='IT分配设备',
                node_type='approval',
                sequence=8,
                role_required='admin',
                actions_on_approve=json.dumps([
                    {'name': 'assign_device', 'action': 'allocate_to_user'},
                    {'name': 'update_asset_record', 'action': 'set_owner'}
                ])
            )
            db.session.add(node8)
            
            print("✓ 创建设备申请流程模板（企业级8节点）")
        
        # 4. 设备借用流程
        loan_template = WorkflowTemplate.query.filter_by(order_type='equipment_loan').first()
        if not loan_template:
            loan_template = WorkflowTemplate(
                name='设备借用流程',
                order_type='equipment_loan',
                description='部门负责人审批 → 设备管理员确认',
                is_active=True,
                created_by_id=1
            )
            db.session.add(loan_template)
            db.session.flush()
            
            node1 = WorkflowNode(
                template_id=loan_template.id,
                name='部门负责人审批',
                node_type='approval',
                sequence=1,
                role_required='department_head'
            )
            db.session.add(node1)
            
            node2 = WorkflowNode(
                template_id=loan_template.id,
                name='设备管理员确认',
                node_type='approval',
                sequence=2,
                role_required='admin',
                actions_on_approve=json.dumps([
                    {'name': 'update_equipment_status', 'status': 'loaned'}
                ])
            )
            db.session.add(node2)
            
            print("✓ 创建设备借用流程模板")
        
        # 5. 设备调拨流程
        transfer_template = WorkflowTemplate.query.filter_by(order_type='equipment_transfer').first()
        if not transfer_template:
            transfer_template = WorkflowTemplate(
                name='设备调拨流程',
                order_type='equipment_transfer',
                description='调出部门审批 → 调入部门确认 → 管理员执行',
                is_active=True,
                created_by_id=1
            )
            db.session.add(transfer_template)
            db.session.flush()
            
            node1 = WorkflowNode(
                template_id=transfer_template.id,
                name='调出部门审批',
                node_type='approval',
                sequence=1,
                role_required='department_head'
            )
            db.session.add(node1)
            
            node2 = WorkflowNode(
                template_id=transfer_template.id,
                name='调入部门确认',
                node_type='approval',
                sequence=2,
                role_required='department_head'
            )
            db.session.add(node2)
            
            node3 = WorkflowNode(
                template_id=transfer_template.id,
                name='管理员执行',
                node_type='approval',
                sequence=3,
                role_required='admin',
                actions_on_approve=json.dumps([
                    {'name': 'transfer_equipment', 'action': 'update_department'}
                ])
            )
            db.session.add(node3)
            
            print("✓ 创建设备调拨流程模板")
        
        # 6. 设备报废流程
        scrap_template = WorkflowTemplate.query.filter_by(order_type='equipment_scrap').first()
        if not scrap_template:
            scrap_template = WorkflowTemplate(
                name='设备报废流程',
                order_type='equipment_scrap',
                description='资产管理员评估 → 部门负责人批准 → 财务确认',
                is_active=True,
                created_by_id=1
            )
            db.session.add(scrap_template)
            db.session.flush()
            
            node1 = WorkflowNode(
                template_id=scrap_template.id,
                name='资产管理员评估',
                node_type='approval',
                sequence=1,
                role_required='admin'
            )
            db.session.add(node1)
            
            node2 = WorkflowNode(
                template_id=scrap_template.id,
                name='部门负责人批准',
                node_type='approval',
                sequence=2,
                role_required='department_head'
            )
            db.session.add(node2)
            
            node3 = WorkflowNode(
                template_id=scrap_template.id,
                name='管理员最终确认',
                node_type='approval',
                sequence=3,
                role_required='admin',
                actions_on_approve=json.dumps([
                    {'name': 'scrap_equipment', 'action': 'set_status_retired'}
                ])
            )
            db.session.add(node3)
            
            print("✓ 创建设备报废流程模板")
        
        # 7. 并行审批示例（高金额采购需要多人会签）
        parallel_template = WorkflowTemplate.query.filter_by(order_type='high_value_procurement').first()
        if not parallel_template:
            parallel_template = WorkflowTemplate(
                name='高额采购并行审批流程',
                order_type='high_value_procurement',
                description='部门负责人 + 财务 + 采购 并行审批（需2/3同意）',
                is_active=True,
                created_by_id=1
            )
            db.session.add(parallel_template)
            db.session.flush()
            
            # 并行节点
            node1 = WorkflowNode(
                template_id=parallel_template.id,
                name='多方会签',
                node_type='approval',
                sequence=1,
                is_parallel=True,
                approver_user_ids=json.dumps([]),  # 实际使用时应填入具体 user_id
                required_approvals=2,  # 至少2人同意
                timeout_seconds=86400 * 5
            )
            db.session.add(node1)
            
            node2 = WorkflowNode(
                template_id=parallel_template.id,
                name='管理员最终审批',
                node_type='approval',
                sequence=2,
                role_required='admin'
            )
            db.session.add(node2)
            
            print("✓ 创建并行审批流程模板")
        
        # 8. 权限申请流程（账号/系统权限）
        permission_template = WorkflowTemplate.query.filter_by(order_type='permission_request').first()
        if not permission_template:
            permission_template = WorkflowTemplate(
                name='权限申请流程',
                order_type='permission_request',
                description='直属主管→系统管理员→安全合规→自动生效',
                is_active=True,
                created_by_id=1
            )
            db.session.add(permission_template)
            db.session.flush()
            
            node1 = WorkflowNode(
                template_id=permission_template.id,
                name='直属主管审批',
                node_type='approval',
                sequence=1,
                role_required='department_head',
                timeout_seconds=86400 * 2
            )
            db.session.add(node1)
            
            node2 = WorkflowNode(
                template_id=permission_template.id,
                name='系统管理员审批',
                node_type='approval',
                sequence=2,
                role_required='admin',
                timeout_seconds=86400 * 3
            )
            db.session.add(node2)
            
            node3 = WorkflowNode(
                template_id=permission_template.id,
                name='安全合规审批',
                node_type='approval',
                sequence=3,
                role_required='security',
                timeout_seconds=86400 * 2
            )
            db.session.add(node3)
            
            node4 = WorkflowNode(
                template_id=permission_template.id,
                name='自动生效',
                node_type='auto',
                sequence=4,
                actions_on_approve=json.dumps([
                    {'name': 'create_account', 'action': 'provision_user'},
                    {'name': 'grant_permissions', 'action': 'assign_roles'},
                    {'name': 'set_expiry', 'action': 'schedule_revoke'}
                ])
            )
            db.session.add(node4)
            
            print("✓ 创建权限申请流程模板")
        
        # 9. 设备报废流程（完整版）
        scrap_enhanced_template = WorkflowTemplate.query.filter_by(order_type='equipment_scrap_enhanced').first()
        if not scrap_enhanced_template:
            scrap_enhanced_template = WorkflowTemplate(
                name='设备报废流程（企业级）',
                order_type='equipment_scrap_enhanced',
                description='报废申请→IT检查→安全确认→财务核销→高层批准→执行报废',
                is_active=True,
                created_by_id=1
            )
            db.session.add(scrap_enhanced_template)
            db.session.flush()
            
            node1 = WorkflowNode(
                template_id=scrap_enhanced_template.id,
                name='IT检查确认',
                node_type='approval',
                sequence=1,
                role_required='admin'
            )
            db.session.add(node1)
            
            node2 = WorkflowNode(
                template_id=scrap_enhanced_template.id,
                name='安全合规确认',
                node_type='approval',
                sequence=2,
                role_required='security',
                metadata=json.dumps({'check_items': ['data_wipe', 'certificate_destroy']})
            )
            db.session.add(node2)
            
            node3 = WorkflowNode(
                template_id=scrap_enhanced_template.id,
                name='财务核销',
                node_type='approval',
                sequence=3,
                role_required='finance'
            )
            db.session.add(node3)
            
            node4 = WorkflowNode(
                template_id=scrap_enhanced_template.id,
                name='条件检查-价值阈值',
                node_type='condition',
                sequence=4,
                condition_expr='asset_value > 10000'
            )
            db.session.add(node4)
            
            node5 = WorkflowNode(
                template_id=scrap_enhanced_template.id,
                name='高层批准',
                node_type='approval',
                sequence=5,
                role_required='executive'
            )
            db.session.add(node5)
            
            node6 = WorkflowNode(
                template_id=scrap_enhanced_template.id,
                name='执行报废',
                node_type='auto',
                sequence=6,
                actions_on_approve=json.dumps([
                    {'name': 'update_status', 'action': 'set_retired'},
                    {'name': 'generate_scrap_certificate', 'action': 'create_document'},
                    {'name': 'update_accounting', 'action': 'write_off_asset'},
                    {'name': 'archive_record', 'action': 'store_audit_log'}
                ])
            )
            db.session.add(node6)
            
            print("✓ 创建设备报废流程模板（企业级6节点）")
        
        db.session.commit()
        print("\n" + "="*50)
        print("✅ 审批流程模板初始化完成！")
        print("="*50)
        
        # 打印统计
        total_templates = WorkflowTemplate.query.filter_by(is_active=True).count()
        total_nodes = WorkflowNode.query.filter_by(is_active=True).count()
        print(f"\n总计：{total_templates} 个模板，{total_nodes} 个节点")
        print("\n流程模板列表:")
        for tmpl in WorkflowTemplate.query.filter_by(is_active=True).all():
            node_count = WorkflowNode.query.filter_by(template_id=tmpl.id, is_active=True).count()
            print(f"  - {tmpl.name} ({tmpl.order_type}): {node_count} 节点")


if __name__ == '__main__':
    init_workflow_templates()
