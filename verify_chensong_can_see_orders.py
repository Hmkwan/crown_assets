"""验证陈松能否看到分配给他的工单"""
import sys
sys.path.insert(0, '.')

from app import create_app, db
from app.models import User, RepairOrder, ApprovalWorkflow
from sqlalchemy import or_

app = create_app()

with app.app_context():
    print("="*70)
    print("验证陈松的工单可见性")
    print("="*70)
    
    # 查找陈松
    chensong = User.query.filter_by(username='陈松').first()
    if not chensong:
        print("✗ 找不到用户陈松")
        sys.exit(1)
    
    print(f"\n用户信息:")
    print(f"  - ID: {chensong.id}")
    print(f"  - 用户名: {chensong.username}")
    print(f"  - 部门: {chensong.department}")
    
    # 查找陈松需要审批的工单
    pending_approvals = ApprovalWorkflow.query.filter_by(
        approver_id=chensong.id,
        status='pending'
    ).all()
    
    pending_ids = [a.order_id for a in pending_approvals if a.order_type == 'repair_order']
    
    print(f"\n陈松待审批的工单ID: {pending_ids}")
    print(f"共 {len(pending_ids)} 个")
    
    # 模拟repair_orders路由的查询逻辑
    query = RepairOrder.query.filter(
        or_(
            RepairOrder.requester_id == chensong.id,
            RepairOrder.id.in_(pending_ids) if pending_ids else False
        )
    ).order_by(RepairOrder.created_date.desc())
    
    orders = query.all()
    
    print(f"\n陈松在repair_orders页面能看到的工单:")
    print(f"共 {len(orders)} 个工单")
    
    for order in orders:
        print(f"\n工单 #{order.id}:")
        print(f"  - 设备: {order.equipment.name if order.equipment else 'N/A'}")
        print(f"  - 申请人: {order.requester.username}")
        print(f"  - 状态: {order.status}")
        print(f"  - 原因: {'我申请的' if order.requester_id == chensong.id else '待我审批'}")
        
        # 查看这个工单的审批记录
        approvals = ApprovalWorkflow.query.filter_by(
            order_id=order.id,
            order_type='repair_order'
        ).all()
        
        print(f"  - 审批记录:")
        for a in approvals:
            approver_name = a.approver.username if a.approver else 'None'
            print(f"      #{a.id}: {a.status} - 审批人:{approver_name}")
    
    print(f"\n{'='*70}")
    if len(pending_ids) > 0 and len(orders) >= len(pending_ids):
        print("✓ 陈松可以看到需要他审批的工单")
    else:
        print("✗ 有问题: 陈松看不到所有需要审批的工单")
    print(f"{'='*70}")
