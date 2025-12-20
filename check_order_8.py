"""检查工单#8的详细状态"""
import sys
sys.path.insert(0, '.')

from app import create_app, db
from app.models import User, RepairOrder, ApprovalWorkflow

app = create_app()

with app.app_context():
    print("="*70)
    print("检查工单#8的详细状态")
    print("="*70)
    
    order = RepairOrder.query.get(8)
    
    if not order:
        print("未找到工单#8")
        sys.exit(1)
    
    print(f"\n工单基本信息:")
    print(f"  - ID: {order.id}")
    print(f"  - 申请人: {order.requester.username if order.requester else '未知'}")
    print(f"  - 部门: {order.requester.department if order.requester else '未知'}")
    print(f"  - 状态: {order.status}")
    print(f"  - 描述: {order.description}")
    
    print(f"\n审批记录:")
    approvals = ApprovalWorkflow.query.filter_by(
        order_type='repair_order',
        order_id=8
    ).order_by(ApprovalWorkflow.created_date).all()
    
    print(f"  共 {len(approvals)} 条审批记录:")
    for i, approval in enumerate(approvals, 1):
        print(f"\n  [{i}] 审批记录 #{approval.id}")
        print(f"      节点: {approval.workflow_node.name if approval.workflow_node else '未知'}")
        print(f"      审批人ID: {approval.approver_id}")
        if approval.approver:
            print(f"      审批人: {approval.approver.username} ({approval.approver.department})")
        else:
            print(f"      审批人: 未分配")
        print(f"      状态: {approval.status}")
        print(f"      创建时间: {approval.created_date}")
        if approval.approved_date:
            print(f"      审批时间: {approval.approved_date}")
    
    # 查找陈松
    chen_song = User.query.filter_by(username='陈松').first()
    if chen_song:
        print(f"\n陈松用户信息:")
        print(f"  - ID: {chen_song.id}")
        print(f"  - 部门: {chen_song.department}")
        
        # 检查是否有分配给陈松的审批
        chen_approvals = [a for a in approvals if a.approver_id == chen_song.id]
        if chen_approvals:
            print(f"\n  陈松有 {len(chen_approvals)} 个审批记录:")
            for a in chen_approvals:
                print(f"    - 状态: {a.status}")
        else:
            print(f"\n  陈松没有此工单的审批记录")
            
            # 检查是否应该分配给陈松
            if order.requester and order.requester.department == '企管部':
                print(f"  → 工单来自企管部，但未分配给陈松")
                print(f"  → 可能原因: get_approver_id 选择了同部门的其他用户")
