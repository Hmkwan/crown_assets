import pytest
from app import create_app, db
from app.models import User, Announcement

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.app_context():
        db.create_all()
        # create admin user
        user = User(username='admin', email='admin@system.local', role='admin')
        user.set_password('admin12')
        db.session.add(user)
        db.session.commit()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def login_admin(client):
    # create admin user if not exists is handled by fixture
    client.post('/auth/login', data={'username':'admin','password':'admin12','submit':'登录'})


def test_create_announcement_rejects_empty_content(client, app):
    # login
    login_admin(client)

    # try to create announcement with empty content
    rv = client.post('/admin/announcements/create', data={'title':'T1', 'content':''}, follow_redirects=True)
    assert '公告内容不能为空' in rv.data.decode('utf-8')
    # ensure no announcement created
    with app.app_context():
        assert Announcement.query.count() == 0


def test_edit_announcement_preserves_content_on_empty_submission(client, app):
    # login and create a valid announcement directly
    with app.app_context():
        user = User.query.filter_by(username='admin').first()
        ann = Announcement(title='A1', content='Hello', creator_id=user.id, is_published=True)
        db.session.add(ann)
        db.session.commit()
        ann_id = ann.id

    login_admin(client)
    # submit edit with empty content
    rv = client.post(f'/admin/announcements/{ann_id}/edit', data={'title':'A1 edited', 'content':''}, follow_redirects=True)
    assert '公告内容不能为空' in rv.data.decode('utf-8')
    # ensure original content remains
    with app.app_context():
        ann = Announcement.query.get(ann_id)
        assert ann.content == 'Hello'
