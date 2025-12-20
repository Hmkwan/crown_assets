"""为工单#10设置测试维修费用"""
import sys
sys.path.insert(0, '.')

from app import create_app, db
from app.models import RepairOrder

app = create_app()

with app.app_context():
    order = RepairOrder.query.get(10)
    if order:
        print(f"工单 #{order.id} 当前维修费用: ¥{order.repair_cost if order.repair_cost else 0:.2f}")
        
        # 设置测试费用
        order.repair_cost = 1588.50
        db.session.commit()
        
        print(f"已设置测试维修费用: ¥{order.repair_cost:.2f}")
        print("\n现在可以测试:")
        print("1. 在审批列表中应该显示 ¥1588.50")
        print("2. '确定维修金额'节点的审批人点击批准时,应该看到绿色提示框显示已评估金额")
    else:
        print("工单#10不存在")
