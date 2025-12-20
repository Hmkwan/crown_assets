import os
import tempfile
from io import BytesIO
from app import create_app, db
from app.chat_models import ChatConversation, ChatAttachment

class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


def test_upload_and_associate_attachment_and_rename():
    app = create_app(TestConfig)
    # use temp upload folder to avoid polluting repo
    temp_dir = tempfile.mkdtemp()

    with app.app_context():
        app.config['UPLOAD_FOLDER'] = temp_dir
        # ensure a clean schema for in-memory DB (drop existing tables then recreate)
        db.drop_all()
        db.create_all()
        client = app.test_client()

        # create users
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

        # login as admin by setting session directly
        with client.session_transaction() as sess:
            sess['_user_id'] = str(admin.id)
            sess['_fresh'] = True

        # create a group conversation
        create_resp = client.post('/api/chat/conversations', json={
            'type': 'group',
            'participant_ids': [user.id],
            'name': 'Test Group'
        })
        assert create_resp.status_code in (200,201)
        conv_id = create_resp.get_json()['conversation']['id']

        # upload attachment
        data = {
            'conversation_id': str(conv_id)
        }
        file_content = b'Test file content'
        file_storage = (BytesIO(file_content), 'test.txt')
        resp = client.post('/api/chat/attachments', data={'file': file_storage, 'conversation_id': conv_id}, content_type='multipart/form-data')
        assert resp.status_code == 201
        json_data = resp.get_json()
        att_id = json_data['attachment_id']

        # send message with attachment
        send_resp = client.post('/api/chat/messages', json={
            'conversation_id': conv_id,
            'content': 'Here is a file',
            'attachment_ids': [att_id]
        })
        assert send_resp.status_code in (200,201)
        send_json = send_resp.get_json()
        assert send_json.get('success') is True

        # check attachment associated
        att = ChatAttachment.query.get(att_id)
        assert att is not None
        assert att.message_id is not None

        # rename group (admin is owner)
        patch_resp = client.patch(f'/api/chat/conversations/{conv_id}', json={'name': 'Renamed Group'})
        assert patch_resp.status_code == 200
        conv = ChatConversation.query.get(conv_id)
        assert conv.name == 'Renamed Group'

        # cleanup temp files
        try:
            for f in os.listdir(temp_dir):
                os.remove(os.path.join(temp_dir, f))
            os.rmdir(temp_dir)
        except Exception:
            pass


if __name__ == '__main__':
    test_upload_and_associate_attachment_and_rename()