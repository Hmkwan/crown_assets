"""
设置一些配件为公开状态用于测试
"""
import sqlite3
import os

db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'app.db')

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 获取前3个配件
    cursor.execute("SELECT id, name, part_number FROM spare_part LIMIT 3")
    parts = cursor.fetchall()
    
    if not parts:
        print("没有找到配件数据")
    else:
        print("设置以下配件为公开:")
        for part in parts:
            cursor.execute("UPDATE spare_part SET is_public = 1 WHERE id = ?", (part[0],))
            print(f"  ✓ [ID:{part[0]}] {part[1]} (编号:{part[2]})")
        
        conn.commit()
        print("\n设置完成!")
    
    conn.close()
    
except Exception as e:
    print(f"✗ 操作失败: {str(e)}")
    if 'conn' in locals():
        conn.close()
