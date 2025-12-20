"""
创建测试聊天数据
"""
from app import create_app, db
from app.models import User
from app.chat_models import ChatConversation, ChatParticipant, ChatMessage
from datetime import datetime, timedelta

app = create_app()

with app.app_context():
    # 获取现有用户
    users = User.query.limit(5).all()
    
    if len(users) < 2:
        print("❌ 用户数量不足,至少需要2个用户")
        exit(1)
    
    print(f"✓ 找到 {len(users)} 个用户:")
    for user in users:
        print(f"  - {user.username} (ID: {user.id})")
    
    # 创建测试会话1: 两人对话
    print("\n创建测试会话1: 两人对话")
    conv1 = ChatConversation(
        name=f"{users[0].username} 和 {users[1].username}",
        creator_id=users[0].id,
        conversation_type='direct'
    )
    db.session.add(conv1)
    db.session.flush()
    
    # 添加参与者
    p1 = ChatParticipant(conversation_id=conv1.id, user_id=users[0].id)
    p2 = ChatParticipant(conversation_id=conv1.id, user_id=users[1].id)
    db.session.add_all([p1, p2])
    
    # 添加消息
    messages_conv1 = [
        ChatMessage(
            conversation_id=conv1.id,
            sender_id=users[0].id,
            content="你好!最近怎么样?",
            message_type='text',
            created_date=datetime.utcnow() - timedelta(minutes=30)
        ),
        ChatMessage(
            conversation_id=conv1.id,
            sender_id=users[1].id,
            content="挺好的,正在处理设备维修工单。",
            message_type='text',
            created_date=datetime.utcnow() - timedelta(minutes=28)
        ),
        ChatMessage(
            conversation_id=conv1.id,
            sender_id=users[0].id,
            content="需要帮忙吗?我这边有几台备用设备。",
            message_type='text',
            created_date=datetime.utcnow() - timedelta(minutes=25)
        ),
        ChatMessage(
            conversation_id=conv1.id,
            sender_id=users[1].id,
            content="太好了!我需要一台笔记本电脑。",
            message_type='text',
            created_date=datetime.utcnow() - timedelta(minutes=20)
        ),
        ChatMessage(
            conversation_id=conv1.id,
            sender_id=users[0].id,
            content="没问题,我现在就给你发过去。",
            message_type='text',
            created_date=datetime.utcnow() - timedelta(minutes=15)
        ),
    ]
    db.session.add_all(messages_conv1)
    
    # 创建测试会话2: 群聊
    if len(users) >= 3:
        print("\n创建测试会话2: 群聊")
        conv2 = ChatConversation(
            name="技术讨论组",
            creator_id=users[0].id,
            conversation_type='group'
        )
        db.session.add(conv2)
        db.session.flush()
        
        # 添加参与者(前3个用户)
        for i in range(min(3, len(users))):
            p = ChatParticipant(conversation_id=conv2.id, user_id=users[i].id)
            db.session.add(p)
        
        # 添加消息
        messages_conv2 = [
            ChatMessage(
                conversation_id=conv2.id,
                sender_id=users[0].id,
                content="大家好!今天我们讨论一下新的资产管理流程。",
                message_type='text',
                created_date=datetime.utcnow() - timedelta(hours=2)
            ),
            ChatMessage(
                conversation_id=conv2.id,
                sender_id=users[1].id,
                content="好的,我准备了一些数据分析报告。",
                message_type='text',
                created_date=datetime.utcnow() - timedelta(hours=1, minutes=50)
            ),
            ChatMessage(
                conversation_id=conv2.id,
                sender_id=users[2].id,
                content="我也带了设备清单,等会儿分享给大家。",
                message_type='text',
                created_date=datetime.utcnow() - timedelta(hours=1, minutes=45)
            ),
            ChatMessage(
                conversation_id=conv2.id,
                sender_id=users[0].id,
                content="很好!我们先从设备分类开始讨论吧。",
                message_type='text',
                created_date=datetime.utcnow() - timedelta(hours=1, minutes=30)
            ),
            ChatMessage(
                conversation_id=conv2.id,
                sender_id=users[1].id,
                content="建议按部门和设备类型双维度分类。",
                message_type='text',
                created_date=datetime.utcnow() - timedelta(hours=1, minutes=15)
            ),
            ChatMessage(
                conversation_id=conv2.id,
                sender_id=users[2].id,
                content="赞同!这样查询和统计都更方便。",
                message_type='text',
                created_date=datetime.utcnow() - timedelta(hours=1)
            ),
            ChatMessage(
                conversation_id=conv2.id,
                sender_id=users[0].id,
                content="那就这么定了,我来更新系统文档。",
                message_type='text',
                created_date=datetime.utcnow() - timedelta(minutes=45)
            ),
        ]
        db.session.add_all(messages_conv2)
    
    # 创建测试会话3: 最近的对话
    if len(users) >= 4:
        print("\n创建测试会话3: 最近的对话")
        conv3 = ChatConversation(
            name=f"{users[0].username} 和 {users[3].username}",
            creator_id=users[0].id,
            conversation_type='direct'
        )
        db.session.add(conv3)
        db.session.flush()
        
        # 添加参与者
        p1 = ChatParticipant(conversation_id=conv3.id, user_id=users[0].id)
        p2 = ChatParticipant(conversation_id=conv3.id, user_id=users[3].id)
        db.session.add_all([p1, p2])
        
        # 添加消息
        messages_conv3 = [
            ChatMessage(
                conversation_id=conv3.id,
                sender_id=users[3].id,
                content="你好,有个紧急的设备故障需要处理。",
                message_type='text',
                created_date=datetime.utcnow() - timedelta(minutes=5)
            ),
            ChatMessage(
                conversation_id=conv3.id,
                sender_id=users[0].id,
                content="收到!具体是什么问题?",
                message_type='text',
                created_date=datetime.utcnow() - timedelta(minutes=4)
            ),
            ChatMessage(
                conversation_id=conv3.id,
                sender_id=users[3].id,
                content="会议室的投影仪无法开机,半小时后有重要会议。",
                message_type='text',
                created_date=datetime.utcnow() - timedelta(minutes=3)
            ),
            ChatMessage(
                conversation_id=conv3.id,
                sender_id=users[0].id,
                content="明白了,我马上过去检查!",
                message_type='text',
                created_date=datetime.utcnow() - timedelta(minutes=2)
            ),
        ]
        db.session.add_all(messages_conv3)
    
    # 提交所有更改
    try:
        db.session.commit()
        print("\n✓ 测试聊天数据创建成功!")
        print(f"  - 会话数量: {ChatConversation.query.count()}")
        print(f"  - 消息数量: {ChatMessage.query.count()}")
        print(f"  - 参与者数量: {ChatParticipant.query.count()}")
        print("\n现在可以访问 http://localhost:5020/chat 查看聊天功能")
    except Exception as e:
        db.session.rollback()
        print(f"\n❌ 创建失败: {e}")
        raise
