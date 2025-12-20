"""
测试审批流程金额配置功能
"""
from app import create_app, db
from app.approval_models import WorkflowNode, WorkflowTemplate

def test_workflow_config():
    app = create_app()
    with app.app_context():
        print("=" * 70)
        print("  测试审批流程金额配置功能")
        print("=" * 70)
        
        # 1. 查看现有配置
        print("\n1. 查看维修工单流程节点:")
        repair_nodes = WorkflowNode.query.filter_by(
            order_type='repair_order',
            is_active=True
        ).order_by(WorkflowNode.sequence).all()
        
        for node in repair_nodes:
            print(f"\n   序号 {node.sequence}: {node.name}")
            print(f"   角色: {node.role_required}")
            if node.amount_threshold:
                print(f"   金额阈值: ¥{node.amount_threshold}")
                skip_rule = "金额 < 阈值时跳过" if node.skip_if_below_threshold else "金额 ≥ 阈值时需要"
                print(f"   跳过规则: {skip_rule}")
            else:
                print(f"   金额阈值: 未设置")
        
        # 2. 测试修改金额阈值
        print("\n\n2. 测试修改金额阈值:")
        test_node = repair_nodes[1] if len(repair_nodes) > 1 else None
        
        if test_node:
            print(f"\n   原配置:")
            print(f"   - 节点: {test_node.name}")
            print(f"   - 金额阈值: {test_node.amount_threshold or '未设置'}")
            
            # 修改配置
            from decimal import Decimal
            test_node.amount_threshold = Decimal('2000.00')
            test_node.skip_if_below_threshold = True
            db.session.commit()
            
            print(f"\n   新配置:")
            print(f"   - 节点: {test_node.name}")
            print(f"   - 金额阈值: ¥{test_node.amount_threshold}")
            print(f"   - 跳过规则: 金额 < ¥2000时跳过")
            print(f"   ✓ 配置修改成功!")
        
        # 3. 查看配件申请流程
        print("\n\n3. 查看配件申请流程节点:")
        part_nodes = WorkflowNode.query.filter_by(
            order_type='part_request_order',
            is_active=True
        ).order_by(WorkflowNode.sequence).all()
        
        if part_nodes:
            for node in part_nodes:
                print(f"\n   序号 {node.sequence}: {node.name}")
                print(f"   角色: {node.role_required}")
                if node.amount_threshold:
                    print(f"   金额阈值: ¥{node.amount_threshold}")
                    skip_rule = "金额 < 阈值时跳过" if node.skip_if_below_threshold else "金额 ≥ 阈值时需要"
                    print(f"   跳过规则: {skip_rule}")
        else:
            print("   未找到配件申请流程节点")
        
        # 4. 统计所有流程类型
        print("\n\n4. 流程类型统计:")
        templates = WorkflowTemplate.query.filter_by(is_active=True).all()
        
        for template in templates:
            node_count = WorkflowNode.query.filter_by(
                order_type=template.order_type,
                is_active=True
            ).count()
            
            amount_nodes = WorkflowNode.query.filter_by(
                order_type=template.order_type,
                is_active=True
            ).filter(WorkflowNode.amount_threshold.isnot(None)).count()
            
            print(f"\n   {template.name}:")
            print(f"   - 节点数量: {node_count}")
            print(f"   - 含金额阈值: {amount_nodes}")
        
        print("\n" + "=" * 70)
        print("  测试完成!")
        print("=" * 70)
        
        # 访问提示
        print("\n📌 Web界面访问:")
        print("   URL: http://localhost:5020/admin/workflow_config")
        print("   菜单: 审批 → 金额阈值配置")
        print("   权限: 管理员(admin)登录后访问")
        print()

if __name__ == '__main__':
    test_workflow_config()
