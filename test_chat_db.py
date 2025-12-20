#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
聊天系统数据库直连测试
直接查询PostgreSQL数据库验证聊天功能是否正常
"""
import psycopg2
from datetime import datetime

# PostgreSQL连接配置
DB_CONFIG = {
    'host': 'host.docker.internal',  # 或 'localhost'
    'port': 5432,
    'database': 'it_asset',
    'user': 'postgres',
    'password': 'difyai123456'
}

def test_database_connection():
    """测试数据库连接"""
    print("\n" + "="*100)
    print("[测试1] 连接PostgreSQL数据库")
    print("="*100)
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        print("✓ 数据库连接成功")
        return conn
    except Exception as e:
        print(f"✗ 数据库连接失败: {e}")
        return None

def check_chat_tables(conn):
    """检查聊天表是否存在"""
    print("\n" + "="*100)
    print("[测试2] 检查聊天表结构")
    print("="*100)
    
    cursor = conn.cursor()
    
    # 查询聊天相关的表
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name LIKE 'chat%'
        ORDER BY table_name
    """)
    
    tables = cursor.fetchall()
    
    if tables:
        print(f"✓ 找到 {len(tables)} 个聊天表:")
        for (table_name,) in tables:
            print(f"  - {table_name}")
            
            # 获取表的列信息
            cursor.execute(f"""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = '{table_name}'
                ORDER BY ordinal_position
                LIMIT 10
            """)
            columns = cursor.fetchall()
            for col_name, col_type in columns:
                print(f"      {col_name} ({col_type})")
        
        return True
    else:
        print("✗ 未找到聊天表")
        return False

def check_users(conn):
    """检查用户数据"""
    print("\n" + "="*100)
    print("[测试3] 检查用户数据")
    print("="*100)
    
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, username, real_name, department 
        FROM app_user 
        ORDER BY id 
        LIMIT 10
    """)
    
    users = cursor.fetchall()
    
    if users:
        print(f"✓ 找到 {len(users)} 个用户:")
        for user_id, username, real_name, dept in users:
            print(f"  - ID:{user_id} {real_name or username}({username}) [{dept or '无'}]")
        return users
    else:
        print("✗ 未找到用户")
        return []

def check_conversations(conn):
    """检查会话数据"""
    print("\n" + "="*100)
    print("[测试4] 检查会话数据")
    print("="*100)
    
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, type, name, created_date 
        FROM chat_conversation 
        ORDER BY created_date DESC 
        LIMIT 10
    """)
    
    convs = cursor.fetchall()
    
    if convs:
        print(f"✓ 找到 {len(convs)} 个会话:")
        for conv_id, conv_type, name, created_date in convs:
            print(f"  - 会话#{conv_id}: {name or '(未命名)'} | {conv_type} | {created_date}")
            
            # 查询参与者
            cursor.execute("""
                SELECT u.real_name, u.username 
                FROM chat_participant p
                JOIN app_user u ON p.user_id = u.id
                WHERE p.conversation_id = %s
            """, (conv_id,))
            
            participants = cursor.fetchall()
            if participants:
                parts = [f"{real_name or username}({username})" for real_name, username in participants]
                print(f"    参与者: {' ↔️ '.join(parts)}")
        
        return convs
    else:
        print("✗ 未找到会话")
        return []

def check_messages(conn, conversation_id=None):
    """检查消息数据"""
    print("\n" + "="*100)
    if conversation_id:
        print(f"[测试5] 检查会话#{conversation_id}的消息")
    else:
        print("[测试5] 检查所有消息")
    print("="*100)
    
    cursor = conn.cursor()
    
    if conversation_id:
        cursor.execute("""
            SELECT m.id, m.conversation_id, m.content, m.created_date,
                   u.real_name, u.username
            FROM chat_message m
            JOIN app_user u ON m.sender_id = u.id
            WHERE m.conversation_id = %s
            ORDER BY m.created_date ASC
        """, (conversation_id,))
    else:
        cursor.execute("""
            SELECT m.id, m.conversation_id, m.content, m.created_date,
                   u.real_name, u.username
            FROM chat_message m
            JOIN app_user u ON m.sender_id = u.id
            ORDER BY m.created_date DESC
            LIMIT 20
        """)
    
    msgs = cursor.fetchall()
    
    if msgs:
        print(f"✓ 找到 {len(msgs)} 条消息:")
        for msg_id, conv_id, content, created_date, real_name, username in msgs:
            sender = real_name or username
            content_preview = content[:50] if content else "(空)"
            print(f"  [{created_date}] {sender}: {content_preview}")
        return msgs
    else:
        print("✗ 未找到消息")
        return []

def create_test_conversation(conn, user1_id, user2_id):
    """创建测试会话"""
    print("\n" + "="*100)
    print(f"[测试6] 创建测试会话 (用户{user1_id} ↔️ 用户{user2_id})")
    print("="*100)
    
    cursor = conn.cursor()
    
    try:
        # 创建会话
        cursor.execute("""
            INSERT INTO chat_conversation (type, created_by, created_date)
            VALUES ('direct', %s, %s)
            RETURNING id
        """, (user1_id, datetime.now()))
        
        conv_id = cursor.fetchone()[0]
        print(f"✓ 会话创建成功: 会话#{conv_id}")
        
        # 添加参与者
        cursor.execute("""
            INSERT INTO chat_participant (conversation_id, user_id, joined_date)
            VALUES (%s, %s, %s), (%s, %s, %s)
        """, (
            conv_id, user1_id, datetime.now(),
            conv_id, user2_id, datetime.now()
        ))
        
        conn.commit()
        print(f"✓ 参与者添加成功")
        
        return conv_id
    except Exception as e:
        conn.rollback()
        print(f"✗ 创建失败: {e}")
        return None

def send_test_message(conn, conversation_id, sender_id, content):
    """发送测试消息"""
    print("\n" + "="*100)
    print(f"[测试7] 发送测试消息")
    print("="*100)
    print(f"会话ID: {conversation_id}")
    print(f"发送者ID: {sender_id}")
    print(f"内容: {content}")
    
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO chat_message (conversation_id, sender_id, content, message_type, created_date)
            VALUES (%s, %s, %s, 'text', %s)
            RETURNING id
        """, (conversation_id, sender_id, content, datetime.now()))
        
        msg_id = cursor.fetchone()[0]
        
        # 更新会话的last_message
        cursor.execute("""
            UPDATE chat_conversation
            SET last_message_id = %s, last_message_time = %s
            WHERE id = %s
        """, (msg_id, datetime.now(), conversation_id))
        
        conn.commit()
        
        print(f"✓ 消息发送成功: 消息#{msg_id}")
        return msg_id
    except Exception as e:
        conn.rollback()
        print(f"✗ 发送失败: {e}")
        return None

def main():
    print("\n" + "█"*100)
    print("█" + " "*98 + "█")
    print("█" + "聊天系统数据库测试 (PostgreSQL直连)".center(96) + "█")
    print("█" + " "*98 + "█")
    print("█"*100)
    
    # 测试1: 连接数据库
    conn = test_database_connection()
    if not conn:
        return
    
    try:
        # 测试2: 检查表结构
        if not check_chat_tables(conn):
            print("\n❌ 测试终止: 聊天表不存在")
            return
        
        # 测试3: 检查用户
        users = check_users(conn)
        if len(users) < 2:
            print("\n❌ 测试终止: 用户数量不足(需要至少2个)")
            return
        
        # 测试4: 检查会话
        convs = check_conversations(conn)
        
        # 测试5: 检查消息
        if convs:
            # 检查第一个会话的消息
            check_messages(conn, convs[0][0])
        else:
            check_messages(conn)
        
        # 测试6-7: 创建测试会话和消息
        user1_id = users[0][0]  # admin
        user2_id = users[1][0] if len(users) > 1 else users[0][0]
        
        # conv_id = create_test_conversation(conn, user1_id, user2_id)
        # if conv_id:
        #     send_test_message(conn, conv_id, user1_id, f"[数据库测试] 这是一条测试消息 - {datetime.now()}")
        
        # 测试总结
        print("\n" + "█"*100)
        print("█" + " "*98 + "█")
        print("█" + "测试完成!".center(96) + "█")
        print("█" + " "*98 + "█")
        print("█"*100)
        
        print("\n数据库状态:")
        print(f"  ✓ 聊天表: 正常")
        print(f"  ✓ 用户数: {len(users)}")
        print(f"  ✓ 会话数: {len(convs)}")
        
    finally:
        conn.close()
        print("\n✓ 数据库连接已关闭")

if __name__ == '__main__':
    main()
