#!/usr/bin/env python3
"""查询设备信息"""

from app import create_app
from app.models import Equipment

app = create_app()
with app.app_context():
    equipment = Equipment.query.first()
    if equipment:
        print(f"设备ID: {equipment.id}")
        print(f"设备名称: {equipment.name}")
        print(f"设备编号: {equipment.asset_number}")
    else:
        print("数据库中没有设备")
