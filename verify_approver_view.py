"""验证陈松用户能否看到待审批的维修工单"""
import sys
sys.path.insert(0, '.')

from app import create_app, db
from app.models import User, RepairOrder, ApprovalWorkflow
from sqlalchemy import or_

app = create_app()

with app.app_context():
    print("="*70)
    print("验证审批人查看工单权限")
    print("="*70)
    
    # 查找陈松用户
    chen_song = User.query.filter_by(username='陈松').first()
    
    if not chen_song:
        print("未找到陈松用户")
        sys.exit(1)
    
    print(f"\n用户信息:")
    print(f"  - 用户名: {chen_song.username}")
    print(f"  - 角色: {chen_song.role}")
    print(f"  - 部门: {chen_song.department}")
    
    # 1. 检查待审批的工单
    print(f"\n[1] 陈松的待审批工单")
    print("-"*70)
    
    pending_approvals = ApprovalWorkflow.query.filter_by(
        order_type='repair_order',
        approver_id=chen_song.id,
        status='pending'
    ).all()
    
    print(f"找到 {len(pending_approvals)} 个待审批记录:")
    for approval in pending_approvals:
        order = RepairOrder.query.get(approval.order_id)
        if order:
            print(f"  - 工单 #{order.id}")
            print(f"    申请人: {order.requester.username if order.requester else '未知'}")
            print(f"    状态: {order.status}")
            print(f"    审批节点: {approval.workflow_node.name if approval.workflow_node else '未知'}")
    
    # 2. 使用旧的查询逻辑（修复前）
    print(f"\n[2] 旧逻辑能看到的工单（只有自己创建的）")
    print("-"*70)
    
    old_query = RepairOrder.query.filter_by(requester_id=chen_song.id)
    old_orders = old_query.all()
    
    print(f"能看到 {len(old_orders)} 个工单")
    for order in old_orders:
        print(f"  - 工单 #{order.id} (状态: {order.status})")
    
    # 3. 使用新的查询逻辑（修复后）
    print(f"\n[3] 新逻辑能看到的工单（自己创建的 + 待审批的）")
    print("-"*70)
    
    # 获取需要审批的工单ID
    pending_approval_order_ids = db.session.query(ApprovalWorkflow.order_id).filter(
        ApprovalWorkflow.order_type == 'repair_order',
        ApprovalWorkflow.approver_id == chen_song.id,
        ApprovalWorkflow.status == 'pending'
    ).distinct().all()
    pending_ids = [oid[0] for oid in pending_approval_order_ids]
    
    # 新查询
    new_query = RepairOrder.query.filter(
        or_(
            RepairOrder.requester_id == chen_song.id,
            RepairOrder.id.in_(pending_ids) if pending_ids else False
        )
    )
    new_orders = new_query.all()
    
    print(f"能看到 {len(new_orders)} 个工单:")
    for order in new_orders:
        is_creator = order.requester_id == chen_song.id
        is_approver = order.id in pending_ids
        tag = ""
        if is_creator and is_approver:
            tag = "[创建+审批]"
        elif is_creator:
            tag = "[创建]"
        elif is_approver:
            tag = "[待审批]"
        
        print(f"  - 工单 #{order.id} {tag} (状态: {order.status})")
        if is_approver:
            approval = ApprovalWorkflow.query.filter_by(
                order_type='repair_order',
                order_id=order.id,
                approver_id=chen_song.id,
                status='pending'
            ).first()
            if approval and approval.workflow_node:
                print(f"    → 节点: {approval.workflow_node.name}")
    
    # 4. 对比
    print(f"\n[4] 对比结果")
    print("-"*70)
    print(f"修复前能看到: {len(old_orders)} 个工单")
    print(f"修复后能看到: {len(new_orders)} 个工单")
    print(f"新增可见: {len(new_orders) - len(old_orders)} 个工单")
    
    if len(new_orders) > len(old_orders):
        print(f"\n修复成功！陈松现在可以看到待审批的工单了")
    else:
        print(f"\n陈松目前没有待审批的工单")
