"""
添加Equipment表的location字段
直接使用SQLite命令
"""
import sqlite3
import os

db_path = 'app.db'

if not os.path.exists(db_path):
    print(f"❌ 数据库文件不存在: {db_path}")
    exit(1)

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 检查列是否已存在
    cursor.execute("PRAGMA table_info(equipment)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'location' not in columns:
        # 添加location列
        cursor.execute("ALTER TABLE equipment ADD COLUMN location VARCHAR(120)")
        conn.commit()
        print("✅ 成功添加equipment.location字段")
    else:
        print("ℹ️  equipment.location字段已存在,无需添加")
    
    conn.close()
    
except Exception as e:
    print(f"❌ 操作失败: {str(e)}")
    if conn:
        conn.close()
    raise
