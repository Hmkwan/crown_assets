"""检查维修工单数据"""
import sys
sys.path.insert(0, '.')

from app import create_app
from app.models import RepairOrder

app = create_app()

with app.app_context():
    orders = RepairOrder.query.order_by(RepairOrder.id.desc()).limit(3).all()
    
    print("最近3个工单:")
    for order in orders:
        print(f"\n工单 #{order.id}:")
        print(f"  设备: {order.equipment.name if order.equipment else 'N/A'}")
        print(f"  申请人: {order.requester.username}")
        print(f"  部门: {order.requester.department}")
        print(f"  故障描述: {order.description[:50]}")
        print(f"  状态: {order.status}")
        print(f"  状态(中文):", end=" ")
        if order.status == 'submitted':
            print("已提交")
        elif order.status == 'department_head_approved':
            print("部门领导已批准")
        elif order.status == 'admin_approved':
            print("管理员已批准")
        elif order.status == 'in_progress':
            print("处理中")
        elif order.status == 'completed':
            print("已完成")
        elif order.status == 'approved':
            print("已批准")
        else:
            print(order.status)
