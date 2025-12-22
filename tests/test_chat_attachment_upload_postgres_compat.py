import os
import tempfile
from io import BytesIO
from app import create_app, db
from app.chat_models import ChatAttachment

class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


def test_upload_attachment_allows_null_message_and_associate():
    app = create_app(TestConfig)
    temp_dir = tempfile.mkdtemp()
    with app.app_context():
        app.config['UPLOAD_FOLDER'] = temp_dir
        db.drop_all()
        db.create_all()
        client = app.test_client()

        from app.models import User
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(username='admin', email='admin@example.com', role='admin')
            admin.set_password('admin123')
            db.session.add(admin)
        user = User(username='u1', email='u1@example.com', role='user')
        user.set_password('user123')
        db.session.add(user)
        db.session.commit()

        with client.session_transaction() as sess:
            sess['_user_id'] = str(admin.id)
            sess['_fresh'] = True

        # create a direct conversation
        create_resp = client.post('/api/chat/conversations', json={'type': 'direct', 'participant_ids': [user.id]})
        assert create_resp.status_code in (200, 201)
        conv_id = create_resp.get_json()['conversation']['id']

        # upload attachment (should not fail with foreign key issues)
        file_content = b'Test file'
        file_storage = (BytesIO(file_content), 'test.txt')
        resp = client.post('/api/chat/attachments', data={'file': file_storage, 'conversation_id': conv_id}, content_type='multipart/form-data')
        assert resp.status_code == 201
        data = resp.get_json()
        att_id = data['attachment_id']

        # attachment record exists and message_id is None until associated
        att = ChatAttachment.query.get(att_id)
        assert att is not None
        assert att.message_id is None

        # associate via sending a message
        send_resp = client.post('/api/chat/messages', json={'conversation_id': conv_id, 'content': 'here', 'attachment_ids': [att_id]})
        assert send_resp.status_code in (200, 201)
        att = ChatAttachment.query.get(att_id)
        assert att.message_id is not None

        # cleanup
        try:
            for f in os.listdir(temp_dir):
                os.remove(os.path.join(temp_dir, f))
            os.rmdir(temp_dir)
        except Exception:
            pass
