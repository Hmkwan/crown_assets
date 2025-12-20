#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""管理员聊天记录查看工具 - 使用纯SQL查询"""
import sqlite3
import sys
from datetime import datetime

DB_PATH = 'app.db'

def view_conversation_messages(conv_id=None):
    """查看会话消息(含用户名)"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print("\n" + "="*120)
    print("聊天消息详情(含用户信息)")
    print("="*120)
    
    # SQL查询:关联用户表获取用户名
    if conv_id:
        sql = """
        SELECT 
            m.id as msg_id,
            m.conversation_id,
            m.sender_id,
            u.username,
            u.real_name,
            u.department,
            m.content,
            m.message_type,
            m.is_recalled,
            m.created_date,
            c.name as conv_name,
            c.type as conv_type
        FROM chat_message m
        LEFT JOIN app_user u ON m.sender_id = u.id
        LEFT JOIN chat_conversation c ON m.conversation_id = c.id
        WHERE m.conversation_id = ?
        ORDER BY m.created_date ASC
        """
        cursor.execute(sql, (conv_id,))
    else:
        sql = """
        SELECT 
            m.id as msg_id,
            m.conversation_id,
            m.sender_id,
            u.username,
            u.real_name,
            u.department,
            m.content,
            m.message_type,
            m.is_recalled,
            m.created_date,
            c.name as conv_name,
            c.type as conv_type
        FROM chat_message m
        LEFT JOIN app_user u ON m.sender_id = u.id
        LEFT JOIN chat_conversation c ON m.conversation_id = c.id
        ORDER BY m.conversation_id, m.created_date ASC
        """
        cursor.execute(sql)
    
    messages = cursor.fetchall()
    
    if not messages:
        print("没有找到消息")
        conn.close()
        return
    
    print(f"找到 {len(messages)} 条消息\n")
    
    current_conv = None
    for msg in messages:
        # 显示会话头
        if msg['conversation_id'] != current_conv:
            current_conv = msg['conversation_id']
            
            # 查询会话参与者
            cursor.execute("""
                SELECT u.username, u.real_name, u.department
                FROM chat_participant p
                LEFT JOIN app_user u ON p.user_id = u.id
                WHERE p.conversation_id = ?
            """, (current_conv,))
            participants = cursor.fetchall()
            
            print("\n" + "="*120)
            print(f"【会话 #{current_conv}】{msg['conv_name'] or '(未命名)'} | 类型:{msg['conv_type']}")
            parts = [f"{p['real_name'] or p['username']}({p['username']})" for p in participants]
            print(f"参与者: {' ↔️ '.join(parts)}")
            print("="*120)
        
        # 显示消息
        name = msg['real_name'] or msg['username'] or '未知用户'
        username = msg['username'] or 'N/A'
        dept = f"[{msg['department']}]" if msg['department'] else ""
        status = " [已撤回]" if msg['is_recalled'] else ""
        
        print(f"\n[{msg['created_date']}] {name}({username}){dept}{status}")
        print(f"  消息ID:{msg['msg_id']} | 类型:{msg['message_type']}")
        print(f"  内容: {msg['content'] or '(空消息)'}")
    
    conn.close()

def view_all_conversations():
    """查看所有会话"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print("\n" + "="*120)
    print("所有会话列表")
    print("="*120)
    
    cursor.execute("""
        SELECT id, name, type, created_date
        FROM chat_conversation
        ORDER BY created_date DESC
    """)
    
    convs = cursor.fetchall()
    
    for conv in convs:
        print(f"\n【会话#{conv['id']}】{conv['name'] or '(未命名)'} | {conv['type']}")
        print(f"  创建时间: {conv['created_date']}")
        print(f"  参与人员:")
        
        # 查询参与者
        cursor.execute("""
            SELECT u.username, u.real_name, u.department
            FROM chat_participant p
            LEFT JOIN app_user u ON p.user_id = u.id
            WHERE p.conversation_id = ?
        """, (conv['id'],))
        
        participants = cursor.fetchall()
        for p in participants:
            name = p['real_name'] or p['username']
            print(f"    - {name}({p['username']}) [{p['department'] or '无部门'}]")
        
        # 消息数量
        cursor.execute("SELECT COUNT(*) as cnt FROM chat_message WHERE conversation_id = ?", (conv['id'],))
        cnt = cursor.fetchone()['cnt']
        print(f"  消息数量: {cnt} 条")
        print("-"*120)
    
    conn.close()

def view_user_messages(username):
    """查看用户的所有消息"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print(f"\n查询用户: {username}")
    
    # 查找用户
    cursor.execute("""
        SELECT id, username, real_name, department
        FROM app_user
        WHERE username = ? OR real_name = ?
    """, (username, username))
    
    user = cursor.fetchone()
    
    if not user:
        print("❌ 未找到用户")
        conn.close()
        return
    
    print(f"✓ 找到用户: {user['real_name'] or user['username']}({user['username']}) [{user['department'] or '无'}]")
    
    # 查询消息
    cursor.execute("""
        SELECT m.id, m.conversation_id, m.content, m.created_date, m.is_recalled,
               c.name as conv_name
        FROM chat_message m
        LEFT JOIN chat_conversation c ON m.conversation_id = c.id
        WHERE m.sender_id = ?
        ORDER BY m.created_date DESC
    """, (user['id'],))
    
    msgs = cursor.fetchall()
    print(f"\n该用户共发送 {len(msgs)} 条消息\n")
    
    for msg in msgs:
        status = " [已撤回]" if msg['is_recalled'] else ""
        content = (msg['content'][:60] + "...") if msg['content'] and len(msg['content']) > 60 else (msg['content'] or "")
        print(f"[{msg['created_date']}] 会话#{msg['conversation_id']} {msg['conv_name'] or ''}")
        print(f"  {content}{status}\n")
    
    conn.close()

def search_content(keyword):
    """搜索消息内容"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print(f"\n搜索关键词: '{keyword}'")
    
    cursor.execute("""
        SELECT m.id, m.content, m.created_date,
               u.username, u.real_name,
               c.id as conv_id, c.name as conv_name
        FROM chat_message m
        LEFT JOIN app_user u ON m.sender_id = u.id
        LEFT JOIN chat_conversation c ON m.conversation_id = c.id
        WHERE m.content LIKE ? AND m.is_recalled = 0
        ORDER BY m.created_date DESC
    """, (f'%{keyword}%',))
    
    msgs = cursor.fetchall()
    print(f"找到 {len(msgs)} 条匹配消息\n")
    
    for msg in msgs:
        name = msg['real_name'] or msg['username'] or '未知'
        print(f"[{msg['created_date']}] {name} 在会话「{msg['conv_name'] or msg['conv_id']}」中:")
        print(f"  {msg['content']}\n")
    
    conn.close()

def main():
    if len(sys.argv) < 2:
        print("""
管理员聊天记录查看工具

使用方法:
  python admin_view_chat.py conv              # 查看所有会话(含参与者)
  python admin_view_chat.py msg <会话ID>       # 查看指定会话的所有消息
  python admin_view_chat.py msg               # 查看所有消息
  python admin_view_chat.py user <用户名>      # 查看指定用户的所有消息
  python admin_view_chat.py search <关键词>    # 搜索消息内容

示例:
  python admin_view_chat.py msg 5             # 查看会话5的聊天记录
  python admin_view_chat.py user admin        # 查看admin的所有消息
  python admin_view_chat.py user 朱绪          # 查看朱绪的所有消息
  python admin_view_chat.py search 设备        # 搜索包含"设备"的消息
""")
        return
    
    cmd = sys.argv[1]
    
    if cmd == 'conv':
        view_all_conversations()
    elif cmd == 'msg':
        cid = int(sys.argv[2]) if len(sys.argv) > 2 else None
        view_conversation_messages(cid)
    elif cmd == 'user':
        if len(sys.argv) < 3:
            print("❌ 需要指定用户名或姓名")
            return
        view_user_messages(sys.argv[2])
    elif cmd == 'search':
        if len(sys.argv) < 3:
            print("❌ 需要指定搜索关键词")
            return
        search_content(' '.join(sys.argv[2:]))
    else:
        print(f"❌ 未知命令: {cmd}")
        print("使用 python admin_view_chat.py 查看帮助")

if __name__ == '__main__':
    main()
