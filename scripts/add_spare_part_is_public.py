"""
为SparePart表添加is_public字段
支持配件公开到仓库功能
"""
import sqlite3
import os

# 获取数据库路径
db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'app.db')

try:
    # 连接数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 检查列是否已存在
    cursor.execute("PRAGMA table_info(spare_part)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'is_public' in columns:
        print("ℹ is_public字段已存在,无需重复添加")
    else:
        # 添加is_public列
        cursor.execute('ALTER TABLE spare_part ADD COLUMN is_public BOOLEAN DEFAULT 0')
        conn.commit()
        print("✓ 成功为spare_part表添加is_public字段")
        print("✓ 配件现在可以设置为公开,供其他部门查看和申请")
    
    conn.close()
except Exception as e:
    print(f"✗ 添加字段失败: {str(e)}")
    if 'conn' in locals():
        conn.close()
