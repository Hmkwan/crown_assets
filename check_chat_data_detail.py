"""
详细检查聊天数据
"""
from app import create_app, db
from app.models import User
from app.chat_models import ChatConversation, ChatParticipant, ChatMessage
from sqlalchemy import text

app = create_app()

with app.app_context():
    print("=" * 80)
    print("检查用户数据")
    print("=" * 80)
    users = User.query.all()
    for user in users:
        print(f"ID: {user.id}, 用户名: {user.username}")
    
    print("\n" + "=" * 80)
    print("检查会话数据")
    print("=" * 80)
    conversations = ChatConversation.query.all()
    for conv in conversations:
        print(f"\n会话ID: {conv.id}")
        print(f"  名称: {conv.name}")
        print(f"  类型: {conv.conversation_type}")
        print(f"  创建者ID: {conv.creator_id}")
        
        # 显示参与者
        participants = ChatParticipant.query.filter_by(conversation_id=conv.id).all()
        print(f"  参与者: {len(participants)} 人")
        for p in participants:
            user = User.query.get(p.user_id)
            print(f"    - {user.username} (ID: {user.id})")
    
    print("\n" + "=" * 80)
    print("检查消息数据 (最近20条)")
    print("=" * 80)
    messages = ChatMessage.query.order_by(ChatMessage.created_date.desc()).limit(20).all()
    
    for msg in messages:
        sender = User.query.get(msg.sender_id)
        conv = ChatConversation.query.get(msg.conversation_id)
        print(f"\n消息ID: {msg.id}")
        print(f"  会话: {conv.name if conv else 'N/A'} (ID: {msg.conversation_id})")
        print(f"  发送者: {sender.username if sender else 'N/A'} (ID: {msg.sender_id})")
        print(f"  内容: {msg.content[:50]}...")
        print(f"  时间: {msg.created_date}")
    
    print("\n" + "=" * 80)
    print("统计信息")
    print("=" * 80)
    print(f"用户总数: {User.query.count()}")
    print(f"会话总数: {ChatConversation.query.count()}")
    print(f"消息总数: {ChatMessage.query.count()}")
    print(f"参与者总数: {ChatParticipant.query.count()}")
    
    # 检查是否有孤立消息(发送者不存在的)
    print("\n" + "=" * 80)
    print("检查数据完整性")
    print("=" * 80)
    
    orphan_messages = db.session.execute(text("""
        SELECT m.id, m.sender_id, m.conversation_id, m.content
        FROM chat_message m
        LEFT JOIN user u ON m.sender_id = u.id
        WHERE u.id IS NULL
        LIMIT 5
    """)).fetchall()
    
    if orphan_messages:
        print("⚠️  发现孤立消息(发送者不存在):")
        for row in orphan_messages:
            print(f"  消息ID: {row[0]}, SENDER_ID: {row[1]}, 内容: {row[3][:30]}...")
    else:
        print("✓ 没有孤立消息")
    
    # 检查会话参与者是否正确
    invalid_participants = db.session.execute(text("""
        SELECT p.id, p.conversation_id, p.user_id
        FROM chat_participant p
        LEFT JOIN user u ON p.user_id = u.id
        WHERE u.id IS NULL
        LIMIT 5
    """)).fetchall()
    
    if invalid_participants:
        print("\n⚠️  发现无效参与者(用户不存在):")
        for row in invalid_participants:
            print(f"  参与者ID: {row[0]}, USER_ID: {row[2]}")
    else:
        print("✓ 所有参与者都有效")
