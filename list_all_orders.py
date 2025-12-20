"""查看所有工单"""
import sys
sys.path.insert(0, '.')

from app import create_app
from app.models import RepairOrder

app = create_app()

with app.app_context():
    orders = RepairOrder.query.all()
    print(f"共 {len(orders)} 个工单:")
    for o in orders:
        print(f"  #{o.id}: {o.equipment.name if o.equipment else 'N/A'} - {o.requester.username} - {o.status}")
