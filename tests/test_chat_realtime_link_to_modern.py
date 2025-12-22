import pytest

from app import create_app, db
from app.models import User

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.app_context():
        db.create_all()
        user = User(username='admin', email='admin@system.local', role='admin')
        user.set_password('admin12')
        db.session.add(user)
        db.session.commit()
    yield app
    with app.app_context():
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()


def login_admin(client):
    client.post('/auth/login', data={'username': 'admin', 'password': 'admin12'}, follow_redirects=True)


def test_chat_realtime_contains_link_to_modern(client, app):
    login_admin(client)
    rv = client.get('/chat')
    assert rv.status_code == 200
    html = rv.get_data(as_text=True)
    assert '/chat/modern' in html
    assert '切换到现代聊天视图' in html
