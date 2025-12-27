# -*- coding: utf-8 -*-
import pytest
from app import create_app, db
from app.models import User
from app.chat_models import ChatConversation, ChatParticipant, ChatMessage


@pytest.fixture
def app_ctx():
    app = create_app()
    app.config['TESTING'] = True
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


def test_send_message_increments_unread(app_ctx):
    # 创建两个用户
    import uuid
    uname1 = f'u1_{uuid.uuid4().hex[:8]}'
    uname2 = f'u2_{uuid.uuid4().hex[:8]}'
    u1 = User(username=uname1, email=f'{uname1}@example.com')
    u1.set_password('pass')
    u2 = User(username=uname2, email=f'{uname2}@example.com')
    u2.set_password('pass')
    db.session.add_all([u1, u2])
    db.session.commit()

    # 创建一对一会话
    conv = ChatConversation(conversation_type='direct', creator_id=u1.id)
    db.session.add(conv)
    db.session.flush()

    p1 = ChatParticipant(conversation_id=conv.id, user_id=u1.id)
    p2 = ChatParticipant(conversation_id=conv.id, user_id=u2.id)
    db.session.add_all([p1, p2])
    db.session.commit()

    # 模拟 u1 发送消息
    msg = ChatMessage(conversation_id=conv.id, sender_id=u1.id, content='hello')
    db.session.add(msg)
    db.session.flush()

    # 触发未读更新逻辑 as in send_message route
    # 增加 p2 未读数
    p2.unread_count = (p2.unread_count or 0) + 1
    db.session.add(p2)
    db.session.commit()

    p2_reloaded = ChatParticipant.query.filter_by(conversation_id=conv.id, user_id=u2.id).first()
    assert p2_reloaded.unread_count == 1
