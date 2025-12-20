"""
检查设备的is_public_pool状态
"""
import sqlite3
import os

db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'app.db')

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("=== 设备列表及公开状态 ===\n")
    
    cursor.execute("""
        SELECT id, name, brand, model, serial_number, department, status, is_public_pool
        FROM equipment
        ORDER BY id
    """)
    
    equipments = cursor.fetchall()
    
    print(f"总设备数: {len(equipments)}\n")
    
    public_count = 0
    private_count = 0
    
    for eq in equipments:
        eq_id, name, brand, model, serial_number, dept, status, is_public_pool = eq
        public_status = "✓ 公开" if is_public_pool else "✗ 私有"
        if is_public_pool:
            public_count += 1
        else:
            private_count += 1
        
        print(f"[ID:{eq_id}] {name} {brand} {model}")
        print(f"  序列号: {serial_number}")
        print(f"  部门: {dept}")
        print(f"  状态: {status}")
        print(f"  公开: {public_status}")
        print()
    
    print(f"统计: 公开 {public_count} 个, 私有 {private_count} 个")
    
    conn.close()
    
except Exception as e:
    print(f"✗ 错误: {str(e)}")
    if 'conn' in locals():
        conn.close()
