#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""初始化聊天测试数据"""
from app import create_app, db
from app.chat_models import ChatConversation, ChatParticipant, ChatMessage
from app.models import User
from datetime import datetime

app = create_app()
with app.app_context():
    print("="*80)
    print("初始化聊天测试数据")
    print("="*80)
    
    # 获取用户
    admin = User.query.filter_by(username='admin').first()
    other_user = User.query.filter(User.username != 'admin').first()
    
    if not admin:
        print("❌ 未找到admin用户")
        exit(1)
    
    if not other_user:
        print("❌ 未找到其他用户")
        exit(1)
    
    print(f"✓ 用户1: {admin.username} (ID:{admin.id})")
    print(f"✓ 用户2: {other_user.username} (ID:{other_user.id})")
    
    # 检查是否已有会话
    existing = ChatConversation.query.first()
    if existing:
        print(f"\n已有 {ChatConversation.query.count()} 个会话,跳过创建")
    else:
        # 创建测试会话
        conv = ChatConversation(
            conversation_type='direct',
            name=None,
            creator_id=admin.id,
            created_date=datetime.now()
        )
        db.session.add(conv)
        db.session.flush()
        
        # 添加参与者
        p1 = ChatParticipant(
            conversation_id=conv.id,
            user_id=admin.id,
            joined_date=datetime.now()
        )
        p2 = ChatParticipant(
            conversation_id=conv.id,
            user_id=other_user.id,
            joined_date=datetime.now()
        )
        db.session.add(p1)
        db.session.add(p2)
        
        # 添加测试消息
        msg1 = ChatMessage(
            conversation_id=conv.id,
            sender_id=admin.id,
            content='你好!这是一条测试消息',
            message_type='text',
            created_date=datetime.now()
        )
        db.session.add(msg1)
        db.session.flush()
        
        # 更新会话最后消息
        conv.last_message_id = msg1.id
        conv.last_message_time = msg1.created_date
        
        db.session.commit()
        
        print(f"\n✓ 创建测试会话 #{conv.id}")
        print(f"  参与者: {admin.username} ↔ {other_user.username}")
        print(f"  消息数: 1")
    
    # 显示当前状态
    print(f"\n当前数据:")
    print(f"  会话数: {ChatConversation.query.count()}")
    print(f"  消息数: {ChatMessage.query.count()}")
    print(f"  参与者: {ChatParticipant.query.count()}")
    
    print("\n" + "="*80)
    print("✓ 初始化完成!")
    print("现在访问: http://10.168.93.93:5020/chat")
    print("="*80)
