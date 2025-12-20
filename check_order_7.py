"""检查工单#7"""
import sys
sys.path.insert(0, '.')

from app import create_app, db
from app.models import RepairOrder, ApprovalWorkflow

app = create_app()

with app.app_context():
    order = RepairOrder.query.get(7)
    
    if not order:
        print("工单#7不存在")
        sys.exit(1)
    
    print(f"工单 #{order.id}:")
    print(f"  设备: {order.equipment.name if order.equipment else 'N/A'}")
    print(f"  申请人: {order.requester.username}")
    print(f"  申请人ID: {order.requester_id}")
    print(f"  部门: {order.requester.department if order.requester else 'N/A'}")
    print(f"  状态: {order.status}")
    print(f"  是否删除: {order.is_deleted if hasattr(order, 'is_deleted') else 'N/A'}")
    
    print(f"\n审批记录:")
    approvals = ApprovalWorkflow.query.filter_by(
        order_id=7,
        order_type='repair_order'
    ).all()
    
    for a in approvals:
        approver_name = a.approver.username if a.approver else 'None'
        print(f"  #{a.id}: {a.status} - 审批人:{approver_name} (ID:{a.approver_id})")
