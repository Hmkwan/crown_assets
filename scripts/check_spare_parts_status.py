"""
检查配件的is_public状态
"""
import sqlite3
import os

db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app.db')

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("=== 配件列表及公开状态 ===\n")
    
    cursor.execute("""
        SELECT id, name, part_number, department, department_id, is_public
        FROM spare_part
        ORDER BY id
    """)
    
    parts = cursor.fetchall()
    
    print(f"总配件数: {len(parts)}\n")
    
    public_count = 0
    private_count = 0
    
    for part in parts:
        part_id, name, part_number, dept_name, dept_id, is_public = part
        status = "✓ 公开" if is_public else "✗ 私有"
        if is_public:
            public_count += 1
        else:
            private_count += 1
        
        print(f"[ID:{part_id}] {name} (编号:{part_number})")
        print(f"  部门: {dept_name or '未设置'} (ID:{dept_id})")
        print(f"  状态: {status}")
        print()
    
    print(f"统计: 公开 {public_count} 个, 私有 {private_count} 个")
    
    conn.close()
    
except Exception as e:
    print(f"✗ 错误: {str(e)}")
    if 'conn' in locals():
        conn.close()
