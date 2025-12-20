#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""检查聊天数据"""
from app import create_app, db
from app.chat_models import ChatConversation, ChatParticipant, ChatMessage
from app.models import User

app = create_app()
with app.app_context():
    print("="*80)
    print("聊天系统数据检查")
    print("="*80)
    
    # 会话
    convs = ChatConversation.query.all()
    print(f"\n✓ 会话数: {len(convs)}")
    for c in convs:
        print(f"  - 会话#{c.id}: {c.type} | 创建于 {c.created_date}")
        
        # 参与者
        parts = ChatParticipant.query.filter_by(conversation_id=c.id).all()
        users = [p.user.username if p.user else '?' for p in parts]
        print(f"    参与者: {' ↔ '.join(users)}")
        
        # 消息数
        msg_count = ChatMessage.query.filter_by(conversation_id=c.id).count()
        print(f"    消息数: {msg_count}")
    
    # 最新消息
    print(f"\n最新5条消息:")
    msgs = ChatMessage.query.order_by(ChatMessage.created_date.desc()).limit(5).all()
    for m in msgs:
        sender = m.sender.username if m.sender else '?'
        content = m.content[:40] if m.content else ''
        print(f"  [{m.created_date}] {sender}: {content}")
    
    print("\n" + "="*80)
