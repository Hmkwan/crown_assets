"""简化版测试数据创建"""
import sys
sys.path.insert(0, '.')

from app import create_app, db
from app.models import (User, SparePart, SparePartType)
from datetime import datetime, timedelta

app = create_app()

with app.app_context():
    print("创建测试数据...")
    
    # 检查配件
    if SparePart.query.count() == 0:
        # 创建配件类型
        pt = SparePartType.query.filter_by(name='电脑配件').first()
        if not pt:
            pt = SparePartType(name='电脑配件', description='电脑相关配件')
            db.session.add(pt)
            db.session.flush()
        
        # 创建配件
        parts = [
            SparePart(name='内存条', part_number='MEM001', type_id=pt.id, price=299, stock_quantity=50, department='企管部', is_public=True),
            SparePart(name='硬盘', part_number='HDD001', type_id=pt.id, price=399, stock_quantity=30, department='企管部', is_public=True),
        ]
        for p in parts:
            db.session.add(p)
        
        db.session.commit()
        print("已创建配件数据")
    
    print("\n现在可以在Web界面手动创建测试工单")
    print("访问系统后台创建:")
    print("  - 配件申请")
    print("  - 设备申请")
    print("  - 设备借用")
    print("  - 设备调拨")
    print("  - 设备报废")
