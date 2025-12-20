"""
更新会话的last_message字段
"""
from app import create_app, db
from app.chat_models import ChatConversation, ChatMessage

app = create_app()

with app.app_context():
    print("更新所有会话的last_message...")
    
    conversations = ChatConversation.query.all()
    
    for conv in conversations:
        # 获取该会话的最后一条消息
        last_msg = ChatMessage.query.filter_by(
            conversation_id=conv.id,
            is_deleted=False
        ).order_by(ChatMessage.created_date.desc()).first()
        
        if last_msg:
            conv.last_message_id = last_msg.id
            conv.last_message_time = last_msg.created_date
            print(f"✓ 会话{conv.id} ({conv.name}): 更新last_message_id={last_msg.id}")
        else:
            print(f"  会话{conv.id} ({conv.name}): 无消息")
    
    db.session.commit()
    print(f"\n✓ 完成! 更新了 {len(conversations)} 个会话")
