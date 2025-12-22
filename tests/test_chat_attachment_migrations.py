import os
import tempfile
from app import create_app, db
from app.chat_models import ChatAttachment
from scripts.normalize_attachment_paths import normalize_paths

class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


def test_normalize_paths_updates_records():
    app = create_app(TestConfig)
    with app.app_context():
        db.drop_all()
        db.create_all()
        # Create two upload dirs to simulate /app/app/uploads vs /app/uploads
        base = app.root_path
        uploads_a = os.path.join(base, 'uploads', 'chat')
        uploads_b = os.path.join(os.path.dirname(base), 'uploads', 'chat')
        os.makedirs(uploads_b, exist_ok=True)

        # Create a real file in uploads_b
        fname = 'migrate_test.png'
        real_path = os.path.join(uploads_b, fname)
        with open(real_path, 'wb') as f:
            f.write(b'png')

        # Insert a DB record that points to uploads_a (which doesn't exist) but real file exists in uploads_b
        stored_in_db = os.path.join(base, 'uploads', 'chat', fname)
        att = ChatAttachment(
            message_id=None,
            filename=fname,
            stored_filename=fname,
            file_path=stored_in_db,
            thumbnail_path=None,
            file_size=123,
            file_type='image/png',
            upload_user_id=1
        )
        db.session.add(att)
        db.session.commit()

        # Dry run should report potential change but not apply
        changes = normalize_paths(app, apply_changes=False)
        assert changes == 0

        # Apply changes
        changes = normalize_paths(app, apply_changes=True)
        assert changes == 1

        # Verify DB updated to point to the real path
        att2 = ChatAttachment.query.get(att.id)
        assert os.path.exists(att2.file_path)
        assert att2.file_path != stored_in_db

        # Cleanup
        os.remove(real_path)
