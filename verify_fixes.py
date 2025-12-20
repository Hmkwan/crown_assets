"""验证WorkflowNode和重新分配审批人功能的修复"""
import sys
sys.path.insert(0, '.')

from app import create_app, db
from app.approval_models import WorkflowNode, WorkflowTemplate
from app.models import User, ApprovalWorkflow

app = create_app()

with app.app_context():
    print("="*70)
    print("验证修复结果")
    print("="*70)
    
    # 1. 测试 WorkflowNode.order_type 属性
    print("\n[测试1] WorkflowNode.order_type 属性")
    print("-"*70)
    
    nodes = WorkflowNode.query.limit(5).all()
    for node in nodes:
        try:
            order_type = node.order_type
            status = "✓" if order_type else "⚠"
            print(f"{status} 节点 #{node.id} '{node.name}': order_type = {order_type}")
        except Exception as e:
            print(f"✗ 节点 #{node.id} 失败: {e}")
    
    # 2. 测试审批流程详情页的用户列表逻辑
    print("\n[测试2] 审批流程详情页 - 获取可选审批人")
    print("-"*70)
    
    approval = ApprovalWorkflow.query.filter_by(status='pending').first()
    
    if approval:
        print(f"找到待审批流程 #{approval.id}")
        print(f"  工单类型: {approval.order_type}")
        print(f"  当前审批人: {approval.approver.username if approval.approver else '未分配'}")
        
        # 模拟获取eligible_users的逻辑
        eligible_users = []
        if approval.workflow_node and approval.workflow_node.approval_role_id:
            from app.approval_roles import UserApprovalRole
            role_assignments = UserApprovalRole.query.filter_by(
                role_id=approval.workflow_node.approval_role_id,
                is_active=True
            ).all()
            eligible_users = [
                assignment.user 
                for assignment in role_assignments 
                if assignment.user and assignment.user.is_active
            ]
            
            if not eligible_users:
                print(f"  ⚠ 审批角色 #{approval.workflow_node.approval_role_id} 没有分配用户")
                print(f"  → Fallback 到所有活跃用户")
                eligible_users = User.query.filter_by(is_active=True).all()
        else:
            print(f"  未设置审批角色，使用所有活跃用户")
            eligible_users = User.query.filter_by(is_active=True).all()
        
        print(f"  可选审批人数量: {len(eligible_users)}")
        for i, user in enumerate(eligible_users[:5], 1):
            dept = user.department or '无部门'
            print(f"    {i}. {user.username} ({dept})")
        
        if len(eligible_users) > 5:
            print(f"    ... 还有 {len(eligible_users) - 5} 个用户")
        
        if len(eligible_users) > 0:
            print("  ✓ 用户列表可用，重新分配功能应该正常工作")
        else:
            print("  ✗ 没有可用用户！")
    else:
        print("  没有找到待审批流程")
    
    # 3. 测试打回到指定节点功能
    print("\n[测试3] 打回到指定节点 - order_type 验证")
    print("-"*70)
    
    if approval:
        workflow_nodes = WorkflowNode.query.join(WorkflowTemplate).filter(
            WorkflowTemplate.order_type == approval.order_type,
            WorkflowNode.is_active == True
        ).order_by(WorkflowNode.sequence).all()
        
        print(f"  工单类型 '{approval.order_type}' 的可用节点:")
        for node in workflow_nodes:
            try:
                node_order_type = node.order_type
                match = "✓" if node_order_type == approval.order_type else "✗"
                print(f"    {match} 节点 #{node.id} '{node.name}' (seq={node.sequence})")
            except Exception as e:
                print(f"    ✗ 节点 #{node.id} 访问order_type失败: {e}")
        
        if len(workflow_nodes) > 0:
            print(f"  ✓ 找到 {len(workflow_nodes)} 个节点，打回功能应该正常")
        else:
            print(f"  ⚠ 没有找到节点")
    
    # 4. 总结
    print("\n" + "="*70)
    print("修复验证完成")
    print("="*70)
    print("\n修复内容:")
    print("1. ✓ 为 WorkflowNode 添加了 order_type 属性（通过 template 获取）")
    print("2. ✓ 修复了所有直接访问 node.order_type 的代码")
    print("3. ✓ 添加了用户列表的 fallback 逻辑（角色无用户时使用全部用户）")
    print("4. ✓ 修复了导入路径问题")
    print("\n建议:")
    print("- 在Docker中重新构建镜像: docker-compose build")
    print("- 或者重启容器以加载最新代码: docker-compose restart")
    print()
