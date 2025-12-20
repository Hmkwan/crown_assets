"""修复未分配审批人的待审批工单"""
import sys
sys.path.insert(0, '.')

from app import create_app, db
from app.models import ApprovalWorkflow, RepairOrder, User
from app.approval_models import WorkflowNode

app = create_app()

with app.app_context():
    print("="*70)
    print("修复未分配审批人的待审批工单")
    print("="*70)
    
    # 查找所有pending状态但没有审批人的审批记录
    unassigned_approvals = ApprovalWorkflow.query.filter_by(
        status='pending',
        approver_id=None
    ).all()
    
    print(f"\n找到 {len(unassigned_approvals)} 个未分配审批人的审批记录:")
    
    if not unassigned_approvals:
        print("所有审批记录都已分配审批人")
        sys.exit(0)
    
    # 导入get_approver_id函数
    from app.main.routes import get_approver_id
    
    fixed_count = 0
    failed_count = 0
    
    for approval in unassigned_approvals:
        print(f"\n审批记录 #{approval.id}:")
        print(f"  - 工单类型: {approval.order_type}")
        print(f"  - 工单ID: {approval.order_id}")
        print(f"  - 节点ID: {approval.node_id}")
        
        # 获取工单信息以确定部门
        department = None
        if approval.order_type == 'repair_order':
            order = RepairOrder.query.get(approval.order_id)
            if order and order.requester:
                department = order.requester.department
                print(f"  - 申请人部门: {department}")
        
        # 获取节点
        node = WorkflowNode.query.get(approval.node_id) if approval.node_id else None
        
        if node:
            print(f"  - 节点: {node.name}")
            
            # 获取审批人ID
            approver_id = get_approver_id(node, department)
            
            if approver_id:
                approver = User.query.get(approver_id)
                if approver:
                    approval.approver_id = approver_id
                    print(f"  ✓ 分配审批人: {approver.username} ({approver.department})")
                    fixed_count += 1
                else:
                    print(f"  ✗ 审批人ID {approver_id} 不存在")
                    failed_count += 1
            else:
                print(f"  ✗ 无法确定审批人")
                failed_count += 1
        else:
            print(f"  ✗ 节点不存在")
            failed_count += 1
    
    if fixed_count > 0:
        try:
            db.session.commit()
            print(f"\n{'='*70}")
            print(f"✓ 成功修复 {fixed_count} 个审批记录")
            if failed_count > 0:
                print(f"⚠ {failed_count} 个记录无法修复")
            print(f"{'='*70}")
            
            print(f"\n修复后的审批记录:")
            for approval in unassigned_approvals:
                if approval.approver:
                    print(f"  - 审批 #{approval.id}: {approval.approver.username}")
        except Exception as e:
            db.session.rollback()
            print(f"\n✗ 提交失败: {e}")
    else:
        print(f"\n没有可修复的记录")
