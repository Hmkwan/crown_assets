#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
重置 Docker 容器中的用户密码
将所有用户密码重置为默认密码 '123456'，使用 sha256 哈希方法
"""
import sqlite3
from werkzeug.security import generate_password_hash

def reset_passwords():
    # 连接数据库
    conn = sqlite3.connect('/app/app.db')
    cursor = conn.cursor()
    
    # 获取所有用户
    cursor.execute('SELECT id, username FROM user')
    users = cursor.fetchall()
    
    print(f"找到 {len(users)} 个用户，开始重置密码...")
    
    # 为所有用户重置密码为 '123456'，使用 sha256 方法
    default_password = '123456'
    new_hash = generate_password_hash(default_password, method='pbkdf2:sha256')
    
    print(f"新密码哈希: {new_hash[:50]}...")
    
    # 更新所有用户密码
    for user_id, username in users:
        cursor.execute('UPDATE user SET password_hash = ? WHERE id = ?', (new_hash, user_id))
        print(f"  ✓ 重置用户: {username}")
    
    # 提交更改
    conn.commit()
    conn.close()
    
    print("\n密码重置完成!")
    print("所有用户的新密码: 123456")
    print("哈希方法: pbkdf2:sha256")

if __name__ == '__main__':
    reset_passwords()
