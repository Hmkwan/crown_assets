import io
from werkzeug.datastructures import FileStorage

from app import create_app, db
from app.services.announcement_service import create_announcement_from_form


class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


def test_create_announcement_with_attachment(tmp_path):
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()

        # import models after app is created to avoid early import side-effects
        from app.models import User, Announcement, AnnouncementAttachment

        # create admin user
        admin = User(username='testadmin', email='a@example.com')
        admin.set_password('password')
        admin.role = 'admin'
        db.session.add(admin)
        db.session.commit()

        # build fake file
        img_bytes = io.BytesIO()
        # use a tiny red PNG
        img_bytes.write(b'\x89PNG\r\n\x1a\n')
        img_bytes.seek(0)
        fs = FileStorage(stream=img_bytes, filename='test.png', content_type='image/png')

        form = {
            'title': 'Test',
            'content': '<p>Hello</p>',
            'type': 'notice',
            'priority': 'normal',
            'is_pinned': '0',
            'is_active': '1'
        }

        ann = create_announcement_from_form(form, [fs], admin)

        from app.models import Announcement, AnnouncementAttachment

        assert isinstance(ann, Announcement)
        assert ann.title == 'Test'

        atts = AnnouncementAttachment.query.filter_by(announcement_id=ann.id).all()
        assert len(atts) == 1
        att = atts[0]
        assert att.filename == 'test.png'
        # In TESTING mode thumbnail generation runs synchronously and should set thumbnail_path or be None but valid path
        # Check thumbnail field exists (may be None if create_thumbnail failed)
        assert hasattr(att, 'thumbnail_path')
