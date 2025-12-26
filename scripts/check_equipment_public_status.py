#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import Equipment, Department

def check_equipment_status():
    app = create_app()
    
    with app.app_context():
        equipments = Equipment.query.all()
        
        print(f"\n{'='*80}")
        print(f"{'设备公开状态检查':^70}")
        print(f"{'='*80}\n")
        
        print(f"{'ID':<5} {'设备名称':<20} {'品牌':<15} {'型号':<15} {'部门':<15} {'状态':<10} {'公开':<10}")
        print(f"{'-'*80}")
        
        public_count = 0
        private_count = 0
        
        for eq in equipments:
            # department may be a string or a relationship object
            if eq.department:
                dept_name = eq.department if isinstance(eq.department, str) else getattr(eq.department, 'name', '无')
            else:
                dept_name = '无'
            is_public_str = "是" if eq.is_public_pool else "否"
            
            if eq.is_public_pool:
                public_count += 1
            else:
                private_count += 1
            
            print(f"{eq.id:<5} {eq.name[:18]:<20} {eq.brand[:13]:<15} {eq.model[:13]:<15} {dept_name[:13]:<15} {eq.status:<10} {is_public_str:<10}")
        
        print(f"\n{'-'*80}")
        print(f"总计: {len(equipments)} 台设备")
        print(f"公开设备: {public_count} 台")
        print(f"私有设备: {private_count} 台")
        print(f"{'='*80}\n")

if __name__ == '__main__':
    check_equipment_status()
