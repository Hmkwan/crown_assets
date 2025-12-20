"""测试维修费用显示功能"""
import sys
sys.path.insert(0, '.')

from app import create_app, db
from app.models import RepairOrder
from app.approval_models import WorkflowNode

app = create_app()

with app.app_context():
    print("="*70)
    print("测试维修费用显示")
    print("="*70)
    
    # 查找所有工单
    orders = RepairOrder.query.all()
    
    print(f"\n当前系统中有 {len(orders)} 个维修工单:")
    for order in orders:
        print(f"\n工单 #{order.id}:")
        print(f"  设备: {order.equipment.name if order.equipment else 'N/A'}")
        print(f"  申请人: {order.requester.username}")
        print(f"  维修费用: ¥{order.repair_cost if order.repair_cost else 0:.2f}")
        print(f"  状态: {order.status}")
    
    # 查找审批节点
    print(f"\n{'='*70}")
    print("审批流程节点:")
    print(f"{'='*70}")
    
    nodes = WorkflowNode.query.filter_by(is_active=True).order_by(WorkflowNode.sequence).all()
    for node in nodes:
        print(f"\n{node.sequence}. {node.name}")
        print(f"   代码: {node.code}")
        if '管理员' in node.name and '评估' in node.name:
            print(f"   👉 此节点需要输入维修金额")
        if '确定' in node.name and '维修' in node.name:
            print(f"   👁 此节点需要查看已评估的维修金额")
    
    print(f"\n{'='*70}")
    print("✓ 测试完成")
    print(f"{'='*70}")
