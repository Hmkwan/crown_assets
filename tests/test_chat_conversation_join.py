from app.chat_models import ChatConversation, ChatParticipant
from app.models import User
import pytest
from app import create_app, db

@pytest.fixture
def app_ctx():
    app = create_app()
    app.config['TESTING'] = True
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


def test_create_conversation_joins_user_if_not_participant(app_ctx):
    # 创建两个用户 u1 (请求者) 和 u2 (已有会话的参与者)
    u1 = User(username='u1-join-test', email='u1-join@example.com')
    u1.set_password('pass')
    u2 = User(username='u2-join-test', email='u2-join@example.com')
    u2.set_password('pass')
    db = app_ctx.db if hasattr(app_ctx, 'db') else __import__('app').db
    db.session.add_all([u1, u2])
    db.session.commit()

    # 创建会话并仅加入 u2
    conv = ChatConversation(conversation_type='direct', creator_id=u2.id)
    db.session.add(conv)
    db.session.flush()
    p2 = ChatParticipant(conversation_id=conv.id, user_id=u2.id)
    db.session.add(p2)
    db.session.commit()

    client = app_ctx.test_client()

    # 登录为 u1
    with client:
        client.post('/auth/login', data={'username': u1.username, 'password': 'pass'}, follow_redirects=True)
        # 直接尝试获取会话详情，API 应该自动将 u1 加入（容错行为）并返回会话
        resp = client.get(f'/api/chat/conversations/{conv.id}')
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'conversation' in data

        # 确认数据库中现在存在 u1 的参与记录
        pr = ChatParticipant.query.filter_by(conversation_id=conv.id, user_id=u1.id).first()
        assert pr is not None
        assert pr.is_left is False
