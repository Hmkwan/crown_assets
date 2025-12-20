#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
重置PostgreSQL中admin用户的密码为pbkdf2格式(Docker兼容)
"""
from werkzeug.security import generate_password_hash
import psycopg2
import os

# 数据库连接
DB_URL = os.environ.get('DATABASE_URL', 'postgresql://postgres:difyai123456@localhost:5432/it_asset')

# 解析连接信息
parts = DB_URL.replace('postgresql://', '').split('@')
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
    # 生成新的密码哈希(使用默认pbkdf2方法,兼容性好)
    new_password = 'admin123'
    password_hash = generate_password_hash(new_password, method='pbkdf2:sha256')
    
    print(f"新密码哈希: {password_hash[:50]}...")
    print(f"哈希长度: {len(password_hash)}")
    
    # 更新admin用户密码
    cur.execute("""
        UPDATE app_user 
        SET password_hash = %s 
        WHERE username = 'admin'
    """, (password_hash,))
    
    print("\n✅ admin密码已重置为: admin123")
    print("   使用pbkdf2:sha256方法(Docker兼容)")
    
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
finally:
    cur.close()
    conn.close()
