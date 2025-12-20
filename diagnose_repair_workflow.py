"""检查维修工单审批流程配置"""
import sys
sys.path.insert(0, '.')

from app import create_app, db
from app.approval_models import WorkflowNode, WorkflowTemplate
from app.models import User, ApprovalWorkflow, RepairOrder
from app.approval_roles import ApprovalRole, UserApprovalRole

app = create_app()

with app.app_context():
    print("="*70)
    print("维修工单审批流程诊断")
    print("="*70)
    
    # 1. 检查维修工单的流程模板
    print("\n[1] 检查 repair_order 流程模板")
    print("-"*70)
    
    templates = WorkflowTemplate.query.filter_by(
        order_type='repair_order',
        is_active=True
    ).all()
    
    if templates:
        for template in templates:
            print(f"✓ 找到模板: {template.name} (ID={template.id}, 版本={template.version})")
            print(f"  - 是否默认: {template.is_default}")
            print(f"  - 是否启用: {template.is_active}")
    else:
        print("✗ 没有找到 repair_order 的流程模板！")
    
    # 2. 检查审批节点
    print("\n[2] 检查审批节点")
    print("-"*70)
    
    nodes = WorkflowNode.query.join(WorkflowTemplate).filter(
        WorkflowTemplate.order_type == 'repair_order',
        WorkflowNode.is_active == True
    ).order_by(WorkflowNode.sequence).all()
    
    if nodes:
        print(f"找到 {len(nodes)} 个审批节点:")
        for node in nodes:
            print(f"\n  节点 #{node.id}: {node.name} (序号={node.sequence})")
            print(f"    - Code: {node.code}")
            print(f"    - 节点类型: {node.node_type}")
            
            # 检查审批角色
            if node.approval_role_id:
                role = ApprovalRole.query.get(node.approval_role_id)
                if role:
                    print(f"    - 审批角色: {role.name} (ID={role.id})")
                    
                    # 检查该角色的用户
                    assignments = UserApprovalRole.query.filter_by(
                        role_id=role.id,
                        is_active=True
                    ).all()
                    
                    print(f"    - 分配的用户数: {len(assignments)}")
                    for assign in assignments:
                        if assign.user:
                            print(f"      * {assign.user.username} (部门: {assign.user.department or '无'})")
                else:
                    print(f"    - ⚠ 审批角色ID {node.approval_role_id} 不存在")
            else:
                print(f"    - ⚠ 未设置审批角色")
            
            # 检查旧的 role_required (兼容性)
            role_req = node.role_required
            if role_req:
                print(f"    - role_required (兼容): {role_req}")
    else:
        print("✗ 没有找到任何审批节点！")
    
    # 3. 检查部门负责人
    print("\n[3] 检查部门负责人配置")
    print("-"*70)
    
    dept_heads = User.query.filter_by(role='department_head', is_active=True).all()
    if dept_heads:
        print(f"找到 {len(dept_heads)} 个部门负责人:")
        for user in dept_heads:
            print(f"  - {user.username} (部门: {user.department or '未设置'})")
    else:
        print("⚠ 没有找到部门负责人用户")
    
    # 4. 检查现有维修工单的审批记录
    print("\n[4] 检查最近的维修工单审批记录")
    print("-"*70)
    
    recent_orders = RepairOrder.query.order_by(RepairOrder.id.desc()).limit(3).all()
    
    if recent_orders:
        for order in recent_orders:
            print(f"\n维修工单 #{order.id}:")
            print(f"  - 申请人: {order.requester.username if order.requester else '未知'}")
            print(f"  - 部门: {order.requester.department if order.requester else '未知'}")
            print(f"  - 状态: {order.status}")
            
            approvals = ApprovalWorkflow.query.filter_by(
                order_type='repair_order',
                order_id=order.id
            ).order_by(ApprovalWorkflow.created_date).all()
            
            if approvals:
                print(f"  - 审批记录数: {len(approvals)}")
                for approval in approvals:
                    approver_name = approval.approver.username if approval.approver else '未分配'
                    node_name = approval.workflow_node.name if approval.workflow_node else '未知节点'
                    print(f"    * 节点: {node_name}")
                    print(f"      审批人: {approver_name} ({approval.status})")
            else:
                print(f"  - ⚠ 没有审批记录！")
    else:
        print("没有找到维修工单")
    
    # 5. 诊断建议
    print("\n" + "="*70)
    print("诊断结果与建议")
    print("="*70)
    
    issues = []
    
    if not templates:
        issues.append("❌ 缺少 repair_order 流程模板")
    
    if not nodes:
        issues.append("❌ 没有配置审批节点")
    else:
        for node in nodes:
            if not node.approval_role_id:
                issues.append(f"⚠ 节点 '{node.name}' 未设置审批角色")
            else:
                role = ApprovalRole.query.get(node.approval_role_id)
                if role:
                    assignments = UserApprovalRole.query.filter_by(
                        role_id=role.id,
                        is_active=True
                    ).count()
                    if assignments == 0:
                        issues.append(f"⚠ 角色 '{role.name}' (节点: {node.name}) 没有分配用户")
    
    if issues:
        print("\n发现以下问题:")
        for issue in issues:
            print(f"  {issue}")
        
        print("\n建议操作:")
        if not templates:
            print("  1. 运行初始化脚本创建默认流程模板")
            print("     python scripts/init_workflow_templates.py")
        
        if not nodes or any("未设置审批角色" in i for i in issues):
            print("  2. 配置审批节点的审批角色")
            print("     访问: 管理员 → 流程模板管理")
        
        if any("没有分配用户" in i for i in issues):
            print("  3. 为审批角色分配用户")
            print("     访问: 管理员 → 审批角色管理 → 分配用户")
    else:
        print("\n✓ 审批流程配置正常")
    
    print()
