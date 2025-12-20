"""
清空并重建聊天测试数据
"""
from app import create_app, db
from app.models import User
from app.chat_models import ChatConversation, ChatParticipant, ChatMessage
from datetime import datetime, timedelta

app = create_app()

with app.app_context():
    print("=" * 80)
    print("清空现有聊天数据")
    print("=" * 80)
    
    # 删除所有聊天数据
    ChatMessage.query.delete()
    ChatParticipant.query.delete()
    ChatConversation.query.delete()
    db.session.commit()
    print("✓ 已清空所有聊天数据")
    
    # 获取现有用户
    users = User.query.limit(5).all()
    
    if len(users) < 2:
        print("❌ 用户数量不足,至少需要2个用户")
        exit(1)
    
    print(f"\n✓ 找到 {len(users)} 个用户:")
    for user in users:
        print(f"  - {user.username} (ID: {user.id})")
    
    # 创建会话1: admin 和 朱绪 的私聊
    print("\n" + "=" * 80)
    print("创建会话1: admin 和 朱绪 的私聊")
    print("=" * 80)
    conv1 = ChatConversation(
        name=f"{users[0].username}和{users[1].username}",
        creator_id=users[0].id,
        conversation_type='direct'
    )
    db.session.add(conv1)
    db.session.flush()
    
    # 添加参与者
    p1 = ChatParticipant(conversation_id=conv1.id, user_id=users[0].id)
    p2 = ChatParticipant(conversation_id=conv1.id, user_id=users[1].id)
    db.session.add_all([p1, p2])
    
    # 添加消息 (注意发送者交替)
    base_time = datetime.utcnow()
    messages_conv1 = [
        ChatMessage(
            conversation_id=conv1.id,
            sender_id=users[0].id,  # admin发送
            content="你好!最近设备管理系统用得怎么样?",
            message_type='text',
            created_date=base_time - timedelta(minutes=30)
        ),
        ChatMessage(
            conversation_id=conv1.id,
            sender_id=users[1].id,  # 朱绪回复
            content="挺好的!正在处理几个设备维修工单。",
            message_type='text',
            created_date=base_time - timedelta(minutes=28)
        ),
        ChatMessage(
            conversation_id=conv1.id,
            sender_id=users[0].id,  # admin
            content="需要帮忙吗?我这边有几台备用设备。",
            message_type='text',
            created_date=base_time - timedelta(minutes=25)
        ),
        ChatMessage(
            conversation_id=conv1.id,
            sender_id=users[1].id,  # 朱绪
            content="太好了!我需要一台笔记本电脑,客户端那边急用。",
            message_type='text',
            created_date=base_time - timedelta(minutes=20)
        ),
        ChatMessage(
            conversation_id=conv1.id,
            sender_id=users[0].id,  # admin
            content="没问题,我现在就给你调配一台ThinkPad。",
            message_type='text',
            created_date=base_time - timedelta(minutes=15)
        ),
    ]
    db.session.add_all(messages_conv1)
    print(f"✓ 会话1创建成功,添加了 {len(messages_conv1)} 条消息")
    print(f"  参与者: {users[0].username} ↔ {users[1].username}")
    
    # 创建会话2: 三人技术讨论组
    if len(users) >= 3:
        print("\n" + "=" * 80)
        print("创建会话2: 技术讨论组(三人群聊)")
        print("=" * 80)
        conv2 = ChatConversation(
            name="设备管理技术讨论组",
            creator_id=users[0].id,
            conversation_type='group'
        )
        db.session.add(conv2)
        db.session.flush()
        
        # 添加参与者(前3个用户)
        for i in range(min(3, len(users))):
            p = ChatParticipant(conversation_id=conv2.id, user_id=users[i].id)
            db.session.add(p)
        
        # 添加消息 (三个人轮流发言)
        messages_conv2 = [
            ChatMessage(
                conversation_id=conv2.id,
                sender_id=users[0].id,  # admin
                content="@全体成员 今天我们讨论一下新的资产管理流程优化方案。",
                message_type='text',
                created_date=base_time - timedelta(hours=2)
            ),
            ChatMessage(
                conversation_id=conv2.id,
                sender_id=users[1].id,  # 朱绪
                content="好的!我准备了这个月的设备使用率分析报告,稍后分享给大家。",
                message_type='text',
                created_date=base_time - timedelta(hours=1, minutes=50)
            ),
            ChatMessage(
                conversation_id=conv2.id,
                sender_id=users[2].id,  # 陈松
                content="我这边整理了各部门的设备清单和维修记录,等会儿一起看看。",
                message_type='text',
                created_date=base_time - timedelta(hours=1, minutes=45)
            ),
            ChatMessage(
                conversation_id=conv2.id,
                sender_id=users[0].id,  # admin
                content="很好!我们先从设备分类和编码规则开始讨论。",
                message_type='text',
                created_date=base_time - timedelta(hours=1, minutes=30)
            ),
            ChatMessage(
                conversation_id=conv2.id,
                sender_id=users[1].id,  # 朱绪
                content="建议按「部门-设备类型-序号」的方式编码,便于查询统计。",
                message_type='text',
                created_date=base_time - timedelta(hours=1, minutes=15)
            ),
            ChatMessage(
                conversation_id=conv2.id,
                sender_id=users[2].id,  # 陈松
                content="赞同!而且这样可以直接从编码看出设备归属,管理起来更方便。",
                message_type='text',
                created_date=base_time - timedelta(hours=1)
            ),
        ]
        db.session.add_all(messages_conv2)
        print(f"✓ 会话2创建成功,添加了 {len(messages_conv2)} 条消息")
        print(f"  参与者: {users[0].username}, {users[1].username}, {users[2].username}")
    
    # 提交所有更改
    try:
        db.session.commit()
        print("\n" + "=" * 80)
        print("✓ 测试数据创建成功!")
        print("=" * 80)
        
        # 详细统计
        print(f"会话总数: {ChatConversation.query.count()}")
        print(f"消息总数: {ChatMessage.query.count()}")
        print(f"参与者总数: {ChatParticipant.query.count()}")
        
        print("\n会话详情:")
        for conv in ChatConversation.query.all():
            msg_count = ChatMessage.query.filter_by(conversation_id=conv.id).count()
            participant_count = ChatParticipant.query.filter_by(conversation_id=conv.id).count()
            print(f"  - [{conv.conversation_type}] {conv.name}: {msg_count}条消息, {participant_count}个参与者")
        
        print("\n消息发送者统计:")
        for user in users[:3]:
            msg_count = ChatMessage.query.filter_by(sender_id=user.id).count()
            print(f"  - {user.username} (ID:{user.id}): 发送了 {msg_count} 条消息")
            
    except Exception as e:
        db.session.rollback()
        print(f"\n❌ 创建失败: {e}")
        raise
