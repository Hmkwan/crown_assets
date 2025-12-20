"""
在Flask应用内直接测试API响应
"""
from app import create_app, db
from app.models import User
from app.chat_models import ChatConversation, ChatParticipant, ChatMessage
from flask import json

app = create_app()

with app.app_context():
    # 获取admin用户
    admin = User.query.filter_by(username='admin').first()
    
    print("=" * 80)
    print(f"当前用户: {admin.username} (ID: {admin.id})")
    print("=" * 80)
    
    # 测试API逻辑
    print("\n1. 查询用户参与的会话")
    print("=" * 80)
    
    participants = ChatParticipant.query.filter_by(
        user_id=admin.id,
        is_left=False
    ).all()
    
    print(f"找到 {len(participants)} 个参与记录")
    
    for p in participants:
        print(f"\n参与者记录 ID:{p.id}")
        print(f"  会话ID: {p.conversation_id}")
        print(f"  会话对象: {p.conversation}")
        if p.conversation:
            print(f"  会话名称: {p.conversation.name}")
            print(f"  会话类型: {p.conversation.conversation_type}")
            print(f"  最后消息时间: {p.conversation.last_message_time}")
            
            # 测试to_dict方法
            try:
                conv_dict = p.conversation.to_dict(admin.id)
                print(f"  to_dict结果: {json.dumps(conv_dict, ensure_ascii=False, indent=2)}")
            except Exception as e:
                print(f"  ❌ to_dict失败: {e}")
    
    print("\n" + "=" * 80)
    print("2. 测试手动构建响应")
    print("=" * 80)
    
    conversations = []
    for p in participants:
        try:
            conv_dict = p.conversation.to_dict(admin.id)
            conv_dict['is_pinned'] = p.is_pinned
            conv_dict['is_muted'] = p.is_muted
            
            # 获取最后一条消息
            if p.conversation.last_message:
                conv_dict['last_message'] = {
                    'content': p.conversation.last_message.content,
                    'sender_name': p.conversation.last_message.sender.username,
                    'created_date': p.conversation.last_message.created_date.strftime('%Y-%m-%d %H:%M:%S')
                }
            
            conversations.append(conv_dict)
            print(f"✓ 会话 {conv_dict['id']} 添加成功")
        except Exception as e:
            print(f"❌ 处理会话失败: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n成功构建 {len(conversations)} 个会话")
    print("\n最终JSON:")
    print(json.dumps({'conversations': conversations}, ensure_ascii=False, indent=2))
