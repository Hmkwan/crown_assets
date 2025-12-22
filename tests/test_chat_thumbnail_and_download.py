import os
import tempfile
from io import BytesIO
from app import create_app, db
from app.chat_models import ChatAttachment
from PIL import Image

class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


def test_thumbnail_and_download_for_image():
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

        # create conversation
        create_resp = client.post('/api/chat/conversations', json={'type': 'direct', 'participant_ids': [user.id]})
        assert create_resp.status_code in (200, 201)
        conv_id = create_resp.get_json()['conversation']['id']

        # create a small PNG in memory
        img = Image.new('RGB', (80, 80), color=(0, 128, 255))
        b = BytesIO()
        img.save(b, format='PNG')
        b.seek(0)

        # upload image via attachments endpoint
        file_storage = (b, 'test_img.png')
        resp = client.post('/api/chat/attachments', data={'file': file_storage, 'conversation_id': conv_id}, content_type='multipart/form-data')
        assert resp.status_code == 201
        att_id = resp.get_json()['attachment_id']

        # thumbnail endpoint should return an image
        thumb_resp = client.get(f'/api/chat/attachments/{att_id}/thumbnail')
        assert thumb_resp.status_code == 200
        assert thumb_resp.headers.get('Content-Type', '').startswith('image/')

        # thumbnail file should exist on disk (thumbnail path saved)
        att = ChatAttachment.query.get(att_id)
        assert att.thumbnail_path is not None
        assert os.path.exists(att.thumbnail_path)

        # download should return file content
        dl_resp = client.get(f'/api/chat/attachments/{att_id}/download')
        assert dl_resp.status_code == 200
        assert dl_resp.data and len(dl_resp.data) > 0

        # cleanup
        try:
            for f in os.listdir(temp_dir):
                os.remove(os.path.join(temp_dir, f))
            os.rmdir(temp_dir)
        except Exception:
            pass


def test_resolve_existing_path_variants():
    app = create_app(TestConfig)
    with app.app_context():
        from app.chat_routes import _resolve_existing_path
        base = app.root_path
        alt_uploads = os.path.join(os.path.dirname(base), 'uploads', 'chat')
        os.makedirs(alt_uploads, exist_ok=True)
        fname = 'variant_test.png'
        p = os.path.join(alt_uploads, fname)
        with open(p, 'wb') as f:
            f.write(b'pngdata')

        # Simulate stored path pointing to /app/app/uploads/... while real file is at /app/uploads/...
        stored_path = os.path.join(base, 'uploads', 'chat', fname)
        resolved = _resolve_existing_path(stored_path)
        assert resolved is not None and os.path.exists(resolved)

        # Cleanup
        os.remove(p)
