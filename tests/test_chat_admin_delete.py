import io
import pytest
from app import create_app, db
from app.models import User
from app.chat_models import ChatConversation, ChatMessage, ChatParticipant, ChatAttachment


@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.app_context():
        db.create_all()
        # ensure admin user exists
        admin = User(username='admin', email='admin@local', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()


def test_admin_can_delete_conversation(client):
    # 登录为 admin（conftest 会确保 admin 用户存在）
    login = client.post('/auth/login', data={'username': 'admin', 'password': 'admin123'}, follow_redirects=True)
    assert login.status_code in (200, 302)

    admin = User.query.filter_by(username='admin').first()
    assert admin is not None

    # 创建对话（creator_id 必须存在）
    conv = ChatConversation(conversation_type='direct', name='to-delete', creator_id=admin.id)
    db.session.add(conv)
    db.session.flush()

    # 添加参与者
    p1 = ChatParticipant(conversation_id=conv.id, user_id=admin.id, role='owner')
    db.session.add(p1)

    # 添加消息
    msg = ChatMessage(conversation_id=conv.id, sender_id=admin.id, content='hello')
    db.session.add(msg)
    db.session.flush()

    # 添加假 attachment（若模型存在）
    try:
        att = ChatAttachment(filename='test.txt', stored_filename='test.txt', file_path='/tmp/test.txt', file_size=10, file_type='text/plain', upload_user_id=admin.id)
        db.session.add(att)
        db.session.flush()
        msg.attachments = [att]
        db.session.commit()
    except Exception:
        db.session.rollback()
        db.session.commit()

    # 使用 admin 权限删除
    resp = client.delete(f'/api/chat/admin/conversations/{conv.id}')
    assert resp.status_code == 200, resp.get_data(as_text=True)

    # 确认会话被删除
    assert ChatConversation.query.get(conv.id) is None

    # 确认消息也被删除或标记
    assert ChatMessage.query.filter_by(conversation_id=conv.id).count() == 0
