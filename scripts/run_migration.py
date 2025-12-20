"""
执行数据库迁移脚本
"""
import sqlite3
import os

def run_migration():
    db_path = 'app.db'
    migration_file = 'migrations/002_add_workflow_engine_tables.sql'
    
    if not os.path.exists(db_path):
        print(f"错误: 数据库文件 {db_path} 不存在")
        return
    
    if not os.path.exists(migration_file):
        print(f"错误: 迁移文件 {migration_file} 不存在")
        return
    
    print(f"执行迁移脚本: {migration_file}")
    
    with open(migration_file, 'r', encoding='utf-8') as f:
        sql = f.read()
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 执行迁移脚本
        cursor.executescript(sql)
        conn.commit()
        print("✓ 迁移脚本执行成功")
        
        # 验证表已创建
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'workflow%'")
        tables = cursor.fetchall()
        print(f"\n创建的表: {', '.join([t[0] for t in tables])}")
        
    except Exception as e:
        print(f"✗ 迁移失败: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    run_migration()
