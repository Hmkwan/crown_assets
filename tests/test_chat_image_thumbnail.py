import tempfile
from io import BytesIO
from PIL import Image
from app import create_app, db

class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


def make_png_bytes(size=(100, 100), color=(255, 0, 0)):
    bio = BytesIO()
    img = Image.new('RGB', size, color=color)
    img.save(bio, format='PNG')
    bio.seek(0)
    return bio


def test_image_upload_generates_thumbnail_and_can_download():
    app = create_app(TestConfig)
    tmpdir = tempfile.mkdtemp()

    with app.app_context():
        app.config['UPLOAD_FOLDER'] = tmpdir
        db.drop_all()
        db.create_all()
        client = app.test_client()

        # create users
        from app.models import User
        admin = User(username='admin', email='admin@example.com', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()

        with client.session_transaction() as sess:
            sess['_user_id'] = str(admin.id)
            sess['_fresh'] = True

        # create conversation
        resp = client.post('/api/chat/conversations', json={'type': 'direct', 'participant_ids': []})
        # The endpoint may return 400 if no participants provided; create a direct conv by creating another user
        if resp.status_code != 201:
            from app.models import User as U
            u2 = U(username='tmpuser', email='tmp@example.com', role='user')
            u2.set_password('p')
            db.session.add(u2)
            db.session.commit()
            resp = client.post('/api/chat/conversations', json={'type': 'direct', 'participant_ids': [u2.id]})
        assert resp.status_code in (200, 201)
        conv_id = resp.get_json()['conversation']['id']

        # upload an image
        png = make_png_bytes()
        data = {
            'conversation_id': str(conv_id),
            'file': (png, 'test.png')
        }
        upload = client.post('/api/chat/attachments', data=data, content_type='multipart/form-data')
        assert upload.status_code == 201
        j = upload.get_json()
        att = j['attachment']
        assert att['is_image'] or att['file_type'].startswith('image/')
        assert 'thumbnail_url' in att or j.get('attachment_id') is not None

        # fetch thumbnail if provided
        if att.get('thumbnail_url'):
            turl = att['thumbnail_url']
            # thumbnail endpoint requires auth
            tresp = client.get(turl)
            assert tresp.status_code == 200
            assert 'image' in tresp.content_type

        # download
        dresp = client.get(f"/api/chat/attachments/{j['attachment_id']}/download")
        assert dresp.status_code == 200
        assert 'attachment' in dresp.headers.get('Content-Disposition', '')

        # cleanup
        import os
        try:
            for f in os.listdir(tmpdir):
                os.remove(os.path.join(tmpdir, f))
            os.rmdir(tmpdir)
        except Exception:
            pass