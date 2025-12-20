"""
通过Flask应用上下文检查数据库状态
"""
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 不要启动Flask应用,只导入模型
from app.models import db, SparePart, Equipment, Department

# 检查数据库文件
db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'app.db')
print(f"数据库路径: {db_path}")
print(f"数据库存在: {os.path.exists(db_path)}")

if os.path.exists(db_path):
    print(f"数据库大小: {os.path.getsize(db_path)} 字节")

# 使用原始SQL查看表
import sqlite3
try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    print(f"\n数据库中的表 ({len(tables)}个):")
    for table in tables:
        print(f"  - {table[0]}")
        # 获取表的行数
        cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
        count = cursor.fetchone()[0]
        print(f"    行数: {count}")
    
    conn.close()
except Exception as e:
    print(f"✗ 错误: {str(e)}")
