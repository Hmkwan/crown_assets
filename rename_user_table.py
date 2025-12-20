#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
重命名PostgreSQL中的user表为app_user
避免保留关键字冲突
"""
from app import create_app
import psycopg2

app = create_app()

with app.app_context():
    db_url = app.config['SQLALCHEMY_DATABASE_URI']
    print(f"数据库: {db_url.split('@')[1]}")
    
    # 解析连接信息
    # postgresql://postgres:password@host:port/database
    parts = db_url.replace('postgresql://', '').split('@')
    user_pass = parts[0].split(':')
    host_port_db = parts[1].split('/')
    host_port = host_port_db[0].split(':')
    
    conn = psycopg2.connect(
        dbname=host_port_db[1],
        user=user_pass[0],
        password=user_pass[1],
        host=host_port[0],
        port=host_port[1] if len(host_port) > 1 else '5432'
    )
    conn.autocommit = True
    cur = conn.cursor()
    
    try:
        # 检查user表是否存在
        cur.execute("""
            SELECT tablename FROM pg_tables 
            WHERE tablename = 'user' AND schemaname = 'public'
        """)
        if cur.fetchone():
            print("\n重命名表: user -> app_user")
            cur.execute('ALTER TABLE "user" RENAME TO app_user')
            print("✅ 表重命名成功")
        else:
            print("\n⚠️ user表不存在,可能已经是app_user")
            
        # 检查app_user表
        cur.execute("""
            SELECT tablename FROM pg_tables 
            WHERE tablename = 'app_user' AND schemaname = 'public'
        """)
        if cur.fetchone():
            print("✅ app_user表已存在")
            
            # 获取记录数
            cur.execute("SELECT COUNT(*) FROM app_user")
            count = cur.fetchone()[0]
            print(f"   记录数: {count}")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cur.close()
        conn.close()
        
print("\n完成!")
