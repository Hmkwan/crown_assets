# -*- coding: utf-8 -*-
import pytest
from app import create_app, db
from app.models import User
from app.chat_models import ChatConversation, ChatParticipant, ChatMessage
from app.approval_models import WorkflowTemplate, ApprovalInstance

@pytest.fixture
def app_ctx():
    app = create_app()
    app.config['TESTING'] = True
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


def test_chat_start_workflow_creates_instance_and_message(app_ctx):
    # 创建用户和会话
    import uuid
    u1_username = 'u1-' + uuid.uuid4().hex[:8]
    u2_username = 'u2-' + uuid.uuid4().hex[:8]
    u1 = User(username=u1_username, email=f'{u1_username}@example.com')
    u1.set_password('pass')
    u2 = User(username=u2_username, email=f'{u2_username}@example.com')
    u2.set_password('pass')
    # use generated username when logging in later
    login_username = u1_username
    db.session.add_all([u1, u2])
    db.session.commit()

    conv = ChatConversation(conversation_type='direct', creator_id=u1.id)
    db.session.add(conv)
    db.session.flush()

    p1 = ChatParticipant(conversation_id=conv.id, user_id=u1.id)
    p2 = ChatParticipant(conversation_id=conv.id, user_id=u2.id)
    db.session.add_all([p1, p2])
    db.session.commit()

    # 创建模板
    tmpl = WorkflowTemplate(name='Chat Approval', code='chat_approval', is_active=True, order_type='chat')
    db.session.add(tmpl)
    db.session.commit()

    client = app_ctx.test_client()

    # 模拟登录为 u1
    with client:
        client.post('/auth/login', data={'username': login_username, 'password': 'pass', 'csrf_token': client.get('/auth/login').data.decode()})
        # 列表模板
        resp = client.get('/api/chat/workflow_templates')
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data['templates']) >= 1

        # 发起流程
        resp2 = client.post('/api/chat/start_workflow', json={'conversation_id': conv.id, 'template_id': tmpl.id})
        assert resp2.status_code == 201
        data2 = resp2.get_json()
        assert data2['success'] is True
        inst_id = data2['instance_id']

        # 检查 ApprovalInstance
        inst = ApprovalInstance.query.get(inst_id)
        assert inst is not None
        assert inst.order_type == 'chat'
        assert inst.order_id == conv.id

        # 检查系统消息已创建
        msg = ChatMessage.query.filter_by(conversation_id=conv.id, message_type='system').first()
        assert msg is not None
        assert str(inst_id) in (msg.content or '')
