from app import create_app, db
from app.models import User, Announcement
from datetime import datetime

class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

app = create_app(TestConfig)
with app.app_context():
    db.create_all()
    u = User(username='ui_tester', email='ui@test')
    db.session.add(u); db.session.commit()
    ann = Announcement(title='ui test', content='body', is_published=True, publish_time=datetime.utcnow(), creator_id=u.id)
    db.session.add(ann); db.session.commit()
    c = app.test_client()
    from app import login
    with c.session_transaction() as s:
        s[login.session_key] = str(u.id)
    r = c.get('/announcements')
    print('status', r.status_code)
    print(r.get_data(as_text=True)[:1200])
