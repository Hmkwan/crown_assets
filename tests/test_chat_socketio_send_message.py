# -*- coding: utf-8 -*-
import pytest
from app import create_app, db
from app.models import User
from app.chat_models import ChatConversation, ChatParticipant
from app.socketio_handler import init_socketio, socketio


@pytest.fixture
def app_with_socket():
    app = create_app()
    app.config['TESTING'] = True
    with app.app_context():
        db.create_all()
        init_socketio(app)
        yield app
        db.session.remove()
        db.drop_all()


def test_socketio_send_message_broadcasts_wrapped(app_with_socket):
    app = app_with_socket

    # 创建两个用户
    u1 = User(username='u1', email='u1@example.com')
    u1.set_password('pass')
    u2 = User(username='u2', email='u2@example.com')
    u2.set_password('pass')
    db.session.add_all([u1, u2])
    db.session.commit()

    # 创建会话并将两人加入
    conv = ChatConversation(conversation_type='direct', creator_id=u1.id)
    db.session.add(conv)
    db.session.flush()
    p1 = ChatParticipant(conversation_id=conv.id, user_id=u1.id)
    p2 = ChatParticipant(conversation_id=conv.id, user_id=u2.id)
    db.session.add_all([p1, p2])
    db.session.commit()

    # 使用 Flask 测试客户端登录并创建 SocketIO 测试客户端
    client1 = app.test_client()
    login_resp = client1.post('/auth/login', data={'username': 'u1', 'password': 'pass'}, follow_redirects=True)
    assert login_resp.status_code in (200, 302)

    client2 = app.test_client()
    login_resp2 = client2.post('/auth/login', data={'username': 'u2', 'password': 'pass'}, follow_redirects=True)
    assert login_resp2.status_code in (200, 302)

    # 捕获 socketio.emit 调用 (来自 /api/chat/messages 路由)
    calls = []
    def fake_emit(event, payload, room=None, **kwargs):
        calls.append({'event': event, 'payload': payload, 'room': room, 'kwargs': kwargs})
    # Monkeypatch the socketio.emit used by the routes (ensure we patch the live object in the module)
    import app.socketio_handler as sio_mod
    original_emit = None
    if hasattr(sio_mod, 'socketio') and hasattr(sio_mod.socketio, 'emit'):
        original_emit = sio_mod.socketio.emit
        sio_mod.socketio.emit = fake_emit
    try:
        # 使用 HTTP POST 发送消息 (这应触发 socketio.emit)
        client1 = app.test_client()
        login_resp = client1.post('/auth/login', data={'username': 'u1', 'password': 'pass'}, follow_redirects=True)
        assert login_resp.status_code in (200, 302)

        resp = client1.post('/api/chat/messages', json={'conversation_id': conv.id, 'content': 'hello via http'})
        assert resp.status_code == 200

        # 验证 emit 被调用
        assert len(calls) >= 1, f'socketio.emit was not called; calls={calls}'
        # 找到 new_message 的调用
        new_calls = [c for c in calls if c['event'] == 'new_message']
        assert new_calls, f'no new_message emits: {calls}'
        data = new_calls[0]['payload']
        assert isinstance(data, dict)
        assert 'conversation_id' in data
        assert 'message' in data
        assert data['conversation_id'] == conv.id
        assert data['message']['content'] == 'hello via http'
    finally:
        if original_emit and hasattr(sio_mod, 'socketio') and hasattr(sio_mod.socketio, 'emit'):
            sio_mod.socketio.emit = original_emit