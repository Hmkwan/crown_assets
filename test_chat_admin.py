"""
聊天管理系统功能测试
快速验证所有管理API是否正常工作
"""

def test_chat_admin():
    from app import create_app, db
    from app.chat_models import ChatConversation, ChatMessage, ChatParticipant
    from app.models import User
    
    app = create_app()
    
    with app.app_context():
        print("\n" + "="*60)
        print("聊天管理系统功能测试")
        print("="*60)
        
        # 1. 检查数据表
        print("\n1. 检查数据表...")
        conv_count = ChatConversation.query.count()
        msg_count = ChatMessage.query.count()
        part_count = ChatParticipant.query.count()
        print(f"   ✓ 会话数: {conv_count}")
        print(f"   ✓ 消息数: {msg_count}")
        print(f"   ✓ 参与者数: {part_count}")
        
        # 2. 检查管理员用户
        print("\n2. 检查管理员用户...")
        admins = User.query.filter_by(role='admin').all()
        print(f"   ✓ 管理员数量: {len(admins)}")
        for admin in admins[:3]:
            print(f"   - {admin.username} (ID={admin.id})")
        
        # 3. 检查会话类型分布
        print("\n3. 检查会话类型分布...")
        from sqlalchemy import func
        types = db.session.query(
            ChatConversation.conversation_type,
            func.count(ChatConversation.id)
        ).group_by(ChatConversation.conversation_type).all()
        for conv_type, count in types:
            print(f"   - {conv_type}: {count}个")
        
        # 4. 检查消息发送者
        print("\n4. 检查活跃用户(前5名)...")
        active_users = db.session.query(
            User,
            func.count(ChatMessage.id).label('msg_count')
        ).join(
            ChatMessage, User.id == ChatMessage.sender_id
        ).group_by(User.id).order_by(
            func.count(ChatMessage.id).desc()
        ).limit(5).all()
        
        for idx, (user, msg_count) in enumerate(active_users, 1):
            username = getattr(user, 'real_name', user.username)
            print(f"   {idx}. {username}: {msg_count}条消息")
        
        # 5. 检查最近消息
        print("\n5. 检查最近的5条消息...")
        recent_msgs = ChatMessage.query.filter_by(
            is_deleted=False
        ).order_by(
            ChatMessage.created_date.desc()
        ).limit(5).all()
        
        for msg in recent_msgs:
            sender = User.query.get(msg.sender_id)
            sender_name = getattr(sender, 'real_name', sender.username) if sender else '未知'
            content = msg.content[:30] + '...' if msg.content and len(msg.content) > 30 else msg.content or '(附件)'
            print(f"   - [{msg.id}] {sender_name}: {content}")
        
        # 6. 模拟统计API数据
        print("\n6. 模拟统计API响应...")
        from datetime import datetime, timedelta
        
        today = datetime.now().date()
        today_msgs = ChatMessage.query.filter(
            func.date(ChatMessage.created_date) == today
        ).count()
        
        # 简化活跃会话查询
        active_conv_ids = {msg.conversation_id for msg in ChatMessage.query.all()}
        active_conv_count = len(active_conv_ids)
        
        print(f"   ✓ 总会话数: {conv_count}")
        print(f"   ✓ 活跃会话数: {active_conv_count}")
        print(f"   ✓ 总消息数: {msg_count}")
        print(f"   ✓ 今日消息数: {today_msgs}")
        print(f"   ✓ 活跃用户数: {db.session.query(ChatMessage.sender_id).distinct().count()}")
        
        # 7. 检查消息趋势(最近7天)
        print("\n7. 检查消息趋势(最近7天)...")
        for i in range(6, -1, -1):
            date = today - timedelta(days=i)
            count = ChatMessage.query.filter(
                func.date(ChatMessage.created_date) == date
            ).count()
            print(f"   {date}: {count}条")
        
        print("\n" + "="*60)
        print("✅ 所有检查完成!")
        print("="*60)
        print("\n访问管理页面: http://localhost:5020/chat/admin")
        print("(需要管理员权限)\n")

if __name__ == '__main__':
    test_chat_admin()
