"""
聊天系统快速测试脚本
测试基本功能是否正常工作
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User, Department
from app.chat_models import ChatConversation, ChatParticipant, ChatMessage

def test_chat_system():
    """测试聊天系统基本功能"""
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print("聊天系统功能测试")
        print("=" * 60)
        
        # 1. 检查表是否存在
        print("\n1. 检查数据库表...")
        tables = db.inspect(db.engine).get_table_names()
        chat_tables = [t for t in tables if t.startswith('chat_')]
        
        assert len(chat_tables) == 5, f"聊天表不完整,只找到 {len(chat_tables)} 个"
        print(f"✓ 找到5个聊天表: {', '.join(chat_tables)}")
        
        # 2. 检查是否有测试用户
        print("\n2. 检查测试用户...")
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            # create admin to ensure test runs in isolated DB
            admin = User(username='admin', email='admin@example.com', role='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
        print(f"✓ 找到测试用户: {admin.username} (ID={admin.id})")
        
        # 3. 创建测试会话
        print("\n3. 创建测试会话...")
        
        # 查找或创建第二个用户
        test_user = User.query.filter(User.id != admin.id).first()
        if not test_user:
            # 创建测试用户
            dept = Department.query.first()
            test_user = User(
                username='chattest',
                real_name='聊天测试用户',
                email='chattest@test.com',
                role='user',
                department_id=dept.id if dept else None
            )
            test_user.set_password('123456')
            db.session.add(test_user)
            db.session.commit()
            print(f"✓ 创建测试用户: {test_user.username} (ID={test_user.id})")
        else:
            print(f"✓ 使用现有用户: {test_user.username} (ID={test_user.id})")
        
        # 创建一对一会话
        conversation = ChatConversation(
            conversation_type='direct',
            creator_id=admin.id
        )
        db.session.add(conversation)
        db.session.flush()
        
        # 添加参与者
        participant1 = ChatParticipant(
            conversation_id=conversation.id,
            user_id=admin.id,
            role='member'
        )
        participant2 = ChatParticipant(
            conversation_id=conversation.id,
            user_id=test_user.id,
            role='member'
        )
        db.session.add_all([participant1, participant2])
        db.session.commit()
        
        print(f"✓ 创建会话: ID={conversation.id}, 类型={conversation.conversation_type}")
        print(f"  参与者: {admin.username}, {test_user.username}")
        
        # 4. 发送测试消息
        print("\n4. 发送测试消息...")
        
        message = ChatMessage(
            conversation_id=conversation.id,
            sender_id=admin.id,
            message_type='text',
            content='这是一条测试消息!'
        )
        db.session.add(message)
        
        # 更新会话最后消息
        conversation.last_message_id = message.id
        conversation.last_message_time = message.created_date
        
        # 更新未读数
        participant2.unread_count += 1
        
        db.session.commit()
        
        print(f"✓ 发送消息: ID={message.id}")
        print(f"  内容: {message.content}")
        print(f"  时间: {message.created_date}")
        
        # 5. 测试消息序列化
        print("\n5. 测试消息序列化...")
        message_dict = message.to_dict()
        required_fields = ['id', 'conversation_id', 'sender_id', 'content', 'created_date']
        
        missing_fields = [f for f in required_fields if f not in message_dict]
        assert not missing_fields, f"缺少字段: {', '.join(missing_fields)}"
        print("✓ 消息序列化正常")
        print(f"  字段数: {len(message_dict)}")
        
        # 6. 测试会话序列化
        print("\n6. 测试会话序列化...")
        conv_dict = conversation.to_dict(current_user_id=admin.id)
        
        assert 'other_user' in conv_dict, "会话序列化缺少other_user字段"
        print(f"✓ 会话序列化正常")
        print(f"  对方用户: {conv_dict['other_user']['username']}")
        print(f"  未读数: {conv_dict.get('unread_count', 0)}")
        
        # 7. 统计信息
        print("\n7. 数据库统计...")
        stats = {
            '会话数': ChatConversation.query.count(),
            '参与者数': ChatParticipant.query.count(),
            '消息数': ChatMessage.query.count()
        }
        
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        print("\n" + "=" * 60)
        print("✅ 聊天系统测试通过!")
        print("=" * 60)
        
        # 清理测试数据（在pytest环境下自动清理）
        print("\n是否清理测试数据? (y/n): ", end='')
        try:
            if os.environ.get('PYTEST_CURRENT_TEST') or 'pytest' in sys.modules:
                # 在pytest环境下默认选择清理，避免交互阻塞
                choice = 'y'
                print(choice)
            else:
                choice = input().strip().lower()
        except Exception:
            choice = 'y'

        if choice == 'y':
            db.session.delete(message)
            db.session.delete(participant1)
            db.session.delete(participant2)
            db.session.delete(conversation)
            if test_user.username == 'chattest':
                db.session.delete(test_user)
            db.session.commit()
            print("✓ 测试数据已清理")
        else:
            print("ℹ 保留测试数据")
        
        return True

if __name__ == '__main__':
    try:
        success = test_chat_system()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
